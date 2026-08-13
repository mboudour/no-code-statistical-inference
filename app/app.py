"""Interactive companion app for the No-Code Statistical Inference seminar."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

st.set_page_config(
    page_title="No-Code Statistical Inference",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def demo_data() -> pd.DataFrame:
    """Return a deterministic teaching dataset for the comparison activity."""
    rng = np.random.default_rng(2026)
    return pd.DataFrame(
        {
            "condition": ["Control"] * 30 + ["Intervention"] * 30,
            "outcome": np.concatenate(
                [rng.normal(51, 9, 30), rng.normal(57, 9, 30)]
            ).round(2),
            "baseline_score": rng.normal(50, 10, 60).round(2),
        }
    )


def read_uploaded_csv(uploaded_file) -> pd.DataFrame | None:
    """Read a CSV upload without persisting it to disk."""
    if uploaded_file is None:
        return None
    try:
        return pd.read_csv(uploaded_file)
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"The uploaded file could not be read as a CSV: {error}")
        return None


def cohens_d(group_a: np.ndarray, group_b: np.ndarray) -> float:
    """Compute Cohen's d using pooled sample standard deviation."""
    pooled_sd = np.sqrt(
        ((len(group_a) - 1) * np.var(group_a, ddof=1)
        + (len(group_b) - 1) * np.var(group_b, ddof=1))
        / (len(group_a) + len(group_b) - 2)
    )
    return float((np.mean(group_b) - np.mean(group_a)) / pooled_sd)


