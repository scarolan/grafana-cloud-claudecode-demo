#!/bin/bash
# Claude Code Tracing Setup Checker
# Validates that all tracing components are in place

echo "🔍 Checking Claude Code tracing addon setup..."
echo ""

# Check for required files
echo "📁 Checking files:"
files=(
    "trace_hook.py"
    ".claude/settings.json"
    "dashboards/claude-code-traces.json"
    ".env"
)

all_files_exist=true
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        all_files_exist=false
    fi
done

echo ""

# Check .env for tracing variables
echo "🔧 Checking .env configuration:"
required_vars=(
    "GRAFANA_CLOUD_TOKEN"
    "GRAFANA_OTLP_GATEWAY_URL"
    "GRAFANA_OTLP_INSTANCE_ID"
    "TRACE_MODE"
)

env_configured=true
if [[ -f ".env" ]]; then
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2)
            if [[ -n "$value" && "$value" != "your_value_here" ]]; then
                echo "  ✅ $var (configured)"
            else
                echo "  ⚠️  $var (needs value)"
                env_configured=false
            fi
        else
            echo "  ❌ $var (missing)"
            env_configured=false
        fi
    done
else
    echo "  ❌ .env file missing"
    env_configured=false
fi

echo ""

# Check for Python (optional)
echo "🐍 Checking Python availability:"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    echo "  ✅ $python_version"

    # Check for OpenTelemetry packages
    if python3 -c "import opentelemetry" &> /dev/null; then
        echo "  ✅ OpenTelemetry packages installed"
        python_ready=true
    else
        echo "  ⚠️  OpenTelemetry packages needed:"
        echo "     pip install opentelemetry-distro opentelemetry-exporter-otlp"
        python_ready=false
    fi
elif command -v python &> /dev/null; then
    python_version=$(python --version 2>&1)
    echo "  ✅ $python_version"

    if python -c "import opentelemetry" &> /dev/null; then
        echo "  ✅ OpenTelemetry packages installed"
        python_ready=true
    else
        echo "  ⚠️  OpenTelemetry packages needed:"
        echo "     pip install opentelemetry-distro opentelemetry-exporter-otlp"
        python_ready=false
    fi
else
    echo "  ❌ Python not found"
    echo "     Install Python 3.8+ to enable tracing"
    python_ready=false
fi

echo ""

# Summary
echo "📊 Setup Summary:"
if $all_files_exist && $env_configured && $python_ready; then
    echo "  🎉 Tracing addon fully configured and ready!"
    echo "     Start a Claude Code session to generate traces."
elif $all_files_exist && $env_configured; then
    echo "  ⚡ Tracing addon configured but Python setup needed"
    echo "     Install Python + OpenTelemetry packages to activate tracing"
elif $all_files_exist; then
    echo "  📝 Tracing addon files ready but .env needs configuration"
    echo "     Add your Grafana Cloud credentials to .env"
else
    echo "  🔧 Tracing addon needs setup - missing files detected"
fi

echo ""
echo "💡 For help: See README.md 'Extra Credit: Claude Code Tracing' section"