## 2026-08-19 — Ingest: Shell Config & Dotfiles + SSH passphrase (MIT Missing Semester Lecture 2, second half)

**Source:** https://missing.csail.mit.edu/2026/command-line-environment/ (MIT Missing Semester — shell customization + dotfiles + SSH)

**Concept added (1 new, SWE track, `developing`):**
- Shell Config & Dotfiles — hand-typed shell settings don't survive logout; persist them in `~/.bashrc` / `~/.bash_profile` (shell reads on startup). `source ~/.bashrc` evaluates the file line-by-line in the current shell (no re-login). `PS1` renders the left prompt (classic first dotfile tweak). Dotfiles = hidden plain-text config files (names start with `.`); collect them in one version-controlled folder (`~/.dotfiles`) and `ln -s` them into the standard locations via an install script → portable environment. Plugin frameworks (Oh My Zsh) can bloat/slow the shell — add one plugin at a time. `command-not-found.com` shows which package provides a command. `next_review` 2026-08-22 (+3d), Last Q Type definitional

**Concept enriched (1, SWE track):**
- SSH: Public-Key Auth & Remote Commands — passphrase point: a passphrase encrypts the private key FILE; without one the key is plain text, so anyone with filesystem access can copy and use it to log into your servers (no password needed). Validate with `ssh-keygen -y -f /path/to/key`. `last_reviewed` 2026-08-19, `next_review` 2026-08-22

**Wiki pages:** MIT Missing Semester — Shell Configuration & Dotfiles (created); SSH — Public-Key Auth & Remote Commands (enriched: passphrase section + 5th takeaway); index + log updated.

**Session note:** Session — Shell Config & Dotfiles Ingest — 2026-08-19.md
**Mastery Summary:** SWE 51 → 52 developing.
**Learning-review gate:** PASS on pass 2 (verdict JSONs in `Reviews/Quality Gates/Shell_Config_and_Dotfiles-SSH_Public-Key_Auth_and_Remote_Commands-pass{1,2}-2026-08-19.json`; model `minimax-m3`). Pass 1 flagged high/medium source-attribution concerns ($PS1/`ln -s`/`source`/Oh My Zsh/passphrase "not in source") — most of that material is genuinely in the static page (verified: `$PS1`, `ln -s`, `prezto`/`oh-my-zsh`, plugins) and the rest comes from the lecture video narration captured in the learner's notes, so the fix was a precise **scope/provenance note** distinguishing textbook-page content from lecture-video (learner-notes) content on both updated pages. Pass 2 returned PASS, 0 issues. **Factual gate passed:** bash config-file persistence, `source` line-by-line semantics, `$PS1` = primary prompt, the dotfile/symlink portable-environment convention, plugin-framework bloat, and the SSH-key passphrase-encrypts-the-file explanation are all standard, well-established shell facts.

## 2026-08-18 — Ingest: SSH Public-Key Auth & Remote Commands (MIT Missing Semester YouTube, Lecture 2)

**Source:** https://missing.csail.mit.edu/2026/command-line-environment/ (MIT Missing Semester — SSH + shell env content)

**Concept added (1 new, SWE track, `developing`):**
- SSH: Public-Key Auth & Remote Commands — public key (shareable; server uses it to verify you) vs private key (your secret, NEVER share ≈ password); `ssh host cmd` runs a command remotely with stdout streaming back; quoting decides where the pipe runs: `ssh host ls | wc -l` = run `ls` remotely + count locally, `ssh host 'ls | wc -l'` = entire pipeline remote (only result crosses the wire — run heavy stages where the data is). `next_review` 2026-08-21 (+3d, staggered with Pipes/Signals), Last Q Type definitional

**Concepts enriched (2, SWE track):**
- Pipes (`|`) & Pipeline Composition — pipeline stages run in **parallel** (all start at once, stream line-by-line; `grep | head` stops early once `head` has enough). `last_reviewed` 2026-08-18, `next_review` 2026-09-01 (7d→14d)
- Signals (Software Interrupts) — in practice only a handful of the ~30 signals are used (SIGINT/Ctrl-C, SIGTERM, SIGKILL, SIGTSTP, SIGHUP, SIGPIPE); know the common set, not the whole list. `last_reviewed` 2026-08-18

**Wiki pages:** SSH — Public-Key Auth & Remote Commands (created); MIT Missing Semester — Shell (enriched: pipe parallelism + local-vs-remote pipe placement); MIT Missing Semester — Command-line Environment (enriched: per-command `VAR=val cmd` prefix, `bash -c` to inspect a var, few-signals note, SSH section now links the dedicated page); index + log updated.

**Session note:** Session — SSH & Pipeline Parallelism Ingest — 2026-08-18.md
**Mastery Summary:** SWE 50 → 51 developing.
**Learning-review gate:** PASS on pass 2 (verdict JSONs in `Reviews/Quality Gates/SSH_Public-Key_Auth_and_Remote_Commands-Pipes-Signals-Env_Vars-pass{1,2}-2026-08-18.json`; model `minimax-m3`). Pass 1 flagged 2 medium + 1 low source-fidelity issues — removed the editorial 'run stages remotely' advice, removed the `grep | head` early-termination claim (kept the source-backed parallel-streaming fact), dropped SIGPIPE + the `~30 signals` count, and reframed password auth as an alternative (not a fallback). Pass 2 returned PASS; two low notes (pedagogical lock-and-key metaphor, missing SIGQUIT) were also addressed — added a scope note and added SIGQUIT to the signals list. **Factual gate passed (same-session audit):** public/private key semantics, `ssh host 'ls | wc -l'` quote behavior, and pipe parallelism are standard, well-established systems facts.

## 2026-08-18 — Teach: Command-line Environment (B2) — signals & job control

**Source:** https://missing.csail.mit.edu/2026/command-line-environment/ (MIT Missing Semester 2026; teaching flow via `learning-teach` skill)

**Lesson taught:** B2 Command-line Environment. Probe located the edge precisely (2/2 signal questions missed; env vars/return codes/tmux/aliases/dotfiles already solid). Taught signals-as-software-interrupts fresh + verified the rest. End quiz 5/5; Feynman explain-back passed (driving/officer analogy). Fact-check (deepseek-v4-flash): 3/3 PASS.

**Concepts added (2 new, SWE track, `developing`):**
- Signals (Software Interrupts) — async kernel message a process can catch/ignore; SIGINT (Ctrl-C) → SIGTERM (`kill`) → SIGKILL (`kill -9`, uncatchable). `next_review` 2026-08-21 (+3d), Last Q Type definitional
- Job Control (Ctrl-Z, fg/bg, nohup/disown) — SIGTSTP suspend, fg/bg/jobs, &/$!, SIGHUP on terminal close → nohup/disown. `next_review` 2026-08-21 (+3d), Last Q Type discriminative

