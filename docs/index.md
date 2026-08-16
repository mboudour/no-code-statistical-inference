---
layout: default
title: No-Code Statistical Inference
---

# No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence

**instats Seminar — Dates to be announced**  
**Instructor:** Moses Boudourides, Data Science Graduate Program, School of Professional Studies, Northwestern University

Welcome to the project site for the **No-Code Statistical Inference** seminar. This three-day intensive seminar introduces an interactive approach to statistical practice in which participants investigate data, uncertainty, and evidence through browser-based analytical applications rather than conventional coding workflows.

The seminar is grounded in a simple premise: statistical inference should be understandable, inspectable, and reproducible. The no-code interface lowers the operational barrier, while the repository documents the assumptions, analytical decisions, computational engine, and reproducibility artefacts behind each result.

## Seminar Structure

The seminar spans **three three-hour days** for a total of **nine hours**. Each day begins with a ten-minute introduction and is composed of **ten 17-minute modules**. Every module begins with a formal presentation of the relevant concepts, notation, assumptions, and statistical results. These presentations are mathematically rigorous but do not include proofs.

| Day | General day theme | Module titles |
|---|---|---|
| Day 1 | **Foundations of data, variation, and uncertainty** | **D1M01** Observational units, variables, populations, and samples; **D1M02** Measurement scales, coding, and data quality; **D1M03** Distributional summaries: centre, spread, and shape; **D1M04** Visual evidence and exploratory data analysis; **D1M05** Random variation and repeated sampling; **D1M06** Sampling distributions and the central limit theorem; **D1M07** Standard errors and confidence intervals; **D1M08** Bootstrap confidence intervals; **D1M09** Monte Carlo simulation and numerical uncertainty; **D1M10** Assumptions, outliers, and analytical readiness |
| Day 2 | **Evidence from comparisons, tests, and categorical data** | **D2M01** Estimands, hypotheses, and null reference distributions; **D2M02** Effect sizes and practical significance; **D2M03** Independent two-group comparisons; **D2M04** Paired and repeated-measures comparisons; **D2M05** Analysis of variance and multi-group questions; **D2M06** Nonparametric and permutation approaches; **D2M07** Categorical variables and conditional probabilities; **D2M08** Contingency tables and chi-square inference; **D2M09** Stratification, confounding, and Simpson-type reversals; **D2M10** Randomization tests and sensitivity to design choices |
| Day 3 | **Conditional modelling, prediction, diagnostics, and reproducibility** | **D3M01** Simple linear regression and conditional means; **D3M02** Multiple regression and adjustment; **D3M03** Regression uncertainty and coefficient intervals; **D3M04** Nonlinearity, transformations, and model specification; **D3M05** Logistic regression, odds, and predicted probabilities; **D3M06** Binary-outcome prediction and classification thresholds; **D3M07** Calibration, discrimination, and probability communication; **D3M08** Diagnostics, influence, and sensitivity analysis; **D3M09** Training, testing, and out-of-sample validation; **D3M10** Reproducible no-code workflows and transparent reporting |

Each module has three **distinct** data pathways: one instructor-demonstrated public dataset; three different public BYOD datasets; and the option for participants to upload their own CSV for the same module workflow. The demonstrated dataset is never offered as a BYOD option in that module. All public data are vendored locally, so no API key or runtime network connection is required. See the full [nine-hour seminar design](./seminar_design.md) and [dataset documentation](../data/README.md).

## Interactive Companion App

This project includes a Streamlit companion application that supports interactive statistical exploration and guided data analysis.

**[Launch the Interactive App](https://no-code-statistical-inference.streamlit.app)** *(Deployment link will be activated when the app is published.)*

The app provides a **day-first, theory-led workflow** and three shared safeguards around the curriculum:

1. **Three direct day pages:** Participants open Day 1, Day 2, or Day 3 from the sidebar. Each page begins with theory and then provides ten module panels.
2. **Question and module contract:** Every module presents its research-question prompt, variable requirements, assumption focus, diagnostics, interpretation template, and pre-analysis audit prompt before an analysis interaction.
3. **Guided Inference:** A question-first page records outcome structure, comparison/predictor structure, dependence/design, and inferential aim before recommending compatible seminar modules and warning about incompatible choices.
4. **Dataset Laboratory:** Every bundled public CSV and participant upload receives a dataset-audit card, including inferred types, missingness, duplicates, constant variables, source/use guidance, known limitations, and suitable modules.
5. **Guarded analysis:** Supported analysis families use a standard result sequence: question; data and design; method; assumptions; diagnostics; estimate; uncertainty; effect size; test evidence where relevant; interpretation; limitations; and next step.
6. **Reproducibility and audit:** Participants can download a Markdown record of the selections and result, then use a dedicated Audit mode and day-synthesis page to critique the scope of an inferential claim. CSV and Excel uploads remain in memory only for the session, and the laboratory supports manual entry of small practice tables.

### R and Python support

The browser interface is built in Python with Streamlit. The underlying analysis architecture supports both Python and R methods through a common request-and-result contract. This allows R-oriented academics to examine or reuse R implementations while participants retain one consistent, no-code user experience.

## Resources

The repository will include the following seminar resources as they are prepared:

| Resource | Location |
|---|---|
| Companion application | [`app/`](../app) |
| Module curriculum and statistical presentations | [`seminar_design.md`](./seminar_design.md) |
| Curated public no-key datasets and metadata cards | [`data/`](../data) |
| Guided workflow and result contract | [`inference_workflow.md`](./inference_workflow.md) |
| Position paper | [`paper/`](../paper) |
| Instructor scripts and examples | [`scripts/`](../scripts) |
| Module slide decks | [`slides/`](../slides) |

---

*Seminar developed by Moses Boudourides, Northwestern University.*
