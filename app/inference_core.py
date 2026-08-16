"""Core inference workflows for the no-code statistical inference seminar.

The functions in this module are deliberately independent of Streamlit so that their
calculations can be tested, reused by an R adapter, and recorded in reports.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.power import TTestIndPower

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


def one_sample_mean(data: pd.DataFrame, outcome: str, confidence: float = 0.95) -> dict[str, Any]:
    values = data[outcome].dropna().to_numpy(dtype=float)
    interval = mean_interval(values, confidence)
    return {
        "method": "Mean with t confidence interval",
        "question": f"What is the mean of {outcome} in the stated target population?",
        "data_design": f"{len(values)} non-missing observations of {outcome}.",
        "assumptions": ["Observations represent the stated target population.", "Observations are independent under the study design.", "A mean and t interval are appropriate summaries for this outcome and sample size."],
        "diagnostics": {"shape": shapiro_diagnostic(values), "outliers_iqr": iqr_outlier_count(values)},
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
    subset = data[[outcome, group]].dropna().copy()
    subset[group] = subset[group].astype(str)
    first = subset.loc[subset[group] == levels[0], outcome].to_numpy(dtype=float)
    second = subset.loc[subset[group] == levels[1], outcome].to_numpy(dtype=float)
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
    subset = data[[first_name, second_name]].dropna()
    differences = (subset[second_name] - subset[first_name]).to_numpy(dtype=float)
    interval = mean_interval(differences, confidence)
    test = stats.ttest_1samp(differences, 0)
    return {
        "method": "Paired comparison of within-unit differences",
        "question": f"What is the mean within-unit difference ({second_name} minus {first_name})?",
        "data_design": f"{len(differences)} complete row pairs. The analyst must verify that each row is a valid matched pair.",
        "assumptions": ["Rows are valid pairs measured on the same unit or a documented matched design.", "Pairs are independent of other pairs.", "Inference concerns the distribution of within-pair differences."],
        "diagnostics": {"difference_shape": shapiro_diagnostic(differences), "outliers_iqr": iqr_outlier_count(differences)},
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
    subset = data[[outcome, group]].dropna().copy()
    subset[group] = subset[group].astype(str)
    groups = [values.to_numpy(dtype=float) for _, values in subset.groupby(group, sort=True)[outcome]]
    labels = [str(label) for label, _ in subset.groupby(group, sort=True)[outcome]]
    test = stats.f_oneway(*groups)
    overall = subset[outcome].mean()
    between = sum(len(values) * (values.mean() - overall) ** 2 for values in groups)
    total = sum((subset[outcome] - overall) ** 2)
    eta_sq = between / total if total else float("nan")
    levene = stats.levene(*groups, center="median")
    diagnostics = {"variance_structure": {"statistic": float(levene.statistic), "p_value": float(levene.pvalue), "message": "A small p-value is evidence against equal variance under this diagnostic model, not an automatic decision rule."}}
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
    table = pd.crosstab(data[first].astype(str).fillna("Missing"), data[second].astype(str).fillna("Missing"))
    chi2, p_value, df, expected = stats.chi2_contingency(table)
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
        "diagnostics": {"minimum_expected_count": float(expected.min()), "cells_expected_below_5": small_expected, "fisher_exact": fisher, "message": "When expected counts are small, consider Fisher's exact test for a 2x2 table or a simulation-based alternative."},
        "estimate": "Observed conditional distributions are shown in the contingency table.",
        "uncertainty": "The chi-square reference distribution is approximate and depends on expected-count conditions.",
        "effect_size": f"Cramer's V = {cramer_v:.3f}",
        "test": f"Chi-square({df}) = {chi2:.3f}, p = {p_value:.4f}",
        "interpretation": "The test evaluates evidence against an independence model, not the practical importance or causal direction of the association.",
        "limitations": "Sparse cells, dependent observations, and post-hoc category selection can invalidate a simple interpretation.",
        "next_step": "Inspect conditional proportions, cell counts, expected counts, and the study design before reporting an association.",
        "details": {"table": table, "expected": pd.DataFrame(expected, index=table.index, columns=table.columns), "n": int(n), "chi2": float(chi2), "df": int(df), "p_value": float(p_value), "cramer_v": float(cramer_v)},
    }


def linear_regression(data: pd.DataFrame, outcome: str, predictors: list[str]) -> dict[str, Any]:
    subset = data[[outcome, *predictors]].dropna().astype(float)
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
        "diagnostics": {"residual_shape": shapiro_diagnostic(residuals), "breusch_pagan": {"statistic": float(bp_stat), "p_value": float(bp_pvalue), "message": "This diagnostic tests a particular heteroskedasticity pattern and is not a universal model-validity test."}, "largest_cooks_distance": float(np.max(cooks)), "vif": vifs},
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
    subset = data[[outcome, *predictors]].dropna().copy()
    levels = sorted(subset[outcome].astype(str).unique().tolist())
    if len(levels) != 2:
        raise ValueError("The selected outcome must have exactly two observed levels for logistic regression.")
    y = (subset[outcome].astype(str) == levels[1]).astype(int)
    x = sm.add_constant(subset[predictors].astype(float), has_constant="add")
    model = sm.Logit(y, x).fit(disp=False)
    probabilities = model.predict(x)
    coefficient_table = pd.DataFrame({"Log-odds estimate": model.params, "Odds ratio": np.exp(model.params), "CI low OR": np.exp(model.conf_int().iloc[:, 0]), "CI high OR": np.exp(model.conf_int().iloc[:, 1]), "p-value": model.pvalues}).round(4)
    return {
        "method": "Logistic regression for a binary outcome",
        "question": f"How is the probability of {levels[1]} conditionally associated with {', '.join(predictors)}?",
        "data_design": f"{len(subset)} complete records; binary outcome coded as {levels[0]} / {levels[1]}.",
        "assumptions": ["Rows are independent under the study design.", "The selected predictors have an appropriate relationship with the log-odds under the specified model.", "There are adequate observations in both outcome classes."],
        "diagnostics": {"outcome_counts": y.value_counts().to_dict(), "minimum_predicted_probability": float(probabilities.min()), "maximum_predicted_probability": float(probabilities.max())},
        "estimate": coefficient_table,
        "uncertainty": "Odds-ratio intervals are conditional on the specified model and predictor scale.",
        "effect_size": f"McFadden pseudo R² = {model.prsquared:.3f}",
        "test": f"Model likelihood-ratio p = {model.llr_pvalue:.4f}",
        "interpretation": "Odds ratios and fitted probabilities are conditional model summaries. They do not by themselves establish risk differences or causal effects.",
        "limitations": "Separation, sparse outcomes, nonlinear log-odds, omitted variables, and threshold choices require separate investigation.",
        "next_step": "Inspect calibration, discrimination, outcome balance, and the practical consequences of any classification threshold.",
        "details": {"n": len(subset), "levels": levels, "coefficients": coefficient_table, "probabilities": probabilities},
    }


def independent_group_power(effect_size: float, group_size: int, alpha: float = 0.05) -> dict[str, float]:
    analysis = TTestIndPower()
    power = float(analysis.power(effect_size=effect_size, nobs1=group_size, alpha=alpha, ratio=1.0, alternative="two-sided"))
    required = float(analysis.solve_power(effect_size=effect_size, power=0.80, alpha=alpha, ratio=1.0, alternative="two-sided"))
    return {"power": power, "n_per_group_for_80_percent_power": required}


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


def build_report(result: dict[str, Any], audit: dict[str, Any], selections: dict[str, Any]) -> str:
    """Build a compact reproducibility record that can be downloaded as Markdown."""
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
    lines.extend(["", "## Software", "- Python analysis engine: pandas, SciPy, statsmodels, Plotly, Seaborn, and Streamlit.", "- Results are conditional on the data, selections, model, and stated assumptions. A no-code result is not a substitute for study-design knowledge or substantive judgment."])
    return "\n".join(lines)
