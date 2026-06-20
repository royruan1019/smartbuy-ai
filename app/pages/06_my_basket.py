import streamlit as st

from app.common import configure_page, demo_notice
from src.data.data_loader import load_market_prices
from src.recommendation.purchase_advisor import get_purchase_advice


configure_page("我的菜籃")
st.title("🧺 我的菜籃")
st.write("先收藏常買品項；MVP 會保留到本次瀏覽結束。")
demo_notice()

products = sorted(load_market_prices()["product_name"].unique().tolist())
default = st.session_state.get("basket", ["高麗菜", "地瓜葉"])
basket = st.multiselect("常買品項", products, default=[item for item in default if item in products])
st.session_state["basket"] = basket

if not basket:
    st.info("目前菜籃是空的，從上方加入常買品項吧。")
for product in basket:
    advice = get_purchase_advice(product)
    with st.container(border=True):
        st.subheader(f"{product}｜{advice['recommendation']}")
        st.write(advice["advice"])

