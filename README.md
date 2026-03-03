# Demo Builder

A template for Grafana SEs to rapidly build customer demos that ship telemetry (metrics, logs, traces) to Grafana Cloud.

**How it works:** Copy this template, describe your demo scenario to Claude Code, and it builds out the infrastructure, telemetry pipeline, and tests for you.

## Prerequisites

| Tool | Required | Install |
|------|----------|---------|
| Make | Yes | Pre-installed on macOS/Linux; WSL: `sudo apt install make` |
| Docker Desktop | Yes | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| GitHub CLI (`gh`) | Yes | [cli.github.com](https://cli.github.com/) |
| Claude Code | Yes | [docs.anthropic.com/claude-code](https://docs.anthropic.com/en/docs/claude-code) |
| Terraform | If demo needs cloud resources | [terraform.io/downloads](https://www.terraform.io/downloads) |
| k6 | For load testing | [grafana.com/docs/k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) |
| BATS | For running tests | [github.com/bats-core/bats-core](https://github.com/bats-core/bats-core) |

## Quick Start

### 1. Create your demo repo from this template

Name it `grafana-cloud-<technology>-demo` (e.g., `grafana-cloud-oracle-demo`, `grafana-cloud-mssql-demo`):

```bash
gh repo create grafana-cloud-mytech-demo --template grafana/demo-builder --private
sleep 5
gh repo clone grafana-cloud-mytech-demo
cd grafana-cloud-mytech-demo
```

### 2. Configure Grafana Cloud credentials

```bash
cp .env.example .env
# Edit .env with your Grafana Cloud credentials
# Find them at: grafana.com → My Account → Stack details
```

### 3. Verify prerequisites

```bash
make preflight
```

### 4. Add Grafana MCP server (for dashboards)

Create a Service Account with **Editor** role in your Grafana Cloud instance (Administration > Service Accounts), generate a token, then:

```bash
claude mcp add --transport stdio grafana \
    --env GRAFANA_URL=https://your-instance.grafana.net \
    --env GRAFANA_API_KEY=glsa_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
    -- docker run -i --rm \
      -e GRAFANA_URL \
      -e GRAFANA_API_KEY \
      mcp/grafana --transport=stdio
```

This lets Claude Code create and edit dashboards directly in your Grafana Cloud instance.

### 5. Describe your scenario to Claude Code

```bash
claude
```

Tell Claude what you're demoing. For example:
> "I need a demo showing a Python Flask app with PostgreSQL. The app should expose REST endpoints, emit traces via OpenTelemetry, and I need to show database query metrics in Grafana Cloud."

Claude Code reads `CLAUDE.md` and follows the 10-step workflow to build your demo.

### 6. Start, test, and demo

```bash
make start          # Start all services
make test           # Verify everything works
make load-test      # Generate traffic (optional)
make stop           # Tear down when done
```

## 🎯 Extra Credit: Claude Code Tracing

**Optional advanced feature - no Python required for main workshop!**

This repository includes an OpenTelemetry tracing addon that instruments Claude Code sessions, sending detailed traces to Grafana Cloud. Perfect for instructor demonstrations and advanced students who want to explore observability of AI tooling.

### What It Does

- **Traces Every Tool Call**: Read, Write, Edit, Bash, Glob, Grep, Agent → trace spans
- **Performance Metrics**: Execution time, result sizes, error rates
- **Session Correlation**: All spans linked within each Claude Code session
- **Privacy Safe**: File paths sanitized, commands redacted for secrets
- **Zero Impact**: Main workshop works normally even without Python

### Quick Check

```bash
# Check if tracing addon is ready (works on any system)
bash check-tracing-setup.sh
```

### Setup for Tracing (Students: Optional!)

**If you want to see Claude Code traces in Grafana Cloud:**

1. **Install Python** (any recent version)
2. **Install tracing packages:**
   ```bash
   pip install opentelemetry-distro opentelemetry-exporter-otlp
   ```
3. **Verify setup:** `bash check-tracing-setup.sh`
4. **Use Claude Code normally** - traces flow automatically!

**How it works internally:**
- `.claude/settings.json` hooks activate when Python is available
- `trace_hook.py` instruments tool calls → OpenTelemetry spans
- Direct export to Grafana Cloud OTLP gateway (no Alloy needed)
- Graceful fallback when Python unavailable (no errors)

### Dashboard Import

1. Open your Grafana Cloud instance
2. Go to **Dashboards** → **New** → **Import**
3. Upload `dashboards/claude-code-traces.json`
4. Configure your Tempo data source
5. Explore Claude Code session traces in real-time!

### Demo Flow

1. **Start a Claude Code session** in this directory
2. **Use Claude Code normally** - every tool call creates traces
3. **Open the dashboard** to see real-time trace data
4. **Show workflow patterns** - tool usage, performance, session flows

Perfect for demonstrating how modern AI tooling can be observed and optimized just like any other distributed system.

## Template Structure

```
├── CLAUDE.md                    # Guide for Claude Code (the brain)
├── README.md                    # This file
├── Makefile                     # Task runner (run 'make help')
├── .env.example                 # Grafana Cloud credentials template
├── .gitignore                   # Prevents secrets from being committed
├── docker-compose.yml           # Services (Alloy + your demo apps)
├── alloy/
│   └── config.alloy             # Telemetry pipeline configuration
├── terraform/                   # Cloud infrastructure (when needed)
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── scripts/
│   ├── preflight-check.sh       # Prerequisite verification
│   ├── start-demo.sh            # Start everything
│   └── stop-demo.sh             # Stop everything
├── tests/
│   ├── README.md                # Testing guide
│   ├── preflight.bats           # Tool/config checks
│   ├── smoke.bats               # Service health checks
│   └── telemetry.bats           # Data flow verification
├── k6/
│   ├── README.md                # Load testing guide
│   └── load-test.js             # k6 load test script
└── dashboards/
    └── README.md                # Dashboard export/import instructions
```

## Conventions

- **Docker Compose V2** — `docker compose` (space, not hyphen)
- **Pinned image versions** — no `:latest` tags
- **Health checks on every service** — enables reliable `depends_on`
- **All secrets in `.env`** — never hardcoded
- **Local Terraform state** — demos are ephemeral, no remote backends
- **BATS for testing** — purpose-built for CLI/infrastructure verification
- **Dashboards via Grafana MCP** — Claude Code pushes dashboards directly to Grafana Cloud

## Available Make Targets

Run `make help` to see all targets:

| Target | Description |
|--------|-------------|
| `make help` | Show available targets |
| `make preflight` | Run preflight checks |
| `make start` | Start the demo |
| `make stop` | Stop the demo |
| `make test` | Run all tests |
| `make test-preflight` | Run preflight tests only |
| `make test-smoke` | Run smoke tests only |
| `make test-telemetry` | Run telemetry tests only |
| `make load-test` | Run k6 load test |
| `make clean` | Remove containers, volumes, networks |

## Graduating a Demo

When a demo is polished enough to share across the SE team:

1. Ensure all tests pass (`make test`)
2. Update this README with demo-specific documentation
3. Export and commit dashboards to `dashboards/`
4. Request transfer to the grafana org via your team lead
