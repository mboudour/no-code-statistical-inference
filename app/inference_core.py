"""Core inference workflows for the no-code statistical inference seminar.

The functions in this module are deliberately independent of Streamlit so that their
calculations can be tested, reused by an R adapter, and recorded in reports.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.power import TTestIndPower
from statsmodels.tools.sm_exceptions import ConvergenceWarning, PerfectSeparationError

from validation import InputValidationError, validate_inputs

RESULT_SECTIONS = [
    "Question",
    "Data and design",
    "Method",
    "Assumptions",
    "Diagnostics",
    "Estimate",
    "Uncertainty",
    "Effect size",
    "Test statistic and p-value",
    "Interpretation",
    "Limitations",
    "Next step",
]

METHOD_CARDS: dict[str, dict[str, Any]] = {
    "estimate_mean": {
        "label": "Estimate one numeric population quantity",
        "method": "Mean with confidence interval",
        "module_ids": ["d1m07", "d1m08"],
        "requirements": "One numeric outcome with observations that can reasonably be related to a target population.",
        "warnings": ["Independence and representativeness arise from the sampling/design process and cannot be proven from a CSV.", "Extreme skewness or outliers can make a mean-based interval fragile in small samples."],
    },
    "two_independent": {
        "label": "Compare two independent groups",
        "method": "Welch two-sample comparison",
        "module_ids": ["d2m02", "d2m03"],
        "requirements": "One numeric outcome, one grouping variable with two selected levels, and independent units.",
        "warnings": ["Do not use this procedure for matched or repeated observations.", "The interface checks sample sizes, outliers, groupwise shape, and variance evidence; these checks do not establish design independence."],
    },
    "paired": {
        "label": "Compare paired measurements",
        "method": "Paired comparison of within-unit differences",
        "module_ids": ["d2m04"],
        "requirements": "Two numeric measurements on the same observational units or a properly aligned paired design.",
        "warnings": ["Rows must represent valid pairs; alignment cannot be inferred automatically.", "The normality diagnostic concerns differences, not the two raw variables separately."],
    },
    "anova": {
        "label": "Compare three or more groups",
        "method": "One-way analysis of variance",
        "module_ids": ["d2m05", "d2m06"],
        "requirements": "One numeric outcome and a grouping variable with at least three levels.",
        "warnings": ["An omnibus result does not identify which groups differ.", "Independence remains a design condition; groupwise shape and variance diagnostics are evidence, not guarantees."],
    },
    "association": {
        "label": "Assess association between two categorical variables",
        "method": "Chi-square association test",
        "module_ids": ["d2m07", "d2m08", "d2m09"],
        "requirements": "Two categorical variables measured on independent observational units.",
        "warnings": ["Small expected counts weaken the chi-square approximation.", "Association does not establish a causal relationship."],
    },
    "linear_regression": {
        "label": "Model or predict a continuous outcome",
        "method": "Linear regression",
        "module_ids": ["d3m01", "d3m02", "d3m03", "d3m04", "d3m08"],
        "requirements": "One numeric outcome and one or more numeric predictors with an explicitly stated conditional question.",
        "warnings": ["A fitted regression line is not a causal model without design and substantive justification.", "Residual, influence, collinearity, and heteroskedasticity checks must be interpreted together."],
    },
    "logistic_regression": {
        "label": "Model or predict a binary outcome",
        "method": "Logistic regression",
        "module_ids": ["d3m05", "d3m06", "d3m07"],
        "requirements": "A binary outcome and one or more numeric predictors with enough observations in both outcome classes.",
        "warnings": ["Odds ratios are not risk ratios.", "Classification thresholds encode consequences and should not be chosen solely to maximize accuracy."],
    },
}


def method_compatibility(
    outcome_type: str,
    explanatory_type: str,
    design: str,
    aim: str,
) -> list[dict[str, str]]:
    """Return transparent compatibility statuses from design features, not test names."""
    independent = design == "Independent observational units"
    paired = design == "Paired or matched measurements"
    unknown_design = design in {"Unknown — investigate before analysis", "Repeated / clustered / longitudinal"}
    rules = {
        "estimate_mean": outcome_type == "Continuous / numeric" and explanatory_type == "None / estimation" and aim == "Estimation",
        "two_independent": outcome_type == "Continuous / numeric" and explanatory_type == "Two groups" and aim == "Comparison" and independent,
        "paired": outcome_type == "Continuous / numeric" and explanatory_type == "Two groups" and aim == "Comparison" and paired,
        "anova": outcome_type == "Continuous / numeric" and explanatory_type == "Three or more groups" and aim == "Comparison" and independent,
        "association": outcome_type in {"Binary", "Categorical"} and explanatory_type == "Two categorical variables" and aim == "Association" and independent,
        "linear_regression": outcome_type == "Continuous / numeric" and explanatory_type == "One or more predictors" and aim in {"Association", "Prediction"} and independent,
        "logistic_regression": outcome_type == "Binary" and explanatory_type == "One or more predictors" and aim in {"Association", "Prediction"} and independent,
    }
    recommendations: list[dict[str, str]] = []
    for key, card in METHOD_CARDS.items():
        if rules[key]:
            status, reason = "Compatible", "The recorded outcome, explanatory structure, dependence assumption, and aim match this pathway."
        elif unknown_design:
            status, reason = "Caution", "Dependence is unknown or clustered/repeated. This app’s simple workflow is not automatically appropriate; establish the design before calculation."
        else:
            status, reason = "Not compatible", "The recorded outcome, explanatory structure, design, or aim does not match this pathway."
        recommendations.append({"key": key, "status": status, "method": card["method"], "reason": reason, "modules": ", ".join(module_id.upper() for module_id in card["module_ids"])})
    return recommendations


def numeric_columns(data: pd.DataFrame) -> list[str]:
    """Return numeric columns excluding boolean indicators."""
    return [name for name in data.select_dtypes(include=np.number).columns if not pd.api.types.is_bool_dtype(data[name])]


def categorical_columns(data: pd.DataFrame) -> list[str]:
    """Return non-numeric columns plus low-cardinality numeric indicators."""
    columns = data.select_dtypes(exclude=np.number).columns.tolist()
    for name in numeric_columns(data):
        values = data[name].dropna().unique()
        if len(values) <= 8 and set(values).issubset({0, 1}):
            columns.append(name)
    return list(dict.fromkeys(columns))


def variable_type(series: pd.Series) -> str:
    non_missing = series.dropna()
    unique = non_missing.nunique()
    if pd.api.types.is_numeric_dtype(series):
        if unique <= 2:
            return "binary numeric"
        if unique <= 12 and np.allclose(non_missing, np.round(non_missing)):
            return "discrete numeric"
        return "continuous / numeric"
    if unique <= 2:
        return "binary categorical"
    return "categorical"


def iqr_outlier_count(values: pd.Series | np.ndarray) -> int:
    values = pd.Series(values).dropna().astype(float)
    if len(values) < 4:
        return 0
    q1, q3 = values.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0:
        return 0
    return int(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).sum())


def audit_dataset(data: pd.DataFrame, dataset_name: str = "Uploaded dataset", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a data audit that is safe to show before inferential analysis."""
    metadata = metadata or {}
    rows, columns = data.shape
    variable_rows: list[dict[str, Any]] = []
    for name in data.columns:
        series = data[name]
        variable_rows.append(
            {
                "Variable": name,
                "Inferred type": variable_type(series),
                "Missing": int(series.isna().sum()),
                "Missing %": round(100 * series.isna().mean(), 1),
                "Distinct values": int(series.nunique(dropna=True)),
                "Constant": bool(series.nunique(dropna=True) <= 1),
            }
        )
    variable_table = pd.DataFrame(variable_rows)
    missing = data.isna().sum().sort_values(ascending=False)
    return {
        "dataset": dataset_name,
        "rows": rows,
        "columns": columns,
        "duplicate_rows": int(data.duplicated().sum()),
        "complete_rows": int(data.dropna().shape[0]),
        "missing_cells": int(data.isna().sum().sum()),
        "numeric_columns": numeric_columns(data),
        "categorical_columns": categorical_columns(data),
        "constant_columns": variable_table.loc[variable_table["Constant"], "Variable"].tolist(),
        "variable_table": variable_table,
        "missing_table": pd.DataFrame({"Variable": missing.index, "Missing": missing.values, "Missing %": (100 * missing.values / max(rows, 1)).round(1)}),
        "source": metadata.get("source", "Participant supplied or local seminar file"),
        "license": metadata.get("license", "Document before use beyond classroom demonstration"),
        "unit_of_observation": metadata.get("unit_of_observation", "Confirm with the data documentation before inference"),
        "limitations": metadata.get("limitations", "Sampling process, measurement process, and target population must be documented by the analyst."),
        "suitable_modules": metadata.get("suitable_modules", []),
    }


