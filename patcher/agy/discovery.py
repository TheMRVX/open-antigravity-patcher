import os
import glob
import shutil


def clean_path(raw_path):
    """Strips quotes and whitespace from edges."""
    return raw_path.strip().strip('"').strip("'")


def _dedup_newest(paths):
    """Deduplicates real paths and sorts by modification time (newest first)."""
    seen = set()
    out = []
    existing = {p for p in paths if p and os.path.exists(p)}
    for p in sorted(existing, key=lambda x: os.path.getmtime(x), reverse=True):
        key = os.path.normcase(os.path.realpath(p))
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def _win_candidate_dirs():
    """Search roots for agy.exe on Windows: environment variables + scoop + Programs."""
    out = []
    for var in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)",
                "ProgramData", "APPDATA"):
        p = os.environ.get(var)
        if not p:
            continue
        out.append(p)
        programs = os.path.join(p, "Programs")
        if os.path.isdir(programs):
            out.append(programs)
    up = os.environ.get("USERPROFILE", "")
    if up:
        out.append(os.path.join(up, "scoop", "apps"))
    scoop = os.environ.get("SCOOP", "")
    if scoop:
        out.append(os.path.join(scoop, "apps"))
    return [p for p in out if p and os.path.isdir(p)]


def _posix_candidate_dirs():
    """Search directories for agy binary on POSIX."""
    from patcher.utils.file import get_posix_invoking_user_home
    user_home = get_posix_invoking_user_home()
    out = ["/usr/local/bin", "/usr/bin", "/opt/antigravity/bin", "/opt/antigravity"]
    if user_home:
        out.append(os.path.join(user_home, ".local/bin"))
        out.append(os.path.join(user_home, "bin"))
    else:
        out.append(os.path.expanduser("~/.local/bin"))
        out.append(os.path.expanduser("~/bin"))
    return [p for p in out if p and os.path.isdir(p)]


def _win_find():
    cands = []
    w = shutil.which("agy")
    if w:
        # which() returns upper-case .EXE from PATHEXT; normalize for dedup
        base, ext = os.path.splitext(w)
        cands.append(base + ext.lower())
    for root in _win_candidate_dirs():
        cands += glob.glob(os.path.join(root, "agy", "bin", "agy.exe"))
        cands += glob.glob(os.path.join(root, "agy", "*", "bin", "agy.exe"))  # scoop version dirs
        cands += glob.glob(os.path.join(root, "agy*", "agy.exe"))
    return _dedup_newest(cands)


def _posix_find():
    cands = []
    local_agy = os.path.join(os.getcwd(), "agy")
    if os.path.isfile(local_agy):
        cands.append(local_agy)
    w = shutil.which("agy")
    if w:
        cands.append(w)
    for root in _posix_candidate_dirs():
        cands += glob.glob(os.path.join(root, "agy"))
    return _dedup_newest(cands)


def find_agy_binary():
    """Returns path to agy binary (agy.exe on Windows, agy on POSIX) or ''.
    Discovery is location-agnostic: PATH + standard directories + scoop."""
    try:
        hits = _win_find() if os.name == "nt" else _posix_find()
    except Exception:
        return ""
    return hits[0] if hits else ""


def resolve_agy_path(raw_path):
    """Resolves user-specified path to agy binary.
    Returns valid path or ''. agy/agy.exe file is accepted directly;
    directories are searched using glob patterns."""
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(cleaned)))

    if os.path.isfile(resolved):
        name = os.path.basename(resolved).lower()
        if name in ("agy", "agy.exe"):
            return resolved
        # Arbitrary file - accept as is
        return resolved

    if os.path.isdir(resolved):
        # Search inside specified directory (including bin/ and scoop version dirs)
        patterns = (["agy.exe", os.path.join("bin", "agy.exe")] if os.name == "nt"
                    else ["agy", os.path.join("bin", "agy")])
        hits = []
        for pat in patterns:
            hits += glob.glob(os.path.join(resolved, pat))
            hits += glob.glob(os.path.join(resolved, "*", pat))
        deduped = _dedup_newest(hits)
        if deduped:
            return deduped[0]

    return ""
