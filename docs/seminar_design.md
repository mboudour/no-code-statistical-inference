---
layout: default
title: Nine-Hour Seminar Design
---

# Nine-Hour Seminar Design: Days, Modules, Demonstrations, and BYOD

This is a **nine-hour seminar** consisting of **three three-hour days**. Each day begins with a ten-minute introduction and contains **ten 17-minute modules**. Each module follows a presentation-first microstructure: six minutes for a mathematically rigorous presentation without proofs, five minutes for an instructor demonstration using one selected public dataset, and six minutes for a BYOD activity using a **different** public dataset or a participant-uploaded CSV file.

> **Three distinct data pathways are compulsory in every module.** The instructor demonstrates one public dataset. Participants then choose one of three different public BYOD datasets assigned to that module, or upload their own CSV. The demonstrated dataset is never listed as a BYOD option for the same module.

## Standard 17-minute module format

| Component | Minutes | Purpose |
|---|---:|---|
| Rigorous presentation | 6 | Definitions, notation, assumptions, and results; no proofs |
| Instructor demonstration | 5 | Transparent analysis of one selected public dataset |
| BYOD activity | 6 | A separate public dataset choice or a participant CSV upload |

## Day 1 — Data, variation, and uncertainty

Day 1 establishes the language of data, estimands, variation, sampling distributions, and uncertainty. After a ten-minute orientation, ten 17-minute modules each begin with a rigorous presentation and then move to a public-data demonstration and a distinct BYOD activity.

| Module | Formal presentation | Demonstrated dataset | Public BYOD datasets |
|---|---|---|---|
| D1M01 — Observational units, variables, populations, and samples | Define observational units, variables, populations, samples, parameters, statistics, and the distinction between a scientific target and an observed dataset. | Iris | Motor Trend Car Road Tests; US Arrest Rates; New York Air Quality |
| D1M02 — Measurement scales, coding, and data quality | Introduce nominal, ordinal, interval, and ratio scales; distinguish recorded codes from substantive constructs; and identify missingness and data-quality concerns. | New York Air Quality | College; Health Insurance; Doctor Visits |
| D1M03 — Distributional summaries: centre, spread, and shape | Define the mean, median, variance, standard deviation, interquartile range, quantiles, skewness, and the role of robust summaries. | Average Heights and Weights for American Women | Speed and Stopping Distances; Motor Trend Car Road Tests; Iris |
| D1M04 — Visual evidence and exploratory data analysis | State the purpose and limitations of histograms, boxplots, scatterplots, conditional summaries, and visual detection of unusual observations. | Earthquake Locations and Magnitudes | Old Faithful Eruptions; Black Cherry Trees; Motorcycle Accident Simulation Data |
| D1M05 — Random variation and repeated sampling | Introduce randomness, sampling variability, repeated-sampling thought experiments, and the distinction between a realised sample and its sampling distribution. | Old Faithful Eruptions | Iris; Speed and Stopping Distances; New York Air Quality |
| D1M06 — Sampling distributions and the central limit theorem | Define a sampling distribution, standard error, normal approximation, and the regularity conditions behind the central limit theorem. | Black Cherry Trees | Average Heights and Weights for American Women; Automobile Data; House Prices |
| D1M07 — Standard errors and confidence intervals | Define standard error, confidence procedures, interval width, confidence level, and long-run coverage. | Speed and Stopping Distances | Average Heights and Weights for American Women; Black Cherry Trees; Motorcycle Accident Simulation Data |
| D1M08 — Bootstrap confidence intervals | Define the empirical distribution, resampling with replacement, bootstrap replicates, bootstrap standard error, and percentile intervals. | Motorcycle Accident Simulation Data | Birth Weight; Tooth Growth; Plant Growth |
| D1M09 — Monte Carlo simulation and numerical uncertainty | Introduce simulation design, pseudo-random draws, Monte Carlo estimators, reproducible seeds, and simulation error. | Motor Trend Car Road Tests | Automobile Data; Carseats; Credit |
| D1M10 — Assumptions, outliers, and analytical readiness | Define an assumption, an outlier, leverage, influence, transformations, and the difference between data screening and post-hoc result selection. | College | New York Air Quality; House Prices; Doctor Visits |

### Module-level upload route

Participants may upload their own CSV file in **every** module. The app reads the upload in memory, asks the participant to select compatible variables, and applies the same descriptive or inferential workflow. An uploaded dataset does not make a method automatically appropriate; the participant must still evaluate the design, variables, assumptions, and target inference.

