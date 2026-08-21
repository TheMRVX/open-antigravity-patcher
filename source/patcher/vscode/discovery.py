import os
import glob


def clean_path(raw_path):
    """Убирает кавычки/пробелы по краям — как в ide/agy discovery."""
    return raw_path.strip().strip('"').strip("'")


def _extension_roots():
    """Корневые каталоги расширений VS Code (обычный, Insiders, OSS, remote-server).
    Первым идёт переопределение через env VSCODE_EXTENSIONS, если задано."""
    home = os.path.expanduser("~")
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
    """Возвращает новейший каталог расширения google.google-antigravity-*.
    Имя каталога версионированное (например google.google-antigravity-1.0.0),
    поэтому ищем по маске и сортируем по mtime (новейший первым)."""
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
    """Возвращает путь к extension.js расширения google.google-antigravity или ''."""
    ext_dir = find_extension_dir()
    if not ext_dir:
        return ""
    js = os.path.join(ext_dir, "extension.js")
    return js if os.path.isfile(js) else ""


def resolve_extension_path(raw_path):
    """Разрешает пользовательский путь к extension.js.
    Принимает: сам файл extension.js, каталог расширения
    (google.google-antigravity-*) или корневой каталог extensions."""
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(cleaned)))

    if os.path.isfile(resolved):
        if os.path.basename(resolved).lower() == "extension.js":
            return resolved
        # Произвольный файл — принимаем как есть (пользователь лучше знает)
        return resolved

    if os.path.isdir(resolved):
        # Каталог самого расширения
        direct = os.path.join(resolved, "extension.js")
        if os.path.isfile(direct):
            return direct
        # Корневой каталог extensions — ищем внутри google.google-antigravity-*
        hits = glob.glob(
            os.path.join(resolved, "google.google-antigravity-*", "extension.js")
        )
        hits = [h for h in hits if os.path.isfile(h)]
        if hits:
            hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return hits[0]

    return ""


def find_gemini_antigravity_binary():
    """Бинарь Antigravity CLI, скачиваемый расширением в ~/.gemini/bin.
    Windows: antigravity.exe, macOS/Linux: antigravity. Возвращает путь или ''."""
    name = "antigravity.exe" if os.name == "nt" else "antigravity"
    p = os.path.join(os.path.expanduser("~"), ".gemini", "bin", name)
    return p if os.path.isfile(p) else ""


def describe_gemini_binary_path():
    """Человекочитаемый ожидаемый путь к бинарю (для сообщений)."""
    name = "antigravity.exe" if os.name == "nt" else "antigravity"
    return os.path.join("~", ".gemini", "bin", name)
