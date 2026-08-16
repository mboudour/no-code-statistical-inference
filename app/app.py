"""Module-driven Streamlit companion app for No-Code Statistical Inference."""

from __future__ import annotations

import json
import sys
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
sys.path.insert(0, str(APP_DIR))

st.set_page_config(
    page_title="No-Code Statistical Inference",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_manifest() -> dict:
    """Load the locally vendored curriculum and dataset manifest."""
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_local_data(filename: str) -> pd.DataFrame:
    """Load a public teaching dataset bundled with the repository."""
    data = pd.read_csv(DATA_DIR / filename)
    if "rownames" in data.columns:
        data = data.drop(columns="rownames")
    return data


def read_uploaded_csv(uploaded_file) -> pd.DataFrame | None:
    """Read a participant CSV in memory without persisting the upload."""
    if uploaded_file is None:
        return None
    try:
        data = pd.read_csv(uploaded_file)
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"The uploaded file could not be read as a CSV: {error}")
        return None
    if "rownames" in data.columns:
        data = data.drop(columns="rownames")
    return data


def module_lookup(manifest: dict) -> dict[str, dict]:
    """Return each module keyed by its stable identifier."""
    return {
        module["id"]: {**module, "day_id": day["id"], "day_title": day["title"], "day_intro": day["introduction"]}
        for day in manifest["days"]
        for module in day["modules"]
    }


def dataset_lookup(manifest: dict) -> dict[str, str]:
    """Return a readable name for each locally packaged dataset file."""
    lookup: dict[str, str] = {}
    for module in module_lookup(manifest).values():
        lookup[module["worked_example"]["file"]] = module["worked_example"]["name"]
        for dataset in module["byod"]:
            lookup[dataset["file"]] = dataset["name"]
    return lookup


def numerical_columns(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=np.number).columns.tolist()