### Formal notation and results

#### D1M01 — Observational units, variables, populations, and samples

**Notation.** Let X_1, …, X_n denote observed values sampled from a population distribution F; a parameter θ is a feature of F, while a statistic T(X_1, …, X_n) is a function of the sample.

**Results to state.** A statistic and a parameter are conceptually different objects. The population of inference must be specified before a sample can support a general claim.

#### D1M02 — Measurement scales, coding, and data quality

**Notation.** A variable X can be numeric without being interval-scaled; transformations and arithmetic summaries require assumptions about the scale and coding of X.

**Results to state.** Variable coding determines which comparisons and summaries are meaningful. Missing values are part of the data-generating and measurement process, not merely a software inconvenience.

#### D1M03 — Distributional summaries: centre, spread, and shape

**Notation.** For values x_1, …, x_n, x̄ = n⁻¹Σ_i x_i and s² = (n−1)⁻¹Σ_i(x_i−x̄)²; the median minimizes the sum of absolute deviations.

**Results to state.** The mean and standard deviation are sensitive to extreme observations. Quantiles and robust summaries can communicate distributional structure that one average obscures.

#### D1M04 — Visual evidence and exploratory data analysis

**Notation.** The empirical distribution function is F̂_n(x) = n⁻¹Σ_i I(X_i ≤ x); graphical displays approximate features of F̂_n or of conditional distributions.

**Results to state.** A graphic is an estimator or display of data structure, not a proof of a model. Patterns should be checked against variable definitions, sampling mechanisms, and potential measurement artifacts.

#### D1M05 — Random variation and repeated sampling

**Notation.** If X_1, …, X_n are iid with mean μ and variance σ², then E[X̄] = μ and Var(X̄) = σ²/n.

**Results to state.** The observed sample mean is one realisation of a random estimator. Larger samples reduce the variance of the sample mean when the iid model is appropriate.

#### D1M06 — Sampling distributions and the central limit theorem

**Notation.** Under iid sampling with finite variance, √n(X̄−μ)/σ converges in distribution to N(0,1) as n grows.

**Results to state.** The central limit theorem concerns an estimator over repeated samples, not the raw-data shape alone. Normal approximations require context-specific checks rather than mechanical invocation.

#### D1M07 — Standard errors and confidence intervals

**Notation.** An approximate 1−α interval for μ is X̄ ± z_(1−α/2) SE(X̄); the procedure targets P_μ{μ ∈ C(X)} = 1−α under stated assumptions.

**Results to state.** A confidence interval is not a probability distribution over a fixed parameter in the frequentist interpretation. Interval width depends on variability, sample size, and chosen confidence level.

#### D1M08 — Bootstrap confidence intervals

**Notation.** The empirical distribution F̂_n places mass 1/n on each observation; θ̂* is the statistic recomputed on a sample drawn from F̂_n.

**Results to state.** Bootstrap methods approximate sampling variation through the empirical distribution. Resampling cannot repair selection bias, an ill-defined estimand, or data that do not represent the target population.

#### D1M09 — Monte Carlo simulation and numerical uncertainty

**Notation.** For independent simulation outputs Z_1, …, Z_B, the Monte Carlo estimator B⁻¹Σ_b Z_b has standard error proportional to B^(−1/2).

**Results to state.** A simulation estimate has its own numerical uncertainty. Seeds support reproducibility but do not validate the underlying statistical model.

#### D1M10 — Assumptions, outliers, and analytical readiness

**Notation.** For a model M, inferential validity is conditional on the data-generating conditions and assumptions encoded by M, not only on a computed p-value.

**Results to state.** Outliers should be investigated substantively and statistically rather than removed automatically. Analytical decisions made after inspecting outcomes require transparent documentation.

## Day 2 — Tests, comparisons, and categorical inference

Day 2 develops formal comparisons and categorical-data reasoning. Every module states its estimand, assumptions, and reference distribution before participants see a demonstrated analysis and work with a separate public BYOD dataset or an upload.

