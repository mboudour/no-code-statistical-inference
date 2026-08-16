"""Dataset laboratory for public-data audits and participant uploads."""

import pandas as pd
import streamlit as st

from seminar_ui import (
    load_manifest,
    load_public_data,
    public_dataset_labels,
    read_upload,
    render_dataset_workspace,
    render_sidebar,
)

st.set_page_config(page_title="Dataset Laboratory", page_icon="🧪", layout="wide")
manifest = load_manifest()
render_sidebar()
st.title("Dataset laboratory")
st.caption("Audit a public teaching dataset or upload a CSV before choosing an inferential pathway.")

public_tab, upload_tab, manual_tab = st.tabs(["Bundled public datasets", "Participant file upload", "Manual data entry"])
with public_tab:
    labels = public_dataset_labels(manifest)
    filename = st.selectbox("Choose a bundled public dataset", sorted(labels), format_func=lambda item: f"{labels[item]} ({item})")
    render_dataset_workspace(load_public_data(filename), "laboratory_public", labels[filename], filename)
with upload_tab:
    uploaded_file = st.file_uploader("Upload a CSV or Excel dataset", type=["csv", "xlsx", "xls"], key="laboratory_upload")
    uploaded = read_upload(uploaded_file)
    if uploaded is None:
        st.info("CSV and Excel uploads are processed in this browser session only and are not written to disk.")
    else:
        render_dataset_workspace(uploaded, "laboratory_upload", "Participant-uploaded dataset")

with manual_tab:
    st.caption("Enter a small table for practice. Rename columns to meaningful variables before drawing an inferential conclusion.")
    columns = st.number_input("Number of columns", min_value=1, max_value=10, value=2, step=1, key="manual_column_count")
    starter = {f"variable_{index + 1}": pd.Series(dtype="object") for index in range(int(columns))}
    entered = st.data_editor(pd.DataFrame(starter), num_rows="dynamic", use_container_width=True, key="manual_data_editor")
    if entered.empty:
        st.info("Add at least one row to activate the dataset audit and guided analysis workflow.")
    else:
        render_dataset_workspace(entered, "laboratory_manual", "Participant-entered dataset")
