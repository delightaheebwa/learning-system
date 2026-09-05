"""
gate_pipe — Deterministic delegation gate (Open WebUI Filter).

Installed as Filter (Function type filter), bound to Scout/Tutor/Clerk presets.
Runs as outlet (blocking before render) with inlet pass-through.

Enforces:
- Tutor new-lesson: Scout digest + Scout message present (slug match, 7-day TTL).
  Resume of existing lesson (Lessons/ file exists) bypasses digest check.
- Tutor content (Learning Tutor only, multi-turn): per-generation GATE:fact_check /
  GATE:quiz_audit receipts — each Tutor generation that teaches must have a fresh
  fact_check (claims) or quiz_audit (questions) with parent_message_id == draft.id;
  an upfront Plan batch never satisfies later Teach steps, and quiz_audit never
  satisfies claims. Mixed claims+quiz needs BOTH receipts for the same message.
- Clerk content (single-turn): single GATE:review receipt per wiki write.

Retry: outlet replaces blocked draft with BLOCKED (<code>) banner. Cap 2 per
USER TURN (reset when parent user message changes), durably counted in
Chat.meta.gate_state. After cap, withheld banner only.

Digest: Learning System/.tmp/context-<chat_id>-<slug>.json, gitignored.
Expiry 7 days, swept on next Tutor/Clerk inlet.

Install: setup_openwebui.py creates Function and binds filterIds to presets.
"""

import json
import os
import re
import time
from pathlib import Path

try:
    from pydantic import BaseModel, Field
except Exception as e:  # pragma: no cover
    raise ImportError("pydantic is required for gate_pipe — install it or run inside Open WebUI") from e

try:
    from gate_schema import (
        GATEFactCheckEnvelope,
        GATEReviewEnvelope,
        GATEQuizAuditEnvelope,
        extract_json_block,
    )
except Exception:
    try:
        from open_webui.functions.gate_schema import (  # type: ignore
            GATEFactCheckEnvelope,
            GATEReviewEnvelope,
            GATEQuizAuditEnvelope,
            extract_json_block,
        )
    except Exception:
        GATEFactCheckEnvelope = None  # type: ignore
        GATEReviewEnvelope = None  # type: ignore
        GATEQuizAuditEnvelope = None  # type: ignore
        extract_json_block = lambda t: None  # noqa: E731


TMP_DIR = ".tmp"
SLUG_RE = re.compile(r"[^a-z0-9]+")
TRIGGER_RE = re.compile(r"^\s*(/teach|/lesson|/continue|teach me|learn|study)\b", re.I)
# Per-generation gate (Tutor only): detect quiz vs claims content
_QUIZ_RE = re.compile(r"(\|\s*A\s*\||\|\s*B\s*\||\bQ\s*\d+\b|Your answer \+ confidence|correct_index|questions_json)", re.I)


def _is_quiz_content(text: str) -> bool:
    return bool(_QUIZ_RE.search(text or ""))


def _non_quiz_prose_len(text: str) -> int:
    """Chars outside quiz markers/tables — used to distinguish pure quiz vs mixed."""
    total = 0
    for line in text.splitlines():
        if _QUIZ_RE.search(line):
            continue
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        total += len(stripped)
    return total


def _is_claims_content(text: str) -> bool:
    s = (text or "").strip()
    if len(s) < 120:
        return False
    if not _is_quiz_content(s):
        return True

    non_quiz = _non_quiz_prose_len(s)
    hits = len(_QUIZ_RE.findall(s))

    # Pure quiz: several markers but little prose → quiz-only
    if hits >= 3 and non_quiz < 300:
        return False
    if hits >= 2 and non_quiz < 200:
        return False

    # Mixed: quiz markers plus substantial prose → needs fact_check as well
    if non_quiz > 250:
        return True
    return len(s) > 500 and non_quiz > 120


def _gate_needs(content: str, is_tutor: bool, is_clerk: bool):
    """Return (needs_fact_check, needs_quiz_audit, needs_review) for Gate 2."""
    if is_tutor:
        needs_fact = _is_claims_content(content)
        needs_quiz = _is_quiz_content(content)
        if not needs_fact and not needs_quiz and len(content.strip()) > 120:
            needs_fact = True
        return needs_fact, needs_quiz, False
    if is_clerk and len(content.strip()) > 80:
        return False, False, True
    return False, False, False


