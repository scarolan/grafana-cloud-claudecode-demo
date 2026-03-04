# 🚀 Ultimate Dummy-Proof Setup

**For students who want ZERO friction.** I'll do almost everything for you! 🤖

---

## The Only Manual Steps (2 tokens)

**You literally only need to create 2 tokens. That's it.**

### Step 1: Service Account Token

1. **Go to:** https://scdemo.grafana.net/admin/serviceaccounts
2. **Click:** Add service account
3. **Name:** `claude-workshop`
4. **Role:** `Admin`
5. **Add service account** → **Add service account token**
6. **Copy the token** (starts with `glsa_`)

### Step 2: OTLP Token

1. **Go to:** https://scdemo.grafana.net/settings/api-keys
2. **Click:** Add API Key
3. **Name:** `claude-otlp`
4. **Role:** `Editor`
5. **Copy the token** (starts with `glc_`)

---

## The Automated Part

**Clone repo and run the wizard:**

```bash
git clone https://github.com/scarolan/grafana-cloud-claudecode-demo
cd grafana-cloud-claudecode-demo
python setup_wizard.py
```

**The wizard will:**
- ✅ Auto-discover your Grafana endpoints
- ✅ Install all Python packages
- ✅ Generate your `.env` file perfectly
- ✅ Configure Claude MCP server
- ✅ Verify everything works

**Then start Claude and say:**
> "Create me a Claude Code tracing dashboard with beautiful visualizations!"

---

## What Actually Happens

**Behind the scenes, I will:**

1. **Query your Grafana instance** via MCP to discover:
   - Tempo datasource endpoints
   - Prometheus endpoints
   - OTLP gateway URLs
   - Instance IDs and usernames

2. **Generate your `.env` file** with all the right values:
   ```bash
   GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
   GRAFANA_OTLP_INSTANCE_ID=860585
   GRAFANA_CLOUD_TOKEN=glc_your_token_here
   # ... all the other endpoints auto-discovered
   ```

3. **Install everything** you need:
   ```bash
   pip install mcp-grafana opentelemetry-distro opentelemetry-exporter-otlp
   ```

4. **Configure Claude MCP** server:
   ```bash
   claude mcp add -t stdio \
     -e GRAFANA_URL=https://scdemo.grafana.net \
     -e GRAFANA_API_KEY=your_service_account_token \
     -- grafana mcp-grafana --transport stdio
   ```

5. **Verify everything** works and give you the dashboard URL

---

## What You Get

**Instead of complex setup instructions, students just:**

1. Get 2 tokens (guided step-by-step)
2. Run one Python script
3. Start Claude and ask for a dashboard

**The script handles:**
- ❌ No more "find your OTLP endpoint" confusion
- ❌ No more "what's my instance ID?" guessing
- ❌ No more manual .env file editing
- ❌ No more package installation errors
- ❌ No more MCP server configuration

**Total manual effort:** ~2 minutes to get tokens
**Everything else:** Automated by AI 🤖

---

## For Instructors

**This makes demos incredibly smooth:**

1. **"Who wants to see real-time tracing?"** → Students raise hands
2. **"Go get 2 tokens, run the wizard"** → 2 minutes later they're ready
3. **"Now ask Claude to build your dashboard"** → Students watch magic happen
4. **"Use Claude Code and watch your traces"** → Real-time observability!

**No more:**
- Debug setup issues during workshop
- Students struggling with credential configuration
- Half the class missing because their .env is wrong
- Technical friction killing the "wow" moment

**Just pure AI-powered observability magic!** ✨

---

*Total time: 3 minutes to working traces + live dashboard creation*