def shapiro_diagnostic(values: np.ndarray) -> dict[str, Any]:
    values = np.asarray(values, dtype=float)
    if len(values) < 3:
        return {"available": False, "message": "At least three observations are required for this shape diagnostic."}
    if np.unique(values).size < 2:
        return {"available": False, "message": "The selected values have zero observed variation, so a normality/shape diagnostic is not informative."}
    if len(values) > 5000:
        values = values[:5000]
        sampled = True
    else:
        sampled = False
    statistic, p_value = stats.shapiro(values)
    return {
        "available": True,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "message": "This is a diagnostic for distributional shape, not a proof that a model is valid." + (" The first 5,000 observations were used." if sampled else ""),
    }


def mean_interval(values: np.ndarray, confidence: float = 0.95) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    if len(values) < 2:
        return {"mean": mean, "se": float("nan"), "low": float("nan"), "high": float("nan")}
    se = float(stats.sem(values))
    critical = float(stats.t.ppf((1 + confidence) / 2, len(values) - 1))
    return {"mean": mean, "se": se, "low": mean - critical * se, "high": mean + critical * se}


def descriptive_numeric_summary(data: pd.DataFrame, outcome: str) -> dict[str, Any]:
    """Return a non-inferential numeric summary when a standard error is undefined."""
    values = pd.to_numeric(data[outcome], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if len(values) < 1:
        raise InputValidationError(f"A descriptive summary of {outcome} requires at least one finite, non-missing observation.")
    summary = {"n": int(len(values)), "mean": float(np.mean(values)), "median": float(np.median(values)), "minimum": float(np.min(values)), "maximum": float(np.max(values)), "unique_values": int(len(np.unique(values)))}
    return {
        "method": "Descriptive numeric summary only",
        "question": f"What values of {outcome} were observed in this selected dataset?",
        "data_design": f"{len(values)} finite, non-missing observations of {outcome}. No inferential reference calculation is attempted.",
        "assumptions": ["This is descriptive only; it does not require a sampling distribution assumption.", "The values and unit of observation still require substantive verification."],
        "diagnostics": {"shape": shapiro_diagnostic(values), "outliers_iqr": iqr_outlier_count(values), "input_validation": ["The selected outcome has zero observed variation, so a standard error and t confidence interval are undefined. The app provides a descriptive-only fallback."]},
        "estimate": f"Mean = {summary['mean']:.3f}; median = {summary['median']:.3f}; range = [{summary['minimum']:.3f}, {summary['maximum']:.3f}]",
        "uncertainty": "No standard error, confidence interval, or hypothesis test is reported because the observed outcome has zero variation.",
        "effect_size": "Not applicable for a descriptive-only constant outcome.",
        "test": "No inferential test was performed.",
        "interpretation": f"All {summary['n']} observed non-missing values equal {summary['mean']:.3f}. This describes the selected data; it does not establish that the population value is known without uncertainty.",
        "limitations": "A constant observed variable can reflect true homogeneity, rounding, coding, truncation, or a data-processing issue. Inspect the original measurement process.",
        "next_step": "Verify coding and measurement. If a population inference is needed, obtain data with observed variation or reconsider the estimand.",
        "details": summary,
    }


def one_sample_mean(data: pd.DataFrame, outcome: str, confidence: float = 0.95) -> dict[str, Any]:
    validation = validate_inputs("estimate_mean", data, outcome=outcome)
    values = pd.to_numeric(data[outcome], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    interval = mean_interval(values, confidence)
    return {
        "method": "Mean with t confidence interval",
        "question": f"What is the mean of {outcome} in the stated target population?",
        "data_design": f"{len(values)} non-missing observations of {outcome}.",
        "assumptions": ["Observations represent the stated target population.", "Observations are independent under the study design.", "A mean and t interval are appropriate summaries for this outcome and sample size."],
        "diagnostics": {"shape": shapiro_diagnostic(values), "outliers_iqr": iqr_outlier_count(values), "input_validation": list(validation.warnings)},
        "estimate": interval["mean"],
        "uncertainty": f"{confidence:.0%} CI [{interval['low']:.3f}, {interval['high']:.3f}]",
        "effect_size": "Not applicable for a single mean without a reference value.",
        "test": "No null-hypothesis test was requested.",
        "interpretation": f"The sample mean of {outcome} is {interval['mean']:.3f}; the interval describes uncertainty in a population mean under the stated assumptions.",
        "limitations": "This interval cannot resolve selection bias, measurement error, or an undefined target population.",
        "next_step": "State the population, sampling process, and practical scale before using the estimate in a substantive claim.",
        "details": {"n": len(values), **interval},
    }


def two_group_welch(data: pd.DataFrame, outcome: str, group: str, levels: list[str], confidence: float = 0.95) -> dict[str, Any]:
    validation = validate_inputs("two_independent", data, outcome=outcome, group=group, levels=levels)
    subset = data[[outcome, group]].dropna().copy()
    subset[group] = subset[group].astype(str)
    first = pd.to_numeric(subset.loc[subset[group] == str(levels[0]), outcome], errors="coerce").dropna().to_numpy(dtype=float)
    second = pd.to_numeric(subset.loc[subset[group] == str(levels[1]), outcome], errors="coerce").dropna().to_numpy(dtype=float)
    n1, n2 = len(first), len(second)
    mean1, mean2 = float(np.mean(first)), float(np.mean(second))
    diff = mean2 - mean1
    var1, var2 = float(np.var(first, ddof=1)), float(np.var(second, ddof=1))
    se = float(np.sqrt(var1 / n1 + var2 / n2))
    df_num = (var1 / n1 + var2 / n2) ** 2
    df_den = ((var1 / n1) ** 2 / (n1 - 1)) + ((var2 / n2) ** 2 / (n2 - 1))
    df = df_num / df_den
    critical = float(stats.t.ppf((1 + confidence) / 2, df))
    test = stats.ttest_ind(first, second, equal_var=False)
    pooled_sd = float(np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)))
    cohen_d = diff / pooled_sd if pooled_sd else float("nan")
    levene = stats.levene(first, second, center="median") if n1 >= 2 and n2 >= 2 else None
    return {
        "method": "Welch independent-samples comparison",
        "question": f"How does the mean of {outcome} differ between {levels[0]} and {levels[1]}?",
        "data_design": f"Independent-group comparison with {n1} and {n2} complete observations.",
        "assumptions": ["Rows are independent within and between groups under the study design.", "The outcome is appropriately treated as numeric.", "The comparison targets a mean difference, not a causal effect by default."],
        "diagnostics": {
            f"shape_{levels[0]}": shapiro_diagnostic(first),
            f"shape_{levels[1]}": shapiro_diagnostic(second),
            "variance_structure": {"statistic": float(levene.statistic), "p_value": float(levene.pvalue), "message": "Welch's procedure does not impose equal variances, but large variance differences remain substantively informative."} if levene else {},
            "outliers_iqr": {levels[0]: iqr_outlier_count(first), levels[1]: iqr_outlier_count(second)},
            "input_validation": list(validation.warnings),
        },
        "estimate": diff,
        "uncertainty": f"{confidence:.0%} CI for mean difference [{diff - critical * se:.3f}, {diff + critical * se:.3f}]",
        "effect_size": f"Cohen's d = {cohen_d:.3f}",
        "test": f"Welch t({df:.1f}) = {float(test.statistic):.3f}, p = {float(test.pvalue):.4f}",
        "interpretation": f"The observed mean difference ({levels[1]} minus {levels[0]}) is {diff:.3f}. Its practical meaning depends on the outcome scale and study design.",
        "limitations": "A p-value does not measure effect magnitude, importance, or the probability that either hypothesis is true.",
        "next_step": "Inspect the grouped plot, diagnostics, design, and effect-size interval before drawing a substantive conclusion.",
        "details": {"n_first": n1, "n_second": n2, "mean_first": mean1, "mean_second": mean2, "difference": diff, "se": se, "df": df, "p_value": float(test.pvalue), "cohen_d": cohen_d},
    }


