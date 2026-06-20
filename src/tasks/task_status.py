from __future__ import annotations

import json
from pathlib import Path

from src.tasks.task_loader import TASKS_PATH, load_tasks


VALID_STATUSES = {"待認領", "進行中", "等待測試", "需要修改", "已完成", "已封存"}


def update_task_status(task_id: str, status: str, path: Path | None = None) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"不支援的任務狀態：{status}")
    target = path or TASKS_PATH
    tasks = load_tasks(target)
    for task in tasks:
        if task["task_id"] == task_id:
            task["status"] = status
            target.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return
    raise KeyError(f"找不到任務：{task_id}")

