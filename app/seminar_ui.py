"""Shared Streamlit components for the No-Code Statistical Inference seminar."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from scipy import stats

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data" / "public"
MANIFEST_PATH = PROJECT_DIR / "data" / "module_manifest.json"


@st.cache_data
def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_public_data(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / filename).drop(columns="rownames", errors="ignore")


def read_upload(uploaded_file) -> pd.DataFrame | None:
    if uploaded_file is None:
        return None
    try:
        return pd.read_csv(uploaded_file).drop(columns="rownames", errors="ignore")
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"This file could not be read as a CSV: {error}")
        return None


def numerical(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=np.number).columns.tolist()


def categorical(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(exclude=np.number).columns.tolist()


def public_dataset_labels(manifest: dict) -> dict[str, str]:
    labels: dict[str, str] = {}
    for day in manifest["days"]:
        for module in day["modules"]:
            demo = module["demonstration"]
            labels[demo["file"]] = demo["name"]
            for item in module["byod"]:
                labels[item["file"]] = item["name"]
    for file in DATA_DIR.glob("*.csv"):
        labels.setdefault(file.name, file.stem.replace("_", " ").title())
    return labels


def render_sidebar() -> None:
    st.sidebar.markdown("### Seminar companion")
    st.sidebar.info(
        "Use the page links above to open **Day 1**, **Day 2**, or **Day 3**. "
        "Each day begins with theory and contains ten module sections."
    )
    st.sidebar.markdown("#### Data policy")
    st.sidebar.caption(
        "Public teaching datasets are bundled with the app. Participant CSV uploads are processed "
        "in session memory and are not written to disk."
    )


def render_profile(data: pd.DataFrame, key: str) -> None:
    """Dataset-agnostic descriptive workbench with interactive and static chart options."""
    a, b, c = st.columns(3)
    a.metric("Rows", f"{len(data):,}")
    b.metric("Columns", len(data.columns))
    c.metric("Complete rows", f"{len(data.dropna()):,}")
    st.dataframe(data.head(15), width="stretch")

    nums = numerical(data)
    cats = categorical(data)
    univariate, grouped, association, static = st.tabs(
        ["Univariate distributions", "Numeric by group", "Two categorical variables", "Static teaching figure"]
    )

    with univariate:
        left, right = st.columns(2)
        with left:
            st.markdown("##### Numeric: histogram and boxplot")
            if nums:
                variable = st.selectbox("Numeric variable", nums, key=f"{key}_numeric")
                values = data[variable].dropna()
                st.dataframe(values.describe().to_frame("Value").round(3), width="stretch")
                bins = min(30, max(5, int(np.sqrt(max(1, len(values))))))
                hist = px.histogram(
                    data, x=variable, nbins=bins, marginal="box", title=f"Histogram of {variable}",
                    labels={variable: variable, "count": "Count"}, template="plotly_white"
                )
                hist.update_layout(showlegend=False)
                st.plotly_chart(hist, use_container_width=True, key=f"{key}_histogram")
                box = px.box(data, y=variable, points="outliers", title=f"Boxplot of {variable}", template="plotly_white")
                st.plotly_chart(box, use_container_width=True, key=f"{key}_boxplot")
            else:
                st.info("No numeric variable is available in this dataset.")
        with right:
            st.markdown("##### Categorical: count or proportion bar chart")
            if cats:
                variable = st.selectbox("Categorical variable", cats, key=f"{key}_categorical")
                display = st.radio("Display", ["Counts", "Proportions"], horizontal=True, key=f"{key}_categorical_display")
                summary = data[variable].astype(str).fillna("Missing").value_counts(dropna=False).rename_axis(variable).reset_index(name="Count")
                if display == "Proportions":
                    summary["Value"] = summary["Count"] / summary["Count"].sum()
                    y_value, y_title = "Value", "Proportion"
                    text_template = "%{y:.1%}"
                else:
                    summary["Value"] = summary["Count"]
                    y_value, y_title = "Value", "Count"
                    text_template = "%{y:.0f}"
                bars = px.bar(
                    summary, x=variable, y=y_value, text=y_value, title=f"{display[:-1]} of {variable}",
                    labels={y_value: y_title}, template="plotly_white"
                )
                bars.update_traces(texttemplate=text_template, textposition="outside")
                bars.update_layout(showlegend=False)
                st.plotly_chart(bars, use_container_width=True, key=f"{key}_categorical_bar")
            else:
                st.info("No categorical variable is available in this dataset.")

    with grouped:
        st.markdown("##### Grouped boxplot: numeric outcome by categorical group")
        if nums and cats:
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_box_outcome")
            group = st.selectbox("Categorical grouping variable", cats, key=f"{key}_box_group")
            subset = data[[outcome, group]].dropna().copy()
            if subset.empty:
                st.warning("The selected variables have no complete pairs.")
            else:
                subset[group] = subset[group].astype(str)
                figure = px.box(
                    subset, x=group, y=outcome, points="outliers", color=group,
                    title=f"{outcome} by {group}", template="plotly_white"
                )
                figure.update_layout(showlegend=False)
                st.plotly_chart(figure, use_container_width=True, key=f"{key}_group_boxplot")
                st.caption("A boxplot is meaningful here because the x-axis is categorical and the plotted response is numeric.")
        else:
            st.info("A grouped boxplot requires both a numeric outcome and a categorical grouping variable.")

    with association:
        st.markdown("##### Association display: two categorical variables")
        if len(cats) >= 2:
            first = st.selectbox("First categorical variable", cats, key=f"{key}_first_category")
            second = st.selectbox("Second categorical variable", [item for item in cats if item != first], key=f"{key}_second_category")
            table = pd.crosstab(data[first].astype(str).fillna("Missing"), data[second].astype(str).fillna("Missing"))
            st.dataframe(table, width="stretch")
            heatmap = px.imshow(
                table, text_auto=True, aspect="auto", color_continuous_scale="Blues",
                title=f"Counts: {first} by {second}", labels={"x": second, "y": first, "color": "Count"}
            )
            st.plotly_chart(heatmap, use_container_width=True, key=f"{key}_categorical_heatmap")
        else:
            st.info("A two-categorical association display requires at least two categorical variables.")

    with static:
        st.markdown("##### Seaborn / Matplotlib static teaching figure")
        st.caption("Use this fixed-style figure for slides, handouts, or discussion; use the Plotly charts above for interactive exploration.")
        if nums:
            variable = st.selectbox("Numeric variable for static figure", nums, key=f"{key}_static_numeric")
            group_options = ["No grouping"] + cats
            group = st.selectbox("Optional categorical grouping", group_options, key=f"{key}_static_group")
            figure, axis = plt.subplots(figsize=(8, 4.5))
            if group == "No grouping":
                sns.histplot(data=data, x=variable, bins="auto", kde=True, color="#2C7FB8", ax=axis)
                axis.set_title(f"Static distribution of {variable}")
            else:
                subset = data[[variable, group]].dropna().copy()
                subset[group] = subset[group].astype(str)
                sns.boxplot(data=subset, x=group, y=variable, hue=group, legend=False, ax=axis, color="#7FCDBB")
                sns.stripplot(data=subset, x=group, y=variable, color="#253494", alpha=0.5, ax=axis)
                axis.set_title(f"Static boxplot: {variable} by {group}")
                axis.tick_params(axis="x", rotation=30)
            st.pyplot(figure, clear_figure=True, use_container_width=True)
        else:
            st.info("A static numerical teaching figure requires a numeric variable.")


def render_analysis(data: pd.DataFrame, key: str) -> None:
    """No-code analyses that activate only when the selected data support them."""
    st.markdown("##### No-code analysis")
    method = st.selectbox(
        "Choose an analysis",
        ["Descriptive summary", "Bootstrap interval for a mean", "Two-group comparison", "Simple linear regression"],
        key=f"{key}_method",
    )
    nums, cats = numerical(data), categorical(data)
    if method == "Descriptive summary":
        if nums:
            st.dataframe(data[nums].describe().T.round(3), width="stretch")
        else:
            st.info("No numeric summary is available for this dataset.")
        return
    if method == "Bootstrap interval for a mean":
        if not nums:
            st.warning("Choose a dataset with a numeric variable for this analysis.")
            return
        variable = st.selectbox("Variable", nums, key=f"{key}_boot_variable")
        values = data[variable].dropna().to_numpy(dtype=float)
        if len(values) < 2:
            st.warning("At least two non-missing observations are required.")
            return
        repetitions = st.slider("Bootstrap repetitions", 500, 5000, 1000, step=500, key=f"{key}_boot_reps")
        rng = np.random.default_rng(2026)
        indices = rng.integers(0, len(values), size=(repetitions, len(values)))
        means = values[indices].mean(axis=1)
        low, high = np.quantile(means, [0.025, 0.975])
        x, y, z = st.columns(3)
        x.metric("Observed mean", f"{values.mean():.3f}")
        y.metric("Bootstrap SE", f"{np.std(means, ddof=1):.3f}")
        z.metric("95% interval", f"[{low:.3f}, {high:.3f}]")
        return
    if method == "Two-group comparison":
        if not nums or not cats:
            st.warning("Choose a dataset with a numeric outcome and a categorical grouping variable.")
            return
        outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_group_outcome")
        group = st.selectbox("Grouping variable", cats, key=f"{key}_group_variable")
        subset = data[[outcome, group]].dropna().copy()
        levels = sorted(subset[group].astype(str).unique().tolist())
        if len(levels) < 2:
            st.warning("The selected grouping variable has fewer than two levels.")
            return
        selected = st.multiselect("Choose two groups", levels, default=levels[:2], max_selections=2, key=f"{key}_group_levels")
        if len(selected) != 2:
            st.info("Select exactly two groups.")
            return
        first = subset.loc[subset[group].astype(str) == selected[0], outcome].to_numpy(dtype=float)
        second = subset.loc[subset[group].astype(str) == selected[1], outcome].to_numpy(dtype=float)
        if len(first) < 2 or len(second) < 2:
            st.warning("Each group requires at least two observations.")
            return
        result = stats.ttest_ind(first, second, equal_var=False)
        a, b, c = st.columns(3)
        a.metric("Mean difference", f"{second.mean() - first.mean():.3f}")
        b.metric("Welch p-value", f"{result.pvalue:.4f}")
        c.metric("Group sizes", f"{len(first)} / {len(second)}")
        return
    if len(nums) < 2:
        st.warning("Choose a dataset with two numeric variables for simple linear regression.")
        return
    outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_reg_outcome")
    predictor = st.selectbox("Numeric predictor", [name for name in nums if name != outcome], key=f"{key}_reg_predictor")
    subset = data[[outcome, predictor]].dropna()
    if len(subset) < 3:
        st.warning("At least three complete observations are required.")
        return
    result = stats.linregress(subset[predictor], subset[outcome])
    a, b, c = st.columns(3)
    a.metric("Slope", f"{result.slope:.4f}")
    b.metric("p-value", f"{result.pvalue:.4f}")
    c.metric("R²", f"{result.rvalue ** 2:.3f}")
    st.scatter_chart(subset, x=predictor, y=outcome)


def render_dataset_workspace(data: pd.DataFrame, key: str) -> None:
    render_profile(data, key)
    render_analysis(data, key)


def render_module(module: dict, manifest: dict) -> None:
    module_id = module["id"].upper()
    demonstration = module["demonstration"]
    with st.expander(f"**{module_id} — {module['title']}**", expanded=False):
        st.markdown("#### Theory")
        st.write(module["presentation_focus"])
        st.markdown("**Formal notation.** " + module["notation"])
        st.markdown("**Results to state.** " + " ".join(module["results"]))
        st.markdown("---")
        st.markdown("#### 📋 Worked-out public dataset")
        st.success(f"**{demonstration['name']}** — {demonstration['activity']}")
        st.caption(f"Selected public file: `{demonstration['file']}`")
        if st.checkbox("Open the worked dataset analysis", key=f"{module['id']}_open_worked"):
            worked_data = load_public_data(demonstration["file"])
            render_dataset_workspace(worked_data, f"{module['id']}_worked")
            st.download_button(
                "Download the worked dataset as CSV",
                worked_data.to_csv(index=False).encode("utf-8"),
                demonstration["file"],
                "text/csv",
                key=f"{module['id']}_download_worked",
            )
        st.markdown("---")
        st.markdown("#### 🔬 BYOD — upload your own dataset")
        st.write(module["upload_guidance"])
        uploaded_file = st.file_uploader(
            "Upload a CSV dataset for this module",
            type=["csv"],
            key=f"{module['id']}_upload",
        )
        uploaded = read_upload(uploaded_file)
        if uploaded is None:
            st.caption("Upload processing is in memory only for this browser session.")
        else:
            st.caption("Participant-uploaded dataset — processed in session memory only.")
            render_dataset_workspace(uploaded, f"{module['id']}_upload")
        st.markdown("---")
        with st.expander("Process another available public dataset"):
            labels = public_dataset_labels(manifest)
            filename = st.selectbox(
                "Available public dataset",
                sorted(labels),
                format_func=lambda item: f"{labels[item]} ({item})",
                key=f"{module['id']}_public_file",
            )
            if st.checkbox("Open this public dataset", key=f"{module['id']}_open_public"):
                render_dataset_workspace(load_public_data(filename), f"{module['id']}_public")


def render_day(day_id: str) -> None:
    manifest = load_manifest()
    day = next(item for item in manifest["days"] if item["id"] == day_id)
    render_sidebar()
    st.title(day["title"])
    st.caption("No-Code Statistical Inference · 3-hour seminar day")
    st.markdown("---")
    st.header("📘 Theory")
    st.subheader(day["general_theme"])
    st.info(day["introduction"])
    st.markdown(
        "Each module below begins with theory, continues with a selected public worked dataset, "
        "and provides a participant CSV-upload BYOD workflow."
    )
    st.markdown("---")
    st.header("📋 Modules")
    for module in day["modules"]:
        render_module(module, manifest)
    st.markdown("---")
    st.caption(f"{day['title']} · No-Code Statistical Inference · © 2026 Moses Boudourides")
