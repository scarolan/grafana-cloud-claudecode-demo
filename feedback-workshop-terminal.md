# Workshop Feedback: Replace Default Terminal with Cmder

## Problem

Students using Claude Code on Windows Server 2022 Datacenter instances currently have three bad options:

- **cmd.exe** — Ugly, no tabs, no copy-paste sanity, students think it's 1995
- **PowerShell** — Mangles CLI arguments (`@` becomes splatting, `--` gets consumed), breaks `claude mcp add` and other commands with special characters
- **VSCode integrated terminal** — Wedges Claude Code into a panel inside another IDE, undermining the standalone agent experience. Can't pop out into its own window.

All three create unnecessary friction. Students spend workshop time debugging terminal issues instead of learning observability concepts.

## Proposal: Pre-install Cmder on Workshop AMIs

**Cmder** (https://cmder.app/) is a portable console emulator for Windows that solves every problem above:

- **No GPU required** — Uses GDI rendering (not OpenGL), works perfectly over RDP on Server instances
- **Ships with Git Bash** — The full version bundles Git for Windows, giving students a proper bash shell where `--`, `@`, and other CLI characters work as expected
- **Looks professional** — Monokai theme, good fonts, tabs, split panes out of the box
- **Zero config needed** — Unzip and run, or `choco install cmder -y`
- **Portable** — Can be pre-staged on the desktop as a folder, no installer, no admin prompts
- **Battle-tested** — Years of use on Windows Server environments, conferences, workshops

## Why This Matters for Claude Code

Claude Code is a standalone CLI agent. It's designed to be THE interface, not a panel inside VSCode. Running it in a proper terminal:

- Gives students the real Claude Code experience (full-screen, focused)
- Avoids PowerShell argument mangling that breaks MCP server setup commands
- Provides Git Bash as the shell, matching all documentation and examples
- Looks polished enough for a professional workshop setting

## Installation

One line in the AMI build script:

```powershell
choco install cmder -y
```

Or for maximum control, download the full zip from https://cmder.app/ and extract to `C:\tools\cmder`. Pin `Cmder.exe` to the taskbar or drop a shortcut on the desktop.

## Optional: Pre-configure for Workshop

Drop a custom `user_profile.cmd` in the Cmder config directory to auto-cd into the workshop repo and display a welcome message. Students double-click one icon and they're ready.

## Alternatives Considered

| Terminal | Problem |
|----------|---------|
| Alacritty | Requires GPU/OpenGL, crashes silently over RDP |
| WezTerm | GPU-accelerated, unreliable on Server + RDP |
| Windows Terminal | Not available on Windows Server Datacenter |
| Hyper | Electron-based, heavy, GPU issues |
| cmd.exe | Works but looks terrible, no tabs, poor UX |
| PowerShell | Argument mangling breaks CLI tools |

Cmder is the only option that is good-looking, reliable over RDP, and works on Windows Server without GPU.
