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
