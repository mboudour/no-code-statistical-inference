# Guided Inference Workflow and Result Contract

## Scope

The companion app is a teaching environment for **guarded no-code statistical inference**. It supports a limited set of transparently specified analysis families and makes the related assumptions, diagnostic evidence, and interpretation limits visible. It is not a substitute for study-design expertise, subject-matter knowledge, or independent statistical review.

> **Core rule:** A calculated result is conditional on the selected data, target population, study design, variable coding, missing-data treatment, model, assumptions, and analytical choices.

## Learn, Practice, and Audit

| Mode | Participant action | App response |
|---|---|---|
| **Learn** | Open a day and module. | Theory, notation, results, worked public data, and a module-specific question/assumption contract. |
| **Practice** | Use a bundled dataset or upload a CSV. | Dataset audit, variable selection, guarded analysis, diagnostics, interactive graphics, and a standardized result record. |
| **Audit** | Critique a result. | Prompts about population, unit of observation, variable coding, assumptions, uncertainty, effect size, limitations, and robustness checks. |

## Question-first pathway

The **Guided Inference** page begins with the intended analytical purpose, outcome structure, explanatory/comparison structure, dependence/design, and inferential aim. It recommends relevant seminar modules and displays incompatibility warnings. It does not infer causal identification, valid pairing, independence, or a target population from a CSV file.

## Dataset audit contract

Every public dataset and CSV upload receives a common audit card before analysis. The audit reports local rows and columns, inferred variable types, missingness, duplicate rows, constant variables, source/use information, known limitations, and associated seminar modules. Participants must still document the unit of observation, original variable definitions, sampling process, measurement process, and target population.

## Supported analysis families

| Analysis family | Estimate and uncertainty | Diagnostics / safeguards | Important limitation |
|---|---|---|---|
| Mean estimation | Sample mean and t confidence interval | Distributional shape and IQR outlier count | Does not establish representativeness or a target population. |
| Independent groups | Mean difference, Welch interval, Cohen’s *d* | Group sizes, groupwise shape, outliers, variance evidence, planning-context power display | Does not establish causal effect or independence. |
| Paired measurements | Mean within-pair difference and interval | Difference distribution and outlying differences | Pair identity must be scientifically documented. |
| One-way comparison | Group means, omnibus F test, eta-squared | Group sizes, groupwise shape, outliers, variance evidence | Does not identify which groups differ; post-hoc choices require an explicit plan. |
| Categorical association | Contingency table, chi-square evidence, Cramér’s *V* | Expected-count warnings and Fisher exact result for 2×2 tables | Association is not causal direction or practical importance. |
| Linear regression | Coefficients, intervals, R² | Residual shape, heteroskedasticity evidence, Cook’s distance, VIF | Coefficients are conditional model associations, not automatic causal effects. |
| Logistic regression | Odds ratios, intervals, fitted-probability range | Outcome counts and probability-range checks | Odds ratios are not risk ratios; calibration and thresholds need further assessment. |

## Standard result record

Every implemented analysis follows the same result structure:

1. **Question**
2. **Data and design**
3. **Method**
4. **Assumptions**
5. **Diagnostics**
6. **Estimate**
7. **Uncertainty**
8. **Effect size**
9. **Test statistic and p-value**, where relevant
10. **Interpretation**
11. **Limitations**
12. **Next step**

The American Statistical Association states that p-values can indicate incompatibility between data and a specified model, but do not measure the probability that a hypothesis is true, effect size, or result importance; scientific conclusions should not be based solely on a threshold crossing.[1] The application therefore treats a p-value as one model-based item in a larger reporting record.

## Reproducibility record

After an analysis, participants may download a Markdown record containing the dataset audit, selected variables, research-question and design details retained in session, method, assumptions, diagnostics, numerical results, interpretation, limitations, and software context. The file is intentionally a compact record, not a claim of complete analytical reproducibility: users must also preserve the original data, source documentation, and any design decisions outside the app.

## Quality assurance

The repository contains deterministic calculation tests, public-dataset processing checks, curriculum and visualization validation, Streamlit `AppTest` page checks, and a GitHub Actions workflow. Streamlit’s official testing framework supports simulated app runs, widget manipulation, and inspection of rendered outputs in `pytest` suites.[2]

## References

[1] [American Statistical Association, *Statement on Statistical Significance and P-Values*](https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf)

[2] [Streamlit, *Get started with app testing*](https://docs.streamlit.io/develop/concepts/app-testing/get-started)
