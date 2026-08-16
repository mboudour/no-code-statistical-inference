# R Analysis Engine

This directory is reserved for R implementations of selected statistical procedures used by the Streamlit companion app. It is not a second user interface. The app remains a single no-code browser experience; this directory allows an analysis request to be executed with R when that is the appropriate or validated implementation.

## Integration contract

Each R procedure should be executable non-interactively through `Rscript` and should follow this workflow:

1. Read a validated request from a JSON file or a temporary CSV plus a parameter file.
2. Apply the stated missing-data treatment and model settings.
3. Return a standard JSON result containing estimates, uncertainty intervals, test statistics, p-values, effect sizes where applicable, warnings, engine metadata, and paths to generated figures.
4. Exit with a meaningful non-zero status and a human-readable error message if the request cannot be completed.

The Python interface should never evaluate uploaded code or user-supplied R expressions.

## Initial dual-engine targets

| Procedure | Expected R implementation | Python parity target |
|---|---|---|
| Descriptive statistics | `summary()` and tidy result formatting | `pandas` / `numpy` |
| Independent-samples comparison | `stats::t.test()` | `scipy.stats.ttest_ind(..., equal_var = FALSE)` |
| Chi-square test | `stats::chisq.test()` | `scipy.stats.chi2_contingency()` |
| One-way ANOVA | `stats::aov()` | `scipy.stats.f_oneway()` or a validated model library |
| Linear regression | `stats::lm()` | `statsmodels` OLS |

## Visualization standard

The R engine uses **ggplot2** as its plotting standard. It should create `ggplot` objects with explicit data mappings, geometries, scales, labels, and themes, then save static figures through `ggsave()` at a documented size and resolution. The chart-selection policy mirrors the Streamlit application: histograms and boxplots for a numeric variable, count/proportion bars for a categorical variable, grouped boxplots for a numeric outcome by category, and count/proportion tables or heatmaps for two categorical variables. A boxplot must never be used for a categorical variable alone; it requires a numeric response grouped by a categorical variable.

Generated figures should be returned through the integration contract as paths plus structured metadata stating the dataset, selected variables, missing-data rule, chart type, and rendering settings. See the [project visualization standard](../../../docs/visualization_standard.md) for the shared R/Python policy and examples.

## Dependency management

The production image should pin the R version and packages through `renv.lock` or an equivalent reproducible environment definition. Do not install packages during an app request. The primary deployment should use a container that explicitly installs R alongside the pinned Python dependencies.

## Validation

Dual implementations must be checked against fixed teaching datasets. Validation should compare sample treatment, reference coding, estimates, standard errors, confidence intervals, p-values within an appropriate numerical tolerance, warnings, and metadata. Where defaults differ, the app should document the difference rather than represent the outputs as automatically interchangeable.
