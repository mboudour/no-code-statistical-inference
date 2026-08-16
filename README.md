# No-Code Statistical Inference

**instats Seminar — Dates to be announced**

**Instructor:** Moses Boudourides, Data Science Graduate Program, School of Professional Studies, Northwestern University

---

## Overview

This repository contains the materials for the *No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence* seminar. It brings together concise statistical theory, interactive browser-based analysis, reproducible workflows, and guided Bring Your Own Data (BYOD) activities.

The project is designed around a simple principle: **participants should be able to investigate statistical evidence without writing code, while the analysis remains inspectable, documented, and reproducible.** The companion application uses Streamlit as its user interface and is structured to support both Python and R analysis engines.

---

## Seminar Structure

The seminar consists of **three days**, with **three modules per day**. Every day begins with an introduction. Every module begins with a mathematically rigorous presentation of concepts, notation, assumptions, and results—**without proofs**—before participants see a worked analysis or begin a BYOD activity.

| Day | Modules | Core theme |
|---|---:|---|
| 1 | 3 | Data-generating processes, estimators, sampling distributions, confidence intervals, bootstrap, and Monte Carlo reasoning |
| 2 | 3 | Group comparisons, categorical association, and regression as conditional inference |
| 3 | 3 | Logistic regression, diagnostics and sensitivity, validation, provenance, and reproducible BYOD workflows |

Every module has **one worked public dataset** and **four public datasets** for participant-led BYOD work. The curated files are stored in the repository, so the app uses no API keys or live data connection. See the [detailed seminar design](./docs/seminar_design.md) and [dataset library](./data/README.md).

---

## Interactive Companion App

The Streamlit companion app follows the same presentation-first sequence as the seminar:

1. **Curriculum and Rigorous Presentation:** The active day and module show definitions, formal notation, assumptions, and results before any analysis interaction.
2. **Dataset Explorer:** Participants inspect the module's worked dataset or choose one of its four locally bundled, public BYOD datasets.
3. **Analysis Studio:** Guided interfaces support descriptive summaries, bootstrap intervals, two-group comparisons, contingency tables, simple linear regression, and a starter logistic-regression workflow.
4. **Reproducibility:** The interface identifies data provenance, analytical settings, assumptions, and interpretation limits.

The interface is intentionally no-code. It never executes user-supplied code and reads uploaded CSV files in memory for the session.

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
