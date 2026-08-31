# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-08-31

### Added
- **Multi-Platform Automated Releases**: Added `.github/workflows/release.yml` with automated builds and packages for:
  - Windows x64 & ARM64 (`.exe`, `.zip`)
  - Linux x64 & ARM64 (`binary`, `.deb`, `.tar.gz`)
  - macOS Universal2 (`binary`, `.zip`, `.tar.gz`)
  - `checksums.txt` SHA-256 integrity verification.
- **Automated Upstream Sync**: Added `.github/workflows/sync-upstream.yml` for scheduled and on-demand synchronization with the upstream repository while preserving repository customizations.
- **Debian (.deb) Packaging**: Native `.deb` packages for easy system-wide installation on Debian/Ubuntu/Mint distributions.

### Changed
- **Full English Localization (i18n)**:
  - Translated all interactive console menus, status messages, confirmation prompts, error diagnostics, and docstrings from Russian to clear English.
  - Rewrote `README.md` completely in idiomatic English with troubleshooting guides, architecture breakdown, and installation instructions.
  - Localized all module comments across `ide`, `manager`, `agy`, `vscode`, and `utils`.
- **Flattened Repository Architecture**: Moved all source code from `source/` to the repository root for cleaner execution, standard packaging, and easier development.
- **Attribution & Fork Setup**: Updated all links, telemetry-free banners, and GitHub release endpoints to point to the `TheMRVX/open-antigravity-patcher` fork.

---

## [1.3.4] - 2026-08-22 (Upstream Baseline)
- Initial open-source release baseline supporting Antigravity IDE, Antigravity 2.0, Antigravity CLI, and VS Code extension patching.
