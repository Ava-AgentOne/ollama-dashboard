# Changelog

All notable changes to ollama-dashboard will be documented in this file.

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
