"""Streamlit interface components for guided, guarded no-code inference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from inference_core import (
    METHOD_CARDS,
    audit_dataset,
    build_report,
    categorical_association,
    categorical_columns,
    independent_group_power,
    linear_regression,
    logistic_regression,
    numeric_columns,
    one_sample_mean,
    one_way_anova,
    paired_comparison,
    renderable_diagnostics,
    two_group_welch,
)

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
    return audit


def render_question_to_method(manifest: dict, key: str = "wizard") -> None:
    """Render the Learn/Choose question-first decision aid."""
    st.title("Guided inference pathway")
    st.caption("Start with a research question and study design. The app recommends a seminar pathway; it does not replace subject-matter or design judgment.")
    purpose = st.selectbox(
        "What is the main purpose of your analysis?",
        list(METHOD_CARDS),
        format_func=lambda item: METHOD_CARDS[item]["label"],
        key=f"{key}_purpose",
    )
    card = METHOD_CARDS[purpose]
    left, middle, right = st.columns(3)
    with left:
        outcome_type = st.selectbox("Outcome structure", ["Continuous / numeric", "Binary", "Categorical", "Count", "Ordinal", "Time-to-event"], key=f"{key}_outcome_type")
    with middle:
        explanatory_type = st.selectbox("Explanatory variable or comparison structure", ["None / estimation", "Two groups", "Three or more groups", "One or more predictors", "Two categorical variables"], key=f"{key}_explanatory_type")
    with right:
        design = st.selectbox("Dependence / design", ["Independent observational units", "Paired or matched measurements", "Repeated / clustered / longitudinal", "Unknown — investigate before analysis"], key=f"{key}_design")
    aim = st.selectbox("Primary inferential aim", ["Estimation", "Comparison", "Association", "Prediction", "Causal interpretation (requires design justification)"], key=f"{key}_aim")
    question = st.text_area("State your research question in one sentence", placeholder="Example: How does mean birth weight differ between the selected groups?", key=f"{key}_question")
    st.subheader(f"Recommended pathway: {card['method']}")
    st.markdown(f"**Required data structure:** {card['requirements']}")
    st.markdown("**Before calculation, check:**")
    for warning in card["warnings"]:
        st.warning(warning)
    if purpose == "two_independent" and design != "Independent observational units":
        st.warning("The selected design is not compatible with a simple independent-groups pathway. Consider the paired/repeated-measures material or seek design-specific advice.")
    if purpose == "paired" and design != "Paired or matched measurements":
        st.warning("A paired comparison requires documented matching or repeated measurement; do not infer pairing from similarly named columns.")
    if aim == "Causal interpretation (requires design justification)":
        st.warning("None of the automated method recommendations establishes causality. Record the intervention, identification strategy, confounding assumptions, and target population separately.")
    module_map = {module["id"]: module for day in manifest["days"] for module in day["modules"]}
    pathways = [module_map[module_id] for module_id in card["module_ids"] if module_id in module_map]
    if pathways:
        st.markdown("**Relevant seminar modules:**")
        st.dataframe(pd.DataFrame([{"Module": module["id"].upper(), "Title": module["title"], "Question prompt": module["research_question_prompt"]} for module in pathways]), width="stretch", hide_index=True)
    if question.strip():
        st.info("Your question has been recorded in the session and will be included in an exported analysis record when you run a compatible workflow.")
        st.session_state[f"{key}_question_value"] = question.strip()
        st.session_state[f"{key}_design_summary"] = {"outcome_type": outcome_type, "explanatory_type": explanatory_type, "design": design, "aim": aim}


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
    subset = data[[outcome, predictor]].dropna()
    plot_data = pd.DataFrame({"Fitted value": details["fitted"], "Residual": details["residuals"], "Cook's distance": details["cooks_distance"]})
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.scatter(plot_data, x="Fitted value", y="Residual", hover_data=["Cook's distance"], title="Residuals versus fitted values", template="plotly_white"), width="stretch", key=f"{key}_residuals")
    with right:
        st.plotly_chart(px.scatter(subset, x=predictor, y=outcome, title=f"Observed {outcome} by {predictor}", template="plotly_white"), width="stretch", key=f"{key}_scatter")


def render_guarded_analysis(data: pd.DataFrame, audit: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Render analysis families with test-specific data checks and a common output structure."""
    st.subheader("Guided analysis")
    st.caption("Use this after the audit. The calculation is conditional on the selected variables and cannot verify study design, causal identification, or substantive relevance.")
    available = ["estimate_mean"]
    nums, cats = numeric_columns(data), categorical_columns(data)
    if nums and cats:
        available.extend(["two_independent", "anova"])
    if len(nums) >= 2:
        available.extend(["paired", "linear_regression"])
    if len(cats) >= 2:
        available.append("association")
    binary_candidates = [name for name in cats if data[name].dropna().astype(str).nunique() == 2]
    if binary_candidates and nums:
        available.append("logistic_regression")
    method_key = st.selectbox("Analysis purpose", available, format_func=lambda item: METHOD_CARDS[item]["label"], key=f"{key}_analysis_purpose")
    result: dict[str, Any] | None = None
    selections: dict[str, Any] = {"analysis purpose": METHOD_CARDS[method_key]["label"]}
    try:
        if method_key == "estimate_mean":
            outcome = st.selectbox("Numeric outcome", nums, key=f"{key}_mean_outcome")
            selections["outcome"] = outcome
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
            power = independent_group_power(abs(result["details"]["cohen_d"]) if np.isfinite(result["details"]["cohen_d"]) else 0.2, min(result["details"]["n_first"], result["details"]["n_second"]))
            st.info(f"Planning context only: with the observed standardized difference and smaller group size, estimated two-sided power is {power['power']:.2f}. About {power['n_per_group_for_80_percent_power']:.0f} observations per group are required for 80% power at the same assumed effect size. Do not use a post-hoc calculation as a substitute for prospective design planning.")
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
            selections.update({"first variable": first, "second variable": second})
            result = categorical_association(data, first, second)
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
    report = build_report(result, audit, selections)
    st.download_button("Download reproducibility record (Markdown)", report, file_name=f"{key}_inference_record.md", mime="text/markdown", key=f"{key}_report")
    return result


def render_workspace(data: pd.DataFrame, key: str, dataset_name: str, filename: str | None = None) -> None:
    """Render the common Learn / Practice / Audit workflow for a dataset."""
    learn, practice, audit_mode = st.tabs(["1. Learn from the data", "2. Practice guided analysis", "3. Audit the claim"])
    with learn:
        audit = render_dataset_audit(data, key, dataset_name, filename)
    with practice:
        audit = audit_dataset(data, dataset_name, metadata_for(filename))
        render_guarded_analysis(data, audit, key)
    with audit_mode:
        st.subheader("Inference audit prompts")
        st.markdown("- What target population and unit of observation support the claim?")
        st.markdown("- Which variables, coding choices, missing-data rules, and exclusions were used?")
        st.markdown("- Which assumptions are design facts, and which have only been explored diagnostically?")
        st.markdown("- What does the estimate and uncertainty interval say on the practical scale?")
        st.markdown("- What does the result **not** establish, including causal or practical importance claims?")
        st.text_area("Write a brief audit note", key=f"{key}_audit_note", placeholder="State the most important limitation or robustness check.")
