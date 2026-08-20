# No-Code Statistical Inference

**instats Seminar — September 28, 29, and 30, 2026**

**Instructor:** Moses Boudourides, Data Science Graduate Program, School of Professional Studies, Northwestern University

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://no-code-statistical-inference.streamlit.app/) [Open the Streamlit App](https://no-code-statistical-inference.streamlit.app/)

---

## Overview

This repository contains the materials for the *No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence* seminar: six session slide decks, a position paper, and the source code for the interactive Streamlit companion application.

The seminar treats statistical inference as a problem of **reasoning from data to evidence**. Its objective is to help participants formulate a clear estimand, examine the design and data-generating conditions that support an analysis, quantify uncertainty, interpret effect sizes and model-based evidence, and state limitations proportionately. Participants do not need to write, read, or navigate R or Python code; the emphasis is on statistical reasoning rather than software operation.

---

## Seminar Schedule

| Day | Date | Session | Title | Time |
|---|---|---:|---|---|
| 1 | September 28 | 1.1 | Data, Measurement, and Exploratory Analysis | 3:00–4:30 PM UTC |
| 1 | September 28 | 1.2 | Sampling, Estimation, and Uncertainty | 4:30–6:00 PM UTC |
| 2 | September 29 | 2.1 | Comparing Groups: Estimands, Effects, and Tests | 3:00–4:30 PM UTC |
| 2 | September 29 | 2.2 | Categorical Data, Association, and Study Design | 4:30–6:00 PM UTC |
| 3 | September 30 | 3.1 | Regression, Adjustment, and Conditional Inference | 3:00–4:30 PM UTC |
| 3 | September 30 | 3.2 | Prediction, Model Checking, and Reproducibility | 4:30–6:00 PM UTC |

---

## Interactive Companion App

The **[Streamlit application](https://no-code-statistical-inference.streamlit.app/)** is a guarded teaching and analysis environment, not an unrestricted statistical decision engine. It provides:

1. **Theory-led day pages** — Day 1, Day 2, and Day 3 begin with their conceptual framework and lead to ten structured modules each.
2. **Worked examples** — Each module introduces a selected public dataset, statistical definitions, assumptions, a worked procedure, visualizations, interpretation, and limitations.
3. **Bring Your Own Data (BYOD)** — Participants can upload CSV or Excel datasets, or enter a small practice table manually, then inspect the data and use supported analysis pathways.
4. **Guided Inference** — The interface begins with the research question, outcome structure, explanatory structure, design, dependence, and inferential aim. It identifies pathways as **Compatible**, **Caution**, or **Not compatible**, with an explanation rather than an automatic test choice.
5. **Dataset Laboratory and reporting** — Dataset audit cards document variable structure, missingness, duplicates, and limitations. For supported analyses, a reproducibility record can be downloaded.

The application does not execute participant-supplied code, and uploaded files remain in memory for the session. Its implemented teaching workflows cover mean estimation, Welch independent-group comparison, paired comparison, one-way ANOVA, categorical association, linear regression, and logistic regression. Each workflow presents the question, data and design, method, assumptions, diagnostics, estimate, uncertainty, effect size where relevant, model-based evidence where relevant, interpretation, limitations, and next step.

**Running locally:**

```bash
cd app
python -m pip install -r requirements.txt
streamlit run app.py
```

---

## Six Session Themes

1. **Data and measurement** — observational units, populations, variables, scales, data quality, descriptive statistics, graphics, and missingness.
2. **Sampling and uncertainty** — sampling distributions, standard errors, confidence intervals, simulation, bootstrap methods, and assumptions.
3. **Comparisons and evidence** — estimands, hypotheses, effect sizes, Welch inference, paired designs, ANOVA, and power.
4. **Categorical inference and design** — conditional probabilities, contingency tables, odds ratios, Fisher’s exact test, confounding, stratification, and randomization.
5. **Regression and adjustment** — conditional means, model specification, coefficient interpretation, uncertainty, logistic regression, and separation.
6. **Prediction and reproducibility** — calibration, discrimination, diagnostics, influence, validation, missing-data choices, and transparent reporting.

---

## Position Paper

The seminar’s position paper is available here: [*No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence*](./position_paper/no_code_statistical_inference_position_paper.pdf).

---

## Seminar Materials and Repository Layout

| Folder | Contents |
|---|---|
| [`app/`](./app) | Streamlit companion app, guided analysis workflows, and R-engine boundary |
| [`data/`](./data) | Curriculum manifest and curated public no-key datasets |
| [`docs/`](./docs) | Seminar information, inference workflow, visualization standard, and dataset documentation |
| [`position_paper/`](./position_paper) | Academic position paper |
| [`scripts/`](./scripts) | Curriculum, dataset, and application validation utilities |
| [`slides/`](./slides) | Seminar slide materials |
| [`tests/`](./tests) | Deterministic calculation, guardrail, known-result, and Streamlit application tests |

---

## Reproducibility and Responsible Use

Statistical conclusions are conditional on the data, model, assumptions, and analytical choices. The repository includes deterministic calculation tests, public-dataset processing checks, visualization smoke tests, and Streamlit `AppTest` checks. GitHub Actions runs these checks on pushes and pull requests. Install development dependencies with `python -m pip install -r requirements-dev.txt`, then run `pytest tests/` from the repository root.

---

## License

© 2026 Moses Boudourides · Northwestern University
Materials in this repository are made available for educational use. Please cite appropriately if you use or adapt them.
