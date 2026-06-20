from __future__ import annotations

import html

import streamlit as st


def render_solar_term_card(term: dict) -> None:
    products = "、".join(term["recommended_products"])
    st.markdown(
        f'<div class="sb-card"><div class="sb-title">🌿 今日節氣：{html.escape(term["term_name"])}</div>'
        f'<div class="sb-value">{html.escape(term["shopping_tip"])}</div>'
        f'<div class="sb-note">{html.escape(term["description"])}<br>推薦：{html.escape(products)}</div></div>',
        unsafe_allow_html=True,
    )

