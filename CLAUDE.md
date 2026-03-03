# CLAUDE.md — AWS + Anthropic Workshop Module Guide

You are working in the **AWS + Anthropic Claude Code Workshop** advanced observability module. This repository demonstrates how to instrument AI-powered development workflows with OpenTelemetry distributed tracing, creating enterprise-grade observability for Claude Code sessions.

## Workshop Context

This is **not a generic demo** — it's a specialized workshop module that shows how modern AI tooling integrates with traditional observability platforms. Students learn to apply distributed tracing concepts to AI systems, bridging the gap between AI/ML and DevOps practices.

## Core Philosophy

1. **Educational First** — Every component teaches observability concepts through practical AI tooling
2. **Zero Barriers** — Must work on standard AWS Windows workshop instances without setup friction
3. **Production Patterns** — Demonstrate enterprise-ready approaches that scale to real organizations
4. **AI + Observability** — Show how emerging AI systems fit traditional monitoring/alerting paradigms
5. **Hands-On Learning** — Students see immediate visual feedback for their Claude Code usage

## Repository Purpose

### **Primary Goal: Claude Code Tracing Workshop**

This repository instruments Claude Code sessions with OpenTelemetry, sending distributed traces to Grafana Cloud. Students learn:

- **How AI tools can be observed** using standard observability practices
- **OpenTelemetry implementation** in real-world AI system contexts
- **Grafana Cloud visualization** of complex AI workflow patterns
- **Enterprise architecture patterns** for AI system monitoring
- **Performance optimization** techniques for AI-assisted development

### **Key Components**

- **`trace_hook.py`** — OpenTelemetry instrumentation for Claude Code tool calls
- **`.claude/settings.json`** — Hooks configuration that activates tracing automatically
- **`dashboards/claude-code-traces.json`** — Professional Grafana dashboard for visualization
- **Workshop-friendly setup** — Graceful degradation on minimal Windows environments

## Workshop Workflow

### **Instructor Demonstration Flow**

1. **Context Setting** — Explain why AI systems need observability
2. **Dashboard Import** — Show the tracing visualization platform
3. **Live Claude Code Session** — Generate real traces during actual development work
4. **Pattern Analysis** — Explore tool usage, performance metrics, session correlation
5. **Enterprise Discussion** — How this scales to AI-powered development teams

### **Student Experience Path**

**Immediate Learning (No Setup):**
- Complete workshop materials available and functional
- Professional observability infrastructure in place
- Understand concepts through instructor demonstrations
- See enterprise-grade AI system monitoring

**Enhanced Hands-On (Optional 2-Minute Setup):**
- Install Python + OpenTelemetry packages
- Generate personal traces of their Claude Code usage
- Explore their own development patterns in dashboard
- Experience full distributed tracing workflow

## Technical Architecture

### **AWS Integration**
- Designed for **AWS EC2 Windows** workshop instances
- **AWS-hosted Grafana Cloud** for data storage and visualization
- Compatible with **AWS observability services** (CloudWatch, X-Ray)
- Follows **AWS Well-Architected** monitoring patterns

### **Anthropic Integration**
- Instruments **Claude Code tool calls** with minimal overhead
- **Privacy-safe tracing** — sanitizes paths, redacts secrets
- **Session correlation** across multi-tool workflows
- **Zero impact** on Claude Code performance or functionality

### **Grafana Cloud Integration**
- **Direct OTLP export** to Grafana Cloud gateway
- **Professional dashboard** with branded header and enterprise styling
- **Real-time visualization** of AI workflow patterns
- **Standard observability metrics** (latency, error rates, throughput)

## Scenarios You Can Support

### **Basic Workshop Scenarios**

**"Show me Claude Code tracing"**
- Import the dashboard
- Enable tracing (if Python available)
- Use Claude Code normally
- Demonstrate real-time trace visualization

**"How does this work technically?"**
- Examine `trace_hook.py` implementation
- Explain OpenTelemetry span creation
- Show `.claude/settings.json` hook configuration
- Discuss enterprise architecture patterns

**"What patterns do you see?"**
- Analyze tool usage distribution
- Identify performance bottlenecks
- Correlate session flows
- Demonstrate alerting possibilities

### **Advanced Workshop Extensions**

**"Scale this to a team"**
- Discuss multi-developer dashboards
- Design team-wide observability strategies
- Consider CI/CD integration scenarios
- Explore cost optimization approaches

**"Integrate with existing systems"**
- Show AWS CloudWatch correlation
- Demonstrate alert routing to PagerDuty/Slack
- Connect to existing observability platforms
- Design enterprise deployment architectures

**"Custom instrumentation"**
- Modify span attributes for specific use cases
- Create domain-specific metrics
- Build custom dashboard panels
- Implement advanced trace sampling

## Implementation Guidelines

### **When Working in This Repository**

- **Maintain workshop focus** — This is educational, not a production demo
- **Preserve zero-setup experience** — Core functionality must work without dependencies
- **Test on Windows** — Verify compatibility with workshop environment constraints
- **Think enterprise** — Patterns should scale to real organizational deployment
- **Document learning objectives** — Every change should support pedagogical goals

### **Component Relationships**

```
Workshop Students
       ↓
   Claude Code (with tracing hooks)
       ↓
   OpenTelemetry (trace_hook.py)
       ↓
   Grafana Cloud (AWS-hosted)
       ↓
   Real-time Dashboard Visualization
```

### **Quality Standards**

- **Educational clarity** — Code should teach observability concepts
- **Production readiness** — Architecture should scale to enterprise use
- **Workshop compatibility** — Must work on constrained workshop environments
- **Visual excellence** — Dashboard should impress and engage students
- **Documentation quality** — README should guide both instructors and students

## Success Metrics

### **Student Learning Outcomes**

- **Understand distributed tracing** concepts through practical AI application
- **Experience OpenTelemetry** implementation in real-world context
- **Visualize complex workflows** using professional observability tools
- **Connect AI systems** to traditional DevOps practices
- **Envision enterprise applications** of AI system observability

### **Instructor Experience**

- **Reliable demonstration platform** that works consistently across workshop environments
- **Engaging visual content** that maintains student attention and interest
- **Flexible scenarios** supporting different skill levels and time constraints
- **Professional appearance** that reflects enterprise-grade practices
- **Clear learning progression** from concepts to hands-on to enterprise implications

## Workshop Context Notes

- **This is advanced content** — Assumes students understand basic observability concepts
- **Focus on AI/observability intersection** — Not generic OpenTelemetry training
- **AWS + Anthropic partnership context** — Demonstrates integration between platforms
- **Enterprise audience** — Students are likely senior developers, architects, DevOps engineers
- **Hands-on preferred** — Students learn best through direct experience with tools

**Remember:** You're not building a generic demo. You're creating an educational experience that shows how emerging AI systems integrate with established observability practices. Every component should support this learning objective.