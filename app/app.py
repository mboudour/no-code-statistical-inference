"""No-Code Statistical Inference — seminar landing page."""

import pandas as pd
import streamlit as st

from seminar_ui import load_manifest, render_sidebar

st.set_page_config(
    page_title="No-Code Statistical Inference",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

manifest = load_manifest()
render_sidebar()

st.title("📊 No-Code Statistical Inference")
st.subheader("A Three-Day Academic Seminar — Understanding Data, Uncertainty, and Evidence")
st.markdown(
    "**Instructor:** Moses Boudourides, Data Science Graduate Program, "
    "School of Professional Studies, Northwestern University"
)
st.markdown("---")

st.header("A no-code seminar for rigorous statistical reasoning")
st.markdown(
    "This seminar is a **fully no-code** introduction to statistical inference. Participants do not "
    "need to write or modify code. Instead, they learn to make defensible decisions about data, "
    "uncertainty, and evidence through carefully annotated theory, worked public datasets, and "
    "Bring Your Own Data (BYOD) activities."
)
st.markdown(
    "The central premise is that a no-code interface must not hide statistical reasoning. Every result "
    "remains conditional on a target population, design, variables, model, assumptions, and analytical choices."
)
st.markdown("---")

st.header("How to navigate")
st.markdown(
    "Use the **sidebar page links** to open **Day 1**, **Day 2**, or **Day 3**. Each day page begins "
    "with its theory introduction and contains ten expandable modules. Every module includes a formal "
    "presentation without proofs, a selected public worked dataset, and a CSV-upload BYOD workflow."
)
rows = []
for day in manifest["days"]:
    rows.append(
        {
            "Day": day["title"],
            "General theme": day["general_theme"],
            "Modules": len(day["modules"]),
            "Module workflow": "Theory → worked public dataset → BYOD CSV upload",
        }
    )
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
st.info("👈 Select Day 1, Day 2, or Day 3 from the sidebar to begin.")
st.markdown("---")

st.header("Public datasets and BYOD")
st.markdown(
    "The application contains **34 bundled public CSV datasets** and can process every one through "
    "the same descriptive and inferential workbench. Each module identifies one selected public dataset "
    "for its worked example. Participants may also upload their own CSV dataset inside every module."
)
st.markdown(
    "> **Privacy notice:** Participant CSV uploads are processed in session memory only. They are not written to disk by the app."
)
st.markdown("---")

st.header("Resources")
first, second = st.columns(2)
with first:
    st.markdown("**GitHub repository**\n\n[View the code, datasets, and seminar materials](https://github.com/mboudour/no-code-statistical-inference)")
with second:
    st.markdown("**Seminar design**\n\n[View the detailed day-and-module design](https://github.com/mboudour/no-code-statistical-inference/blob/main/docs/seminar_design.md)")
st.markdown("---")
st.caption("© 2026 Moses Boudourides · Northwestern University · Built with Streamlit")
