"""Streamlit interface components for guided, guarded no-code inference."""

from __future__ import annotations

import json
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
from inference_core import (
    METHOD_CARDS,
    audit_dataset,
    build_report,
    categorical_association,
    categorical_columns,
    descriptive_numeric_summary,
    independent_group_power,
    linear_regression,
    logistic_regression,
    method_compatibility,
    numeric_columns,
    one_sample_mean,
    one_way_anova,
    paired_comparison,
    renderable_diagnostics,
    two_group_welch,
)
from validation import InputValidationError

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
CATALOG_PATH = PROJECT_DIR / "data" / "dataset_catalog.json"


@st.cache_data
def _load_dataset_catalog(version: int) -> dict[str, dict[str, Any]]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_dataset_catalog() -> dict[str, dict[str, Any]]:
    if not CATALOG_PATH.exists():
        return {}
    return _load_dataset_catalog(CATALOG_PATH.stat().st_mtime_ns)


def metadata_for(filename: str | None) -> dict[str, Any]:
    if not filename:
        return {}
    return load_dataset_catalog().get(filename, {})


def render_dataset_audit(data: pd.DataFrame, key: str, dataset_name: str, filename: str | None = None) -> dict[str, Any]:
    """Render a common audit panel before any inferential calculation."""
    audit = audit_dataset(data, dataset_name, metadata_for(filename))
    st.subheader("Dataset audit")
    st.caption("Inference begins with data and design, not with a test name. Confirm the study context before using a method recommendation.")
    a, b, c, d = st.columns(4)
    a.metric("Rows", audit["rows"])
    b.metric("Columns", audit["columns"])
    c.metric("Complete rows", audit["complete_rows"])
    d.metric("Duplicate rows", audit["duplicate_rows"])
    st.markdown("#### Metadata card")
    st.markdown(f"**Source:** {audit['source']}")
    st.markdown(f"**License / use:** {audit['license']}")
    st.markdown(f"**Unit of observation:** {audit['unit_of_observation']}")
    st.warning(f"**Known limitations:** {audit['limitations']}")
    if audit["suitable_modules"]:
        st.info("**Suitable seminar modules:** " + ", ".join(audit["suitable_modules"]))

    details, missing = st.tabs(["Variable dictionary", "Missingness and data quality"])
    with details:
        st.dataframe(audit["variable_table"], width="stretch", hide_index=True)
        st.caption("The local CSV provides field names and values. Confirm substantive meanings, coding, and measurement scales in source documentation.")
    with missing:
        st.dataframe(audit["missing_table"], width="stretch", hide_index=True)
        checks = []
        if audit["constant_columns"]:
            checks.append("Constant variables: " + ", ".join(audit["constant_columns"]))
        if audit["duplicate_rows"]:
            checks.append(f"{audit['duplicate_rows']} duplicated row(s) detected; verify whether duplicates are data errors or valid repeated records.")
        if audit["missing_cells"]:
            checks.append(f"{audit['missing_cells']} missing cell(s) detected; document the missing-data treatment before analysis.")
        if checks:
            for item in checks:
                st.warning(item)
        else:
            st.success("No constant variables, duplicate rows, or missing cells were detected by the automated audit.")
        if audit["missing_cells"]:
            st.markdown("**Missingness is an inferential choice, not merely data cleaning.** The app cannot determine whether values are missing completely at random (MCAR), missing at random conditional on observed variables (MAR), or missing not at random (MNAR). Complete-case analysis can be biased when missingness is informative, and treating missingness as a category changes the estimand.")
            st.checkbox("I acknowledge that I must document and justify the missing-data rule before making an inferential claim.", key=f"{key}_audit_missingness_ack")
    return audit


