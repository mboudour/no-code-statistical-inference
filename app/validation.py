"""Shared, method-specific input validation for no-code inference workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


class InputValidationError(ValueError):
    """Raised when a selected dataset cannot support the requested app workflow."""


@dataclass(frozen=True)
class ValidationSummary:
    method: str
    complete_cases: int
    warnings: tuple[str, ...] = ()


def _numeric(values: pd.Series | np.ndarray, label: str, minimum: int = 2, require_variation: bool = True) -> np.ndarray:
    series = pd.to_numeric(pd.Series(values), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(series) < minimum:
        raise InputValidationError(f"{label} requires at least {minimum} finite, non-missing observation(s); {len(series)} are available after selection.")
    if require_variation and series.nunique() < 2:
        raise InputValidationError(f"{label} has zero observed variation after selection. A standard error or model cannot be estimated from a constant outcome.")
    return series.to_numpy(dtype=float)


def validate_inputs(method: str, data: pd.DataFrame, **selection: Any) -> ValidationSummary:
    """Validate minimum data, degrees of freedom, structure, and rank before model fitting.

    This layer validates data properties that software can inspect. It cannot validate
    scientific design facts such as random sampling, causal identification, or valid pairing.
    """
    if method == "estimate_mean":
        values = _numeric(data[selection["outcome"]], selection["outcome"], minimum=2)
        return ValidationSummary(method, len(values))

    if method == "two_independent":
        outcome, group, levels = selection["outcome"], selection["group"], selection["levels"]
        if len(levels) != 2:
            raise InputValidationError("An independent-group comparison requires exactly two selected group levels.")
        subset = data[[outcome, group]].dropna().copy()
        subset[group] = subset[group].astype(str)
        first = _numeric(subset.loc[subset[group] == str(levels[0]), outcome], f"Group {levels[0]}", minimum=2)
        second = _numeric(subset.loc[subset[group] == str(levels[1]), outcome], f"Group {levels[1]}", minimum=2)
        return ValidationSummary(method, len(first) + len(second))

    if method == "paired":
        first_name, second_name = selection["first_name"], selection["second_name"]
        subset = data[[first_name, second_name]].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if len(subset) < 2:
            raise InputValidationError(f"A paired comparison requires at least two complete pairs; {len(subset)} are available.")
        differences = subset[second_name] - subset[first_name]
        if differences.nunique() < 2:
            raise InputValidationError("All observed paired differences are identical, so a paired standard error and t statistic are undefined. Report the paired differences descriptively instead.")
        return ValidationSummary(method, len(subset))

    if method == "anova":
        outcome, group = selection["outcome"], selection["group"]
        subset = data[[outcome, group]].dropna().copy()
        subset[group] = subset[group].astype(str)
        groups = [values for _, values in subset.groupby(group, sort=True)[outcome]]
        if len(groups) < 3:
            raise InputValidationError("A one-way ANOVA requires at least three observed groups. Use the independent-group workflow for two groups.")
        small = [str(label) for label, values in subset.groupby(group, sort=True)[outcome] if len(values) < 2]
        if small:
            raise InputValidationError("Each ANOVA group requires at least two complete observations. Too small: " + ", ".join(small) + ".")
        _numeric(subset[outcome], outcome, minimum=3)
        zero_variance = [str(label) for label, values in subset.groupby(group, sort=True)[outcome] if pd.Series(values).nunique() < 2]
        warnings = tuple(["The following group(s) have zero within-group variation: " + ", ".join(zero_variance) + ". Interpret any omnibus reference calculation with caution."] if zero_variance else [])
        return ValidationSummary(method, len(subset), warnings)

    if method == "association":
        first, second = selection["first"], selection["second"]
        if first == second:
            raise InputValidationError("Select two distinct categorical variables for an association analysis.")
        if data[[first, second]].dropna(how="all").empty:
            raise InputValidationError("No observed values are available for the selected categorical variables.")
        first_levels = data[first].where(data[first].notna(), "Missing").astype(str).nunique()
        second_levels = data[second].where(data[second].notna(), "Missing").astype(str).nunique()
        warnings = []
        if max(first_levels, second_levels) > 20:
            warnings.append(f"At least one selected variable has more than 20 observed categories ({first_levels} and {second_levels}). This app can form the table, but a high-cardinality sparse table may be pedagogically unhelpful and can weaken simple approximations.")
        return ValidationSummary(method, int(len(data)), tuple(warnings))

    if method == "linear_regression":
        outcome, predictors = selection["outcome"], list(selection["predictors"])
        if not predictors:
            raise InputValidationError("Linear regression requires at least one predictor.")
        if outcome in predictors:
            raise InputValidationError("The outcome cannot also be selected as a predictor.")
        subset = data[[outcome, *predictors]].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        parameters = len(predictors) + 1
        if len(subset) <= parameters:
            raise InputValidationError(f"Linear regression requires more complete cases than fitted parameters. {len(subset)} complete cases are available for {parameters} parameters.")
        _numeric(subset[outcome], outcome, minimum=parameters + 1)
        constants = [name for name in predictors if subset[name].nunique() < 2]
        if constants:
            raise InputValidationError("Constant predictor(s) cannot be included: " + ", ".join(constants) + ".")
        design = np.column_stack([np.ones(len(subset)), subset[predictors].to_numpy(dtype=float)])
        if np.linalg.matrix_rank(design) < parameters:
            raise InputValidationError("The selected predictor matrix is rank deficient (perfect collinearity or redundant coding). Remove or recode a predictor.")
        return ValidationSummary(method, len(subset))

    if method == "logistic_regression":
        outcome, predictors = selection["outcome"], list(selection["predictors"])
        if not predictors:
            raise InputValidationError("Logistic regression requires at least one predictor.")
        if outcome in predictors:
            raise InputValidationError("The binary outcome cannot also be selected as a predictor.")
        subset = data[[outcome, *predictors]].copy()
        subset[predictors] = subset[predictors].apply(pd.to_numeric, errors="coerce")
        subset = subset.replace([np.inf, -np.inf], np.nan).dropna()
        classes = sorted(subset[outcome].astype(str).unique().tolist())
        if len(classes) != 2:
            raise InputValidationError("Logistic regression requires exactly two observed outcome classes after complete-case selection.")
        y = (subset[outcome].astype(str) == classes[1]).astype(int)
        event_counts = y.value_counts().to_dict()
        parameters = len(predictors) + 1
        minimum_events = 5 * parameters
        if min(event_counts.values()) < minimum_events:
            raise InputValidationError(f"The smaller outcome class has {min(event_counts.values())} observations. This app requires at least {minimum_events} per class for {parameters} fitted parameters to reduce sparse-event risk.")
        constants = [name for name in predictors if subset[name].nunique() < 2]
        if constants:
            raise InputValidationError("Constant predictor(s) cannot be included: " + ", ".join(constants) + ".")
        design = np.column_stack([np.ones(len(subset)), subset[predictors].to_numpy(dtype=float)])
        if np.linalg.matrix_rank(design) < parameters:
            raise InputValidationError("The selected predictor matrix is rank deficient (perfect collinearity or redundant coding). Remove or recode a predictor.")
        separation_risks = []
        for predictor in predictors:
            values_zero = subset.loc[y == 0, predictor]
            values_one = subset.loc[y == 1, predictor]
            if values_zero.max() < values_one.min() or values_one.max() < values_zero.min():
                separation_risks.append(predictor)
        warnings = tuple(["Visible single-predictor range separation risk for: " + ", ".join(separation_risks) + ". This is a screen, not proof that multivariable separation is absent or present. Logistic coefficients may be non-finite; simplify the model or use a penalized method outside this workflow."] if separation_risks else [])
        return ValidationSummary(method, len(subset), warnings)

    raise InputValidationError(f"Unknown validation method: {method}.")