| Module | Formal presentation | Demonstrated dataset | Public BYOD datasets |
|---|---|---|---|
| D2M01 — Estimands, hypotheses, and null reference distributions | Define null and alternative hypotheses, test statistics, null distributions, significance level, p-values, and the relation between tests and estimands. | Tooth Growth | Plant Growth; Birth Weight; Chick Weight |
| D2M02 — Effect sizes and practical significance | Define raw differences, standardized mean differences, uncertainty intervals, practical thresholds, and the difference between statistical and substantive significance. | Plant Growth | Tooth Growth; Birth Weight; Warp Breaks |
| D2M03 — Independent two-group comparisons | Present the independent-samples mean difference, Welch's t procedure, standard-error construction, confidence intervals, and assumptions about group formation. | Birth Weight | Tooth Growth; Plant Growth; Chick Weight |
| D2M04 — Paired and repeated-measures comparisons | Define paired differences, within-unit dependence, repeated observations, longitudinal structure, and why an independent-sample analysis can be inappropriate for paired data. | Chick Weight | Tooth Growth; Plant Growth; Pima Indians Diabetes Training Data |
| D2M05 — Analysis of variance and multi-group questions | Introduce between-group and within-group variation, the one-way ANOVA model, F statistics, omnibus tests, contrasts, and multiplicity-aware follow-up questions. | Insect Sprays | Plant Growth; Warp Breaks; Chick Weight |
| D2M06 — Nonparametric and permutation approaches | Introduce rank-based tests, randomization/permutation logic, exchangeability, and when a distribution-free label is misleading. | Warp Breaks | Insect Sprays; Tooth Growth; Plant Growth |
| D2M07 — Categorical variables and conditional probabilities | Define joint, marginal, and conditional distributions; risk differences; relative risks; odds; and the role of stratification. | Arthritis Treatment Data | Health Insurance; Credit Card Default; Smoke Ban |
| D2M08 — Contingency tables and chi-square inference | Define expected counts, Pearson's chi-square statistic, independence models, reference degrees of freedom, and sparse-table cautions. | UC Berkeley Admissions | Titanic Passenger Survival; Arthritis Treatment Data; Credit Card Default |
| D2M09 — Stratification, confounding, and Simpson-type reversals | Define a confounder, stratified comparison, marginal association, conditional association, and why aggregation can alter apparent relationships. | Titanic Passenger Survival | UC Berkeley Admissions; Arthritis Treatment Data; Health Insurance |
| D2M10 — Randomization tests and sensitivity to design choices | Define a sharp null hypothesis, random assignment, randomization distributions, design-consistent testing, and sensitivity to recoding or subgroup definitions. | Smoke Ban | Arthritis Treatment Data; Credit Card Default; Health Insurance |

### Module-level upload route

Participants may upload their own CSV file in **every** module. The app reads the upload in memory, asks the participant to select compatible variables, and applies the same descriptive or inferential workflow. An uploaded dataset does not make a method automatically appropriate; the participant must still evaluate the design, variables, assumptions, and target inference.

### Formal notation and results

#### D2M01 — Estimands, hypotheses, and null reference distributions

**Notation.** For H_0: θ=θ_0 and test statistic T, the p-value is P_{H_0}(|T|≥|t_obs|) for a two-sided reference rule.

**Results to state.** A p-value is conditional on the null model and the specified test statistic. A non-significant result is not evidence that an effect is exactly zero.

#### D2M02 — Effect sizes and practical significance

**Notation.** For two groups, Cohen's d = (X̄_2−X̄_1)/s_p, where s_p is a pooled within-group standard deviation under its stated convention.

**Results to state.** Effect sizes require scale and context for interpretation. An effect can be precisely estimated yet substantively negligible, or important yet imprecisely estimated.

#### D2M03 — Independent two-group comparisons

**Notation.** T = (X̄_1−X̄_2)/√(s_1²/n_1+s_2²/n_2), with a Welch–Satterthwaite reference degrees-of-freedom approximation.

**Results to state.** Welch's procedure does not assume equal population variances. Causal language requires an appropriate design, not only a two-group test.

#### D2M04 — Paired and repeated-measures comparisons

**Notation.** For paired values (X_i,Y_i), analyse D_i=Y_i−X_i; the paired t statistic is T=D̄/(s_D/√n).

**Results to state.** Pairing can reduce variance when within-unit correlation is used correctly. Repeated measurements require clarity about the observational unit and the dependence structure.

#### D2M05 — Analysis of variance and multi-group questions

**Notation.** In Y_ij=μ+α_j+ε_ij, the F statistic compares mean-square variation between groups with mean-square variation within groups.

**Results to state.** An omnibus ANOVA test does not identify which group differences are present. Planned contrasts and post-hoc comparisons should be distinguished and documented.

#### D2M06 — Nonparametric and permutation approaches

**Notation.** Under exchangeability under H_0, a permutation distribution is formed by recomputing T over relabelings consistent with the null hypothesis.

