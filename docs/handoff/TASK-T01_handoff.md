# TASK-T01 交接摘要：任務資料

## 已完成

- 任務 JSON 格式、必要欄位驗證、三條件篩選與狀態更新。
- 任務中心已有初始 MVP 任務資料。

## 尚未完成

- 尚未加入多人同時寫入的鎖定機制。
- 尚未在有 Python 的環境跑完測試。

## 已知問題

JSON 適合單機 MVP，多人同時修改時仍應透過 Git 分支協作。

## 接手前必讀

- `data/tasks/tasks.json`
- `src/tasks/task_loader.py`
- `src/tasks/task_status.py`

## 測試指令

`python -m pytest tests/test_task_loader.py -q`

