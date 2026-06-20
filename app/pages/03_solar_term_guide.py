import streamlit as st

from app.common import configure_page, demo_notice
from app.components.solar_term_card import render_solar_term_card
from src.anomaly.price_status import get_price_status
from src.calendar.solar_terms import get_today_solar_term_advice
from src.recommendation.seasonal_recommender import get_seasonal_recommendations


configure_page("節氣推薦")
st.title("🌿 24 節氣採買指南")
demo_notice()

term = get_today_solar_term_advice()
render_solar_term_card(term)
st.write(f"飲食與保存提醒：{term['health_tip']}")
st.warning(f"留意：{term['risk_note']}")

st.header("這個節氣適合看看")
recommendations = get_seasonal_recommendations()
if not recommendations:
    st.info("目前示範品項較少，尚無更詳細的節氣品項資料。")
for item in recommendations:
    price = get_price_status(item["product_name"])
    with st.container(border=True):
        st.subheader(f"{item['product_name']}｜{price['status']}")
        st.write(item["reason"])
        st.write(f"料理：{item['suggested_cooking']}")
        st.caption(f"保存：{item['storage_tip']}")
st.caption(term["reference_note"])

