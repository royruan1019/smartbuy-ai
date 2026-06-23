# TASK-D06 小白教學：ML 訓練與預測產生流程

## 1. 這個功能是做什麼的？

建立農產品未來價格 Baseline 預測腳本與排程，實踐歷史行情分析、漲跌預警狀態研判，並寫回資料庫。

## 2. 這次完成了什麼？

完成 Baseline 價格預測與漲跌判定引擎，建立批次預測執行腳本，並成功 UPSERT 100 筆預測記錄至 Supabase

## 3. 功能流程

```text
讀取任務
  ↓
修改相關檔案
  ↓
執行測試
  ↓
產生文件並更新任務狀態
```

## 4. 相關檔案

- `src/ml/baseline_predictor.py`
- `scripts/generate_baseline_predictions.py`
- `tests/test_baseline_predictor.py`
- `tests/test_generate_baseline_predictions.py`

## 5. 怎麼測試？

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

## 6. 預期與實際結果

60 passed

## 7. 下一步可以怎麼做？

已完成價格預測 baseline 行程，下一階段可進行更複雜的 ML 模型或外部特徵擴充