def render_home() -> None:
    st.title("No-Code Statistical Inference")
    st.subheader("Understanding Data, Uncertainty, and Evidence")
    st.write(
        "This companion application is designed for the Instats seminar. It lets "
        "participants explore inference and perform guided analyses without writing code."
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### What this app teaches")
        st.markdown(
            "- How samples vary from one draw to another.\n"
            "- What confidence intervals and p-values represent.\n"
            "- How assumptions and analytical choices affect conclusions.\n"
            "- How a transparent research app records its computational provenance."
        )
    with right:
        st.markdown("### Design principle")
        st.info(
            "No-code for participants; transparent and reproducible analysis underneath. "
            "The interface is Python/Streamlit, with a planned parallel R engine for "
            "selected conventional statistical procedures."
        )

    st.markdown("### Start here")
    st.write(
        "Use **Inference Explorer** to simulate sampling uncertainty. Use **Analysis "
        "Studio** to run a guided two-group comparison with the included teaching data "
        "or your own CSV file."
    )


def render_inference_explorer() -> None:
    st.title("Inference Explorer")
    st.write(
        "Repeated sampling makes uncertainty visible. Adjust the population and study "
        "settings, then inspect the distribution of sample means.")

    controls, results = st.columns([1, 2])
    with controls:
        population_mean = st.number_input("Population mean", value=50.0, step=1.0)
        population_sd = st.number_input(
            "Population standard deviation", min_value=0.1, value=10.0, step=0.5
        )
        sample_size = st.slider("Sample size", min_value=5, max_value=500, value=30)
        repetitions = st.slider(
            "Repeated samples", min_value=100, max_value=5_000, value=1_000, step=100
        )
        seed = st.number_input("Simulation seed", min_value=0, value=2026, step=1)

    rng = np.random.default_rng(seed)
    samples = rng.normal(population_mean, population_sd, size=(repetitions, sample_size))
    sample_means = samples.mean(axis=1)
    standard_error = population_sd / np.sqrt(sample_size)
    ci_low = sample_means - 1.96 * standard_error
    ci_high = sample_means + 1.96 * standard_error
    coverage = np.mean((ci_low <= population_mean) & (population_mean <= ci_high))

    with results:
        metric_1, metric_2, metric_3 = st.columns(3)
        metric_1.metric("Mean of sample means", f"{sample_means.mean():.2f}")
        metric_2.metric("Theoretical standard error", f"{standard_error:.2f}")
        metric_3.metric("Observed 95% CI coverage", f"{coverage:.1%}")

        histogram_data = pd.DataFrame({"Sample mean": sample_means})
        st.bar_chart(
            np.histogram(histogram_data["Sample mean"], bins=35)[0],
            x_label="Histogram bin",
            y_label="Number of simulated samples",
        )
        st.caption(
            "The histogram summarizes sample means across repeated samples. The displayed "
            "coverage is the proportion of approximate 95% confidence intervals containing "
            "the population mean in this simulation."
        )

    with st.expander("Interpretation"):
        st.write(
            "A confidence interval procedure is evaluated across repeated samples. With the "
            "settings above, intervals constructed in the same way will contain the fixed "
            "population mean approximately 95% of the time over many repetitions."
        )


def render_analysis_studio() -> None:
    st.title("Analysis Studio")
    st.write(
        "Run a guided independent-samples comparison. The starter workflow uses Welch's "
        "t-test, which does not assume equal group variances.")

    uploaded_file = st.file_uploader("Optional: upload a CSV file", type=["csv"])
    data = read_uploaded_csv(uploaded_file)
    if data is None:
        data = demo_data()
        st.caption("Using the built-in teaching dataset (60 observations).")
    else:
        st.caption(f"Using uploaded data: {len(data):,} rows and {len(data.columns):,} columns.")

    numeric_columns = data.select_dtypes(include=np.number).columns.tolist()
    categorical_columns = data.select_dtypes(exclude=np.number).columns.tolist()
    if not numeric_columns or not categorical_columns:
        st.warning(
            "A two-group comparison requires at least one numeric outcome column and one "
            "non-numeric grouping column."
        )
        return

    left, right = st.columns(2)
    with left:
        outcome = st.selectbox("Outcome variable", numeric_columns)
    with right:
        group = st.selectbox("Grouping variable", categorical_columns)

    analysis_data = data[[outcome, group]].dropna().copy()
    levels = analysis_data[group].astype(str).unique().tolist()
    if len(levels) != 2:
        st.warning(
            f"The selected grouping variable has {len(levels)} non-missing levels. Select a variable with exactly two groups."
        )
        return

    group_a_name, group_b_name = levels
    group_a = analysis_data.loc[analysis_data[group].astype(str) == group_a_name, outcome].to_numpy()
    group_b = analysis_data.loc[analysis_data[group].astype(str) == group_b_name, outcome].to_numpy()

    test = stats.ttest_ind(group_a, group_b, equal_var=False)
    difference = float(np.mean(group_b) - np.mean(group_a))
    se_difference = np.sqrt(np.var(group_a, ddof=1) / len(group_a) + np.var(group_b, ddof=1) / len(group_b))
    numerator = (np.var(group_a, ddof=1) / len(group_a) + np.var(group_b, ddof=1) / len(group_b)) ** 2
    denominator = (
        (np.var(group_a, ddof=1) / len(group_a)) ** 2 / (len(group_a) - 1)
        + (np.var(group_b, ddof=1) / len(group_b)) ** 2 / (len(group_b) - 1)
    )
    degrees_of_freedom = numerator / denominator
    critical_value = stats.t.ppf(0.975, degrees_of_freedom)
    ci = (difference - critical_value * se_difference, difference + critical_value * se_difference)
    effect_size = cohens_d(group_a, group_b)

    st.subheader("Result summary")
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Mean difference", f"{difference:.2f}")
    metric_2.metric("95% CI", f"[{ci[0]:.2f}, {ci[1]:.2f}]")
    metric_3.metric("p-value", f"{test.pvalue:.4f}")
    metric_4.metric("Cohen's d", f"{effect_size:.2f}")

    summary = pd.DataFrame(
        {
            "Group": [group_a_name, group_b_name],
            "n": [len(group_a), len(group_b)],
            "Mean": [np.mean(group_a), np.mean(group_b)],
            "Standard deviation": [np.std(group_a, ddof=1), np.std(group_b, ddof=1)],
        }
    )
    st.dataframe(summary.round(3), use_container_width=True, hide_index=True)

    st.subheader("Interpretation")
    direction = "higher" if difference > 0 else "lower"
    st.write(
        f"The mean outcome for **{group_b_name}** was {abs(difference):.2f} units {direction} "
        f"than for **{group_a_name}**. The 95% confidence interval for this difference is "
        f"[{ci[0]:.2f}, {ci[1]:.2f}]. This result should be interpreted alongside the study "
        "design, outcome scale, group construction, missing-data treatment, and model assumptions."
    )

    with st.expander("Assumptions and provenance"):
        st.markdown(
            "| Item | Current setting |\n"
            "|---|---|\n"
            "| Method | Welch independent-samples t-test |\n"
            "| Data treatment | Complete cases for the selected outcome and grouping variable |\n"
            "| Null hypothesis | Equal population means |\n"
            "| Confidence level | 95% |\n"
            "| Execution engine | Python / SciPy starter implementation |\n"
            "| Parallel R implementation | Planned in `app/engines/r/` |"
        )


def render_byod() -> None:
    st.title("Bring Your Own Data")
    st.write(
        "The workshop version will provide a guided workflow for uploaded tabular data, "
        "method selection, assumption checks, output download, and interpretation support."
    )
    st.info(
        "This starter repository does not persist uploads. The final deployment will state "
        "its data-retention policy prominently and will not execute user-supplied code."
    )


def render_reproducibility() -> None:
    st.title("Reproducibility")
    st.write(
        "No-code does not mean opaque. Each production procedure should expose a concise "
        "record of how its result was produced.")
    st.markdown(
        "| Element | Practice |\n"
        "|---|---|\n"
        "| Analysis request | Store selected variables, settings, and missing-data treatment |\n"
        "| Engine | Identify Python or R and the relevant package/function |\n"
        "| Assumptions | Explain assumptions and show applicable warnings |\n"
        "| Result contract | Return standard estimates, uncertainty, tests, plots, and metadata |\n"
        "| Validation | Compare dual-engine methods on fixed teaching datasets |\n"
        "| Artefacts | Provide a human-readable summary and optional machine-readable output |"
    )
    st.caption(
        "This starter app demonstrates the Python engine. The repository's R-engine folder "
        "documents the boundary for parallel R implementations and parity testing."
    )


PAGES = {
    "Home": render_home,
    "Inference Explorer": render_inference_explorer,
    "Analysis Studio": render_analysis_studio,
    "Bring Your Own Data": render_byod,
    "Reproducibility": render_reproducibility,
}

with st.sidebar:
    st.title("Seminar App")
    selected_page = st.radio("Navigate", list(PAGES))
    st.divider()
    st.caption("No-code interface · transparent analytical provenance")

PAGES[selected_page]()
