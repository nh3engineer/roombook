import json
import os
from pathlib import Path
from typing import List

from . import config
from .models import Project


def _project_file(project_id: str) -> Path:
    return config.projects_dir() / f"{project_id}.json"


def list_projects(include_archived: bool = True) -> List[Project]:
    folder = config.projects_dir()
    projects: List[Project] = []
    if not folder.exists():
        return projects
    for file in sorted(folder.glob("*.json")):
        try:
            with open(file, encoding="utf-8") as fh:
                data = json.load(fh)
            project = Project.from_dict(data)
            projects.append(project)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    if not include_archived:
        projects = [p for p in projects if not p.archiviert]
    projects.sort(key=lambda p: (p.archiviert, p.name.lower()))
    return projects


def save_project(project: Project) -> None:
    config.ensure_data_dirs()
    path = _project_file(project.id)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(project.to_dict(), fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_project(project_id: str) -> Project:
    path = _project_file(project_id)
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return Project.from_dict(data)


def delete_project(project_id: str) -> None:
    path = _project_file(project_id)
    if path.exists():
        path.unlink()


def export_project(project: Project, target: Path) -> None:
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(project.to_dict(), fh, indent=2, ensure_ascii=False)


def import_project(source: Path) -> Project:
    with open(source, encoding="utf-8") as fh:
        data = json.load(fh)
    project = Project.from_dict(data)
    return project