def paired_comparison(data: pd.DataFrame, first_name: str, second_name: str, confidence: float = 0.95) -> dict[str, Any]:
    validation = validate_inputs("paired", data, first_name=first_name, second_name=second_name)
    subset = data[[first_name, second_name]].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    differences = (subset[second_name] - subset[first_name]).to_numpy(dtype=float)
    interval = mean_interval(differences, confidence)
    test = stats.ttest_1samp(differences, 0)
    return {
        "method": "Paired comparison of within-unit differences",
        "question": f"What is the mean within-unit difference ({second_name} minus {first_name})?",
        "data_design": f"{len(differences)} complete row pairs. The analyst must verify that each row is a valid matched pair.",
        "assumptions": ["Rows are valid pairs measured on the same unit or a documented matched design.", "Pairs are independent of other pairs.", "Inference concerns the distribution of within-pair differences."],
        "diagnostics": {"difference_shape": shapiro_diagnostic(differences), "outliers_iqr": iqr_outlier_count(differences), "input_validation": list(validation.warnings)},
        "estimate": interval["mean"],
        "uncertainty": f"{confidence:.0%} CI [{interval['low']:.3f}, {interval['high']:.3f}]",
        "effect_size": f"Standardized paired difference = {interval['mean'] / np.std(differences, ddof=1):.3f}" if np.std(differences, ddof=1) else "Undefined because the difference standard deviation is zero.",
        "test": f"Paired t({len(differences) - 1}) = {float(test.statistic):.3f}, p = {float(test.pvalue):.4f}",
        "interpretation": f"The average within-pair difference is {interval['mean']:.3f}; interpretation depends on valid pairing and outcome scale.",
        "limitations": "The interface cannot infer whether matching was scientifically appropriate or whether pairing was broken by data handling.",
        "next_step": "Confirm pair identity and inspect the distribution of differences before reporting the comparison.",
        "details": {"n_pairs": len(differences), **interval, "p_value": float(test.pvalue)},
    }


