from __future__ import annotations

import streamlit as st


def primary_action(label: str, key: str | None = None) -> bool:
    return st.button(label, key=key, type="primary", use_container_width=True)