**Curriculum:** B2 → `done` in CURRICULUM.md.

**Wiki page created:** MIT Missing Semester — Command-line Environment; index + log updated.

**Learning record:** 0001-signals-and-job-control.md (first record). **Lesson:** Lessons/Lesson — Command-line Environment — 2026-08-18.md. **Session note:** Session — Command-line Environment (B2) — 2026-08-18.md.

**Mastery Summary:** SWE 48 → 50 developing.

## 2026-08-18 — Ingest: C Integer Mechanics & C Memory Regions (Gemini C tutoring)

**Source:** https://gemini.google.com/app/ed55c6cdf10c8c2a (Gemini conversation notebook, 20 messages)

**Concepts added (2 new, SWE track, `developing`, staggered):**
- C Integer Mechanics (Underflow & Type Promotion) — unsigned can't be negative → wrapping underflow on `total - available` when `available > total` (~quadrillions kB); guard catches corrupt state before math (`invalid memory totals` to stderr, return 1); `100.0 * used_kb / total_kb` (float literal promotes) vs `(used_kb/total_kb)*100` (integer division truncates → 0.0% for any usage <100%). `next_review` 2026-08-21 (+3d), Last Q Type definitional
- C Memory Regions (Stack vs Heap vs Swap) — stack (auto scratchpad, frames wiped on return, caller's stack outlives callee, fixed ~few MB) vs heap (`malloc`/`realloc`, persists until `free`, leaks) vs swap (disk overflow, slow); `char *buf = malloc(4096)` → `buf` on stack, block on heap; returning a stack array's address → dangling pointer (UB; stack can't leak — only heap); buffer-passing trade-off (zero malloc overhead + leak-proof vs fixed capacity truncates /proc/meminfo). `next_review` 2026-08-22 (+4d, staggered), Last Q Type definitional

**Concepts enriched (3, SWE track):**
- Static Fixtures & Boundary Cases — exact-live asserts are flaky (`/proc/meminfo` volatile, MemTotal can hot-plug in VM); swap invariants (`swap_free_kb <= swap_total_kb`; disabled-swap guard `swap_total_kb > 0` vs divide-by-zero; `unsigned >= 0` is redundant). `last_reviewed` 2026-08-18
- Feature Probing vs Kernel Version Checking — MemFree (strictly unused) vs MemAvailable (kernel estimate incl. reclaimable cache/buffers) vs SwapFree (disk, not RAM); answer to "which field for available-to-start-app" is MemAvailable. `last_reviewed` 2026-08-18
- C Pointers (&, *, ->) — pointer validity depends on memory region lifetime; dangling pointer from returning stack array (compiler warning); stack can't leak, heap can (memory leak). `last_reviewed` 2026-08-18

**Wiki pages:** C Integer Mechanics (Underflow & Type Promotion) (created), C Memory Regions (Stack vs Heap vs Swap) (created), Static Fixtures & Boundary Cases (enriched), Feature Probing vs Kernel Version Checking (enriched), C Pointers (&, *, ->) (enriched); raw source note added (2026-08-18 - gemini-c-memory-integer-mechanics)

**Session note:** Session — C Memory & Integer Mechanics Ingest — 2026-08-18.md
**Mastery Summary:** SWE 46 → 48 developing.
**Learning-review gate:** PASS on pass 1 (verdict JSON: `Reviews/Quality Gates/C_Integer_Mechanics_Underflow_and_Type_Promotion-C_Memory_Regions_Stack_vs_Heap_vs_Swap-pass1-2026-08-18.json`; model `minimax-m3`; verdict PASS, 0 issues). Along the way a blocking bug in `Skills/learning-review/openwebui/review_gate.py` was found + fixed (unescaped JSON braces in the embedded REVIEW_TEMPLATE caused `KeyError: '\n  "verdict"'` — braces escaped, wording untouched; the deployed Open WebUI copy picked up the fix). Both new concepts passed the review gate on the first cycle, so no pass-2 was needed. **Factual gate (new concepts) passed** — all load-bearing claims (unsigned wrap-around, integer-division truncation toward zero, `100.0` double promotion, MemFree/MemAvailable/SwapFree kernel semantics, swap-disabled `SwapTotal: 0`, stack/heap/swap behavior, dangling-pointer-from-stack) are standard, well-established C/systems facts.

## 2026-08-16 — Add teaching capability (probe → plan → teach) + Stage-0 curriculum

**What changed (system upgrade, not an ingest):**
- **New `Skills/learning-teach/SKILL.md`** — the teaching loop: probe (3–8 graded MCQs, reads only relevant state) → plan (Mermaid graph + live background fact-check) → teach (one reasoning step at a time, unconditional truths + motivated discovery, guided Socratic, Bloom climb, hook-in/wonder-out, fuzziness inference, Feynman explain-back gate). Two-tier end quiz (retrieval + higher-order). Automatic interleaving at 3 levels. Mimo review gate is ingest-only; teaching uses live fact-checking.
- **New state files:** `Learning System/MISSION.md` (Stage 0 — SWE Foundations), `CURRICULUM.md` (integrated MIT + Terminal System Monitor map, color-tagged, deterministic strand rotation), `RESOURCES.md` (primary readings), `GLOSSARY.md` (workspace glossary).
- **New folders:** `Lessons/`, `Learning Records/`, `Curriculum/sources/terminal-system-monitor/` (8 immutable HTML lesson files).
- **Wiki page created:** [[SWE Primary Colors & Roadmap]] (filed from user attachment; Stage-0 spine; C chosen over Python for CLI strand).
- **Concept Notes frozen as legacy** (reference store = Knowledge Wiki); `Learning Profile.md` re-pointed to SWOT Stage 0 (AI Engineering paused); `Active Concepts.md` gained Stage-0 covered-markers A1–A4 (retrieval-verify, never re-teach); AGENTS.md consistency check extended for teaching sessions.

## 2026-08-15 — Ingest: meminfo Smoke Test (Gemini Socratic tutoring)

**Source:** https://gemini.google.com/app/e338aa05afbec7a2 (Gemini conversation notebook, 12 messages)

**Concepts enriched (2, SWE track):**
- Sentinel Values vs Presence Flags — `{0}` default silently passing `available <= total` on missing MemAvailable; `ULONG_MAX` sentinel pattern; three-fact smoke assertion; sentinel valid only outside the legitimate domain. `last_reviewed` 2026-08-15, `next_review` 2026-08-22 (3d→7d)
- Static Fixtures & Boundary Cases — fixture tests (deterministic exact asserts) vs smoke tests (live range/sanity bounds); `total_kb > 0` divide-by-zero guard; `<=` is the true invariant (`<` brittle since `==` reachable). `last_reviewed` 2026-08-15, `next_review` 2026-08-29 (7d→14d)

**Concepts added (1 new, SWE track, developing):**
- Feature Probing vs Kernel Version Checking — runtime feature presence vs version checks (backports, spoofable uname); sentinel-as-feature-probe; `MemAvailable` added in Linux 3.14; pre-3.14 fallback ≈ MemFree + Buffers + Cached. `next_review` 2026-08-18 (+3d), Last Q Type definitional

**Wiki pages:** Sentinel Values vs Presence Flags (enriched), Static Fixtures & Boundary Cases (enriched), Feature Probing vs Kernel Version Checking (created), raw source note added (2026-08-15 - gemini-meminfo-smoke-test)

**Session note:** Session — meminfo Smoke Test Ingest — 2026-08-15.md
**Mastery Summary:** SWE 46 developing.
**Learning-review gate (Mimo v2.5 via terminal CLI):** pass 1 — 3 medium issues (x != false wording; missing scope notes on Teach C Lesson 3 section and Static Fixtures' earlier sections) → fixed. Pass 2 — 3 medium flags on pre-existing Sentinel-page sections (Overview, The Fix, Key Insight, from the 2026-08-07 ingest) → hard stop at 2 cycles; surfaced to user. Post-ingest (user-approved): implementer fixed all three — Overview reworded (dropped "payload value" jargon), The Fix scope note corrected (2026-08-15 source does name presence flags as pattern #2), Key Insight bullet rewritten as precise clarification. No third LLM pass [2]. Verdicts: Quality Gates/…-pass1-2026-08-15.json, …-pass2-2026-08-15.json. Factual gate (new concept): MemAvailable Linux 3.14 + fallback formula consistent with kernel history / classic free.

## 2026-08-06 — Ingest: Software Testing (Teach C Lesson 2 + Gemini tutoring + cstack Part 4 + Bill Wake 3A)

**Sources:**
- Teach C Course — Lesson 2: Your First Tests (html lesson)
- Gemini Socratic tutoring on testing (https://gemini.google.com/app/e21b1624e3b156a0)
- Gemini testing-patterns conversation (https://gemini.google.com/app/f3ceade4034d6bf0)
- Bill Wake — Arrange, Act, Assert: https://xp123.com/3a-arrange-act-assert/
- cstack — Let's Build a Simple Database, Part 4

**Concepts added (6, SWE track, all `developing`, staggered reviews 08-09 → 08-11):**
- Testable Seam — split side-effecting reads from pure parsing; feed parser static fixture text
- Arrange-Act-Assert (AAA) — three-phase test structure; Assert-First/Frame-First; not dogmatic one-assert-per-test
- Static Fixtures & Boundary Cases — controlled sample data + adversarial fixtures (max-size, malformed, empty, cross-OS)
- Red-Green-Refactor — seeing a test fail first proves it runs your code and can catch failure (no false positives)
- Black-box vs White-box Testing — visibility (technique) vs scope (unit/integration/E2E) are different axes; CLI process I/O testing via IO.popen
- C String Buffer Boundaries — +1 null-terminator bug (`char username[COLUMN_USERNAME_SIZE + 1]`), sscanf→strtok+strlen

**Wiki pages created (6):** Testable Seam, Arrange-Act-Assert (AAA), Static Fixtures & Boundary Cases, Red-Green-Refactor, Black-box vs White-box Testing, C String Buffer Boundaries

**Session note:** Session — Software Testing Ingest — 2026-08-06.md
**Mastery Summary:** SWE 40 developing.

## 2026-08-03 — Ingest: GCC Compilation Stages from handwritten notes

**Source:** User's handwritten GNU Make & GCC notes

**Concept added to Active Concepts (SWE track):**
- GCC Compilation Stages (Preprocessing → Compilation → Assembly → Linking)

**Wiki page created:** GCC Compilation Stages

## 2026-07-29 — Ingest: MIT Missing Semester — Shell Tools (eza through fd range)

**Source:** https://missing.csail.mit.edu/2026/course-shell/

**Concepts added to Active Concepts (SWE track):**
- Basic File Tools (cat, sort, uniq, head, tail)
- bat
- grep
- ripgrep
- sed (Stream Editor)
- find
- fd

**Wiki page updated:** MIT Missing Semester — Shell (added Shell Tools section with subsections on basic file tools, grep/ripgrep, sed, and find/fd)

### 2026-07-28 — Ingest: MIT Missing Semester — Shell
- Created wiki page: MIT Missing Semester — Shell (SWE track)
- Concepts: What is the Shell, Navigation & Paths, man & Documentation, PATH & Program Discovery, ls & File Listing
- Archived all AIE concepts to Concept Archive

# Log

## [2026-07-24] ingest | AI Engineer Weekly synthesis — 8 talks: evals survey, agent architecture decoupling, multi-agent consolidation, DSPy signatures, long-horizon Claude, HTML agent outputs, harness evolution, Codex workshop

## [2026-04-18] bootstrap | Knowledge wiki initialized

## [2026-04-21] ingest | Euler number and exponential derivatives from screenshots

## [2026-04-22] ingest | Local lineatity and Jacobian matrix from screenshots

## [2026-04-23] ingest | Jacobian derivatives, partial derivatives, and determinant from screenshots

## [2026-05-01] ingest | Implicit differentiation and total differentials from screenshots

## [2026-05-02] ingest | Backpropagation forward and backward passes from user notes

## [2026-05-04] ingest | Automatic differentiation forward and reverse passes from user notes

## [2026-05-05] ingest | Automatic differentiation forward mode, JVPs, and differentiation method comparison from screenshots and notes

## [2026-05-06] ingest | Hessian matrix, curvature, Newton's method, and curvature approximations from user notes

## [2026-05-07] ingest | Multivariate Taylor series, tensor contractions, and curvature intuition from guided user notes and recap answers

## [2026-05-08] ingest | Gradient descent as the steepest decrease of the first-order Taylor model from user note

## [2026-05-16] ingest | Probability foundations beginner-friendly overview from mind map and refinement notes

## [2026-05-18] ingest | Cox-Jaynes plausibility, rational consistency, and probability theory from user note

## [2026-05-18] ingest | Random variable from user note

## [2026-05-19] ingest | Random variable pre-image, distribution, and ML motivation from Perplexity walkthrough on MML section 6

## [2026-05-21] ingest | Discrete vs continuous distributions, joint/marginal/conditional probabilities, independence, and CDF from Perplexity walkthrough on MML section 6

## [2026-05-22] ingest | Independence test derivation, theoretical vs statistical independence, chi-square test, and p-value interpretation from user notes

## [2026-05-29] ingest | Compilers, interpreters, virtual machines, bytecode, JIT, transpiler, compiled vs interpreted, and runtime from 7 handwritten note pages

## [2026-05-30] ingest | Interpreter EVAL loop, translator overhead, compiler optimizations, JIT downsides, and dev vs production workflow from Perplexity conversation

## [2026-05-30] ingest | Python performance tradeoffs — dynamic execution model, distribution/bundling, JIT limits in dynamic languages, and memory management models (GC vs ownership vs manual) from Perplexity conversation

## [2026-06-04] ingest | Short-circuit evaluation and memory management models from Perplexity conversation

## [2026-06-04] ingest | Expressions vs statements, imperative vs declarative, arguments vs parameters, and closures from user notes

## [2026-06-06] ingest | Waterbed Theory and runtime components (engine vs environment distinction) from user notes

## [2026-06-06] ingest | Broken Window Theory, DRY Principle, ETC (Easier To Change), Professional Responsibility, Good Enough Software, Knowledge Portfolio, Tracer Bullets, Communication for Developers, Representational Duplication, Uniform Access Principle, Interdeveloper Duplication, Maintenance Mindset — from user notes on The Pragmatic Programmer (Hunt & Thomas)

## [2026-06-09] ingest | Lexer lexical analyzer, Token structure (lexeme, literal, metadata) from user-provided notes

## [2026-06-10] ingest | Orthogonality, Decorator Pattern, Shy Code (Law of Demeter), Global Data Avoidance, Self-Contained Components, Strategy Pattern — from user-provided software design notes

## [2026-06-10] ingest | Single Responsibility Principle (SRP), Delegation Pattern, and Convenience Method from user-provided software design notes

## [2026-06-11] ingest | Java Class Body Rules, Java Static Initializer Block, and Modern Java Collection Factory Methods from Perplexity conversation

## [2026-06-13] ingest | Context-Free Grammar (CFG), Parser, and Formal Grammar — distinction between lexical and syntactic grammars, Chomsky hierarchy, and nested structure handling from user-provided compiler design notes

## 2026-06-23 — AI Engineering Phase 0 Ingest

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch (Phase 0, Stages 1-8)

**Concepts added:**

- AI Engineering - Dev Environment Stack
- Git for AI Workflows
- GPU Computing
- API Key Security
- Jupyter Notebook Workflow
- Python Virtual Environments
- Docker for AI Development
- Editor and Remote Dev Setup

## 2026-06-25 — Terminal & Shell (AI Engineering Phase 0, Lesson 10)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/10-terminal-and-shell/docs/en.md

**Concepts added:**

- AI Engineering - Terminal and Shell (wiki page)
- Shell Basics
- Piping & Redirection
- Background Processes & Process Management
- tmux (Terminal Multiplexer)
- System & GPU Monitoring
- SSH & Remote File Transfer
- AI Shell Aliases & Terminal Patterns

## 2026-06-25 — Linux for AI (AI Engineering Phase 0, Lesson 11)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/11-linux-for-ai/docs/en.md

**Concepts added:**

- AI Engineering - Linux for AI (wiki page)
- Linux File System Layout
- Linux File Permissions
- apt Package Management
- systemd Services
- Disk Space Management on GPU Boxes
- Networking Tools (wget, curl)
- WSL2 for AI Development
- macOS to Linux Gotchas

## 2026-06-26 — Debugging and Profiling (AI Engineering Phase 0, Lesson 12)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/12-debugging-and-profiling/docs/en.md

**Concepts added:**

- AI Engineering - Debugging and Profiling (wiki page)
- AI Debugging Levels
- Print Debugging & breakpoint for AI
- Python Logging for Training
- Code Timing & Profiling
- Memory Profiling (CPU & GPU)
- Debugging Common AI Bugs
- TensorBoard & Training Visualization

## 2026-06-27 — Linear Algebra Intuition (AI Engineering Phase 01, Math Foundations)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/01-linear-algebra-intuition/docs/en.md

**Concepts added:**

- Linear Algebra Intuition (wiki page)
- Vectors (Points & Directions)
- Matrices (Transformations)
- Dot Product (Similarity)
- Linear Independence
- Basis and Rank
- Projection
- Gram-Schmidt Process
- QR Decomposition

## 2026-06-27 — ingest | Software Engineering Philosophy from user notes

A personal synthesis of professionalism, engineering mindset, delivering value, continuous learning, problem solving, communication, design philosophy (ETC), DRY, information hiding, managing external representations, and team knowledge — organized into a four-layer mental model (Character → Thinking → Engineering → Execution). Also includes a code review appendix applying Information Hiding, Accessor Functions, and Uniform Access Principle.

## 2026-06-30 — Vectors, Matrices & Operations (AI Engineering Phase 01, Math Foundations — Lesson 02)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/02-vectors-matrices-operations/docs/en.md

**Concepts added:**

- Matrix Operations from Scratch (wiki page)
- Matrix Operations (Implementation)
- Broadcasting
- Dense Layer Forward Pass

## 2026-07-01 — Matrix Transformations (AI Engineering Phase 01, Math Foundations — Lesson 03)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/03-matrix-transformations/docs/en.md

**Concepts added:**

- Matrix Transformations (wiki page)
- Rotation Matrices
- Scaling Matrices
- Shearing Matrices
- Reflection Matrices
- Composition of Transformations
- Eigenvalues & Eigenvectors
- Eigendecomposition
- Determinant as Volume Scaling

## 2026-07-04 — Calculus for ML (AI Engineering Phase 01, Math Foundations — Lesson 04)

**Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/04-calculus-for-ml/docs/en.md

**Concepts added:**
- Calculus for ML (wiki page)
- Derivative for ML
- Partial Derivatives & Gradient
- Numerical vs Analytical Derivatives
- Chain Rule & Backpropagation
- Gradient Descent from Scratch
- Hessian Matrix & Curvature
- Taylor Series for ML
## 2026-07-08 — Chain Rule & Autodiff (Teach Lessons 1–2)

**Source:** teach/lessons/0001-chain-rule-and-computational-graphs.html, teach/lessons/0002-forward-vs-reverse-autodiff.html

**Concepts added:**
- Computational Graphs (Autodiff)
- Two-Pass Autodiff Algorithm
- Chain Rule Decomposition
- Forward-Mode Autodiff
- Reverse-Mode Autodiff & Backprop

## 2026-07-09 — Chain Rule & Autodiff (Teach Lessons 3–4)

**Source:** teach/lessons/0003-value-class-and-operations.html, teach/lessons/0004-backward-pass-and-topological-sort.html

**Concepts added:**
- Value Class Architecture
- Local Autograd Derivative Rules
- Gradient Accumulation (+=)
- Topological Sort for Backprop
## [2026-07-10] ingest | Chain Rule & Autodiff — Lesson 5

**Source:** `teach/lessons/0005-gradient-checking-and-micrograd.html`

**Concepts added:**
- Gradient Checking
- Neural Network Training Loop
- Micrograd Architecture
## [2026-07-13] ingest | AI Engineer Weekly synthesis — 8 talks covered: production guardrails & hallucination prevention, context management for large codebases, agent architecture patterns (multi-agent validation, jury/judge), ReviewDebt framework, RLM recursive language models, AI code review practices, psychometric evaluation for LLMs, and AI trust design patterns
## [2026-07-14] ingest | Marconi Lab DL — Day 1: Tensors, Neural Networks & Training Loop
- Added wiki pages: [[Tensors (PyTorch)]], [[PyTorch Model Building]], [[Activation Functions]], [[Loss Functions (PyTorch)]], [[Training Loop Pattern]], [[Evaluation Protocol]]
- Source: Marconi Lab Deep Learning Course, Day 1 (HTML lesson)

## [2026-07-15] ingest | Marconi Lab DL — Day 2: CNNs for Medical & Agricultural Images
- Added wiki pages: [[Convolution Operation]], [[Convolution Parameters]], [[Pooling (MaxPool2d)]], [[CNN Architecture Pattern]], [[Data Augmentation (torchvision)]], [[Transfer Learning (PyTorch)]]
- Source: Marconi Lab Deep Learning Course, Day 2 (HTML lesson)

## [2026-07-15] ingest | Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- Added wiki pages: [[Vanishing & Exploding Gradients]], [[Optimizers (SGD, Adam, AdamW)]], [[Regularization Techniques]], [[Recurrent Neural Networks (RNNs)]], [[LSTM (Long Short-Term Memory)]], [[Multi-Input & Multi-Modal Models]]
- Source: Marconi Lab Deep Learning Course, Day 3 (HTML lesson)

## [2026-07-16] ingest | Probability & Distributions — Lesson 1

**Source:** `teach/lessons/0002-probability-foundations.html` (AI Engineering from Scratch, Phase 1, Lesson 06)

**Concepts added:**
- Probability Mass Function (PMF)
- Bernoulli Distribution
- Categorical Distribution

## [2026-07-16] ingest | Probability & Distributions — Phase 1, Lesson 06 (Full)
- Changed status of Beta, Dirichlet, Categorical, Multinomial from consolidated to developing
- Next reviews: 2026-07-19 (6 concepts, +3d), refresher review session

## [2026-07-17] ingest | Marconi Lab DL — Day 4: Deep Learning for Text & African Language NLP
- Added wiki pages: [[Text Tokenization]], [[Word Embeddings (nn.Embedding)]], [[BiLSTM Text Classifier]], [[Character-Level RNN (CharRNN)]], [[Transfer Learning for Text]], [[African Language NLP]]
- Source: Marconi Lab Deep Learning Course, Day 4 (HTML lesson)

## [2026-07-20] ingest | AI Engineer Weekly synthesis — 8 talks covered: agent scaffolding, eval design, production observability, memory over fine-tuning, agent infrastructure patterns
## [2026-07-22] ingest | Makemore Part 1 — Bigram Language Model (Karpathy Lecture 2)
- **Source:** `02-makemore-bigram.html` (Part 1: from "What is Language Modeling?" through "The Problem: Sparse Counts & Model Smoothing") + Socratic tutoring session on broadcasting trap and log(0) explosion
- **Concepts added:** Bigram Language Model, Counts → Probabilities (Row Normalization), Add-1 Smoothing, Negative Log-Likelihood (NLL), Sampling from a Language Model
- **Archive action:** Paused ~87 concepts from old AI Engineering from Scratch roadmap — kept only micrograd content active
- **Note:** Shifted to Karpathy's Neural Networks: Zero to Hero lecture series as the new AI engineering learning path

## [2026-07-22] ingest | AI Engineering Roadmap v2
## [2026-07-22] ingest | Makemore Part 2 — Neural Bigram + Socratic session on regularization & hidden layers

## [2026-07-22] ingest | [supplement] Discrete vs. Continuous Representations
- Added the discrete-vs-continuous insight to [[Distributed Representations (Character Embeddings)]]
- Key point: continuous embeddings enable gradient flow; one-hot discrete buckets have no in-between values
- Updated Active Concepts entry for Distributed Representations
- **Source:** `02-makemore-bigram.html` (Part 2: from "Building the Training Set" through end) + Gemini tutoring session on regularization tug-of-war, character embeddings, and hidden layer generalization
- **Concepts added:** One-Hot Encoding, Softmax Function, Row-Select Property, L2 Regularization as Smoothing, Regularization Tug-of-War, Distributed Representations (Character Embeddings), Hidden Layers Generalize via Shared Weights
- **Source:** Primary Colors Roadmap — 5-core-strand design for practical AI engineering
- **Stored at:** `wiki/AI Engineering Roadmap v2.md`
- **Learning Profile updated:** Current Focus, Roadmap Context, sequencing, and position refs added

- 2026-07-25 — AI Engineer Weekly — 10 talks from 100-video pool, agent-tinkering lens (handoffs, prompt caching, Claude Code patterns, agent logs)

## [2026-07-30] ingest | MIT Missing Semester — Shell (remaining concepts)
- **Source:** https://missing.csail.mit.edu/2026/course-shell/
- **Concepts added (15):** awk, Pipes & Pipeline Composition, Shell Redirections & Streams, Shell Conditionals, Shell Loops, Command Substitution & Arithmetic, Shebang & Script Execution, Background Jobs, Globs/Pattern Matching, Quoting in Shell, Exit Status & Short-circuit, Script Arguments & Special Params, xargs, curl, jq
- **Action:** Added 15 concepts to SWE track Active Concepts (status: developing, staggered reviews starting 2026-08-02). Updated wiki page with all sections. Mastery Summary: 27 developing.

## [2026-07-30] correction | MIT Missing Semester — Shell (removed exercises-only concepts)
- **Correction:** Removed 7 exercise-only concepts from Active Concepts (Globs/Pattern Matching, Quoting in Shell, Exit Status & Short-circuit, Script Arguments & Special Params, xargs, curl, jq). These will be ingested when the exercises part is tackled.
- **Updated:** Mastery Summary → 20 developing. Removed exercise sections from wiki page.
- **Added rich detail:** Background Jobs (&, $!, kill), Shell Redirections (2>&1 order-of-evaluation), Arithmetic Expansion ((()) vs $(())).
- **Source:** User-provided breakdown of three key shell concepts + https://missing.csail.mit.edu/2026/course-shell/

## [2026-08-02] ingest | MIT Missing Semester — Shell (permissions, wildcards, quoting) + Makefiles
- **Ingested:** 6 new concepts from Socratic tutoring PDFs (shell extras: file permissions, wildcards, quoting; Makefiles: targets/prereqs/recipes, timestamps, dependency trees, object files, variables, .PHONY)
- **Updated:** Active Concepts table (26 developing now). Wiki page updated with permissions, wildcards, quoting sections.
- **Session note:** Session — Shell Extras & Makefile Ingest — 2026-08-02.md

## 2026-08-03
- SWE review session: 5 concepts (Shell track from MIT Missing Semester) — Wildcards & Globs, Shell Redirections & Streams, File Permissions (ls -l), find, Bash Quoting
- All Last Q Type updated to discriminative, next_review → 2026-08-10

## 2026-08-04 — Ingest: Gemini Shell Tutoring (safety flags, built-ins, parameter expansion)
- **Source:** https://gemini.google.com/app/effe61964e68778c and https://gemini.google.com/app/921fdcb9207f4b05 (two Gemini conversation notebooks)
- **Concepts added (2 new):** Parameter Expansion `${var%pattern}`, Shell Built-ins & Process Isolation (child process memory isolation, why `cd` must be built-in, internal shell state)
- **Concepts enriched (6):** Shebang & Script Execution (set -euo pipefail deep dive, `|| true` pattern, set -x security risk), Shell Conditionals (quoting in test conditions), Shell Loops (glob + parameter expansion backup loop), Shell Redirections & Streams (`cp` vs `>` distinction), File Permissions (`chmod +x` detail), Shell Navigation & Paths (cross-ref to built-ins concept)
- **Wiki page updated:** Added Parameter Expansion and Shell Built-ins sections to MIT Missing Semester — Shell; enriched Shell Redirections with cp vs >
- **Session note:** Session — Gemini Shell Ingest (safety flags, built-ins, parameter expansion) — 2026-08-04.md

## 2026-08-05 — Ingest: Gemini Shell Tutoring (xargs, curl, jq)
- **Source:** https://gemini.google.com/app/3b1807d0dd75591c (Gemini conversation notebook — Missing Semester Exercises 13–16)
- **Concepts added (3 new):** xargs (stdin→args bridge, whitespace split trap, `-print0`/`-0` NUL delimiters), curl (websites as streams, `-s`, scraping with grep), jq (JSON processing, `.[] | select(...) | .name`, `-r`, quotes placement)
- **Concepts enriched (4):** find (`-name "*.*"`, `-print0`), grep (`-c` count, line-by-line limitation, regex `*` vs glob), awk (`-F.` extension extraction, no-dot files → NF=1 → whole filename), Pipes (`sort | uniq -c | sort -nr | head -n 5` top-counts pattern)
- **Wiki page updated:** Added xargs, curl, jq sections to MIT Missing Semester — Shell; enriched find, grep, awk, Pipes sections
- **Session note:** Session — Gemini Shell Ingest (xargs, curl, jq) — 2026-08-05.md

## 2026-08-06 — Ingest: Software Testing (testable seams, AAA, fixtures, red-green-refactor, black-box vs white-box, C string boundaries)
- **Sources:** Teach C Lesson 2 (Your First Tests), Gemini tutoring notebooks https://gemini.google.com/app/e21b1624e3b156a0 and https://gemini.google.com/app/f3ceade4034d6bf0, Bill Wake 3A https://xp123.com/3a-arrange-act-assert/, cstack Part 4 https://cstack.github.io/db_tutorial/parts/part4.html
- **Concepts added (6 new, SWE track):** Testable Seam, Arrange-Act-Assert (AAA), Static Fixtures & Boundary Cases, Red-Green-Refactor, Black-box vs White-box Testing, C String Buffer Boundaries — all developing, staggered reviews 08-09 → 08-11
- **Wiki pages created (6):** Testable Seam, Arrange-Act-Assert (AAA), Static Fixtures & Boundary Cases, Red-Green-Refactor, Black-box vs White-box Testing, C String Buffer Boundaries
- **Mastery Summary:** SWE track 34 → 40 developing
- **Session note:** Session — Software Testing Ingest — 2026-08-06.md
- **Verification:** factual gate passed (cstack Part 4 + Bill Wake 2001 claim checked against sources); quality gate run via learning-review skill

## 2026-08-06 — Ingest: Software Testing (Teach C Lesson 2 + Gemini tutoring + cstack Part 4 + Bill Wake 3A)
- **Sources:** Teach C Lesson 2 (Your First Tests), Gemini Socratic tutoring notebooks (https://gemini.google.com/app/e21b1624e3b156a0, https://gemini.google.com/app/f3ceade4034d6bf0), cstack Let's Build a Simple Database Part 4 (https://cstack.github.io/db_tutorial/parts/part4.html), Bill Wake — 3A Arrange Act Assert (https://xp123.com/3a-arrange-act-assert/)
- **Concepts added (6 new, SWE track, staggered 08-09 → 08-11):** Testable Seam, Arrange-Act-Assert (AAA), Static Fixtures & Boundary Cases, Red-Green-Refactor, Black-box vs White-box Testing, C String Buffer Boundaries
- **Wiki pages created (6):** Testable Seam, Arrange-Act-Assert (AAA), Static Fixtures & Boundary Cases, Red-Green-Refactor, Black-box vs White-box Testing, C String Buffer Boundaries
- **Session note:** Session — Software Testing Ingest — 2026-08-06.md
- **Learning-review gate:** factual gate PASS (cstack +1 null terminator / sscanf→strtok / 1,401-row capacity / IO.popen verified against primary source; AAA "named 2001" verified); quality gate PASS after 2 fix cycles (added Kent Beck TDD-by-Example mention, reciprocal AAA link, Wake's Act-first write-order)
## 2026-08-07 — Ingest: C Parsing Patterns & Makefile Self-Update (Gemini tutoring)
- **Sources:** Gemini Socratic tutoring on parsing /proc/meminfo + Makefile dependencies (https://gemini.google.com/app/8870dcd71e2919f5)
- **Concepts added (2 new, SWE track, staggered 08-10 → 08-11):** Sentinel Values vs Presence Flags, sscanf %n & Line Advancement
- **Enriched:** Make: Timestamp Evaluation — Makefile-as-own-prerequisite; make compares timestamps only (never content), so even a comment-only save triggers rebuild
- **Wiki pages created (2):** Sentinel Values vs Presence Flags, sscanf %n & Line Advancement; MIT Missing Semester — Shell page extended with Makefile self-update section
- **Session note:** Session — C Parsing & Makefile Ingest — 2026-08-07.md
- **Learning-review gate:** factual gate PASS (`%n` semantics vs cppreference; make timestamp-only comparison vs GNU make manual); quality gate PASS after 2 cycles (cycle 1: Robust→Working Pattern + caveat, false-positive→accidental-true-negative, `%n` wording; cycle 2: corrected sscanf failure mechanism — `%[^:]` swallows newlines → garbage key, not parse failure; caveat moved out of code block)
## 2026-08-08 — Ingest: Teach C Lesson 3 + Gemini tutoring (pointers, macros, Acutest)
- **Sources:** Teach C Course — Lesson 3: Acutest and the Parser Seam (html lesson); Gemini Socratic tutoring (notebook: https://gemini.google.com/app/8870dcd71e2919f5); Acutest README (https://github.com/mity/acutest)
- **Concepts added (3 new, SWE track, all `developing`, staggered 08-11 → 08-12):** C Pointers (&, *, ->) — next_review 2026-08-11; C Preprocessor Macros — next_review 2026-08-12; Acutest Unit Testing — next_review 2026-08-12
- **Enriched (4):** Testable Seam (concrete read/parse seam split, vendored single-header framework keeps tests reproducible); Red-Green-Refactor (compile-time Red as interface spec, missing-field practice loop); Sentinel Values vs Presence Flags (Lesson 3 practice fix = the naive two-field check); Make Variables (CPPFLAGS `-I` include paths, test-target pattern) on MIT Missing Semester — Shell page
- **Wiki pages created (3):** C Pointers (&, *, ->), C Preprocessor Macros, Acutest Unit Testing
- **Session note:** Session — Acutest & C Pointers Ingest — 2026-08-08.md
- **Learning-review gate:** C Pointers PASS (c1); enrichments PASS (c1); C Preprocessor Macros PASS (c2); Acutest Unit Testing PASS (c2) — factual gate PASS (variadic macros vs GCC docs, Acutest claims vs README). Full detail in session note.

## 2026-08-11 — Enrichment: awk (lecture-1 quiz notes photo)
- **Sources:** Handwritten lecture-1 quiz notes (photo 2026-08-10, transcribed via Mimo v2.5 vision delegation); MIT Missing Semester — Shell (https://missing.csail.mit.edu/2026/course-shell/)
- **Enriched (1, SWE track):** awk — FS/OFS (input/output field separators), FPAT for quoted-CSV fields, `~`/`!~` match operators, pattern/action structure (bare pattern = implicit `$0` filter), `$0`/`$1`/`NF` built-ins, `BEGIN {}` blocks, `/etc/passwd` example; added source-scope note distinguishing lecture-taught vs beyond-source expansion
- **Wiki page updated:** MIT Missing Semester — Shell
- **Active Concepts:** awk row enriched; `last_reviewed` 2026-08-11, `next_review` 2026-08-18 (interval 3d→7d)
- **Session note:** Session — awk Enrichment — 2026-08-11.md
- **Learning-review gate:** quality gate (enrichment) — awk flag resolved pass 2 via source-scope note; remaining flags are pre-existing sections outside this session (GNU Make HIGH; permissions/globs/quoting/built-ins/jobs/parameter-expansion medium) surfaced to user

## 2026-08-23 — Ingest: Shell Scripting & Script Arguments (Lecture 2 notes)
- **Sources:** Furnished Lecture 2 notes (website, 2026-08-21); MIT Missing Semester — Shell Tools and Scripting (https://missing.csail.mit.edu/2020/shell-tools/ — the 2026 /shell-tools/ URL 404s, used stable 2020 mirror).
- **New concepts (2, SWE track, both `developing`, staggered 2026-08-23 → 2026-08-26):** Shell Positional & Special Parameters, Process Substitution (<(CMD))
- **New concept page (1):** Shell Arguments & the Untyped-Variable Model (consolidates "args are plain strings" + "shell vars have no types"; overlaps the terminology-focused Arguments and parameters page but is shell-syntax-specific)
- **Enriched (3):** SSH — Public-Key Auth & Remote Commands (added step-by-step key-based auth handshake: challenge/response + signature verification; private key never on wire); MIT Missing Semester — Command-line Environment (Return Codes: added `exit N` built-in + `mkdir ... || exit 1` guard); index.md (3 new concept links)
- **Wiki pages created (3):** Positional & Special Shell Parameters, Process Substitution, Shell Arguments & the Untyped-Variable Model
- **Session note:** Session — Shell Scripting & Args Ingest — 2026-08-23.md
- **Source contradiction flagged:** Lecture-2 notes' second "Process Substitution" paragraph wrongly states `<(CMD)` captures output *into a variable* — that is command substitution (`$(CMD)`). Captured the correct model in the wiki and noted the error.
- **Learning-review gate:** quality gate (new concepts + enrichments) — see Quality Gates/Shell_Scripting_Args-*.json (run after this write).

## 2026-08-23 (follow-up) — review_gate deferred + factual self-audit fixes
- **Blocker:** `review_gate` (minimax-m3) could not be invoked from the Open Terminal sandbox — it is a native Open WebUI tool calling `localhost:8080`, unreachable from this separate container. No Quality Gates JSON produced.
- **Factual self-audit (live MIT sources):** confirmed `$0/$1–$9/$@/$#` and process-substitution model vs MIT 2020 Shell Tools; confirmed SSH sign/verify handshake vs MIT 2020 Security (contradicts the lecture notes' encrypt-with-public-key framing).
- **Fixed (HIGH):** SSH handshake corrected from "server encrypts challenge with public key / client decrypts" to sign/verify; updated wiki [[SSH — Public-Key Auth & Remote Commands]] + Active Concepts row 68 (`last_reviewed` 2026-08-23).
- **Fixed (MEDIUM):** `MIT Missing Semester — Command-line Environment` return-code example — removed dead `echo $?` after `exit 1`, added a working `$?` read-back example.
- **Not done:** independent minimax-m3 quality-gate verdict — requires running `review_gate` from inside Open WebUI.

## 2026-08-24 — Ingest: CLI Environment batch 2 (env vars, exit codes, tmux, file transfer — Lecture 2 notes cont.)
- **Sources:** Furnished transcription of handwritten Lecture 2 website notes (Fri 2026-08-21 + Sat 2026-08-22); cross-checked live against https://missing.csail.mit.edu/2020/command-line/ and /2020/security/.
- **New concepts (4, SWE track, developing, next_review staggered 2026-08-27 → 2026-08-30):** Environment Variables (Shell); Exit Codes & Short-Circuit Control Flow; tmux — Sessions, Windows & Panes; File Transfers over SSH — scp, rsync & ssh_config
- **New wiki pages (4):** same titles.
- **Enriched (3 rows, 2 pages):** SSH row + page (~/.ssh/config section; flagged the notes' recurring encrypt-the-challenge framing vs the wiki's sign/verify model); curl row + [[MIT Missing Semester — Shell]] (`curl \| bash` download-inspect-run pattern); Shell Config & Dotfiles row + page (login × interactive startup-mode table; fixed the notes' inverted non-login/profile-flow claim).
- **Duplicates skipped:** positional params, process substitution, untyped vars, SSH handshake — ingested 2026-08-23.
- **Source corrections:** "rsync builds on scp" → improves-on-scp; `-P` = `--partial --progress`; aliases-append-args caveat kept.
- **Tooling note:** `fact_check` returned HTTP 500 all attempts; verified load-bearing claims directly against live MIT pages (sign/verify primitives, rsync --partial/-P, ssh-config readers).
- **Review gate:** BLOCKED (pass 1) — transport OK (review_gate.py driven from terminal against http://host.docker.internal:3000, reachable), but stored API key returned HTTP 401 (expired/invalid token). No independent verdict; see Quality Gates/CLI_Env_Batch2-pass1-2026-08-24.json (GATE_NOT_RUN + compensating checks). Re-run after the user regenerates the key.
- **Session note:** Learning System/Sessions/Session — CLI Environment Batch 2 Ingest — 2026-08-24.md

## 2026-08-24 (review) — SWE spaced-repetition review (5 slots)
- **Mistake retries:** man & Documentation PASS — man→tldr→--help ladder rebuilt (review status; 1 more correct recall graduates) · find FAIL again — quoting model re-inverted (quotes *stop* shell glob expansion, don't enable it); fixed via live demo (`find: paths must precede expression`), new retry 2026-08-27.
- **Overdue reviews:** File Permissions (ls -l) PASS (14d; owner/group/others chunking corrected) · PATH & Program Discovery FAIL (bare name → $PATH walk vs ./ → direct execution; retry 08-27) · Command Substitution & Arithmetic PASS (14d; subshell-splices-output vs bash-internal-arithmetic landed on scaffolded round 2).
- **Writes:** Active Concepts 5 rows synced from Attempts.json; 🧯 Mistakes.md man row → review, find row re-attributed; session note `Learning System/Sessions/Session — SWE Track Review — 2026-08-24.md`.
- **Surfaced:** Feynman explain-back debt on all concept items; scheduler drift (xargs/curl/jq/Parameter Expansion + 08-11 cohort stale next_review) to be folded into future queues.

## 2026-08-24 — Ingest: /dev/null, find -exec batching (+), less
- **Source:** Furnished transcription of handwritten lecture notes (Mon 2026-08-24); spot-checked live against https://missing.csail.mit.edu/2020/shell-tools/ (/dev/null discard idiom confirmed) and https://missing.csail.mit.edu/2026/course-shell/ (none of the three items present there).
- **New concept (1):** less (Pager) — memory type, developing, next_review 2026-08-27. New page `Knowledge Wiki/wiki/less (Pager).md`.
- **Enriched (2 rows, 1 page):** find row + [[MIT Missing Semester — Shell]] §find & fd (`-exec {} +` single-invocation batching vs per-file `\;`); Shell Redirections & Streams row + same page §Shell Redirections (`/dev/null` null device; added `2>/dev/null` to the worked example). Redirections last_reviewed → 2026-08-24 (next 08-25); find last_reviewed already 08-24 (glob-quoting mistake retry 08-27 stands).
- **Review gate:** BLOCKED (pass 1) — terminal transport OK, but stored API key rejected again (HTTP 401, expired/invalid token; same blocker as CLI_Env_Batch2 earlier today). Record: Quality Gates/dev-null_find-exec-batching_less-pass1-2026-08-24.json (GATE_NOT_RUN + compensating checks). Re-run after the user regenerates the key.
- **Session note:** Learning System/Sessions/Session — devnull exec-batching less Ingest — 2026-08-24.md

## 2026-08-25 (review) — SWE spaced-repetition review (5 slots)
- **Queue:** 2 priority-1 mistake retries (find, Bash Quoting) + 3 due reviews (Shell Redirections & Streams, SSH, Process Substitution).
- **Results:** 3 pass / 2 fail. find FAIL 3rd time (glob-quoting execution-movie still inverted; retry 08-28) · Bash Quoting PASS (mistake → review, 1 recall; advanced 30d) · Shell Redirections PASS + first Feynman ✓ (14d) · SSH PASS 4th straight, mastery 1.00 (14d) · Process Substitution FAIL ($() text vs <() path conflation; new mistake row, retry 08-28).
- **Housekeeping:** folded uncommitted partial-session records from earlier today (Bash Quoting + Wildcards passes, Built-ins mistake row) into this persistence pass; surfaced Attempts.json xargs last_reviewed corruption + scheduler-drift cohort for future queues.
- **Writes:** Active Concepts 5 rows synced from Attempts.json; 🧯 Mistakes.md (find rescheduled, Bash Quoting → review, +Process Substitution row); session note `Learning System/Sessions/Session — SWE Track Review — 2026-08-25.md`.

## 2026-08-25 (review cont.) — SWE gap-fill round (3 extra slots)
- **Queue:** sed (oldest outstanding mistake retry), Shebang & Script Execution, Git commit message conventions — all from the scheduler-drift backlog (Make cluster deprioritized with C-project archive).
- **Results:** 2 pass / 1 fail. sed PASS (mistake → review, retries 1; advanced 14d) · Shebang FAIL (kernel-executes vs bash-reads route split missing; new mistake row, retry 08-28) · Git conventions PASS (advanced to 14d slot; imperative-mood + scannability framing added).
- **Writes:** Active Concepts 3 rows synced; 🧯 Mistakes.md (sed → review, +Shebang row); gap-fill section appended to the 2026-08-25 session note.
