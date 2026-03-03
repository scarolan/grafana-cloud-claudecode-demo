#!/usr/bin/env python3
"""
Claude Code Tracing Hook - OpenTelemetry Instrumentation

This hook instruments Claude Code sessions with distributed tracing, sending
traces to Grafana Cloud for visualization. It captures tool calls, their
duration, parameters, and results as OpenTelemetry spans.

Usage: Automatically activated via .claude/settings.json hooks configuration.
"""

import os
import sys
import json
import time
import traceback
import argparse
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Load .env file if available
def load_env_file():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key, value = key.strip(), value.strip()
                        # Don't override existing environment variables
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            print(f"WARNING: Failed to load .env file: {e}", file=sys.stderr)

# Load environment variables at module import
load_env_file()

# OpenTelemetry imports with fallback error handling
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.span import Span
    OTEL_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: OpenTelemetry not available: {e}", file=sys.stderr)
    print("Install with: pip install opentelemetry-distro opentelemetry-exporter-otlp", file=sys.stderr)
    OTEL_AVAILABLE = False

class ClaudeCodeTracer:
    """OpenTelemetry tracer for Claude Code sessions"""

    def __init__(self):
        self.tracer = None
        self.current_span = None
        self.session_id = None
        self.enabled = False

        if not OTEL_AVAILABLE:
            return

        try:
            self._setup_tracing()
            self.enabled = True
            print("+ Claude Code tracing initialized", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to initialize tracing: {e}", file=sys.stderr)
            print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)

    def _setup_tracing(self):
        """Initialize OpenTelemetry tracing"""
        # Generate session ID for correlation
        import uuid
        self.session_id = str(uuid.uuid4())[:8]

        # Resource identifies this service
        resource = Resource.create({
            "service.name": "claude-code",
            "service.version": "1.0.0",
            "deployment.environment": "workshop",
            "session.id": self.session_id,
        })

        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()

        # Configure exporter based on TRACE_MODE
        trace_mode = os.environ.get("TRACE_MODE", "direct")

        if trace_mode == "direct":
            exporter = self._create_direct_exporter()
        else:
            exporter = self._create_alloy_exporter()

        # Add batch span processor
        span_processor = BatchSpanProcessor(exporter)
        tracer_provider.add_span_processor(span_processor)

        # Get tracer
        self.tracer = trace.get_tracer("claude-code-hook")

    def _create_direct_exporter(self) -> OTLPSpanExporter:
        """Create exporter for direct Grafana Cloud OTLP gateway"""
        otlp_url = os.environ.get("GRAFANA_OTLP_GATEWAY_URL")
        instance_id = os.environ.get("GRAFANA_OTLP_INSTANCE_ID")
        token = os.environ.get("GRAFANA_CLOUD_TOKEN")

        if not all([otlp_url, instance_id, token]):
            raise ValueError("Missing GRAFANA_OTLP_* environment variables for direct mode")

        # OTLP HTTP endpoint expects /v1/traces suffix
        endpoint = f"{otlp_url}/v1/traces"

        # Grafana Cloud OTLP gateway uses Basic auth with instance_id:token
        import base64
        auth_string = f"{instance_id}:{token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        headers = {
            "Authorization": f"Basic {auth_b64}",
        }

        return OTLPSpanExporter(endpoint=endpoint, headers=headers)

    def _create_alloy_exporter(self) -> OTLPSpanExporter:
        """Create exporter for local Alloy collector"""
        # Alloy OTLP HTTP endpoint (when running via docker-compose)
        endpoint = "http://localhost:4318/v1/traces"

        # Try to detect if we're inside Docker network
        if os.path.exists("/.dockerenv"):
            endpoint = "http://alloy:4318/v1/traces"

        return OTLPSpanExporter(endpoint=endpoint)

    def start_tool_span(self, tool_name: str, args: Dict[str, Any]) -> Optional[Span]:
        """Start a span for a tool call"""
        if not self.enabled or not self.tracer:
            return None

        try:
            # Create span for this tool call
            span = self.tracer.start_span(
                name=f"tool/{tool_name}",
                kind=trace.SpanKind.INTERNAL
            )

            # Add standard attributes
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("session.id", self.session_id)

            # Add tool-specific attributes (sanitized)
            self._add_tool_attributes(span, tool_name, args)

            # Handle parent-child correlation by setting span context
            # This is the "reaching into internals" part Sean mentioned
            if self.current_span:
                try:
                    # Get the current span's trace context
                    parent_context = self.current_span.get_span_context()
                    if hasattr(span, '_context'):
                        # Override the trace_id to match parent (for correlation)
                        span._context = span._context._replace(trace_id=parent_context.trace_id)
                except Exception as e:
                    print(f"WARNING: Span context correlation failed: {e}", file=sys.stderr)

            self.current_span = span
            return span

        except Exception as e:
            print(f"ERROR: Failed to start span for {tool_name}: {e}", file=sys.stderr)
            return None

    def _add_tool_attributes(self, span: Span, tool_name: str, args: Dict[str, Any]):
        """Add tool-specific attributes to span, with sanitization"""
        try:
            # Common attributes for all tools
            span.set_attribute("tool.args_count", len(args))

            # Tool-specific attribute handling
            if tool_name == "Read":
                file_path = args.get("file_path", "")
                span.set_attribute("file.path", self._sanitize_path(file_path))
                if "limit" in args:
                    span.set_attribute("file.limit", args["limit"])

            elif tool_name == "Write":
                file_path = args.get("file_path", "")
                content_length = len(str(args.get("content", "")))
                span.set_attribute("file.path", self._sanitize_path(file_path))
                span.set_attribute("file.content_length", content_length)

            elif tool_name == "Edit":
                file_path = args.get("file_path", "")
                old_length = len(str(args.get("old_string", "")))
                new_length = len(str(args.get("new_string", "")))
                span.set_attribute("file.path", self._sanitize_path(file_path))
                span.set_attribute("edit.old_length", old_length)
                span.set_attribute("edit.new_length", new_length)
                span.set_attribute("edit.replace_all", args.get("replace_all", False))

            elif tool_name == "Bash":
                command = args.get("command", "")
                # Sanitize command (remove potential secrets)
                sanitized_cmd = self._sanitize_command(command)
                span.set_attribute("bash.command", sanitized_cmd[:200])  # Limit length
                span.set_attribute("bash.background", args.get("run_in_background", False))

            elif tool_name == "Glob":
                pattern = args.get("pattern", "")
                span.set_attribute("glob.pattern", pattern)
                if "path" in args:
                    span.set_attribute("glob.path", self._sanitize_path(args["path"]))

            elif tool_name == "Grep":
                pattern = args.get("pattern", "")
                span.set_attribute("grep.pattern", pattern[:100])  # Limit length
                span.set_attribute("grep.case_insensitive", args.get("-i", False))
                if "glob" in args:
                    span.set_attribute("grep.glob", args["glob"])
                if "output_mode" in args:
                    span.set_attribute("grep.output_mode", args["output_mode"])

            elif tool_name == "Agent":
                subagent = args.get("subagent_type", "")
                span.set_attribute("agent.subagent_type", subagent)
                span.set_attribute("agent.description", args.get("description", "")[:100])
                span.set_attribute("agent.background", args.get("run_in_background", False))

        except Exception as e:
            print(f"WARNING: Failed to add attributes for {tool_name}: {e}", file=sys.stderr)

    def _sanitize_path(self, path: str) -> str:
        """Sanitize file paths to remove sensitive info"""
        if not path:
            return path

        # Replace user directory with ~
        home_dir = os.path.expanduser("~")
        if path.startswith(home_dir):
            path = "~" + path[len(home_dir):]

        # Limit length
        return path[:200]

    def _sanitize_command(self, command: str) -> str:
        """Sanitize bash commands to remove potential secrets"""
        if not command:
            return command

        # Common patterns to redact
        sensitive_patterns = [
            "password", "token", "key", "secret", "credential",
            "AWS_ACCESS", "GRAFANA_", "GITHUB_TOKEN"
        ]

        sanitized = command
        for pattern in sensitive_patterns:
            if pattern.lower() in command.lower():
                # Replace sensitive values with [REDACTED]
                words = command.split()
                for i, word in enumerate(words):
                    if pattern.lower() in word.lower() and "=" in word:
                        key, _ = word.split("=", 1)
                        words[i] = f"{key}=[REDACTED]"
                sanitized = " ".join(words)
                break

        return sanitized

    def finish_tool_span(self, span: Optional[Span], success: bool = True,
                        error: Optional[str] = None, result_size: Optional[int] = None):
        """Finish a tool span with status and metrics"""
        if not span:
            return

        try:
            # Add result metrics
            if result_size is not None:
                span.set_attribute("result.size", result_size)

            # Set status
            if success:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR, error or "Tool execution failed"))
                if error:
                    span.set_attribute("error.message", error[:500])  # Limit length

            # End the span
            span.end()

            # Reset current span if this was it
            if span == self.current_span:
                self.current_span = None

        except Exception as e:
            print(f"ERROR: Failed to finish span: {e}", file=sys.stderr)

