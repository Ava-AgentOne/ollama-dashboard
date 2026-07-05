# Changelog

All notable changes to ollama-dashboard will be documented in this file.

## [v1.2] - 2026-07-05

### Changed
- **Production WSGI server** — both the dashboard (8088) and the API proxy (11434) now run on waitress instead of the Flask development server; thread pools tunable via `PROXY_THREADS` (default 16) and `DASHBOARD_THREADS` (default 8)
- Dependency bumps: flask 3.1.0 → 3.1.3, requests 2.32.3 → 2.34.2; base image python:3.11-slim → python:3.13-slim

### Fixed
- Login uses constant-time password comparison and delays failed attempts by 0.75s (brute-force hardening)
- `poll_interval` is clamped to 1–300s at point of use — a saved value of 0 previously turned the poll loop into a busy loop hammering Ollama
- `history.json` and `settings.json` writes are now atomic (temp file + rename), so a crash mid-write can no longer corrupt them
- Update checker note pointed at the upstream `intelanalytics` image instead of `ghcr.io/ava-agentone/ollama-intel`

### Added
- Docker `HEALTHCHECK` on the dashboard port (shows healthy/unhealthy in the Unraid Docker tab)

## [v1.1] - 2026-04-15

*(Retroactive entry — v1.1 was tagged before its changes were recorded in the changelog.)*

### Added (community contribution by @icordos)
- **Track all APIs** — token/latency tracking extended beyond Ollama-native routes to all OpenAI-compatible (`/v1/chat/completions`) and Anthropic-compatible (`/v1/messages`) endpoints, including SSE streaming and `stream_options.include_usage` injection
- **NVIDIA NeMo Guardrails integration** — optional pre-check of generation requests via `NEMO_GUARDRAILS_URL` with fail-closed behavior, rail toggles, base64 payload sanitization, and 403 `blocked_by_guardrails` responses logged to history
- **Opt-in prompt logging** — full input/output text captured to append-only `prompts.jsonl` (kept out of `history.json`), viewable in the Request History popup
- Configurable proxy timeout via `PROXY_TIMEOUT`; tokens/sec fallback when duration fields are absent

### Fixed
- gpt-oss and `/v1/messages` streams not tracking tokens; health-check noise no longer logged to history

## [v1.0] - 2026-02-21

### Added
- **Password protection** — optional login page with themed UI
  - Set `DASHBOARD_PASSWORD` env var to enable
  - Session cookie persists for 30 days
  - All dashboard and API routes protected when enabled
  - Proxy port (11434) remains open for Ollama clients
  - Logout button appears in nav when auth is active
- **API documentation page** — new "API" nav tab documenting all endpoints
  - Dashboard API endpoints with methods, paths, and body examples
  - Proxy endpoint documentation
  - Auth endpoint docs (shown only when auth is enabled)
- **Login page** — styled to match dashboard theme with animated logo
- **Snapshot card** — 📸 button generates branded PNG stats card (Canvas API, no dependencies)
  - 8-stat grid: requests, tokens, avg/peak tok/s, top model, models, clients, events
  - Downloads as `ollama-snapshot-YYYY-MM-DD.png`

### Changed
- Version bump to v1.0 — production ready
- Settings API returns `auth_enabled` flag for UI state
- Unraid template includes `DASHBOARD_PASSWORD` and `SECRET_KEY` config
- All API routes return 401 JSON when unauthenticated
- Trim/export/clear controls moved from dashboard footer into Settings → Data Management

### Fixed
- **Chart flickering** — charts only re-render when history data actually changes (hash comparison)
- **Settings save error** — fixed wrong `request` object (`request` → `flask_request`)

## [v0.9] - 2026-02-21

### Added
- **PWA support** — installable as a standalone app on mobile and desktop
  - Web app manifest with icons (192px, 512px)
  - Service worker with network-first caching for offline shell
  - Apple touch icon and iOS standalone mode
  - "Add to Home Screen" support on Android and iOS
- **Collapsible panels** — click any panel header to collapse/expand (persists per session)
- **Responsive mobile layout** at 3 breakpoints:
  - **≤900px** (tablet): single column grids, wrapped header
  - **≤600px** (phone): compact stats, hidden Duration/Quant columns, stacked settings, smaller fonts
  - **≤400px** (small phone): tighter spacing, single-column popups
- **Touch-friendly popup** — full-width on mobile, single-column grid
- **Hidden columns** — Duration and Quant columns auto-hide on mobile (full details in popup)

### Changed
- Viewport meta tag updated with `viewport-fit=cover` for notched phones
- Chart toolbar wraps cleanly on narrow screens
- Controls bar stacks vertically on mobile
- Settings rows stack vertically on mobile for easier input
- Filter buttons and nav tabs compact on small screens

## [v0.8] - 2026-02-21

### Added
- **Settings page** — new nav tab with persistent server-side settings
  - **Client mapping editor** — add/remove/edit IP-to-name mappings with emoji icons from the UI
  - **Poll interval control** — adjust status polling frequency (1-60 seconds)
  - **Auto-trim retention** — configure how long to keep history data
  - **Theme sync** — optionally save theme/mode to server (persists across browsers)
- **Event icons** — 🟢 load, 🔴 unload, ⚠️ warning, ❌ error in model events
- **Settings API** — `GET/POST /api/settings` for persistent configuration
- **Settings file** — `settings.json` persisted to `/data` volume

### Changed
- Client map now loaded from saved settings (falls back to `CLIENT_MAP` env var)
- Backend poll loop uses saved poll interval instead of fixed env var
- Frontend poll interval respects saved settings
- Events display includes icon column and detail field

## [v0.7] - 2026-02-21

