# 🚀 Claude Code Tracing - MCP Edition Setup

**The new hotness!** Instead of importing dashboard JSON files, you'll ask Claude to **build your dashboard live**. Much cooler! 🤖✨

---

## Step 1: Install Python (2 minutes)

### **Windows (Workshop Workstations):**

1. **Open PowerShell** (search "PowerShell" in Start menu)
2. **Copy and paste this command:**
   ```powershell
   winget install Python.Python.3.12
   ```
3. **Press Enter** and wait for installation
4. **Close and reopen** PowerShell
5. **Test it works:** Type `python --version` and press Enter

**Should see:** `Python 3.12.x`

---

## Step 2: Clone the Workshop Repository (30 seconds)

```bash
git clone https://github.com/scarolan/grafana-cloud-claudecode-demo
cd grafana-cloud-claudecode-demo
```

---

## Step 3: Configure Grafana Service Account (2 minutes)

**You need admin powers in your Grafana Cloud stack:**

1. **Open your Grafana Cloud** (instructor provides URL)
2. **Go to:** Administration → Service Accounts → **Add service account**
3. **Name:** `claude-code-workshop`
4. **Role:** `Admin` (or at least `Editor`)
5. **Click:** Add service account
6. **Click:** Add service account token
7. **Copy the token** (starts with `glsa_...`)

**Save this token** - you'll need it in the next step!

---

## Step 4: Install MCP Grafana & Add Server (2 minutes)

```bash
# Install the Grafana MCP server
pip install mcp-grafana

# Add it to Claude Code (replace with your actual URL and token)
claude mcp add -t stdio \
  -e GRAFANA_URL=https://your-stack.grafana.net \
  -e GRAFANA_API_KEY=glsa_your_actual_token_here \
  -- grafana mcp-grafana --transport stdio
```

**Example:**
```bash
claude mcp add -t stdio \
  -e GRAFANA_URL=https://scdemo.grafana.net \
  -e GRAFANA_API_KEY=glsa_your_actual_token_here_replace_this \
  -- grafana mcp-grafana --transport stdio
```

---

## Step 5: Install OpenTelemetry Packages (1 minute)

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
```

---

## Step 6: Configure Your .env (1 minute)

**Ask your instructor for the credentials, then:**

1. **Copy `.env.example` to `.env`**
2. **Edit `.env`** with real values:

```bash
GRAFANA_CLOUD_TOKEN=glc_your_instructor_provided_token
GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_OTLP_INSTANCE_ID=your_instructor_provided_id
TRACE_MODE=direct
```

---

## Step 7: The Magic Part! ✨

**Start Claude Code in this directory:**

```bash
claude
```

**Then say something like:**
> "Create me a Claude Code tracing dashboard! I want to see tool usage patterns, performance metrics, and be able to drill into traces. Make it look professional with a nice header."

**Watch Claude:**
- Query your datasources
- Create dashboard panels with proper TraceQL queries
- Add beautiful visualizations
- Give you the dashboard URL when done

**That's it!** No JSON imports, no manual configuration. Claude builds your observability stack live! 🚀

---

## Step 8: Start Tracing & Enjoy!

1. **Keep using Claude Code** in this repo directory
2. **Every tool call becomes a trace span**
3. **Open your new dashboard** - see real-time traces!
4. **Ask Claude to enhance the dashboard** as you think of new ideas

---

## 🔥 Pro Tips

**Dashboard iterations:**
> "Add a panel showing file access patterns"
> "Create an alert for slow tool calls"
> "Show me command descriptions in a word cloud"

**Explore your traces:**
> "What are the slowest operations in my traces?"
> "Show me all the files I've been working on"
> "Are there any error patterns I should know about?"

**The beauty:** Claude can analyze the traces AND build the dashboards to visualize them!

---

## 🔧 Troubleshooting

### **"MCP server connection failed"**
- **Check your service account token** - it needs `Admin` or `Editor` permissions
- **Verify the Grafana URL** - should be `https://your-stack.grafana.net`

### **"No traces appearing"**
- **Run:** `bash check-tracing-setup.sh`
- **Check `.env`** file has correct OTLP credentials
- **Restart Claude Code** after installing packages

### **"Dashboard looks empty"**
- **Use Claude Code for a few minutes** to generate traces
- **Refresh the dashboard** - traces appear with ~30 second delay
- **Ask Claude:** "Why isn't my dashboard showing data?"

---

**Total time: ~6 minutes → AI-powered dashboards + real-time tracing! 🤯**

**The difference:** Instead of importing someone else's dashboard, you **co-create** it with Claude. Way more engaging!