def _check_fact_check(data: dict, verd_text: str):
    """Validate fact_check envelope + verdicts. Returns (ok, code, detail)."""
    # Lift per-claim source to top-level if needed (LLM drift)
    if not data.get("source_url") and not data.get("source_urls") and not data.get("source_file"):
        for c in (data.get("claims") or []):
            if isinstance(c, dict) and (c.get("source_url") or c.get("source_urls") or c.get("source_file")):
                if c.get("source_url"):
                    data["source_url"] = c.get("source_url")
                if c.get("source_urls"):
                    data["source_urls"] = c.get("source_urls")
                if c.get("source_file"):
                    data["source_file"] = c.get("source_file")
                break
    if GATEFactCheckEnvelope is not None:
        try:
            clean = dict(data)
            clean["claims"] = [{k: v for k, v in cc.items() if k in ("id", "claim")} if isinstance(cc, dict) else cc for cc in (clean.get("claims") or [])]
            GATEFactCheckEnvelope.model_validate(clean)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"fact_check envelope invalid: {e}"
    claims = data.get("claims") or []
    if not claims or not isinstance(claims, list):
        return False, "MALFORMED_ENVELOPE", "GATE:fact_check envelope missing claims[]"
    if not data.get("source_url") and not data.get("source_urls") and not data.get("source_file"):
        return False, "MALFORMED_ENVELOPE", "GATE:fact_check requires source_url(s) or source_file (multi-source source_urls preferred: Rohit + external refs)"
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdicts" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Subagent did not return {verdicts:[...]}"
    verdicts = verdict_data.get("verdicts") or []
    bad = [v for v in verdicts if v.get("verdict") not in ("PASS", "ISSUES", "UNVERIFIED")]
    if bad:
        return False, "MALFORMED_VERDICTS", f"Invalid verdict value: {bad[0].get('verdict')}"
    verdict_ids = {v.get("id") for v in verdicts}
    claim_ids = {c.get("id") for c in claims}
    if claim_ids - verdict_ids:
        return False, "MALFORMED_VERDICTS", f"Verdicts missing ids: {claim_ids - verdict_ids}"
    return True, "", ""


