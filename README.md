# SmartBuy AI｜便宜買 AI

把農產品行情、產地天氣與 24 節氣轉成簡單採買建議的 Streamlit MVP。

## 快速開始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/main.py
```

執行測試：

```powershell
pytest -q
```

目前版本使用 `data/` 內的示範資料，可在沒有 API 金鑰的情況下完整展示。正式串接農業部與中央氣象署 API 前，請先確認資料授權、欄位與更新頻率。

完整原始規格請見根目錄的 `SmartBuy_AI_便宜買AI_MVP完整開發規格書_v1.1_含任務中心與24節氣.md`，開發入口見 `docs/SPEC.md`。

