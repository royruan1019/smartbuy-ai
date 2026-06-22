from pathlib import Path
import sys

# 取得專案根目錄：
# 目前檔案位置是 app/pages/99_db_test.py
# parents[2] 會回到 smartbuy-ai 專案根目錄
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 將專案根目錄加入 Python 模組搜尋路徑
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from src.db import get_engine


st.title("資料庫連線測試")
st.write("測試 Streamlit 是否可以成功讀取 Supabase 的農產品行情資料。")

query = """
SELECT
    trans_date,
    crop_code,
    crop_name,
    market_code,
    market_name,
    upper_price,
    middle_price,
    lower_price,
    avg_price,
    volume
FROM agri_price_daily
ORDER BY trans_date DESC, crop_name ASC
LIMIT 50;
"""

try:
    engine = get_engine()
    df = pd.read_sql(query, engine)

    st.success("成功連接 Supabase，並讀取 agri_price_daily 資料。")
    st.write("目前讀取資料筆數：", len(df))
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("讀取 Supabase 資料失敗。")
    st.exception(e)