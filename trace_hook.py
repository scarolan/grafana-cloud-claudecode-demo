#!/usr/bin/env python3
"""
Claude Code Tracing Hook — OpenTelemetry Instrumentation

Reads hook event JSON from stdin (Claude Code hook protocol), creates OTel spans
for each tool call, and exports them to Grafana Cloud Tempo.

All tool calls within a session share a single trace ID, with each tool call
as a child span of a root session span. This gives a proper trace waterfall
showing the full session flow.

Hook events handled:
  - SessionStart:        Generates trace ID + root span ID, records session start time
  - PreToolUse:          Records start timestamp to temp file for duration calculation
  - PostToolUse:         Creates a child span parented to the session root
  - PostToolUseFailure:  Same as PostToolUse but marks span as ERROR
  - SessionEnd:          Creates the root session span covering the full session duration

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
            # Always override GRAFANA_/TRACE_ vars from .env — the shell
            # environment may contain unrelated tokens (e.g. MCP service
            # account keys) that don't work for OTLP gateway auth.
            if key and (key.startswith("GRAFANA_") or key.startswith("TRACE_")):
                os.environ[key] = value
            elif key and key not in os.environ:
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
    from opentelemetry.trace import StatusCode, SpanKind, NonRecordingSpan, SpanContext, TraceFlags
    from opentelemetry.sdk.trace.id_generator import IdGenerator
    import opentelemetry.trace as trace_api
except ImportError:
    sys.exit(0)

# ---------------------------------------------------------------------------
# Temp directory for cross-invocation state
# ---------------------------------------------------------------------------
TRACES_DIR = os.path.join(tempfile.gettempdir(), "claude-traces")


def _events_path(session_id):
    return os.path.join(TRACES_DIR, f"{session_id}_events.jsonl")


def _session_path(session_id):
    return os.path.join(TRACES_DIR, f"{session_id}_session.json")


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


def _make_provider(id_generator=None):
    kwargs = {"resource": RESOURCE}
    if id_generator:
        kwargs["id_generator"] = id_generator
    provider = TracerProvider(**kwargs)
    provider.add_span_processor(SimpleSpanProcessor(_make_exporter()))
    return provider


class _FixedIdGenerator(IdGenerator):
    """Returns pre-determined trace and span IDs — used to give the session root span exact IDs."""
    def __init__(self, trace_id_int, span_id_int):
        self._trace_id = trace_id_int
        self._span_id = span_id_int

    def generate_trace_id(self):
        return self._trace_id

    def generate_span_id(self):
        return self._span_id


# ---------------------------------------------------------------------------
# Session context: trace ID + root span ID persisted across hook invocations
# ---------------------------------------------------------------------------
def _new_span_id():
    return os.urandom(8).hex()


def _new_trace_id():
    return os.urandom(16).hex()


def _save_session(session_id, trace_id, root_span_id, start_ns):
    os.makedirs(TRACES_DIR, exist_ok=True)
    with open(_session_path(session_id), "w") as f:
        json.dump({"trace_id": trace_id, "root_span_id": root_span_id, "start_ns": start_ns}, f)


def _load_session(session_id):
    path = _session_path(session_id)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def _update_session(session_id, **kwargs):
    """Merge new fields into the session JSON without overwriting unrelated keys."""
    path = _session_path(session_id)
    data = {}
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)
    data.update(kwargs)
    os.makedirs(TRACES_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def _make_parent_context(trace_id_hex, span_id_hex):
    """Build an OTel context with an explicit parent span — used to attach tool spans to the session root."""
    span_ctx = SpanContext(
        trace_id=int(trace_id_hex, 16),
        span_id=int(span_id_hex, 16),
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )
    return trace_api.set_span_in_context(NonRecordingSpan(span_ctx))


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
    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR", os.path.dirname(os.path.abspath(__file__))
    )
    if project_dir and p.startswith(project_dir):
        p = p[len(project_dir):].lstrip("/\\")
        return p[:200] if p else "."
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
        if tool_input.get("description"):
            attrs["tool.description"] = str(tool_input["description"])[:200]
    elif tool_name in ("Grep", "Glob"):
        attrs["tool.pattern"] = str(tool_input.get("pattern", ""))[:200]
    elif tool_name == "Agent":
        attrs["tool.agent_type"] = str(tool_input.get("subagent_type", ""))
        if tool_input.get("description"):
            attrs["tool.description"] = str(tool_input["description"])[:200]

    try:
        input_bytes = len(json.dumps(tool_input))
        attrs["tool.input_size"] = input_bytes
        attrs["tool.estimated_input_tokens"] = input_bytes // 4
    except (TypeError, ValueError):
        pass
    if tool_input.get("run_in_background"):
        attrs["tool.background"] = True

    return attrs


# ---------------------------------------------------------------------------
# Hook handlers
# ---------------------------------------------------------------------------
def handle_session_start(hook_data):
    """Generate a trace ID and root span ID for this session and persist them."""
    session_id = hook_data.get("session_id", "unknown")
    _save_session(session_id, _new_trace_id(), _new_span_id(), time.time_ns())


def _close_prompt_span(session, end_ns):
    """Emit a completed prompt span using its stored start time and pre-assigned span ID.

    The FixedIdGenerator ensures the span ID matches what tool child spans already
    recorded as their parent, so the waterfall assembles correctly in Tempo.
    """
    id_gen = _FixedIdGenerator(
        trace_id_int=int(session["trace_id"], 16),
        span_id_int=int(session["prompt_span_id"], 16),
    )
    parent_ctx = _make_parent_context(session["trace_id"], session["root_span_id"])
    provider = _make_provider(id_generator=id_gen)
    try:
        tracer = provider.get_tracer("claude-code-hooks")
        span = tracer.start_span(
            name="prompt",
            kind=SpanKind.INTERNAL,
            context=parent_ctx,
            start_time=session["prompt_start_ns"],
            attributes={"user.prompt": session["current_prompt"]},
        )
        span.set_status(StatusCode.OK)
        span.end(end_time=end_ns)
        provider.force_flush()
    finally:
        provider.shutdown()


def handle_user_prompt(hook_data):
    """UserPromptSubmit: close the previous prompt span (if any) and open a new one."""
    session_id = hook_data.get("session_id", "unknown")
    prompt = hook_data.get("prompt", "").strip()
    if not prompt:
        return
    if len(prompt) > 500:
        prompt = prompt[:497] + "..."

    now_ns = time.time_ns()
    session = _load_session(session_id)

    # Close the prompt span from the previous turn now that we know its end time
    if session and session.get("prompt_span_id"):
        _close_prompt_span(session, end_ns=now_ns)

    _update_session(session_id,
        current_prompt=prompt,
        prompt_span_id=_new_span_id(),
        prompt_start_ns=now_ns,
    )


def handle_pre(hook_data):
    """PreToolUse: record start time for later duration calculation."""
    session_id = hook_data.get("session_id", "unknown")
    _append_event(session_id, {
        "tool_use_id": hook_data.get("tool_use_id", ""),
        "tool_name": hook_data.get("tool_name", ""),
        "start_ns": time.time_ns(),
    })


def handle_post(hook_data, is_error=False):
    """PostToolUse / PostToolUseFailure: create a child span under the session root."""
    session_id = hook_data.get("session_id", "unknown")
    tool_use_id = hook_data.get("tool_use_id", "")
    tool_name = hook_data.get("tool_name", "unknown")

    pre = _find_event(session_id, tool_use_id)
    start_ns = pre["start_ns"] if pre else time.time_ns()
    end_ns = time.time_ns()

    attrs = {
        "tool.name": tool_name,
        "tool.status": "error" if is_error else "ok",
        "session.id": session_id,
    }

    tool_input = hook_data.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}
    attrs.update(_extract_attrs(tool_name, tool_input))

    tool_response = hook_data.get("tool_response", "")
    if isinstance(tool_response, dict):
        try:
            response_bytes = len(json.dumps(tool_response))
            attrs["tool.response_size"] = response_bytes
            attrs["tool.estimated_output_tokens"] = response_bytes // 4
        except (TypeError, ValueError):
            pass
    elif isinstance(tool_response, str):
        response_bytes = len(tool_response)
        attrs["tool.response_size"] = response_bytes
        attrs["tool.estimated_output_tokens"] = response_bytes // 4

    if is_error:
        resp = tool_response
        if isinstance(resp, dict):
            resp = json.dumps(resp)
        attrs["tool.error"] = str(resp)[:500]

    session = _load_session(session_id)
    if session and session.get("prompt_span_id"):
        # Parent off the active prompt span — gives the 3-level waterfall:
        # session → prompt → tool calls
        parent_ctx = _make_parent_context(session["trace_id"], session["prompt_span_id"])
    elif session:
        parent_ctx = _make_parent_context(session["trace_id"], session["root_span_id"])
    else:
        parent_ctx = None
    if session and session.get("current_prompt"):
        attrs["user.prompt"] = session["current_prompt"]

    provider = _make_provider()
    try:
        tracer = provider.get_tracer("claude-code-hooks")
        span = tracer.start_span(
            name=f"tool:{tool_name}",
            kind=SpanKind.INTERNAL,
            context=parent_ctx,
            start_time=start_ns,
            attributes=attrs,
        )
        span.set_status(StatusCode.ERROR, attrs.get("tool.error", "")) if is_error else span.set_status(StatusCode.OK)
        span.end(end_time=end_ns)
        provider.force_flush()
    finally:
        provider.shutdown()


def handle_session_end(hook_data):
    """Create the root session span covering the full session duration.

    Uses a FixedIdGenerator so the span gets the exact trace_id and span_id
    that were stored at SessionStart — making tool call spans proper children
    in the Tempo waterfall.
    """
    session_id = hook_data.get("session_id", "unknown")
    session = _load_session(session_id)
    if not session:
        return

    end_ns = time.time_ns()
    start_ns = session["start_ns"]

    # Close the last prompt span before emitting the root session span
    if session.get("prompt_span_id"):
        _close_prompt_span(session, end_ns=end_ns)

    id_gen = _FixedIdGenerator(
        trace_id_int=int(session["trace_id"], 16),
        span_id_int=int(session["root_span_id"], 16),
    )
    provider = _make_provider(id_generator=id_gen)
    try:
        tracer = provider.get_tracer("claude-code-hooks")
        # No parent context — this span IS the root, and its IDs come from the generator.
        span = tracer.start_span(
            name="session",
            kind=SpanKind.SERVER,
            start_time=start_ns,
            attributes={"session.id": session_id},
        )
        span.set_status(StatusCode.OK)
        span.end(end_time=end_ns)
        provider.force_flush()
    finally:
        provider.shutdown()

    for path in [_session_path(session_id), _events_path(session_id)]:
        try:
            os.remove(path)
        except OSError:
            pass


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

    if event == "SessionStart":
        handle_session_start(hook_data)
    elif event == "UserPromptSubmit":
        handle_user_prompt(hook_data)
    elif event == "PreToolUse":
        handle_pre(hook_data)
    elif event == "PostToolUse":
        handle_post(hook_data)
    elif event == "PostToolUseFailure":
        handle_post(hook_data, is_error=True)
    elif event == "SessionEnd":
        handle_session_end(hook_data)


if __name__ == "__main__":
    main()
