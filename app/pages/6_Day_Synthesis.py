"""Daily synthesis and inference-audit activities for the seminar."""

import pandas as pd
import streamlit as st

from seminar_ui import load_manifest, render_sidebar

st.set_page_config(page_title="Day Synthesis", page_icon="🧩", layout="wide")
manifest = load_manifest()
render_sidebar()
st.title("Day synthesis and inference audit")
st.caption("Use this page at the end of each day to connect the ten modules into one inferential workflow.")

days = {day["id"]: day for day in manifest["days"]}
selected = st.selectbox("Select a day", list(days), format_func=lambda item: days[item]["title"])
day = days[selected]
st.header(day["general_theme"])
st.info(day["introduction"])
st.subheader("Conceptual map")
st.markdown("**What participants bring forward:** data structure, unit of observation, variable definitions, design, and uncertainty. Every later method remains conditional on those foundations.")
st.markdown("**What this day adds:** " + day["general_theme"] + ".")
st.markdown("**What participants should carry onward:** a written question, stated estimand, documented assumptions, diagnostic evidence, an estimate with uncertainty, and a limitation statement.")

st.subheader("Ten-module thread")
rows = []
for module in day["modules"]:
    rows.append({"Module": module["id"].upper(), "Title": module["title"], "Question": module["research_question_prompt"], "Diagnostic focus": module["diagnostic_focus"]})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("Synthesis activity")
st.markdown("1. Select one module and state its research question in your own words.\n2. Identify the unit of observation, target population, and one assumption that cannot be verified from a plot.\n3. Name the estimate and uncertainty statement you would report.\n4. State one limitation and one robustness check that would be appropriate.")
st.text_area("Write your synthesis note", key=f"synthesis_{selected}", placeholder="A defensible inference claim begins with …")
st.warning("A low p-value is not a measure of effect size, importance, or the probability that a hypothesis is true. Use it only as one model-based piece of evidence alongside estimates, intervals, diagnostics, design, and context.")