def one_way_anova(data: pd.DataFrame, outcome: str, group: str) -> dict[str, Any]:
    validation = validate_inputs("anova", data, outcome=outcome, group=group)
    subset = data[[outcome, group]].dropna().copy()
    subset[outcome] = pd.to_numeric(subset[outcome], errors="coerce")
    subset = subset.dropna()
    subset[group] = subset[group].astype(str)
    groups = [values.to_numpy(dtype=float) for _, values in subset.groupby(group, sort=True)[outcome]]
    labels = [str(label) for label, _ in subset.groupby(group, sort=True)[outcome]]
    test = stats.f_oneway(*groups)
    overall = subset[outcome].mean()
    between = sum(len(values) * (values.mean() - overall) ** 2 for values in groups)
    total = sum((subset[outcome] - overall) ** 2)
    eta_sq = between / total if total else float("nan")
    levene = stats.levene(*groups, center="median")
    diagnostics = {"variance_structure": {"statistic": float(levene.statistic), "p_value": float(levene.pvalue), "message": "A small p-value is evidence against equal variance under this diagnostic model, not an automatic decision rule."}, "input_validation": list(validation.warnings)}
    for label, values in zip(labels, groups, strict=True):
        diagnostics[f"shape_{label}"] = shapiro_diagnostic(values)
        diagnostics.setdefault("outliers_iqr", {})[label] = iqr_outlier_count(values)
    return {
        "method": "One-way analysis of variance",
        "question": f"Is there evidence that mean {outcome} differs across levels of {group}?",
        "data_design": f"{len(subset)} complete observations across {len(groups)} groups.",
        "assumptions": ["Observations are independent under the study design.", "The outcome is numeric and group labels identify the intended comparison.", "ANOVA evaluates an omnibus mean difference; it does not identify a specific pair."],
        "diagnostics": diagnostics,
        "estimate": f"Group means: {dict(zip(labels, [round(float(values.mean()), 3) for values in groups], strict=True))}",
        "uncertainty": "Inspect groupwise distributions and confidence intervals; no post-hoc contrast is automatically selected.",
        "effect_size": f"Eta-squared = {eta_sq:.3f}",
        "test": f"F({len(groups)-1}, {len(subset)-len(groups)}) = {float(test.statistic):.3f}, p = {float(test.pvalue):.4f}",
        "interpretation": "The omnibus test concerns any difference among group means. It is not evidence of which groups differ or why.",
        "limitations": "Multiple post-hoc comparisons require an explicit plan and multiplicity-aware procedure.",
        "next_step": "Specify planned contrasts or a post-hoc strategy before investigating individual group differences.",
        "details": {"n": len(subset), "groups": labels, "eta_squared": eta_sq, "p_value": float(test.pvalue)},
    }


