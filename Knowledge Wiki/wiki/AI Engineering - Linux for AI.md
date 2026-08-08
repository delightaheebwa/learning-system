# Linux for AI

> Most AI runs on Linux. You need to know enough to not be stuck.
> Source: [ai-engineering-from-scratch — Phase 0, Lesson 11](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/11-linux-for-ai/docs/en.md)

## File System Layout

Linux organizes everything under a single root `/`. Key directories for AI work:

| Directory | Purpose |
| --- | --- |
| `/home/your-username/` (`~`) | Your files — clone repos, run training |
| `/tmp/` | Temporary files, cleared on reboot |
| `/usr/` | System programs and libraries |
| `/etc/` | Config files |
| `/var/log/` | Logs — check when something breaks |
| `/mnt/` or `/media/` | External drives and volumes |
| `/proc/` and `/sys/` | Virtual files — kernel and hardware info |

## File Permissions

Every file has an owner and permission bits. Read with `ls -l`:

```markdown
-rwxr-xr-- 1 user group 2048 Mar 19 10:00 train.py
 ^^^          owner: read, write, execute
    ^^^       group: read, execute
       ^^     everyone else: read only
```

Common fixes:

- `chmod +x script.sh` — make executable
- `chmod 755 script.sh` — owner: full, others: read+execute
- `chmod 644 config.yaml` — owner: read+write, others: read
- `chown user:group file.txt` — change owner (needs sudo)

## Package Management (apt)

Ubuntu uses `apt` for system-level software:

- `sudo apt update` → refresh package list (always do this first)
- `sudo apt install -y <pkg>` → install
- `apt list --installed` → what's installed?
- `sudo apt remove <pkg>` → uninstall
- `sudo apt clean` → clear apt cache

Common fresh GPU box install:

```markdown
build-essential git curl wget tmux htop unzip python3-venv
```

## sudo & Users

- `whoami` — current user
- `sudo <command>` — run as root
- `sudo su` — become root (use sparingly)

On cloud GPU instances, you're typically the only user with sudo access. Don't run everything as root.

## systemd Services

Systemd manages background daemons (inference servers, etc.):

- `sudo systemctl start/stop/restart/status <service>`
- `sudo systemctl enable <service>` — start on boot

## Disk Space Management

GPU boxes have limited disk. Models and datasets fill it fast:

- `df -h` — disk usage for all mounted drives
- `du -sh *` — size of each item in current directory
- `du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20` — biggest space hogs

Common space savers:

- `pip cache purge` — clear pip cache
- `sudo apt clean` — clear apt cache
- `rm -rf checkpoints/epoch_01/` — remove old checkpoints

## Networking Tools

- `wget <url>` — download a file
- `curl -O <url>` — same with curl
- `curl -s <api_url> | python3 -m json.tool` — hit an API, pretty-print JSON
- `scp <local> user@remote:/path/` — copy to remote
- `scp user@remote:/path/<file> .` — copy from remote
- `rsync -avz --progress ./data/ user@remote:/data/` — sync directories (faster than scp, resumes on failure)

Use `rsync` over `scp` for anything large — it only transfers changed bytes and handles interrupted connections.

## WSL2 (Windows Subsystem for Linux)

For Windows users: WSL2 gives a real Linux environment without dual-booting.

- `wsl --install -d Ubuntu-24.04` (in PowerShell admin)
- GPU passthrough works with NVIDIA drivers installed on **Windows** side (not Linux)

## macOS → Linux Gotchas

| macOS | Linux | Note |
| --- | --- | --- |
| `brew install` | `sudo apt install` | Different package names |
| `open file.txt` | `xdg-open file.txt` | No GUI on remote — use `cat`/`less` |
| `pbcopy`/`pbpaste` | N/A | No clipboard over SSH |
| `~/.zshrc` | `~/.bashrc` | Different default shells |
| `/opt/homebrew/` | `/usr/bin/` | Different binary locations |
| Case-insensitive FS | Case-sensitive FS | `file Model.py` ≠ `file model.py` |
| `\n` line endings | `\n` line endings | Same. Windows uses `\r\n` (run `dos2unix`) |

## Related

- \[\[AI Engineering - Terminal and Shell\]\]
- \[\[SSH & Remote File Transfer\]\]