def render_question_to_method(manifest: dict, key: str = "wizard") -> None:
    """Render a design-first, transparent recommendation pathway without asking for a test name."""
    st.title("Guided inference pathway")
    st.caption("Describe the question and design first. The app derives compatible seminar pathways; it does not infer study design or replace statistical judgment.")
    question = st.text_area("1. State your research question in one sentence", placeholder="Example: How does mean birth weight differ between the selected groups?", key=f"{key}_question")
    left, middle, right = st.columns(3)
    with left:
        outcome_type = st.selectbox("2. Outcome structure", ["Continuous / numeric", "Binary", "Categorical", "Count", "Ordinal", "Time-to-event"], key=f"{key}_outcome_type")
    with middle:
        explanatory_type = st.selectbox("3. Explanatory variable or comparison structure", ["None / estimation", "Two groups", "Three or more groups", "One or more predictors", "Two categorical variables"], key=f"{key}_explanatory_type")
    with right:
        design = st.selectbox("4. Dependence / design", ["Independent observational units", "Paired or matched measurements", "Repeated / clustered / longitudinal", "Unknown — investigate before analysis"], key=f"{key}_design")
    aim = st.selectbox("5. Primary inferential aim", ["Estimation", "Comparison", "Association", "Prediction", "Causal interpretation (requires design justification)"], key=f"{key}_aim")
    if aim == "Causal interpretation (requires design justification)":
        st.warning("The app does not establish causality. Record the intervention, identification strategy, confounding assumptions, and target population before any causal claim.")
    recommendations = method_compatibility(outcome_type, explanatory_type, design, aim)
    compatible = [item for item in recommendations if item["status"] == "Compatible"]
    caution = [item for item in recommendations if item["status"] == "Caution"]
    st.subheader("Derived pathway compatibility")
    if compatible:
        st.success("Compatible pathways are shown below. Confirm the dataset-specific requirements in the next step before fitting a model.")
    else:
        st.warning("No simple app workflow is compatible with the recorded features. Review the design, use the relevant theory module, or seek design-specific advice rather than forcing a method.")
    st.dataframe(pd.DataFrame(recommendations)[["status", "method", "reason", "modules"]], width="stretch", hide_index=True)
    module_map = {module["id"]: module for day in manifest["days"] for module in day["modules"]}
    recommended_rows = []
    for item in compatible + caution:
        card = METHOD_CARDS[item["key"]]
        for module_id in card["module_ids"]:
            module = module_map.get(module_id)
            if module:
                recommended_rows.append({"Status": item["status"], "Module": module["id"].upper(), "Title": module["title"], "Question prompt": module["research_question_prompt"]})
    if recommended_rows:
        st.markdown("**Relevant seminar modules:**")
        st.dataframe(pd.DataFrame(recommended_rows), width="stretch", hide_index=True)
    if question.strip():
        st.info("Your question and design summary are retained in this browser session and will be included in a compatible analysis record.")
        st.session_state[f"{key}_question_value"] = question.strip()
        st.session_state[f"{key}_design_summary"] = {"outcome_type": outcome_type, "explanatory_type": explanatory_type, "design": design, "aim": aim, "compatible_pathways": [item["method"] for item in compatible], "compatible_pathway_keys": [item["key"] for item in compatible]}


def _display_result(result: dict[str, Any]) -> None:
    st.subheader("Standardized result record")
    headers = [
        ("Question", result["question"]),
        ("Data and design", result["data_design"]),
        ("Method", result["method"]),
        ("Assumptions", result["assumptions"]),
        ("Diagnostics", result["diagnostics"]),
        ("Estimate", result["estimate"]),
        ("Uncertainty", result["uncertainty"]),
        ("Effect size", result["effect_size"]),
        ("Test statistic and p-value", result["test"]),
        ("Interpretation", result["interpretation"]),
        ("Limitations", result["limitations"]),
        ("Next step", result["next_step"]),
    ]
    for heading, value in headers:
        with st.expander(heading, expanded=heading in {"Question", "Estimate", "Uncertainty", "Interpretation"}):
            if heading == "Assumptions":
                for item in value:
                    st.markdown(f"- {item}")
            elif heading == "Diagnostics":
                for item in renderable_diagnostics(value):
                    st.markdown(f"- {item}")
                if "table" in result.get("details", {}):
                    st.dataframe(result["details"]["table"], width="stretch")
                if "expected" in result.get("details", {}):
                    st.caption("Expected counts under the independence model")
                    st.dataframe(result["details"]["expected"].round(2), width="stretch")
            elif isinstance(value, pd.DataFrame):
                st.dataframe(value, width="stretch")
            else:
                st.write(value)


def _render_linear_diagnostics(result: dict[str, Any], predictor: str, outcome: str, data: pd.DataFrame, key: str) -> None:
    details = result["details"]
    coefficient_count = len(details["coefficients"].index) - 1
    if coefficient_count > 1:
        st.caption(f"The observed outcome-versus-{predictor} panel is a first-predictor visualization only. It is not a partial-residual or adjusted-effect plot for the full multivariable model.")
    subset = data[[outcome, predictor]].dropna()
    plot_data = pd.DataFrame({"Fitted value": details["fitted"], "Residual": details["residuals"], "Cook's distance": details["cooks_distance"]})
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.scatter(plot_data, x="Fitted value", y="Residual", hover_data=["Cook's distance"], title="Residuals versus fitted values", template="plotly_white"), width="stretch", key=f"{key}_residuals")
    with right:
        st.plotly_chart(px.scatter(subset, x=predictor, y=outcome, title=f"Observed {outcome} by first selected predictor: {predictor}", template="plotly_white"), width="stretch", key=f"{key}_scatter")


