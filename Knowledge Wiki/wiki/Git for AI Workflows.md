# Git for AI Workflows

> Version control for experiments, models, and engineering collaboration.

## The Daily Workflow

Only four commands needed for this course:

| Command | Purpose |
|---------|---------|
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Save a snapshot |
| `git push` | Back up to remote |
| `git pull` | Get latest changes |

## Branching for Experiments

```bash
git checkout -b experiment/new-optimizer
# make changes, commit
git checkout main
git merge experiment/new-optimizer
```

Branch = a pointer to a commit that moves forward as you work.

## Key Concepts

- **Commit** — A snapshot of the entire project at a point in time, not just changed files.
- **Branch** — A movable pointer to a commit. Use branches for isolated experiments without breaking main.
- **Merge** — Taking changes from one branch and applying them to another.
- **Remote** — A copy of the repo hosted elsewhere (GitHub, GitLab).

## ML Artifact .gitignore

Always exclude model checkpoints and large binary files:

```gitignore
*.pt
*.pth
*.safetensors
*.bin
*.onnx
data/
models/
```

## Related
- [[AI Engineering - Dev Environment Stack]]
