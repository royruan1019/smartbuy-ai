# TASK-T01 開發紀錄：建立 tasks.json 任務資料格式

## 任務目標

建立可被任務中心讀取與篩選的任務資料。

## 本次修改

- 新增 `data/tasks/tasks.json`。
- 新增 `src/tasks/task_loader.py`，驗證必要欄位並提供篩選。
- 新增 `src/tasks/task_status.py`，限制合法狀態後才更新。
- 新增 `tests/test_task_loader.py`。

## 設計理由

JSON 適合 MVP 與初學者直接查看；讀取時先檢查必要欄位，可避免畫面在不明位置才出錯。

## 測試方式

```powershell
python -m pytest tests/test_task_loader.py -q
```

## 測試結果

程式已完成，當前執行環境沒有可用的 Python 安裝，待有 Python 的環境執行驗證。

