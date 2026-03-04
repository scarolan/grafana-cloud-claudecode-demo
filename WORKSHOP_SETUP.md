# Workshop Setup

Get Claude Code tracing working in about 5 minutes.

---

## Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download and run the installer
3. **Check "Add Python to PATH"** at the bottom of the installer
4. Click "Install Now"
5. Open a new terminal and verify: `python --version`

---

## Step 2: Create a Grafana Cloud Account

1. Sign up for free at https://grafana.com
2. Once your stack is created, note your stack URL: `https://YOUR-STACK.grafana.net`

---

## Step 3: Get Your OTLP Credentials

These let the tracing hook send data to your Grafana Cloud instance.

1. Go to https://grafana.com and click **My Account**
2. Find your stack and click **Configure** under the **OpenTelemetry** section
3. Copy the **OTLP endpoint URL** (looks like `https://otlp-gateway-prod-us-east-0.grafana.net/otlp`)
4. Copy your **Instance ID** (a number like `860585`)
5. Click **Generate now** to create an API token
6. Copy the **token** (starts with `glc_`)

---

## Step 4: Configure .env

1. Copy `.env.example` to `.env`
2. Fill in the three values from Step 3:

```
GRAFANA_CLOUD_TOKEN=glc_your_token
GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_OTLP_INSTANCE_ID=your_instance_id
TRACE_MODE=direct
```

---

## Step 5: Install Packages

```
pip install opentelemetry-distro opentelemetry-exporter-otlp mcp-grafana
```

---

## Step 6: Create a Grafana Service Account Token

This lets Claude talk to your Grafana instance to build dashboards.

1. Go to `https://YOUR-STACK.grafana.net/admin/serviceaccounts`
2. Click **Add service account**
3. Name: `claude-workshop`, Role: **Admin**
4. Click **Add service account**, then **Add service account token**
5. Copy the token (starts with `glsa_`)

---

## Step 7: Add the Grafana MCP Server to Claude

Run this in **cmd** (not PowerShell — PowerShell mangles the `--` separator):

```
claude mcp add -t stdio -e GRAFANA_URL=https://YOUR-STACK.grafana.net -e GRAFANA_API_KEY=glsa_YOUR_TOKEN -- grafana mcp-grafana --transport stdio
```

---

## Step 8: Start Claude and Build Your Dashboard

```
claude
```

Then ask:

> "Create me a Claude Code tracing dashboard with tool usage patterns, performance metrics, and trace exploration."

Claude will query your datasources and build the dashboard live.

---

## Verify Tracing Works

1. Use Claude Code normally (read files, edit code, run commands)
2. Open your dashboard at `https://YOUR-STACK.grafana.net`
3. Traces appear within ~30 seconds

You can also run the setup checker:

```
"C:\Program Files\Git\bin\bash.exe" check-tracing-setup.sh
```

---

## Troubleshooting

**"python: command not found"** — Close and reopen your terminal. Try `py --version` instead.

**"pip install failed"** — Try `py -m pip install ...` instead.

**"MCP server connection failed"** — Check your service account token has Admin permissions. Make sure you used cmd, not PowerShell.

**"No traces appearing"** — Check `.env` has the right credentials. Restart Claude Code after installing packages.
