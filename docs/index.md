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

The seminar spans three days. Each day combines conceptual material with interactive demonstrations and applied exercises.

### Day 1: Understanding Statistical Inference through Interactive Exploration

Participants examine data-generating processes, random variation, sampling distributions, confidence intervals, bootstrap intuition, and Monte Carlo demonstrations. The focus is on how uncertainty arises and how inferential summaries communicate it.

### Day 2: Classical and Modern Methods in a No-Code Environment

Participants use guided interfaces for t-tests, chi-square tests, ANOVA, nonparametric methods, linear regression, logistic regression, diagnostics, effect sizes, and sensitivity analysis. The focus is on method selection, assumptions, and interpretation rather than formula memorisation.

### Day 3: Reproducible Research Apps and BYOD Workshop

Participants explore repository structure, app provenance, transparent analysis reporting, and AI-assisted extension of analytical tools. In the BYOD workshop, participants apply the seminar workflow to their own data under guided supervision.

## Interactive Companion App

This project includes a Streamlit companion application that supports interactive statistical exploration and guided data analysis.

**[Launch the Interactive App](https://no-code-statistical-inference.streamlit.app)** *(Deployment link will be activated when the app is published.)*

The application is organised around three modes:

1. **Inference Explorer:** Visual demonstrations of sampling variation, confidence intervals, bootstrap procedures, and simulation-based reasoning.
2. **Analysis Studio:** Guided forms for common statistical procedures, with data validation, assumption prompts, tables, graphics, and interpretation notes.
3. **Bring Your Own Data:** A session-based upload environment for analysing a participant's own tabular data. The final deployment will document data-retention and privacy behaviour explicitly.

### R and Python support

The browser interface is built in Python with Streamlit. The underlying analysis architecture supports both Python and R methods through a common request-and-result contract. This allows R-oriented academics to examine or reuse R implementations while participants retain one consistent, no-code user experience.

## Resources

The repository will include the following seminar resources as they are prepared:

| Resource | Location |
|---|---|
| Companion application | [`app/`](../app) |
| Method notes and reproducibility guidance | [`docs/`](.) |
| Position paper | [`paper/`](../paper) |
| Instructor scripts and examples | [`scripts/`](../scripts) |
| Session slides | [`slides/`](../slides) |

---

*Seminar developed by Moses Boudourides, Northwestern University.*
