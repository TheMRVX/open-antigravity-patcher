import os
import hashlib
import time
import shutil
import subprocess

try:
    import pwd
except ImportError:
    pwd = None


def file_hash(path):
    """Returns SHA-256 hash of file or None on error."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def file_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return 0


def format_bytes(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def fix_posix_permissions(path):
    """Ensures the path and its contents are owned by the invoking user on POSIX when running via sudo."""
    if os.name != "posix" or os.getuid() != 0:
        return

    sudo_uid = os.environ.get("SUDO_UID")
    sudo_gid = os.environ.get("SUDO_GID")

    if sudo_uid and sudo_gid:
        try:
            subprocess.run(["chown", "-R", f"{sudo_uid}:{sudo_gid}", path], check=False, timeout=30)
        except Exception:
            pass


def get_posix_invoking_user_home():
    """Returns the invoking user's home on POSIX, even when running via sudo."""
    if os.name != "posix":
        return ""

    if pwd is not None:
        sudo_uid = os.environ.get("SUDO_UID")
        if sudo_uid:
            try:
                return pwd.getpwuid(int(sudo_uid)).pw_dir
            except Exception:
                pass

        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            try:
                return pwd.getpwnam(sudo_user).pw_dir
            except Exception:
                pass

    home = os.environ.get("HOME")
    if home:
        return home

    return os.path.expanduser("~")


def backup_json_file(path):
    if not os.path.exists(path):
        return ""

    base = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    backup_path = base
    counter = 1
    while os.path.exists(backup_path):
        counter += 1
        backup_path = f"{base}-{counter}"

    shutil.copy2(path, backup_path)
    fix_posix_permissions(backup_path)
    return backup_path


def find_app_bundle(path):
    """Walks up from path to the first directory ending with .app.

    Used on macOS to determine the .app bundle root for re-signing
    after modifying main.js.
    """
    p = os.path.abspath(path)
    while p and p != os.path.dirname(p):
        if p.endswith(".app"):
            return p
        p = os.path.dirname(p)
    return ""


def remove_macos_immutable_flags(path):
    """Removes uchg/schg flags from a file or directory on macOS.

    On macOS, files inside .app bundles may have immutable flags
    that prevent write access even for root. Call before attempting
    to write to a .app bundle.
    """
    import sys
    if sys.platform != "darwin":
        return
    try:
        subprocess.run(
            ["chflags", "-R", "nouchg", path],
            check=False, capture_output=True, timeout=30,
        )
    except FileNotFoundError:
        pass
    except Exception:
        pass


def remove_macos_quarantine(path):
    """Removes com.apple.quarantine attribute from .app bundle."""
    import sys
    if sys.platform != "darwin":
        return
    try:
        subprocess.run(
            ["xattr", "-dr", "com.apple.quarantine", path],
            check=False, capture_output=True, timeout=30,
        )
    except FileNotFoundError:
        pass
    except Exception:
        pass


def resign_macos_bundle(main_js_path):
    """Re-signs .app with ad-hoc signature after modifying main.js.

    On macOS, any modification inside a signed .app bundle invalidates
    its code signature. Electron apps with Hardened Runtime crash
    at launch if the signature is invalid. codesign --force --sign - applies
    an ad-hoc signature (no Developer ID required), sufficient for local
    execution. Also removes com.apple.quarantine to avoid Gatekeeper warnings.
    """
    import sys
    if sys.platform != "darwin":
        return

    from patcher.utils.console import info, ok, warn

    app_path = find_app_bundle(main_js_path)
    if not app_path:
        # main.js is not inside .app (e.g. portable copy) - skip
        return

    info(f"Re-signing {os.path.basename(app_path)} (ad-hoc)...")
    try:
        subprocess.run(
            ["codesign", "--force", "--deep", "--sign", "-", app_path],
            check=True, capture_output=True, text=True, timeout=60,
        )
        ok("Ad-hoc signature applied")
    except FileNotFoundError:
        warn("codesign not found - install Xcode Command Line Tools")
        return
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        warn(f"codesign failed: {stderr}")
        return

    remove_macos_quarantine(app_path)


def resign_macos_binary(path):
    """Re-signs binary with ad-hoc signature after modification.

    On Apple Silicon macOS, the kernel immediately SIGKILLs any process
    whose code signature does not match its contents. codesign --force --sign -
    replaces Developer ID signature with ad-hoc signature for local execution.
    """
    import sys
    if sys.platform != "darwin":
        return

    from patcher.utils.console import info, ok, warn

    real = os.path.realpath(path)
    info(f"Re-signing {os.path.basename(real)} (ad-hoc)...")
    try:
        subprocess.run(
            ["codesign", "--force", "--sign", "-", real],
            check=True, capture_output=True, text=True, timeout=60,
        )
        ok("Ad-hoc signature applied")
    except FileNotFoundError:
        warn("codesign not found — install Xcode Command Line Tools")
    except subprocess.CalledProcessError as e:
        warn(f"codesign failed: {(e.stderr or '').strip()}")
