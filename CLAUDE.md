# CLAUDE.md

## What This Is

A workshop module that instruments Claude Code with OpenTelemetry tracing, sending spans to Grafana Cloud. Students learn distributed tracing concepts by observing their own AI-assisted development workflows.

## Repository Structure

```
trace_hook.py                       # OpenTelemetry instrumentation (hooks into every tool call)
.claude/settings.json               # Hook configuration (activates tracing automatically)
.mcp.json                           # Grafana MCP server config (students edit 2 values)
dashboards/claude-code-traces.json  # Grafana dashboard definition
check-tracing-setup.sh              # Setup validator script
.env.example                        # Credential template (OTLP gateway URL, instance ID, token)
WORKSHOP_SETUP.md                   # Student setup guide
```

## How Tracing Works

Claude Code hooks in `.claude/settings.json` call `trace_hook.py` on every tool use. The hook:
1. Reads credentials from `.env`
2. Creates an OpenTelemetry span with tool name, parameters, duration, status
3. Exports directly to Grafana Cloud OTLP gateway

Graceful degradation: if Python or OTel packages are missing, hooks exit silently with no impact.

## Key Technical Details

- **Hooks are project-scoped** — only active when Claude Code runs in this directory
- **Privacy-safe** — file paths sanitized, credentials redacted from command strings
- **Span attributes**: `tool.name`, `tool.file_path`, `tool.command`, `tool.input_size`, `tool.response_size`, `tool.description`, `tool.background`
- **Service name**: `claude-code` (used in all TraceQL queries)
- **Grafana MCP server** lets Claude query datasources and build dashboards live

## Guidelines

- Keep the repo minimal — this ships to AWS, no cruft
- One setup path in `WORKSHOP_SETUP.md`, keep it simple
- Test on Windows — workshop runs on AWS Windows EC2 instances
- Students bring their own Grafana Cloud accounts (free tier)
- Use `cmd` not PowerShell for CLI commands (PowerShell mangles `--` and `@`)
