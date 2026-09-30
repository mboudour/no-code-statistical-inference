"""Additional Day 3 computations aligned with the Day 3 slide sequence.

These computations are intentionally separate from the Streamlit interface so their
mathematics can be tested.  They complement the base Day 3 model functions with
categorical contrasts, adjustment comparisons, nested specifications, resampling,
and case-deletion sensitivity checks.
"""
from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from scipy import stats

from day3_analysis import (
    _design_matrix,
    _model_frame,
    calibration_table,
    fit_day3_linear_model,
    fit_day3_logistic_model,
    roc_points,
)
from validation import InputValidationError


ModelKind = Literal["linear", "logistic"]


def binary_outcome_columns(data: pd.DataFrame) -> list[str]:
    """Return columns with exactly two observed levels, including 0/1 numeric fields."""
    return [column for column in data.columns if data[column].dropna().nunique() == 2]


def _contrast_summary(
    model: Any, contrast: np.ndarray, label: str, alpha: float = 0.05
) -> dict[str, float | str]:
    estimate = float(np.asarray(contrast) @ np.asarray(model.params, dtype=float))
    covariance = np.asarray(model.cov_params(), dtype=float)
    standard_error = float(np.sqrt(max(0.0, contrast @ covariance @ contrast)))
    df = float(model.df_resid)
    critical = float(stats.t.ppf(1 - alpha / 2, df))
    statistic = estimate / standard_error if standard_error else np.nan
    p_value = float(2 * stats.t.sf(abs(statistic), df)) if np.isfinite(statistic) else np.nan
    return {
        "Contrast": label,
        "Estimate": estimate,
        "SE": standard_error,
        "CI low": estimate - critical * standard_error,
        "CI high": estimate + critical * standard_error,
        "p-value": p_value,
    }


def categorical_predictor_regression(data: pd.DataFrame, outcome: str, group: str) -> dict[str, Any]:
    """Fit treatment-coded group regression and report model-based group contrasts."""
    result = fit_day3_linear_model(data, outcome, [], [group])
    model = result["_model"]
    design = result["_design"]
    levels = result["details"]["schema"]["category_levels"][group]
    reference = levels[0]
    vectors: dict[str, np.ndarray] = {}
    mean_rows = []
    for level in levels:
        vector = np.zeros(design.shape[1], dtype=float)
        vector[list(design.columns).index("const")] = 1.0
        term = f"{group}={level}"
        if term in design.columns:
            vector[list(design.columns).index(term)] = 1.0
        vectors[level] = vector
        summary = _contrast_summary(model, vector, f"Mean for {level}")
        mean_rows.append({"Group": level, "Predicted mean": summary["Estimate"], "CI low": summary["CI low"], "CI high": summary["CI high"]})
    contrast_rows = []
    for position, later in enumerate(levels[1:], start=1):
        contrast_rows.append(_contrast_summary(model, vectors[later] - vectors[reference], f"{later} − {reference}"))
        for earlier in levels[1:position]:
            contrast_rows.append(_contrast_summary(model, vectors[later] - vectors[earlier], f"{later} − {earlier}"))
    result["method"] = "Treatment-coded linear regression for a categorical predictor with model-based contrasts"
    result["question"] = f"How does the conditional mean of {outcome} differ across levels of {group} under the stated reference coding?"
    result["data_design"] += f" Reference group for {group}: {reference}."
    result["interpretation"] = (
        "The group coefficients and contrasts are conditional mean differences under the stated treatment coding. "
        "They do not establish a causal group effect without a relevant design and adjustment rationale."
    )
    result["details"].update(
        {
            "reference_group": reference,
            "group_means": pd.DataFrame(mean_rows).round(4),
            "contrasts": pd.DataFrame(contrast_rows).round(4),
        }
    )
    return result


