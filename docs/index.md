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

| Day | Modules | Focus |
|---|---:|---|
| Day 1 | 10 | Data, measurement, distributions, sampling variation, interval estimation, bootstrap, simulation, and analytical readiness |
| Day 2 | 10 | Estimands, hypotheses, effect sizes, group comparisons, ANOVA, nonparametrics, categorical inference, stratification, and design sensitivity |
| Day 3 | 10 | Linear and logistic regression, prediction, diagnostics, validation, reproducibility, and transparent reporting |

Each module has three **distinct** data pathways: one instructor-demonstrated public dataset; three different public BYOD datasets; and the option for participants to upload their own CSV for the same module workflow. The demonstrated dataset is never offered as a BYOD option in that module. All public data are vendored locally, so no API key or runtime network connection is required. See the full [nine-hour seminar design](./seminar_design.md) and [dataset documentation](../data/README.md).

## Interactive Companion App

This project includes a Streamlit companion application that supports interactive statistical exploration and guided data analysis.

**[Launch the Interactive App](https://no-code-statistical-inference.streamlit.app)** *(Deployment link will be activated when the app is published.)*

The app provides a presentation-first workflow for each module:

1. **Curriculum and Rigorous Presentation:** Formal concepts, notation, assumptions, and results are displayed before analysis interaction.
2. **Instructor Demonstration:** The public dataset selected for the module demonstration is clearly labelled.
3. **Module BYOD:** Participants select one of three **different** public datasets assigned to that module, or upload their own CSV file.
4. **Analysis Studio:** No-code workflows support descriptive summaries, bootstrap intervals, two-group comparisons, contingency tables, simple linear regression, and a starter logistic-regression workflow.
5. **Reproducibility:** Dataset provenance, analytical choices, and interpretation limits are made explicit.

### R and Python support

The browser interface is built in Python with Streamlit. The underlying analysis architecture supports both Python and R methods through a common request-and-result contract. This allows R-oriented academics to examine or reuse R implementations while participants retain one consistent, no-code user experience.

## Resources

The repository will include the following seminar resources as they are prepared:

| Resource | Location |
|---|---|
| Companion application | [`app/`](../app) |
| Module curriculum and statistical presentations | [`seminar_design.md`](./seminar_design.md) |
| Curated public no-key datasets | [`data/`](../data) |
| Position paper | [`paper/`](../paper) |
| Instructor scripts and examples | [`scripts/`](../scripts) |
| Module slide decks | [`slides/`](../slides) |

---

*Seminar developed by Moses Boudourides, Northwestern University.*
