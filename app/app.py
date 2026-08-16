"""Day-first Streamlit companion app for No-Code Statistical Inference."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import streamlit as st
from scipy import stats

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data" / "public"
MANIFEST_PATH = PROJECT_DIR / "data" / "module_manifest.json"

st.set_page_config(
    page_title="No-Code Statistical Inference",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_public_data(filename: str) -> pd.DataFrame:
    """Read a bundled public dataset and remove archive-only row labels."""
    data = pd.read_csv(DATA_DIR / filename)
    return data.drop(columns="rownames", errors="ignore")


def read_uploaded_csv(uploaded_file) -> pd.DataFrame | None:
    """Read a participant CSV in memory only; never write the upload to disk."""
    if uploaded_file is None:
        return None
    try:
        data = pd.read_csv(uploaded_file)
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"The uploaded file could not be read as a CSV: {error}")
        return None
    return data.drop(columns="rownames", errors="ignore")


def day_lookup(manifest: dict) -> dict[str, dict]:
    return {day["id"]: day for day in manifest["days"]}


def public_dataset_labels(manifest: dict) -> dict[str, str]:
    """Return a label for every bundled CSV, including files not assigned to a module."""
    labels: dict[str, str] = {}
    for day in manifest["days"]:
        for module in day["modules"]:
            labels[module["demonstration"]["file"]] = module["demonstration"]["name"]
            for item in module["byod"]:
                labels[item["file"]] = item["name"]
    for path in DATA_DIR.glob("*.csv"):
        labels.setdefault(path.name, path.stem.replace("_", " ").title())
    return labels


def numeric_columns(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=np.number).columns.tolist()


def categorical_columns(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(exclude=np.number).columns.tolist()


def encode_binary(series: pd.Series) -> tuple[pd.Series, list[str]] | None:
    levels = sorted(series.dropna().astype(str).unique().tolist())
    if len(levels) != 2:
        return None
    encoded = series.dropna().astype(str).map({levels[0]: 0, levels[1]: 1}).astype(float)
    return encoded, levels


def render_dataset_profile(data: pd.DataFrame, key_prefix: str) -> None:
    """Show a safe, generic first look for any public or uploaded tabular data."""
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Rows", f"{len(data):,}")
    metric_b.metric("Columns", len(data.columns))
    metric_c.metric("Complete rows", f"{len(data.dropna()):,}")
    st.dataframe(data.head(20), width="stretch")

    numeric = numeric_columns(data)
    categorical = categorical_columns(data)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Numeric profile")
        if numeric:
            variable = st.selectbox("Numeric variable", numeric, key=f"{key_prefix}_profile_numeric")
            values = data[variable].dropna()
            st.dataframe(values.describe().to_frame("Value").round(3), width="stretch")
            bins = min(30, max(5, int(np.sqrt(max(len(values), 1)))))
            st.bar_chart(np.histogram(values, bins=bins)[0])
        else:
            st.info("No numeric variables are available after import.")
    with right:
        st.markdown("#### Categorical profile")
        if categorical:
            variable = st.selectbox("Categorical variable", categorical, key=f"{key_prefix}_profile_categorical")
            counts = data[variable].astype(str).value_counts(dropna=False)
            st.dataframe(counts.rename("Count").to_frame(), width="stretch")
            st.bar_chart(counts)
        else:
            st.info("No categorical variables are available after import.")

    if len(numeric) >= 2:
        st.markdown("#### Relationship explorer")
        x_name = st.selectbox("Horizontal variable", numeric, key=f"{key_prefix}_profile_x")
        y_name = st.selectbox("Vertical variable", [name for name in numeric if name != x_name], key=f"{key_prefix}_profile_y")
        st.scatter_chart(data[[x_name, y_name]].dropna(), x=x_name, y=y_name)


def render_bootstrap_mean(data: pd.DataFrame, key_prefix: str) -> None:
    numeric = numeric_columns(data)
    if not numeric:
        st.warning("A bootstrap mean interval requires a numeric variable.")
        return
    variable = st.selectbox("Variable", numeric, key=f"{key_prefix}_bootstrap_variable")
    repetitions = st.slider("Bootstrap repetitions", 500, 10_000, 2_000, 500, key=f"{key_prefix}_bootstrap_repetitions")
    seed = st.number_input("Random seed", 0, value=2026, key=f"{key_prefix}_bootstrap_seed")
    values = data[variable].dropna().to_numpy(dtype=float)
    if len(values) < 2:
        st.warning("At least two non-missing values are required.")
        return
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    bootstrap_means = values[indices].mean(axis=1)
    interval = np.quantile(bootstrap_means, [0.025, 0.975])
    left, middle, right = st.columns(3)
    left.metric("Observed mean", f"{values.mean():.3f}")
    middle.metric("Bootstrap SE", f"{np.std(bootstrap_means, ddof=1):.3f}")
    right.metric("95% percentile interval", f"[{interval[0]:.3f}, {interval[1]:.3f}]")
    st.bar_chart(np.histogram(bootstrap_means, bins=30)[0])
    st.caption("This resampling interval quantifies sampling variation under the empirical-distribution approximation; it does not correct a biased design or an ill-defined target population.")


def render_two_group(data: pd.DataFrame, key_prefix: str) -> None:
    numeric = numeric_columns(data)
    categorical = categorical_columns(data)
    if not numeric or not categorical:
        st.warning("A two-group comparison needs one numeric outcome and one categorical grouping variable.")
        return
    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Numeric outcome", numeric, key=f"{key_prefix}_two_group_outcome")
    with right:
        group = st.selectbox("Grouping variable", categorical, key=f"{key_prefix}_two_group_group")
    subset = data[[outcome, group]].dropna().copy()
    levels = sorted(subset[group].astype(str).unique().tolist())
    if len(levels) < 2:
        st.warning("The selected grouping variable has fewer than two observed levels.")
        return
    selected = st.multiselect("Choose exactly two groups", levels, default=levels[:2], max_selections=2, key=f"{key_prefix}_two_group_levels")
    if len(selected) != 2:
        st.info("Choose two groups to calculate the comparison.")
        return
    group_a = subset.loc[subset[group].astype(str) == selected[0], outcome].to_numpy(dtype=float)
    group_b = subset.loc[subset[group].astype(str) == selected[1], outcome].to_numpy(dtype=float)
    if len(group_a) < 2 or len(group_b) < 2:
        st.warning("Each group needs at least two non-missing observations.")
        return
    result = stats.ttest_ind(group_a, group_b, equal_var=False)
    diff = float(group_b.mean() - group_a.mean())
    var_a, var_b = np.var(group_a, ddof=1), np.var(group_b, ddof=1)
    se = np.sqrt(var_a / len(group_a) + var_b / len(group_b))
    df = (var_a / len(group_a) + var_b / len(group_b)) ** 2 / (
        (var_a / len(group_a)) ** 2 / (len(group_a) - 1) + (var_b / len(group_b)) ** 2 / (len(group_b) - 1)
    )
    critical = stats.t.ppf(0.975, df)
    interval = (diff - critical * se, diff + critical * se)
    pooled = np.sqrt(((len(group_a) - 1) * var_a + (len(group_b) - 1) * var_b) / (len(group_a) + len(group_b) - 2))
    d_value = diff / pooled if pooled > 0 else np.nan
    a, b, c, d = st.columns(4)
    a.metric("Mean difference", f"{diff:.3f}")
    b.metric("95% CI", f"[{interval[0]:.3f}, {interval[1]:.3f}]")
    c.metric("Welch p-value", f"{result.pvalue:.4f}")
    d.metric("Cohen's d", f"{d_value:.3f}")


def render_chi_square(data: pd.DataFrame, key_prefix: str) -> None:
    categorical = categorical_columns(data)
    if len(categorical) < 2:
        st.warning("A categorical association analysis needs two categorical variables.")
        return
    left, right = st.columns(2)
    with left:
        x_name = st.selectbox("Row variable", categorical, key=f"{key_prefix}_chi_x")
    with right:
        y_name = st.selectbox("Column variable", [name for name in categorical if name != x_name], key=f"{key_prefix}_chi_y")
    if "Freq" in data.columns and pd.api.types.is_numeric_dtype(data["Freq"]):
        table = pd.pivot_table(data, index=x_name, columns=y_name, values="Freq", aggfunc="sum", fill_value=0)
        st.caption("The dataset has an explicit frequency column; it is used as the contingency-table count.")
    else:
        table = pd.crosstab(data[x_name], data[y_name], dropna=False)
    if table.shape[0] < 2 or table.shape[1] < 2:
        st.warning("Both selected variables need at least two observed levels.")
        return
    chi_square, p_value, degrees_freedom, expected = stats.chi2_contingency(table)
    a, b, c = st.columns(3)
    a.metric("Chi-square statistic", f"{chi_square:.3f}")
    b.metric("Degrees of freedom", int(degrees_freedom))
    c.metric("p-value", f"{p_value:.4f}")
    st.markdown("#### Observed counts")
    st.dataframe(table, width="stretch")
    st.markdown("#### Expected counts under independence")
    st.dataframe(pd.DataFrame(expected, index=table.index, columns=table.columns).round(2), width="stretch")


def render_linear_regression(data: pd.DataFrame, key_prefix: str) -> None:
    numeric = numeric_columns(data)
    if len(numeric) < 2:
        st.warning("Simple linear regression requires two numeric variables.")
        return
    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Numeric outcome", numeric, key=f"{key_prefix}_linear_outcome")
    with right:
        predictor = st.selectbox("Numeric predictor", [name for name in numeric if name != outcome], key=f"{key_prefix}_linear_predictor")
    subset = data[[outcome, predictor]].dropna()
    if len(subset) < 3:
        st.warning("At least three complete observations are required.")
        return
    fit = stats.linregress(subset[predictor], subset[outcome])
    df = len(subset) - 2
    critical = stats.t.ppf(0.975, df)
    interval = (fit.slope - critical * fit.stderr, fit.slope + critical * fit.stderr)
    a, b, c, d = st.columns(4)
    a.metric("Slope", f"{fit.slope:.4f}")
    b.metric("95% slope CI", f"[{interval[0]:.4f}, {interval[1]:.4f}]")
    c.metric("p-value", f"{fit.pvalue:.4f}")
    d.metric("R²", f"{fit.rvalue ** 2:.3f}")
    st.scatter_chart(subset, x=predictor, y=outcome)


def render_logistic_regression(data: pd.DataFrame, key_prefix: str) -> None:
    numeric = numeric_columns(data)
    categorical = categorical_columns(data)
    if not numeric or not categorical:
        st.warning("This starter logistic workflow requires a binary categorical outcome and a numeric predictor.")
        return
    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Binary outcome", categorical, key=f"{key_prefix}_logistic_outcome")
    with right:
        predictor = st.selectbox("Numeric predictor", numeric, key=f"{key_prefix}_logistic_predictor")
    subset = data[[outcome, predictor]].dropna().copy()
    encoded_info = encode_binary(subset[outcome])
    if encoded_info is None:
        st.warning("Choose an outcome with exactly two observed levels.")
        return
    encoded, levels = encoded_info
    subset = subset.loc[encoded.index]
    try:
        model = sm.Logit(encoded, sm.add_constant(subset[[predictor]].astype(float))).fit(disp=False)
    except (ValueError, np.linalg.LinAlgError) as error:
        st.error(f"The logistic model could not be fitted: {error}")
        return
    coefficient = float(model.params[predictor])
    confidence = model.conf_int().loc[predictor]
    a, b, c, d = st.columns(4)
    a.metric("Log-odds coefficient", f"{coefficient:.4f}")
    b.metric("95% coefficient CI", f"[{confidence.iloc[0]:.4f}, {confidence.iloc[1]:.4f}]")
    c.metric("Odds ratio", f"{np.exp(coefficient):.3f}")
    d.metric("p-value", f"{model.pvalues[predictor]:.4f}")
    grid = pd.DataFrame({predictor: np.linspace(subset[predictor].min(), subset[predictor].max(), 100)})
    grid["Predicted probability"] = model.predict(sm.add_constant(grid, has_constant="add"))
    st.line_chart(grid, x=predictor, y="Predicted probability")
    st.caption(f"The outcome is coded as 1 for **{levels[1]}** and 0 for **{levels[0]}**.")


def render_analysis(data: pd.DataFrame, key_prefix: str) -> None:
    """Run one of the generic no-code workflows on any compatible tabular dataset."""
    st.markdown("### No-code analysis")
    method = st.selectbox(
        "Choose an analysis",
        ["Descriptive profile", "Bootstrap interval for a mean", "Two-group comparison", "Categorical association", "Simple linear regression", "Logistic regression"],
        key=f"{key_prefix}_method",
    )
    if method == "Descriptive profile":
        numeric = numeric_columns(data)
        if numeric:
            st.dataframe(data[numeric].describe().T.round(3), width="stretch")
        else:
            st.info("No numeric variables are available for a descriptive numeric profile.")
    elif method == "Bootstrap interval for a mean":
        render_bootstrap_mean(data, key_prefix)
    elif method == "Two-group comparison":
        render_two_group(data, key_prefix)
    elif method == "Categorical association":
        render_chi_square(data, key_prefix)
    elif method == "Simple linear regression":
        render_linear_regression(data, key_prefix)
    else:
        render_logistic_regression(data, key_prefix)


def render_worked_example(module: dict, manifest: dict) -> None:
    """Render the module's instructor-selected public dataset and generic workbench."""
    demonstration = module["demonstration"]
    st.subheader(f"Worked-out example: {demonstration['name']}")
    st.success(demonstration["activity"])
    st.caption(f"This is the selected public worked dataset for **{module['id'].upper()}**: `{demonstration['file']}`.")
    data = load_public_data(demonstration["file"])
    render_dataset_profile(data, f"{module['id']}_worked_profile")
    render_analysis(data, f"{module['id']}_worked")
    st.download_button(
        "Download this worked dataset as CSV",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name=demonstration["file"],
        mime="text/csv",
        key=f"{module['id']}_worked_download",
    )

    labels = public_dataset_labels(manifest)
    with st.expander("Process another available public dataset"):
        st.write("All public datasets bundled with the seminar use this same processing workbench.")
        filename = st.selectbox(
            "Available public dataset",
            options=sorted(labels),
            format_func=lambda item: f"{labels[item]} ({item})",
            key=f"{module['id']}_alternative_public",
        )
        alternative = load_public_data(filename)
        st.caption(f"Selected public dataset: `{filename}`")
        render_dataset_profile(alternative, f"{module['id']}_alternative_profile")
        render_analysis(alternative, f"{module['id']}_alternative")