def adjustment_comparison(
    data: pd.DataFrame, outcome: str, focal_predictor: str, adjustment_predictors: list[str]
) -> dict[str, Any]:
    """Compare a focal coefficient before and after named numeric adjustment variables."""
    adjustments = [column for column in dict.fromkeys(adjustment_predictors) if column != focal_predictor]
    if not adjustments:
        raise InputValidationError("Select at least one additional predictor for the adjusted model.")
    unadjusted = fit_day3_linear_model(data, outcome, [focal_predictor])
    adjusted = fit_day3_linear_model(data, outcome, [focal_predictor, *adjustments])

    def focal_row(result: dict[str, Any], label: str) -> dict[str, Any]:
        table = result["details"]["coefficients"]
        row = table.loc[focal_predictor]
        return {"Model": label, "Estimate": row["Estimate"], "SE": row["SE"], "CI low": row["CI low"], "CI high": row["CI high"], "p-value": row["p-value"], "Complete records": result["details"]["n"]}

    return {
        "method": "Unadjusted-versus-adjusted ordinary least squares comparison",
        "question": f"How does the conditional coefficient for {focal_predictor} change when the named adjustment variables are included?",
        "data_design": f"Outcome={outcome}; focal predictor={focal_predictor}; adjustment predictors={', '.join(adjustments)}.",
        "comparison": pd.DataFrame([focal_row(unadjusted, "Unadjusted"), focal_row(adjusted, "Adjusted")]).round(4),
        "unadjusted": unadjusted,
        "adjusted": adjusted,
        "interpretation": (
            "The change in the focal coefficient records a change in the conditional comparison induced by the selected formula. "
            "It is not, by itself, proof that the adjustment set controls confounding or identifies a causal effect."
        ),
        "limitations": "A valid causal interpretation needs a design and a defensible account of temporal order, confounding, mediators, colliders, measurement, and support.",
    }


