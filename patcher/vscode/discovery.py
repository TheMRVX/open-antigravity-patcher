import os
import glob


def _user_home():
    """User home directory. On POSIX when running via sudo,
    returns the invoking user's home (~user) rather than /root,
    so that ~/.vscode-server and ~/.gemini are resolved correctly."""
    if os.name == "posix":
        from patcher.utils.file import get_posix_invoking_user_home
        home = get_posix_invoking_user_home()
        if home:
            return home
    return os.path.expanduser("~")


def clean_path(raw_path):
    """Strips quotes and whitespace from edges."""
    return raw_path.strip().strip('"').strip("'")


def _extension_roots():
    """VS Code extension root directories (standard, Insiders, OSS, remote-server).
    Environment variable VSCODE_EXTENSIONS takes precedence if set."""
    home = _user_home()
    roots = []
    env = os.environ.get("VSCODE_EXTENSIONS")
    if env and os.path.isdir(env):
        roots.append(env)
    roots += [
        os.path.join(home, ".vscode", "extensions"),
        os.path.join(home, ".vscode-insiders", "extensions"),
        os.path.join(home, ".vscode-oss", "extensions"),
        os.path.join(home, ".vscode-server", "extensions"),
        os.path.join(home, ".vscode-server-insiders", "extensions"),
    ]
    seen = set()
    out = []
    for r in roots:
        key = os.path.normcase(os.path.abspath(r))
        if key not in seen and os.path.isdir(r):
            seen.add(key)
            out.append(r)
    return out


def find_extension_dir():
    """Returns the newest directory for the google.google-antigravity-* extension.
    Directory name is versioned (e.g. google.google-antigravity-1.0.0),
    so we match by glob and sort by mtime (newest first)."""
    candidates = []
    for root in _extension_roots():
        candidates += glob.glob(
            os.path.join(root, "google.google-antigravity-*")
        )
    dirs = [d for d in candidates if os.path.isdir(d)]
    if not dirs:
        return ""
    dirs.sort(key=lambda d: os.path.getmtime(d), reverse=True)
    return dirs[0]


def find_extension_js():
    """Returns path to extension.js of google.google-antigravity extension or ''."""
    ext_dir = find_extension_dir()
    if not ext_dir:
        return ""
    js = os.path.join(ext_dir, "extension.js")
    return js if os.path.isfile(js) else ""


def resolve_extension_path(raw_path):
    """Resolves user path to extension.js.
    Accepts: the extension.js file itself, the extension directory
    (google.google-antigravity-*), or the root extensions directory."""
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(cleaned)))

    if os.path.isfile(resolved):
        if os.path.basename(resolved).lower() == "extension.js":
            return resolved
        # Arbitrary file - accept as is
        return resolved

    if os.path.isdir(resolved):
        # Extension directory directly
        direct = os.path.join(resolved, "extension.js")
        if os.path.isfile(direct):
            return direct
        # Root extensions directory — search inside google.google-antigravity-*
        hits = glob.glob(
            os.path.join(resolved, "google.google-antigravity-*", "extension.js")
        )
        hits = [h for h in hits if os.path.isfile(h)]
        if hits:
            hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return hits[0]

    return ""


def find_gemini_antigravity_binary():
    """Binary downloaded by the extension into ~/.gemini/bin.
    Windows: antigravity.exe / agy.exe, macOS/Linux: antigravity / agy.
    Returns path or ''. Used ONLY by 'Antigravity VS Code Patch'."""
    home = _user_home()
    ext = ".exe" if os.name == "nt" else ""
    for name in ("antigravity", "agy"):
        p = os.path.join(home, ".gemini", "bin", name + ext)
        if os.path.isfile(p):
            return p
    return ""


def describe_gemini_binary_path():
    """Human-readable expected binary path (for messages)."""
    name = "antigravity.exe" if os.name == "nt" else "antigravity"
    return os.path.join("~", ".gemini", "bin", name)