def categorical_association(data: pd.DataFrame, first: str, second: str) -> dict[str, Any]:
    validation = validate_inputs("association", data, first=first, second=second)
    first_values = data[first].where(data[first].notna(), "Missing").astype(str)
    second_values = data[second].where(data[second].notna(), "Missing").astype(str)
    table = pd.crosstab(first_values, second_values)
    if table.shape[0] < 2 or table.shape[1] < 2:
        raise InputValidationError("The selected variables produce fewer than two observed categories in at least one dimension after missing-value handling.")
    try:
        chi2, p_value, df, expected = stats.chi2_contingency(table)
    except ValueError as error:
        raise InputValidationError(f"The chi-square reference calculation is undefined for this table: {error}") from error
    n = table.to_numpy().sum()
    phi2 = chi2 / n if n else float("nan")
    r, c = table.shape
    cramer_v = np.sqrt(phi2 / min(r - 1, c - 1)) if min(r - 1, c - 1) else float("nan")
    small_expected = int((expected < 5).sum())
    fisher = None
    if table.shape == (2, 2):
        odds_ratio, fisher_p = stats.fisher_exact(table.to_numpy())
        fisher = {"odds_ratio": float(odds_ratio), "p_value": float(fisher_p)}
    return {
        "method": "Chi-square test of categorical association",
        "question": f"Are {first} and {second} associated in the observed table?",
        "data_design": f"Contingency table with {n} observed records, {r} by {c} cells.",
        "assumptions": ["Rows represent independent observational units.", "Categories are mutually exclusive under the chosen coding.", "Expected counts are large enough for the chi-square reference approximation."],
        "diagnostics": {"minimum_expected_count": float(expected.min()), "cells_expected_below_5": small_expected, "fisher_exact": fisher, "input_validation": list(validation.warnings), "message": "When expected counts are small, Fisher's exact result is promoted for a 2×2 table; larger sparse tables require a simulation-based or collapsed-category analysis outside this workflow."},
        "estimate": "Observed conditional distributions are shown in the contingency table.",
        "uncertainty": "The chi-square reference distribution is approximate and depends on expected-count conditions.",
        "effect_size": f"Cramer's V = {cramer_v:.3f}",
        "test": (f"Fisher exact p = {fisher['p_value']:.4f}; odds ratio = {fisher['odds_ratio']:.3f} (promoted because {small_expected} expected cell(s) are below 5)." if fisher and small_expected else f"Chi-square({df}) = {chi2:.3f}, p = {p_value:.4f}"),
        "interpretation": ("For this sparse 2×2 table, Fisher's exact result is the primary small-sample reference calculation. It still does not measure practical importance or causal direction." if fisher and small_expected else "The test evaluates evidence against an independence model, not the practical importance or causal direction of the association."),
        "limitations": "Sparse cells, dependent observations, and post-hoc category selection can invalidate a simple interpretation.",
        "next_step": "Inspect conditional proportions, cell counts, expected counts, and the study design before reporting an association.",
        "details": {"table": table, "expected": pd.DataFrame(expected, index=table.index, columns=table.columns), "n": int(n), "chi2": float(chi2), "df": int(df), "p_value": float(p_value), "cramer_v": float(cramer_v)},
    }


