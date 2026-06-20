from __future__ import annotations

import streamlit as st


def render_task_card(task: dict) -> None:
    with st.container(border=True):
        st.subheader(f"{task['task_id']}｜{task['title']}")
        cols = st.columns(3)
        cols[0].metric("狀態", task["status"])
        cols[1].metric("優先度", task["priority"])
        cols[2].metric("模組", task["module"])
        st.write(task["goal"])
        st.caption(f"負責人：{task['owner']}｜協作：{task['worker_type']}")

