# TASK-D02 小白教學：將價格搜尋頁切換為 Supabase 優先

## 1. 這個功能是做什麼的？

建立價格資料存取層 price_repository.py，支援 Supabase 優先與本機 CSV 備援讀取，並修改價格搜尋頁使用該資料層。

## 2. 這次完成了什麼？

修正 price_repository 測試中 load_price_history 的日期依賴問題。新增 reference_date 參數，並在測試中指定固定日期，使 pytest 穩定通過。

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
.\.venv\Scripts\python.exe -m pytest -q
```

## 6. 預期與實際結果

60 passed

## 7. 下一步可以怎麼做？

已完成測試修復，全數測試通過，無已知問題。