def linear_regression(data: pd.DataFrame, outcome: str, predictors: list[str]) -> dict[str, Any]:
    validation = validate_inputs("linear_regression", data, outcome=outcome, predictors=predictors)
    subset = data[[outcome, *predictors]].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    y = subset[outcome]
    x = sm.add_constant(subset[predictors], has_constant="add")
    model = sm.OLS(y, x).fit()
    residuals = model.resid
    influence = model.get_influence()
    cooks = influence.cooks_distance[0]
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(residuals, x)
    vifs = {}
    if len(predictors) > 1:
        for index, name in enumerate(predictors, start=1):
            vifs[name] = float(variance_inflation_factor(x.values, index))
    coefficient_table = pd.DataFrame({"Estimate": model.params, "SE": model.bse, "CI low": model.conf_int().iloc[:, 0], "CI high": model.conf_int().iloc[:, 1], "p-value": model.pvalues}).round(4)
    return {
        "method": "Ordinary least squares linear regression",
        "question": f"How is {outcome} conditionally associated with {', '.join(predictors)} under a linear model?",
        "data_design": f"{len(subset)} complete cases; all selected predictors are treated as numeric.",
        "assumptions": ["Rows are independent under the study design.", "The conditional mean structure is adequately represented by the specified linear form.", "Residual diagnostics are interpreted together with substantive knowledge and data collection conditions."],
        "diagnostics": {"residual_shape": shapiro_diagnostic(residuals), "breusch_pagan": {"statistic": float(bp_stat), "p_value": float(bp_pvalue), "message": "This diagnostic tests a particular heteroskedasticity pattern and is not a universal model-validity test."}, "largest_cooks_distance": float(np.max(cooks)), "vif": vifs, "input_validation": list(validation.warnings)},
        "estimate": coefficient_table,
        "uncertainty": "Coefficient intervals are conditional on the specified model, predictors, and assumptions.",
        "effect_size": f"R² = {model.rsquared:.3f}; adjusted R² = {model.rsquared_adj:.3f}",
        "test": f"Model F = {model.fvalue:.3f}, p = {model.f_pvalue:.4f}",
        "interpretation": "Each coefficient is a model-based conditional association, not automatically a causal effect.",
        "limitations": "Omitted variables, selection effects, nonlinear relationships, dependence, and influential cases can change the interpretation.",
        "next_step": "Inspect residual and leverage plots, consider a robust or transformed model where warranted, and articulate the scientific design.",
        "details": {"n": len(subset), "r_squared": float(model.rsquared), "adjusted_r_squared": float(model.rsquared_adj), "coefficients": coefficient_table, "fitted": model.fittedvalues, "residuals": residuals, "cooks_distance": cooks},
    }


