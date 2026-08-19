# SSH — Public-Key Auth & Remote Commands

**Source:** [Command-line Environment](https://missing.csail.mit.edu/2026/command-line-environment/) · MIT Missing Semester (YouTube: Lecture on Shell/Environment)
**Track:** SWE (Software Engineering Fundamentals)
**Ingested:** 2026-08-18

> **Scope note:** the core facts (key pairs, `ssh host cmd`, quoting, `ssh-keygen -y` passphrase validation) are from the MIT Missing Semester lecture/page. The lock-and-key metaphor, the "cryptographic challenge" phrasing, the line about encrypting the connection, and the **passphrase explanation** (a passphrase encrypts the private key file; without one the key is a plain-text file anyone with file access can copy) are short, accurate clarifications — the passphrase rationale comes from the lecture video narration as captured in the learner's notes, matching standard SSH security behavior.

## What SSH is

**SSH (Secure Shell)** lets you log into a remote machine and run commands on it as if you were sitting at its terminal. It encrypts the connection so nobody on the wire can read what you type or receive.

## Public-Key Cryptography (the "why no password" part)

SSH uses **public-key cryptography** to prove to a server that you are who you say you are — *without* typing a password.

A key pair has two halves that are mathematically linked:

- **Public key** — a piece of information you can freely *give people* (or the server) so they can **verify you**. It's like a lock that anyone can look at but only the matching key can open.
- **Private key** — your secret half. **Never give it to anyone.** It is the equivalent of your password. If someone gets it, they can impersonate you on every machine that trusts your public key.

The server holds your public key (`~/.ssh/authorized_keys`). The client proves it holds the matching private key (via a cryptographic challenge — no password needed on the wire). The server *verifies* but never needs the private key itself.

> The public key is shareable; the private key is equivalent to a password — never share it. Protecting the private key (`chmod 600 ~/.ssh/id_ed25519`) matters precisely because it's the secret.

**Add a passphrase to the private key.** A passphrase **encrypts the private key file itself**. Without one, your private key is just a **plain-text file** — if anyone (or any malware) gains access to your computer's file system, they can copy that file and immediately use it to log into your remote servers, no password or permission needed. With a passphrase, the key file is useless without the passphrase, even if stolen. Generate with `ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519` (you'll be prompted for a passphrase); validate/check an existing one with `ssh-keygen -y -f /path/to/key`.

## Running commands remotely

`ssh` is itself a program you can put anywhere in a pipeline. It can take input and produce output like any other shell command:

```bash
ssh user@server ls | wc -l
└─────┬────┘ └──┬─┘
   on        on local
 remote      machine
```

- `ssh user@server ls` — this part runs `ls` **on the remote machine**.
- The `| wc -l` — the pipe runs **on your local machine**, counting the lines of remote output that came back over the connection.

**Quoting changes WHERE the pipe runs:**

```bash
ssh user@server 'ls | wc -l'
        └─────────┬─────────┘
            both on remote machine
```

- With the command in **single quotes**, the *entire* pipeline (including the `|`) is sent to and executed **on the remote machine**, and only the final result comes back.
- Without quotes, the local shell interprets the `|`, so only the first command runs remotely and the *remote output* is piped locally.

**What this means in practice:** the two forms differ in *where the work happens*. Quoting the pipeline keeps all stages remote (only the final result crosses the wire); leaving it unquoted ships the raw output back to your machine first, then finishes the work locally.

## SSH (brief) — the rest

- `ssh alice@server` opens a remote shell; key-based auth (public-key crypto) is preferred over passwords.
- SSH can also be used with a password instead of a key; key-based auth is the preferred option.
- `scp`/`rsync` copy files to/from remote machines; `rsync` syncs incrementally.
- `~/.ssh/config` stores per-host defaults (host alias, user, identity file, port).
- A tunnel/metaprogram: any program appears as a local one through `ssh` — which is why the whole `ssh` *pipeline* example in the Shell wiki works as a single streaming command.

## Key Takeaways

1. Public key = shareable; private key = your secret, never share it (equivalent to a password).
2. The server verifies your identity using your public key — no password travels the network.
3. `ssh host cmd` runs a command on the remote machine; its stdout streams back to you.
4. Quoting decides where the pipe runs: unquoted pipe = local, quoted `'...'` = remote.
5. A passphrase encrypts the private key file; without one the key is plain text, so anyone with file access can copy and use it.
