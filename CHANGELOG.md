# Changelog

All notable changes to ollama-dashboard will be documented in this file.

## [v2.2] - 2026-02-21

### Changed
- Increased font sizes across the dashboard for better readability (labels, body text, stat values)
- Network default set to br0 (macvlan) — required when Ollama runs on br0
- Removed port config from Unraid template (not needed on br0)
- Updated install instructions for Unraid 7.x (Private Apps method replaces removed Template Repositories)

### Added
- Networking note in README: host networking cannot reach macvlan containers on Linux

### Fixed
- Dashboard showing empty history when using host networking with Ollama on br0

## [v2.1] - 2026-02-20

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
