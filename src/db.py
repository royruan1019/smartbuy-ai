import streamlit as st
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    """
    建立 Supabase PostgreSQL 資料庫連線。

    DATABASE_URL 會從 .streamlit/secrets.toml 讀取，
    不要把資料庫密碼直接寫在程式碼裡。
    """
    database_url = st.secrets["DATABASE_URL"]

    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    return engine