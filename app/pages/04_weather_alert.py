import streamlit as st

from app.common import configure_page, demo_notice
from app.components.alert_card import render_alert_card
from src.data.data_loader import load_product_origins
from src.weather.origin_weather_risk import get_origin_weather_risk
from src.weather.typhoon_alert import get_typhoon_alert


configure_page("產地天氣提醒")
st.title("🌧️ 產地天氣與天災提醒")
demo_notice()

typhoon = get_typhoon_alert()
render_alert_card("颱風狀況", typhoon["message"], "很高" if typhoon["active"] else "低")

products = load_product_origins()["product_name"].tolist()
product = st.selectbox("查看哪個品項的主要產地？", products)
risk = get_origin_weather_risk(product)
render_alert_card(f"{product}｜風險 {risk['risk_level']}", risk["message"], risk["risk_level"])
st.write("主要產地：" + "、".join(risk["origins"]))
if risk.get("affected_origins"):
    st.write("需要留意：" + "、".join(risk["affected_origins"]))
st.info("天氣只是影響價格的因素之一，畫面使用「可能」而非保證漲跌。")

