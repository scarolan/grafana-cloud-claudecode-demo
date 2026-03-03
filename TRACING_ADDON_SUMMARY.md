# 🎯 AWS + Anthropic Workshop Module: Claude Code Tracing

**Status: ✅ READY FOR WORKSHOP DELIVERY**

## Workshop Module Overview

This advanced observability module for the **AWS + Anthropic Claude Code Workshop** demonstrates how to instrument AI-powered development workflows with enterprise-grade distributed tracing. Students learn to apply traditional observability patterns to emerging AI systems.

## Components Created

### 1. **`trace_hook.py`** - Core Instrumentation
- OpenTelemetry spans for every tool call (Read, Write, Edit, Bash, Glob, Grep, Agent)
- Span context manipulation for parent-child correlation (the "reaching into internals" part you mentioned)
- Graceful fallback when Python/OTel unavailable (no errors, no breakage)
- Privacy-safe: sanitizes file paths, redacts secrets from commands
- Direct export to Grafana Cloud OTLP gateway (bypasses Alloy)

### 2. **`.claude/settings.json`** - Hooks Configuration
- Activates tracing automatically for all Claude Code sessions in this project
- Includes existing permissions from `.claude/settings.local.json`
- Only activates when Python + OpenTelemetry packages available

### 3. **`dashboards/claude-code-traces.json`** - Grafana Dashboard
- Tool usage patterns and distribution
- Session performance metrics (P95 latency, error rates)
- Real-time trace exploration table
- Session correlation and deep-dive capabilities

### 4. **`check-tracing-setup.sh`** - Setup Validator
- Works on any system (no Python required)
- Checks files, .env configuration, Python availability
- Clear status reporting with actionable next steps

### 5. **Enhanced Makefile**
- `make test-traces` - runs setup checker (no Python dependency)
- Integrated into `make test` workflow

### 6. **Updated Documentation**
- README.md includes "Extra Credit" section for students
- Clear separation between core workshop (no deps) and optional tracing
- Installation instructions for interested students

## Testing Results

✅ **Python 3.14.3 installed and working**
✅ **OpenTelemetry packages installed**
✅ **OTLP authentication working** (401 errors resolved)
✅ **Test traces successfully sent** to Grafana Cloud
✅ **Setup checker shows all green**
✅ **Real Claude Code operations traced** (this session generated traces!)

## Student Experience

**Without Python:** Core workshop works normally, zero impact, no setup needed
**With Python:** Add 2 packages → get real-time traces of Claude Code usage

## Demo Flow Suggestion

1. **Show the dashboard first** - import `claude-code-traces.json`
2. **Start a Claude Code session** in this directory
3. **Do normal Claude Code work** - read files, edit code, run commands
4. **Switch to dashboard** - show real-time traces appearing
5. **Explore patterns** - tool usage, performance, session correlation

## Workshop Integration

- **Zero disruption** to existing workshop content
- **Graceful degradation** on bare-bones workstations
- **Easy opt-in** for advanced students
- **Great presenter tool** for showing observability concepts

## Files Modified/Created

```
✅ trace_hook.py                    # OpenTelemetry instrumentation
✅ .claude/settings.json            # Hooks configuration
✅ dashboards/claude-code-traces.json # Tracing dashboard
✅ check-tracing-setup.sh           # Setup validator
✅ Makefile                         # Added test-traces target
✅ README.md                        # Extra credit section
✅ alloy/config.alloy               # Enabled tracing pipeline
```

The tracing addon is production-ready for workshop demonstrations!