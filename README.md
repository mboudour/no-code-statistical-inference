# No-Code Statistical Inference

**instats Seminar — Dates to be announced**

**Instructor:** Moses Boudourides, Data Science Graduate Program, School of Professional Studies, Northwestern University

---

## Overview

This repository contains the materials for the *No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence* seminar. It brings together concise statistical theory, interactive browser-based analysis, reproducible workflows, and guided Bring Your Own Data (BYOD) activities.

The project is designed around a simple principle: **participants should be able to investigate statistical evidence without writing code, while the analysis remains inspectable, documented, and reproducible.** The companion application uses Streamlit as its user interface and is structured to support both Python and R analysis engines.

---

## Seminar Structure

This is a **nine-hour seminar** consisting of **three three-hour days**, with **ten modules per day**. Every day begins with a ten-minute introduction. Every 17-minute module begins with a mathematically rigorous presentation of concepts, notation, assumptions, and results—**without proofs**—before an instructor demonstration and participant activity.

| Day | General day theme | Module titles |
|---|---|---|
| Day 1 | **Foundations of data, variation, and uncertainty** | **D1M01** Observational units, variables, populations, and samples; **D1M02** Measurement scales, coding, and data quality; **D1M03** Distributional summaries: centre, spread, and shape; **D1M04** Visual evidence and exploratory data analysis; **D1M05** Random variation and repeated sampling; **D1M06** Sampling distributions and the central limit theorem; **D1M07** Standard errors and confidence intervals; **D1M08** Bootstrap confidence intervals; **D1M09** Monte Carlo simulation and numerical uncertainty; **D1M10** Assumptions, outliers, and analytical readiness |
| Day 2 | **Evidence from comparisons, tests, and categorical data** | **D2M01** Estimands, hypotheses, and null reference distributions; **D2M02** Effect sizes and practical significance; **D2M03** Independent two-group comparisons; **D2M04** Paired and repeated-measures comparisons; **D2M05** Analysis of variance and multi-group questions; **D2M06** Nonparametric and permutation approaches; **D2M07** Categorical variables and conditional probabilities; **D2M08** Contingency tables and chi-square inference; **D2M09** Stratification, confounding, and Simpson-type reversals; **D2M10** Randomization tests and sensitivity to design choices |
| Day 3 | **Conditional modelling, prediction, diagnostics, and reproducibility** | **D3M01** Simple linear regression and conditional means; **D3M02** Multiple regression and adjustment; **D3M03** Regression uncertainty and coefficient intervals; **D3M04** Nonlinearity, transformations, and model specification; **D3M05** Logistic regression, odds, and predicted probabilities; **D3M06** Binary-outcome prediction and classification thresholds; **D3M07** Calibration, discrimination, and probability communication; **D3M08** Diagnostics, influence, and sensitivity analysis; **D3M09** Training, testing, and out-of-sample validation; **D3M10** Reproducible no-code workflows and transparent reporting |

Every module has **three separate data pathways**. The instructor demonstrates one selected public dataset; participants choose from **three different public BYOD datasets** that are not the demonstrated dataset; and participants may upload their own CSV dataset for that same module. The curated public files are stored in the repository, so the app uses no API keys or live data connection. See the [detailed nine-hour design](./docs/seminar_design.md) and [dataset library](./data/README.md).

---

## Interactive Companion App

The Streamlit companion app follows a **day-first, theory-led sequence**:

1. **Select a day:** Participants choose **Day 1**, **Day 2**, or **Day 3**.
2. **Day theory:** The chosen day opens with its general theoretical introduction and a ten-module map identifying the selected worked-out public dataset for each module.
3. **Select a module:** Participants enter one of the ten modules belonging to the selected day.
4. **Module theory:** Each module presents its definitions, notation, assumptions, and results before any analysis interaction.
5. **Worked-out public dataset:** The instructor-selected dataset is processed in a no-code profile and analysis workbench. An optional selector makes every bundled public dataset processable through the same workbench.
6. **BYOD upload:** Participants upload a CSV dataset within the selected module. The file remains in memory for the session and is processed through the same generic workbench.

The interface is intentionally no-code. It never executes user-supplied code, and it keeps participant-uploaded CSV files in memory only.

### Bilingual analysis architecture

Streamlit is the Python interface. The application is organised so that conventional statistical procedures can run through either a Python or an R back end using a shared result contract. The first implementation will prioritise parity for descriptives, independent-samples comparisons, chi-square tests, ANOVA, and linear regression. Interactive teaching simulations may use a single engine when a duplicate implementation provides no pedagogical benefit.

### Running locally

```bash
cd app
python -m pip install -r requirements.txt
streamlit run app.py
```

R-backed procedures require a local R installation and the packages documented in `app/engines/r/README.md`. The starter application currently demonstrates the Python teaching engine; the R directory defines the parallel integration boundary for subsequent methods.

---

## Repository Layout

| Folder | Contents |
|---|---|
| [`app/`](./app) | Module-driven Streamlit companion app, Python analysis workflows, and R-engine boundary |
| [`data/`](./data) | Machine-readable curriculum manifest and curated public no-key datasets |
| [`docs/`](./docs) | Public seminar site, detailed day/module design, and reproducibility documentation |
| [`paper/`](./paper) | Position paper and related scholarly materials |
| [`scripts/`](./scripts) | Reusable instructor demonstrations and validation utilities |
| [`slides/`](./slides) | Seminar slide decks organised by module |

---

## Reproducibility and Responsible Use

The project treats statistical conclusions as conditional on the data, model, assumptions, and analytical choices. Each implemented procedure should therefore identify its sample treatment, parameterisation, inferential settings, warnings, and software provenance. Results generated in the app are learning aids and should be interpreted in relation to the research design and subject-matter context.

---

## License

© 2026 Moses Boudourides · Northwestern University

Materials in this repository are made available for educational use. Please cite appropriately if you use or adapt them.