# Global tracer instance
_tracer = None

def get_tracer() -> ClaudeCodeTracer:
    """Get or create the global tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = ClaudeCodeTracer()
    return _tracer

def on_tool_start(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Hook called when a tool starts executing"""
    tracer = get_tracer()
    span = tracer.start_tool_span(tool_name, args)

    # Return metadata to pass to on_tool_end
    return {"span": span, "start_time": time.time()}

def on_tool_end(tool_name: str, args: Dict[str, Any], result: Any,
                metadata: Dict[str, Any], error: Optional[Exception] = None):
    """Hook called when a tool finishes executing"""
    span = metadata.get("span")
    if not span:
        return

    start_time = metadata.get("start_time", time.time())
    duration = time.time() - start_time

    # Calculate result size
    result_size = None
    if result is not None:
        try:
            result_size = len(str(result))
        except:
            pass

    # Add duration
    span.set_attribute("tool.duration_ms", int(duration * 1000))

    # Finish span
    tracer = get_tracer()
    tracer.finish_tool_span(
        span,
        success=(error is None),
        error=str(error) if error else None,
        result_size=result_size
    )

def main():
    """Command-line interface for the tracing hook"""

    parser = argparse.ArgumentParser(description="Claude Code OpenTelemetry Tracing Hook")
    parser.add_argument("--hook", choices=["tool-start", "tool-end"],
                       help="Hook type to execute")
    parser.add_argument("--tool-name", help="Name of the tool being executed")
    parser.add_argument("--args", help="JSON-encoded tool arguments")
    parser.add_argument("--result", help="JSON-encoded tool result")
    parser.add_argument("--metadata", help="JSON-encoded metadata from tool-start")
    parser.add_argument("--error", help="Error message if tool failed")
    parser.add_argument("--test", action="store_true", help="Run test mode")

    args = parser.parse_args()

    if args.test:
        return run_test()

    if not args.hook:
        parser.error("--hook is required")

    if args.hook == "tool-start":
        return handle_tool_start(args)
    elif args.hook == "tool-end":
        return handle_tool_end(args)

    return 0