def render_guarded_analysis(data: pd.DataFrame, audit: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Render analysis families with test-specific data checks and a common output structure."""
    st.subheader("Guided analysis")
    st.caption("Use this after the audit. The calculation is conditional on the selected variables and cannot verify study design, causal identification, or substantive relevance.")
    available: list[str] = []
    nums, cats = numeric_columns(data), categorical_columns(data)
    if nums:
        available.append("estimate_mean")
    if nums and cats:
        available.extend(["two_independent", "anova"])
    if len(nums) >= 2:
        available.extend(["paired", "linear_regression"])
    if len(cats) >= 2:
        available.append("association")
    binary_candidates = [name for name in cats if data[name].dropna().astype(str).nunique() == 2]
    if binary_candidates and nums:
        available.append("logistic_regression")
    guided_keys = st.session_state.get("wizard_design_summary", {}).get("compatible_pathway_keys", [])
    if guided_keys:
        compatible_available = [item for item in available if item in guided_keys]
        if compatible_available:
            available = compatible_available
            st.info("The available analyses are filtered to pathways compatible with your recorded question and design. Revisit Guided Inference to change the design description.")
        else:
            st.warning("The recorded design has no compatible simple workflow for this dataset. Revisit Guided Inference or seek design-specific advice; the app will not force a method.")
            return None
    if not available:
        st.warning("This dataset has no supported analysis pathway with its currently detected variable structure. Use the data audit to verify variable coding or choose another workflow.")
        return None
    method_key = st.selectbox("Compatible analysis pathway", available, format_func=lambda item: METHOD_CARDS[item]["label"], key=f"{key}_analysis_purpose")
    result: dict[str, Any] | None = None
    selections: dict[str, Any] = {"analysis purpose": METHOD_CARDS[method_key]["label"]}
    try:
        if method_key == "estimate_mean":
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_mean_outcome")
            selections["outcome"] = outcome
            finite_values = pd.to_numeric(data[outcome], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            if finite_values.nunique() < 2:
                st.info("The selected outcome is constant after missing-value handling. A t interval is undefined, so the app provides a descriptive-only summary rather than forcing an inferential calculation.")
                result = descriptive_numeric_summary(data, outcome)
            else:
                result = one_sample_mean(data, outcome)
        elif method_key == "two_independent":
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_two_outcome")
            group = st.selectbox("Grouping variable", cats, key=f"{key}_two_group")
            levels = sorted(data[group].dropna().astype(str).unique().tolist())
            chosen = st.multiselect("Choose exactly two groups", levels, default=levels[:2], max_selections=2, key=f"{key}_two_levels")
            if len(chosen) != 2:
                st.info("Choose exactly two groups to continue.")
                return None
            if min((data.loc[data[group].astype(str) == level, outcome].dropna().shape[0] for level in chosen), default=0) < 2:
                st.warning("Each selected group requires at least two complete observations.")
                return None
            selections.update({"outcome": outcome, "group": group, "levels": chosen})
            result = two_group_welch(data, outcome, group, chosen)
            st.markdown("##### Prospective planning context")
            st.caption("Choose a substantively meaningful standardized effect size for future study planning. The observed effect is intentionally not used as the planning effect.")
            planning_effect = st.number_input("Target standardized effect size (Cohen's d)", min_value=0.01, max_value=5.0, value=0.50, step=0.05, key=f"{key}_planning_effect")
            target_power = st.select_slider("Target power", options=[0.70, 0.80, 0.90, 0.95], value=0.80, key=f"{key}_target_power")
            power = independent_group_power(float(planning_effect), min(result["details"]["n_first"], result["details"]["n_second"]), target_power=float(target_power))
            st.info(f"For a planning effect size of d = {power['planning_effect_size']:.2f}, current smaller-group size {min(result['details']['n_first'], result['details']['n_second'])}, and target power {power['target_power']:.0%}, estimated power is {power['power']:.2f}. About {power['n_per_group_for_target_power']:.0f} observations per group are required under these prospective assumptions.")
            selections.update({"planning effect size": planning_effect, "target power": target_power})
        elif method_key == "paired":
            first = st.selectbox("First paired measurement", nums, key=f"{key}_paired_first")
            second = st.selectbox("Second paired measurement", [name for name in nums if name != first], key=f"{key}_paired_second")
            selections.update({"first measurement": first, "second measurement": second})
            result = paired_comparison(data, first, second)
        elif method_key == "anova":
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_anova_outcome")
            group = st.selectbox("Grouping variable", cats, key=f"{key}_anova_group")
            if data[group].dropna().astype(str).nunique() < 3:
                st.warning("A one-way comparison requires at least three observed groups. Use the two-group workflow instead.")
                return None
            selections.update({"outcome": outcome, "group": group})
            result = one_way_anova(data, outcome, group)
        elif method_key == "association":
            first = st.selectbox("First categorical variable", cats, key=f"{key}_assoc_first")
            second = st.selectbox("Second categorical variable", [name for name in cats if name != first], key=f"{key}_assoc_second")
            missing_rows = int(data[[first, second]].isna().any(axis=1).sum())
            missing_rule = st.radio(
                "Missing-data rule for this association",
                options=["complete_case", "substantive_missing_category"],
                format_func=lambda value: "Complete-case analysis (default)" if value == "complete_case" else "Treat missing values as a substantive category — use only if scientifically justified",
                key=f"{key}_assoc_missing_rule",
            )
            if missing_rule == "complete_case":
                st.info(f"Complete-case analysis will exclude {missing_rows} row(s) with a missing value in either selected variable. This can be biased if missingness is informative; the app cannot determine whether MCAR, MAR, or MNAR reasoning is appropriate.")
            else:
                st.warning("This option inserts ‘Missing’ into the contingency table as an analytic category. Use it only when missingness is scientifically meaningful and you can justify that estimand.")
            if missing_rows and not st.checkbox("I acknowledge that missing-data handling is an inferential choice and have selected the rule intentionally.", key=f"{key}_assoc_missing_ack"):
                st.info("Acknowledge the missing-data rule to run the association analysis.")
                return None
            selections.update({"first variable": first, "second variable": second, "missing-data rule": missing_rule, "rows with missing values in either selected variable": missing_rows})
            result = categorical_association(data, first, second, missing_rule=missing_rule)
        elif method_key == "linear_regression":
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_linear_outcome")
            predictors = st.multiselect("Numeric predictor(s)", [name for name in nums if name != outcome], default=[name for name in nums if name != outcome][:1], key=f"{key}_linear_predictors")
            if not predictors:
                st.info("Choose at least one numeric predictor.")
                return None
            selections.update({"outcome": outcome, "predictors": predictors})
            result = linear_regression(data, outcome, predictors)
            _render_linear_diagnostics(result, predictors[0], outcome, data, key)
        else:
            outcome = st.selectbox("Binary outcome", binary_candidates, key=f"{key}_logit_outcome")
            eligible_predictors = [name for name in nums if name != outcome]
            if not eligible_predictors:
                st.warning("Choose a dataset with at least one numeric predictor distinct from the binary outcome.")
                return None
            predictors = st.multiselect("Numeric predictor(s)", eligible_predictors, default=eligible_predictors[:1], key=f"{key}_logit_predictors")
            if not predictors:
                st.info("Choose at least one numeric predictor.")
                return None
            selections.update({"outcome": outcome, "predictors": predictors})
            result = logistic_regression(data, outcome, predictors)
    except InputValidationError as error:
        st.warning(f"This analysis is not available for the current selections: {error}")
        return None
    except (ValueError, np.linalg.LinAlgError) as error:
        st.error(f"This model could not be fit with the current selections: {error}")
        return None
    if result is None:
        return None
    guided_question = st.session_state.get("wizard_question_value")
    guided_design = st.session_state.get("wizard_design_summary", {})
    if guided_question:
        result["question"] = guided_question
        selections["guided research question"] = guided_question
    for selection_name, selection_value in guided_design.items():
        selections[f"guided {selection_name.replace('_', ' ')}"] = selection_value
    _display_result(result)
    include_details = st.checkbox("Include detailed tables, expected counts / coefficient tables, and diagnostic references in the report", value=False, key=f"{key}_report_details")
    report = build_report(result, audit, selections, include_details=include_details)
    st.download_button("Download reproducibility record (Markdown)", report, file_name=f"{key}_inference_record.md", mime="text/markdown", key=f"{key}_report")
    return result


def _day3_report_download(result: dict[str, Any], audit: dict[str, Any], selections: dict[str, Any], key: str) -> None:
    """Offer the same explicit record for every Day 3 computation."""
    report = build_report(result, audit, selections, include_details=True)
    st.download_button(
        "Download interpretation and reproducibility record (Markdown)",
        report,
        file_name=f"{key}_day3_model_record.md",
        mime="text/markdown",
        key=f"{key}_day3_report",
    )


def _day3_categorical_candidates(data: pd.DataFrame, outcome: str, numeric_selected: list[str]) -> list[str]:
    """Offer only small, non-overlapping factors for transparent treatment coding."""
    return [
        name
        for name in categorical_columns(data)
        if name != outcome and name not in numeric_selected and 2 <= data[name].dropna().astype(str).nunique() <= 12
    ]


def _render_day3_linear_lab(data: pd.DataFrame, audit: dict[str, Any], key: str, module_id: str) -> None:
    """Show linear regression, specification, uncertainty, and diagnostic calculations."""
    st.subheader("Day 3 linear-model laboratory")
    module_messages = {
        "d3m01": "Fit one conditional-mean line, then read its fitted values and residuals.",
        "d3m02": "Add predictors only when the conditional comparison and adjustment rationale are explicit.",
        "d3m03": "Compare conventional and heteroskedasticity-consistent coefficient uncertainty; neither is a prediction interval.",
        "d3m04": "Compare a defensible functional form, transformation, or numeric interaction without searching indiscriminately.",
        "d3m08": "Use residual, leverage, Cook's-distance, and collinearity diagnostics as prompts for investigation rather than deletion rules.",
        "d3m10": "Build an explicit specification and download the corresponding interpretation and reproducibility record.",
    }
    st.caption(module_messages.get(module_id, "Fit a documented linear model and inspect its diagnostics."))
    numeric = numeric_columns(data)
    if len(numeric) < 2:
        st.info("This laboratory needs a numeric outcome and at least one distinct numeric predictor.")
        return
    outcome = st.selectbox("Numeric outcome", numeric, key=f"{key}_d3_linear_outcome")
    available_numeric = [name for name in numeric if name != outcome]
    if module_id == "d3m01":
        numeric_predictors = [st.selectbox("Numeric predictor", available_numeric, key=f"{key}_d3_linear_predictor")]
    else:
        numeric_predictors = st.multiselect(
            "Numeric predictor(s)",
            available_numeric,
            default=available_numeric[: min(2, len(available_numeric))],
            key=f"{key}_d3_linear_predictors",
        )
    if not numeric_predictors:
        st.info("Select at least one numeric predictor.")
        return
    categorical_predictors: list[str] = []
    if module_id in {"d3m02", "d3m04", "d3m08", "d3m10"}:
        categorical_predictors = st.multiselect(
            "Optional categorical predictor(s) — treatment coded",
            _day3_categorical_candidates(data, outcome, numeric_predictors),
            key=f"{key}_d3_linear_categorical",
        )
    quadratic_predictor = None
    log1p_predictor = None
    interaction = None
    if module_id == "d3m04":
        with st.expander("Specification choices — record a rationale before comparing models", expanded=True):
            form = st.selectbox(
                "Functional form for one selected numeric predictor",
                ["Linear only", "Add a quadratic term", "Add a log1p transformation"],
                key=f"{key}_d3_form",
            )
            target = st.selectbox("Predictor for this form choice", numeric_predictors, key=f"{key}_d3_form_target")
            if form == "Add a quadratic term":
                quadratic_predictor = target
            elif form == "Add a log1p transformation":
                log1p_predictor = target
            if len(numeric_predictors) >= 2 and st.checkbox("Add one numeric × numeric interaction", key=f"{key}_d3_interaction_enabled"):
                left = st.selectbox("First interaction predictor", numeric_predictors, key=f"{key}_d3_interaction_left")
                right = st.selectbox("Second interaction predictor", [name for name in numeric_predictors if name != left], key=f"{key}_d3_interaction_right")
                interaction = (left, right)
    try:
        result = fit_day3_linear_model(
            data,
            outcome,
            numeric_predictors,
            categorical_predictors,
            quadratic_predictor=quadratic_predictor,
            log1p_predictor=log1p_predictor,
            interaction=interaction,
        )
    except InputValidationError as error:
        st.warning(f"This model is not available for the current selections: {error}")
        return
    details = result["details"]
    cases = details["diagnostic_cases"]
    largest_cooks_distance = cases["Cook's distance"].max()
    a, b, c, d = st.columns(4)
    a.metric("Complete records", details["n"])
    b.metric("R²", f"{result['_model'].rsquared:.3f}")
    c.metric("Largest Cook's distance", f"{largest_cooks_distance:.3f}")
    d.metric("Leverage screen", f"{result['diagnostics']['leverage_screen']:.3f}")
    model_tabs = st.tabs(["Coefficients and uncertainty", "Residual structure", "Influence and collinearity", "Interpretation record"])
    with model_tabs[0]:
        st.caption("Terms in the fitted model: " + ", ".join(details["formula_terms"]))
        left, right = st.columns(2)
        with left:
            st.markdown("**Conventional coefficient intervals**")
            st.dataframe(details["coefficients"], width="stretch")
        with right:
            st.markdown("**HC3 robust coefficient intervals**")
            st.dataframe(details["robust_hc3_coefficients"], width="stretch")
        st.info("HC3 changes the coefficient uncertainty calculation when residual variance may vary; it does not repair an omitted variable, dependence, a poor functional form, or a causal-design problem.")
    with model_tabs[1]:
        left, right = st.columns(2)
        with left:
            residual_plot = px.scatter(cases, x="Fitted", y="Residual", hover_data=["Row", "Cook's distance"], title="Residuals versus fitted values", template="plotly_white")
            residual_plot.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(residual_plot, width="stretch", key=f"{key}_d3_residual_plot")
        with right:
            qq = details["qq_points"]
            qq_plot = px.scatter(qq, x="Normal theoretical quantile", y="Ordered standardized residual", title="Quantile–quantile diagnostic", template="plotly_white")
            st.plotly_chart(qq_plot, width="stretch", key=f"{key}_d3_qq_plot")
        st.caption("Curvature, a funnel pattern, or extreme tails are evidence to investigate measurement, functional form, variance structure, and support. They do not prove a single repair.")
    with model_tabs[2]:
        left, right = st.columns(2)
        with left:
            influence_plot = px.scatter(
                cases,
                x="Leverage",
                y="Standardized residual",
                size="Cook's distance",
                hover_data=["Row", "Fitted", "Residual"],
                title="Leverage, standardized residuals, and Cook's distance",
                template="plotly_white",
            )
            influence_plot.add_vline(x=result["diagnostics"]["leverage_screen"], line_dash="dash", line_color="orange")
            st.plotly_chart(influence_plot, width="stretch", key=f"{key}_d3_influence_plot")
        with right:
            st.markdown("**Variance-inflation factors**")
            st.dataframe(details["vif"], width="stretch", hide_index=True)
            st.markdown("**Diagnostic screens**")
            st.write({
                "Breusch–Pagan p-value": result["diagnostics"].get("breusch_pagan", {}).get("p_value"),
                "Cases above leverage screen": result["diagnostics"]["observations_above_leverage_screen"],
                "Cases above Cook's-distance screen": result["diagnostics"]["observations_above_cooks_screen"],
            })
        st.warning("A diagnostic screen identifies records or assumptions to investigate. Do not remove a case merely because it is influential or produces an inconvenient coefficient.")
    with model_tabs[3]:
        st.markdown("**Model-based interpretation**")
        st.write(result["interpretation"])
        st.markdown("**Limitations to record**")
        st.write(result["limitations"])
        _day3_report_download(
            result,
            audit,
            {
                "module": module_id.upper(),
                "outcome": outcome,
                "numeric predictors": numeric_predictors,
                "categorical predictors": categorical_predictors,
                "quadratic predictor": quadratic_predictor or "None",
                "log1p predictor": log1p_predictor or "None",
                "numeric interaction": " × ".join(interaction) if interaction else "None",
            },
            key,
        )


def _render_day3_logistic_lab(data: pd.DataFrame, audit: dict[str, Any], key: str, module_id: str) -> None:
    """Show odds, probability, threshold, calibration, and receiver-operating-characteristic calculations."""
    st.subheader("Day 3 binary-outcome prediction laboratory")
    module_messages = {
        "d3m05": "Fit log odds and translate selected results into predicted probabilities rather than treating an odds ratio as a risk ratio.",
        "d3m06": "Move the threshold deliberately and inspect the resulting false-positive and false-negative trade-off.",
        "d3m07": "Separate probability calibration from discrimination; a strong ranking is not necessarily a well-calibrated probability model.",
    }
    st.caption(module_messages.get(module_id, "Fit and examine a documented binary-outcome model."))
    binary_outcomes = [name for name in categorical_columns(data) if data[name].dropna().astype(str).nunique() == 2]
    numeric = numeric_columns(data)
    if not binary_outcomes or not numeric:
        st.info("This laboratory needs a documented binary outcome and at least one numeric predictor.")
        return
    outcome = st.selectbox("Binary outcome", binary_outcomes, key=f"{key}_d3_logit_outcome")
    available_numeric = [name for name in numeric if name != outcome]
    if not available_numeric:
        st.info("Select a dataset with a numeric predictor distinct from the binary outcome.")
        return
    numeric_predictors = st.multiselect(
        "Numeric predictor(s)",
        available_numeric,
        default=available_numeric[: min(2, len(available_numeric))],
        key=f"{key}_d3_logit_predictors",
    )
    if not numeric_predictors:
        st.info("Select at least one numeric predictor.")
        return
    categorical_predictors = st.multiselect(
        "Optional categorical predictor(s) — treatment coded",
        _day3_categorical_candidates(data, outcome, numeric_predictors),
        key=f"{key}_d3_logit_categorical",
    )
    try:
        result = fit_day3_logistic_model(data, outcome, numeric_predictors, categorical_predictors)
    except InputValidationError as error:
        st.warning(f"This logistic model is not available for the current selections: {error}")
        return
    details = result["details"]
    probabilities = result["_probabilities"]
    observed = result["_outcome"]
    a, b, c, d = st.columns(4)
    a.metric("Complete records", details["n"])
    b.metric("Event outcome", details["event_level"])
    c.metric("In-sample AUC", f"{result['diagnostics']['area_under_roc_curve']:.3f}")
    d.metric("In-sample Brier score", f"{result['diagnostics']['brier_score']:.4f}")
    model_tabs = st.tabs(["Odds and probabilities", "Calibration", "Threshold consequences", "Discrimination", "Interpretation record"])
    with model_tabs[0]:
        left, right = st.columns(2)
        with left:
            st.dataframe(details["coefficients"], width="stretch")
        with right:
            cases = details["probability_cases"]
            probability_plot = px.scatter(
                cases,
                x="Row",
                y="Predicted probability",
                color="Observed event",
                title="Predicted probabilities by observation",
                template="plotly_white",
            )
            st.plotly_chart(probability_plot, width="stretch", key=f"{key}_d3_probability_plot")
        st.info("Odds ratios compare odds, not probabilities. The probability impact of a predictor depends on the starting covariate values and the selected reference outcome.")
    with model_tabs[1]:
        calibration = details["calibration"]
        calibration_plot = px.scatter(
            calibration,
            x="Mean_predicted_probability",
            y="Observed_event_rate",
            size="Records",
            hover_data=["Bin", "Records"],
            title="Binned calibration display",
            template="plotly_white",
        )
        calibration_plot.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(calibration_plot, width="stretch", key=f"{key}_d3_calibration_plot")
        st.dataframe(calibration, width="stretch", hide_index=True)
        st.caption("Binned calibration is descriptive and can be unstable in small bins. Calibration on the same data used to fit the model is optimistic.")
    with model_tabs[2]:
        threshold = st.slider("Classification threshold", min_value=0.05, max_value=0.95, value=0.50, step=0.05, key=f"{key}_d3_threshold")
        metrics = classification_metrics(observed, probabilities, threshold)
        first, second, third, fourth = st.columns(4)
        first.metric("Sensitivity", f"{metrics['sensitivity']:.3f}")
        second.metric("Specificity", f"{metrics['specificity']:.3f}")
        third.metric("Positive predictive value", f"{metrics['positive_predictive_value']:.3f}")
        fourth.metric("Accuracy", f"{metrics['accuracy']:.3f}")
        st.dataframe(
            pd.DataFrame(
                [{"Predicted / observed": "Positive", "Observed event": metrics["true_positive"], "Observed non-event": metrics["false_positive"]}, {"Predicted / observed": "Negative", "Observed event": metrics["false_negative"], "Observed non-event": metrics["true_negative"]}],
            ),
            width="stretch",
            hide_index=True,
        )
        st.warning("A threshold is a decision choice. Select it from the costs, benefits, and fairness implications of false positives and false negatives—not because 0.50 is conventional.")
    with model_tabs[3]:
        roc = details["roc"]
        roc_plot = px.line(roc, x="False positive rate", y="True positive rate", title="Receiver-operating-characteristic curve", template="plotly_white")
        roc_plot.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(roc_plot, width="stretch", key=f"{key}_d3_roc_plot")
        st.caption(f"Area under the curve = {result['diagnostics']['area_under_roc_curve']:.3f}. It is the tie-aware probability that a randomly selected event receives a higher score than a randomly selected non-event; it does not measure calibration.")
    with model_tabs[4]:
        st.markdown("**Model-based interpretation**")
        st.write(result["interpretation"])
        st.markdown("**Limitations to record**")
        st.write(result["limitations"])
        _day3_report_download(
            result,
            audit,
            {"module": module_id.upper(), "binary outcome": outcome, "numeric predictors": numeric_predictors, "categorical predictors": categorical_predictors},
            key,
        )


def _render_day3_validation_lab(data: pd.DataFrame, audit: dict[str, Any], key: str, filename: str | None = None) -> None:
    """Show an internal split or the named Pima train/test validation calculation."""
    st.subheader("Day 3 train/test validation laboratory")
    numeric = numeric_columns(data)
    named_pima_test = filename == "pima_test.csv"
    if named_pima_test:
        st.caption("This worked dataset is the named Pima test file. The app fits the selected logistic model on the bundled Pima training file and evaluates it once on this separate test file.")
        outcome = "type"
        predictors = st.multiselect(
            "Numeric predictor(s) fitted on Pima training data",
            [name for name in numeric if name != outcome],
            default=[name for name in ["glu", "bmi", "age"] if name in numeric],
            key=f"{key}_d3_external_validation_predictors",
        )
        if not predictors:
            st.info("Select at least one numeric predictor.")
            return
        try:
            training = pd.read_csv(PROJECT_DIR / "data" / "public" / "pima_train.csv").drop(columns="rownames", errors="ignore")
            result = external_logistic_validation(training, data, outcome, predictors)
        except InputValidationError as error:
            st.warning(f"This external-file validation calculation is not available for the current selections: {error}")
            return
        model_kind = "logistic"
        validation_selections = {"module": "D3M09", "validation design": "Bundled Pima training file → bundled Pima test file", "outcome": outcome, "model family": model_kind, "numeric predictors": predictors}
    else:
        st.caption("The app creates one deterministic internal split. It keeps test records out of fitting, but it does not replace grouped, temporal, or external validation when those match deployment.")
        binary = [name for name in categorical_columns(data) if data[name].dropna().astype(str).nunique() == 2]
        choices: list[tuple[str, str]] = [(name, "logistic") for name in binary] + [(name, "linear") for name in numeric if name not in binary]
        if not choices:
            st.info("This laboratory needs either a binary outcome or a numeric outcome plus numeric predictors.")
            return
        outcome, model_kind = st.selectbox(
            "Outcome and model family",
            choices,
            format_func=lambda item: f"{item[0]} — {'binary logistic model' if item[1] == 'logistic' else 'continuous-outcome linear model'}",
            key=f"{key}_d3_validation_outcome",
        )
        predictors = st.multiselect(
            "Numeric predictor(s)",
            [name for name in numeric if name != outcome],
            default=[name for name in numeric if name != outcome][: min(2, max(0, len(numeric) - 1))],
            key=f"{key}_d3_validation_predictors",
        )
        if not predictors:
            st.info("Select at least one numeric predictor.")
            return
        first, second = st.columns(2)
        with first:
            test_fraction = st.select_slider("Test-set fraction", options=[0.20, 0.25, 0.30, 0.33], value=0.25, key=f"{key}_d3_validation_fraction")
        with second:
            seed = st.number_input("Split seed", min_value=1, max_value=999999, value=2026, step=1, key=f"{key}_d3_validation_seed")
        try:
            result = holdout_validation(data, outcome, predictors, model_kind=model_kind, test_fraction=float(test_fraction), seed=int(seed))
        except InputValidationError as error:
            st.warning(f"This validation calculation is not available for the current selections: {error}")
            return
        validation_selections = {"module": "D3M09", "validation design": "Deterministic internal holdout", "outcome": outcome, "model family": model_kind, "numeric predictors": predictors, "test fraction": test_fraction, "split seed": int(seed)}
    st.dataframe(result["estimate"], width="stretch", hide_index=True)
    if model_kind == "logistic":
        roc = result["details"]["roc"]
        roc_plot = px.line(roc, x="False positive rate", y="True positive rate", title="Held-out receiver-operating-characteristic curve", template="plotly_white")
        roc_plot.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(roc_plot, width="stretch", key=f"{key}_d3_validation_roc")
        st.dataframe(result["details"]["calibration"], width="stretch", hide_index=True)
    else:
        predictions = result["details"]["test_predictions"]
        prediction_plot = px.scatter(predictions, x="Observed", y="Predicted", hover_data=["Row", "Residual"], title="Held-out observed versus predicted values", template="plotly_white")
        low = min(predictions["Observed"].min(), predictions["Predicted"].min())
        high = max(predictions["Observed"].max(), predictions["Predicted"].max())
        prediction_plot.add_shape(type="line", x0=low, y0=low, x1=high, y1=high, line={"dash": "dash", "color": "gray"})
        st.plotly_chart(prediction_plot, width="stretch", key=f"{key}_d3_validation_predictions")
    st.warning("Do not revise the model repeatedly using the displayed test performance. That leaks test information into model selection and makes the reported metric optimistic.")
    _day3_report_download(result, audit, validation_selections, key)


def render_day3_analysis(data: pd.DataFrame, audit: dict[str, Any], key: str, module_id: str, filename: str | None = None) -> None:
    """Route a Day 3 module to calculations that match its teaching focus."""
    if module_id in {"d3m01", "d3m02", "d3m03", "d3m04", "d3m08", "d3m10"}:
        _render_day3_linear_lab(data, audit, key, module_id)
    elif module_id in {"d3m05", "d3m06", "d3m07"}:
        _render_day3_logistic_lab(data, audit, key, module_id)
    elif module_id == "d3m09":
        _render_day3_validation_lab(data, audit, key, filename)
    else:
        st.warning("This Day 3 module has no registered computation laboratory.")


def render_workspace(data: pd.DataFrame, key: str, dataset_name: str, filename: str | None = None, module_id: str | None = None) -> None:
    """Render a data/design, computation, and interpretation-record workflow."""
    learn, practice, audit_mode = st.tabs(["1. Inspect data and design", "2. Run the method-appropriate analysis", "3. Interpret, limitations & reproducibility"])
    with learn:
        audit = render_dataset_audit(data, key, dataset_name, filename)
    with practice:
        audit = audit_dataset(data, dataset_name, metadata_for(filename))
        if module_id and module_id.startswith("d3m"):
            render_day3_analysis(data, audit, key, module_id, filename)
        else:
            render_guarded_analysis(data, audit, key)
    with audit_mode:
        st.subheader("Interpret the result, state limitations, and document the analysis")
        st.caption("This replaces the vague label “Audit the claim.” Use this tab to turn a calculation into a bounded, reproducible statement.")
        st.markdown("- **Target and unit:** What population, prediction setting, and unit of observation does this analysis address?")
        st.markdown("- **Specification:** Which variables, coding choices, transformations, missing-data rules, exclusions, and thresholds were used?")
        st.markdown("- **Assumptions and diagnostics:** Which conditions are design facts, and which have only been explored diagnostically?")
        st.markdown("- **Practical meaning:** What do the estimate, probabilities, prediction metrics, and uncertainty mean on the relevant scale?")
        st.markdown("- **Limitations:** What does the result **not** establish, including causal, fairness, practical-importance, or transportability claims?")
        st.text_area("Write an interpretation, limitation, or next analysis step", key=f"{key}_audit_note", placeholder="State the main limitation, the diagnostic finding to investigate, or the next validation step.")