def categorical_columns(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(exclude=np.number).columns.tolist()


def coerce_binary(series: pd.Series) -> tuple[pd.Series, list[str]] | None:
    """Encode a two-level response for a logistic model."""
    values = series.dropna().astype(str)
    levels = sorted(values.unique().tolist())
    if len(levels) != 2:
        return None
    encoded = values.map({levels[0]: 0, levels[1]: 1}).astype(float)
    return encoded, levels


def render_day_and_module(manifest: dict) -> dict:
    """Render a presentation-first curriculum view and return the active module."""
    st.title("Curriculum and Rigorous Presentation")
    st.write(
        "Every **day** opens with an introduction, and every **module** begins with a "
        "formal presentation of the concepts, notation, assumptions, and results used in "
        "the activity. Proofs are intentionally outside the seminar's scope."
    )

    day_options = {day["id"]: day for day in manifest["days"]}
    selected_day_id = st.selectbox(
        "Select a seminar day",
        options=list(day_options),
        format_func=lambda day_id: day_options[day_id]["title"],
    )
    day = day_options[selected_day_id]
    st.subheader(day["title"])
    st.info(day["introduction"])

    module_options = {module["id"]: module for module in day["modules"]}
    selected_module_id = st.selectbox(
        "Select a module",
        options=list(module_options),
        format_func=lambda module_id: module_options[module_id]["title"],
    )
    module = module_options[selected_module_id]

    st.markdown("### Module introduction and presentation")
    st.write(module["presentation_focus"])
    st.markdown("#### Formal notation")
    st.info(module["notation"])
    st.markdown("#### Results to be stated and interpreted")
    for result in module["results"]:
        st.markdown(f"- {result}")

    st.markdown("### Worked example")
    worked = module["worked_example"]
    st.success(f"**{worked['name']}** — {worked['activity']}")

    st.markdown("### BYOD dataset choices for this module")
    choices = pd.DataFrame(module["byod"])
    choices.columns = ["Local file", "Public dataset"]
    st.dataframe(choices, width="stretch", hide_index=True)
    st.caption(
        "The listed datasets are public and bundled locally with the app. No API key or "
        "live external data request is required to use them."
    )
    return module


def choose_data(manifest: dict, label_prefix: str) -> tuple[pd.DataFrame | None, str, str]:
    """Provide a safe choice among bundled examples and an in-memory CSV upload."""
    names = dataset_lookup(manifest)
    source = st.radio(
        "Data source",
        ["Module worked example", "Module BYOD choice", "Upload a CSV"],
        horizontal=True,
        key=f"{label_prefix}_source",
    )
    module_map = module_lookup(manifest)
    current_module_id = st.session_state.get("last_module")
    current_module = module_map.get(current_module_id) if current_module_id else None

    if source == "Upload a CSV":
        uploaded_file = st.file_uploader("Upload a comma-separated values (CSV) file", type=["csv"], key=f"{label_prefix}_upload")
        data = read_uploaded_csv(uploaded_file)
        return data, "Participant upload", "Uploaded CSV held in memory for this session"

    if current_module is None:
        current_module = next(iter(module_map.values()))

    if source == "Module worked example":
        filename = current_module["worked_example"]["file"]
        return load_local_data(filename), current_module["worked_example"]["name"], f"Bundled public dataset: {filename}"

    byod_options = {entry["file"]: entry["name"] for entry in current_module["byod"]}
    filename = st.selectbox(
        "Select a public BYOD dataset for the active module",
        options=list(byod_options),
        format_func=lambda item: f"{byod_options[item]} ({item})",
        key=f"{label_prefix}_byod_file",
    )
    return load_local_data(filename), names[filename], f"Bundled public dataset: {filename}"


def render_data_explorer(manifest: dict) -> None:
    st.title("Dataset Explorer")
    st.write(
        "Use the active module's worked example or one of its 3–5 public BYOD datasets. "
        "The app keeps the data experience no-code while showing the decisions needed for sound inference."
    )
    data, dataset_name, provenance = choose_data(manifest, "explorer")
    if data is None:
        st.info("Upload a CSV to begin exploring your own data.")
        return

    st.subheader(dataset_name)
    st.caption(provenance)
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Rows", f"{len(data):,}")
    metric_b.metric("Columns", len(data.columns))
    metric_c.metric("Complete rows", f"{len(data.dropna()):,}")
    st.dataframe(data.head(20), width="stretch")

    numeric = numerical_columns(data)
    categorical = categorical_columns(data)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Numeric profile")
        if numeric:
            selected_numeric = st.selectbox("Numeric variable", numeric, key="explorer_numeric")
            values = data[selected_numeric].dropna()
            st.dataframe(values.describe().to_frame("Value").round(3), width="stretch")
            chart_data = pd.DataFrame({selected_numeric: values})
            bin_count = min(30, max(5, int(np.sqrt(len(values)))))
            histogram_counts = np.histogram(chart_data[selected_numeric], bins=bin_count)[0]
            st.bar_chart(histogram_counts)
        else:
            st.info("This dataset has no numeric columns after import.")
    with right:
        st.markdown("#### Categorical profile")
        if categorical:
            selected_categorical = st.selectbox("Categorical variable", categorical, key="explorer_categorical")
            counts = data[selected_categorical].astype(str).value_counts(dropna=False)
            st.dataframe(counts.rename("Count").to_frame(), width="stretch")
            st.bar_chart(counts)
        else:
            st.info("This dataset has no categorical columns after import.")

    if len(numeric) >= 2:
        st.markdown("#### Relationship explorer")
        x_value = st.selectbox("Horizontal variable", numeric, key="explorer_x")
        y_value = st.selectbox("Vertical variable", [item for item in numeric if item != x_value], key="explorer_y")
        st.scatter_chart(data[[x_value, y_value]].dropna(), x=x_value, y=y_value)


def render_bootstrap(data: pd.DataFrame) -> None:
    numeric = numerical_columns(data)
    if not numeric:
        st.warning("Bootstrap inference requires a numeric variable.")
        return
    variable = st.selectbox("Variable", numeric, key="bootstrap_variable")
    repetitions = st.slider("Bootstrap repetitions", 500, 10_000, 2_000, step=500)
    seed = st.number_input("Random seed", min_value=0, value=2026, step=1, key="bootstrap_seed")
    values = data[variable].dropna().to_numpy(dtype=float)
    if len(values) < 2:
        st.warning("At least two non-missing values are required.")
        return
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    boot_means = values[indices].mean(axis=1)
    lower, upper = np.quantile(boot_means, [0.025, 0.975])
    se = np.std(boot_means, ddof=1)
    a, b, c = st.columns(3)
    a.metric("Observed mean", f"{np.mean(values):.3f}")
    b.metric("Bootstrap SE", f"{se:.3f}")
    c.metric("95% percentile interval", f"[{lower:.3f}, {upper:.3f}]")
    st.bar_chart(np.histogram(boot_means, bins=30)[0])
    st.caption(
        "This interval quantifies resampling variation under the empirical-distribution approximation. It does not address selection bias, measurement error, or a poorly specified target population."
    )


def render_two_group(data: pd.DataFrame) -> None:
    numeric = numerical_columns(data)
    categorical = categorical_columns(data)
    if not numeric or not categorical:
        st.warning("A two-group comparison requires a numeric outcome and a categorical grouping variable.")
        return
    outcome, group = st.columns(2)
    with outcome:
        outcome_name = st.selectbox("Numeric outcome", numeric, key="two_group_outcome")
    with group:
        group_name = st.selectbox("Grouping variable", categorical, key="two_group_group")
    subset = data[[outcome_name, group_name]].dropna().copy()
    levels = sorted(subset[group_name].astype(str).unique().tolist())
    if len(levels) < 2:
        st.warning("The selected grouping variable has fewer than two observed levels.")
        return
    selected_levels = st.multiselect(
        "Choose exactly two groups", levels, default=levels[:2], max_selections=2, key="two_group_levels"
    )
    if len(selected_levels) != 2:
        st.info("Choose two groups to calculate the comparison.")
        return
    group_a = subset.loc[subset[group_name].astype(str) == selected_levels[0], outcome_name].to_numpy(dtype=float)
    group_b = subset.loc[subset[group_name].astype(str) == selected_levels[1], outcome_name].to_numpy(dtype=float)
    if len(group_a) < 2 or len(group_b) < 2:
        st.warning("Each group requires at least two non-missing observations.")
        return
    test = stats.ttest_ind(group_a, group_b, equal_var=False)
    difference = np.mean(group_b) - np.mean(group_a)
    variance_a, variance_b = np.var(group_a, ddof=1), np.var(group_b, ddof=1)
    se = np.sqrt(variance_a / len(group_a) + variance_b / len(group_b))
    degrees_freedom = (variance_a / len(group_a) + variance_b / len(group_b)) ** 2 / (
        (variance_a / len(group_a)) ** 2 / (len(group_a) - 1) + (variance_b / len(group_b)) ** 2 / (len(group_b) - 1)
    )
    critical = stats.t.ppf(0.975, degrees_freedom)
    ci = (difference - critical * se, difference + critical * se)
    pooled_sd = np.sqrt(((len(group_a) - 1) * variance_a + (len(group_b) - 1) * variance_b) / (len(group_a) + len(group_b) - 2))
    d_value = difference / pooled_sd if pooled_sd > 0 else np.nan
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mean difference", f"{difference:.3f}")
    m2.metric("95% CI", f"[{ci[0]:.3f}, {ci[1]:.3f}]")
    m3.metric("Welch p-value", f"{test.pvalue:.4f}")
    m4.metric("Cohen's d", f"{d_value:.3f}")
    summary = pd.DataFrame(
        {"Group": selected_levels, "n": [len(group_a), len(group_b)], "Mean": [np.mean(group_a), np.mean(group_b)], "SD": [np.std(group_a, ddof=1), np.std(group_b, ddof=1)]}
    )
    st.dataframe(summary.round(3), width="stretch", hide_index=True)


def render_chi_square(data: pd.DataFrame) -> None:
    categorical = categorical_columns(data)
    if len(categorical) < 2:
        st.warning("A chi-square association analysis requires two categorical variables.")
        return
    first, second = st.columns(2)
    with first:
        x_name = st.selectbox("Row variable", categorical, key="chi_x")
    with second:
        y_name = st.selectbox("Column variable", [item for item in categorical if item != x_name], key="chi_y")
    if "Freq" in data.columns and pd.api.types.is_numeric_dtype(data["Freq"]):
        table = pd.pivot_table(
            data,
            index=x_name,
            columns=y_name,
            values="Freq",
            aggfunc="sum",
            fill_value=0,
        )
        st.caption("This dataset contains an explicit frequency column, which is used as the contingency-table count.")
    else:
        table = pd.crosstab(data[x_name], data[y_name], dropna=False)
    if table.shape[0] < 2 or table.shape[1] < 2:
        st.warning("Both variables require at least two observed levels.")
        return
    chi_square, p_value, degrees_freedom, expected = stats.chi2_contingency(table)
    expected_table = pd.DataFrame(expected, index=table.index, columns=table.columns)
    a, b, c = st.columns(3)
    a.metric("Chi-square statistic", f"{chi_square:.3f}")
    b.metric("Degrees of freedom", int(degrees_freedom))
    c.metric("p-value", f"{p_value:.4f}")
    st.markdown("#### Observed counts")
    st.dataframe(table, width="stretch")
    st.markdown("#### Expected counts under independence")
    st.dataframe(expected_table.round(2), width="stretch")
    st.caption("Inspect expected counts before relying on the chi-square reference approximation.")


def render_linear_regression(data: pd.DataFrame) -> None:
    numeric = numerical_columns(data)
    if len(numeric) < 2:
        st.warning("Simple linear regression requires at least two numeric variables.")
        return
    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Numeric outcome", numeric, key="linear_outcome")
    with right:
        predictor = st.selectbox("Numeric predictor", [item for item in numeric if item != outcome], key="linear_predictor")
    subset = data[[outcome, predictor]].dropna()
    if len(subset) < 3:
        st.warning("At least three complete observations are required.")
        return
    fit = stats.linregress(subset[predictor], subset[outcome])
    residuals = subset[outcome] - (fit.intercept + fit.slope * subset[predictor])
    degrees_freedom = len(subset) - 2
    critical = stats.t.ppf(0.975, degrees_freedom)
    slope_ci = (fit.slope - critical * fit.stderr, fit.slope + critical * fit.stderr)
    a, b, c, d = st.columns(4)
    a.metric("Slope", f"{fit.slope:.4f}")
    b.metric("95% slope CI", f"[{slope_ci[0]:.4f}, {slope_ci[1]:.4f}]")
    c.metric("p-value", f"{fit.pvalue:.4f}")
    d.metric("R²", f"{fit.rvalue ** 2:.3f}")
    st.scatter_chart(subset, x=predictor, y=outcome)
    st.dataframe(
        pd.DataFrame({"Fitted value": fit.intercept + fit.slope * subset[predictor], "Residual": residuals}).head(20).round(3),
        width="stretch",
    )
    st.caption("This simple model estimates the conditional mean of the outcome given one predictor. Causal interpretation requires additional design and substantive assumptions.")


def render_logistic_regression(data: pd.DataFrame) -> None:
    categorical = categorical_columns(data)
    numeric = numerical_columns(data)
    if not categorical or not numeric:
        st.warning("This starter logistic workflow requires a binary categorical outcome and a numeric predictor.")
        return
    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Binary outcome", categorical, key="logistic_outcome")
    with right:
        predictor = st.selectbox("Numeric predictor", numeric, key="logistic_predictor")
    subset = data[[outcome, predictor]].dropna().copy()
    encoded_info = coerce_binary(subset[outcome])
    if encoded_info is None:
        st.warning("Choose an outcome with exactly two observed levels.")
        return
    encoded, levels = encoded_info
    subset = subset.loc[encoded.index].copy()
    try:
        design = sm.add_constant(subset[[predictor]].astype(float))
        model = sm.Logit(encoded, design).fit(disp=False)
    except (ValueError, np.linalg.LinAlgError) as error:
        st.error(f"The logistic model could not be fitted: {error}")
        return
    coefficient = float(model.params[predictor])
    confidence_interval = model.conf_int().loc[predictor]
    odds_ratio = np.exp(coefficient)
    a, b, c, d = st.columns(4)
    a.metric("Log-odds coefficient", f"{coefficient:.4f}")
    b.metric("95% coefficient CI", f"[{confidence_interval.iloc[0]:.4f}, {confidence_interval.iloc[1]:.4f}]")
    c.metric("Odds ratio", f"{odds_ratio:.3f}")
    d.metric("p-value", f"{model.pvalues[predictor]:.4f}")
    prediction_grid = pd.DataFrame({predictor: np.linspace(subset[predictor].min(), subset[predictor].max(), 100)})
    prediction_grid["Predicted probability"] = model.predict(sm.add_constant(prediction_grid, has_constant="add"))
    st.line_chart(prediction_grid, x=predictor, y="Predicted probability")
    st.caption(f"The outcome is coded as 1 for **{levels[1]}** and 0 for **{levels[0]}**. The displayed odds ratio is conditional on this one-predictor model.")


def render_analysis_studio(manifest: dict) -> None:
    st.title("Analysis Studio")
    st.write(
        "Select an analysis only after reviewing the active module's presentation. The app "
        "reports an estimate, uncertainty where implemented, a statistical test where appropriate, and design cautions."
    )
    data, dataset_name, provenance = choose_data(manifest, "analysis")
    if data is None:
        st.info("Upload a CSV to begin a participant-data analysis.")
        return
    st.subheader(dataset_name)
    st.caption(provenance)
    method = st.selectbox(
        "Analysis activity",
        ["Descriptive profile", "Bootstrap interval for a mean", "Two-group comparison", "Categorical association", "Simple linear regression", "Logistic regression"],
    )
    if method == "Descriptive profile":
        numeric = numerical_columns(data)
        if numeric:
            st.dataframe(data[numeric].describe().T.round(3), width="stretch")
        else:
            st.info("No numeric variables are available for this profile.")
    elif method == "Bootstrap interval for a mean":
        render_bootstrap(data)
    elif method == "Two-group comparison":
        render_two_group(data)
    elif method == "Categorical association":
        render_chi_square(data)
    elif method == "Simple linear regression":
        render_linear_regression(data)
    else:
        render_logistic_regression(data)

    st.download_button(
        "Download the current data as CSV",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="seminar_analysis_data.csv",
        mime="text/csv",
    )


def render_dataset_library(manifest: dict) -> None:
    st.title("Public Dataset Library")
    st.write(
        "All datasets used in the seminar are public and bundled in the repository. They are available without API keys and remain accessible when the app has no network connection."
    )
    records = []
    for day in manifest["days"]:
        for module in day["modules"]:
            worked = module["worked_example"]
            records.append({"Day": day["title"], "Module": module["title"], "Role": "Worked example", "Dataset": worked["name"], "File": worked["file"]})
            for dataset in module["byod"]:
                records.append({"Day": day["title"], "Module": module["title"], "Role": "BYOD choice", "Dataset": dataset["name"], "File": dataset["file"]})
    catalog = pd.DataFrame(records)
    st.dataframe(catalog, width="stretch", hide_index=True)
    st.markdown("### Provenance")
    source = manifest["dataset_source"]
    st.write(f"**Archive:** [{source['name']}]({source['catalog_url']})")
    st.write(source["access"])
    st.caption("Dataset documentation and original package/source attributions should be consulted before any substantive research use.")


def render_reproducibility(manifest: dict) -> None:
    st.title("Reproducibility and Responsible Interpretation")
    st.write(
        "The no-code interface is not intended to conceal the analytical work. Each module "
        "identifies its mathematical target, data source, method, assumptions, and interpretation boundary."
    )
    st.markdown(
        "| Element | Practice in this project |\n"
        "|---|---|\n"
        "| Seminar structure | Each day and module begins with a rigorous, no-proof presentation. |\n"
        "| Dataset access | Public datasets are vendored locally; no API key is required. |\n"
        "| Input handling | CSV uploads are read in memory and not written to disk by the app. |\n"
        "| Analytical provenance | The active dataset, method, model settings, and warnings are visible in the interface. |\n"
        "| Computational engines | The app is Python/Streamlit; the repository documents a parallel R-engine contract for selected methods. |\n"
        "| Interpretation | Results remain conditional on the data, design, variables, assumptions, and analytical choices. |"
    )
    st.markdown("### Repository resources")
    st.write("The `data/module_manifest.json` file is the single source of truth for the curriculum, mathematical presentation prompts, worked examples, and BYOD datasets.")
    st.write("The `app/engines/r/README.md` file defines the integration and validation boundary for R implementations.")


def render_home(manifest: dict) -> None:
    st.title(manifest["title"])
    st.subheader("A three-day, presentation-first seminar with a no-code research app")
    st.write(
        "The seminar is organized as **three days**, each consisting of **three modules**. "
        "Every day begins with an introduction, and every module begins with a rigorous presentation of its concepts, notation, assumptions, and results—without proofs—before participants work with data."
    )
    overview = []
    for day in manifest["days"]:
        overview.append({"Day": day["title"], "Modules": len(day["modules"]), "Worked examples": len(day["modules"]), "BYOD choices": sum(len(module["byod"]) for module in day["modules"])})
    st.dataframe(pd.DataFrame(overview), width="stretch", hide_index=True)
    st.info(
        "Every module contains one worked public dataset and four public datasets for "
        "participant-led BYOD activity. The app ships with these data locally, so no API key is required."
    )
    st.markdown("### Suggested seminar use")
    st.write(
        "Begin in **Curriculum and Rigorous Presentation**, then inspect the worked dataset "
        "in **Dataset Explorer**. Use **Analysis Studio** only after the relevant mathematical "
        "and statistical presentation. The **Public Dataset Library** documents the available "
        "BYOD choices for each module."
    )


manifest = load_manifest()
module_map = module_lookup(manifest)

with st.sidebar:
    st.title("Seminar App")
    active_page = st.radio(
        "Navigate",
        ["Home", "Curriculum and Rigorous Presentation", "Dataset Explorer", "Analysis Studio", "Public Dataset Library", "Reproducibility"],
    )
    st.divider()
    active_module_id = st.selectbox(
        "Active module",
        options=list(module_map),
        format_func=lambda item: f"{module_map[item]['day_id'].replace('_', ' ').title()} · {module_map[item]['title']}",
    )
    st.session_state["last_module"] = active_module_id
    st.caption("No-code interface · presentation-first curriculum · transparent provenance")

if active_page == "Home":
    render_home(manifest)
elif active_page == "Curriculum and Rigorous Presentation":
    active_module = render_day_and_module(manifest)
    st.session_state["last_module"] = active_module["id"]
elif active_page == "Dataset Explorer":
    render_data_explorer(manifest)
elif active_page == "Analysis Studio":
    render_analysis_studio(manifest)
elif active_page == "Public Dataset Library":
    render_dataset_library(manifest)
else:
    render_reproducibility(manifest)
