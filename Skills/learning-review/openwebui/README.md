# Review Gate — Open WebUI setup

This folder is the Open WebUI adaptation of the original `bun run review.ts` gate.
It does the same job with Open WebUI-native parts:

| Original (Zo) | Open WebUI equivalent |
| --- | --- |
| `bun run Skills/learning-review/scripts/review.ts` | Tool `review_gate` (`review_gate.py`), called from chat |
| `/zo/ask` + `byok:...` model | Open WebUI `/api/chat/completions` + any model id |
| `model-config.json` (`review_model`) | `model-config.json` here + Tool Valves / env vars |
| `templates/review.template.md` (owned by script) | `../templates/review.template.md` (mirrored inside the tool) |
| Verdict JSON → `Learning System/Reviews/Quality Gates/` | Tool returns the same JSON; the chat saves it to the same folder |

## Install (one time, ~2 minutes)

1. **Open WebUI** → Admin Panel → **Workspace** → **Tools** → **+** (Create Tool).
2. Paste the entire contents of `review_gate.py` into the code box.
3. Name it `review_gate` (the tool name the model will call) → **Save**.
4. **Your profile** → Settings → **Tools** → enable `review_gate`.
5. Open the tool (pencil) → **Valves** and set:
   - `openwebui_base_url` — e.g. `http://localhost:3000` (or your public URL)
   - `openwebui_api_key` — generate one in **Admin Panel → API Keys**
   - `review_model` — any model id your instance can serve, e.g. `gpt-4o` or `llama3.1:8b`
   - `repo_path` — absolute path to this repo **on the Open WebUI server** if you
     cloned it there (e.g. `/home/delight/learning-system`). If empty, wiki-path
     validation is skipped (still safe — the chat shows you the content anyway).

   Environment-variable fallbacks (same names, prefixed where noted) work if you
   prefer not to use Valves: `OPENWEBUI_BASE_URL`, `OPENWEBUI_API_KEY`,
   `REVIEW_GATE_MODEL`, `LEARNING_REPO_PATH`.

## Usage — terminal CLI (preferred: independent second model)

`gate_cli.py` runs the same gate from the terminal, calling a second model
(Mimo v2.5 by default) in Open WebUI — so the reviewer is independent of the
chat model:

```bash
python3 Skills/learning-review/openwebui/gate_cli.py \
  --source "https://missing.csail.mit.edu/2026/course-shell/" \
  --concepts "awk,Pipes" \
  --wiki "Knowledge Wiki/wiki/MIT Missing Semester — Shell.md" \
  --model "mimo-v2.5" \
  --base-url "http://host.docker.internal:3000" \
  --pass-number 1
```

- API key: env `OPENWEBUI_API_KEY`, or a file `~/.config/learning-system/openwebui_key`
  (0600). Never on the command line.
- Exit codes: 0 = PASS, 1 = ISSUES, 2 = error/no verdict.
- Save the printed verdict to
  `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json`
  (match the naming of the existing files in that folder).

## Usage — Tool (optional, same logic in-chat)

You can also call the `review_gate` tool from chat with the same arguments
(source, concepts, wiki_paths, pass_number). The Tool reads the same key
(Valve `openwebui_api_key` or env `OPENWEBUI_API_KEY`) and returns the same JSON.

## If the tool cannot be installed

Use the **in-chat fallback** from `../SKILL.md` step 2: the chat model plays the
independent reviewer using `../templates/review.template.md` against the fetched
source and the wiki text — same rules, same severity scale, same 2-cycle cap.
You lose only the "separate model" independence; the process is otherwise identical.

## Troubleshooting

- **"wiki path(s) do not exist"** — you passed a path you didn't write, or
  `repo_path` points somewhere else. Fix the path, re-run. Never pass a path you
  have not actually written.
- **"could not fetch source URL"** — dead/unstable URL. Use a stable URL (raw
  GitHub, course page), not a workspace path or a session link.
- **HTTP 401 on the model call** — wrong/expired API key.
- **HTTP 404 on /api/chat/completions** — wrong `openwebui_base_url` or your
  Open WebUI version exposes a different path; check Admin → API docs.
