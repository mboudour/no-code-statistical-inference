"""Question-first entry point for the seminar inference workflows."""

import streamlit as st

from inference_ui import render_question_to_method
from seminar_ui import load_manifest, render_sidebar

st.set_page_config(page_title="Guided Inference", page_icon="🧭", layout="wide")
render_sidebar()
render_question_to_method(load_manifest())
