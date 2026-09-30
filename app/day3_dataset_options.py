"""Method-compatible public datasets for the computation-first Day 3 sequence."""
from __future__ import annotations

from typing import Final, TypedDict


class Day3DatasetOption(TypedDict):
    """One public file plus an explicit Day 3 computation rationale."""

    file: str
    method: str
    rationale: str
    caution: str


DAY3_MODULE_IDS: Final[tuple[str, ...]] = tuple(f"d3m{number:02d}" for number in range(1, 11))

DAY3_DATASET_OPTIONS: Final[dict[str, tuple[Day3DatasetOption, ...]]] = {
    "d3m01": (
        {"file": "auto.csv", "method": "Simple least-squares regression: miles per gallon by vehicle weight", "rationale": "`mpg` and `weight` are numeric and support a fitted line, residuals, coefficient uncertainty, and observed-versus-fitted plots.", "caution": "The association is observational; do not interpret the slope as a causal effect of weight on fuel use."},
        {"file": "cars.csv", "method": "Simple least-squares regression: stopping distance by speed", "rationale": "`dist` and `speed` form a compact numeric outcome–predictor pair for fitting a line and inspecting residuals.", "caution": "The speed range is limited, so a fitted line should not be extrapolated beyond observed values."},
        {"file": "trees.csv", "method": "Simple least-squares regression: tree volume by girth", "rationale": "`Volume` and `Girth` provide an interpretable continuous pair for the least-squares computation.", "caution": "Tree geometry may be nonlinear; treat the line as a conditional summary before moving to the specification module."},
    ),
    "d3m02": (
        {"file": "carseats.csv", "method": "Multiple regression: sales by price, income, and advertising", "rationale": "The continuous `Sales` outcome and several numeric predictors permit partial-coefficient, robust-uncertainty, and collinearity calculations.", "caution": "The coefficient for one predictor is conditional on the others; it is not a separate causal effect."},
        {"file": "credit.csv", "method": "Multiple regression: credit balance by income, limit, and rating", "rationale": "The numeric outcome and correlated numeric features make partial comparisons and variance-inflation factors visible.", "caution": "Limit and rating may be strongly collinear, so individual coefficient signs and intervals require care."},
        {"file": "house_prices.csv", "method": "Multiple regression: price by housing characteristics", "rationale": "Price, lot size, bedrooms, and bathrooms support adjusted conditional-mean calculations.", "caution": "Omitted location and quality variables make these conditional associations incomplete descriptions."},
    ),
    "d3m03": (
        {"file": "carseats.csv", "method": "Categorical-predictor regression: sales by shelf location", "rationale": "`Sales` is numeric and `ShelveLoc` has a small number of categorical levels, enabling reference coding and contrasts.", "caution": "The reference group changes coefficient labels, not fitted means; store type is not randomly assigned."},
        {"file": "college.csv", "method": "Categorical-predictor regression: graduation rate by private/public status", "rationale": "`Grad.Rate` is numeric and `Private` is a two-level categorical predictor for treatment coding.", "caution": "The contrast is descriptive unless a defensible design and adjustment rationale are supplied."},
    ),
    "d3m04": (
        {"file": "credit.csv", "method": "Unadjusted-versus-adjusted comparison: balance and income with credit characteristics", "rationale": "Several numeric predictors let the app compare a focal coefficient before and after named adjustments.", "caution": "A coefficient change does not validate the adjustment set or prove that confounding was removed."},
        {"file": "carseats.csv", "method": "Unadjusted-versus-adjusted comparison: sales and price with store characteristics", "rationale": "Numeric store features permit a transparent comparison between two explicitly stated formulas.", "caution": "Do not control mechanically for every column; temporal order and causal structure matter."},
        {"file": "auto.csv", "method": "Unadjusted-versus-adjusted comparison: miles per gallon and weight with vehicle features", "rationale": "Weight, horsepower, displacement, and acceleration support a model-comparison demonstration.", "caution": "Correlated vehicle design features may make an adjusted coefficient unstable rather than causal."},
    ),
    "d3m05": (
        {"file": "cars.csv", "method": "Nested specification: quadratic stopping distance by speed", "rationale": "The numeric one-predictor structure supports a baseline line and an explicit squared-speed extension.", "caution": "A better in-sample fit does not justify extrapolation or identify a physical mechanism."},
        {"file": "motorcycle.csv", "method": "Nested specification: acceleration by time with a quadratic term", "rationale": "`accel` and `times` provide a visibly non-linear teaching relationship for a declared functional-form comparison.", "caution": "A polynomial is a local approximation and may behave implausibly outside the observed time range."},
        {"file": "trees.csv", "method": "Interaction or quadratic specification: tree volume from girth and height", "rationale": "Several numeric size measures support an interaction or quadratic extension beyond a stated baseline model.", "caution": "Select an extension because it is scientifically motivated and check it with residuals and validation."},
    ),
    "d3m06": (
        {"file": "default.csv", "method": "Logistic regression: credit-card default by balance and income", "rationale": "`default` is binary and the financial measures are numeric predictors for log odds, odds ratios, and fitted probabilities.", "caution": "Default is uncommon; odds ratios are not risk ratios and in-sample probabilities are not deployment guarantees."},
        {"file": "pima_train.csv", "method": "Logistic regression: diabetes type by glucose, body-mass index, and age", "rationale": "`type` is binary and the clinical measurements are numeric predictors for a probability model.", "caution": "Check coding and plausible measurement values before interpreting predicted probabilities."},
        {"file": "birth_weight.csv", "method": "Logistic regression: low birth weight by maternal characteristics", "rationale": "The numeric binary `low` outcome and maternal measures support the same logistic computation.", "caution": "This is observational data; a fitted probability is a conditional model summary, not a causal effect."},
    ),
    "d3m07": (
        {"file": "cars.csv", "method": "Residual and heteroskedasticity computation: stopping distance by speed", "rationale": "A compact numeric model permits residual-versus-fitted, quantile–quantile, Breusch–Pagan, and HC3 robust-uncertainty displays.", "caution": "A test or plot indicates a pattern to investigate; it does not dictate an automatic repair."},
        {"file": "house_prices.csv", "method": "Residual and heteroskedasticity computation: housing price model", "rationale": "The continuous price outcome and numeric features support comparisons of conventional and HC3 coefficient intervals.", "caution": "Robust standard errors change uncertainty estimates, not the model's target or omitted-variable bias."},
        {"file": "carseats.csv", "method": "Residual and heteroskedasticity computation: store sales model", "rationale": "Several numeric predictors provide an accessible multivariable residual diagnostic example.", "caution": "Examine the scientific meaning of residual structure before transforming or weighting the outcome."},
    ),
    "d3m08": (
        {"file": "ca_schools.csv", "method": "Leverage and influence sensitivity refit: school outcomes", "rationale": "The numeric school variables support leverage, Cook's-distance, and temporary case-exclusion sensitivity computations.", "caution": "An influential record is not an error by definition; investigate it and report sensitivity rather than deleting it mechanically."},
        {"file": "auto.csv", "method": "Leverage and influence sensitivity refit: fuel-economy model", "rationale": "Vehicle characteristics provide multivariable predictor support for leverage and case-deletion comparisons.", "caution": "Outlying predictors and a large residual measure different things; neither alone is a deletion rule."},
        {"file": "credit.csv", "method": "Leverage and influence sensitivity refit: credit-balance model", "rationale": "The several numeric credit features support coefficient comparison after a transparent temporary exclusion.", "caution": "Report which row labels were excluded for a sensitivity display and why; preserve the original analysis."},
    ),
    "d3m09": (
        {"file": "pima_train.csv", "method": "Prediction performance: thresholds, calibration, and discrimination", "rationale": "The binary `type` outcome supports fitted probabilities, threshold metrics, a calibration display, Brier score, and a receiver-operating-characteristic curve.", "caution": "A threshold encodes costs and benefits; strong ranking does not ensure calibrated probabilities or fairness."},
        {"file": "default.csv", "method": "Prediction performance: credit-card default probabilities", "rationale": "The large binary-outcome dataset supports stable demonstrations of threshold-dependent classification and probability performance.", "caution": "All displayed calibration and discrimination metrics are in-sample until validated on held-out or external data."},
        {"file": "birth_weight.csv", "method": "Prediction performance: low-birth-weight probabilities", "rationale": "The binary `low` field supports a small-sample structure demonstration of the performance calculations.", "caution": "Small samples and sparse events make calibration bins and threshold metrics unstable."},
    ),
    "d3m10": (
        {"file": "pima_test.csv", "method": "Separate-file validation: Pima training file to Pima test file", "rationale": "The module opens the bundled test data and can fit a documented logistic model on the paired bundled training file before one test-file evaluation.", "caution": "Do not use the test-file result to repeatedly tune the model; that would leak test information into model selection."},
        {"file": "default.csv", "method": "Internal validation and bootstrap optimism: default model", "rationale": "The large binary-outcome data support holdout, k-fold cross-validation, and bootstrap-optimism calculations for probability predictions.", "caution": "Internal validation is not external validation and may not mimic a future site, time period, or population."},
        {"file": "auto.csv", "method": "Linear-model holdout and cross-validation: fuel-economy prediction", "rationale": "The numeric outcome and predictors support held-out root-mean-squared error, mean absolute error, and k-fold cross-validation.", "caution": "A random split may not reflect the intended deployment setting; document why the validation design is relevant."},
    ),
}


def day3_dataset_options(module_id: str) -> tuple[Day3DatasetOption, ...] | None:
    """Return method-compatible public options for one Day 3 computation module."""
    return DAY3_DATASET_OPTIONS.get(module_id)
