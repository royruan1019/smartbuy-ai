# 函式介面

MVP 採單體 Streamlit 應用，頁面透過 Python 函式呼叫領域模組，暫不提供公開 HTTP API。

| 函式 | 輸入 | 主要輸出 |
|---|---|---|
| `get_price_status` | 品項、選填市場 | 今日價格、狀態、白話原因 |
| `get_origin_weather_risk` | 品項 | 主要產地、風險等級、提醒 |
| `get_today_solar_term_advice` | 選填日期 | 節氣、說明、推薦品項 |
| `get_purchase_advice` | 品項 | 價格、天氣、節氣、替代品整合建議 |
| `load_tasks` | 選填 JSON 路徑 | 任務陣列 |
| `update_task_status` | 任務 ID、狀態 | 無；更新 JSON |

未來拆成 FastAPI 時可保持輸出字典欄位，降低前端改版成本。

