# TASK-D01 開發紀錄：建立 Parquet 歷史資料儲存層

## 1. 任務目標

建立本機 Parquet 歷史資料儲存層，降低 Supabase 容量負擔，並支援 ML 離線訓練與預測結果寫回。

## 2. 執行資訊

- 執行者：Antigravity
- 產生時間：2026-06-25T10:20:58+08:00
- 交付結果：success
- 下一狀態：已完成

## 3. 本次修改內容

實作 Cloudflare R2 Parquet 歷史資料湖雙向同步與驗證。新增 R2 連線與同步工具、CLI 同步工具、整合每日行情更新與歷史回補流程、更新預測導引與 Actions 部署配置，並完成嚴格模式與 pruning 阻斷安全設計。

### 修改檔案

- `requirements.txt,src/data/r2_sync.py,scripts/sync_parquet_r2.py,scripts/update_agri_price_daily.py,scripts/backfill_agri_price_history.py,scripts/generate_baseline_predictions.py,.github/workflows/daily_agri_price_update.yml,docs/r2_parquet_data_lake.md,README.md,docs/SPEC.md,tests/test_r2_sync.py`

## 4. 完成標準

- [ ] 新增 data/history_parquet/ 目錄
- [ ] 歷史回補腳本支援將資料存入分月 Parquet 檔案
- [ ] 每日更新腳本支援同步更新 Parquet 並定期清理 Supabase 舊資料
- [ ] 提供 pandas 載入 Parquet 作為 ML 訓練資料來源的工具函式
- [ ] 設計預測結果寫入 Supabase prediction_results 表的介面與結構
- [ ] 更新 README 與 docs 說明雙層資料儲存架構

## 5. 測試方式

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 6. 測試結果

70 passed

## 7. 下一步

已完成 Cloudflare R2 歷史資料湖串接，後續可在 Actions 中配置 Secrets 啟用 R2 同步功能。
