# Open AG Patcher

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="GPL-3.0 License"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Architecture-x86--64%20%7C%20ARM64-success?style=for-the-badge" alt="Architectures">
</p>

An open-source patcher and region-unlock utility for **Antigravity 2.0**, **Antigravity IDE**, **Antigravity CLI** (`agy`), and the **Google Antigravity extension for VS Code**. It unlocks access and bypasses region restrictions without requiring a VPN or changing your Google account region.

![Open AG Patcher Screenshot](https://i.ibb.co/s9Vh80CM/python-w-TPlox-Po-G4.png)

---

## Key Features

- **Automated Detection**: Automatically finds installations of Antigravity 2.0, Antigravity IDE, Antigravity CLI (`agy`), and the Google Antigravity VS Code extension across Windows registry, standard system paths, and package managers.
- **Antigravity IDE Patch**: Bypasses the internal `isGoogleInternal` auth gate in `main.js` and automatically clears VS Code compilation caches (`CachedData` and `Code Cache/js`) to ensure changes take effect immediately.
- **Antigravity 2.0 Patch (`language_server`)**: Patches the backend service binary at the machine code level using byte signatures for both **x86-64** and **ARM64** architectures, forcing `hasValidAuth=true`.
- **Antigravity CLI (`agy`) Patch**: Bypasses the "Eligibility Check" gate in the compiled Go binary at the machine code level via byte signatures for **x86-64** and **ARM64**.
- **VS Code Extension Patch**: Injects an anti-redownload guard into `extension.js` for `google.google-antigravity`, disables the channel change check (`isChannelChanged -> false`), and patches the downloaded backend binary in `~/.gemini/bin`.
- **Safe & Fully Reversible**: Creates clean backup copies (`.bak`, `.agybak`, `.vscodebak`) before modifying any files, with stale backup refreshing and 1-click restore functionality from the menu.
- **Cross-Platform Support**: Full support for Windows, Linux, and macOS (including Apple Silicon ARM64 and automatic ad-hoc code re-signing via `codesign`).
- **Privilege Management**: Automatically requests elevation when required (UAC on Windows, `sudo` on Linux/macOS) while respecting user home directories.

---

## Quick Start & Usage

### 1. Launching from Source

Ensure you have Python 3.8+ installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the patcher
python main.py
```

### 2. Specifying Custom Paths via CLI

If your application is installed in a non-standard directory, you can pass the path as a command-line argument:

```bash
# Windows
python main.py "C:\Users\<username>\AppData\Local\Programs\Antigravity IDE"
python main.py "C:\Users\<username>\AppData\Local\Programs\Antigravity\resources\bin\language_server.exe"
python main.py "C:\Users\<username>\AppData\Local\agy\bin\agy.exe"

# Linux
python main.py /usr/share/antigravity-ide
python main.py /opt/Antigravity/resources/bin/language_server
python main.py /usr/local/bin/agy

# macOS
python3 main.py "/Applications/Antigravity IDE.app"
python3 main.py "/Applications/Antigravity.app"
python3 main.py /usr/local/bin/agy
```

### 3. Running via Docker

You can also run the patcher containerized without installing Python locally:

```bash
# Pull and run the interactive CLI
docker run --rm -it themrvx/open-antigravity-patcher:latest

# Mount and patch host paths directly
docker run --rm -it -v /path/to/target:/target themrvx/open-antigravity-patcher:latest /target
```

---

## Interactive Menu Overview

When launched, the patcher presents an interactive terminal interface:

| Option | Category | Description |
| :--- | :--- | :--- |
| **`1`** | **PATCH** | **Antigravity IDE patch** — Modifies `main.js` to bypass region lock (`isGoogleInternal`) and clears compile caches. |
| **`2`** | **PATCH** | **Antigravity 2.0 patch** — Byte-signature patch for `language_server` binary (`hasValidAuth=true`). |
| **`3`** | **PATCH** | **Antigravity CLI (agy) patch** — Byte-signature patch for `agy` / `agy.exe` to bypass eligibility check. |
| **`4`** | **PATCH** | **Antigravity VS Code Patch** — Patches `extension.js` + unlocks the `~/.gemini/bin` backend binary. |
| **`5`** | **RESTORE** | **Antigravity IDE** — Restores original `main.js` from backup (`.bak`). |
| **`6`** | **RESTORE** | **Antigravity 2.0** — Restores original `language_server` binary from backup (`.agybak`). |
| **`7`** | **RESTORE** | **Antigravity CLI** — Restores original `agy` binary from backup (`.agybak`). |
| **`8`** | **RESTORE** | **Antigravity VS Code extension** — Restores `extension.js` and `~/.gemini/bin` binary from backups. |
| **`9`** | **TOOLS** | **Check for updates** — Query GitHub API for latest releases. |
| **`10`** | **TOOLS** | **Open GitHub repository** — Open project homepage in default web browser. |
| **`11`** | **TOOLS** | **Select custom path** — Manually specify installation path for any target. |
| **`12`** | **TOOLS** | **About program** — View version, licenses, and attribution. |
| **`0`** | **EXIT** | **Exit** — Close the patcher. |

---

## macOS Setup & Instructions

Because macOS enforces strict code-signing (Gatekeeper & Hardened Runtime), modifying an Electron bundle or Mach-O binary requires specific considerations:

### Option 1: Run directly from source (Recommended)

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Completely quit Antigravity IDE or Antigravity 2.0 if running.
3. Run the patcher:
   ```bash
   python3 main.py "/Applications/Antigravity IDE.app"
   ```
   *Note: If the application is located in `/Applications`, the script will request `sudo` access to write into the system directory.*

### Option 2: Precompiled Binary on macOS

If running a compiled binary, remove the macOS quarantine attribute after downloading:
```bash
chmod +x Open_AG_Patcher_macOS
xattr -dr com.apple.quarantine Open_AG_Patcher_macOS
./Open_AG_Patcher_macOS
```

### Automatic Re-signing

Whenever a patch is applied on macOS, the script automatically re-signs the bundle/binary using ad-hoc signature:
```bash
codesign --force --deep --sign - "/Applications/Antigravity IDE.app"
xattr -dr com.apple.quarantine "/Applications/Antigravity IDE.app"
```
To verify the ad-hoc signature manually:
```bash
codesign -dv "/Applications/Antigravity IDE.app" 2>&1 | grep Signature
# Expected output: Signature=adhoc
```

---

## Technical Details: How the Patches Work

### 1. Antigravity IDE Patch (`main.js`)

- **Mechanism**: The patcher searches for the authorization check in `main.js`:
  ```javascript
  // Original
  resetIsTierGCPTos(),this.XXX.isGoogleInternal
  
  // Patched
  resetIsTierGCPTos(),true
  ```
- **Cache Invalidation**: Electron/VS Code caches compiled bytecode in `CachedData` and `Code Cache/js`. The patcher clears these directories upon patching so that the IDE is forced to recompile the patched JS code.

### 2. Antigravity Manager Patch (`language_server`)

`language_server` is the backend service used in Antigravity 2.0. The patcher modifies the compiled Go binary using architecture-specific signatures:
- **x86-64 (Intel Mac / Windows x64 / Linux x64)**:
  Replaces `cmp byte ptr [rax + 8], 0` with `mov byte ptr [rax + 8], 1` followed by NOPs (`\xc6\x40\x08\x01\x90\x90`).
- **ARM64 (Apple Silicon / Linux ARM64 / Windows ARM64)**:
  Replaces `ldrb w3, [x0, #8] ; tbz w3, #0, skip` with `mov w3, #1 ; strb w3, [x0, #8]` (`\x23\x00\x80\x52\x03\x20\x00\x39`).
- **Result**: `hasValidAuth` is unconditionally set to `true`.

### 3. Antigravity CLI Patch (`agy`)

The `agy` CLI binary performs an "Eligibility Check". The patcher bypasses this gate in machine code:
- **x86-64**:
  Replaces `cmp byte ptr [rax + 8], 0` with `test rax, rax` + `NOP` (`48 85 c0 90`), causing the subsequent conditional jump (`jne`) to always branch to the "eligible" path.
- **ARM64**:
  Replaces `ldrb w1, [x0, #8]` with `mov w1, #1` (`21 00 80 52`), forcing the `tbnz` instruction to follow the eligible branch.

### 4. VS Code Extension Patch (`google.google-antigravity`)

The official extension checks release channels and automatically redownloads the backend binary on start, overwriting local patches. The patcher solves this in two steps:
1. **Guard Injection (Part 1)**: Injects an early-return check immediately after `[INSTALL] Checking Antigravity releases...` in `extension.js`. If a binary is already present in `~/.gemini/bin`, it reuses it and skips the download.
2. **Disable Channel Check (Part 2)**: Replaces:
   ```javascript
   const isChannelChanged = manifestFetched && lastInstalledUrl !== releaseBaseUrl;
   ```
   with:
   ```javascript
   const isChannelChanged = false;
   ```
3. **Backend Binary Patch**: Automatically invokes the `agy` patcher on `~/.gemini/bin/antigravity` (or `agy`).

---

## Troubleshooting & Error Guide

### Error HTTP 500 Internal Server Error
If you receive `HTTP 500 Internal Server Error` during AI queries in Antigravity IDE, this indicates an upstream server error on Google's backend. The local client patch cannot resolve internal server issues; switching accounts or regions may help.

### Error HTTP 403 Forbidden / SUBSCRIPTION_REQUIRED (#3501)
```json
{
  "error": {
    "code": 403,
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "domain": "cloudaicompanion.googleapis.com",
        "reason": "SUBSCRIPTION_REQUIRED"
      }
    ],
    "message": "You do not have a valid license of this product. Please contact your administrator to request a license. (#3501)",
    "status": "PERMISSION_DENIED"
  }
}
```
- **Cause**: This error originates from the Google Cloud AI API due to server-side license verification.
- **Explanation**: The patcher modifies local files to bypass client-side region checks, but cannot fabricate server-side licenses.
- **Solution**: Use an account with access to the service or configure an active subscription.

### Error HTTP 400 Bad Request ("User location is not supported")
```json
{
  "error": {
    "code": 400,
    "message": "User location is not supported for the API use.",
    "status": "FAILED_PRECONDITION"
  }
}
```
- **Solution**: Apply **PATCH → 1 (Antigravity IDE patch)**. If already patched, verify that you restarted the IDE and that your network DNS/IP settings are not triggering server-side geo-blocks.

### Patch Error: `isGoogleInternal -> true (auth) — pattern not found`
- **Cause**: The patcher detected a `main.js` file, but it belongs to another Electron app or is from an unsupported version.
- **Solution**: Choose **TOOLS → 11 (Select custom path)** and specify the exact path to your Antigravity IDE directory manually.

### macOS: "Operation not permitted"
If you encounter permission errors when creating backups on macOS:
1. Grant Full Disk Access to Terminal: **System Settings → Privacy & Security → Full Disk Access**.
2. Remove quarantine attributes:
   ```bash
   sudo xattr -rd com.apple.quarantine "/Applications/Antigravity IDE.app"
   ```

---

## Discovery & Search Order

The patcher looks for target files in the following order:

1. **CLI Argument / Custom Path**: Explicitly passed via terminal or Option 11.
2. **Current Directory**: Checks `./main.js` or `./agy` in the working directory.
3. **Standard System Paths**:
   - **Windows**: `%LOCALAPPDATA%\Programs\Antigravity IDE`, `Program Files`, Scoop directories (`%USERPROFILE%\scoop\apps`), and Registry uninstall keys (`{AA73B3E3-C6C8-45C8-B1DC-4AE56C751432}_is1`).
   - **Linux**: `/usr/share/antigravity-ide`, `/opt/Antigravity IDE`, `/usr/local/bin/agy`, `~/.local/bin/agy`.
   - **macOS**: `/Applications/Antigravity IDE.app`, `~/Applications/Antigravity IDE.app`, `/Applications/Antigravity.app`.
4. **VS Code Extensions**: Searches `~/.vscode/extensions`, `~/.vscode-insiders/extensions`, `~/.vscode-server/extensions`, and `VSCODE_EXTENSIONS` environment variable.

---

## Requirements & Compatibility

- **Python**: 3.8 or higher
- **Dependencies**: `packaging`
- **Supported Operating Systems**:
  - Windows (x64, ARM64)
  - Linux (x64, ARM64)
  - macOS (Intel x86-64, Apple Silicon ARM64)
- **Supported Versions**:
  - Antigravity IDE: `2.1.1` and higher
  - Antigravity 2.0: `2.3.0` and higher

---

## Building Standalone Executables

To build standalone binary executables using PyInstaller:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Build Commands:

- **Windows**:
  ```bash
  pyinstaller --onefile --uac-admin --icon=icon.ico --name="Open_AG_Patcher_Windows" --noupx --clean --version-file=version.txt main.py
  ```
- **Linux**:
  ```bash
  pyinstaller --onefile --icon=icon.ico --name="Open_AG_Patcher_Linux" --hidden-import=packaging --hidden-import=packaging.version --hidden-import=packaging.specifiers --hidden-import=packaging.requirements main.py
  ```
- **macOS (Universal2)**:
  ```bash
  pyinstaller --onefile --name="Open_AG_Patcher_macOS" --target-arch universal2 --hidden-import=packaging --hidden-import=packaging.version --hidden-import=packaging.specifiers --hidden-import=packaging.requirements main.py
  ```

---

## Repository Structure

```text
open-antigravity-patcher/
├── LICENSE                     # GNU General Public License v3.0
├── README.md                   # Project documentation
├── requirements.txt            # Python package dependencies
├── main.py                     # Main application entry point & privilege elevation
├── version.txt                 # Windows PE file version metadata
├── build.txt                   # PyInstaller build commands reference
├── icon.ico                    # Application icon
├── .github/
│   └── workflows/
│       ├── build-python.yml    # Multi-platform CI build pipeline
│       ├── release.yml         # Automated multi-platform release pipeline
│       └── sync-upstream.yml   # Upstream synchronization workflow
└── patcher/
    ├── __init__.py             # Package root
    ├── constants.py            # Global constants, regexes, and ANSI palette
    ├── cli.py                  # Interactive console interface and menu routing
    ├── ide/                    # Antigravity IDE (main.js) discovery & patching
    │   ├── discovery.py
    │   └── patcher.py
    ├── manager/                # Antigravity 2.0 (language_server) discovery & patching
    │   ├── discovery.py
    │   └── patcher.py
    ├── agy/                    # Antigravity CLI (agy binary) discovery & patching
    │   ├── discovery.py
    │   └── patcher.py
    ├── vscode/                 # VS Code extension (extension.js) discovery & patching
    │   ├── discovery.py
    │   └── patcher.py
    └── utils/                  # Helper utilities
        ├── admin.py            # UAC / sudo elevation & process termination
        ├── captcha.py          # Confirmation CAPTCHA for re-patching
        ├── console.py          # ANSI terminal formatting, tables, and frames
        ├── file.py             # File hashing, POSIX permissions, and macOS codesign
        └── update.py           # GitHub release update checker
```

---

## License & Attribution

This project is licensed under the **GNU General Public License v3.0** ([`LICENSE`](LICENSE)).

### Attribution & Project Links
- Fork maintained by [TheMRVX](https://github.com/TheMRVX/open-antigravity-patcher).
- Upstream project development by [AvenCores](https://github.com/AvenCores/open-antigravity-patcher).
- Portions of the binary machine code patching logic and research are based on [eligibility-antigravity-patcher](https://github.com/QNIX-Dev/eligibility-antigravity-patcher) (MIT License).
