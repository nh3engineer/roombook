import json
import os
import tempfile
from pathlib import Path

DEFAULT_DIR_NAME = "Raumbuch"
SETTINGS_FILE = "einstellungen.json"
PROJECTS_SUBDIR = "projects"
EXPORTS_SUBDIR = "exports"
LOGO_FILE = "logo.png"

COLORS = {
    "primary": "#1A1A1A",
    "primary_dark": "#000000",
    "accent": "#E8A0B4",
    "accent_soft": "#F6E3E8",
    "text_dark": "#1A1A1A",
    "bg_light": "#EFC9C4",
    "sidebar": "#E3CDDC",
    "sidebar_hover": "#D5C2D2",
    "muted": "#6E5F6B",
    "card": "#FFFFFF",
    "success": "#2E9E5B",
    "warning": "#E2A03F",
    "danger": "#B23A2E",
}


def default_data_dir() -> Path:
    home = Path.home()
    docs = home / "Documents"
    if docs.exists():
        return docs / DEFAULT_DIR_NAME
    return home / DEFAULT_DIR_NAME


def _settings_path() -> Path:
    return default_data_dir() / SETTINGS_FILE


def load_settings() -> dict:
    path = _settings_path()
    settings = {"datenordner": str(default_data_dir())}
    if path.exists():
        try:
            with open(path, encoding="utf-8") as fh:
                saved = json.load(fh)
            if isinstance(saved, dict):
                settings.update(saved)
        except (OSError, json.JSONDecodeError):
            pass
    return settings


def save_settings(settings: dict) -> None:
    path = _settings_path()
    ensure_writable(path.parent)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def ensure_writable(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    test = directory / ".schreibtest"
    try:
        test.write_text("ok", encoding="utf-8")
        test.unlink()
    except OSError as exc:
        raise PermissionError(
            f"Im Ordner '{directory}' kann nicht gespeichert werden. "
            f"Bitte prüfen Sie die Schreibrechte oder wählen Sie in den "
            f"Einstellungen einen anderen Datenordner."
        ) from exc


def projects_dir() -> Path:
    data_dir = Path(load_settings()["datenordner"])
    return data_dir / PROJECTS_SUBDIR


def exports_dir() -> Path:
    data_dir = Path(load_settings()["datenordner"])
    return data_dir / EXPORTS_SUBDIR


def ensure_data_dirs() -> Path:
    data_dir = Path(load_settings()["datenordner"])
    ensure_writable(data_dir)
    (data_dir / PROJECTS_SUBDIR).mkdir(exist_ok=True)
    (data_dir / EXPORTS_SUBDIR).mkdir(exist_ok=True)
    return data_dir


def open_in_explorer(path: Path) -> None:
    import sys
    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        os.system(f'open "{path}"')
    else:
        os.system(f'xdg-open "{path}"')


def safe_temp_copy(source: Path) -> Path:
    tmp = Path(tempfile.gettempdir()) / source.name
    data = source.read_bytes()
    tmp.write_bytes(data)
    return tmp
