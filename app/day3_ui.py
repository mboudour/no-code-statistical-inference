"""Computation-first Day 3 interface aligned with the revised Day 3 slides."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from day3_analysis import (
    classification_metrics,
    external_logistic_validation,
    fit_day3_linear_model,
    fit_day3_logistic_model,
    holdout_validation,
)
from day3_computations import (
    adjustment_comparison,
    binary_outcome_columns,
    bootstrap_optimism_logistic,
    categorical_predictor_regression,
    cross_validate_day3_model,
    nested_specification_comparison,
    refit_after_case_exclusion,
)
from inference_core import build_report, categorical_columns, numeric_columns
from validation import InputValidationError

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent


def _record_download(result: dict[str, Any], audit: dict[str, Any], selections: dict[str, Any], key: str) -> None:
    report = build_report(result, audit, selections, include_details=True)
    st.download_button(
        "Download computation and reproducibility record (Markdown)",
        report,
        file_name=f"{key}_day3_computation_record.md",
        mime="text/markdown",
        key=f"{key}_day3_computation_record",
    )


def _dataset_context(data: pd.DataFrame, dataset_name: str) -> None:
    st.caption(f"Dataset used for this computation: **{dataset_name}**")
    first, second, third = st.columns(3)
    first.metric("Rows", len(data))
    second.metric("Variables", len(data.columns))
    third.metric("Complete rows", len(data.dropna()))
    with st.expander("View data context and variables", expanded=False):
        st.dataframe(data.head(15), width="stretch", hide_index=True)
        st.caption("Confirm variable definitions, coding, units, provenance, and missing-data handling before interpreting a result.")


def _linear_inputs(data: pd.DataFrame, key: str, multiple: bool = False, categories: bool = False) -> tuple[str, list[str], list[str]] | None:
    numbers = numeric_columns(data)
    if len(numbers) < 2:
        st.info("This computation needs one numeric outcome and at least one distinct numeric predictor.")
        return None
    outcome = st.selectbox("Numeric outcome", numbers, key=f"{key}_outcome")
    available = [column for column in numbers if column != outcome]
    if multiple:
        predictors = st.multiselect("Numeric predictor(s)", available, default=available[: min(2, len(available))], key=f"{key}_predictors")
    else:
        predictors = [st.selectbox("Numeric predictor", available, key=f"{key}_predictor")]
    if not predictors:
        st.info("Select at least one numeric predictor.")
        return None
    factors: list[str] = []
    if categories:
        options = [column for column in categorical_columns(data) if 2 <= data[column].dropna().nunique() <= 12]
        factors = st.multiselect("Optional categorical predictor(s) — treatment coded", options, key=f"{key}_factors")
    return outcome, predictors, factors


def _render_linear_result(result: dict[str, Any], audit: dict[str, Any], key: str, selections: dict[str, Any], emphasis: str) -> None:
    details = result["details"]
    cases = details["diagnostic_cases"]
    largest_cooks_distance = cases["Cook's distance"].max()
    first, second, third, fourth = st.columns(4)
    first.metric("Complete records", details["n"])
    second.metric("R²", f"{result['_model'].rsquared:.3f}")
    third.metric("Largest Cook's distance", f"{largest_cooks_distance:.3f}")
    fourth.metric("Breusch–Pagan p-value", f"{result['diagnostics'].get('breusch_pagan', {}).get('p_value', float('nan')):.4f}")
    tabs = st.tabs(["Coefficients", "Residuals and variance", "Leverage and influence", "Record"])
    with tabs[0]:
        st.caption(emphasis)
        left, right = st.columns(2)
        with left:
            st.markdown("**Conventional coefficient intervals**")
            st.dataframe(details["coefficients"], width="stretch")
        with right:
            st.markdown("**HC3 robust coefficient intervals**")
            st.dataframe(details["robust_hc3_coefficients"], width="stretch")
        st.caption("HC3 changes coefficient uncertainty when residual variance may differ. It does not repair confounding, dependence, a poor mean form, or selection bias.")
    with tabs[1]:
        left, right = st.columns(2)
        with left:
            residual = px.scatter(cases, x="Fitted", y="Residual", hover_data=["Row", "Cook's distance"], title="Residuals versus fitted values", template="plotly_white")
            residual.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(residual, width="stretch", key=f"{key}_residual_plot")
        with right:
            qq = details["qq_points"]
            plot = px.scatter(qq, x="Normal theoretical quantile", y="Ordered standardized residual", title="Quantile–quantile display", template="plotly_white")
            st.plotly_chart(plot, width="stretch", key=f"{key}_qq_plot")
    with tabs[2]:
        left, right = st.columns(2)
        with left:
            influence = px.scatter(cases, x="Leverage", y="Standardized residual", size="Cook's distance", hover_data=["Row", "Fitted", "Residual"], title="Leverage, residuals, and Cook's distance", template="plotly_white")
            influence.add_vline(x=result["diagnostics"]["leverage_screen"], line_dash="dash", line_color="orange")
            st.plotly_chart(influence, width="stretch", key=f"{key}_influence_plot")
        with right:
            st.markdown("**Variance-inflation factors**")
            st.dataframe(details["vif"], width="stretch", hide_index=True)
            st.write({
                "Leverage screen": result["diagnostics"]["leverage_screen"],
                "Cook's-distance screen": result["diagnostics"]["cooks_distance_screen"],
                "Cases above leverage screen": result["diagnostics"]["observations_above_leverage_screen"],
                "Cases above Cook's-distance screen": result["diagnostics"]["observations_above_cooks_screen"],
            })
    with tabs[3]:
        st.write(result["interpretation"])
        st.write(result["limitations"])
        _record_download(result, audit, selections, key)


def _simple_or_multiple_linear(data: pd.DataFrame, audit: dict[str, Any], key: str, module_id: str) -> None:
    labels = {
        "d3m01": "Least-squares line, fitted values, residuals, and slope uncertainty",
        "d3m02": "Multiple-regression partial comparisons with collinearity and robust-uncertainty displays",
        "d3m07": "Residual patterns, heteroskedasticity evidence, and conventional versus HC3 robust uncertainty",
    }
    selection = _linear_inputs(data, key, multiple=module_id != "d3m01", categories=module_id == "d3m02")
    if selection is None:
        return
    outcome, predictors, factors = selection
    try:
        result = fit_day3_linear_model(data, outcome, predictors, factors)
    except InputValidationError as error:
        st.warning(f"This computation is unavailable for the selected columns: {error}")
        return
    _render_linear_result(result, audit, key, {"module": module_id.upper(), "outcome": outcome, "numeric predictors": predictors, "categorical predictors": factors}, labels[module_id])


def _categorical_contrasts(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    numbers = numeric_columns(data)
    factors = [column for column in categorical_columns(data) if 2 <= data[column].dropna().nunique() <= 12]
    if not numbers or not factors:
        st.info("This computation needs a numeric outcome and a categorical predictor with between two and twelve observed levels.")
        return
    outcome = st.selectbox("Numeric outcome", numbers, key=f"{key}_contrast_outcome")
    group = st.selectbox("Categorical predictor", factors, key=f"{key}_contrast_group")
    try:
        result = categorical_predictor_regression(data, outcome, group)
    except InputValidationError as error:
        st.warning(f"This coding-and-contrast computation is unavailable: {error}")
        return
    st.info(f"Treatment coding uses **{result['details']['reference_group']}** as the reference level.")
    first, second = st.columns(2)
    with first:
        st.markdown("**Predicted group means**")
        st.dataframe(result["details"]["group_means"], width="stretch", hide_index=True)
    with second:
        st.markdown("**Model-based contrasts**")
        st.dataframe(result["details"]["contrasts"], width="stretch", hide_index=True)
    st.markdown("**Treatment-coded coefficients**")
    st.dataframe(result["details"]["coefficients"], width="stretch")
    st.caption("Changing the reference category changes coefficient labels, not the fitted group means. Contrast intervals are conditional on the stated linear model.")
    _record_download(result, audit, {"module": "D3M03", "outcome": outcome, "categorical predictor": group, "reference group": result["details"]["reference_group"]}, key)


def _adjustment_computation(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    selection = _linear_inputs(data, key, multiple=False)
    if selection is None:
        return
    outcome, focal_list, _ = selection
    focal = focal_list[0]
    candidates = [column for column in numeric_columns(data) if column not in {outcome, focal}]
    adjustments = st.multiselect("Named adjustment predictor(s)", candidates, default=candidates[: min(2, len(candidates))], key=f"{key}_adjustments")
    if not adjustments:
        st.info("Select at least one named adjustment predictor to compare the two specifications.")
        return
    try:
        result = adjustment_comparison(data, outcome, focal, adjustments)
    except InputValidationError as error:
        st.warning(f"The adjustment comparison is unavailable: {error}")
        return
    st.dataframe(result["comparison"], width="stretch", hide_index=True)
    st.info(result["interpretation"])
    st.warning(result["limitations"])
    with st.expander("View the full adjusted coefficient table"):
        st.dataframe(result["adjusted"]["details"]["coefficients"], width="stretch")
    record = {"method": result["method"], "question": result["question"], "data_design": result["data_design"], "assumptions": result["adjusted"]["assumptions"], "diagnostics": result["adjusted"]["diagnostics"], "estimate": result["comparison"], "uncertainty": result["adjusted"]["uncertainty"], "effect_size": result["adjusted"]["effect_size"], "test": result["adjusted"]["test"], "interpretation": result["interpretation"], "limitations": result["limitations"], "next_step": "Use a causal diagram and study-design rationale before giving the adjusted coefficient a causal interpretation.", "details": {"table": result["comparison"]}}
    _record_download(record, audit, {"module": "D3M04", "outcome": outcome, "focal predictor": focal, "adjustment predictors": adjustments}, key)


def _specification_computation(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    selection = _linear_inputs(data, key, multiple=True, categories=True)
    if selection is None:
        return
    outcome, predictors, factors = selection
    extension = st.radio("Extended specification", ["Add a quadratic term", "Add a numeric interaction"], horizontal=True, key=f"{key}_extension")
    quadratic, interaction = None, None
    if extension == "Add a quadratic term":
        quadratic = st.selectbox("Predictor receiving the squared term", predictors, key=f"{key}_quadratic")
    elif len(predictors) >= 2:
        first = st.selectbox("First interaction predictor", predictors, key=f"{key}_interaction_first")
        second = st.selectbox("Second interaction predictor", [item for item in predictors if item != first], key=f"{key}_interaction_second")
        interaction = (first, second)
    else:
        st.info("Select at least two numeric predictors for an interaction computation.")
        return
    try:
        result = nested_specification_comparison(data, outcome, predictors, factors, quadratic_predictor=quadratic, interaction=interaction)
    except InputValidationError as error:
        st.warning(f"The specification comparison is unavailable: {error}")
        return
    st.dataframe(result["comparison"], width="stretch", hide_index=True)
    st.write(result["nested_test"])
    st.info(result["interpretation"])
    st.warning(result["limitations"])
    with st.expander("View extended-model coefficients"):
        st.dataframe(result["extended"]["details"]["coefficients"], width="stretch")
    record = {"method": result["method"], "question": result["question"], "data_design": f"Outcome={outcome}; baseline predictors={', '.join(predictors)}; extension={quadratic or ' × '.join(interaction or ())}.", "assumptions": result["extended"]["assumptions"], "diagnostics": result["extended"]["diagnostics"], "estimate": result["comparison"], "uncertainty": result["extended"]["uncertainty"], "effect_size": result["extended"]["effect_size"], "test": str(result["nested_test"]), "interpretation": result["interpretation"], "limitations": result["limitations"], "next_step": "Inspect residual patterns and validate the selected specification on data not used for model selection.", "details": {"table": result["comparison"]}}
    _record_download(record, audit, {"module": "D3M05", "outcome": outcome, "baseline predictors": predictors, "quadratic predictor": quadratic or "None", "interaction": " × ".join(interaction) if interaction else "None"}, key)


def _logistic_inputs(data: pd.DataFrame, key: str) -> tuple[str, list[str], list[str]] | None:
    outcomes = binary_outcome_columns(data)
    numbers = numeric_columns(data)
    if not outcomes or not numbers:
        st.info("This computation needs a binary outcome and at least one numeric predictor.")
        return None
    outcome = st.selectbox("Binary outcome", outcomes, key=f"{key}_binary_outcome")
    predictors = st.multiselect("Numeric predictor(s)", [column for column in numbers if column != outcome], default=[column for column in numbers if column != outcome][:2], key=f"{key}_binary_predictors")
    if not predictors:
        st.info("Select at least one numeric predictor.")
        return None
    factors = [column for column in categorical_columns(data) if column != outcome and 2 <= data[column].dropna().nunique() <= 12]
    categorical = st.multiselect("Optional categorical predictor(s) — treatment coded", factors, key=f"{key}_binary_factors")
    return outcome, predictors, categorical


def _fit_logistic(data: pd.DataFrame, key: str) -> tuple[dict[str, Any], str, list[str], list[str]] | None:
    selections = _logistic_inputs(data, key)
    if selections is None:
        return None
    outcome, predictors, factors = selections
    try:
        return fit_day3_logistic_model(data, outcome, predictors, factors), outcome, predictors, factors
    except InputValidationError as error:
        st.warning(f"The logistic computation is unavailable for these selections: {error}")
        return None


def _logistic_probability_computation(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    fitted = _fit_logistic(data, key)
    if fitted is None:
        return
    result, outcome, predictors, factors = fitted
    st.dataframe(result["details"]["coefficients"], width="stretch")
    cases = result["details"]["probability_cases"]
    plot = px.scatter(cases, x="Row", y="Predicted probability", color="Observed event", title="Fitted probabilities by record", template="plotly_white")
    st.plotly_chart(plot, width="stretch", key=f"{key}_probability_plot")
    st.caption("Odds ratios compare odds rather than probabilities. Use the fitted-probability display to communicate results on the probability scale.")
    _record_download(result, audit, {"module": "D3M06", "binary outcome": outcome, "numeric predictors": predictors, "categorical predictors": factors}, key)


def _influence_sensitivity(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    selection = _linear_inputs(data, key, multiple=True, categories=True)
    if selection is None:
        return
    outcome, predictors, factors = selection
    try:
        original = fit_day3_linear_model(data, outcome, predictors, factors)
    except InputValidationError as error:
        st.warning(f"The diagnostic model is unavailable: {error}")
        return
    cases = original["details"]["diagnostic_cases"].sort_values("Cook's distance", ascending=False)
    influence = px.scatter(cases, x="Leverage", y="Standardized residual", size="Cook's distance", hover_data=["Row", "Fitted", "Residual"], title="Influence screening display", template="plotly_white")
    influence.add_vline(x=original["diagnostics"]["leverage_screen"], line_dash="dash", line_color="orange")
    st.plotly_chart(influence, width="stretch", key=f"{key}_sensitivity_influence")
    candidate_rows = cases["Row"].head(min(10, len(cases))).astype(str).tolist()
    excluded = st.multiselect("Temporarily refit without selected high-Cook's-distance row(s)", candidate_rows, key=f"{key}_exclude_rows")
    st.caption("This is a sensitivity computation, not a deletion recommendation. Inspect the record and mechanism before excluding a real case.")
    if excluded:
        try:
            reduced = refit_after_case_exclusion(data, outcome, predictors, factors, excluded)
        except InputValidationError as error:
            st.warning(f"The sensitivity refit is unavailable: {error}")
            return
        first, second = st.columns(2)
        with first:
            st.markdown("**Original coefficients**")
            st.dataframe(original["details"]["coefficients"], width="stretch")
        with second:
            st.markdown("**Sensitivity-refit coefficients**")
            st.dataframe(reduced["details"]["coefficients"], width="stretch")
        record = reduced
        selections = {"module": "D3M08", "outcome": outcome, "predictors": predictors, "categorical predictors": factors, "temporarily excluded diagnostic rows": excluded}
    else:
        record = original
        selections = {"module": "D3M08", "outcome": outcome, "predictors": predictors, "categorical predictors": factors, "temporarily excluded diagnostic rows": "None"}
    _record_download(record, audit, selections, key)


def _prediction_performance(data: pd.DataFrame, audit: dict[str, Any], key: str) -> None:
    fitted = _fit_logistic(data, key)
    if fitted is None:
        return
    result, outcome, predictors, factors = fitted
    probabilities, observed = result["_probabilities"], result["_outcome"]
    tabs = st.tabs(["Threshold consequences", "Calibration", "Discrimination", "Record"])
    with tabs[0]:
        threshold = st.slider("Classification threshold", 0.05, 0.95, 0.50, 0.05, key=f"{key}_threshold")
        metrics = classification_metrics(observed, probabilities, threshold)
        values = st.columns(4)
        values[0].metric("Sensitivity", f"{metrics['sensitivity']:.3f}")
        values[1].metric("Specificity", f"{metrics['specificity']:.3f}")
        values[2].metric("Positive predictive value", f"{metrics['positive_predictive_value']:.3f}")
        values[3].metric("Accuracy", f"{metrics['accuracy']:.3f}")
        st.dataframe(pd.DataFrame([{"Predicted / observed": "Positive", "Observed event": metrics["true_positive"], "Observed non-event": metrics["false_positive"]}, {"Predicted / observed": "Negative", "Observed event": metrics["false_negative"], "Observed non-event": metrics["true_negative"]}]), width="stretch", hide_index=True)
    with tabs[1]:
        calibration = result["details"]["calibration"]
        plot = px.scatter(calibration, x="Mean_predicted_probability", y="Observed_event_rate", size="Records", hover_data=["Bin"], title="Binned calibration display", template="plotly_white")
        plot.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(plot, width="stretch", key=f"{key}_calibration")
        st.dataframe(calibration, width="stretch", hide_index=True)
    with tabs[2]:
        roc = result["details"]["roc"]
        plot = px.line(roc, x="False positive rate", y="True positive rate", title="Receiver-operating-characteristic curve", template="plotly_white")
        plot.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(plot, width="stretch", key=f"{key}_roc")
        st.metric("In-sample area under the curve", f"{result['diagnostics']['area_under_roc_curve']:.3f}")
        st.metric("In-sample Brier score", f"{result['diagnostics']['brier_score']:.4f}")
    with tabs[3]:
        _record_download(result, audit, {"module": "D3M09", "binary outcome": outcome, "numeric predictors": predictors, "categorical predictors": factors}, key)


def _validation_and_reproducibility(data: pd.DataFrame, audit: dict[str, Any], key: str, filename: str | None) -> None:
    numeric = numeric_columns(data)
    binary = binary_outcome_columns(data)
    options = [(column, "logistic") for column in binary] + [(column, "linear") for column in numeric if column not in binary]
    if not options:
        st.info("This computation needs a binary or numeric outcome plus numeric predictors.")
        return
    outcome, kind = st.selectbox("Outcome and model family", options, format_func=lambda item: f"{item[0]} — {'binary logistic model' if item[1] == 'logistic' else 'continuous-outcome linear model'}", key=f"{key}_validation_outcome")
    predictors = st.multiselect("Numeric predictor(s)", [column for column in numeric if column != outcome], default=[column for column in numeric if column != outcome][:2], key=f"{key}_validation_predictors")
    if not predictors:
        st.info("Select at least one numeric predictor.")
        return
    validation, cross_validation, bootstrap, record_tab = st.tabs(["Holdout / external test", "K-fold cross-validation", "Bootstrap optimism", "Reproducibility record"])
    result_for_record: dict[str, Any] | None = None
    with validation:
        try:
            if filename == "pima_test.csv" and kind == "logistic" and outcome == "type":
                training = pd.read_csv(PROJECT_DIR / "data" / "public" / "pima_train.csv").drop(columns="rownames", errors="ignore")
                result = external_logistic_validation(training, data, outcome, predictors)
                st.caption("This uses the bundled Pima training file to fit the model and the opened Pima test file for one separate-file evaluation.")
            else:
                fraction = st.select_slider("Test-set fraction", options=[0.20, 0.25, 0.30, 0.33], value=0.25, key=f"{key}_validation_fraction")
                seed = st.number_input("Split seed", 1, 999999, 2026, 1, key=f"{key}_validation_seed")
                result = holdout_validation(data, outcome, predictors, kind, float(fraction), int(seed))
            st.dataframe(result["estimate"], width="stretch", hide_index=True)
            st.info(result["interpretation"])
            result_for_record = result
        except InputValidationError as error:
            st.warning(f"The holdout calculation is unavailable: {error}")
    with cross_validation:
        folds = st.select_slider("Number of folds", options=[3, 4, 5, 6, 8, 10], value=5, key=f"{key}_cv_folds")
        seed = st.number_input("Cross-validation seed", 1, 999999, 2026, 1, key=f"{key}_cv_seed")
        if st.button("Run cross-validation", key=f"{key}_run_cv"):
            try:
                cv = cross_validate_day3_model(data, outcome, predictors, kind, int(folds), int(seed))
                st.dataframe(cv["fold_metrics"], width="stretch", hide_index=True)
                st.write(cv["summary"])
                st.info(cv["interpretation"])
            except InputValidationError as error:
                st.warning(f"The cross-validation calculation is unavailable: {error}")
    with bootstrap:
        if kind != "logistic":
            st.info("The current bootstrap-optimism computation is implemented for logistic predicted probabilities, area under the curve, and Brier score. Use a binary-outcome model for this slide topic.")
        else:
            repetitions = st.select_slider("Bootstrap repetitions", options=[20, 30, 50, 75, 100], value=30, key=f"{key}_bootstrap_repetitions")
            seed = st.number_input("Bootstrap seed", 1, 999999, 2026, 1, key=f"{key}_bootstrap_seed")
            if st.button("Run bootstrap optimism calculation", key=f"{key}_run_bootstrap"):
                try:
                    boot = bootstrap_optimism_logistic(data, outcome, predictors, int(repetitions), int(seed))
                    st.dataframe(pd.DataFrame([{"Metric": "AUC", "Apparent": boot["apparent"]["AUC"], "Estimated optimism": boot["optimism"]["AUC"], "Optimism-corrected": boot["corrected"]["AUC"]}, {"Metric": "Brier score", "Apparent": boot["apparent"]["Brier score"], "Estimated optimism": boot["optimism"]["Brier score"], "Optimism-corrected": boot["corrected"]["Brier score"]}]).round(4), width="stretch", hide_index=True)
                    st.caption(f"Completed {boot['repetitions_completed']} of {boot['repetitions_requested']} requested bootstrap repetitions.")
                    st.info(boot["interpretation"])
                except InputValidationError as error:
                    st.warning(f"The bootstrap computation is unavailable: {error}")
    with record_tab:
        st.write("Validation estimates the performance of the full procedure under a named split or resampling design. Save the accompanying record so data, formula, settings, and random seed remain inspectable.")
        if result_for_record is not None:
            _record_download(result_for_record, audit, {"module": "D3M10", "outcome": outcome, "model family": kind, "numeric predictors": predictors}, key)
        else:
            st.caption("Open the first tab to run a holdout or external-test computation before downloading its record.")


def render_day3_computation(data: pd.DataFrame, audit: dict[str, Any], key: str, module_id: str, filename: str | None = None) -> None:
    """Render exactly the Day 3 calculation introduced by the selected module."""
    st.markdown("#### Computation")
    if module_id in {"d3m01", "d3m02", "d3m07"}:
        _simple_or_multiple_linear(data, audit, key, module_id)
    elif module_id == "d3m03":
        _categorical_contrasts(data, audit, key)
    elif module_id == "d3m04":
        _adjustment_computation(data, audit, key)
    elif module_id == "d3m05":
        _specification_computation(data, audit, key)
    elif module_id == "d3m06":
        _logistic_probability_computation(data, audit, key)
    elif module_id == "d3m08":
        _influence_sensitivity(data, audit, key)
    elif module_id == "d3m09":
        _prediction_performance(data, audit, key)
    elif module_id == "d3m10":
        _validation_and_reproducibility(data, audit, key, filename)
    else:
        st.warning("This Day 3 module has no registered computation.")


def render_day3_computation_workspace(data: pd.DataFrame, audit: dict[str, Any], key: str, dataset_name: str, filename: str | None, module_id: str) -> None:
    """Day 3 begins with its computation; the general review is only at the end of the day."""
    _dataset_context(data, dataset_name)
    render_day3_computation(data, audit, key, module_id, filename)


def render_day3_final_review() -> None:
    """Single Day 3 review placed after all slide-aligned computations."""
    st.markdown("---")
    st.header("Final Day 3 model review — after the computations")
    st.caption("Use this once the relevant Day 3 calculation has been run. It is not a substitute for any of the computations above.")
    first, second = st.columns(2)
    with first:
        st.markdown("- **Model target:** State whether the result is a conditional association, probability prediction, or a causal claim requiring a separate design argument.")
        st.markdown("- **Observed support:** State the outcome coding, predictor range, reference groups, transformations, and any sparse or unsupported comparisons.")
        st.markdown("- **Computation evidence:** Record the coefficient or predicted-probability output, residual/influence evidence where relevant, and validation metric where prediction is intended.")
    with second:
        st.markdown("- **Limits:** State what the model does not establish, including causal, fairness, or transportability claims.")
        st.markdown("- **Reproducibility:** Download the computation record for the completed module and preserve the dataset version, formula, settings, and random seed.")
        st.text_area("Final Day 3 review note", key="day3_final_review_note", placeholder="State the completed computation, its main result, the most important limitation, and the next validation or sensitivity step.")
