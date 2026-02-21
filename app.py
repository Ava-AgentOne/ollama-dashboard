#!/usr/bin/env python3
"""Ollama Intel iGPU Monitoring Dashboard v2.2 — Backend"""

from flask import Flask, jsonify, render_template, request as flask_request
import requests
import json
import os
import time
import threading
import re
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)

# ── Configuration ────────────────────────────────────────────────
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_CONTAINER = os.environ.get('OLLAMA_CONTAINER', 'ollama-intel')
DATA_DIR = os.environ.get('DATA_DIR', '/data')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))

history_lock = threading.Lock()
current_status = {"status": "starting", "running": {"models": []}, "models": {"models": []}}
start_time = datetime.now().isoformat()

# Track seen log entries to prevent duplicates
seen_entries = set()
MAX_SEEN = 5000

# ── History persistence ──────────────────────────────────────────
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                for key in ["requests", "benchmarks", "events"]:
                    if key not in data:
                        data[key] = []
                return data
    except:
        pass
    return {"requests": [], "benchmarks": [], "events": []}

def save_history(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ── Docker log parsing ───────────────────────────────────────────
last_log_ts = time.time()

def entry_hash(entry):
    """Create unique hash for a log entry to prevent duplicates"""
    key = f"{entry.get('time','')}|{entry.get('path','')}|{entry.get('client_ip','')}|{entry.get('duration','')}"
    return hashlib.md5(key.encode()).hexdigest()[:16]

def parse_docker_logs():
    global last_log_ts, seen_entries
    try:
        import docker
        client = docker.from_env()
        container = client.containers.get(OLLAMA_CONTAINER)
        since = int(last_log_ts - 2)
        last_log_ts = time.time()
        logs = container.logs(since=since, timestamps=False).decode('utf-8', errors='replace')

        lines = logs.split('\n')
        found = []

        # First pass: collect token info from debug lines
        token_info = {}
        last_prompt_tokens = 0
        last_eval_tokens = 0

        for i, line in enumerate(lines):
            eval_match = re.search(r'"eval_count"\s*:\s*(\d+)', line)
            if eval_match:
                last_eval_tokens = int(eval_match.group(1))
            prompt_match = re.search(r'"prompt_eval_count"\s*:\s*(\d+)', line)
            if prompt_match:
                last_prompt_tokens = int(prompt_match.group(1))
            eval_match2 = re.search(r'eval_count\s+(\d+)', line)
            if eval_match2 and 'prompt' not in line.lower():
                last_eval_tokens = int(eval_match2.group(1))
            prompt_match2 = re.search(r'prompt_eval_count\s+(\d+)', line)
            if prompt_match2:
                last_prompt_tokens = int(prompt_match2.group(1))
            total_match = re.search(r'total_duration\s+(\d+)', line)
            if total_match:
                token_info[i] = {
                    "eval_tokens": last_eval_tokens,
                    "prompt_tokens": last_prompt_tokens,
                    "total_tokens": last_eval_tokens + last_prompt_tokens
                }

        # Second pass: parse GIN request lines
        for i, line in enumerate(lines):
            gin = re.search(
                r'\[GIN\]\s+(\d{4}/\d{2}/\d{2}\s+-\s+\d{2}:\d{2}:\d{2})\s+\|\s+(\d+)\s+\|\s+(.+?)\s+\|\s+(.+?)\s+\|\s+(\w+)\s+"(.+?)"',
                line
            )
            if gin:
                ts, status, duration, client_ip, method, path = gin.groups()
                if path.strip() in ['/', '/api/tags', '/api/ps', '/api/version', '/api/show']:
                    continue
                dur_str = duration.strip()
                dur_ms = 0
                try:
                    if 'ms' in dur_str:
                        dur_ms = float(dur_str.replace('ms', '').replace('\u00b5s', '').strip())
                    elif '\u00b5s' in dur_str:
                        dur_ms = float(dur_str.replace('\u00b5s', '').strip()) / 1000
                    elif 's' in dur_str:
                        parts = dur_str.replace('s', '').strip()
                        if 'm' in parts:
                            mp = parts.split('m')
                            dur_ms = (float(mp[0]) * 60 + float(mp[1])) * 1000
                        else:
                            dur_ms = float(parts) * 1000
                except:
                    dur_ms = 0

                try:
                    dt = datetime.strptime(ts.strip(), "%Y/%m/%d - %H:%M:%S")
                    iso_time = dt.isoformat()
                except:
                    iso_time = ts.strip()

                # Find closest token info (look backwards from this line)
                tokens = 0
                prompt_tokens = 0
                for ti_pos in sorted(token_info.keys(), reverse=True):
                    if ti_pos < i:
                        tokens = token_info[ti_pos].get("eval_tokens", 0)
                        prompt_tokens = token_info[ti_pos].get("prompt_tokens", 0)
                        del token_info[ti_pos]
                        break

                entry = {
                    "time": iso_time,
                    "time_display": ts.strip(),
                    "status": int(status.strip()),
                    "duration": dur_str,
                    "duration_ms": round(dur_ms, 1),
                    "client_ip": client_ip.strip(),
                    "method": method.strip(),
                    "path": path.strip(),
                    "tokens": tokens,
                    "prompt_tokens": prompt_tokens,
                    "total_tokens": tokens + prompt_tokens
                }

                # Dedup check
                h = entry_hash(entry)
                if h not in seen_entries:
                    seen_entries.add(h)
                    found.append(entry)
                    if len(seen_entries) > MAX_SEEN:
                        seen_entries = set(list(seen_entries)[-3000:])

        return found
    except Exception as e:
        return []

# ── Background poller ────────────────────────────────────────────
last_running = set()

def poll_loop():
    global current_status, last_running
    while True:
        try:
            ps_resp = requests.get(f"{OLLAMA_URL}/api/ps", timeout=5)
            tags_resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            ps_data = ps_resp.json() if ps_resp.ok else {"models": []}
            tags_data = tags_resp.json() if tags_resp.ok else {"models": []}

            current_status = {
                "status": "online",
                "running": ps_data,
                "models": tags_data,
                "polled_at": datetime.now().isoformat()
            }

            current_running = {m.get("name", "unknown") for m in ps_data.get("models", [])}
            loaded = current_running - last_running
            unloaded = last_running - current_running

            with history_lock:
                history = load_history()
                now = datetime.now().isoformat()
                changed = False

                for model in loaded:
                    history["events"].append({"time": now, "type": "load", "model": model})
                    changed = True
                for model in unloaded:
                    history["events"].append({"time": now, "type": "unload", "model": model})
                    changed = True

                new_requests = parse_docker_logs()
                if new_requests:
                    history["requests"].extend(new_requests)
                    changed = True

                if changed:
                    save_history(history)

            last_running = current_running

        except Exception as e:
            current_status = {
                "status": "offline",
                "running": {"models": []},
                "models": {"models": []},
                "error": str(e),
                "polled_at": datetime.now().isoformat()
            }

        time.sleep(POLL_INTERVAL)

# ── API Endpoints ────────────────────────────────────────────────
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    data = dict(current_status)
    data["dashboard_start"] = start_time
    data["ollama_url"] = OLLAMA_URL
    return jsonify(data)

@app.route('/api/history')
def api_history():
    with history_lock:
        return jsonify(load_history())

@app.route('/api/benchmark', methods=['POST'])
def api_benchmark():
    body = flask_request.json or {}
    model = body.get('model', '')
    prompt = body.get('prompt', 'Explain quantum computing in exactly three sentences.')

    if not model:
        return jsonify({"error": "No model specified"}), 400

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 128}
        }, timeout=300)

        if not resp.ok:
            return jsonify({"error": f"Ollama returned {resp.status_code}"}), 502

        data = resp.json()
        eval_dur = data.get("eval_duration", 1)
        prompt_dur = data.get("prompt_eval_duration", 1)

        result = {
            "model": model,
            "time": datetime.now().isoformat(),
            "prompt": prompt,
            "total_duration_ms": round(data.get("total_duration", 0) / 1e6, 1),
            "load_duration_ms": round(data.get("load_duration", 0) / 1e6, 1),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "prompt_eval_rate": round(data.get("prompt_eval_count", 0) / max(prompt_dur / 1e9, 0.001), 2),
            "eval_count": data.get("eval_count", 0),
            "eval_duration_ms": round(eval_dur / 1e6, 1),
            "tokens_per_sec": round(data.get("eval_count", 0) / max(eval_dur / 1e9, 0.001), 2),
            "response_preview": data.get("response", "")[:200]
        }

        with history_lock:
            history = load_history()
            history["benchmarks"].append(result)
            save_history(history)

        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({"error": "Benchmark timed out (300s)"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trim', methods=['POST'])
def api_trim():
    body = flask_request.json or {}
    mode = body.get('mode', 'count')

    with history_lock:
        history = load_history()

        if mode == 'count':
            keep = body.get('keep', 500)
            for key in ["requests", "benchmarks", "events"]:
                if key in history and len(history[key]) > keep:
                    history[key] = history[key][-keep:]
            save_history(history)
            return jsonify({"status": "trimmed", "mode": "count", "kept": keep})

        elif mode == 'time':
            months = body.get('months', 6)
            cutoff = (datetime.now() - timedelta(days=months * 30)).isoformat()
            for key in ["requests", "benchmarks", "events"]:
                if key in history:
                    history[key] = [
                        entry for entry in history[key]
                        if entry.get("time", "") >= cutoff
                    ]
            save_history(history)
            return jsonify({"status": "trimmed", "mode": "time", "months": months})

    return jsonify({"error": "Invalid mode"}), 400

@app.route('/api/clear', methods=['POST'])
def api_clear():
    with history_lock:
        save_history({"requests": [], "benchmarks": [], "events": []})
    return jsonify({"status": "cleared"})

@app.route('/api/history/export')
def api_export():
    with history_lock:
        history = load_history()
    return jsonify(history), 200, {
        'Content-Disposition': f'attachment; filename=ollama-history-{datetime.now().strftime("%Y%m%d")}.json'
    }

@app.route('/api/history/stats')
def api_history_stats():
    with history_lock:
        history = load_history()
        file_size = 0
        try:
            file_size = os.path.getsize(HISTORY_FILE)
        except:
            pass
        total_gen_tokens = sum(r.get("tokens", 0) for r in history.get("requests", []))
        total_prompt_tokens = sum(r.get("prompt_tokens", 0) for r in history.get("requests", []))
        total_bench_tokens = sum(b.get("eval_count", 0) for b in history.get("benchmarks", []))
        total_all = total_gen_tokens + total_prompt_tokens + total_bench_tokens
        return jsonify({
            "requests": len(history.get("requests", [])),
            "benchmarks": len(history.get("benchmarks", [])),
            "events": len(history.get("events", [])),
            "file_size_bytes": file_size,
            "file_size": _fmt_bytes(file_size),
            "total_tokens": total_all,
            "total_gen_tokens": total_gen_tokens + total_bench_tokens,
            "total_prompt_tokens": total_prompt_tokens
        })

def _fmt_bytes(b):
    for u in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

# ── Update Checker ───────────────────────────────────────────────
@app.route('/api/updates')
def api_updates():
    results = {"dashboard_packages": [], "base_image": {}, "checked_at": datetime.now().isoformat()}

    try:
        with open('/app/requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('==')
                pkg_name = parts[0]
                current_ver = parts[1] if len(parts) > 1 else 'unknown'
                latest_ver = current_ver
                try:
                    resp = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=10)
                    if resp.ok:
                        latest_ver = resp.json().get("info", {}).get("version", current_ver)
                except:
                    latest_ver = "check failed"
                results["dashboard_packages"].append({
                    "package": pkg_name,
                    "current": current_ver,
                    "latest": latest_ver,
                    "update_available": current_ver != latest_ver and latest_ver != "check failed"
                })
    except:
        pass

    try:
        import docker
        client = docker.from_env()
        try:
            container = client.containers.get(OLLAMA_CONTAINER)
            image = container.image
            current_id = image.short_id
            current_tags = image.tags
            results["base_image"] = {
                "container": OLLAMA_CONTAINER,
                "current_image_id": current_id,
                "current_tags": current_tags,
                "note": "To check for updates, run: docker pull intelanalytics/ipex-llm-inference-cpp-xpu:latest"
            }
        except Exception as e:
            results["base_image"] = {"error": str(e)}
    except:
        results["base_image"] = {"error": "Docker not accessible"}

    results["rebuild_commands"] = {
        "dashboard": [
            "cd /mnt/user/appdata/ollama-dashboard-build",
            "docker pull python:3.11-slim",
            "docker build --no-cache -t ollama-dashboard .",
            "# Then restart from Unraid Docker tab"
        ],
        "ollama_intel": [
            "cd /mnt/user/appdata/ollama-build",
            "docker pull intelanalytics/ipex-llm-inference-cpp-xpu:latest",
            "docker build --no-cache -t ollama-intel .",
            "# Then restart from Unraid Docker tab"
        ]
    }

    return jsonify(results)

# ── Start ────────────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        history = load_history()
        for r in history.get("requests", [])[-2000:]:
            seen_entries.add(entry_hash(r))
        print(f"[DASHBOARD] Loaded {len(seen_entries)} existing entry hashes for dedup")
    except:
        pass
    threading.Thread(target=poll_loop, daemon=True).start()
    print(f"[DASHBOARD] Ollama Monitor v2.2 starting on port 8088")
    print(f"[DASHBOARD] Monitoring: {OLLAMA_URL}")
    print(f"[DASHBOARD] Container: {OLLAMA_CONTAINER}")
    print(f"[DASHBOARD] History: {HISTORY_FILE}")
    app.run(host='0.0.0.0', port=8088, debug=False)
