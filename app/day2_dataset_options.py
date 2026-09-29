"""Curated public datasets for the ten Day 2 Streamlit modules.

The registry is deliberately stricter than the general public-data library.  It
contains only files whose currently supplied columns fit the module's teaching
question without treating a numeric code as a factor or ignoring frequency
weights.  The generic workspace still asks the analyst to verify the study
design and variable coding before any calculation.
"""

from __future__ import annotations

from typing import Final, TypedDict


class Day2DatasetOption(TypedDict):
    """A public file and the reason it belongs in one Day 2 module."""

    file: str
    method: str
    rationale: str
    caution: str


DAY2_MODULE_IDS: Final[tuple[str, ...]] = tuple(f"d2m{number:02d}" for number in range(1, 11))


DAY2_DATASET_OPTIONS: Final[dict[str, tuple[Day2DatasetOption, ...]]] = {
    "d2m01": (
        {
            "file": "tooth_growth.csv",
            "method": "Two-group hypothesis test: tooth length by supplement",
            "rationale": "`len` is numeric and `supp` has two labelled groups.",
            "caution": "Dose is balanced across supplement groups; state whether the comparison averages over dose.",
        },
        {
            "file": "plant_growth.csv",
            "method": "Group-comparison hypotheses: plant weight by treatment group",
            "rationale": "`weight` is numeric and `group` has three labelled levels.",
            "caution": "Specify a two-group contrast or an omnibus three-group question before calculating.",
        },
        {
            "file": "birth_weight.csv",
            "method": "Two-group hypothesis test: birth weight by smoking code",
            "rationale": "`bwt` is numeric and `smoke` is a binary zero/one indicator recognised by the app.",
            "caution": "Document the coding and do not interpret this observational comparison causally.",
        },
        {
            "file": "warpbreaks.csv",
            "method": "Group-comparison hypotheses: breaks by wool or tension",
            "rationale": "`breaks` is numeric; `wool` is binary and `tension` has three labelled levels.",
            "caution": "Pre-specify one grouping variable rather than searching over factors after seeing results.",
        },
    ),
    "d2m02": (
        {
            "file": "plant_growth.csv",
            "method": "Effect size: plant weight by treatment group",
            "rationale": "Supports raw differences and standardized mean differences for selected groups.",
            "caution": "For a two-group effect size, select and justify one planned pair of groups.",
        },
        {
            "file": "tooth_growth.csv",
            "method": "Effect size: tooth length by supplement",
            "rationale": "Continuous `len` and two-level `supp` directly support a standardized difference.",
            "caution": "Keep the role of dose explicit in the interpretation.",
        },
        {
            "file": "birth_weight.csv",
            "method": "Effect size: birth weight by smoking code",
            "rationale": "Continuous birth weight can be compared across the binary smoking indicator.",
            "caution": "The dataset is observational; an effect size does not establish causality.",
        },
        {
            "file": "warpbreaks.csv",
            "method": "Effect size: break counts by wool or tension",
            "rationale": "The outcome and labelled group factors support a practical-significance discussion.",
            "caution": "Choose one planned comparison and state its scientific scale.",
        },
    ),
    "d2m03": (
        {
            "file": "birth_weight.csv",
            "method": "Welch comparison: birth weight by smoking code",
            "rationale": "A numeric outcome and a binary zero/one group indicator are directly available.",
            "caution": "Treat the result as an observational association unless design evidence supports more.",
        },
        {
            "file": "tooth_growth.csv",
            "method": "Welch comparison: tooth length by supplement",
            "rationale": "`len` by `supp` supplies a direct two-group comparison.",
            "caution": "State whether the estimand averages across dose or uses a preselected dose subset.",
        },
        {
            "file": "plant_growth.csv",
            "method": "Welch comparison: a planned pair of treatment groups",
            "rationale": "Two chosen levels of `group` can be compared on numeric `weight`.",
            "caution": "Do not select the pair after inspecting every possible comparison.",
        },
        {
            "file": "warpbreaks.csv",
            "method": "Welch comparison: break counts by wool",
            "rationale": "`breaks` is numeric and `wool` has two labelled groups.",
            "caution": "Account for the second factor, `tension`, in the design discussion.",
        },
        {
            "file": "pima_train.csv",
            "method": "Welch comparison: numeric health measure by diabetes type",
            "rationale": "The labelled binary `type` column can group a numeric measurement such as `glu` or `bmi`.",
            "caution": "This is an independent-group example, not a paired-measurement analysis.",
        },
    ),
    "d2m04": (),
    "d2m05": (
        {
            "file": "insect_sprays.csv",
            "method": "One-way analysis of variance: insect count by spray",
            "rationale": "`count` is numeric and `spray` has six labelled groups.",
            "caution": "The omnibus result does not identify which sprays differ; plan follow-up comparisons.",
        },
        {
            "file": "plant_growth.csv",
            "method": "One-way analysis of variance: plant weight by group",
            "rationale": "A numeric outcome is observed across three labelled treatment groups.",
            "caution": "Inspect group distributions and report an effect size, not only the omnibus p-value.",
        },
        {
            "file": "warpbreaks.csv",
            "method": "One-way analysis of variance: break counts by tension",
            "rationale": "`breaks` is numeric and `tension` has three labelled levels.",
            "caution": "Keep the separate wool factor visible in the design interpretation.",
        },
    ),
    "d2m06": (
        {
            "file": "warpbreaks.csv",
            "method": "Rank/permutation comparison: break counts by wool or tension",
            "rationale": "The outcome-and-group structure supports a comparative randomization or rank-based discussion.",
            "caution": "The current generic app workspace does not implement a dedicated rank or permutation calculation.",
        },
        {
            "file": "insect_sprays.csv",
            "method": "Rank/permutation comparison: insect counts by spray",
            "rationale": "The numeric count outcome is observed across six labelled groups.",
            "caution": "The current generic app workspace does not implement a dedicated rank or permutation calculation.",
        },
        {
            "file": "tooth_growth.csv",
            "method": "Rank/permutation comparison: tooth length by supplement",
            "rationale": "The data provide a numeric outcome and two labelled groups.",
            "caution": "The current generic app workspace does not implement a dedicated rank or permutation calculation.",
        },
        {
            "file": "plant_growth.csv",
            "method": "Rank/permutation comparison: plant weight by group",
            "rationale": "The data provide a numeric outcome and three labelled groups.",
            "caution": "The current generic app workspace does not implement a dedicated rank or permutation calculation.",
        },
    ),
    "d2m07": (
        {
            "file": "arthritis.csv",
            "method": "Conditional probabilities: treatment by improvement",
            "rationale": "`Treatment` and `Improved` are labelled categorical variables.",
            "caution": "`Improved` has missing values; explicitly choose and justify the app's missing-data rule.",
        },
        {
            "file": "default.csv",
            "method": "Conditional probabilities: student status by default",
            "rationale": "`student` and `default` form a direct two-by-two categorical table.",
            "caution": "Default is rare; report conditional probabilities and magnitude, not only significance.",
        },
        {
            "file": "health_insurance.csv",
            "method": "Conditional probabilities: insurance by health status",
            "rationale": "The labelled binary categorical variables provide a direct table.",
            "caution": "A large sample can make a small association statistically detectable.",
        },
        {
            "file": "smoke_ban.csv",
            "method": "Conditional probabilities: smoke-ban status by smoker status",
            "rationale": "`ban` and `smoker` form a direct two-by-two categorical table.",
            "caution": "This association does not by itself show that the ban caused smoking behavior.",
        },
    ),
    "d2m08": (
        {
            "file": "arthritis.csv",
            "method": "Sparse two-by-two table: Fisher's exact test and odds ratio",
            "rationale": "Treatment by improvement produces a two-by-two table with a small expected cell after complete-case handling.",
            "caution": "`Improved` has missing values; explicitly choose and justify the app's missing-data rule.",
        },
        {
            "file": "default.csv",
            "method": "Pearson chi-square: student status by default",
            "rationale": "The two-by-two table has ample expected counts for the chi-square reference calculation.",
            "caution": "Report the odds ratio and conditional proportions alongside the p-value.",
        },
        {
            "file": "health_insurance.csv",
            "method": "Pearson chi-square and Cramér's V: insurance by health status",
            "rationale": "The categorical table has large expected counts and directly supports association measures.",
            "caution": "Association and effect size still need a design-based interpretation.",
        },
        {
            "file": "smoke_ban.csv",
            "method": "Pearson chi-square and Cramér's V: smoke-ban status by smoker status",
            "rationale": "The two-by-two categorical table has very large expected counts.",
            "caution": "Do not convert statistical association into a causal conclusion without design evidence.",
        },
    ),
    "d2m09": (
        {
            "file": "health_insurance.csv",
            "method": "Stratified categorical comparison: insurance, health, and region or education",
            "rationale": "Multiple labelled categorical variables support a marginal-versus-stratified comparison.",
            "caution": "Stratification is a design choice; it does not automatically remove confounding.",
        },
        {
            "file": "smoke_ban.csv",
            "method": "Stratified categorical comparison: ban, smoking, and education or gender",
            "rationale": "The file has several labelled binary and multi-level categorical variables.",
            "caution": "The current generic workspace does not compute a Mantel–Haenszel or Simpson-reversal analysis automatically.",
        },
        {
            "file": "arthritis.csv",
            "method": "Stratified categorical comparison: treatment, improvement, and sex",
            "rationale": "Treatment and sex are labelled factors, with improvement available subject to missingness handling.",
            "caution": "The missing improvement values and small cells make this a design-discussion example, not a routine automated analysis.",
        },
    ),
    "d2m10": (
        {
            "file": "smoke_ban.csv",
            "method": "Design-sensitivity discussion: smoke-ban status and smoking",
            "rationale": "A direct categorical exposure/outcome table supports an explicit discussion of assignment and causal limitations.",
            "caution": "The current app does not implement a randomization-test engine; do not imply random assignment from this file.",
        },
        {
            "file": "arthritis.csv",
            "method": "Design-sensitivity discussion: treatment and improvement",
            "rationale": "The treatment/outcome structure supports a sharp-null and design-assumption discussion.",
            "caution": "The current app does not implement a randomization-test engine, and improvement missingness must be addressed.",
        },
        {
            "file": "default.csv",
            "method": "Design-sensitivity discussion: student status and default",
            "rationale": "A direct two-by-two categorical association supports sensitivity-to-coding discussion.",
            "caution": "The current app does not implement a randomization-test engine; this is observational association data.",
        },
        {
            "file": "health_insurance.csv",
            "method": "Design-sensitivity discussion: insurance and health status",
            "rationale": "Several categorical variables allow transparent alternative coding and subgroup discussions.",
            "caution": "The current app does not implement a randomization-test engine; this is observational association data.",
        },
    ),
}


DAY2_PREPARATION_GUIDANCE: Final[dict[str, str]] = {
    "d2m04": (
        "No bundled public dataset is ready for a paired comparison in the current app. "
        "Chick Weight is relevant repeated-measures source data, but it is long format. "
        "Prepare a wide CSV with one row per chick and two explicitly selected weight-at-time columns, "
        "then upload it through BYOD."
    ),
}


def day2_dataset_options(module_id: str) -> tuple[Day2DatasetOption, ...] | None:
    """Return curated options for a Day 2 module, or ``None`` for other days."""

    return DAY2_DATASET_OPTIONS.get(module_id)


def day2_preparation_guidance(module_id: str) -> str | None:
    """Return an explicit explanation when a module has no ready public file."""

    return DAY2_PREPARATION_GUIDANCE.get(module_id)
