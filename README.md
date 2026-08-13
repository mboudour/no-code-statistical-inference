# No-Code Statistical Inference

**instats Seminar — Dates to be announced**

**Instructor:** Moses Boudourides, Data Science Graduate Program, School of Professional Studies, Northwestern University

---

## Overview

This repository contains the materials for the *No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence* seminar. It brings together concise statistical theory, interactive browser-based analysis, reproducible workflows, and guided Bring Your Own Data (BYOD) activities.

The project is designed around a simple principle: **participants should be able to investigate statistical evidence without writing code, while the analysis remains inspectable, documented, and reproducible.** The companion application uses Streamlit as its user interface and is structured to support both Python and R analysis engines.

---

## Seminar Structure

| Day | Theme | Practical focus |
|---|---|---|
| 1 | Understanding statistical inference through interactive exploration | Data-generating processes, sampling, uncertainty, confidence intervals, bootstrap, and Monte Carlo demonstrations |
| 2 | Classical and modern methods in a no-code environment | Hypothesis tests, regression, model diagnostics, effect sizes, sensitivity analysis, and interpretation |
| 3 | Reproducible research apps and BYOD workshop | GitHub workflows, analysis provenance, interactive dashboards, AI-assisted development, and participants' own data |

---

## Interactive Companion App

The Streamlit companion app will provide three connected experiences:

1. **Inference Explorer:** Interactive simulations that make sampling variation, confidence intervals, and resampling visible.
2. **Analysis Studio:** Guided interfaces for descriptives, comparisons, regression, diagnostics, and interpretation.
3. **BYOD Workshop:** A privacy-conscious upload workflow for applying seminar methods to a participant's own tabular data during the workshop.

The interface is intentionally no-code. Its **Reproducibility** panel will nevertheless expose the method, assumptions, data treatment, computational engine, and downloadable analysis artefacts where appropriate.

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
| [`app/`](./app) | Streamlit companion app, Python modules, and R-engine boundary |
| [`docs/`](./docs) | Public seminar site and method/reproducibility documentation |
| [`paper/`](./paper) | Position paper and related scholarly materials |
| [`scripts/`](./scripts) | Reusable instructor demonstrations and validation utilities |
| [`slides/`](./slides) | Seminar slide decks organised by session |

---

## Reproducibility and Responsible Use

The project treats statistical conclusions as conditional on the data, model, assumptions, and analytical choices. Each implemented procedure should therefore identify its sample treatment, parameterisation, inferential settings, warnings, and software provenance. Results generated in the app are learning aids and should be interpreted in relation to the research design and subject-matter context.

---

## License

© 2026 Moses Boudourides · Northwestern University

Materials in this repository are made available for educational use. Please cite appropriately if you use or adapt them.
