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

The seminar spans **three days**, each composed of **three modules**. Every day begins with an introduction, and every module begins with a formal presentation of the relevant concepts, notation, assumptions, and statistical results. These presentations are mathematically rigorous but do not include proofs.

| Day | Modules | Focus |
|---|---:|---|
| Day 1 | 3 | Data-generating processes, estimators, sampling distributions, confidence intervals, bootstrap, and Monte Carlo reasoning |
| Day 2 | 3 | Group comparisons, categorical association, and linear regression as conditional inference |
| Day 3 | 3 | Logistic regression, diagnostics and sensitivity, validation, provenance, and reproducible BYOD workflows |

Each module uses one public dataset as a worked example and provides four public datasets for participant-led BYOD activity. The data are vendored locally with the project, so no API key or runtime network connection is required. See the full [day-and-module design](./seminar_design.md) and [dataset documentation](../data/README.md).

## Interactive Companion App

This project includes a Streamlit companion application that supports interactive statistical exploration and guided data analysis.

**[Launch the Interactive App](https://no-code-statistical-inference.streamlit.app)** *(Deployment link will be activated when the app is published.)*

The app provides a presentation-first workflow for each module:

1. **Curriculum and Rigorous Presentation:** Formal concepts, notation, assumptions, and results are displayed before analysis interaction.
2. **Dataset Explorer:** Participants inspect the module worked example or select one of its public BYOD datasets.
3. **Analysis Studio:** No-code workflows support descriptive summaries, bootstrap intervals, two-group comparisons, contingency tables, simple linear regression, and a starter logistic-regression workflow.
4. **Reproducibility:** Dataset provenance, analytical choices, and interpretation limits are made explicit.

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
