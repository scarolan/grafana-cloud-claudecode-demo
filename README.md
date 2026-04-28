# Claude Code Tracing Workshop

Instrument Claude Code with OpenTelemetry distributed tracing. Every tool call (Read, Write, Edit, Bash, etc.) becomes a trace span in Grafana Cloud.

![Claude Code Tracing Dashboard](images/claude_code_dashboard.png)

## What You'll Learn

- How to observe AI tooling with distributed tracing
- OpenTelemetry instrumentation in practice
- Grafana Cloud visualization of AI workflows
- How Claude Code can build its own observability dashboards via MCP

## Prerequisites

| Tool | Notes |
|------|-------|
| **Claude Code** | https://docs.anthropic.com/en/docs/claude-code |
| **Python 3.8+** | https://www.python.org/downloads/ |
| **Git** | https://git-scm.com/downloads |
| **Grafana Cloud** | Free tier at https://grafana.com |

## Setup

**[Follow the setup guide](WORKSHOP_SETUP.md)** (~5 minutes)

## How It Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │───>│  OpenTelemetry  │───>│  Grafana Cloud  │
│   (Anthropic)   │    │  (trace_hook)   │    │     (Tempo)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        v                       v                       v
   Hook Events             Span Hierarchy           Visualization
   - SessionStart          - session (root)          - Overview dash
   - UserPromptSubmit      - prompt (child)          - Deep Dive dash
   - PreToolUse/Post       - tool:X (leaf)           - Trace waterfall
   - SessionEnd            - Duration + attrs        - Latency metrics
```

Each Claude Code session produces a single trace with a 3-level span hierarchy: a root **session** span covering the full session, **prompt** spans for each user message, and **tool** child spans nested under the prompt that triggered them. This gives a proper waterfall in Tempo showing exactly which tools ran in response to each prompt.

Hook events in `.claude/settings.json` call `trace_hook.py` on `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, and `SessionEnd`. A `FixedIdGenerator` assigns deterministic span IDs so the hierarchy assembles correctly across separate hook invocations.

The Grafana MCP server lets Claude query your datasources and build dashboards live — so students watch AI create its own observability stack.

## What Gets Traced

- **Tool calls**: Read, Write, Edit, Bash, Glob, Grep, Agent
- **Attributes**: file paths, command descriptions, input/output sizes, estimated token usage
- **Context**: the user prompt that triggered each tool call (`user.prompt`)
- **Performance**: duration per tool, P50/P95/P99 latencies, error rates
- **Privacy**: paths sanitized, credentials redacted, zero data retained locally

## Dashboards

| Dashboard | Description |
|-----------|-------------|
| **Claude Code Traces — Overview** | Session volume, tool usage breakdown, error rate, P95 latency |
| **Claude Code Traces — Deep Dive** | P50/P95/P99 latency trends, trace explorer, slowest tool calls |

Both dashboards are pre-linked to each other for easy navigation.

## Repository Structure

```
.claude/settings.json               # Hook configuration (6 hook events)
.mcp.json                           # Grafana MCP server config (edit 2 values)
trace_hook.py                       # OpenTelemetry instrumentation
dashboards/claude-code-traces.json  # Overview dashboard
dashboards/claude-code-traces-v2.json  # Deep Dive dashboard
architecture.html                   # Visual diagram of span hierarchy
check-tracing-setup.sh              # Setup validator
.env.example                        # Credential template
WORKSHOP_SETUP.md                   # Step-by-step setup guide
```

## Exploring Further

Once tracing is running, try asking Claude:

- "Add a panel showing file access patterns"
- "What are the slowest operations in my traces?"
- "Create an alert for tool calls over 10 seconds"

Claude can analyze the traces AND build the dashboards to visualize them.
