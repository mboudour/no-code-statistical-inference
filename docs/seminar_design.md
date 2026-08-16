---
layout: default
title: Seminar Design
---

# Seminar Design: Days, Modules, Presentations, and Datasets

The seminar uses the following terminology consistently: it consists of **three days**, and each day consists of **three modules**. A day is the principal instructional unit; a module is a self-contained conceptual and applied unit within that day.

> **Instructional rule.** Every day begins with an introduction. Every module begins with a presentation that states the relevant technical and statistical concepts, notation, assumptions, and results with mathematical rigor, but does not present proofs. Only then does the module move to a worked example and a participant-led BYOD activity.

This sequence ensures that the application supports statistical reasoning rather than becoming an uncontextualized button-clicking exercise.

## Standard module sequence

| Stage | Purpose | Required output |
|---|---|---|
| Day introduction | Relate the day's modules and identify the inferential questions they address | A conceptual map and explicit learning objectives |
| Module presentation | State definitions, notation, assumptions, and results without proofs | A concise presentation of the formal statistical framework |
| Worked example | Apply the framework to one selected public dataset | Transparent analysis, interpretation, and cautionary notes |
| BYOD activity | Let participants choose from 3–5 public datasets or upload a suitable table | A guided no-code analysis and reproducibility record |
| Reflection | Compare claims, uncertainty, assumptions, and design limits | A written interpretation that distinguishes results from conclusions |

## Day 1 — Foundations of inference: data, variation, and uncertainty

Day 1 establishes the language required for all subsequent analytical work. The focus is the distinction between observed data, a stochastic data-generating process, estimands, estimators, sampling variation, and uncertainty statements.

| Module | Rigorous presentation | Worked public dataset | Public BYOD choices |
|---|---|---|---|
| 1.1 Data-generating processes, populations, samples, and estimands | Random variables; population distribution \(F\); parameter \(\mu = E_F[X]\); estimator \(\bar X\); expectation and sampling variance | Iris | Motor Trend Car Road Tests; New York Air Quality; US Arrest Rates; Old Faithful Eruptions |
| 1.2 Sampling distributions, the CLT, and confidence intervals | Sampling distributions; standard error; \(\sqrt{n}(\bar X-\mu)/\sigma \overset{d}{\to}N(0,1)\); interval coverage | New York Air Quality | Earthquake Locations and Magnitudes; Black Cherry Trees; Heights and Weights; Speed and Stopping Distances |
| 1.3 Bootstrap and Monte Carlo reasoning | Empirical distribution \(\hat F_n\); bootstrap replicates; Monte Carlo error; percentile intervals | Motorcycle Accident Simulation Data | Tooth Growth; Insect Sprays; Birth Weight; Boston Housing |

## Day 2 — Statistical tests and regression as inferential models

Day 2 introduces conventional inferential procedures as model-based comparisons. The emphasis is on estimands, null reference distributions, effect sizes, interval estimates, and the assumptions that connect the method to the research question.

| Module | Rigorous presentation | Worked public dataset | Public BYOD choices |
|---|---|---|---|
| 2.1 Two-group and multi-group comparisons | \(H_0: \mu_1-\mu_2=0\); Welch t statistic; ANOVA; standardised mean difference; interval estimation | Tooth Growth | Plant Growth; Warp Breaks; Insect Sprays; Chick Weight |
| 2.2 Categorical data, association, and contingency tables | Joint and conditional distributions; \(E_{ij}\); \(X^2=\sum(O_{ij}-E_{ij})^2/E_{ij}\); expected-count conditions | Arthritis Treatment Data | Titanic Passenger Survival; UC Berkeley Admissions; Credit Card Default; Health Insurance |
| 2.3 Linear regression as conditional inference | \(Y=\beta_0+\beta_1X_1+\cdots+\beta_pX_p+\varepsilon\); least squares; residuals; coefficient intervals; diagnostics | Automobile Data | Carseats; College; Credit; California Schools |

## Day 3 — Prediction, diagnostics, sensitivity, and reproducible research apps

Day 3 distinguishes explanatory and predictive goals, makes diagnostic and validation choices explicit, and situates the no-code application in a reproducible research workflow. The BYOD activities combine statistical inference with documented provenance.

| Module | Rigorous presentation | Worked public dataset | Public BYOD choices |
|---|---|---|---|
| 3.1 Binary outcomes and logistic regression | \(\operatorname{logit}[P(Y=1\mid X=x)] = \beta_0+x^T\beta\); odds, odds ratios, predicted probabilities, thresholds | Credit Card Default | Pima Indians Diabetes Training Data; Birth Weight; Health Insurance; Smoke Ban |
| 3.2 Diagnostics, model comparison, and sensitivity analysis | Residual \(e_i=y_i-\hat y_i\); leverage; influence; specification checks; out-of-sample error; analytical sensitivity | Carseats | Automobile Data; College; Credit; House Prices |
| 3.3 Reproducible analysis, resampling validation, and the BYOD workflow | Train-test logic; \(\operatorname{MSPE}=m^{-1}\sum(y_i-\hat y_i)^2\); provenance; seeds; versioning; reproducibility contracts | Pima Indians Diabetes Training Data | Pima Indians Diabetes Test Data; Doctor Visits; Boston Housing; House Prices |

## Dataset framework

Each module has one worked dataset and **four** public BYOD choices, satisfying the requirement of 3–5 datasets per module. The datasets are stored in `data/public/` so the app does not need an API key or a runtime network request. `data/module_manifest.json` is the machine-readable curriculum and dataset catalog.

The data library is based on the public Rdatasets archive, which consolidates datasets distributed with R packages and provides source documentation.[1] Classroom use must still distinguish pedagogical convenience from research validity: the original data documentation, sampling process, variable definitions, licensing conditions, and limitations remain essential.

## App use and mathematical rigor

The Streamlit app mirrors this design. Its **Curriculum and Rigorous Presentation** page presents the active module's formal concepts and results. Its **Dataset Explorer** introduces the worked example or a module-linked BYOD dataset. Its **Analysis Studio** supports descriptive summaries, bootstrap intervals, group comparisons, contingency-table analysis, simple linear regression, and a starter logistic-regression workflow. The app visibly records the active data source and never treats a computed output as an automatic substantive conclusion.

## References

[1] [Vincent Arel-Bundock, *Rdatasets*: a collection of datasets originally distributed with R and its add-on packages](https://github.com/vincentarelbundock/Rdatasets)
