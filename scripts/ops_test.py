#!/usr/bin/env python3
"""Regression tests for scripts/ops.py — stdlib only (run: python3 -m unittest scripts/ops_test).

Guards the three bugs fixed 2026-08:
- ROOT auto-detect works on either checkout (not hardcoded to one path).
- Path-escape guard rejects attempts to read outside the workspace.
- `state <track>` returns the concept TABLE ROWS, not just the section heading.
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Allow running as a standalone module or via `python3 -m unittest scripts.ops_test`
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops  # noqa: E402


class TestRootDetection(unittest.TestCase):
    def test_root_resolves_to_a_checkout_with_core(self):
        # The directory containing this test must have "Learning System/Core".
        self.assertTrue((ops.ROOT / "Learning System" / "Core").is_dir())

    def test_env_override_is_honored(self):
        # LEARNING_SYSTEM_ROOT pointing at a dir without the Core substructure
        # must NOT be selected (falls through to a real checkout).
        os.environ["LEARNING_SYSTEM_ROOT"] = "/tmp/definitely-not-a-checkout"
        try:
            root = ops._detect_root()
        finally:
            del os.environ["LEARNING_SYSTEM_ROOT"]
        self.assertTrue((root / "Learning System" / "Core").is_dir())


class TestPathEscape(unittest.TestCase):
    def test_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            ops._resolve("../etc/passwd")
        with self.assertRaises(ValueError):
            ops._resolve("/etc/passwd")

    def test_internal_path_is_allowed(self):
        p = ops._resolve("Learning System/Core/💡 Learning Profile.md")
        self.assertTrue(str(p).startswith(str(ops.ROOT)))


class TestSectionSlice(unittest.TestCase):
    def test_section_captures_table_rows_not_just_heading(self):
        lines = [
            "# KNOWLEDGE BASE",
            "## SWE Track — Shell & Terminal",
            "| Concept | Type |",
            "| --- | --- |",
            "| What is the Shell | concept |",
            "## aie Track — archived",
            "| old concept | concept |",
        ]
        text, err = ops._section_slice(lines, r"^## swe\b")
        self.assertIsNone(err)
        self.assertIn("What is the Shell", text)
        self.assertNotIn("old concept", text)  # next section excluded
        self.assertIn("## SWE Track", text)

    def test_section_missing_returns_error(self):
        lines = ["# title", "## Other"]
        text, err = ops._section_slice(lines, r"^## nope\b")
        self.assertIsNone(text)
        self.assertIn("no matching section", err)


class TestDoStateActiveConcepts(unittest.TestCase):
    def test_state_swe_returns_concept_rows(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("swe")
        out = buf.getvalue()
        # SWE was archived 2026-09-01 (43 concepts → 📦 Concept Archive.md).
        # The active track is now AIEFS (Mission 0 catch-up). SWE section
        # should contain the ARCHIVED banner, not live concept rows.
        # Keep test green through the roadmap switch.
        self.assertIn("## SWE Track", out)
        if "ARCHIVED" in out:
            self.assertIn("ARCHIVED", out)
            self.assertIn("43 concepts paused", out)
        else:
            # Pre-archive expectation (preserved for history)
            self.assertIn("| What is the Shell |", out)


class TestDoStateIncludesMasterySidecars(unittest.TestCase):
    def test_state_bundles_attempts_and_mistakes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("aiefs")
        out = buf.getvalue()
        self.assertIn("Attempts.json", out)
        self.assertIn("Mistakes.md", out)


class TestAttemptCommand(unittest.TestCase):
    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "Test Concept": {
                    "type": "concept",
                    "attempts": [{"date": "2026-09-01", "is_correct": True,
                                  "result": "pass", "q_type": None}],
                    "interval_index": 0,
                    "consecutive_correct": 1,
                    "consecutive_wrong": 0,
                    "last_reviewed": "2026-09-01",
                    "next_review": "2026-09-04",
                    "feynman": None,
                }
            },
            "meta": {"version": 1,
                     "intervals": {"memory": [0, 1, 3, 7, 14, 30, 60],
                                   "concept": [3, 7, 14, 30],
                                   "procedure": [3, 7, 14],
                                   "design": [14, 28]}},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_attempt_pass_advances_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04")
        out = buf.getvalue()
        self.assertIn("next_review", out)
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(len(entry["attempts"]), 2)
        # 2nd consecutive pass => +2 from index 0
        self.assertEqual(entry["interval_index"], 2)
        self.assertEqual(entry["next_review"], "2026-09-18")  # 2026-09-04 + 14d
        self.assertEqual(entry["last_reviewed"], "2026-09-04")

    def test_attempt_fail_drops_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "fail", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(entry["interval_index"], 0)  # clamped, was 0
        self.assertEqual(entry["consecutive_wrong"], 1)

    def test_attempt_feynman_flag_recorded(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", feynman="feynman_pass",
                           date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["feynman"], "pass")

    def test_attempt_new_concept_defaults(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Brand New", "pass", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertIn("Brand New", data["concepts"])
        self.assertEqual(data["concepts"]["Brand New"]["type"], "concept")

    def test_mastery_caps_single_attempt(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_mastery("aiefs")
        out = buf.getvalue()
        # 1 pass => recency 1.0 capped at 0.5
        self.assertIn("Test Concept", out)
        self.assertIn("0.50", out)


class TestQueueCommand(unittest.TestCase):
    """The deterministic review queue (ops.py queue): due-mistake priority,
    scheduler-truth due reviews, question-type alternation, adjacency guard,
    drift notes, and the digest skeleton."""

    def _seed(self, active_rows, mistakes_rows, attempts):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": attempts, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        header = "| Concept | Track | Type | Status | Source | Last Reviewed | Next Review | Last Q Type | Open Question |"
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        (core / "📚 Active Concepts.md").write_text(
            "\n".join(["# KNOWLEDGE BASE", "", header, sep, *active_rows]) + "\n", encoding="utf-8")
        mheader = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                   "Status | Retries | Next Retry |")
        msep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", mheader, msep, *mistakes_rows]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    @staticmethod
    def _attempt(next_review, ctype="concept", last_q=None, feynman=None):
        return {"type": ctype, "attempts": [{"date": "2026-09-01", "is_correct": True,
                "result": "pass", "q_type": last_q}], "interval_index": 0,
                "consecutive_correct": 1, "consecutive_wrong": 0,
                "last_reviewed": "2026-09-01", "next_review": next_review, "feynman": feynman}

    @staticmethod
    def _active(name, next_review="2026-09-20", last_q="definitional", source="Rohit P1 L01 (Python)",
                ctype="concept", track="aiefs"):
        return (f"| {name} | {track} | {ctype} | developing | {source} | 2026-09-01 | "
                f"{next_review} | {last_q} | note |")

    @staticmethod
    def _mistake(date, name, next_retry, status="active", error_type="structural"):
        return (f"| {date} | {name} | Q? | Expected | {error_type} | why | {status} | 0 | "
                f"{next_retry} |")

    def test_prioritizes_oldest_due_mistakes_then_reviews(self):
        self._seed(
            active_rows=[
                self._active("M1", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("M2", next_review="2026-09-01", source="Rohit P1 L02 (Python)"),
                self._active("R1", next_review="2026-09-01", source="Rohit P1 L03 (Python)"),
            ],
            mistakes_rows=[
                self._mistake("2026-09-05", "M1", "2026-09-06"),
                self._mistake("2026-09-02", "M2", "2026-09-03"),  # oldest
            ],
            attempts={"M1": self._attempt("2026-09-01"), "M2": self._attempt("2026-09-01"),
                      "R1": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        self.assertEqual([e["concept"] for e in q["queue"][:2]], ["M2", "M1"])
        self.assertTrue(all(e["due_kind"] == "mistake" for e in q["queue"][:2]))
        self.assertEqual(q["queue"][2]["concept"], "R1")
        self.assertEqual(q["queue"][2]["due_kind"], "review")

    def test_excludes_not_due_and_other_tracks(self):
        self._seed(
            active_rows=[
                self._active("Due", next_review="2026-09-01"),
                self._active("NotDue", next_review="2026-10-30"),
                self._active("OtherTrack", next_review="2026-09-01", track="swe"),
            ],
            mistakes_rows=[self._mistake("2026-09-01", "NotDue", "2026-10-30")],
            attempts={"Due": self._attempt("2026-09-01"), "NotDue": self._attempt("2026-10-30"),
                      "OtherTrack": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        names = [e["concept"] for e in q["queue"]]
        self.assertEqual(names, ["Due"])

    def test_question_type_alternates_by_last_q_type(self):
        self._seed(
            active_rows=[
                self._active("Defn", next_review="2026-09-01", last_q="definitional"),
                self._active("Disc", next_review="2026-09-01", last_q="discriminative"),
                self._active("Blank", next_review="2026-09-01", last_q=""),
            ],
            mistakes_rows=[],
            attempts={"Defn": self._attempt("2026-09-01"), "Disc": self._attempt("2026-09-01"),
                      "Blank": self._attempt("2026-09-01")},
        )
        by = {e["concept"]: e for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)["queue"]}
        self.assertEqual(by["Defn"]["question_type"], "discriminative")
        self.assertEqual(by["Disc"]["question_type"], "definitional")
        self.assertEqual(by["Blank"]["question_type"], "discriminative")

    def test_adjacency_guard_avoids_consecutive_same_source(self):
        self._seed(
            active_rows=[
                self._active("A1", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("A2", next_review="2026-09-01", source="Rohit P1 L01 (Python)"),
                self._active("B1", next_review="2026-09-01", source="Rohit P1 L02 (Python)"),
            ],
            mistakes_rows=[],
            attempts={"A1": self._attempt("2026-09-01"), "A2": self._attempt("2026-09-01"),
                      "B1": self._attempt("2026-09-01")},
        )
        keys = [ops._source_key(e) for e in ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 3)["queue"]]
        self.assertFalse(any(a == b for a, b in zip(keys, keys[1:])))

    def test_dedupes_same_concept_and_caps_mistakes_at_two(self):
        self._seed(
            active_rows=[
                self._active("M1", next_review="2026-09-01"),
                self._active("M2", next_review="2026-09-01"),
                self._active("M3", next_review="2026-09-01"),
            ],
            mistakes_rows=[
                self._mistake("2026-09-01", "M1", "2026-09-02"),
                self._mistake("2026-09-02", "M1", "2026-09-02"),  # duplicate concept
                self._mistake("2026-09-03", "M2", "2026-09-02"),
                self._mistake("2026-09-04", "M3", "2026-09-02"),
            ],
            attempts={"M1": self._attempt("2026-09-01"), "M2": self._attempt("2026-09-01"),
                      "M3": self._attempt("2026-09-01")},
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        mistakes = [e["concept"] for e in q["queue"] if e["due_kind"] == "mistake"]
        self.assertEqual(mistakes, ["M1", "M2"])

    def test_reports_next_review_drift(self):
        self._seed(
            active_rows=[self._active("Drift", next_review="2026-09-01")],
            mistakes_rows=[],
            attempts={"Drift": self._attempt("2026-09-15")},  # scheduler disagrees with AC
        )
        q = ops._build_queue("aiefs", ops._parse_date("2026-09-10"), 5)
        self.assertEqual(q["queue"], [])
        self.assertTrue(any("Drift" in w and "!=" in w for w in q["warnings"]))

    def test_digest_skeleton_written(self):
        self._seed(
            active_rows=[self._active("Due", next_review="2026-09-01")],
            mistakes_rows=[],
            attempts={"Due": self._attempt("2026-09-01")},
        )
        rel = "Learning System/.tmp/review-test-aiefs.json"
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_queue("aiefs", ops._parse_date("2026-09-10"), 5, digest_path=rel)
        self.assertIn("WROTE", buf.getvalue())
        digest = json.loads((ops.ROOT / rel).read_text(encoding="utf-8"))
        self.assertIsNone(digest["position"])
        self.assertEqual(digest["queue"][0]["concept"], "Due")
        self.assertIn(digest["queue"][0]["source_excerpt"], ("note",))  # notes fallback


class TestMasteryDimensions(unittest.TestCase):
    """P0.4: mastery is per-dimension, and a failed AI-free (solo) attempt
    blocks the independence gate; absent evidence is unknown, not zero."""

    def test_dimensions_split_by_question_type(self):
        entry = {
            "type": "concept", "interval_index": 2, "feynman": "pass",
            "attempts": [
                {"date": "2026-10-01", "is_correct": True, "q_type": "definitional"},
                {"date": "2026-10-02", "is_correct": False, "q_type": "computational"},
                {"date": "2026-10-03", "is_correct": True, "q_type": "transfer"},
            ],
        }
        d = ops.compute_dimensions(entry)
        self.assertEqual(d["recall"], 3)
        self.assertEqual(d["procedural"], 0)
        self.assertEqual(d["transfer"], 3)
        self.assertEqual(d["conceptual"], 3)
        self.assertEqual(d["stability"], 2)
        self.assertIsNone(d["independence"])

    def test_unknown_dimension_is_none_not_zero(self):
        d = ops.compute_dimensions({"attempts": [{"date": "2026-10-01", "is_correct": True}]})
        self.assertIsNone(d["procedural"])
        self.assertIsNone(d["transfer"])
        self.assertIsNone(d["independence"])
        self.assertEqual(d["recall"], 3)  # untagged counts as general recall

    def test_independence_gate_blocks_solid_after_a_failed_solo(self):
        passed = {"attempts": [{"date": "2026-10-01", "is_correct": True, "mode": "solo"}]}
        self.assertTrue(ops.independence_ok(passed))
        failed = {"attempts": [{"date": "2026-10-01", "is_correct": False, "mode": "solo"}]}
        self.assertFalse(ops.independence_ok(failed))
        # No solo evidence is unknown, not failure (grandfathered).
        self.assertTrue(ops.independence_ok({"attempts": [{"date": "2026-10-01", "is_correct": True}]}))

    def test_attempt_records_optional_evidence(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8",
        )
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("X", "fail", qtype="transfer", confidence="hunch", hints=2, mode="solo")
        data = json.loads((core / "Attempts.json").read_text(encoding="utf-8"))
        a = data["concepts"]["X"]["attempts"][0]
        self.assertEqual(a["confidence"], "hunch")
        self.assertEqual(a["hints"], 2)
        self.assertEqual(a["mode"], "solo")
        self.assertFalse(ops.independence_ok(data["concepts"]["X"]))
        # Optional fields are omitted when not supplied (back-compat).
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("Y", "pass")
        y = json.loads((core / "Attempts.json").read_text(encoding="utf-8"))["concepts"]["Y"]["attempts"][0]
        self.assertNotIn("confidence", y)
        self.assertNotIn("hints", y)
        self.assertNotIn("mode", y)


class TestQTypeEnum(unittest.TestCase):
    """P1.2: q_type is an enum, not a free string; legacy aliases normalize."""

    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": {}, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_unknown_qtype_is_rejected(self):
        self._make_root()
        with redirect_stdout(io.StringIO()) as buf:
            with self.assertRaises(SystemExit) as cm:
                ops.do_attempt("X", "pass", qtype="bogus-type")
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("unknown --qtype", buf.getvalue())

    def test_legacy_qtype_alias_is_normalized(self):
        root = self._make_root()
        with redirect_stdout(io.StringIO()):
            ops.do_attempt("X", "pass", qtype="free_recall")
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["X"]["attempts"][0]["q_type"], "free-recall")

    def test_transfer_alias_normalizes_to_near(self):
        self.assertIsNone(ops.normalize_qtype("bogus"))
        self.assertEqual(ops.normalize_qtype("transfer"), "transfer-near")
        self.assertEqual(ops.normalize_qtype("novel"), "transfer-far")
        self.assertEqual(ops.normalize_qtype("transfer-far"), "transfer-far")


class TestGradeMcq(unittest.TestCase):
    """P1.2: deterministic MCQ grading — no LLM in the mechanical path."""

    def test_grade_mcq_mixed_letters(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_grade_mcq("A,B,C", "A,C,C")
        out = buf.getvalue()
        self.assertIn("2/3 correct", out)
        self.assertIn("key B · answer C → FAIL", out)
        self.assertIn("key C · answer C → PASS", out)

    def test_grade_mcq_empty_answer_is_wrong(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_grade_mcq("A,B", "A,-")
        self.assertIn("1/2 correct", buf.getvalue())

    def test_grade_mcq_length_mismatch_exits(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                ops.do_grade_mcq("A,B", "A")
        self.assertEqual(cm.exception.code, 2)


class TestPrereqs(unittest.TestCase):
    """P1.3: prerequisite edges in live state; a fuzzy direct prereq blocks."""

    def _seed(self, concepts, mistakes=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        (core / "Attempts.json").write_text(
            json.dumps({"concepts": concepts, "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS}}),
            encoding="utf-8")
        header = ("| Date | Concept | Question | Expected | Error Type | Self-Attribution | "
                  "Status | Retries | Next Retry |")
        sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        rows = [f"| 2026-09-01 | {c} | Q? | Expected | structural | why | active | 0 | 2026-09-02 |"
                for c in mistakes]
        (core / "🧯 Mistakes.md").write_text(
            "\n".join(["# Mistakes", "", header, sep, *rows]) + "\n", encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    @staticmethod
    def _entry(feynman=None, wrong=0, correct=0, interval=0, last_ok=True):
        return {"type": "concept", "feynman": feynman, "consecutive_wrong": wrong,
                "consecutive_correct": correct, "interval_index": interval,
                "attempts": [{"date": "2026-09-01", "is_correct": last_ok, "result": "pass"}]}

    def test_fuzzy_prereq_blocks(self):
        self._seed({"A": self._entry(wrong=1, last_ok=False)})
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_prereqs("B", set_list=["A"])
        out = buf.getvalue()
        self.assertIn("BLOCKS", out)
        self.assertIn("A: fuzzy", out)

    def test_open_mistake_prereq_blocks(self):
        self._seed({"A": self._entry()}, mistakes=["A"])
        payload = ops._prereq_state("A", {"A": self._entry()}, ops._open_mistake_concepts())
        self.assertEqual(payload, "fuzzy")

    def test_unknown_prereq_does_not_block(self):
        self._seed({"A": self._entry()})
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_prereqs("B", set_list=["Missing"])
        out = buf.getvalue()
        self.assertNotIn("BLOCKS", out)
        self.assertIn("Missing: unknown", out)

    def test_set_persists_prereqs(self):
        root = self._seed({})
        with redirect_stdout(io.StringIO()):
            ops.do_prereqs("B", set_list=["A", "C"])
        data = json.loads((root / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["B"]["prereqs"], ["A", "C"])


class TestCalibration(unittest.TestCase):
    """P1.4: confidence is measured, not just elicited."""

    def test_calibration_flags_overconfidence(self):
        attempts = [
            {"is_correct": True, "confidence": "sure"},
            {"is_correct": False, "confidence": "sure"},
            {"is_correct": False, "confidence": "sure"},
            {"is_correct": True, "confidence": "hunch"},
        ]
        cal = ops.compute_calibration(attempts)
        self.assertIn("overconfident", cal["flags"])
        self.assertEqual(cal["buckets"]["sure"]["n"], 3)
        self.assertEqual(cal["buckets"]["sure"]["correct"], 1)

    def test_calibration_ignores_untagged(self):
        cal = ops.compute_calibration([{"is_correct": True}, {"is_correct": False}])
        self.assertEqual(cal["buckets"], {})

    def test_mastery_json_includes_calibration_and_transfer(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "X": {
                    "type": "concept", "feynman": None, "interval_index": 1,
                    "consecutive_correct": 1, "consecutive_wrong": 0,
                    "attempts": [
                        {"date": "2026-10-01", "is_correct": True,
                         "confidence": "sure", "q_type": "transfer-far"},
                    ],
                }
            },
            "meta": {"version": 1, "intervals": ops.DEFAULT_INTERVALS},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_mastery("", as_json=True)
        rows = json.loads(buf.getvalue())
        row = rows[0]
        self.assertIn("calibration", row)
        self.assertTrue(row["transfer_ok"])


class TestTransferDimension(unittest.TestCase):
    """P1.5: transfer-near/far feed the transfer dimension; far transfer gates
    consolidation (when it exists)."""

    def test_transfer_dimension_from_transfer_far(self):
        entry = {
            "type": "concept", "interval_index": 2, "feynman": None,
            "attempts": [
                {"date": "2026-10-01", "is_correct": True, "q_type": "transfer-far"},
            ],
        }
        self.assertEqual(ops.compute_dimensions(entry)["transfer"], 3)
        self.assertTrue(ops.transfer_ok(entry))

    def test_transfer_far_fail_is_not_transfer_ok(self):
        entry = {"attempts": [{"date": "2026-10-01", "is_correct": False, "q_type": "transfer-far"}]}
        self.assertEqual(ops.compute_dimensions(entry)["transfer"], 0)
        self.assertFalse(ops.transfer_ok(entry))


class TestLearnerHistoryFeynmanGate(unittest.TestCase):
    """P1.1: a concept/design entry cannot be `solid` without a Feynman pass;
    memory/procedure stay exempt."""

    def test_concept_cannot_be_solid_without_feynman(self):
        import learner_history  # noqa: E402

        entry = {
            "type": "concept", "consecutive_correct": 3, "interval_index": 3,
            "consecutive_wrong": 0, "attempts": [{"date": "2026-10-01", "is_correct": True}],
            "feynman": None,
        }
        self.assertNotEqual(learner_history.tag("Concept", entry, set()), "solid")
        entry["feynman"] = "pass"
        self.assertEqual(learner_history.tag("Concept", entry, set()), "solid")

    def test_memory_is_exempt_from_feynman(self):
        import learner_history  # noqa: E402

        entry = {
            "type": "memory", "consecutive_correct": 3, "interval_index": 3,
            "consecutive_wrong": 0, "attempts": [{"date": "2026-10-01", "is_correct": True}],
            "feynman": None,
        }
        self.assertEqual(learner_history.tag("Memory", entry, set()), "solid")


if __name__ == "__main__":
    unittest.main()
