from __future__ import annotations

import json
from pathlib import Path


TASKS_PATH = Path(__file__).resolve().parents[2] / "data/tasks/tasks.json"
REQUIRED_FIELDS = {
    "task_id",
    "title",
    "status",
    "owner",
    "worker_type",
    "priority",
    "module",
    "related_files",
    "goal",
    "done_definition",
    "dev_log",
    "tutorial_doc",
    "handoff_note",
}


def load_tasks(path: Path | None = None) -> list[dict]:
    target = path or TASKS_PATH
    tasks = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(tasks, list):
        raise ValueError("tasks.json 最外層必須是陣列")
    for task in tasks:
        missing = REQUIRED_FIELDS - task.keys()
        if missing:
            raise ValueError(f"{task.get('task_id', '未知任務')} 缺少欄位：{sorted(missing)}")
    return tasks


def filter_tasks(
    tasks: list[dict], status: str | None = None, owner: str | None = None, module: str | None = None
) -> list[dict]:
    return [
        task
        for task in tasks
        if (not status or task["status"] == status)
        and (not owner or task["owner"] == owner)
        and (not module or task["module"] == module)
    ]