**Results to state.** Permutation validity depends on an exchangeability condition tied to the design. Rank-based procedures answer questions about distributions or stochastic ordering that need not equal a mean comparison.

#### D2M07 — Categorical variables and conditional probabilities

**Notation.** P(A|B)=P(A∩B)/P(B); a risk difference is P(Y=1|X=1)−P(Y=1|X=0) when these probabilities are well defined.

**Results to state.** Conditional probabilities must identify the conditioning event clearly. Association in observational data does not by itself identify a causal effect.

#### D2M08 — Contingency tables and chi-square inference

**Notation.** E_ij=(row total_i×column total_j)/N and X²=Σ_ij(O_ij−E_ij)²/E_ij.

**Results to state.** The chi-square approximation requires independent observational units and adequate expected counts. An aggregate table may require frequency weights rather than row counts.

#### D2M09 — Stratification, confounding, and Simpson-type reversals

**Notation.** A marginal association P(Y|X) can differ from a stratum-specific association P(Y|X,Z) when the distribution of Z differs across X.

**Results to state.** Stratification is a design and modeling decision, not a universal cure for confounding. A reversal across aggregation levels should trigger examination of mechanisms, design, and variable definitions.

#### D2M10 — Randomization tests and sensitivity to design choices

**Notation.** With a sharp null and known assignment mechanism, the randomization distribution of T is generated by assignments allowed by the design.

**Results to state.** Randomization inference is anchored to the assignment mechanism. Sensitivity analysis should report the choices varied and their effect on estimates and conclusions.

## Day 3 — Regression, prediction, diagnostics, and reproducibility

Day 3 treats regression and prediction as transparent conditional models. Each module separates a public demonstration from a distinct BYOD data choice and gives participants an upload path for their own tabular data.

| Module | Formal presentation | Demonstrated dataset | Public BYOD datasets |
|---|---|---|---|
| D3M01 — Simple linear regression and conditional means | Introduce the conditional mean function, simple linear model, least squares, fitted values, residuals, slope, intercept, and the conditional interpretation of a coefficient. | Automobile Data | Carseats; Credit; College |
| D3M02 — Multiple regression and adjustment | Define multiple linear regression, partial regression coefficients, covariate adjustment, reference coding, omitted variables, and conditional versus marginal effects. | Carseats | Automobile Data; Credit; House Prices |
| D3M03 — Regression uncertainty and coefficient intervals | Introduce coefficient standard errors, confidence intervals, tests, model degrees of freedom, and the distinction between coefficient uncertainty and predictive uncertainty. | Credit | Automobile Data; Carseats; College |
| D3M04 — Nonlinearity, transformations, and model specification | Define functional form, transformations, polynomial terms, interaction terms, residual patterns, and the risks of specification search. | House Prices | Automobile Data; Carseats; Boston Housing |
| D3M05 — Logistic regression, odds, and predicted probabilities | Introduce binary outcomes, probability models, log-odds, logistic links, odds ratios, and the difference between odds and probability. | Credit Card Default | Pima Indians Diabetes Training Data; Birth Weight; Health Insurance |
| D3M06 — Binary-outcome prediction and classification thresholds | Define fitted probability, classification threshold, false-positive and false-negative errors, sensitivity, specificity, and decision-dependent performance. | Pima Indians Diabetes Training Data | Credit Card Default; Birth Weight; Health Insurance |
| D3M07 — Calibration, discrimination, and probability communication | Define calibration, discrimination, predicted risk, calibration plots, and how probability estimates should be communicated to nontechnical audiences. | Health Insurance | Credit Card Default; Arthritis Treatment Data; Smoke Ban |
| D3M08 — Diagnostics, influence, and sensitivity analysis | Define residual diagnostics, leverage, influence, influential cases, alternative specifications, and transparent analytical sensitivity analysis. | California Schools | College; Automobile Data; Carseats |
| D3M09 — Training, testing, and out-of-sample validation | Define training data, test data, resampling, generalization, prediction error, data leakage, and the distinction between model fitting and model evaluation. | Pima Indians Diabetes Test Data | Pima Indians Diabetes Training Data; Credit Card Default; Health Insurance |
| D3M10 — Reproducible no-code workflows and transparent reporting | Define computational reproducibility, data provenance, analysis specifications, software environments, seeds, versioned data, output records, and limits of app-generated reports. | Doctor Visits | House Prices; Boston Housing; California Schools |