def render_byod_upload(module: dict) -> None:
    """Provide a dedicated module BYOD upload and generic processor."""
    st.subheader(f"BYOD upload: {module['id'].upper()}")
    st.write(module["upload_guidance"])
    uploaded_file = st.file_uploader(
        "Upload a CSV dataset for this module",
        type=["csv"],
        key=f"{module['id']}_upload",
    )
    data = read_uploaded_csv(uploaded_file)
    if data is None:
        st.info("Your file is processed only in memory for the current session. Upload a CSV to begin.")
        return
    st.caption("Participant-uploaded dataset — in-memory session processing only")
    render_dataset_profile(data, f"{module['id']}_upload_profile")
    render_analysis(data, f"{module['id']}_upload")
    st.download_button(
        "Download the uploaded dataset as CSV",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="byod_dataset.csv",
        mime="text/csv",
        key=f"{module['id']}_upload_download",
    )


def render_module(module: dict, manifest: dict) -> None:
    st.title(f"{module['id'].upper()} — {module['title']}")
    theory_tab, example_tab, byod_tab = st.tabs(["Module theory", "Worked-out public dataset", "BYOD upload"])
    with theory_tab:
        st.subheader("Theory")
        st.write(module["presentation_focus"])
        st.markdown("#### Formal notation")
        st.info(module["notation"])
        st.markdown("#### Results to state and interpret")
        for result in module["results"]:
            st.markdown(f"- {result}")
        st.markdown("#### Module data workflow")
        st.write(
            "First review the theory. Then inspect the instructor's worked public example. "
            "Finally, upload a BYOD CSV and apply a compatible no-code analysis to your own variables."
        )
    with example_tab:
        render_worked_example(module, manifest)
    with byod_tab:
        render_byod_upload(module)


