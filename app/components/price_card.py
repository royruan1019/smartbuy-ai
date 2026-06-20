from __future__ import annotations

import html

import streamlit as st


ICONS = {"便宜": "🟢", "正常": "🔵", "偏貴": "🟠", "資料不足": "⚪"}


def render_price_card(item: dict) -> None:
    name = html.escape(str(item["product_name"]))
    status = html.escape(str(item["status"]))
    price = "—" if item.get("today_price") is None else f"{float(item['today_price']):.1f} 元／公斤"
    suggestion = html.escape(str(item.get("suggestion", "")))
    st.markdown(
        f'<div class="sb-card"><div class="sb-title">{ICONS.get(status, "⚪")} {name}</div>'
        f'<div class="sb-value">{status}・{price}</div><div class="sb-note">{suggestion}</div></div>',
        unsafe_allow_html=True,
    )

