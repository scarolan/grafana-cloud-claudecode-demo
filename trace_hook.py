#!/usr/bin/env python3
"""
Claude Code Tracing Hook — OpenTelemetry Instrumentation

Reads hook event JSON from stdin (Claude Code hook protocol), creates OTel spans
for each tool call, and exports them to Grafana Cloud Tempo.

Hook events handled:
  - PreToolUse:  Records start timestamp to temp file for duration calculation
  - PostToolUse: Creates a span with tool attributes and sends it
  - PostToolUseFailure: Same as PostToolUse but marks span as ERROR

Usage: Automatically activated via .claude/settings.json hooks configuration.
"""

import json
import os
import sys
import tempfile
import time

# ---------------------------------------------------------------------------
# Load .env so credentials are available even outside shell environments
# ---------------------------------------------------------------------------
def _load_env():
    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR", os.path.dirname(os.path.abspath(__file__))
    )
    env_path = os.path.join(project_dir, ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value

_load_env()

# ---------------------------------------------------------------------------
# Configuration — exit silently (code 0) if not configured
# ---------------------------------------------------------------------------
TRACE_MODE = os.environ.get("TRACE_MODE", "direct")
OTLP_GATEWAY_URL = os.environ.get("GRAFANA_OTLP_GATEWAY_URL", "")
OTLP_INSTANCE_ID = os.environ.get("GRAFANA_OTLP_INSTANCE_ID", "")
CLOUD_TOKEN = os.environ.get("GRAFANA_CLOUD_TOKEN", "")

if TRACE_MODE != "alloy" and not all([OTLP_GATEWAY_URL, OTLP_INSTANCE_ID, CLOUD_TOKEN]):
    sys.exit(0)

# ---------------------------------------------------------------------------
# OpenTelemetry imports — exit silently if not installed
# ---------------------------------------------------------------------------
try:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace import StatusCode, SpanKind
except ImportError:
    sys.exit(0)

# ---------------------------------------------------------------------------
# Temp directory for cross-invocation state (PreToolUse → PostToolUse)
# ---------------------------------------------------------------------------
TRACES_DIR = os.path.join(tempfile.gettempdir(), "claude-traces")


def _events_path(session_id):
    return os.path.join(TRACES_DIR, f"{session_id}_events.jsonl")


# ---------------------------------------------------------------------------
# OTel exporter factory
# ---------------------------------------------------------------------------
def _make_exporter():
    if TRACE_MODE == "alloy":
        return OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
    import base64
    creds = base64.b64encode(f"{OTLP_INSTANCE_ID}:{CLOUD_TOKEN}".encode()).decode()
    return OTLPSpanExporter(
        endpoint=f"{OTLP_GATEWAY_URL}/v1/traces",
        headers={"Authorization": f"Basic {creds}"},
    )


RESOURCE = Resource.create({
    "service.name": "claude-code",
    "service.version": "1.0.0",
    "deployment.environment": "workshop",
})


def _make_provider():
    provider = TracerProvider(resource=RESOURCE)
    provider.add_span_processor(SimpleSpanProcessor(_make_exporter()))
    return provider


# ---------------------------------------------------------------------------
# Event persistence (JSONL file per session, one line per PreToolUse event)
# ---------------------------------------------------------------------------
def _append_event(session_id, event):
    os.makedirs(TRACES_DIR, exist_ok=True)
    with open(_events_path(session_id), "a") as f:
        f.write(json.dumps(event) + "\n")


def _find_event(session_id, tool_use_id):
    path = _events_path(session_id)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev.get("tool_use_id") == tool_use_id:
                return ev
    return None


# ---------------------------------------------------------------------------
# Sanitisation helpers
# ---------------------------------------------------------------------------
def _sanitize_path(p):
    if not p:
        return p
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    return p[:200]


def _sanitize_cmd(cmd):
    if not cmd:
        return cmd
    for pat in ["password", "token", "key", "secret", "GRAFANA_", "AWS_ACCESS"]:
        if pat.lower() in cmd.lower():
            words = cmd.split()
            for i, w in enumerate(words):
                if pat.lower() in w.lower() and "=" in w:
                    k, _ = w.split("=", 1)
                    words[i] = f"{k}=[REDACTED]"
            return " ".join(words)
    return cmd


# ---------------------------------------------------------------------------
# Extract tool-specific span attributes from tool_input
# ---------------------------------------------------------------------------
def _extract_attrs(tool_name, tool_input):
    attrs = {}
    if not isinstance(tool_input, dict):
        return attrs
    if tool_name in ("Read", "Write"):
        attrs["tool.file_path"] = _sanitize_path(str(tool_input.get("file_path", "")))
    elif tool_name == "Edit":
        attrs["tool.file_path"] = _sanitize_path(str(tool_input.get("file_path", "")))
    elif tool_name == "Bash":
        attrs["tool.command"] = _sanitize_cmd(str(tool_input.get("command", "")))[:200]
    elif tool_name in ("Grep", "Glob"):
        attrs["tool.pattern"] = str(tool_input.get("pattern", ""))[:200]
    elif tool_name == "Agent":
        attrs["tool.agent_type"] = str(tool_input.get("subagent_type", ""))
    return attrs


# ---------------------------------------------------------------------------
# Hook handlers
# ---------------------------------------------------------------------------
def handle_pre(hook_data):
    """PreToolUse: record start time for later duration calculation."""
    session_id = hook_data.get("session_id", "unknown")
    _append_event(session_id, {
        "tool_use_id": hook_data.get("tool_use_id", ""),
        "tool_name": hook_data.get("tool_name", ""),
        "start_ns": time.time_ns(),
    })


def handle_post(hook_data, is_error=False):
    """PostToolUse / PostToolUseFailure: create and export a span."""
    session_id = hook_data.get("session_id", "unknown")
    tool_use_id = hook_data.get("tool_use_id", "")
    tool_name = hook_data.get("tool_name", "unknown")

    # Look up the matching PreToolUse event for start time
    pre = _find_event(session_id, tool_use_id)
    start_ns = pre["start_ns"] if pre else time.time_ns()
    end_ns = time.time_ns()

    # Build span attributes
    attrs = {
        "tool.name": tool_name,
        "tool.status": "error" if is_error else "ok",
        "session.id": session_id,
    }

    # Parse tool_input for tool-specific attributes
    tool_input = hook_data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}
    attrs.update(_extract_attrs(tool_name, tool_input))

    # Capture error message on failure
    if is_error:
        resp = hook_data.get("tool_response", "")
        if isinstance(resp, dict):
            resp = json.dumps(resp)
        attrs["tool.error"] = str(resp)[:500]

    # Create provider, span, export, shutdown — all in one shot
    provider = _make_provider()
    try:
        tracer = provider.get_tracer("claude-code-hooks")
        span = tracer.start_span(
            name=f"tool:{tool_name}",
            kind=SpanKind.INTERNAL,
            start_time=start_ns,
            attributes=attrs,
        )
        if is_error:
            span.set_status(StatusCode.ERROR, attrs.get("tool.error", ""))
        else:
            span.set_status(StatusCode.OK)
        span.end(end_time=end_ns)
        provider.force_flush()
    finally:
        provider.shutdown()


# ---------------------------------------------------------------------------
# Main: read JSON from stdin and dispatch
# ---------------------------------------------------------------------------
def main():
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)
    try:
        hook_data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        sys.exit(0)

    event = hook_data.get("hook_event_name", "")

    if event == "PreToolUse":
        handle_pre(hook_data)
    elif event == "PostToolUse":
        handle_post(hook_data)
    elif event == "PostToolUseFailure":
        handle_post(hook_data, is_error=True)
    # Other events (SessionStart, SessionEnd, etc.) — silently ignore


if __name__ == "__main__":
    main()
