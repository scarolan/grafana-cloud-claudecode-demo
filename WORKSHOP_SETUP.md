# 🚀 Claude Code Tracing - 5-Minute Setup Guide

**Want to see your Claude Code usage as real-time traces?** Follow these super simple steps!

---

## Step 1: Install Python (2 minutes)

1. **Go to:** https://www.python.org/downloads/
2. **Click** the big **"Download Python 3.12"** button
3. **Run the installer**
4. **CHECK "Add Python to PATH"** (bottom of installer - this is critical!)
5. **Click "Install Now"**
6. **Close and reopen** your terminal
7. **Test it works:** Type `python --version` and press Enter

**Should see:** `Python 3.12.x`

---

## Step 2: Get Your Grafana Cloud Credentials (2 minutes)

**You'll need your own free Grafana Cloud account.** Sign up at https://grafana.com if you haven't already.

### Find your OTLP endpoint and instance ID:

1. **Go to:** https://grafana.com → **My Account**
2. **Find your stack** and click **Configure** under the OpenTelemetry section
3. **Copy the OTLP endpoint URL** (looks like `https://otlp-gateway-prod-us-east-0.grafana.net/otlp`)
4. **Copy your Instance ID** (a number like `860585`, shown on the same page)

### Generate a Cloud API token:

1. **On the same OpenTelemetry page**, click **Generate now** to create an API token
2. **Copy the token** (starts with `glc_`)

**You now have all three values:**
```
GRAFANA_CLOUD_TOKEN=glc_your_token_here
GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_OTLP_INSTANCE_ID=your_instance_id
```

---

## Step 3: Create Your .env File (1 minute)

1. **Open the workshop folder** in VS Code (already cloned for you)
2. **Find the file** `.env.example`
3. **Copy it** and rename the copy to `.env`
4. **Open .env** in VS Code
5. **Replace the example values** with the real ones from Step 2

**Your .env should look like:**
```bash
GRAFANA_CLOUD_TOKEN=glc_your_real_token_here
GRAFANA_OTLP_GATEWAY_URL=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
GRAFANA_OTLP_INSTANCE_ID=your_real_instance_id
TRACE_MODE=direct
```

**Save the file** (Ctrl+S)

---

## Step 4: Install Tracing Packages (1 minute)

1. **Open a terminal** in your workshop folder
   - In VS Code: **Terminal** → **New Terminal**
   - Or open **cmd** and navigate to the folder

2. **Copy and paste this command:**
   ```powershell
   pip install opentelemetry-distro opentelemetry-exporter-otlp
   ```

3. **Press Enter** and wait (downloads ~50MB)

**Should see:** `Successfully installed opentelemetry-...`

---

## Step 5: Verify Everything Works (30 seconds)

**Run the setup checker:**

```powershell
bash check-tracing-setup.sh
```

**You should see:**
```
🎉 Tracing addon fully configured and ready!
   Start a Claude Code session to generate traces.
```

**If you see problems:** Ask your instructor for help!

---

## Step 6: Import the Dashboard (30 seconds)

1. **Open your Grafana Cloud** (`https://YOUR-STACK.grafana.net`)
2. **Go to:** Dashboards → New → Import
3. **Click:** Upload dashboard JSON file
4. **Select:** `dashboards/claude-code-traces.json`
5. **Click:** Import

**Done!** Your dashboard is ready.

---

## 🎯 Start Tracing!

1. **Start Claude Code** in this workshop folder
2. **Use Claude Code normally** - read files, write code, whatever!
3. **Open your dashboard** - watch traces appear in real-time!

**Every tool call becomes a trace span. It's magic!** ✨

---

## 🔧 Troubleshooting

### **"python: command not found"**
- **Close and reopen** PowerShell/Terminal
- **Restart VS Code** if using integrated terminal
- **Try:** `py --version` instead of `python --version`

### **"pip install failed"**
- **Try:** `py -m pip install opentelemetry-distro opentelemetry-exporter-otlp`
- **Or ask instructor** - they have backup solutions

### **"No traces appearing"**
- **Check .env file** - are the credentials correct?
- **Run:** `bash check-tracing-setup.sh`
- **Restart Claude Code** after installing packages

### **Still stuck?**
- **🙋‍♀️ Ask your instructor!** That's what they're here for.
- **Your workshop works fine without tracing** - this is just bonus content

---

**Total time: ~5 minutes → Real-time AI workflow observability! 🚀**