def render_day_theory(day: dict) -> None:
    st.title(day["title"])
    st.subheader(day.get("general_theme", "General day theory"))
    st.info(day["introduction"])
    st.markdown("### Day theory")
    st.write(
        "The day introduction defines the overarching inferential logic. Each subsequent module "
        "adds one formal concept, demonstrates it with a selected public dataset, and gives participants a dedicated BYOD upload route."
    )
    rows = [
        {
            "Module": module["id"].upper(),
            "Title": module["title"],
            "Worked-out public dataset": module["demonstration"]["name"],
            "BYOD": "Participant CSV upload",
        }
        for module in day["modules"]
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_home(manifest: dict) -> None:
    st.title(manifest["title"])
    st.subheader("A day-first, theory-led no-code statistical inference app")
    st.write(
        "Select **Day 1**, **Day 2**, or **Day 3** in the sidebar. Begin with the day theory, "
        "then select one of that day's ten modules. Each module contains its own theory, an "
        "instructor worked-out public dataset, and a participant BYOD CSV upload workflow."
    )
    records = [
        {
            "Day": day["title"],
            "General day theme": day.get("general_theme", ""),
            "Modules": len(day["modules"]),
            "BYOD workflow": "CSV upload in every module",
        }
        for day in manifest["days"]
    ]
    st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)


manifest = load_manifest()
days = day_lookup(manifest)

with st.sidebar:
    st.title("Seminar structure")
    selected_day_id = st.radio(
        "Select a day",
        options=list(days),
        format_func=lambda item: days[item]["title"],
    )
    selected_day = days[selected_day_id]
    st.divider()
    selected_view = st.radio("Within this day", ["Day theory", "Modules"])
    selected_module = None
    if selected_view == "Modules":
        selected_module_id = st.selectbox(
            "Select one of the ten modules",
            options=[module["id"] for module in selected_day["modules"]],
            format_func=lambda item: next(module["title"] for module in selected_day["modules"] if module["id"] == item),
        )
        selected_module = next(module for module in selected_day["modules"] if module["id"] == selected_module_id)
    st.divider()
    st.caption("Day theory → module theory → worked public dataset → BYOD upload")

if selected_view == "Day theory":
    render_day_theory(selected_day)
else:
    render_module(selected_module, manifest)