### Added
- **Multi-mode chart system** with 5 views:
  - **tok/s** — generation speed over time (line chart with tooltips)
  - **Total Tokens** — tokens per request over time
  - **In vs Out** — prompt vs generated tokens overlaid
  - **Daily Usage** — stacked bar chart of daily token consumption
  - **By Model** — horizontal bar chart comparing avg/peak tok/s per model
- **Chart toggle buttons** to switch between views
- **Per-client filter dropdown** — filter chart data by specific client
- **Rich hover tooltips** — shows time, client name, model on hover
- **Theme-aware charts** — colors update on theme/mode switch

### Changed
- Replaced custom canvas drawing with Chart.js for all analytics
- Chart height increased to 240px for better readability
- Panel renamed from "Generation Speed Over Time" to "Analytics"

## [v0.6] - 2026-02-21

### Added
- **Popup info card** — click any request row to see full details (endpoint, method, prompt speed, done reason, source)
- **Sortable columns** — click table headers to sort by time, duration, model, tokens, tok/s, client
- **Pagination** — request history loads 50 rows at a time with "Load more" button
- **Client emoji mapping** — known IPs show friendly names (🌐 Open WebUI, 📊 Dashboard, 🖥️ Server, 🤖 default)
- **Active Clients card** — shows unique client count with emoji names (replaced Installed Models card)
- **Avg tok/s card** — real average from proxy data with peak speed in sub-text (replaced Token Speed card)
- **Proxy status dot** — green/red indicator in header next to full proxy IP:port
- **Escape key** closes popup overlay
- **New app icon** — updated container icon

### Changed
- Header uptime now shows Ollama server uptime (removed dashboard uptime clock)
- Proxy header shows full IP:port instead of just port number
- Removed Endpoint column from request history table (available in popup)
- Table now shows 7 columns: Time, Duration, Model, In, Out, tok/s, Client
- Installed Models count moved to badge on Available Models panel header

### Removed
- Dashboard uptime counter (duplicate of Ollama uptime)
- Endpoint column from main table (moved to popup details)
- Token Speed card (replaced by Avg tok/s with real data)
- Installed Models card (count in panel badge)

## [v0.5] - 2026-02-21

### Added
- **In/Out token columns** in Request History (prompt tokens + generated tokens per request)
- **tok/s column** in Request History showing generation speed per request
- **Generation Speed chart** — canvas line chart showing tok/s over time with average line
- **Filtered token totals** — Total Tokens card now updates based on time period filter (in + out)

### Changed
- Active Model sub-text no longer shows VRAM (already shown in GPU Memory card)
- Duration display uses whole seconds when ≥1s (no decimals)
- Total Tokens card shows "X in + Y out" breakdown

### Removed
- Removed redundant VRAM display from Active Model subtitle

## [v0.4] - 2026-02-21

### Added
- **Ollama API Proxy** on port 11434 — transparent proxy that captures token stats from every request
  - Clients (Open WebUI, agents, etc.) point to dashboard IP:11434 instead of Ollama directly
  - Full token tracking: eval_count, prompt_eval_count, tokens/sec for all proxied requests
  - Supports both streaming and non-streaming responses
  - Auto-detects own IP to avoid duplicate entries with GIN log parsing
- Request history now shows **Model** and **Tokens** columns
- ⬡ indicator in Client column for proxied requests
- Proxy port displayed in dashboard header
- Total Tokens stat card now includes tokens from proxied requests + benchmarks
- Proxy/direct request count breakdown in history stats

### Changed
- "Bench Tokens" card renamed back to "Total Tokens" (proxy enables full token tracking again)
- GIN log parser filters out proxy-originated requests to avoid duplicates

### Removed
- **Status column** removed from Request History table

### Fixed
- Streaming proxy: raw byte passthrough instead of iter_lines() which broke chunked responses
- Proxy request context: captured Flask request vars before generator to prevent `RuntimeError: Working outside of request context`

## [v0.3] - 2026-02-21

### Changed
- **Metrics source: API-first instead of log parsing** — all model info (name, family, parameter size, quantization, VRAM) now comes from Ollama `/api/ps` and `/api/version` endpoints
- Request history "Tokens" column replaced with "Model" column (token counts no longer available in Ollama 0.9.x logs)
- "Total Tokens" stat card renamed to "Bench Tokens" (only benchmark tokens are trackable via API)
- Update checker rebuild commands updated for GHCR workflow

### Added
- Ollama version displayed in header (from `/api/version`)
- Active model details: parameter size, quantization level, model family shown under Active Model card
- Model details (size, VRAM, digest, family, quantization) fetched from `/api/ps` every poll cycle

### Removed
- Log-based token parsing (`eval_count`, `prompt_eval_count`) — removed because Ollama 0.9.x no longer outputs these in logs
- Per-request token tracking from request history (not available without log stats)

## [v0.2] - 2026-02-21

### Changed
- Increased font sizes across the dashboard for better readability (labels, body text, stat values)
- Network default set to br0 (macvlan) — required when Ollama runs on br0
- Removed port config from Unraid template (not needed on br0)
- Updated install instructions for Unraid 7.x (Private Apps method replaces removed Template Repositories)

### Added
- Networking note in README: host networking cannot reach macvlan containers on Linux

### Fixed
- Dashboard showing empty history when using host networking with Ollama on br0

## [v0.1] - 2026-02-20

### Initial public release
- Real-time model status monitoring (loaded/unloaded detection)
- Request history with token tracking, parsed from Docker logs
- Built-in benchmarking with detailed metrics
- 6 themes: Terminal, Cyberpunk, Ocean × Dark/Light modes
- Hash-based deduplication for request history
- Auto-polling with configurable interval
- Update checker for base images
- GitHub Actions CI/CD with auto-build to GHCR
- Unraid template with br0 networking