def logistic_regression(data: pd.DataFrame, outcome: str, predictors: list[str]) -> dict[str, Any]:
    validation = validate_inputs("logistic_regression", data, outcome=outcome, predictors=predictors)
    subset = data[[outcome, *predictors]].copy()
    subset[predictors] = subset[predictors].apply(pd.to_numeric, errors="coerce")
    subset = subset.replace([np.inf, -np.inf], np.nan).dropna()
    levels = sorted(subset[outcome].astype(str).unique().tolist())
    y = (subset[outcome].astype(str) == levels[1]).astype(int)
    x = sm.add_constant(subset[predictors].astype(float), has_constant="add")
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model = sm.Logit(y, x).fit(disp=False, maxiter=100)
        if not bool(model.mle_retvals.get("converged", False)) or any(issubclass(item.category, ConvergenceWarning) for item in caught):
            raise InputValidationError("The logistic model did not converge reliably. Simplify the predictor set, check separation/sparse outcomes, or use a penalized method outside this workflow.")
    except PerfectSeparationError as error:
        raise InputValidationError("Perfect separation was detected: one or more predictor patterns distinguish outcome classes completely. Standard logistic coefficients are not finite; simplify the model or use a penalized method outside this workflow.") from error
    except np.linalg.LinAlgError as error:
        raise InputValidationError("The logistic information matrix is singular. This commonly reflects separation, quasi-separation, or redundant predictor information; simplify the model or use a penalized method outside this workflow.") from error
    probabilities = model.predict(x)
    coefficient_table = pd.DataFrame({"Log-odds estimate": model.params, "Odds ratio": np.exp(model.params), "CI low OR": np.exp(model.conf_int().iloc[:, 0]), "CI high OR": np.exp(model.conf_int().iloc[:, 1]), "p-value": model.pvalues}).round(4)
    return {
        "method": "Logistic regression for a binary outcome",
        "question": f"How is the probability of {levels[1]} conditionally associated with {', '.join(predictors)}?",
        "data_design": f"{len(subset)} complete records; binary outcome coded as {levels[0]} / {levels[1]}.",
        "assumptions": ["Rows are independent under the study design.", "The selected predictors have an appropriate relationship with the log-odds under the specified model.", "There are adequate observations in both outcome classes."],
        "diagnostics": {"outcome_counts": y.value_counts().to_dict(), "minimum_predicted_probability": float(probabilities.min()), "maximum_predicted_probability": float(probabilities.max()), "input_validation": list(validation.warnings)},
        "estimate": coefficient_table,
        "uncertainty": "Odds-ratio intervals are conditional on the specified model and predictor scale.",
        "effect_size": f"McFadden pseudo R² = {model.prsquared:.3f}",
        "test": f"Model likelihood-ratio p = {model.llr_pvalue:.4f}",
        "interpretation": "Odds ratios and fitted probabilities are conditional model summaries. They do not by themselves establish risk differences or causal effects.",
        "limitations": "Separation, sparse outcomes, nonlinear log-odds, omitted variables, and threshold choices require separate investigation.",
        "next_step": "Inspect calibration, discrimination, outcome balance, and the practical consequences of any classification threshold.",
        "details": {"n": len(subset), "levels": levels, "coefficients": coefficient_table, "probabilities": probabilities},
    }


