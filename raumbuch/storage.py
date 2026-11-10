import hashlib
import json
import os
import re
import secrets
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from . import config
from .models import Project

USERS_FILE = "benutzer.json"
RAUMTYPEN_FILE = "raumtypen.json"

DEFAULT_RAUMTYPEN = [
    "Lager",
    "Klimatisierung",
    "Technische Klimatisierung",
    "Tiefkühlung",
    "Kühlraum",
    "Reiferaum",
    "Produktionsraum",
    "Verkaufsraum",
]


def _safe_name(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_\-äöüÄÖÜß ]+", "_", text).strip()
    return cleaned or "Projekt"


def project_filename(project: Project) -> str:
    base = f"{project.name or 'Projekt'}_{project.version or 'Auslegung'}"
    return _safe_name(base) + ".raumbuch.json"


def save_project(project: Project, path: Optional[Path] = None) -> Path:
    config.ensure_data_dirs()
    if path is None:
        path = config.projects_dir() / project_filename(project)
    if not project.id:
        project.id = uuid.uuid4().hex
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(project.to_dict(), fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return path


def list_project_files() -> List[Tuple[Path, Project]]:
    folder = config.projects_dir()
    result: List[Tuple[Path, Project]] = []
    if not folder.exists():
        return result
    for file in sorted(folder.glob("*.raumbuch.json")):
        try:
            with open(file, encoding="utf-8") as fh:
                project = Project.from_dict(json.load(fh))
            result.append((file, project))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    result.sort(key=lambda item: (item[1].name.lower(), item[1].version.lower()))
    return result


def load_project(path: Path) -> Project:
    with open(path, encoding="utf-8") as fh:
        return Project.from_dict(json.load(fh))


def delete_project_file(path: Path) -> None:
    if path.exists():
        path.unlink()


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt), 120000)
    return digest.hex()


def _users_path() -> Path:
    return config.ensure_data_dirs() / USERS_FILE


def _load_users() -> dict:
    path = _users_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_users(users: dict) -> None:
    path = _users_path()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(users, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def register_user(email: str, name: str, password: str) -> Tuple[bool, str]:
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Bitte geben Sie eine gültige E-Mail-Adresse ein."
    if not name.strip():
        return False, "Bitte geben Sie Ihren Namen ein."
    if len(password) < 4:
        return False, "Das Passwort muss mindestens 4 Zeichen haben."
    users = _load_users()
    if email in users:
        return False, "Für diese E-Mail-Adresse existiert bereits ein Konto."
    salt = secrets.token_hex(16)
    users[email] = {
        "name": name.strip(),
        "salt": salt,
        "hash": _hash_password(password, salt),
    }
    _save_users(users)
    return True, "Konto erstellt – Sie können sich jetzt anmelden."


def login_user(email: str, password: str) -> Optional[dict]:
    email = email.strip().lower()
    users = _load_users()
    entry = users.get(email)
    if not entry:
        return None
    if _hash_password(password, entry["salt"]) != entry["hash"]:
        return None
    return {"email": email, "name": entry["name"]}


def list_raumtypen() -> List[str]:
    path = config.ensure_data_dirs() / RAUMTYPEN_FILE
    if not path.exists():
        return list(DEFAULT_RAUMTYPEN)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        typen = [str(t) for t in data if str(t).strip()]
        return typen or list(DEFAULT_RAUMTYPEN)
    except (OSError, json.JSONDecodeError):
        return list(DEFAULT_RAUMTYPEN)


def save_raumtypen(typen: List[str]) -> None:
    path = config.ensure_data_dirs() / RAUMTYPEN_FILE
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sorted(set(t.strip() for t in typen if t.strip())),
                  fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def add_raumtyp(name: str) -> bool:
    name = name.strip()
    if not name:
        return False
    typen = list_raumtypen()
    if name in typen:
        return False
    typen.append(name)
    save_raumtypen(typen)
    return True


def remove_raumtyp(name: str) -> None:
    typen = list_raumtypen()
    if name in typen:
        typen.remove(name)
        save_raumtypen(typen)
