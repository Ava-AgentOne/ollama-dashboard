<div align="center">

<img src="https://raw.githubusercontent.com/Ava-AgentOne/ollama-dashboard/main/icon.png" alt="ollama-dashboard" width="150">

# 📊 ollama-dashboard

**Real-Time Monitoring Dashboard for Ollama**

[![Build & Push to GHCR](https://github.com/Ava-AgentOne/ollama-dashboard/actions/workflows/build.yml/badge.svg)](https://github.com/Ava-AgentOne/ollama-dashboard/actions/workflows/build.yml)
[![GHCR](https://img.shields.io/badge/GHCR-ollama--dashboard-blue?logo=github)](https://github.com/Ava-AgentOne/ollama-dashboard/pkgs/container/ollama-dashboard)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Unraid](https://img.shields.io/badge/Unraid-Compatible-orange?logo=unraid)](https://unraid.net)

*Monitor your Ollama instance in style — track models, requests, tokens, and performance in real time.*

---

</div>

## 📖 What Is This?

**ollama-dashboard** is a lightweight monitoring dashboard for [Ollama](https://ollama.com). It provides real-time visibility into your LLM server: which models are loaded, how fast they're generating, request history with token counts, and built-in benchmarking.

Designed as a companion to [ollama-intel](https://github.com/Ava-AgentOne/ollama-intel) but works with **any Ollama instance**.

### 🎯 Who Is This For?

- **Home lab users** running Ollama who want visibility into their LLM server
- **Unraid users** looking for a clean monitoring solution
- Anyone who wants to **track performance** and **benchmark models** on their hardware

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📡 **Live Status** | Real-time model loading/unloading detection |
| 📜 **Request History** | Tracks all API requests with model name, tokens, and duration |
| 🔀 **API Proxy** | Transparent Ollama proxy (port 11434) — captures token stats from every request |
| ⚡ **Benchmarking** | Run speed tests against any loaded model with detailed metrics |
| 🎨 **6 Visual Themes** | 3 themes (Terminal, Cyberpunk, Ocean) × 2 modes (Dark/Light) |
| 🔄 **Update Checker** | Monitors Python package versions and base image status |
| 📦 **History Export** | Export, trim, and clear request history as JSON |
| 🔒 **Deduplication** | Hash-based log entry deduplication prevents duplicates |
| 📈 **Token Tracking** | Full token tracking via proxy — prompt tokens, generation tokens, tok/s |

## 🎨 Themes

The dashboard ships with **3 themes**, each with dark and light modes:

| Theme | Style | Best For |
|-------|-------|----------|
| 🖥️ **Terminal** | Monospace, green-on-dark hacker aesthetic | Classic terminal lovers |
| 🌆 **Cyberpunk** | Neon gradients, futuristic UI | Sci-fi enthusiasts |
| 🌊 **Ocean** | Calm blues, clean typography | Easy on the eyes |

## 🚀 Quick Start

### Docker Run (Standard Bridge)

```bash
docker run -d \
  --name ollama-dashboard \
  --restart unless-stopped \
  -p 8088:8088 \
  -v /mnt/user/appdata/ollama-dashboard:/data \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e OLLAMA_URL=http://<OLLAMA_IP>:11434 \
  -e OLLAMA_CONTAINER=ollama-intel \
  -e POLL_INTERVAL=5 \
  ghcr.io/ava-agentone/ollama-dashboard:latest
```

> Access the dashboard at `http://<your-server-ip>:8088`

### Unraid (br0 / macvlan)

If you prefer the container to have its own IP on your LAN (common on Unraid):

```bash
docker run -d \
  --name ollama-dashboard \
  --restart unless-stopped \
  --network br0 \
  --ip <YOUR_IP> \
  -v /mnt/user/appdata/ollama-dashboard:/data \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e OLLAMA_URL=http://<OLLAMA_IP>:11434 \
  -e OLLAMA_CONTAINER=ollama-intel \
  -e POLL_INTERVAL=5 \
  ghcr.io/ava-agentone/ollama-dashboard:latest
```

> Replace `<YOUR_IP>` with a free static IP on your LAN, and `<OLLAMA_IP>` with the IP of your Ollama container.

> ⚠️ **Networking Note**: If your Ollama container runs on br0 (macvlan), the dashboard must also be on br0. Linux hosts cannot reach their own macvlan containers — so using `host` networking for the dashboard while Ollama is on br0 will result in "No route to host" errors.

## 🔀 API Proxy (Token Tracking)

The dashboard includes a built-in **Ollama API proxy** on port **11434**. Point your clients to the dashboard instead of Ollama directly, and every request gets full token tracking.

### How It Works

```
Client (Open WebUI, agent, etc.)
    ↓ sends request to
Dashboard Proxy (dashboard-ip:11434)
    ↓ forwards to
Ollama (ollama-ip:11434)
    ↓ response passes back through proxy
Dashboard captures: model, tokens, duration, tok/s
```

### Setup

In your client (Open WebUI, agent, etc.), change the Ollama URL:

| Setting | Before | After |
|---------|--------|-------|
| Ollama URL | `http://<OLLAMA_IP>:11434` | `http://<DASHBOARD_IP>:11434` |

The proxy is 100% transparent — same API, same responses. Clients won't notice any difference.

### What Gets Tracked

| Source | Model | Tokens | Duration | Client IP |
|--------|-------|--------|----------|-----------|
| **Via proxy** | ✅ | ✅ | ✅ | ✅ |
| **Direct to Ollama** | ✅ | ❌ | ✅ | ✅ |

Requests that bypass the proxy still appear in history (from Docker log parsing) but without token counts.

### Unraid Private Apps (Recommended)

Add all Ava-AgentOne containers to your Unraid **Apps** tab:

1. Run in your Unraid terminal:
   ```bash
   mkdir -p /boot/config/plugins/community.applications/private/Ava-AgentOne
   curl -o /boot/config/plugins/community.applications/private/Ava-AgentOne/ollama-dashboard.xml \
     https://raw.githubusercontent.com/Ava-AgentOne/unraid-templates/main/ollama-dashboard.xml
   ```
2. Go to **Apps** tab → **Private Apps** in the left sidebar
3. Click **Install**, configure your settings, and click **Apply**

> 💡 See [unraid-templates](https://github.com/Ava-AgentOne/unraid-templates) for an auto-sync script that keeps templates updated.

### Unraid Template (Manual Install)

Alternatively, paste the template URL directly in Unraid:

1. In Unraid, go to **Docker** → **Add Container** → **Template** dropdown → paste this URL:
   ```
   https://raw.githubusercontent.com/Ava-AgentOne/ollama-dashboard/main/unraid-template.xml
   ```
2. Set your **Ollama URL** and **Ollama Container Name**, click **Apply**
3. Open the dashboard at `http://<YOUR-IP>:8088`

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://OLLAMA_IP:11434` | Full URL to your Ollama API endpoint |
| `OLLAMA_CONTAINER` | `ollama-intel` | Docker container name for log parsing |
| `POLL_INTERVAL` | `5` | How often to poll Ollama status (seconds) |
| `PROXY_TIMEOUT` | `600` | Proxy upstream timeout to Ollama (seconds) |
| `NEMO_GUARDRAILS_URL` | `` | Nemo Guardrails check endpoint; when set, every proxied request is checked before forwarding |
| `NEMO_GUARDRAILS_TIMEOUT` | `15` | Timeout for guardrails pre-check request (seconds) |
| `NEMO_GUARDRAILS_FAIL_CLOSED` | `true` | If `true`, block Ollama calls when guardrails is unavailable/errors |
| `NEMO_GUARDRAILS_MAX_BODY` | `20000` | Max request body chars sent to guardrails for evaluation |
| `NEMO_GUARDRAILS_MODEL` | `gemma4:e4b` | Model used for guardrails classification via `v1/chat/completions` |
| `NEMO_CONFIG_ID` | `default-safe` | Nemo Guardrails config id sent as `guardrails.config_id` |
| `NEMO_RAIL_INPUT` | `true` | Enable Nemo input rails (`guardrails.options.rails.input`) |
| `NEMO_RAIL_OUTPUT` | `false` | Enable Nemo output rails (`guardrails.options.rails.output`) |
| `NEMO_RAIL_DIALOG` | `false` | Enable Nemo dialog rails (`guardrails.options.rails.dialog`) |
| `NEMO_RAIL_RETRIEVAL` | `false` | Enable Nemo retrieval rails (`guardrails.options.rails.retrieval`) |
| `DATA_DIR` | `/data` | Path for persistent history storage |

## 📁 Volume Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `/mnt/user/appdata/ollama-dashboard` | `/data` | rw | Persistent history & benchmark data |
| `/var/run/docker.sock` | `/var/run/docker.sock` | ro | Read Ollama container logs (read-only) |

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11, Flask |
| **Frontend** | Jinja2 Templates, Vanilla JS |
| **Charts** | Chart.js |
| **Log Parsing** | Docker SDK for Python |
| **Container** | ~60MB lightweight image |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard web interface |
| `/api/status` | GET | Current Ollama status (models, running state) |
| `/api/history` | GET | Full request/benchmark/event history |
| `/api/benchmark` | POST | Run a benchmark against a model |
| `/api/history/stats` | GET | History statistics (counts, token totals) |
| `/api/history/export` | GET | Download history as JSON file |
| `/api/trim` | POST | Trim old history entries |
| `/api/clear` | POST | Clear all history |
| `/api/updates` | GET | Check for package and image updates |

## 🔌 Companion Projects

| Project | Description |
|---------|-------------|
| [**ollama-intel**](https://github.com/Ava-AgentOne/ollama-intel) | Ollama with Intel iGPU acceleration via IPEX-LLM |
| [**Open WebUI**](https://github.com/open-webui/open-webui) | ChatGPT-style web interface for Ollama |

## 🔍 Troubleshooting

<details>
<summary><strong>Dashboard shows "Offline"</strong></summary>

- Verify `OLLAMA_URL` points to your running Ollama instance
- Check that both containers are on the same network (br0)
- Test connectivity: `docker exec ollama-dashboard curl http://<OLLAMA_IP>:11434/api/tags`
</details>

<details>
<summary><strong>No request history showing</strong></summary>

- Ensure the Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock:ro`
- Verify `OLLAMA_CONTAINER` matches your Ollama container name exactly
- Enable debug logging on Ollama (`OLLAMA_DEBUG=1`) for detailed request logs
</details>

<details>
<summary><strong>Changes not showing after update</strong></summary>

Hard refresh your browser: **Ctrl+Shift+R** (or **Cmd+Shift+R** on Mac) to bypass the browser cache.
</details>

## 📜 License

[MIT](LICENSE) — Use it, modify it, share it.

---

<div align="center">

**Built for Unraid** · Companion to [ollama-intel](https://github.com/Ava-AgentOne/ollama-intel) · Powered by [Flask](https://flask.palletsprojects.com/)

</div>
