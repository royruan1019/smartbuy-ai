# TASK-D02 小白教學：將價格搜尋頁切換為 Supabase 優先

## 1. 這個功能是做什麼的？

建立價格資料存取層 price_repository.py，支援 Supabase 優先與本機 CSV 備援讀取，並修改價格搜尋頁使用該資料層。

## 2. 這次完成了什麼？

已完成價格搜尋頁之 Supabase 優先與本機 CSV 備援讀取功能切換，保障欄位與 UI 相容性。

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

- `src/data/price_repository.py`
- `app/pages/02_price_search.py`
- `src/data/data_loader.py`

## 5. 怎麼測試？

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q --basetemp=.tmp_pytest
```

## 6. 預期與實際結果

全體單元測試 42 passed，覆蓋了 fallback、SQLite 仿真查詢、空查詢不 fallback 與欄位對齊測試；git status 確認無大檔案或敏感配置洩漏。

## 7. 下一步可以怎麼做？

無
