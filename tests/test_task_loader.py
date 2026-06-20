import json

import pytest

from src.tasks.task_loader import filter_tasks, load_tasks
from src.tasks.task_status import update_task_status


def test_project_tasks_are_valid():
    tasks = load_tasks()
    assert tasks
    assert filter_tasks(tasks, status="等待測試")


def test_update_task_status(tmp_path):
    source = load_tasks()[0]
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps([source], ensure_ascii=False), encoding="utf-8")
    update_task_status(source["task_id"], "進行中", path)
    assert load_tasks(path)[0]["status"] == "進行中"


def test_invalid_status_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        update_task_status("TASK-X", "亂碼", tmp_path / "tasks.json")
