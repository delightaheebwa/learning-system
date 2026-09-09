# VERSIONS — environment manifest (pin everything a fresh restore needs)

Generated 2026-09-08 from the live containers. Update this file whenever any
component changes (run `scripts/audit_openwebui.py` to detect drift).

## Images (pinned by digest — the live stack runs these exact bytes)

| Component | Image | Digest | Notes |
| --- | --- | --- | --- |
| Open WebUI | `ghcr.io/open-webui/open-webui:main` | `sha256:8afd2d77…2eb6e4` | version 0.11.3, build `2a960a59…781` |
| Open Terminal | `ghcr.io/open-webui/open-terminal` | `sha256:8df3a502…2538452` | terminal tool-server, port 8000; API key in `infra/.env` (gitignored — rotate it, it leaked into git history in an earlier commit) |
| SearXNG | `searxng/searxng:latest` | `sha256:892cf809…8750788d` | version 2026.8.14 |

## Ports

| Service | Container | Host |
| --- | --- | --- |
| Open WebUI | 8080 | 3000 |
| SearXNG | 8080 | 8080 |
| Open Terminal | 8000 | 8000 |

## Models (Open WebUI presets → base models, UI-owned)

| Preset | Base model | filterIds | toolIds |
| --- | --- | --- | --- |
| Scout | `mimo-v2.5` | [] | — |
| Learning Tutor | `deepseek-v4-pro` | [gate_pipe] | — (builtin `delegate_task` injected natively) |
| Clerk | `mimo-v2.5` | [gate_pipe] | — |

Providers (openai connections, from `webui.db` config): connection 1 = `https://opencode.ai/zen/go/v1`
(header `x-opencode-session: {{CHAT_ID}}`), connection 2 = `https://opencode.ai/zen/v1` (prefix `zen`).
Base model IDs float upstream — record current values here after any model change.

## Installed non-builtin items

| Item | Kind | Version | Source |
| --- | --- | --- | --- |
| gate_pipe | Function (Filter) | repo `Skills/learning-review/openwebui/` | installed by `scripts/setup_openwebui.py` |
| sub_agent ("Sub Agent") | Tool | v0.5.8 (skyzi000) | community tool — NOT used by the learning system (no background mode, no receipts); recorded for portability only |
| fact_check / quiz_gate / review_gate | Tools (legacy) | — | RETIRED 2026-08-25; files archived to `Learning System/Archive/legacy-tools-2026-08-25/` |

## Installer-seeded control layer (see scripts/setup_openwebui.py)

4 Skills · 3 presets · 7 prompts (`/swe /review /ingest /teach /lesson /continue /pause`) ·
gate_pipe Filter (valves: priority 10, max_retries 2, digest_ttl_days 7) ·
`subagents.system_prompt` (4 `GATE:` keys) · subagent config (enable, max_concurrent 10,
max_async 10, max_iterations 30, max_output 30000).

## Repo state

- GitHub origin: `https://github.com/delightaheebwa/learning-system` (public, branch `main`).
- Runtime checkout: named volume `open-terminal` → `/home/user/learning-system`.
- Maintenance checkout (this one): WSL `/home/delinux/learning-system`.

## Upgrade procedure

1. `infra/backup.sh` (volumes).
2. Bump the image tag/digest in `infra/docker-compose.yml` (check https://github.com/open-webui/open-webui/releases).
3. `docker compose -f infra/docker-compose.yml up -d`.
4. Re-run `scripts/setup_openwebui.py` (idempotent; re-seeds skills/prompts/function after image upgrades).
5. `scripts/audit_openwebui.py` → confirm repo↔live parity.
6. Smoke-test: new chat → `/teach` → Tutor must dispatch `delegate_task` and render without a BLOCKED banner.
