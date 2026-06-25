# TASK-D02 開發紀錄：將價格搜尋頁切換為 Supabase 優先

## 1. 任務目標

建立價格資料存取層 price_repository.py，支援 Supabase 優先與本機 CSV 備援讀取，並修改價格搜尋頁使用該資料層。

## 2. 執行資訊

- 執行者：Antigravity
- 產生時間：2026-06-25T09:31:57+08:00
- 交付結果：success
- 下一狀態：已完成

## 3. 本次修改內容

修正 price_repository 測試中 load_price_history 的日期依賴問題。新增 reference_date 參數，並在測試中指定固定日期，使 pytest 穩定通過。

### 修改檔案

- `src/data/price_repository.py,tests/test_price_repository.py`

## 4. 完成標準

- [ ] 建立 src/data/price_repository.py 模組並實作指定函式
- [ ] 資料庫讀取支援 SSL 憑證驗證與安全防禦 (避免 SQL Injection)
- [ ] 資料庫讀取失敗或不可用時能自動且安全地 fallback 至本機 CSV 流程
- [ ] 修改價格搜尋頁以呼叫價格存取層，展示資料來源與最新日期
- [ ] 編寫單元測試覆蓋 Supabase 查詢、Mocking、Fallback 與關鍵字過濾
- [ ] 更新說明文件並依照 Agent 流程輸出日誌與教程

## 5. 測試方式

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 6. 測試結果

60 passed

## 7. 下一步

已完成測試修復，全數測試通過，無已知問題。
