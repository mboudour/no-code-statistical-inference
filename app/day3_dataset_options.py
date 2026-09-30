"""Curated method-compatible public datasets for all ten Day 3 modules.

The selector intentionally excludes files that have only a superficial column match,
that require frequency weights, or that do not support the module's current
calculation. A displayed option still requires a design, coding, and assumption
check before interpretation.
"""

from __future__ import annotations

from typing import Final, TypedDict


class Day3DatasetOption(TypedDict):
    """One public file plus an explicit method-appropriateness explanation."""

    file: str
    method: str
    rationale: str
    caution: str


DAY3_MODULE_IDS: Final[tuple[str, ...]] = tuple(f"d3m{number:02d}" for number in range(1, 11))


DAY3_DATASET_OPTIONS: Final[dict[str, tuple[Day3DatasetOption, ...]]] = {
    "d3m01": (
        {
            "file": "cars.csv",
            "method": "Simple linear regression: stopping distance by speed",
            "rationale": "`dist` and `speed` are numeric, so the lab can fit a one-predictor conditional-mean model and display fitted values and residuals.",
            "caution": "The observed range is small; do not extrapolate a fitted stopping-distance line beyond it or infer a causal mechanism from these records.",
        },
        {
            "file": "trees.csv",
            "method": "Simple linear regression: tree volume by girth",
            "rationale": "`Volume` and `Girth` supply an interpretable numeric outcome-predictor pair.",
            "caution": "Tree geometry suggests possible nonlinearity; use this first for a linear conditional-mean comparison, then inspect residuals.",
        },
        {
            "file": "women.csv",
            "method": "Simple linear regression: weight by height",
            "rationale": "The two numeric measurements provide a compact simple-regression example.",
            "caution": "There are only 15 records and a restricted support range, so coefficient uncertainty and extrapolation need particular care.",
        },
    ),
    "d3m02": (
        {
            "file": "auto.csv",
            "method": "Multiple regression: miles per gallon by weight, horsepower, and acceleration",
            "rationale": "Several numeric vehicle characteristics support partial-regression, collinearity, and adjusted-comparison discussion.",
            "caution": "Vehicle characteristics are correlated; coefficients are conditional associations, not separate causal effects.",
        },
        {
            "file": "credit.csv",
            "method": "Multiple regression: credit balance by income, limit, and rating",
            "rationale": "A numeric outcome with several numeric predictors supports adjusted coefficient interpretation.",
            "caution": "Credit limit and rating can be strongly collinear; inspect variance-inflation factors and avoid mechanical interpretation of individual signs.",
        },
        {
            "file": "house_prices.csv",
            "method": "Multiple regression: price by lot size, bedrooms, and bathrooms",
            "rationale": "A continuous price outcome and several numeric housing characteristics support an adjusted conditional-mean model.",
            "caution": "The file is observational; omitted location and quality features may make a coefficient an incomplete association.",
        },
    ),
    "d3m03": (
        {
            "file": "carseats.csv",
            "method": "Coefficient intervals: sales by price, income, and advertising",
            "rationale": "The continuous `Sales` outcome and numeric predictors permit conventional and HC3 robust coefficient intervals.",
            "caution": "An interval is conditional on this specification; it is not a prediction interval for a new store.",
        },
        {
            "file": "auto.csv",
            "method": "Coefficient intervals: miles per gallon by vehicle characteristics",
            "rationale": "The numeric structure supports a comparison of coefficient estimates, standard errors, and collinearity diagnostics.",
            "caution": "Intervals may widen when correlated vehicle features are included together; report the selected formula.",
        },
        {
            "file": "college.csv",
            "method": "Coefficient intervals: graduation rate by expenditure and student-faculty ratio",
            "rationale": "Numeric institutional outcomes and predictors support a coefficient-uncertainty example.",
            "caution": "Institutional characteristics are not randomly assigned; do not turn conditional associations into policy-effect claims.",
        },
    ),
    "d3m04": (
        {
            "file": "cars.csv",
            "method": "Specification check: quadratic or log-scale stopping distance by speed",
            "rationale": "The one-predictor structure makes changes in functional form and residual pattern easy to inspect.",
            "caution": "Choose transformations from scientific reasoning and residual evidence, not by searching until a p-value becomes favorable.",
        },
        {
            "file": "motorcycle.csv",
            "method": "Specification check: acceleration by time with a nonlinear term",
            "rationale": "`accel` and `times` provide a plausible curved relationship for comparing linear and quadratic specifications.",
            "caution": "The data are a teaching simulation; a polynomial is a local approximation and can be unstable outside observed times.",
        },
        {
            "file": "trees.csv",
            "method": "Transformation example: tree volume by girth and height",
            "rationale": "Numeric size measures permit an explicit comparison of linear, transformed, and multivariable specifications.",
            "caution": "Do not use a log transformation if it is undefined for the chosen values; record the transformation and its interpretation.",
        },
    ),
    "d3m05": (
        {
            "file": "pima_train.csv",
            "method": "Logistic regression: diabetes type by glucose, body-mass index, and age",
            "rationale": "`type` is binary and the health measurements are numeric predictors, so the app can fit log odds, odds ratios, and predicted probabilities.",
            "caution": "Check the meaning and implausible values of clinical measurements; odds ratios are not risk ratios or causal effects.",
        },
        {
            "file": "birth_weight.csv",
            "method": "Logistic regression: low birth weight by maternal characteristics",
            "rationale": "`low` is a binary numeric indicator and `age` and `lwt` are numeric predictors accepted by the logistic workflow.",
            "caution": "This is observational data; treat fitted probabilities as conditional associations and document the coding of all binary variables.",
        },
        {
            "file": "default.csv",
            "method": "Logistic regression: credit-card default by balance and income",
            "rationale": "`default` is binary and the two financial measures are numeric predictors for a probability model.",
            "caution": "Default is uncommon; report calibration and probability scale alongside odds ratios rather than relying on a p-value.",
        },
    ),
    "d3m06": (
        {
            "file": "default.csv",
            "method": "Threshold analysis: classify default from balance and income",
            "rationale": "The binary outcome and large sample make it suitable for varying a probability threshold and computing sensitivity, specificity, and predictive values.",
            "caution": "Choose thresholds from false-positive and false-negative consequences; accuracy alone can be misleading with an uncommon outcome.",
        },
        {
            "file": "pima_train.csv",
            "method": "Threshold analysis: classify diabetes type from health measurements",
            "rationale": "The binary `type` outcome supports threshold-dependent classification metrics after a logistic model.",
            "caution": "A threshold is a decision rule, not a property of the fitted model; do not use an arbitrary 0.5 cutoff without a cost context.",
        },
        {
            "file": "birth_weight.csv",
            "method": "Threshold analysis: classify low birth weight from maternal measures",
            "rationale": "The binary `low` outcome enables a small-sample demonstration of sensitivity and specificity.",
            "caution": "The modest sample makes threshold metrics unstable; use this for structure and limitations, not deployment claims.",
        },
    ),
    "d3m07": (
        {
            "file": "default.csv",
            "method": "Calibration and discrimination: default probability model",
            "rationale": "The large binary-outcome file supports predicted-probability bins, Brier score, receiver-operating-characteristic curve, and area under the curve.",
            "caution": "In-sample calibration and area under the curve are optimistic; use held-out or external data before treating them as deployment performance.",
        },
        {
            "file": "pima_train.csv",
            "method": "Calibration and discrimination: diabetes-type probability model",
            "rationale": "Binary `type` with numeric predictors supports both probability-calibration and ranking diagnostics.",
            "caution": "A good area under the curve does not ensure calibrated risks, fairness, or transportability to another population.",
        },
        {
            "file": "birth_weight.csv",
            "method": "Calibration and discrimination: low-birth-weight probability model",
            "rationale": "The binary `low` indicator enables probability communication with a smaller teaching dataset.",
            "caution": "Sparse events and a small sample make calibration bins noisy; do not overinterpret a smooth-looking plot.",
        },
    ),
    "d3m08": (
        {
            "file": "college.csv",
            "method": "Diagnostics and influence: graduation rate regression",
            "rationale": "Several numeric institutional variables support residual, leverage, Cook's-distance, and collinearity displays.",
            "caution": "A high Cook's distance is a prompt to investigate the record and target population, not an automatic deletion rule.",
        },
        {
            "file": "auto.csv",
            "method": "Diagnostics and sensitivity: miles per gallon regression",
            "rationale": "Vehicle characteristics support residual and influence checks in a multivariable numeric model.",
            "caution": "Correlated predictors and nonlinearity can both affect a residual pattern; document any alternative specification before comparing results.",
        },
        {
            "file": "carseats.csv",
            "method": "Diagnostics and sensitivity: sales regression",
            "rationale": "A continuous outcome and several plausible numeric predictors support a transparent diagnostic workbench.",
            "caution": "Do not remove unusual stores only to improve fit; explain whether they are errors, distinct subgroups, or legitimate boundary cases.",
        },
    ),
    "d3m09": (
        {
            "file": "pima_train.csv",
            "method": "Internal holdout validation: diabetes-type probability model",
            "rationale": "The binary outcome and numeric predictors support a deterministic stratified train/test split, held-out Brier score, area under the curve, and threshold metrics.",
            "caution": "An internal split is not external validation. Keep the held-out set untouched while choosing predictors and transformations.",
        },
        {
            "file": "default.csv",
            "method": "Internal holdout validation: default probability model",
            "rationale": "A large binary-outcome dataset supports a stable demonstration of holdout validation and prevalence-sensitive metrics.",
            "caution": "Random splitting may not reflect a future time period or site; use temporal or grouped validation when deployment requires it.",
        },
        {
            "file": "auto.csv",
            "method": "Internal holdout validation: miles-per-gallon regression",
            "rationale": "A numeric outcome and several numeric predictors support held-out root mean squared error, mean absolute error, and test R-squared.",
            "caution": "Prediction error on one split has sampling variability and does not establish a causal relation between vehicle features and fuel economy.",
        },
    ),
    "d3m10": (
        {
            "file": "house_prices.csv",
            "method": "Reproducible model record: housing-price regression",
            "rationale": "Numeric price and documented predictors support a formula, diagnostic record, results table, and downloadable reproducibility report.",
            "caution": "The downloaded record documents the current app selections; it cannot supply missing provenance, coding rationale, or causal identification.",
        },
        {
            "file": "ca_schools.csv",
            "method": "Reproducible model record: school test-score regression",
            "rationale": "Multiple numeric school-district measures support an explicit model formula and diagnostic trail.",
            "caution": "Do not include identifier-like fields such as `district` as substantive numeric predictors without a defensible measurement rationale.",
        },
        {
            "file": "doctor_visits.csv",
            "method": "Reproducible exploratory record: doctor-visit count regression",
            "rationale": "`visits` and several numeric covariates support a transparent demonstration of a selected analysis record.",
            "caution": "Counts are not automatically well served by a Gaussian linear model; treat this as a reproducibility example and assess an outcome-appropriate model before substantive inference.",
        },
    ),
}


def day3_dataset_options(module_id: str) -> tuple[Day3DatasetOption, ...] | None:
    """Return curated options for a Day 3 module, or ``None`` for other days."""
    return DAY3_DATASET_OPTIONS.get(module_id)
