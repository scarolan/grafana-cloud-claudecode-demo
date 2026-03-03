# AWS + Anthropic Claude Code Workshop: Advanced Observability

🤖 **Welcome to the advanced observability module** of the AWS + Anthropic Claude Code workshop! This hands-on extension demonstrates how to instrument AI-powered development workflows with OpenTelemetry distributed tracing.

**What you'll learn:** How modern AI tooling can be observed, monitored, and optimized using the same techniques we apply to distributed systems - all powered by Grafana Cloud and AWS infrastructure.

---

## 🎯 Workshop Module: Claude Code Tracing

This module adds real-time observability to your Claude Code development sessions. Every tool call (Read, Write, Edit, Bash, etc.) becomes a distributed trace span, giving unprecedented visibility into AI-assisted workflows.

### 🚀 **Core Learning Objectives**

- **Instrument AI tooling** with OpenTelemetry distributed tracing
- **Visualize development workflows** in real-time dashboards
- **Apply observability patterns** to emerging AI/ML systems
- **Demonstrate AWS + Anthropic + Grafana** integration

### ⚡ **Zero-Setup Experience**

This module is designed for **Windows workshop environments** with minimal dependencies:

- ✅ **Works immediately** - no Python installation required for core functionality
- ✅ **Graceful enhancement** - add tracing with 2 pip packages if desired
- ✅ **Enterprise-ready** - follows AWS Well-Architected observability patterns
- ✅ **Workshop-friendly** - tested on standard AWS Windows EC2 instances

---

## 🛠 Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| **Claude Code** | ✅ Yes | Pre-installed on workshop workstations |
| **Git** | ✅ Yes | Available via Git Bash on Windows |
| **Grafana Cloud account** | ✅ Yes | Provided during workshop setup |
| **Python 3.8+** | 🎯 Optional | Only needed for real-time tracing |
| **VS Code** | ✅ Yes | Pre-installed on workshop workstations |

*💡 This module works on the standard AWS workshop Windows instances without additional software.*

---

## 🚀 Quick Start

### **Students: Want Real-Time Tracing?**

📖 **[SUPER SIMPLE 5-MINUTE SETUP GUIDE →](WORKSHOP_SETUP.md)**

**TL;DR:**
1. Install Python (1 command)
2. Copy your Grafana credentials to `.env`
3. Install 2 packages (`pip install` command)
4. Import dashboard
5. **Start using Claude Code → see traces!** ✨

### **Instructors: Workshop Ready**

The repository works **immediately** for demonstrations:
- Import `dashboards/claude-code-traces.json`
- Start Claude Code session
- Show real-time traces (if Python installed)
- **Zero setup needed** for core workshop content

### **Advanced: Full Setup**

<details>
<summary>Detailed technical setup (click to expand)</summary>

### Step 1: Clone the Workshop Repository

```bash
git clone https://github.com/scarolan/grafana-cloud-claudecode-demo
cd grafana-cloud-claudecode-demo
```

### Step 2: Configure Your Grafana Cloud Stack

Update `.env` with your workshop-provided Grafana Cloud credentials:

```bash
# Your instructor will provide these values
GRAFANA_CLOUD_TOKEN=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_OTLP_INSTANCE_ID=123456
```

### Step 3: Verify Setup

```bash
bash check-tracing-setup.sh
```

### Step 4: Import the Dashboard

1. **Open your Grafana Cloud instance** (provided by instructor)
2. **Go to Dashboards** → **New** → **Import**
3. **Upload** `dashboards/claude-code-traces.json`
4. **Configure** your Tempo data source when prompted

### Step 5: Start Tracing (Optional Enhancement)

```bash
# Install Python tracing packages (Windows)
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Verify tracing is active
bash check-tracing-setup.sh
```

### Step 6: Use Claude Code & Observe

1. **Start a Claude Code session** in this directory
2. **Use Claude Code normally** - read files, edit code, run commands
3. **Open your dashboard** - watch traces appear in real-time!

</details>

---

## 🎯 Workshop Demo Flow

### **Instructor Demonstration**

Perfect for showing how **AI systems integrate with traditional observability**:

1. **Show the baseline** - Import dashboard, explain the concept
2. **Live coding session** - Use Claude Code to build something real
3. **Real-time visualization** - Dashboard updates as tools execute
4. **Deep dive analysis** - Session correlation, performance patterns
5. **Enterprise implications** - How this scales to AI-powered teams

### **Student Experience**

**Immediate Value (No Setup):**
- Complete workshop materials work as expected
- Professional-grade tracing infrastructure in place
- Learn observability concepts through AI tooling lens

**Enhanced Experience (2-Minute Setup):**
- Real-time traces of their own Claude Code usage
- Hands-on distributed tracing with OpenTelemetry
- Personal dashboard showing their development patterns