def nested_specification_comparison(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    categorical_predictors: list[str] | None = None,
    quadratic_predictor: str | None = None,
    interaction: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Compare a baseline linear specification with a nested quadratic/interaction extension."""
    if not quadratic_predictor and not interaction:
        raise InputValidationError("Choose a quadratic term or an interaction for the extended specification.")
    baseline = fit_day3_linear_model(data, outcome, numeric_predictors, categorical_predictors)
    extended = fit_day3_linear_model(
        data,
        outcome,
        numeric_predictors,
        categorical_predictors,
        quadratic_predictor=quadratic_predictor,
        interaction=interaction,
    )
    base_model, extended_model = baseline["_model"], extended["_model"]
    added_terms = int(round(extended_model.df_model - base_model.df_model))
    if added_terms < 1:
        raise InputValidationError("The extended model did not add an estimable term beyond the baseline model.")
    numerator = (base_model.ssr - extended_model.ssr) / added_terms
    denominator = extended_model.ssr / extended_model.df_resid
    f_statistic = float(numerator / denominator) if denominator else np.nan
    p_value = float(stats.f.sf(f_statistic, added_terms, extended_model.df_resid)) if np.isfinite(f_statistic) else np.nan
    comparison = pd.DataFrame(
        [
            {"Model": "Baseline", "Residual sum of squares": base_model.ssr, "R²": base_model.rsquared, "Adjusted R²": base_model.rsquared_adj, "Fitted terms": int(base_model.df_model)},
            {"Model": "Extended", "Residual sum of squares": extended_model.ssr, "R²": extended_model.rsquared, "Adjusted R²": extended_model.rsquared_adj, "Fitted terms": int(extended_model.df_model)},
        ]
    ).round(4)
    return {
        "method": "Nested linear-specification comparison",
        "question": f"Does the specified extended conditional-mean term improve in-sample fit beyond the baseline model for {outcome}?",
        "comparison": comparison,
        "nested_test": {"F statistic": f_statistic, "Numerator df": added_terms, "Denominator df": float(extended_model.df_resid), "p-value": p_value},
        "baseline": baseline,
        "extended": extended,
        "interpretation": "The F comparison tests the selected nested restriction under the fitted linear-model assumptions. It does not choose a scientific model automatically or validate prediction beyond these data.",
        "limitations": "A lower residual sum of squares is expected with added terms. Functional form, observed support, substantive rationale, and validation still govern whether the extension is useful.",
    }


def refit_after_case_exclusion(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    categorical_predictors: list[str],
    excluded_rows: list[str],
) -> dict[str, Any]:
    """Fit the stated model after a transparent temporary case exclusion for sensitivity display."""
    labels = {str(index): index for index in data.index}
    absent = [label for label in excluded_rows if label not in labels]
    if absent:
        raise InputValidationError("The selected diagnostic row is not available in the current dataset: " + ", ".join(absent))
    reduced = data.drop(index=[labels[label] for label in excluded_rows])
    if len(reduced) >= len(data):
        raise InputValidationError("Select at least one diagnostic case for a sensitivity refit.")
    result = fit_day3_linear_model(reduced, outcome, numeric_predictors, categorical_predictors)
    result["data_design"] += f" Temporary sensitivity refit excludes original row label(s): {', '.join(excluded_rows)}."
    return result


def _fold_indices(y: np.ndarray, folds: int, seed: int, stratified: bool) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    if stratified:
        parts = [[] for _ in range(folds)]
        for level in (0, 1):
            indices = np.flatnonzero(y == level)
            rng.shuffle(indices)
            for fold, split in enumerate(np.array_split(indices, folds)):
                parts[fold].extend(split.tolist())
        return [np.asarray(sorted(part), dtype=int) for part in parts]
    indices = rng.permutation(len(y))
    return [np.asarray(split, dtype=int) for split in np.array_split(indices, folds)]


def _model_frame_for_validation(data: pd.DataFrame, outcome: str, predictors: list[str]) -> pd.DataFrame:
    frame = data[[outcome, *predictors]].copy()
    frame[predictors] = frame[predictors].apply(pd.to_numeric, errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    if len(frame) < 30:
        raise InputValidationError("Cross-validation needs at least 30 complete records for the selected outcome and predictors.")
    return frame


def cross_validate_day3_model(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    model_kind: ModelKind,
    folds: int = 5,
    seed: int = 2026,
) -> dict[str, Any]:
    """Perform deterministic k-fold cross-validation for the Day 3 linear/logistic labs."""
    if folds < 3 or folds > 10:
        raise InputValidationError("Choose between 3 and 10 folds.")
    frame = _model_frame_for_validation(data, outcome, numeric_predictors)
    if len(frame) < folds * 6:
        raise InputValidationError("Use fewer folds or more data so each fold contains a useful number of records.")
    if model_kind == "logistic":
        levels = sorted(frame[outcome].astype(str).unique().tolist())
        if len(levels) != 2:
            raise InputValidationError("Logistic cross-validation requires exactly two observed outcome levels.")
        y_all = (frame[outcome].astype(str) == levels[1]).astype(int).to_numpy()
        if min(y_all.sum(), len(y_all) - y_all.sum()) < folds * 5:
            raise InputValidationError("Each outcome class needs at least five records per fold for this logistic cross-validation demonstration.")
        split_indices = _fold_indices(y_all, folds, seed, stratified=True)
        rows: list[dict[str, Any]] = []
        all_y, all_p = [], []
        for fold, test_idx in enumerate(split_indices, start=1):
            train_idx = np.setdiff1d(np.arange(len(frame)), test_idx)
            training, testing = frame.iloc[train_idx], frame.iloc[test_idx]
            fitted = fit_day3_logistic_model(training, outcome, numeric_predictors)
            x_test, _ = _design_matrix(testing, numeric_predictors, [], design_columns=fitted["details"]["schema"]["design_columns"])
            y_test = (testing[outcome].astype(str) == levels[1]).astype(int).to_numpy()
            probabilities = np.asarray(fitted["_model"].predict(x_test), dtype=float)
            _, auc = roc_points(y_test, probabilities)
            brier = float(np.mean(np.square(y_test - probabilities)))
            rows.append({"Fold": fold, "Test records": len(testing), "AUC": auc, "Brier score": brier})
            all_y.extend(y_test.tolist())
            all_p.extend(probabilities.tolist())
        _, pooled_auc = roc_points(np.asarray(all_y), np.asarray(all_p))
        pooled_brier = float(np.mean(np.square(np.asarray(all_y) - np.asarray(all_p))))
        return {
            "method": f"{folds}-fold stratified cross-validation of a logistic model",
            "fold_metrics": pd.DataFrame(rows).round(4),
            "summary": {"Out-of-fold AUC": pooled_auc, "Out-of-fold Brier score": pooled_brier},
            "predictions": pd.DataFrame({"Observed event": all_y, "Out-of-fold predicted probability": all_p}).round(5),
            "interpretation": "Each record is scored by a model that did not fit that record. These are internal validation estimates for the chosen random split design, not external validation or a causal effect.",
        }
    if model_kind != "linear":
        raise InputValidationError("Model kind must be linear or logistic.")
    y_all = pd.to_numeric(frame[outcome], errors="coerce").to_numpy(dtype=float)
    split_indices = _fold_indices(y_all, folds, seed, stratified=False)
    rows = []
    observed_all, predicted_all = [], []
    for fold, test_idx in enumerate(split_indices, start=1):
        train_idx = np.setdiff1d(np.arange(len(frame)), test_idx)
        training, testing = frame.iloc[train_idx], frame.iloc[test_idx]
        fitted = fit_day3_linear_model(training, outcome, numeric_predictors)
        x_test, _ = _design_matrix(testing, numeric_predictors, [], design_columns=fitted["details"]["schema"]["design_columns"])
        observed = pd.to_numeric(testing[outcome], errors="coerce").to_numpy(dtype=float)
        predicted = np.asarray(fitted["_model"].predict(x_test), dtype=float)
        rmse = float(np.sqrt(np.mean(np.square(observed - predicted))))
        mae = float(np.mean(np.abs(observed - predicted)))
        rows.append({"Fold": fold, "Test records": len(testing), "RMSE": rmse, "MAE": mae})
        observed_all.extend(observed.tolist())
        predicted_all.extend(predicted.tolist())
    residuals = np.asarray(observed_all) - np.asarray(predicted_all)
    return {
        "method": f"{folds}-fold cross-validation of a linear model",
        "fold_metrics": pd.DataFrame(rows).round(4),
        "summary": {"Out-of-fold RMSE": float(np.sqrt(np.mean(np.square(residuals)))), "Out-of-fold MAE": float(np.mean(np.abs(residuals)))},
        "predictions": pd.DataFrame({"Observed": observed_all, "Out-of-fold prediction": predicted_all}).round(5),
        "interpretation": "Each record is predicted by a model that did not fit that record. These are internal validation estimates for the chosen split design, not an external transportability result or a causal effect.",
    }


def bootstrap_optimism_logistic(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    repetitions: int = 50,
    seed: int = 2026,
) -> dict[str, Any]:
    """Estimate bootstrap optimism for logistic AUC and Brier score with transparent repetitions."""
    if repetitions < 20 or repetitions > 200:
        raise InputValidationError("Choose between 20 and 200 bootstrap repetitions for this demonstration.")
    frame = _model_frame_for_validation(data, outcome, numeric_predictors)
    full = fit_day3_logistic_model(frame, outcome, numeric_predictors)
    full_y = full["_outcome"].to_numpy(dtype=int)
    full_p = full["_probabilities"]
    _, apparent_auc = roc_points(full_y, full_p)
    apparent_brier = float(np.mean(np.square(full_y - full_p)))
    rng = np.random.default_rng(seed)
    success: list[dict[str, float]] = []
    for repetition in range(1, repetitions + 1):
        bootstrap = frame.iloc[rng.integers(0, len(frame), size=len(frame))]
        try:
            fitted = fit_day3_logistic_model(bootstrap, outcome, numeric_predictors)
            boot_y = fitted["_outcome"].to_numpy(dtype=int)
            boot_p = fitted["_probabilities"]
            _, boot_auc = roc_points(boot_y, boot_p)
            boot_brier = float(np.mean(np.square(boot_y - boot_p)))
            x_original, _ = _design_matrix(frame, numeric_predictors, [], design_columns=fitted["details"]["schema"]["design_columns"])
            original_p = np.asarray(fitted["_model"].predict(x_original), dtype=float)
            _, test_auc = roc_points(full_y, original_p)
            test_brier = float(np.mean(np.square(full_y - original_p)))
            success.append({"Repetition": repetition, "Bootstrap AUC": boot_auc, "Original-data AUC": test_auc, "Bootstrap Brier": boot_brier, "Original-data Brier": test_brier})
        except (InputValidationError, np.linalg.LinAlgError, ValueError):
            continue
    if len(success) < max(10, repetitions // 2):
        raise InputValidationError("Too many bootstrap samples produced an unstable logistic model. Simplify the model or use more data.")
    table = pd.DataFrame(success)
    auc_optimism = float((table["Bootstrap AUC"] - table["Original-data AUC"]).mean())
    brier_optimism = float((table["Original-data Brier"] - table["Bootstrap Brier"]).mean())
    return {
        "method": "Bootstrap optimism correction for logistic discrimination and calibration loss",
        "repetitions_requested": repetitions,
        "repetitions_completed": len(table),
        "apparent": {"AUC": apparent_auc, "Brier score": apparent_brier},
        "optimism": {"AUC": auc_optimism, "Brier score": brier_optimism},
        "corrected": {"AUC": apparent_auc - auc_optimism, "Brier score": apparent_brier + brier_optimism},
        "replications": table.round(4),
        "interpretation": "The correction estimates the optimism caused by fitting and evaluating the procedure on the same data. It remains internal validation and does not substitute for external validation.",
    }