def _check_quiz_audit(data: dict, verd_text: str):
    if GATEQuizAuditEnvelope is not None:
        try:
            GATEQuizAuditEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"quiz_audit envelope invalid: {e}"
    if not data.get("questions_json") or not isinstance(data.get("questions_json"), list):
        return False, "MALFORMED_ENVELOPE", "GATE:quiz_audit requires questions_json[]"
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Quiz-audit subagent did not return {verdict: PASS|ISSUES}"
    if verdict_data.get("verdict") not in ("PASS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid quiz verdict: {verdict_data.get('verdict')}"
    return True, "", ""


def _check_review(data: dict, verd_text: str):
    if GATEReviewEnvelope is not None:
        try:
            GATEReviewEnvelope.model_validate(data)
        except Exception as e:
            return False, "MALFORMED_ENVELOPE", f"review envelope invalid: {e}"
    if not data.get("wiki_content") or not data.get("concepts"):
        return False, "MALFORMED_ENVELOPE", "GATE:review requires wiki_content and concepts"
    verdict_data = extract_json_block(verd_text) if callable(extract_json_block) else None
    if not verdict_data or "verdict" not in verdict_data:
        return False, "MALFORMED_VERDICTS", "Review subagent did not return {verdict: PASS|ISSUES}"
    if verdict_data.get("verdict") not in ("PASS", "ISSUES"):
        return False, "MALFORMED_VERDICTS", f"Invalid review verdict: {verdict_data.get('verdict')}"
    return True, "", ""


def _parse_gate_envelope(task: str):
    """Extract gate data dict from delegate_task payload, handling GATE: prefix."""
    json_part = task
    if "GATE:" in task:
        parts = task.split("\n", 1)
        if len(parts) == 2:
            json_part = parts[1]
    stripped = json_part.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except Exception:
            return extract_json_block(task) if callable(extract_json_block) else None
    return extract_json_block(task) if callable(extract_json_block) else None


def _slugify(text: str) -> str:
    s = SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s[:64] or "lesson"


def _extract_topic(parent_text: str) -> str:
    """Extract topic from trigger text — first line only, strip template boilerplate."""
    if not parent_text:
        return ""
    first_line = parent_text.strip().split("\n", 1)[0]
    # Try "teach me X" / "/teach X" pattern on first line only
    m = re.search(r"(?:/teach|teach me)\s+(.+)", first_line, re.I)
    if m:
        topic = m.group(1).strip()
        # Strip trailing boilerplate like "Load the learning-teach skill"
        topic = re.split(r"\s+Load the\b", topic, flags=re.I)[0].strip()
        # Strip leading "about:" that appears in "Teach me about: X" prompts
        topic = re.sub(r"^\s*about\s*:\s*", "", topic, flags=re.I)
        topic = topic.strip("\"' :")
        return topic
    # For /lesson, topic is not in trigger — use curriculum lookup; return empty
    # For bare triggers, return first line truncated
    return first_line[:120]


def _is_scout_message(msg: dict, valves) -> bool:
    prefix = getattr(valves, "scout_name_prefix", "Scout")
    model = msg.get("model") or ""
    models = msg.get("models")
    if isinstance(models, list) and models:
        # models is list of model ids for this message
        if any(prefix.lower() in str(m).lower() for m in models):
            return True
    if model and prefix.lower() in str(model).lower():
        return True
    # Content marker fallback
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return "SCOUT DIGEST" in str(content)


def _is_tutor_preset(model_id: str, valves) -> bool:
    prefix = getattr(valves, "tutor_name_prefix", "Tutor")
    return prefix.lower() in (model_id or "").lower()


def _is_clerk_preset(model_id: str, valves) -> bool:
    prefix = getattr(valves, "clerk_name_prefix", "Clerk")
    return prefix.lower() in (model_id or "").lower()


def _find_digest(chat_id: str, slug: str, ttl_days: int, repo_root: str):
    base = Path(repo_root) / "Learning System" / TMP_DIR
    if not base.exists():
        return None
    # Prefer exact slug match
    exact = list(base.glob(f"context-{chat_id}-{slug}.json"))
    candidates = exact if exact else list(base.glob(f"context-{chat_id}-*.json"))
    # Fallback: legacy Scout files without chat_id prefix (e.g. context-mission-0-*.json)
    # and generic slug mismatches like "next-lesson" vs digest slug "mission-0-catchup-foundations"
    if not candidates:
        candidates = list(base.glob("context-*.json"))
        # For alias topics like "next-lesson", "lesson", "continue" — prefer the newest
        # digest for this chat if any, otherwise any recent digest
        if slug in ("next-lesson", "lesson", "continue", "gather-context-for-next-lesson"):
            chat_candidates = list(base.glob(f"context-{chat_id}-*.json"))
            if chat_candidates:
                candidates = chat_candidates
    # Filter by TTL and pick newest
    valid = []
    for p in candidates:
        try:
            age_days = (time.time() - p.stat().st_mtime) / 86400
            if age_days > ttl_days:
                continue
            # For exact match, verify; for fallback, accept any recent digest for this chat
            valid.append(p)
        except Exception:
            continue
    if not valid:
        return None
    # Newest first
    valid.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # Alias slugs should accept any recent digest (return newest)
    if slug in ("next-lesson", "lesson", "continue", "gather-context-for-next-lesson"):
        return valid[0]
    # If we used fallback, return newest regardless of slug
    if exact:
        for p in valid:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("slug") == slug:
                    return p
            except Exception:
                continue
        # Exact glob matched but slug field mismatched — still return newest exact
        return valid[0]
    # No exact match — check if any candidate's internal slug matches requested slug
    for p in valid:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("slug") == slug:
                return p
        except Exception:
            continue
    return valid[0]


def _sweep_expired(repo_root: str, ttl_days: int):
    base = Path(repo_root) / "Learning System" / TMP_DIR
    if not base.exists():
        return
    now = time.time()
    for p in base.glob("context-*.json"):
        try:
            if (now - p.stat().st_mtime) / 86400 > ttl_days:
                p.unlink()
        except Exception:
            pass


def _get_repo_root(valves, body: dict) -> str:
    # Valve override takes precedence
    v_root = getattr(valves, "repo_root", "") if valves else ""
    if v_root and os.path.isdir(v_root):
        return v_root
    for cand in [
        "/home/user/learning-system",
        "/home/delinux/learning-system",
        os.path.expanduser("~/learning-system"),
    ]:
        if os.path.isdir(cand):
            return cand
    return os.path.expanduser("~/learning-system")


def _last_user_message(hist: dict):
    """Return (msg_id, text) of the most recent user message in history."""
    if not hist:
        return None, ""
    # hist is dict of id -> msg
    # Find max timestamp user message
    user_msgs = [m for m in hist.values() if m.get("role") == "user"]
    if not user_msgs:
        return None, ""
    # Prefer latest timestamp; fallback to insertion order
    try:
        latest = max(user_msgs, key=lambda m: m.get("timestamp", 0))
    except Exception:
        latest = user_msgs[-1]
    mid = latest.get("id")
    content = latest.get("content") or ""
    if isinstance(content, list):
        content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return mid, str(content)


class Filter:
    class Valves(BaseModel):  # type: ignore
        priority: int = Field(default=10, description="Filter priority (higher runs later)")
        max_retries: int = Field(default=2, ge=0, le=5, description="Max fix retries per user turn")
        digest_ttl_days: int = Field(default=7, ge=1, le=30)
        scout_name_prefix: str = Field(default="Scout")
        tutor_name_prefix: str = Field(default="Tutor")
        clerk_name_prefix: str = Field(default="Clerk")
        repo_root: str = Field(default="", description="Override repo path (empty = auto-detect)")
        blocked_banner: str = Field(
            default="⛔ Withheld: not independently verified — retry limit reached. Fix the GATE envelope and retry.",
            description="Banner shown after retry cap",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(self, body: dict, __user__: dict = None, __request__=None, __metadata__: dict = None) -> dict:  # type: ignore
        try:
            repo_root = _get_repo_root(self.valves, body)
            _sweep_expired(repo_root, getattr(self.valves, "digest_ttl_days", 7))
        except Exception:
            pass
        return body

    def _parse_child_hist(self, hist: dict):
        task = ""
        content = ""
        for m in (hist or {}).values():
            if m.get("role") == "user":
                task = m.get("content") or task
            if m.get("role") == "assistant":
                content = m.get("content") or content
        is_done = any(isinstance(v, dict) and v.get("done") for v in (hist or {}).values())
        return task, content, is_done

    async def _fetch_child_chats(self, chat_id: str, assistant_id: str, user: dict):
        """Fetch foreground subagent receipts with parent_message_id == assistant_id."""
        child_chats: list[dict] = []
        try:
            from sqlalchemy import select
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat

            user_id = user.get("id")
            async with get_async_db() as db:
                result = await db.execute(
                    select(Chat).where(
                        Chat.user_id == user_id,
                        Chat.meta["internal"].as_boolean().is_(True),
                        Chat.meta["type"].as_string() == "subagent",
                        Chat.meta["parent_message_id"].as_string() == assistant_id,
                    )
                )
                for row in result.scalars().all():
                    meta = row.meta or {}
                    hist = (row.chat or {}).get("history", {}).get("messages", {}) if hasattr(row, "chat") else {}
                    task, content, is_done = self._parse_child_hist(hist)
                    child_chats.append(
                        {"id": row.id, "meta": meta, "mode": meta.get("mode", ""), "task": task, "content": content, "done": is_done}
                    )
            if child_chats:
                return child_chats

            # Fallback: legacy lookup via parent chat id
            from open_webui.models.chats import Chats

            ids = await Chats.get_internal_chat_ids_by_parent_id(chat_id, user_id)
            for cid in ids:
                c = await Chats.get_chat_by_id(cid)
                if not c or (c.meta or {}).get("parent_message_id") != assistant_id:
                    continue
                meta = c.meta or {}
                if (meta.get("mode") or "").lower() in ("background", "async"):
                    continue
                hist = (c.chat or {}).get("history", {}).get("messages", {})
                task, content, is_done = self._parse_child_hist(hist)
                if not is_done:
                    continue
                child_chats.append({"id": cid, "meta": meta, "mode": meta.get("mode", ""), "task": task, "content": content, "done": True})
        except Exception as e:
            try:
                import logging

                logging.getLogger(__name__).debug(f"gate_pipe child lookup failed (fail open): {e}")
            except Exception:
                pass
            return None  # signal fail-open to caller
        return child_chats

    async def outlet(self, body: dict, __user__: dict = None, __request__=None, __metadata__: dict = None, __model__: dict = None) -> dict:  # type: ignore
        """
        body shape (middleware outlet_filter_handler):
          {model, messages: [{id, role, content, ...}], chat_id, id (assistant message id), filter_ids}
        Returns modified body; content replacement is persisted and emitted via chat:outlet.
        """
        try:
            valves = self.valves
            model_id = body.get("model") or (__model__.get("id") if isinstance(__model__, dict) else "") or ""
            chat_id = body.get("chat_id") or (__metadata__ or {}).get("chat_id") or ""
            assistant_id = body.get("id") or ""
            messages = body.get("messages") or []
            if not messages:
                return body

            # Exempt internal subagent chats (verifiers) — they are not Tutor/Clerk teaching
            # and must not be recursively gated. This prevents verifier BLOCKED loops.
            try:
                if chat_id and __user__ and __user__.get("id"):
                    from open_webui.models.chats import Chats as _ChatsExempt

                    _c = await _ChatsExempt.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                    if _c and (_c.meta or {}).get("internal") is True:
                        return body
                    # Also exempt if body came from a subagent invocation (internal parent)
                    if _c and (_c.meta or {}).get("type") == "subagent":
                        return body
            except Exception:
                pass

            is_tutor = _is_tutor_preset(model_id, valves)
            is_clerk = _is_clerk_preset(model_id, valves)
            if not is_tutor and not is_clerk:
                scout_prefix = getattr(valves, "scout_name_prefix", "Scout").lower()
                if scout_prefix in (model_id or "").lower():
                    return body
                return body

            repo_root = _get_repo_root(valves, body)
            assistant_msg = None
            for m in messages:
                if m.get("id") == assistant_id:
                    assistant_msg = m
                    break
            if not assistant_msg and messages:
                assistant_msg = messages[-1]
                assistant_id = assistant_msg.get("id") or assistant_id

            content = assistant_msg.get("content") or ""
            if isinstance(content, list):
                content = "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
            content_str = str(content)

            # If no request/DB available, fail open (don't block unsaved/temp chats)
            if __request__ is None or not chat_id or not __user__ or not __user__.get("id"):
                return body

            # Fetch full chat history from DB
            chat_history = {}
            parent_user_id = None
            parent_user_text = ""
            try:
                from open_webui.models.chats import Chats

                chat = await Chats.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                if chat and getattr(chat, "chat", None):
                    hist = (chat.chat or {}).get("history", {}).get("messages", {}) or {}
                    chat_history = hist
                    parent_user_id, parent_user_text = _last_user_message(hist)
            except Exception as e:
                # Fail open on DB error — log and pass
                try:
                    import logging

                    logging.getLogger(__name__).debug(f"gate_pipe DB history fetch failed: {e}")
                except Exception:
                    pass
                return body

            # Turn-scoped retry state: reset if this is a new user turn
            try:
                from open_webui.models.chats import Chats as _Chats2

                chat_for_state = await _Chats2.get_chat_by_id_and_user_id(chat_id, __user__.get("id"))
                if chat_for_state:
                    state = (chat_for_state.meta or {}).get("gate_state") or {}
                    last_uid = state.get("last_user_msg_id")
                    if parent_user_id and last_uid and parent_user_id != last_uid:
                        # New turn — reset retries
                        await self._reset_gate_state(chat_id, __user__, __request__)
            except Exception:
                pass

            # Decide if this is a new-lesson trigger vs resume
            is_new_lesson_trigger = bool(TRIGGER_RE.search(parent_user_text or ""))
            # Derive slug from topic (first line) for digest lookup
            topic = _extract_topic(parent_user_text)
            slug = _slugify(topic) if topic else _slugify(parent_user_text)

            has_lesson_file = False
            if slug and slug != "lesson":
                lessons_dir = Path(repo_root) / "Learning System" / "Lessons"
                if lessons_dir.exists():
                    for p in lessons_dir.glob("*.md"):
                        if slug in _slugify(p.stem):
                            has_lesson_file = True
                            break
            else:
                # Empty/generic slug — check if any lesson exists for this chat's recent topic is unreliable;
                # treat as no lesson file so digest check can proceed via fallback
                has_lesson_file = False

            # Gate 1: Scout digest required only for new-lesson Tutor turns
            if is_tutor and is_new_lesson_trigger and not has_lesson_file:
                digest = _find_digest(chat_id, slug, getattr(valves, "digest_ttl_days", 7), repo_root)
                has_scout_msg = any(_is_scout_message(m, valves) for m in chat_history.values())
                # If repo filesystem is not mounted in Open WebUI (common: /home/user is in
                # open-terminal volume, not open-webui), digest will be None even when Scout
                # succeeded. In that case, rely on SCOUT DIGEST message alone (graceful degrade)
                # rather than permanently blocking new lessons.
                digest_base = Path(repo_root) / "Learning System" / TMP_DIR
                repo_unavailable = not digest_base.exists()
                if repo_unavailable and has_scout_msg:
                    # Fail open for file part — message proves Scout ran
                    pass
                elif not digest or not has_scout_msg:
                    blocked = (
                        f"⛔ BLOCKED (NO_SCOUT_CONTEXT) — No Scout digest found for this lesson (`{slug}`).\n\n"
                        f"Switch to your **{getattr(valves, 'scout_name_prefix', 'Scout')}** preset in this same chat and gather context for: `{parent_user_text[:120]}`.\n"
                        f"Then switch back to **{getattr(valves, 'tutor_name_prefix', 'Tutor')}** and retry. "
                        f"Digest expected at `Learning System/.tmp/context-{chat_id}-{slug}.json` (7-day TTL)."
                    )
                    should_retry, cap_msg = await self._check_retry_cap(chat_id, __user__, __request__, parent_user_id)
                    if not should_retry:
                        blocked = cap_msg or getattr(valves, "blocked_banner", "⛔ Withheld: not independently verified.")
                    else:
                        # Record this attempt against the current user turn
                        await self._bump_gate_state(chat_id, __user__, __request__, "NO_SCOUT_CONTEXT", parent_user_id)
                    assistant_msg["content"] = blocked
                    return body

            # Gate 2: Per-generation receipts — Tutor is multi-turn; Clerk single-turn
            needs_fact_check, needs_quiz_audit, needs_review = _gate_needs(
                content_str, is_tutor, is_clerk
            )
            needs_receipt = any((needs_fact_check, needs_quiz_audit, needs_review))

            if not needs_receipt:
                # Trivial messages don't need receipts, but don't reset turn-scoped cap here
                # (that would allow gaming via short acks). Only valid receipts reset.
                return body

            child_chats = await self._fetch_child_chats(chat_id, assistant_id, __user__)
            if child_chats is None:
                return body  # fail open on DB error (helper already logged)

            # Validate receipts per role — Tutor is per-generation (fix 2026-09-01):
            # each Tutor message that contains claims must have a fresh fact_check,
            # each that contains a quiz must have a fresh quiz_audit. An upfront
            # Plan batch never covers later steps, and quiz_audit never covers claims.
            found_fact_check = False
            found_quiz_audit = False
            found_review = False
            reject_code = "NO_DELEGATION"
            reject_detail = "No foreground GATE envelope dispatched via delegate_task for this generation. Each Tutor step needs its own fresh receipt (parent_message_id == this message)."

            if child_chats:
                for ch in child_chats:
                    # Foreground check via meta.mode (authoritative) + done flag
                    mode = (ch.get("mode") or "").lower()
                    is_background = mode == "background" or mode == "async"
                    if is_background or not ch.get("done"):
                        # Background or not yet done — not a valid receipt for this gate
                        reject_code = "MALFORMED_ENVELOPE"
                        reject_detail = "Gate must be foreground (background:false) and completed before presenting. Retry with foreground delegate_task."
                        continue

                    task = ch.get("task") or ""
                    verd_text = ch.get("content") or ""
                    data = _parse_gate_envelope(task)
                    if not data or not isinstance(data, dict) or "gate" not in data:
                        reject_code = "MALFORMED_ENVELOPE"
                        reject_detail = "GATE envelope must be JSON with gate field (fact_check | review | quiz_audit)"
                        continue
                    gate_type = data.get("gate")

                    if gate_type == "fact_check" and is_tutor:
                        ok, code, detail = _check_fact_check(data, verd_text)
                        if ok:
                            found_fact_check = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "quiz_audit" and is_tutor:
                        ok, code, detail = _check_quiz_audit(data, verd_text)
                        if ok:
                            found_quiz_audit = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    if gate_type == "review" and is_clerk:
                        ok, code, detail = _check_review(data, verd_text)
                        if ok:
                            found_review = True
                        else:
                            reject_code, reject_detail = code, detail
                        continue

                    # Cross-role envelope: e.g., quiz_audit on Clerk — treat as invalid gate for that role
                    reject_code = "MALFORMED_ENVELOPE"
                    reject_detail = f"Gate type '{gate_type}' not valid for this preset ({model_id})"
                    continue

            # Evaluate per-generation requirement (Tutor only)
            if is_tutor:
                # Tutor: each generation needs fresh receipt matching its content type.
                # Mixed claims+quiz needs BOTH. Upfront Plan batch never covers later steps.
                if needs_fact_check and needs_quiz_audit:
                    if found_fact_check and found_quiz_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    if not found_fact_check and not found_quiz_audit:
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Mixed claims+quiz message requires BOTH fact_check and quiz_audit receipts for this generation (parent_message_id == this message). Dispatch both foreground GATE envelopes before presenting."
                    elif not found_fact_check:
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Per-generation fact_check required before this teaching step (mixed message). Dispatch a foreground GATE:fact_check for the claims in THIS generation. Upfront Plan verification does not cover Teach steps, and quiz_audit does not cover claims."
                    else:  # found_fact_check but not found_quiz_audit
                        reject_code = "NO_DELEGATION"
                        reject_detail = "Quiz part of this mixed message requires GATE:quiz_audit receipt for this generation (parent_message_id == this message)."
                elif needs_fact_check:
                    if found_fact_check:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Per-generation fact_check required before this teaching step. Dispatch a foreground GATE:fact_check for the claims you are about to present in THIS generation (parent_message_id == this message). Upfront Plan verification does not cover Teach steps, and quiz_audit does not cover claims."
                elif needs_quiz_audit:
                    if found_quiz_audit:
                        await self._reset_gate_state(chat_id, __user__, __request__)
                        return body
                    reject_code = "NO_DELEGATION"
                    reject_detail = "Quiz batch requires GATE:quiz_audit receipt for this generation (parent_message_id == this message). Dispatch foreground quiz_audit before presenting questions."
                else:
                    # Non-trivial but heuristics missed — treat as needs fact_check
                    pass
            elif is_clerk:
                if found_review:
                    await self._reset_gate_state(chat_id, __user__, __request__)
                    return body
            else:
                # Should not reach here (Scout exempt)
                return body

            # No valid receipt — check cap and block
            should_retry, cap_msg = await self._check_retry_cap(chat_id, __user__, __request__, parent_user_id)
            if not should_retry:
                assistant_msg["content"] = cap_msg or getattr(valves, "blocked_banner", "⛔ Withheld: not independently verified.")
                return body

            if is_tutor:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Learning Tutor is multi-turn: **each generation** needs its own fresh GATE receipt before you emit it (parent_message_id must equal this message's id). Do NOT reuse an upfront Plan batch for later Teach steps.\n\n"
                    f"For teaching claims in THIS step:\n"
                    f"```json\n"
                    f'{{\n  "gate": "fact_check",\n  "claims": [{{"id": 1, "claim": "load-bearing claim for THIS step"}}],\n'
                    f'  "source_urls": ["https://rohit-source...", "https://external-ref..."],\n'
                    f'  "reference_excerpt": "digest excerpts for THIS step",\n'
                    f'  "context": "what THIS step teaches"\n}}\n```\n'
                    f"For question batches in THIS generation:\n"
                    f"```json\n"
                    f'{{\n  "gate": "quiz_audit",\n  "questions_json": [{{"id":"q1","type":"mcq","question":"...","options":["a","b","c","d"],"correct_index":1,"target_bloom":"Apply"}}],\n'
                    f'  "purpose": "probe", "concept": "Concept", "source_excerpt": "..."\n}}\n```\n'
                    f"Mixed claims+quiz needs BOTH receipts for the same message. Subagent prompt is fixed via global subagents.system_prompt — send data only."
                )
            else:
                detail_help = (
                    f"⛔ BLOCKED ({reject_code}) — {reject_detail}\n\n"
                    f"Dispatch a foreground GATE:review envelope via delegate_task:\n"
                    f"```json\n"
                    f'{{\n  "gate": "review",\n  "concepts": ["Concept"],\n  "wiki_content": "...",\n'
                    f'  "source_url": "https://...",\n  "lesson_ref": "Lessons/...md"\n}}\n```'
                )

            assistant_msg["content"] = detail_help
            await self._bump_gate_state(chat_id, __user__, __request__, reject_code, parent_user_id)
            return body

        except Exception as e:
            # Fail open on unexpected gate internal error — don't block learner on bug
            try:
                import logging

                logging.getLogger(__name__).exception(f"gate_pipe outlet error: {e}")
            except Exception:
                pass
            return body

    # -----------------------------------------------------------------------
    # Gate state helpers (Chat.meta.gate_state) — per user turn
    # -----------------------------------------------------------------------

    async def _check_retry_cap(self, chat_id: str, user: dict | None, request, parent_user_msg_id: str | None):
        """Returns (should_retry: bool, cap_banner: str|None). Per-turn: different parent user msg resets."""
        try:
            if not chat_id or not user or request is None:
                return True, None
            from open_webui.models.chats import Chats

            chat = await Chats.get_chat_by_id_and_user_id(chat_id, user.get("id"))
            if not chat:
                return True, None
            state = (chat.meta or {}).get("gate_state") or {}
            # If turn changed, we wouldn't be here (reset happens at top), but handle stale state
            if parent_user_msg_id and state.get("last_user_msg_id") and state["last_user_msg_id"] != parent_user_msg_id:
                return True, None
            retries = int(state.get("retries", 0))
            max_retries = int(getattr(self.valves, "max_retries", 2))
            if retries >= max_retries:
                return False, getattr(self.valves, "blocked_banner", "⛔ Withheld: not independently verified — retry limit reached. Fix the GATE envelope and retry.")
            return True, None
        except Exception:
            return True, None

    async def _bump_gate_state(self, chat_id: str, user: dict | None, request, code: str, parent_user_msg_id: str | None):
        try:
            if not chat_id or not user or request is None:
                return
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat
            from sqlalchemy import select

            async with get_async_db() as db:
                result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.get("id")))
                row = result.scalars().first()
                if not row:
                    return
                meta = dict(row.meta or {})
                state = dict(meta.get("gate_state") or {})
                # If turn changed since last bump, reset first
                if parent_user_msg_id and state.get("last_user_msg_id") and state["last_user_msg_id"] != parent_user_msg_id:
                    state = {}
                state["retries"] = int(state.get("retries", 0)) + 1
                state["last_code"] = code
                state["last_at"] = int(time.time())
                if parent_user_msg_id:
                    state["last_user_msg_id"] = parent_user_msg_id
                meta["gate_state"] = state
                row.meta = meta
                await db.commit()
        except Exception:
            pass

    async def _reset_gate_state(self, chat_id: str, user: dict | None, request):
        try:
            if not chat_id or not user or request is None:
                return
            from open_webui.internal.db import get_async_db
            from open_webui.models.chats import Chat
            from sqlalchemy import select

            async with get_async_db() as db:
                result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.get("id")))
                row = result.scalars().first()
                if not row or not (row.meta or {}).get("gate_state"):
                    return
                meta = dict(row.meta or {})
                meta.pop("gate_state", None)
                row.meta = meta
                await db.commit()
        except Exception:
            pass