def independent_group_power(planning_effect_size: float, group_size: int, alpha: float = 0.05, target_power: float = 0.80) -> dict[str, float]:
    """Prospective two-group planning calculation using a user-specified meaningful effect size."""
    if not np.isfinite(planning_effect_size) or planning_effect_size <= 0:
        raise InputValidationError("Choose a positive, substantively meaningful standardized planning effect size; do not use a zero or observed post-hoc effect by default.")
    if group_size < 2:
        raise InputValidationError("Current group size must be at least two for a two-group planning calculation.")
    if not 0 < target_power < 1:
        raise InputValidationError("Target power must be strictly between 0 and 1.")
    analysis = TTestIndPower()
    power = float(analysis.power(effect_size=planning_effect_size, nobs1=group_size, alpha=alpha, ratio=1.0, alternative="two-sided"))
    required = float(analysis.solve_power(effect_size=planning_effect_size, power=target_power, alpha=alpha, ratio=1.0, alternative="two-sided"))
    return {"power": power, "n_per_group_for_target_power": required, "planning_effect_size": float(planning_effect_size), "target_power": float(target_power)}


def renderable_diagnostics(diagnostics: dict[str, Any]) -> list[str]:
    """Convert diagnostic objects to compact, reportable text without decision-rule overclaiming."""
    lines: list[str] = []
    for name, value in diagnostics.items():
        label = name.replace("_", " ").capitalize()
        if isinstance(value, dict) and "p_value" in value:
            lines.append(f"{label}: statistic={value.get('statistic', float('nan')):.3f}, p={value['p_value']:.4f}. {value.get('message', '')}")
        elif isinstance(value, dict) and "available" in value:
            if value["available"]:
                lines.append(f"{label}: W={value['statistic']:.3f}, p={value['p_value']:.4f}. {value['message']}")
            else:
                lines.append(f"{label}: {value['message']}")
        else:
            lines.append(f"{label}: {value}")
    return lines


def build_report(result: dict[str, Any], audit: dict[str, Any], selections: dict[str, Any], include_details: bool = False) -> str:
    """Build a reproducibility record, optionally including detailed tables and diagnostics."""
    created = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# No-Code Statistical Inference Record", "", f"Generated: {created}", "", "## Dataset audit", f"- Dataset: {audit['dataset']}", f"- Rows / columns: {audit['rows']} / {audit['columns']}", f"- Complete rows: {audit['complete_rows']}", f"- Duplicate rows: {audit['duplicate_rows']}", f"- Missing cells: {audit['missing_cells']}", f"- Source: {audit['source']}", f"- Unit of observation: {audit['unit_of_observation']}", "", "## Selections"]
    lines.extend(f"- {key}: {value}" for key, value in selections.items())
    lines.extend(["", "## Result"])
    ordered = {"Question": result.get("question"), "Data and design": result.get("data_design"), "Method": result.get("method"), "Assumptions": result.get("assumptions"), "Estimate": result.get("estimate"), "Uncertainty": result.get("uncertainty"), "Effect size": result.get("effect_size"), "Test statistic and p-value": result.get("test"), "Interpretation": result.get("interpretation"), "Limitations": result.get("limitations"), "Next step": result.get("next_step")}
    for heading, content in ordered.items():
        lines.append(f"### {heading}")
        if isinstance(content, list):
            lines.extend(f"- {item}" for item in content)
        elif isinstance(content, pd.DataFrame):
            lines.extend(["", content.to_markdown(), ""])
        else:
            lines.append(str(content))
        lines.append("")
    lines.append("### Diagnostics")
    lines.extend(f"- {item}" for item in renderable_diagnostics(result.get("diagnostics", {})))
    if include_details:
        lines.extend(["", "## Detailed appendix"])
        details = result.get("details", {})
        for name, value in details.items():
            heading = name.replace("_", " ").title()
            if isinstance(value, pd.DataFrame):
                lines.extend([f"### {heading}", "", value.to_markdown(), ""])
            elif isinstance(value, pd.Series):
                lines.extend([f"### {heading}", "", value.to_frame(name=name).to_markdown(), ""])
            elif isinstance(value, np.ndarray):
                lines.append(f"- {heading}: numerical vector with {value.size} value(s); inspect the interactive app for the corresponding diagnostic plot.")
            elif isinstance(value, (str, int, float, np.integer, np.floating)):
                lines.append(f"- {heading}: {value}")
        lines.extend(["", "### Visualization record", "- Interactive visualizations are rendered in the app from the selected data and variables. This Markdown record does not embed image files; retain exported figures separately if a static review artifact is required."])
    lines.extend(["", "## Software", "- Python analysis engine: pandas, SciPy, statsmodels, Plotly, Seaborn, and Streamlit.", "- Results are conditional on the data, selections, model, and stated assumptions. A no-code result is not a substitute for study-design knowledge or substantive judgment."])
    return "\n".join(lines)
