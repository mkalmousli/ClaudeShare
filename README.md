# ClaudeShare

Give specific people a username and key, and each gets an **isolated Linux desktop in the browser**:
a real terminal (run `claude` on **one shared login**), a file manager, a text editor, and an
always-visible usage meter. Each person has their own home, files, and Claude config.

- **Backend:** Python (FastAPI + Strawberry GraphQL), managed with `uv`
- **Frontend:** vanilla JS, no framework, no CSS/HTML files (only xterm.js is vendored)
- **Deploy:** Docker, one guided colour-coded setup, installed as a systemd service

## Install

Requirements: Linux with Docker and [uv](https://docs.astral.sh/uv/). Then:

```sh
git clone https://github.com/mkalmousli/ClaudeShare && cd ClaudeShare
uv run setup
```

The guided setup asks for access (Cloudflare Tunnel: browser sign-in, API token, or existing token; or local only), your
hostname, usage limits, and resource caps. The default is **browser sign-in**: setup opens Cloudflare's own page, you pick your domain and click
*Authorize*, and it creates the tunnel, the DNS record and the config for you (no token to copy). API-token
and existing-token modes are still available. It then builds the image, installs `claudeshare.service` (the only step that uses
`sudo`), has you sign the shared Claude in once, and creates the first user.

## Day to day (no root needed)

```sh
claudeshare status                 # service state + every user's usage
claudeshare on | off | restart     # the site goes down / comes back; data is kept
claudeshare boot on|off            # start automatically at boot
claudeshare logs [-f]
claudeshare user add alice         # prints URL + key (shown once)
claudeshare user list | passwd NAME | del NAME [--purge] | sessions NAME
claudeshare user limit alice 25%   # a share of the plan, or 5m / 800k tokens; add --period day|week|month
claudeshare login                  # sign the shared source Claude in again
claudeshare update                 # after `git pull`: rebuild and restart
```

If `claudeshare` is not on your PATH after setup: `uv tool update-shell`.

## How it works

- **Isolation:** every user is a real Linux account (uid 10000+, home `/data/home/<name>`, mode 700).
  The server drops to the user's uid for terminals, file operations, uploads and downloads, so the
  kernel — not path checks — keeps people apart. The container drops all capabilities except the few
  needed to switch users and has `no-new-privileges`, plus memory/CPU/pid limits.
- **Shared Claude login:** you sign a single *source* Claude CLI in (`claudeshare login`). The server
  copies its login into every user's `~/.claude`, and keeps it fresh: only the server refreshes the
  token (user copies carry no refresh token, so a rotating token can't break anyone).
- **Usage:** per-user weighted tokens (input ×1, output ×5, cache write ×1.25, cache read ×0.1) read
  from each user's own Claude session logs. The taskbar meter shows your share, time to reset and, when
  available, the whole plan's usage; click it for per-session details. At 100% the user's `claude`
  processes are stopped and new ones refuse to start until the period resets. Terminals and files keep working.
- **Sessions:** terminals survive page reloads (scrollback replayed); Claude sessions are tracked per user.
- **Auth:** scrypt-hashed keys, signed HttpOnly SameSite=Strict cookies, rate-limited login, Origin checks.
  Changing a key signs that user out everywhere.

## Know the limits

- Everyone shares one container's CPU, RAM and disk (caps are set in setup; there are no per-user disk quotas).
- Each user's copy of the Claude login is readable by that user — inherent to sharing a login.
- Plan-wide usage and token refresh use Anthropic's OAuth endpoints, which are undocumented and may change;
  both degrade quietly (the plan figure disappears; run `claudeshare login` if the shared login expires).

## Develop

```sh
uv run pytest                      # auth, accounting, file isolation, root-helper grammar, project rules
DATA_DIR=/tmp/cs RUN_DIR=/tmp/cs-run PORT=3000 uv run python -m backend.main   # as root, for real accounts
```

Rules enforced by `tests/test_rules.py`: Python-only backend, every source file ≤ 100 lines, no shell
scripts, no CSS/HTML besides the verbatim `frontend/index.html`, no `innerHTML`, no min/max-width,
styling only via `.style`.
