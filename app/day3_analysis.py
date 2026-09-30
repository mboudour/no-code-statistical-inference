"""Computation helpers for the Day 3 regression, prediction, and validation labs.

The functions here remain independent of Streamlit so that the calculations can be
unit-tested. They deliberately expose diagnostics and uncertainty rather than
turning a fitted model into a single opaque score.
"""

from __future__ import annotations

from typing import Any, Literal
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.sm_exceptions import ConvergenceWarning, PerfectSeparationError

from validation import InputValidationError


ModelKind = Literal["linear", "logistic"]


def _finite_numeric(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    converted = data[columns].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return converted


def _model_frame(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    categorical_predictors: list[str] | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Build a complete-case model frame without silently coercing categorical values."""
    categorical_predictors = categorical_predictors or []
    numeric_predictors = list(dict.fromkeys(numeric_predictors))
    categorical_predictors = list(dict.fromkeys(categorical_predictors))
    if not numeric_predictors and not categorical_predictors:
        raise InputValidationError("Select at least one numeric or categorical predictor.")
    if outcome in numeric_predictors or outcome in categorical_predictors:
        raise InputValidationError("The outcome cannot also be selected as a predictor.")
    overlap = set(numeric_predictors).intersection(categorical_predictors)
    if overlap:
        raise InputValidationError("A predictor cannot be both numeric and categorical: " + ", ".join(sorted(overlap)) + ".")
    columns = [outcome, *numeric_predictors, *categorical_predictors]
    if any(column not in data.columns for column in columns):
        missing = [column for column in columns if column not in data.columns]
        raise InputValidationError("Selected columns are unavailable: " + ", ".join(missing) + ".")
    frame = data[columns].copy()
    if numeric_predictors:
        frame[numeric_predictors] = _finite_numeric(frame, numeric_predictors)
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna().copy()
    if frame.empty:
        raise InputValidationError("No complete observations remain after applying the selected outcome and predictors.")
    for column in categorical_predictors:
        frame[column] = frame[column].astype(str)
        if frame[column].nunique() < 2:
            raise InputValidationError(f"Categorical predictor {column} has fewer than two observed levels after complete-case selection.")
        if frame[column].nunique() > 12:
            raise InputValidationError(f"Categorical predictor {column} has more than 12 observed levels. Recode or select a lower-cardinality factor for this teaching workflow.")
    for column in numeric_predictors:
        if frame[column].nunique() < 2:
            raise InputValidationError(f"Numeric predictor {column} has zero observed variation after complete-case selection.")
    return frame, categorical_predictors


def _design_matrix(
    frame: pd.DataFrame,
    numeric_predictors: list[str],
    categorical_predictors: list[str],
    quadratic_predictor: str | None = None,
    log1p_predictor: str | None = None,
    interaction: tuple[str, str] | None = None,
    design_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Encode numeric transformations and treatment-coded categorical predictors."""
    if quadratic_predictor and log1p_predictor:
        raise InputValidationError("Choose either a quadratic or a log1p transformation for the primary predictor, not both in this teaching workflow.")
    if quadratic_predictor and quadratic_predictor not in numeric_predictors:
        raise InputValidationError("The quadratic predictor must also be selected as a numeric predictor.")
    if log1p_predictor and log1p_predictor not in numeric_predictors:
        raise InputValidationError("The log1p predictor must also be selected as a numeric predictor.")
    if log1p_predictor and (frame[log1p_predictor] <= -1).any():
        raise InputValidationError(f"log1p({log1p_predictor}) is undefined for observed values less than or equal to -1. Choose another transformation or recode the variable transparently.")
    if interaction and (interaction[0] not in numeric_predictors or interaction[1] not in numeric_predictors):
        raise InputValidationError("Both members of a numeric interaction must be selected numeric predictors.")
    x = frame[numeric_predictors].astype(float).copy() if numeric_predictors else pd.DataFrame(index=frame.index)
    category_levels: dict[str, list[str]] = {}
    if categorical_predictors:
        for column in categorical_predictors:
            category_levels[column] = sorted(frame[column].astype(str).unique().tolist())
        dummies = pd.get_dummies(
            frame[categorical_predictors].astype(str),
            prefix=categorical_predictors,
            prefix_sep="=",
            drop_first=True,
            dtype=float,
        )
        x = pd.concat([x, dummies], axis=1)
    if quadratic_predictor:
        x[f"{quadratic_predictor}²"] = np.square(frame[quadratic_predictor].astype(float))
    if log1p_predictor:
        x[f"log1p({log1p_predictor})"] = np.log1p(frame[log1p_predictor].astype(float))
    if interaction:
        left, right = interaction
        x[f"{left} × {right}"] = frame[left].astype(float) * frame[right].astype(float)
    x = sm.add_constant(x, has_constant="add").astype(float)
    if design_columns is not None:
        x = x.reindex(columns=design_columns, fill_value=0.0)
    schema = {
        "numeric_predictors": list(numeric_predictors),
        "categorical_predictors": list(categorical_predictors),
        "quadratic_predictor": quadratic_predictor,
        "log1p_predictor": log1p_predictor,
        "interaction": interaction,
        "category_levels": category_levels,
        "design_columns": x.columns.tolist(),
    }
    return x, schema


def _coefficient_table(params: Any, bse: Any, conf: Any, pvalues: Any, names: list[str], estimate_name: str = "Estimate") -> pd.DataFrame:
    return pd.DataFrame(
        {
            estimate_name: np.asarray(params, dtype=float),
            "SE": np.asarray(bse, dtype=float),
            "CI low": np.asarray(conf, dtype=float)[:, 0],
            "CI high": np.asarray(conf, dtype=float)[:, 1],
            "p-value": np.asarray(pvalues, dtype=float),
        },
        index=names,
    ).round(4)


def _safe_breusch_pagan(residuals: pd.Series, x: pd.DataFrame) -> dict[str, Any]:
    try:
        statistic, p_value, _, _ = het_breuschpagan(residuals, x)
        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "message": "This tests one residual-variance pattern; it is not a universal model-validity test.",
        }
    except (ValueError, np.linalg.LinAlgError) as error:
        return {"message": f"Breusch–Pagan calculation was unavailable: {error}"}


def _vif_table(x: pd.DataFrame) -> pd.DataFrame:
    if x.shape[1] <= 2:
        return pd.DataFrame({"Predictor": ["Only one non-intercept predictor"], "VIF": [np.nan]})
    rows = []
    for index, name in enumerate(x.columns):
        if name == "const":
            continue
        try:
            value = float(variance_inflation_factor(x.to_numpy(), index))
        except (ValueError, np.linalg.LinAlgError):
            value = float("inf")
        rows.append({"Predictor": name, "VIF": value})
    return pd.DataFrame(rows).round(3)


def fit_day3_linear_model(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    categorical_predictors: list[str] | None = None,
    quadratic_predictor: str | None = None,
    log1p_predictor: str | None = None,
    interaction: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Fit a transparent Day 3 ordinary least-squares model with diagnostics."""
    frame, categorical_predictors = _model_frame(data, outcome, numeric_predictors, categorical_predictors)
    y = pd.to_numeric(frame[outcome], errors="coerce")
    if y.nunique() < 2:
        raise InputValidationError(f"Outcome {outcome} has zero observed variation after complete-case selection.")
    x, schema = _design_matrix(
        frame,
        numeric_predictors,
        categorical_predictors,
        quadratic_predictor=quadratic_predictor,
        log1p_predictor=log1p_predictor,
        interaction=interaction,
    )
    parameter_count = x.shape[1]
    if len(frame) <= parameter_count:
        raise InputValidationError(f"The model has {parameter_count} parameters but only {len(frame)} complete rows. Select fewer terms or more data.")
    if np.linalg.matrix_rank(x.to_numpy()) < parameter_count:
        raise InputValidationError("The selected model matrix is rank deficient. Remove redundant predictors, categories, transformations, or interactions.")
    model = sm.OLS(y.astype(float), x).fit()
    robust = model.get_robustcov_results(cov_type="HC3")
    influence = model.get_influence()
    standardized = np.asarray(influence.resid_studentized_internal, dtype=float)
    leverage = np.asarray(influence.hat_matrix_diag, dtype=float)
    cooks = np.asarray(influence.cooks_distance[0], dtype=float)
    qq_theoretical, qq_ordered = stats.probplot(standardized, dist="norm", fit=False)
    diagnostics_frame = pd.DataFrame(
        {
            "Row": frame.index.astype(str),
            "Observed": y.to_numpy(dtype=float),
            "Fitted": np.asarray(model.fittedvalues, dtype=float),
            "Residual": np.asarray(model.resid, dtype=float),
            "Standardized residual": standardized,
            "Leverage": leverage,
            "Cook's distance": cooks,
        }
    )
    coefficients = _coefficient_table(model.params, model.bse, model.conf_int(), model.pvalues, x.columns.tolist())
    robust_coefficients = _coefficient_table(robust.params, robust.bse, robust.conf_int(), robust.pvalues, x.columns.tolist())
    leverage_screen = 2 * parameter_count / len(frame)
    cooks_screen = 4 / max(len(frame) - parameter_count, 1)
    formula_terms = list(x.columns.drop("const"))
    return {
        "method": "Ordinary least squares linear regression with diagnostic and HC3 robust-uncertainty views",
        "question": f"How is {outcome} conditionally associated with the selected predictors under the stated linear model?",
        "data_design": f"{len(frame)} complete records; {parameter_count - 1} non-intercept fitted term(s). Numeric predictors are treated as numeric; categorical predictors are treatment-coded with the first sorted observed level as reference.",
        "assumptions": [
            "Rows are independent under the study design.",
            "The selected conditional-mean form is substantively and empirically adequate over the observed support.",
            "The reported coefficient uncertainty is conditional on the selected formula; HC3 robust standard errors address a variance-model concern, not confounding, dependence, or specification bias.",
        ],
        "diagnostics": {
            "breusch_pagan": _safe_breusch_pagan(model.resid, x),
            "largest_cooks_distance": float(np.max(cooks)),
            "leverage_screen": float(leverage_screen),
            "cooks_distance_screen": float(cooks_screen),
            "observations_above_leverage_screen": int(np.sum(leverage > leverage_screen)),
            "observations_above_cooks_screen": int(np.sum(cooks > cooks_screen)),
        },
        "estimate": coefficients,
        "uncertainty": "Conventional and HC3 robust coefficient intervals are displayed. They are model-based and do not convert an observational association into a causal effect.",
        "effect_size": f"R² = {model.rsquared:.3f}; adjusted R² = {model.rsquared_adj:.3f}; residual standard error = {np.sqrt(model.mse_resid):.3f}",
        "test": f"Model F({int(model.df_model)}, {int(model.df_resid)}) = {model.fvalue:.3f}, p = {model.f_pvalue:.4f}",
        "interpretation": "Coefficients are conditional comparisons under the selected formula and coding; they are not automatically causal effects or out-of-sample guarantees.",
        "limitations": "Residual patterns, high leverage, influential cases, collinearity, omitted variables, extrapolation, selection, and dependence can change the interpretation.",
        "next_step": "Inspect the residual, quantile–quantile, leverage, and Cook's-distance views; compare only defensible alternative specifications and document the result.",
        "details": {
            "n": int(len(frame)),
            "formula_terms": formula_terms,
            "coefficients": coefficients,
            "robust_hc3_coefficients": robust_coefficients,
            "diagnostic_cases": diagnostics_frame.round(5),
            "qq_points": pd.DataFrame({"Normal theoretical quantile": qq_theoretical, "Ordered standardized residual": qq_ordered}).round(5),
            "vif": _vif_table(x),
            "schema": schema,
        },
        "_model": model,
        "_design": x,
        "_frame": frame,
    }


def _binary_outcome(frame: pd.DataFrame, outcome: str) -> tuple[pd.Series, list[str]]:
    levels = sorted(frame[outcome].astype(str).unique().tolist())
    if len(levels) != 2:
        raise InputValidationError("Logistic regression requires exactly two observed outcome levels after complete-case selection.")
    y = (frame[outcome].astype(str) == levels[1]).astype(int)
    return y, levels


def roc_points(y: np.ndarray | pd.Series, probabilities: np.ndarray | pd.Series) -> tuple[pd.DataFrame, float]:
    """Return receiver-operating-characteristic points and tie-aware AUC without sklearn."""
    y = np.asarray(y, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    positives = int(y.sum())
    negatives = int(len(y) - positives)
    if positives == 0 or negatives == 0:
        raise InputValidationError("Receiver-operating-characteristic calculations require both outcome classes.")
    thresholds = np.r_[np.inf, np.unique(probabilities)[::-1], -np.inf]
    rows = []
    for threshold in thresholds:
        predicted = probabilities >= threshold
        tp = int(np.sum((predicted == 1) & (y == 1)))
        fp = int(np.sum((predicted == 1) & (y == 0)))
        rows.append({"Threshold": float(threshold), "False positive rate": fp / negatives, "True positive rate": tp / positives})
    ranks = stats.rankdata(probabilities, method="average")
    auc = float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))
    return pd.DataFrame(rows), auc


def calibration_table(y: np.ndarray | pd.Series, probabilities: np.ndarray | pd.Series, bins: int = 10) -> pd.DataFrame:
    """Group probability forecasts into fixed bins for a descriptive calibration plot."""
    y = np.asarray(y, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    breaks = np.linspace(0, 1, bins + 1)
    groups = pd.cut(probabilities, breaks, include_lowest=True, duplicates="drop")
    table = pd.DataFrame({"Predicted probability": probabilities, "Observed event": y, "Bin": groups})
    summary = table.groupby("Bin", observed=True).agg(
        Records=("Observed event", "size"),
        Mean_predicted_probability=("Predicted probability", "mean"),
        Observed_event_rate=("Observed event", "mean"),
    ).reset_index()
    summary["Bin"] = summary["Bin"].astype(str)
    return summary.round(4)


def classification_metrics(y: np.ndarray | pd.Series, probabilities: np.ndarray | pd.Series, threshold: float = 0.5) -> dict[str, float | int]:
    """Calculate threshold-dependent classification counts and rates."""
    if not 0 < threshold < 1:
        raise InputValidationError("Choose a classification threshold strictly between 0 and 1.")
    y = np.asarray(y, dtype=int)
    predicted = np.asarray(probabilities, dtype=float) >= threshold
    tp = int(np.sum((predicted == 1) & (y == 1)))
    fn = int(np.sum((predicted == 0) & (y == 1)))
    fp = int(np.sum((predicted == 1) & (y == 0)))
    tn = int(np.sum((predicted == 0) & (y == 0)))
    return {
        "threshold": float(threshold),
        "true_positive": tp,
        "false_negative": fn,
        "false_positive": fp,
        "true_negative": tn,
        "sensitivity": tp / (tp + fn) if tp + fn else float("nan"),
        "specificity": tn / (tn + fp) if tn + fp else float("nan"),
        "positive_predictive_value": tp / (tp + fp) if tp + fp else float("nan"),
        "negative_predictive_value": tn / (tn + fn) if tn + fn else float("nan"),
        "accuracy": (tp + tn) / len(y) if len(y) else float("nan"),
    }


def fit_day3_logistic_model(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    categorical_predictors: list[str] | None = None,
) -> dict[str, Any]:
    """Fit a logistic model and return probability, calibration, and threshold diagnostics."""
    frame, categorical_predictors = _model_frame(data, outcome, numeric_predictors, categorical_predictors)
    y, levels = _binary_outcome(frame, outcome)
    x, schema = _design_matrix(frame, numeric_predictors, categorical_predictors)
    parameter_count = x.shape[1]
    event_counts = y.value_counts().to_dict()
    minimum_events = 5 * parameter_count
    if min(event_counts.values()) < minimum_events:
        raise InputValidationError(f"The smaller outcome class has {min(event_counts.values())} records. This teaching workflow requires at least {minimum_events} per class for {parameter_count} parameters.")
    if np.linalg.matrix_rank(x.to_numpy()) < parameter_count:
        raise InputValidationError("The selected logistic-model matrix is rank deficient. Remove redundant predictors or category levels.")
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model = sm.Logit(y, x).fit(disp=False, maxiter=100)
        if not bool(model.mle_retvals.get("converged", False)) or any(issubclass(item.category, ConvergenceWarning) for item in caught):
            raise InputValidationError("The logistic model did not converge reliably. Simplify predictors, check separation/sparsity, or use a penalized method outside this workflow.")
    except PerfectSeparationError as error:
        raise InputValidationError("Perfect separation was detected. Standard logistic coefficients are not finite; simplify the model or use a penalized method outside this workflow.") from error
    except np.linalg.LinAlgError as error:
        raise InputValidationError("The logistic information matrix is singular, often because of separation or redundant information. Simplify the model.") from error
    probabilities = np.asarray(model.predict(x), dtype=float)
    roc, auc = roc_points(y, probabilities)
    calibration = calibration_table(y, probabilities)
    default_threshold = classification_metrics(y, probabilities, 0.5)
    conf = model.conf_int()
    coefficients = pd.DataFrame(
        {
            "Log-odds estimate": model.params,
            "Odds ratio": np.exp(model.params),
            "CI low OR": np.exp(conf.iloc[:, 0]),
            "CI high OR": np.exp(conf.iloc[:, 1]),
            "p-value": model.pvalues,
        }
    ).round(4)
    probability_frame = pd.DataFrame(
        {"Row": frame.index.astype(str), "Observed event": y.to_numpy(dtype=int), "Predicted probability": probabilities}
    ).round(5)
    brier = float(np.mean(np.square(y.to_numpy(dtype=float) - probabilities)))
    return {
        "method": "Logistic regression with predicted probabilities, calibration, discrimination, and threshold metrics",
        "question": f"How is the probability of {levels[1]} conditionally associated with the selected predictors?",
        "data_design": f"{len(frame)} complete records; reference outcome={levels[0]}, event outcome={levels[1]}; {parameter_count - 1} non-intercept fitted term(s).",
        "assumptions": [
            "Rows are independent under the study design.",
            "The selected predictors have an adequate relationship with the log odds over the observed support.",
            "There are sufficient records in both outcome classes and no problematic separation.",
        ],
        "diagnostics": {
            "event_outcome": levels[1],
            "outcome_counts": {levels[0]: int((y == 0).sum()), levels[1]: int((y == 1).sum())},
            "minimum_predicted_probability": float(probabilities.min()),
            "maximum_predicted_probability": float(probabilities.max()),
            "brier_score": brier,
            "area_under_roc_curve": auc,
        },
        "estimate": coefficients,
        "uncertainty": "Odds-ratio intervals are conditional on the stated model and predictor scale. Probability calibration and discrimination are reported separately.",
        "effect_size": f"McFadden pseudo R² = {model.prsquared:.3f}; in-sample Brier score = {brier:.4f}; in-sample AUC = {auc:.3f}",
        "test": f"Model likelihood-ratio p = {model.llr_pvalue:.4f}",
        "interpretation": "Odds ratios and probabilities are conditional model summaries. A probability threshold encodes decision consequences; neither odds ratios nor threshold metrics establish causal effects.",
        "limitations": "In-sample calibration and discrimination are optimistic. Separation, sparse outcomes, nonlinear log odds, omitted variables, dependence, and transportability require separate investigation.",
        "next_step": "Inspect the probability, calibration, receiver-operating-characteristic, and threshold views; validate the full modeling procedure on suitable new data.",
        "details": {
            "n": int(len(frame)),
            "event_level": levels[1],
            "reference_level": levels[0],
            "coefficients": coefficients,
            "probability_cases": probability_frame,
            "calibration": calibration,
            "roc": roc.round(5),
            "threshold_0_5": default_threshold,
            "schema": schema,
        },
        "_model": model,
        "_design": x,
        "_frame": frame,
        "_outcome": y,
        "_probabilities": probabilities,
    }


def holdout_validation(
    data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
    model_kind: ModelKind,
    test_fraction: float = 0.25,
    seed: int = 2026,
) -> dict[str, Any]:
    """Evaluate a numeric-predictor linear or logistic model on an untouched holdout set."""
    if not 0.1 <= test_fraction <= 0.5:
        raise InputValidationError("Choose a test fraction between 0.10 and 0.50.")
    frame, _ = _model_frame(data, outcome, numeric_predictors, [])
    if len(frame) < 30:
        raise InputValidationError("Holdout validation needs at least 30 complete records in this teaching workflow; use a larger dataset or resampling design.")
    rng = np.random.default_rng(seed)
    if model_kind == "logistic":
        y, levels = _binary_outcome(frame, outcome)
        train_idx: list[int] = []
        test_idx: list[int] = []
        for level in (0, 1):
            positions = np.flatnonzero(y.to_numpy() == level)
            rng.shuffle(positions)
            n_test = max(1, int(round(len(positions) * test_fraction)))
            if len(positions) - n_test < 5:
                raise InputValidationError("The requested split leaves too few records in an outcome class for a stable training model. Reduce the test fraction or use more data.")
            test_idx.extend(positions[:n_test].tolist())
            train_idx.extend(positions[n_test:].tolist())
        training = frame.iloc[sorted(train_idx)].copy()
        testing = frame.iloc[sorted(test_idx)].copy()
        fitted = fit_day3_logistic_model(training, outcome, numeric_predictors)
        schema = fitted["details"]["schema"]
        x_test, _ = _design_matrix(testing, numeric_predictors, [], design_columns=schema["design_columns"])
        y_test, test_levels = _binary_outcome(testing, outcome)
        if test_levels != levels:
            raise InputValidationError("Outcome coding changed between training and test data. Use a common documented binary coding.")
        probabilities = np.asarray(fitted["_model"].predict(x_test), dtype=float)
        roc, auc = roc_points(y_test, probabilities)
        brier = float(np.mean(np.square(y_test.to_numpy(dtype=float) - probabilities)))
        threshold = classification_metrics(y_test, probabilities, 0.5)
        test_cases = pd.DataFrame({"Row": testing.index.astype(str), "Observed event": y_test.to_numpy(dtype=int), "Predicted probability": probabilities}).round(5)
        return {
            "method": "Stratified holdout validation of a logistic model",
            "question": f"How does a model for {outcome} perform on an untouched holdout sample?",
            "data_design": f"Deterministic stratified split with seed={seed}: {len(training)} training and {len(testing)} test records; test fraction requested={test_fraction:.0%}.",
            "assumptions": ["The split mimics the intended deployment setting.", "All preprocessing and model choices were confined to training data.", "Rows are independent and the binary outcome coding is stable."],
            "diagnostics": {"test_brier_score": brier, "test_auc": auc, "threshold_0_5": threshold},
            "estimate": pd.DataFrame({"Metric": ["Test Brier score", "Test AUC", "Test accuracy at 0.50"], "Value": [brier, auc, threshold["accuracy"]]}).round(4),
            "uncertainty": "One holdout split is variable. Repeat or resample only within a validation plan; do not tune repeatedly on the same test set.",
            "effect_size": f"Test AUC = {auc:.3f}; test Brier score = {brier:.4f}",
            "test": "No null-hypothesis test is reported for a validation metric.",
            "interpretation": "These are held-out predictive metrics for the chosen split, not proof of clinical, practical, causal, or external validity.",
            "limitations": "A random internal split may not resemble a future site, time period, or population. Test data should remain untouched during model revision.",
            "next_step": "Use grouped or temporal validation when deployment has groups or time order; seek external validation for transportability.",
            "details": {"test_predictions": test_cases, "roc": roc.round(5), "calibration": calibration_table(y_test, probabilities), "threshold_0_5": threshold, "seed": seed},
        }
    if model_kind != "linear":
        raise InputValidationError("Validation model kind must be linear or logistic.")
    outcome_values = pd.to_numeric(frame[outcome], errors="coerce")
    if outcome_values.nunique() < 2:
        raise InputValidationError("Linear holdout validation requires a numeric outcome with observed variation.")
    positions = rng.permutation(len(frame))
    n_test = max(3, int(round(len(frame) * test_fraction)))
    if len(frame) - n_test <= len(numeric_predictors) + 1:
        raise InputValidationError("The split leaves too few training records for the selected linear model. Reduce the test fraction or select fewer predictors.")
    testing = frame.iloc[positions[:n_test]].copy()
    training = frame.iloc[positions[n_test:]].copy()
    fitted = fit_day3_linear_model(training, outcome, numeric_predictors)
    schema = fitted["details"]["schema"]
    x_test, _ = _design_matrix(testing, numeric_predictors, [], design_columns=schema["design_columns"])
    observed = pd.to_numeric(testing[outcome], errors="coerce").to_numpy(dtype=float)
    predicted = np.asarray(fitted["_model"].predict(x_test), dtype=float)
    residual = observed - predicted
    rmse = float(np.sqrt(np.mean(np.square(residual))))
    mae = float(np.mean(np.abs(residual)))
    denominator = float(np.sum(np.square(observed - observed.mean())))
    test_r2 = float(1 - np.sum(np.square(residual)) / denominator) if denominator else float("nan")
    test_cases = pd.DataFrame({"Row": testing.index.astype(str), "Observed": observed, "Predicted": predicted, "Residual": residual}).round(5)
    return {
        "method": "Holdout validation of a linear regression model",
        "question": f"How does a model for {outcome} perform on an untouched holdout sample?",
        "data_design": f"Deterministic random split with seed={seed}: {len(training)} training and {len(testing)} test records; test fraction requested={test_fraction:.0%}.",
        "assumptions": ["The split mimics the intended deployment setting.", "All preprocessing and model choices were confined to training data.", "The test outcome is on the same scale and has the same meaning as the training outcome."],
        "diagnostics": {"test_rmse": rmse, "test_mae": mae, "test_r_squared": test_r2},
        "estimate": pd.DataFrame({"Metric": ["Test root mean squared error", "Test mean absolute error", "Test R²"], "Value": [rmse, mae, test_r2]}).round(4),
        "uncertainty": "One holdout split is variable. Repeat or resample only within a validation plan; do not tune repeatedly on the same test set.",
        "effect_size": f"Test RMSE = {rmse:.3f}; test MAE = {mae:.3f}; test R² = {test_r2:.3f}",
        "test": "No null-hypothesis test is reported for a validation metric.",
        "interpretation": "These are held-out predictive metrics for the selected split, not proof of causal validity or transportability.",
        "limitations": "A random internal split may not resemble a future site, time period, or population. Test data should remain untouched during model revision.",
        "next_step": "Use grouped or temporal validation when deployment has groups or time order; seek external validation for transportability.",
        "details": {"test_predictions": test_cases, "seed": seed},
    }


def external_logistic_validation(
    training_data: pd.DataFrame,
    testing_data: pd.DataFrame,
    outcome: str,
    numeric_predictors: list[str],
) -> dict[str, Any]:
    """Fit on a named training file and evaluate once on a separate named test file."""
    training_result = fit_day3_logistic_model(training_data, outcome, numeric_predictors)
    testing_frame, _ = _model_frame(testing_data, outcome, numeric_predictors, [])
    y_test, test_levels = _binary_outcome(testing_frame, outcome)
    if test_levels != [training_result["details"]["reference_level"], training_result["details"]["event_level"]]:
        raise InputValidationError("Training and test data use different outcome levels or coding. Document a common binary outcome definition before validation.")
    schema = training_result["details"]["schema"]
    x_test, _ = _design_matrix(testing_frame, numeric_predictors, [], design_columns=schema["design_columns"])
    probabilities = np.asarray(training_result["_model"].predict(x_test), dtype=float)
    roc, auc = roc_points(y_test, probabilities)
    brier = float(np.mean(np.square(y_test.to_numpy(dtype=float) - probabilities)))
    threshold = classification_metrics(y_test, probabilities, 0.5)
    test_cases = pd.DataFrame(
        {"Row": testing_frame.index.astype(str), "Observed event": y_test.to_numpy(dtype=int), "Predicted probability": probabilities}
    ).round(5)
    return {
        "method": "External-file validation of a logistic model",
        "question": f"How does a model trained on the named training file perform on a separate named test file for {outcome}?",
        "data_design": f"Training records={training_result['details']['n']}; separate test records={len(testing_frame)}; outcome event={training_result['details']['event_level']}.",
        "assumptions": ["The separate test file represents the intended future population, site, or time period closely enough for this validation question.", "All model choices were finalized using training data only.", "Outcome coding and predictor measurement are comparable across the two files."],
        "diagnostics": {"test_brier_score": brier, "test_auc": auc, "threshold_0_5": threshold},
        "estimate": pd.DataFrame({"Metric": ["Test Brier score", "Test AUC", "Test accuracy at 0.50"], "Value": [brier, auc, threshold["accuracy"]]}).round(4),
        "uncertainty": "One test file produces a single performance estimate. Quantify sampling uncertainty and evaluate additional sites or periods when decisions require it.",
        "effect_size": f"Test AUC = {auc:.3f}; test Brier score = {brier:.4f}",
        "test": "No null-hypothesis test is reported for a validation metric.",
        "interpretation": "The displayed metrics describe performance on this separate test file, not a causal effect or a guarantee for every new setting.",
        "limitations": "A named test file can still differ from deployment in case mix, measurement, prevalence, or time. Reusing it to tune the model would destroy its role as a final assessment.",
        "next_step": "Preserve the test-file result, document the exact training specification, and seek additional temporal, grouped, or external validation when the target setting differs.",
        "details": {"test_predictions": test_cases, "roc": roc.round(5), "calibration": calibration_table(y_test, probabilities), "threshold_0_5": threshold},
    }
