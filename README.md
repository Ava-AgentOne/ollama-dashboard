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
| 📜 **Request History** | Tracks all API requests with token counts, parsed from Docker logs |
| ⚡ **Benchmarking** | Run speed tests against any loaded model with detailed metrics |
| 🎨 **6 Visual Themes** | 3 themes (Terminal, Cyberpunk, Ocean) × 2 modes (Dark/Light) |
| 🔄 **Update Checker** | Monitors Python package versions and base image status |
| 📦 **History Export** | Export, trim, and clear request history as JSON |
| 🔒 **Deduplication** | Hash-based log entry deduplication prevents duplicates |
| 📈 **Token Tracking** | Tracks prompt tokens, generation tokens, and totals |

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

### Unraid App Store (Recommended)

Add all Ava-AgentOne containers to your Unraid Apps tab with one link:

1. In Unraid, go to **Apps** → **Settings** (bottom-left)
2. In **Template Repositories**, add this URL on a new line:
   ```
   https://github.com/Ava-AgentOne/unraid-templates
   ```
3. Click **Apply** — the container will now appear in your **Apps** tab
4. Search for **ollama-dashboard**, click **Install**, configure your settings, and click **Apply**

> 💡 This repo includes templates for all [Ava-AgentOne](https://github.com/Ava-AgentOne) Unraid containers.

### Unraid Template (Manual Install)

Alternatively, add the template directly:

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
