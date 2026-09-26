# 4-Layer AI Environment Stack

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P0 L01-L12 · **Lang:** Python
> **Insight:** System → Packages → Runtimes → AI Libraries. GPU issue = Runtimes layer.

## The Four Layers
| Layer | What | Examples |
|-------|------|----------|
| System | OS, drivers | NVIDIA driver, nvidia-smi |
| Packages | Tools | Python, git, apt |
| Runtimes | Runtimes + GPU SDK | venv, CUDA toolkit |
| AI Libs | Frameworks | PyTorch, TensorFlow |

## GPU Diagnosis

nvidia-smi OK + torch.cuda False → Runtimes layer issue.

## Related

- [[GPU Computing]]
- [[Python Virtual Environments]]

## Retrieval log (2026-09-26)

- Review retry PASS (MCQ "C") on a fresh prompt isolating the runtime libs (healthy driver + CUDA-enabled torch build + missing CUDA/cuDNN runtime libraries → Runtimes). Grade-audit agreed. The Packages→Runtimes split now holds under retrieval; the 2026-09-05 mistake row moves to `review` (retries 2, next retry 2026-10-03 — a second consecutive correct graduates it, since the 09-23 partial fail broke the 09-16 streak). `next_review` 2026-10-03 (interval_index 1).
