# Changelog

All notable changes to ollama-dashboard will be documented in this file.

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