def handle_tool_start(args):
    """Handle tool-start hook"""
    try:
        tool_name = args.tool_name or "Unknown"
        tool_args = json.loads(args.args or "{}")

        metadata = on_tool_start(tool_name, tool_args)

        # Output metadata for tool-end hook to consume
        print(json.dumps(metadata, default=str))
        return 0
    except Exception as e:
        print(f"ERROR in tool-start hook: {e}", file=sys.stderr)
        return 1

def handle_tool_end(args):
    """Handle tool-end hook"""
    try:
        tool_name = args.tool_name or "Unknown"
        tool_args = json.loads(args.args or "{}")
        metadata = json.loads(args.metadata or "{}")
        result = args.result  # Keep as string
        error = Exception(args.error) if args.error else None

        on_tool_end(tool_name, tool_args, result, metadata, error)
        return 0
    except Exception as e:
        print(f"ERROR in tool-end hook: {e}", file=sys.stderr)
        return 1

def run_test():
    """Test the tracing hook directly"""
    print("Testing Claude Code tracing hook...")

    # Simulate tool calls
    tracer = get_tracer()

    if not tracer.enabled:
        print("ERROR: Tracing not enabled. Check environment variables.")
        return 1

    # Test a few tool calls
    test_cases = [
        ("Read", {"file_path": "/tmp/test.txt"}),
        ("Bash", {"command": "echo hello world"}),
        ("Glob", {"pattern": "*.py"}),
    ]

    for tool_name, args in test_cases:
        print(f"Testing {tool_name} span...")
        metadata = on_tool_start(tool_name, args)
        time.sleep(0.1)  # Simulate work
        on_tool_end(tool_name, args, "mock result", metadata)

    print("+ Test completed. Check Grafana Cloud for traces.")
    return 0

if __name__ == "__main__":
    sys.exit(main())