---

## 📊 What Gets Traced

### **Tool Call Instrumentation**
- **Read operations**: File access patterns, content sizes
- **Write operations**: Code generation metrics, edit frequencies
- **Bash commands**: Execution time, success/error rates
- **Agent interactions**: Sub-agent usage, delegation patterns
- **Search operations**: Glob/Grep performance and patterns

### **Performance Insights**
- **P95 latencies** per tool type
- **Error rates** and failure patterns
- **Session correlation** across entire workflows
- **Resource utilization** trends over time

### **Privacy & Security**
- **Path sanitization** - removes sensitive directories
- **Command redaction** - filters credentials and secrets
- **Configurable scope** - trace only what matters
- **Zero data retention** - all traces flow to your Grafana Cloud

---

## 🏗 Architecture: AWS + Anthropic + Grafana

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │───▶│  OpenTelemetry  │───▶│  Grafana Cloud  │
│   (Anthropic)   │    │   (trace_hook)  │    │   (AWS-hosted)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Tool Execution          Span Creation           Visualization
   • Read files            • Context capture        • Real-time dash
   • Edit code             • Duration metrics       • Performance analysis
   • Run commands          • Error tracking         • Workflow patterns
   • Agent calls           • Session correlation    • Historical trends
```

**Key Integration Points:**
- **AWS EC2** workshop instances run Claude Code + tracing
- **Anthropic API** powers Claude Code tool execution
- **Grafana Cloud** (AWS infrastructure) receives and visualizes traces
- **OpenTelemetry** standard ensures enterprise compatibility

---

## 🎓 Learning Extensions

### **For Advanced Students**

**Explore the Implementation:**
```bash
# Study the tracing implementation
code trace_hook.py

# Examine the dashboard definition
code dashboards/claude-code-traces.json

# Review the hooks configuration
code .claude/settings.json
```

**Custom Scenarios:**
- **Modify span attributes** - add custom metadata
- **Create alert rules** - notify on slow operations
- **Build team dashboards** - aggregate multiple developers
- **Integrate with CI/CD** - trace automated Claude Code usage

### **Discussion Topics**

- **How does this compare** to traditional APM approaches?
- **What enterprise patterns** could benefit from AI workflow observability?
- **How would you scale** this to a team of 100 developers using AI tools?
- **What other AI/ML systems** could benefit from distributed tracing?

---

## 📚 Workshop Resources

### **Reference Materials**
- [`trace_hook.py`](trace_hook.py) - OpenTelemetry instrumentation implementation
- [`dashboards/claude-code-traces.json`](dashboards/claude-code-traces.json) - Grafana dashboard
- [`.claude/settings.json`](.claude/settings.json) - Hooks configuration
- [`TRACING_ADDON_SUMMARY.md`](TRACING_ADDON_SUMMARY.md) - Technical implementation details

### **Troubleshooting**
```bash
# Check setup status
bash check-tracing-setup.sh

# Verify environment variables
env | grep GRAFANA

# Test trace export
python trace_hook.py --test    # (if Python installed)
```

### **Additional Workshop Modules**
- **Container Observability** - Docker + Kubernetes tracing patterns
- **Database Performance** - SQL query optimization with traces
- **Frontend Monitoring** - Real User Monitoring with Grafana Cloud
- **Infrastructure Monitoring** - AWS CloudWatch + Grafana integration

---

## 💼 Enterprise Takeaways

This workshop module demonstrates **production-ready patterns** for observing AI-powered development workflows:

- **OpenTelemetry standards** ensure vendor-neutral observability
- **AWS infrastructure** provides enterprise-scale data processing
- **Grafana Cloud** delivers production observability platform
- **Claude Code hooks** show how to instrument any AI tooling
- **Zero-impact design** maintains developer productivity

**Business Value:**
- **Measure AI ROI** - quantify developer productivity improvements
- **Optimize workflows** - identify bottlenecks in AI-assisted development
- **Ensure reliability** - monitor AI system performance and availability
- **Enable debugging** - trace complex multi-agent AI interactions

---

## 🎯 Next Steps

**Continue Your Observability Journey:**

1. **Apply these patterns** to your own AI/ML systems
2. **Explore Grafana Cloud** advanced features (alerts, SLOs, incidents)
3. **Integrate with AWS** services (CloudWatch, X-Ray, EventBridge)
4. **Build team dashboards** for AI-powered development workflows
5. **Consider enterprise deployment** - how would you scale this organization-wide?

**Questions? Ideas?** The observability community is excited about AI system monitoring. This workshop represents the cutting edge of **AI + Observability** integration.

---

*Built with ❤️ by the AWS + Anthropic + Grafana workshop team*
