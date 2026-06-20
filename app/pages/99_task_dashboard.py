from pathlib import Path

import streamlit as st

from app.common import ROOT, configure_page
from app.components.task_card import render_task_card
from src.tasks.task_loader import filter_tasks, load_tasks


configure_page("任務中心")
st.title("🧩 任務中心｜Human–Agent Dashboard")
st.write("給開發小組查看誰在做什麼、完成標準與交接位置。")

tasks = load_tasks()
statuses = sorted({task["status"] for task in tasks})
owners = sorted({task["owner"] for task in tasks})
modules = sorted({task["module"] for task in tasks})

cols = st.columns(3)
status = cols[0].selectbox("狀態", ["全部", *statuses])
owner = cols[1].selectbox("負責人", ["全部", *owners])
module = cols[2].selectbox("模組", ["全部", *modules])

filtered = filter_tasks(
    tasks,
    None if status == "全部" else status,
    None if owner == "全部" else owner,
    None if module == "全部" else module,
)
st.caption(f"共 {len(filtered)} 個任務")
if not filtered:
    st.info("目前沒有符合篩選條件的任務。")
else:
    task_labels = {f"{task['task_id']}｜{task['title']}": task for task in filtered}
    selected_label = st.selectbox("開啟任務詳情", list(task_labels))
    selected = task_labels[selected_label]
    render_task_card(selected)

    st.subheader("完成標準")
    for item in selected["done_definition"]:
        st.checkbox(item, value=selected["status"] == "已完成", disabled=True, key=f"{selected['task_id']}-{item}")

    st.subheader("相關檔案")
    st.code("\n".join(selected["related_files"]))

    st.subheader("任務文件")
    for label, field in [("開發紀錄", "dev_log"), ("小白教學", "tutorial_doc"), ("交接摘要", "handoff_note")]:
        relative = selected[field]
        exists = (Path(ROOT) / relative).exists()
        st.write(f"{'✅' if exists else '⬜'} {label}：`{relative}`")

