# TASK-D01 小白教學：建立 Parquet 歷史資料儲存層

## 1. 這個功能是做什麼的？

建立本機 Parquet 歷史資料儲存層，降低 Supabase 容量負擔，並支援 ML 離線訓練與預測結果寫回。

## 2. 這次完成了什麼？

實作 Cloudflare R2 Parquet 歷史資料湖雙向同步與驗證。新增 R2 連線與同步工具、CLI 同步工具、整合每日行情更新與歷史回補流程、更新預測導引與 Actions 部署配置，並完成嚴格模式與 pruning 阻斷安全設計。

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

- `scripts/backfill_agri_price_history.py`
- `scripts/update_agri_price_daily.py`
- `src/data/data_loader.py`
- `README.md`
- `docs/SPEC.md`

## 5. 怎麼測試？

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 6. 預期與實際結果

70 passed

## 7. 下一步可以怎麼做？

已完成 Cloudflare R2 歷史資料湖串接，後續可在 Actions 中配置 Secrets 啟用 R2 同步功能。
