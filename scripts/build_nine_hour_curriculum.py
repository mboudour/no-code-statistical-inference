"""Build the nine-hour, 30-module seminar manifest and its public design document."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_DIR / "data" / "module_manifest.json"
DESIGN_PATH = PROJECT_DIR / "docs" / "seminar_design.md"

DATASETS = {
    "iris.csv": "Iris",
    "airquality.csv": "New York Air Quality",
    "women.csv": "Average Heights and Weights for American Women",
    "quakes.csv": "Earthquake Locations and Magnitudes",
    "faithful.csv": "Old Faithful Eruptions",
    "trees.csv": "Black Cherry Trees",
    "cars.csv": "Speed and Stopping Distances",
    "motorcycle.csv": "Motorcycle Accident Simulation Data",
    "mtcars.csv": "Motor Trend Car Road Tests",
    "college.csv": "College",
    "tooth_growth.csv": "Tooth Growth",
    "plant_growth.csv": "Plant Growth",
    "birth_weight.csv": "Birth Weight",
    "chick_weight.csv": "Chick Weight",
    "insect_sprays.csv": "Insect Sprays",
    "warpbreaks.csv": "Warp Breaks",
    "arthritis.csv": "Arthritis Treatment Data",
    "ucb_admissions.csv": "UC Berkeley Admissions",
    "titanic.csv": "Titanic Passenger Survival",
    "smoke_ban.csv": "Smoke Ban",
    "auto.csv": "Automobile Data",
    "carseats.csv": "Carseats",
    "credit.csv": "Credit",
    "house_prices.csv": "House Prices",
    "default.csv": "Credit Card Default",
    "pima_train.csv": "Pima Indians Diabetes Training Data",
    "health_insurance.csv": "Health Insurance",
    "ca_schools.csv": "California Schools",
    "pima_test.csv": "Pima Indians Diabetes Test Data",
    "doctor_visits.csv": "Doctor Visits",
    "us_arrests.csv": "US Arrest Rates",
    "housing.csv": "Boston Housing",
}


def dataset(filename: str) -> dict[str, str]:
    return {"file": filename, "name": DATASETS[filename]}


def module_contract(module_id: str, title: str) -> dict[str, str]:
    """Return the common pedagogical contract that accompanies every module."""
    if module_id.startswith("d1"):
        question = "What are the observational units, variables, target population, and uncertainty-relevant features of this dataset?"
        variables = "Identify numeric, categorical, binary, and potential grouping variables before computing an inferential summary."
        assumptions = "Document the sampling process, unit of observation, missingness, and whether the data can support a target-population claim."
        diagnostics = "Inspect missingness, duplicates, distributions, outliers, and measurement/coding choices."
    elif module_id in {"d2m07", "d2m08", "d2m09"}:
        question = "Are two categorical variables associated in the observed population or sample, under the stated design?"
        variables = "Select two categorical variables with mutually exclusive, documented categories."
        assumptions = "State whether rows are independent and whether table categories and expected counts support the proposed reference distribution."
        diagnostics = "Inspect cell counts, expected counts, conditional proportions, and sparse-category warnings."
    elif module_id == "d2m04":
        question = "What is the average within-unit difference between two valid paired measurements?"
        variables = "Select two numeric variables that form scientifically valid pairs on the same unit."
        assumptions = "Verify pair identity, independence between pairs, and the distribution of within-pair differences."
        diagnostics = "Inspect the paired-difference distribution, missing pairs, and outlying differences."
    elif module_id in {"d2m03", "d2m05", "d2m06", "d2m10"}:
        question = "How do numeric outcomes compare across the selected groups under the stated study design?"
        variables = "Select one numeric outcome and a documented categorical grouping variable."
        assumptions = "State group formation, independence, outcome scale, variance structure, and any planned comparison strategy."
        diagnostics = "Inspect group sizes, grouped distributions, outliers, and variance evidence before interpreting a test."
    elif module_id.startswith("d2"):
        question = "What estimand, reference model, and practical interpretation are appropriate for this comparison?"
        variables = "Identify the outcome, grouping/predictor variable, and the unit of analysis."
        assumptions = "State the design, null/reference model, and whether inference targets a mean, proportion, association, or effect size."
        diagnostics = "Use graphical summaries and sensitivity checks before treating a test statistic as decisive."
    elif module_id in {"d3m05", "d3m06", "d3m07"}:
        question = "How is a binary outcome conditionally associated with the selected predictors under a logistic model?"
        variables = "Select a binary outcome and documented predictors; define the outcome reference category."
        assumptions = "State independence, adequate outcome representation, predictor coding, and the conditional-model interpretation."
        diagnostics = "Inspect outcome balance, fitted probabilities, classification consequences, and calibration/discrimination evidence."
    else:
        question = "How is a numeric outcome conditionally associated with the selected predictors under a stated regression model?"
        variables = "Select a numeric outcome, predictor(s), and the intended unit of analysis."
        assumptions = "State independence, functional form, residual structure, predictor coding, and the non-causal nature of an observational regression unless design justifies otherwise."
        diagnostics = "Inspect residuals, influence, heteroskedasticity, collinearity, and functional-form evidence."
    return {
        "learning_objective": f"Apply the logic of {title.lower()} to a documented research question, dataset audit, and interpretation.",
        "research_question_prompt": question,
        "required_variable_types": variables,
        "assumption_focus": assumptions,
        "diagnostic_focus": diagnostics,
        "interpretation_template": "State the estimate, uncertainty, effect size where applicable, p-value only as model-based evidence, practical meaning, and limitations.",
        "audit_prompt": "Before analysis, identify the target population, unit of observation, measurement process, missing-data treatment, and design limitations.",
    }


def module(
    module_id: str,
    title: str,
    focus: str,
    notation: str,
    results: list[str],
    demonstration: str,
    activity: str,
    byod_files: list[str],
) -> dict:
    return {
        "id": module_id,
        "title": title,
        "duration_minutes": 17,
        "presentation_minutes": 6,
        "demonstration_minutes": 5,
        "byod_minutes": 6,
        "presentation_focus": focus,
        "notation": notation,
        "results": results,
        "demonstration": {**dataset(demonstration), "activity": activity},
        "byod": [dataset(filename) for filename in byod_files],
        "upload_guidance": "Participants may instead upload their own CSV file. They select variables in the app and use the module workflow after recording the research question, unit of observation, and compatibility of variables.",
        **module_contract(module_id, title),
    }


def build_days() -> list[dict]:
    day_1_modules = [
        module(
            "d1m01",
            "Observational units, variables, populations, and samples",
            "Define observational units, variables, populations, samples, parameters, statistics, and the distinction between a scientific target and an observed dataset.",
            "Let X_1, …, X_n denote observed values sampled from a population distribution F; a parameter θ is a feature of F, while a statistic T(X_1, …, X_n) is a function of the sample.",
            ["A statistic and a parameter are conceptually different objects.", "The population of inference must be specified before a sample can support a general claim."],
            "iris.csv",
            "Identify observational units and variable types, then distinguish species-specific sample summaries from population targets.",
            ["mtcars.csv", "us_arrests.csv", "airquality.csv"],
        ),
        module(
            "d1m02",
            "Measurement scales, coding, and data quality",
            "Introduce nominal, ordinal, interval, and ratio scales; distinguish recorded codes from substantive constructs; and identify missingness and data-quality concerns.",
            "A variable X can be numeric without being interval-scaled; transformations and arithmetic summaries require assumptions about the scale and coding of X.",
            ["Variable coding determines which comparisons and summaries are meaningful.", "Missing values are part of the data-generating and measurement process, not merely a software inconvenience."],
            "airquality.csv",
            "Audit variable types, identify missing ozone and solar-radiation values, and specify an analysis-ready subset.",
            ["college.csv", "health_insurance.csv", "doctor_visits.csv"],
        ),
        module(
            "d1m03",
            "Distributional summaries: centre, spread, and shape",
            "Define the mean, median, variance, standard deviation, interquartile range, quantiles, skewness, and the role of robust summaries.",
            "For values x_1, …, x_n, x̄ = n⁻¹Σ_i x_i and s² = (n−1)⁻¹Σ_i(x_i−x̄)²; the median minimizes the sum of absolute deviations.",
            ["The mean and standard deviation are sensitive to extreme observations.", "Quantiles and robust summaries can communicate distributional structure that one average obscures."],
            "women.csv",
            "Compare mean/standard deviation with median/interquartile range for height and weight, then interpret their different purposes.",
            ["cars.csv", "mtcars.csv", "iris.csv"],
        ),
        module(
            "d1m04",
            "Visual evidence and exploratory data analysis",
            "State the purpose and limitations of histograms, boxplots, scatterplots, conditional summaries, and visual detection of unusual observations.",
            "The empirical distribution function is F̂_n(x) = n⁻¹Σ_i I(X_i ≤ x); graphical displays approximate features of F̂_n or of conditional distributions.",
            ["A graphic is an estimator or display of data structure, not a proof of a model.", "Patterns should be checked against variable definitions, sampling mechanisms, and potential measurement artifacts."],
            "quakes.csv",
            "Visualise depth and magnitude, inspect marginal distributions, and describe patterns without inferring a causal process.",
            ["faithful.csv", "trees.csv", "motorcycle.csv"],
        ),
        module(
            "d1m05",
            "Random variation and repeated sampling",
            "Introduce randomness, sampling variability, repeated-sampling thought experiments, and the distinction between a realised sample and its sampling distribution.",
            "If X_1, …, X_n are iid with mean μ and variance σ², then E[X̄] = μ and Var(X̄) = σ²/n.",
            ["The observed sample mean is one realisation of a random estimator.", "Larger samples reduce the variance of the sample mean when the iid model is appropriate."],
            "faithful.csv",
            "Use repeated subsamples to see how estimates of waiting time vary across equally sized samples.",
            ["iris.csv", "cars.csv", "airquality.csv"],
        ),
        module(
            "d1m06",
            "Sampling distributions and the central limit theorem",
            "Define a sampling distribution, standard error, normal approximation, and the regularity conditions behind the central limit theorem.",
            "Under iid sampling with finite variance, √n(X̄−μ)/σ converges in distribution to N(0,1) as n grows.",
            ["The central limit theorem concerns an estimator over repeated samples, not the raw-data shape alone.", "Normal approximations require context-specific checks rather than mechanical invocation."],
            "trees.csv",
            "Simulate repeated samples of tree volume and compare the raw distribution with the distribution of sample means.",
            ["women.csv", "auto.csv", "house_prices.csv"],
        ),
        module(
            "d1m07",
            "Standard errors and confidence intervals",
            "Define standard error, confidence procedures, interval width, confidence level, and long-run coverage.",
            "An approximate 1−α interval for μ is X̄ ± z_(1−α/2) SE(X̄); the procedure targets P_μ{μ ∈ C(X)} = 1−α under stated assumptions.",
            ["A confidence interval is not a probability distribution over a fixed parameter in the frequentist interpretation.", "Interval width depends on variability, sample size, and chosen confidence level."],
            "cars.csv",
            "Estimate mean stopping distance and compare confidence intervals under different sample sizes and confidence levels.",
            ["women.csv", "trees.csv", "motorcycle.csv"],
        ),
        module(
            "d1m08",
            "Bootstrap confidence intervals",
            "Define the empirical distribution, resampling with replacement, bootstrap replicates, bootstrap standard error, and percentile intervals.",
            "The empirical distribution F̂_n places mass 1/n on each observation; θ̂* is the statistic recomputed on a sample drawn from F̂_n.",
            ["Bootstrap methods approximate sampling variation through the empirical distribution.", "Resampling cannot repair selection bias, an ill-defined estimand, or data that do not represent the target population."],
            "motorcycle.csv",
            "Bootstrap the mean acceleration and compare its resampling uncertainty with a normal-approximation interval.",
            ["birth_weight.csv", "tooth_growth.csv", "plant_growth.csv"],
        ),
        module(
            "d1m09",
            "Monte Carlo simulation and numerical uncertainty",
            "Introduce simulation design, pseudo-random draws, Monte Carlo estimators, reproducible seeds, and simulation error.",
            "For independent simulation outputs Z_1, …, Z_B, the Monte Carlo estimator B⁻¹Σ_b Z_b has standard error proportional to B^(−1/2).",
            ["A simulation estimate has its own numerical uncertainty.", "Seeds support reproducibility but do not validate the underlying statistical model."],
            "mtcars.csv",
            "Simulate random subsamples of vehicle records and quantify how a correlation estimate changes across runs.",
            ["auto.csv", "carseats.csv", "credit.csv"],
        ),
        module(
            "d1m10",
            "Assumptions, outliers, and analytical readiness",
            "Define an assumption, an outlier, leverage, influence, transformations, and the difference between data screening and post-hoc result selection.",
            "For a model M, inferential validity is conditional on the data-generating conditions and assumptions encoded by M, not only on a computed p-value.",
            ["Outliers should be investigated substantively and statistically rather than removed automatically.", "Analytical decisions made after inspecting outcomes require transparent documentation."],
            "college.csv",
            "Inspect missingness, distributional extremes, and potentially influential observations before choosing an inferential procedure.",
            ["airquality.csv", "house_prices.csv", "doctor_visits.csv"],
        ),
    ]

    day_2_modules = [
        module(
            "d2m01",
            "Estimands, hypotheses, and null reference distributions",
            "Define null and alternative hypotheses, test statistics, null distributions, significance level, p-values, and the relation between tests and estimands.",
            "For H_0: θ=θ_0 and test statistic T, the p-value is P_{H_0}(|T|≥|t_obs|) for a two-sided reference rule.",
            ["A p-value is conditional on the null model and the specified test statistic.", "A non-significant result is not evidence that an effect is exactly zero."],
            "tooth_growth.csv",
            "Frame a supplement comparison as an estimand and test it at a selected dose, before interpreting the p-value.",
            ["plant_growth.csv", "birth_weight.csv", "chick_weight.csv"],
        ),
        module(
            "d2m02",
            "Effect sizes and practical significance",
            "Define raw differences, standardized mean differences, uncertainty intervals, practical thresholds, and the difference between statistical and substantive significance.",
            "For two groups, Cohen's d = (X̄_2−X̄_1)/s_p, where s_p is a pooled within-group standard deviation under its stated convention.",
            ["Effect sizes require scale and context for interpretation.", "An effect can be precisely estimated yet substantively negligible, or important yet imprecisely estimated."],
            "plant_growth.csv",
            "Compare treatment and control means, calculate a standardized difference, and discuss a domain-relevant threshold.",
            ["tooth_growth.csv", "birth_weight.csv", "warpbreaks.csv"],
        ),
        module(
            "d2m03",
            "Independent two-group comparisons",
            "Present the independent-samples mean difference, Welch's t procedure, standard-error construction, confidence intervals, and assumptions about group formation.",
            "T = (X̄_1−X̄_2)/√(s_1²/n_1+s_2²/n_2), with a Welch–Satterthwaite reference degrees-of-freedom approximation.",
            ["Welch's procedure does not assume equal population variances.", "Causal language requires an appropriate design, not only a two-group test."],
            "birth_weight.csv",
            "Compare birth weight across a selected binary grouping variable and distinguish an observed association from causal evidence.",
            ["tooth_growth.csv", "plant_growth.csv", "chick_weight.csv"],
        ),
        module(
            "d2m04",
            "Paired and repeated-measures comparisons",
            "Define paired differences, within-unit dependence, repeated observations, longitudinal structure, and why an independent-sample analysis can be inappropriate for paired data.",
            "For paired values (X_i,Y_i), analyse D_i=Y_i−X_i; the paired t statistic is T=D̄/(s_D/√n).",
            ["Pairing can reduce variance when within-unit correlation is used correctly.", "Repeated measurements require clarity about the observational unit and the dependence structure."],
            "chick_weight.csv",
            "Use repeated measurements by chick to discuss why time-specific comparisons and independent-unit assumptions must be separated.",
            ["tooth_growth.csv", "plant_growth.csv", "pima_train.csv"],
        ),
        module(
            "d2m05",
            "Analysis of variance and multi-group questions",
            "Introduce between-group and within-group variation, the one-way ANOVA model, F statistics, omnibus tests, contrasts, and multiplicity-aware follow-up questions.",
            "In Y_ij=μ+α_j+ε_ij, the F statistic compares mean-square variation between groups with mean-square variation within groups.",
            ["An omnibus ANOVA test does not identify which group differences are present.", "Planned contrasts and post-hoc comparisons should be distinguished and documented."],
            "insect_sprays.csv",
            "Compare mean insect counts across spray types, interpret the omnibus test, and define an appropriate next comparison.",
            ["plant_growth.csv", "warpbreaks.csv", "chick_weight.csv"],
        ),
        module(
            "d2m06",
            "Nonparametric and permutation approaches",
            "Introduce rank-based tests, randomization/permutation logic, exchangeability, and when a distribution-free label is misleading.",
            "Under exchangeability under H_0, a permutation distribution is formed by recomputing T over relabelings consistent with the null hypothesis.",
            ["Permutation validity depends on an exchangeability condition tied to the design.", "Rank-based procedures answer questions about distributions or stochastic ordering that need not equal a mean comparison."],
            "warpbreaks.csv",
            "Compare break counts across a selected group with a rank or permutation perspective, then state the estimand carefully.",
            ["insect_sprays.csv", "tooth_growth.csv", "plant_growth.csv"],
        ),
        module(
            "d2m07",
            "Categorical variables and conditional probabilities",
            "Define joint, marginal, and conditional distributions; risk differences; relative risks; odds; and the role of stratification.",
            "P(A|B)=P(A∩B)/P(B); a risk difference is P(Y=1|X=1)−P(Y=1|X=0) when these probabilities are well defined.",
            ["Conditional probabilities must identify the conditioning event clearly.", "Association in observational data does not by itself identify a causal effect."],
            "arthritis.csv",
            "Construct treatment-by-improvement conditional probabilities and discuss the study-design requirement for causal interpretation.",
            ["health_insurance.csv", "default.csv", "smoke_ban.csv"],
        ),
        module(
            "d2m08",
            "Contingency tables and chi-square inference",
            "Define expected counts, Pearson's chi-square statistic, independence models, reference degrees of freedom, and sparse-table cautions.",
            "E_ij=(row total_i×column total_j)/N and X²=Σ_ij(O_ij−E_ij)²/E_ij.",
            ["The chi-square approximation requires independent observational units and adequate expected counts.", "An aggregate table may require frequency weights rather than row counts."],
            "ucb_admissions.csv",
            "Use the admissions table to calculate observed and expected counts while distinguishing aggregate patterns from stratified questions.",
            ["titanic.csv", "arthritis.csv", "default.csv"],
        ),
        module(
            "d2m09",
            "Stratification, confounding, and Simpson-type reversals",
            "Define a confounder, stratified comparison, marginal association, conditional association, and why aggregation can alter apparent relationships.",
            "A marginal association P(Y|X) can differ from a stratum-specific association P(Y|X,Z) when the distribution of Z differs across X.",
            ["Stratification is a design and modeling decision, not a universal cure for confounding.", "A reversal across aggregation levels should trigger examination of mechanisms, design, and variable definitions."],
            "titanic.csv",
            "Compare survival patterns by sex and passenger class, using the frequency variable correctly and discussing aggregation.",
            ["ucb_admissions.csv", "arthritis.csv", "health_insurance.csv"],
        ),
        module(
            "d2m10",
            "Randomization tests and sensitivity to design choices",
            "Define a sharp null hypothesis, random assignment, randomization distributions, design-consistent testing, and sensitivity to recoding or subgroup definitions.",
            "With a sharp null and known assignment mechanism, the randomization distribution of T is generated by assignments allowed by the design.",
            ["Randomization inference is anchored to the assignment mechanism.", "Sensitivity analysis should report the choices varied and their effect on estimates and conclusions."],
            "smoke_ban.csv",
            "Frame a design-aware comparison, identify a plausible outcome and treatment definition, and list sensitivity choices before computing a result.",
            ["arthritis.csv", "default.csv", "health_insurance.csv"],
        ),
    ]

    day_3_modules = [
        module(
            "d3m01",
            "Simple linear regression and conditional means",
            "Introduce the conditional mean function, simple linear model, least squares, fitted values, residuals, slope, intercept, and the conditional interpretation of a coefficient.",
            "In Y=β_0+β_1X+ε, ordinary least squares selects β̂ to minimize Σ_i(Y_i−β_0−β_1X_i)².",
            ["A slope estimates a conditional linear association under the model specification.", "A regression line does not establish causation without design and substantive assumptions."],
            "auto.csv",
            "Model miles per gallon as a function of weight, interpret the fitted slope, and inspect the residual definition.",
            ["carseats.csv", "credit.csv", "college.csv"],
        ),
        module(
            "d3m02",
            "Multiple regression and adjustment",
            "Define multiple linear regression, partial regression coefficients, covariate adjustment, reference coding, omitted variables, and conditional versus marginal effects.",
            "In Y=β_0+β_1X_1+…+β_pX_p+ε, β_j is the model-based change in E[Y|X] per unit X_j holding other included X variables fixed.",
            ["Adjustment changes the estimand and requires a substantive rationale for included variables.", "Holding variables fixed in a model is not equivalent to experimental control."],
            "carseats.csv",
            "Fit a sales model using price and advertising, then compare the conditional interpretation with a marginal scatterplot.",
            ["auto.csv", "credit.csv", "house_prices.csv"],
        ),
        module(
            "d3m03",
            "Regression uncertainty and coefficient intervals",
            "Introduce coefficient standard errors, confidence intervals, tests, model degrees of freedom, and the distinction between coefficient uncertainty and predictive uncertainty.",
            "An approximate coefficient interval is β̂_j ± t_(1−α/2,df)SE(β̂_j) under the fitted-model assumptions.",
            ["A coefficient interval is conditional on the model, the observed covariates, and the sampling/design assumptions.", "Statistical significance should not be used as a substitute for model comparison or substantive interpretation."],
            "credit.csv",
            "Estimate a simple credit-balance relationship and interpret a coefficient interval together with the scale of the variables.",
            ["auto.csv", "carseats.csv", "college.csv"],
        ),
        module(
            "d3m04",
            "Nonlinearity, transformations, and model specification",
            "Define functional form, transformations, polynomial terms, interaction terms, residual patterns, and the risks of specification search.",
            "A transformed model replaces X or Y with g(X) or h(Y); a polynomial specification augments E[Y|X] with powers such as X².",
            ["A transformation changes the scale and interpretation of model parameters.", "Improved in-sample fit alone does not justify a more complex specification."],
            "house_prices.csv",
            "Compare raw and transformed price relationships, then explain how the interpretation changes with the chosen scale.",
            ["auto.csv", "carseats.csv", "housing.csv"],
        ),
        module(
            "d3m05",
            "Logistic regression, odds, and predicted probabilities",
            "Introduce binary outcomes, probability models, log-odds, logistic links, odds ratios, and the difference between odds and probability.",
            "logit[P(Y=1|X=x)] = log(p(x)/(1−p(x))) = β_0+x^Tβ; exp(β_j) is a conditional odds ratio.",
            ["An odds ratio is not generally a risk ratio.", "Predicted probabilities depend on the covariate pattern and the model specification."],
            "default.csv",
            "Model default probability as a function of balance and interpret both predicted probabilities and an odds ratio.",
            ["pima_train.csv", "birth_weight.csv", "health_insurance.csv"],
        ),
        module(
            "d3m06",
            "Binary-outcome prediction and classification thresholds",
            "Define fitted probability, classification threshold, false-positive and false-negative errors, sensitivity, specificity, and decision-dependent performance.",
            "A threshold rule predicts Ŷ=I[p̂(X)≥c]; changing c changes the confusion matrix and its error trade-offs.",
            ["A classification threshold encodes a decision and its consequences.", "Accuracy alone can be misleading with imbalanced outcomes or unequal error costs."],
            "pima_train.csv",
            "Fit a binary-outcome model and compare classifications under two thresholds while holding the fitted probabilities fixed.",
            ["default.csv", "birth_weight.csv", "health_insurance.csv"],
        ),
        module(
            "d3m07",
            "Calibration, discrimination, and probability communication",
            "Define calibration, discrimination, predicted risk, calibration plots, and how probability estimates should be communicated to nontechnical audiences.",
            "A calibrated model satisfies approximately P(Y=1|p̂(X)=p)≈p over relevant groups; discrimination concerns separation of outcome classes by scores.",
            ["Good discrimination does not guarantee calibrated probabilities.", "Probability statements should identify the model, population, horizon, and uncertainty."],
            "health_insurance.csv",
            "Choose a binary health-related outcome and examine how a simple model's predicted probabilities should be described responsibly.",
            ["default.csv", "arthritis.csv", "smoke_ban.csv"],
        ),
        module(
            "d3m08",
            "Diagnostics, influence, and sensitivity analysis",
            "Define residual diagnostics, leverage, influence, influential cases, alternative specifications, and transparent analytical sensitivity analysis.",
            "The residual is e_i=y_i−ŷ_i; sensitivity analysis compares estimates over a pre-specified or transparently reported set of defensible choices.",
            ["A model can fit a summary well while failing diagnostically important patterns.", "Sensitivity analysis reveals dependence on choices; it does not eliminate substantive uncertainty."],
            "ca_schools.csv",
            "Fit a simple school-outcome model, inspect unusual observations, and compare a small set of transparent specifications.",
            ["college.csv", "auto.csv", "carseats.csv"],
        ),
        module(
            "d3m09",
            "Training, testing, and out-of-sample validation",
            "Define training data, test data, resampling, generalization, prediction error, data leakage, and the distinction between model fitting and model evaluation.",
            "For held-out outcomes y_i and predictions ŷ_i, MSPE=m⁻¹Σ_i(y_i−ŷ_i)²; evaluation is valid only when the test relationship matches the target use case.",
            ["In-sample fit and out-of-sample performance answer different questions.", "A test set must be protected from model-selection decisions to serve as a final evaluation set."],
            "pima_test.csv",
            "Use the linked training/test context to explain why a held-out set must not guide repeated model tuning.",
            ["pima_train.csv", "default.csv", "health_insurance.csv"],
        ),
        module(
            "d3m10",
            "Reproducible no-code workflows and transparent reporting",
            "Define computational reproducibility, data provenance, analysis specifications, software environments, seeds, versioned data, output records, and limits of app-generated reports.",
            "A reproducible result is conditional on a documented dataset D, transformation A, model M, settings S, software environment E, and random seed r where relevant.",
            ["No-code applications should make assumptions and provenance visible rather than conceal them.", "Reproducibility is necessary but not sufficient for validity or causal interpretation."],
            "doctor_visits.csv",
            "Create a compact reproducibility record: data source, variables, method, settings, assumptions, result, and interpretation caveat.",
            ["house_prices.csv", "housing.csv", "ca_schools.csv"],
        ),
    ]

    return [
        {
            "id": "day_1",
            "title": "Day 1 — Data, variation, and uncertainty",
            "general_theme": "Foundations of data, variation, and uncertainty",
            "duration_minutes": 180,
            "introduction_minutes": 10,
            "introduction": "Day 1 establishes the language of data, estimands, variation, sampling distributions, and uncertainty. After a ten-minute orientation, ten 17-minute modules each begin with a rigorous presentation and then move to a public-data demonstration and a distinct BYOD activity.",
            "modules": day_1_modules,
        },
        {
            "id": "day_2",
            "title": "Day 2 — Tests, comparisons, and categorical inference",
            "general_theme": "Evidence from comparisons, tests, and categorical data",
            "duration_minutes": 180,
            "introduction_minutes": 10,
            "introduction": "Day 2 develops formal comparisons and categorical-data reasoning. Every module states its estimand, assumptions, and reference distribution before participants see a demonstrated analysis and work with a separate public BYOD dataset or an upload.",
            "modules": day_2_modules,
        },
        {
            "id": "day_3",
            "title": "Day 3 — Regression, prediction, diagnostics, and reproducibility",
            "general_theme": "Conditional modelling, prediction, diagnostics, and reproducibility",
            "duration_minutes": 180,
            "introduction_minutes": 10,
            "introduction": "Day 3 treats regression and prediction as transparent conditional models. Each module separates a public demonstration from a distinct BYOD data choice and gives participants an upload path for their own tabular data.",
            "modules": day_3_modules,
        },
    ]


def build_manifest() -> dict:
    return {
        "title": "No-Code Statistical Inference: Understanding Data, Uncertainty, and Evidence",
        "format": {"total_hours": 9, "days": 3, "hours_per_day": 3, "modules_per_day": 10, "module_minutes": 17},
        "dataset_source": {
            "name": "Rdatasets public CSV archive",
            "catalog_url": "https://vincentarelbundock.github.io/Rdatasets/datasets.html",
            "repository_url": "https://github.com/vincentarelbundock/Rdatasets",
            "access": "Public files are vendored locally for this app. No API key or runtime network connection is required.",
        },
        "data_pathways": {
            "demonstration": "One public dataset selected and demonstrated by the instructor in every module.",
            "public_byod": "Three distinct public datasets assigned to every module; none duplicates that module's demonstrated dataset.",
            "participant_upload": "Participants may upload their own CSV dataset in every module and use the module workflow after selecting compatible variables.",
        },
        "days": build_days(),
    }


def build_design(manifest: dict) -> str:
    lines = [
        "---",
        "layout: default",
        "title: Nine-Hour Seminar Design",
        "---",
        "",
        "# Nine-Hour Seminar Design: Days, Modules, Demonstrations, and BYOD",
        "",
        "This is a **nine-hour seminar** consisting of **three three-hour days**. Each day begins with a ten-minute introduction and contains **ten 17-minute modules**. Each module follows a presentation-first microstructure: six minutes for a mathematically rigorous presentation without proofs, five minutes for an instructor demonstration using one selected public dataset, and six minutes for a BYOD activity using a **different** public dataset or a participant-uploaded CSV file.",
        "",
        "> **Three distinct data pathways are compulsory in every module.** The instructor demonstrates one public dataset. Participants then choose one of three different public BYOD datasets assigned to that module, or upload their own CSV. The demonstrated dataset is never listed as a BYOD option for the same module.",
        "",
        "## Standard 17-minute module format",
        "",
        "| Component | Minutes | Purpose |",
        "|---|---:|---|",
        "| Rigorous presentation | 6 | Definitions, notation, assumptions, and results; no proofs |",
        "| Instructor demonstration | 5 | Transparent analysis of one selected public dataset |",
        "| BYOD activity | 6 | A separate public dataset choice or a participant CSV upload |",
        "",
    ]
    for day in manifest["days"]:
        lines.extend([f"## {day['title']}", "", day["introduction"], "", "| Module | Formal presentation | Demonstrated dataset | Public BYOD datasets |", "|---|---|---|---|"])
        for module_item in day["modules"]:
            byod_names = "; ".join(entry["name"] for entry in module_item["byod"])
            lines.append(f"| {module_item['id'].upper()} — {module_item['title']} | {module_item['presentation_focus']} | {module_item['demonstration']['name']} | {byod_names} |")
        lines.extend(["", "### Module-level upload route", "", "Participants may upload their own CSV file in **every** module. The app reads the upload in memory, asks the participant to select compatible variables, and applies the same descriptive or inferential workflow. An uploaded dataset does not make a method automatically appropriate; the participant must still evaluate the design, variables, assumptions, and target inference.", "", "### Formal notation and results", ""])
        for module_item in day["modules"]:
            lines.extend([f"#### {module_item['id'].upper()} — {module_item['title']}", "", f"**Notation.** {module_item['notation']}", "", "**Results to state.** " + " ".join(module_item["results"]), ""])
    lines.extend([
        "## Dataset access and provenance",
        "",
        "The app bundles the public CSV files locally. The dataset assignments are machine-readable in `data/module_manifest.json`, and the original public source is the [Rdatasets archive](https://vincentarelbundock.github.io/Rdatasets/datasets.html).[1] The original data documentation, package attribution, collection process, and limitations remain essential for any use beyond teaching.",
        "",
        "## Reference",
        "",
        "[1] [Vincent Arel-Bundock, *Rdatasets*: a collection of datasets originally distributed with R and its add-on packages](https://github.com/vincentarelbundock/Rdatasets)",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DESIGN_PATH.write_text(build_design(manifest), encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(PROJECT_DIR)} and {DESIGN_PATH.relative_to(PROJECT_DIR)}.")


if __name__ == "__main__":
    main()