### Module-level upload route

Participants may upload their own CSV file in **every** module. The app reads the upload in memory, asks the participant to select compatible variables, and applies the same descriptive or inferential workflow. An uploaded dataset does not make a method automatically appropriate; the participant must still evaluate the design, variables, assumptions, and target inference.

### Formal notation and results

#### D3M01 — Simple linear regression and conditional means

**Notation.** In Y=β_0+β_1X+ε, ordinary least squares selects β̂ to minimize Σ_i(Y_i−β_0−β_1X_i)².

**Results to state.** A slope estimates a conditional linear association under the model specification. A regression line does not establish causation without design and substantive assumptions.

#### D3M02 — Multiple regression and adjustment

**Notation.** In Y=β_0+β_1X_1+…+β_pX_p+ε, β_j is the model-based change in E[Y|X] per unit X_j holding other included X variables fixed.

**Results to state.** Adjustment changes the estimand and requires a substantive rationale for included variables. Holding variables fixed in a model is not equivalent to experimental control.

#### D3M03 — Regression uncertainty and coefficient intervals

**Notation.** An approximate coefficient interval is β̂_j ± t_(1−α/2,df)SE(β̂_j) under the fitted-model assumptions.

**Results to state.** A coefficient interval is conditional on the model, the observed covariates, and the sampling/design assumptions. Statistical significance should not be used as a substitute for model comparison or substantive interpretation.

#### D3M04 — Nonlinearity, transformations, and model specification

**Notation.** A transformed model replaces X or Y with g(X) or h(Y); a polynomial specification augments E[Y|X] with powers such as X².

**Results to state.** A transformation changes the scale and interpretation of model parameters. Improved in-sample fit alone does not justify a more complex specification.

#### D3M05 — Logistic regression, odds, and predicted probabilities

**Notation.** logit[P(Y=1|X=x)] = log(p(x)/(1−p(x))) = β_0+x^Tβ; exp(β_j) is a conditional odds ratio.

**Results to state.** An odds ratio is not generally a risk ratio. Predicted probabilities depend on the covariate pattern and the model specification.

#### D3M06 — Binary-outcome prediction and classification thresholds

**Notation.** A threshold rule predicts Ŷ=I[p̂(X)≥c]; changing c changes the confusion matrix and its error trade-offs.

**Results to state.** A classification threshold encodes a decision and its consequences. Accuracy alone can be misleading with imbalanced outcomes or unequal error costs.

#### D3M07 — Calibration, discrimination, and probability communication

**Notation.** A calibrated model satisfies approximately P(Y=1|p̂(X)=p)≈p over relevant groups; discrimination concerns separation of outcome classes by scores.

**Results to state.** Good discrimination does not guarantee calibrated probabilities. Probability statements should identify the model, population, horizon, and uncertainty.

#### D3M08 — Diagnostics, influence, and sensitivity analysis

**Notation.** The residual is e_i=y_i−ŷ_i; sensitivity analysis compares estimates over a pre-specified or transparently reported set of defensible choices.

**Results to state.** A model can fit a summary well while failing diagnostically important patterns. Sensitivity analysis reveals dependence on choices; it does not eliminate substantive uncertainty.

#### D3M09 — Training, testing, and out-of-sample validation

**Notation.** For held-out outcomes y_i and predictions ŷ_i, MSPE=m⁻¹Σ_i(y_i−ŷ_i)²; evaluation is valid only when the test relationship matches the target use case.

**Results to state.** In-sample fit and out-of-sample performance answer different questions. A test set must be protected from model-selection decisions to serve as a final evaluation set.

#### D3M10 — Reproducible no-code workflows and transparent reporting

**Notation.** A reproducible result is conditional on a documented dataset D, transformation A, model M, settings S, software environment E, and random seed r where relevant.

**Results to state.** No-code applications should make assumptions and provenance visible rather than conceal them. Reproducibility is necessary but not sufficient for validity or causal interpretation.

## Dataset access and provenance

The app bundles the public CSV files locally. The dataset assignments are machine-readable in `data/module_manifest.json`, and the original public source is the [Rdatasets archive](https://vincentarelbundock.github.io/Rdatasets/datasets.html).[1] The original data documentation, package attribution, collection process, and limitations remain essential for any use beyond teaching.

## Reference

[1] [Vincent Arel-Bundock, *Rdatasets*: a collection of datasets originally distributed with R and its add-on packages](https://github.com/vincentarelbundock/Rdatasets)
