# Public Dataset Library

The companion app uses a curated library of **34 public datasets** that are bundled as CSV files in `data/public/`. This design makes the seminar exercises stable, transparent, and usable without API keys or live network access.

## Source and provenance

The local files are sourced from [Rdatasets](https://vincentarelbundock.github.io/Rdatasets/datasets.html), a public archive of datasets distributed with R packages and related teaching resources. The archive's [GitHub repository](https://github.com/vincentarelbundock/Rdatasets) provides the CSV source paths and documentation links for each dataset. The original package, data collection, and attribution information remain important and should be consulted before any use beyond classroom demonstration.[1]

The `module_manifest.json` file is the authoritative mapping between a seminar module, its one worked example, and its four public BYOD choices. Every module therefore has a reproducible, no-key data plan.

| Day | Modules | Worked examples | BYOD dataset choices |
|---|---:|---:|---:|
| Day 1: Foundations of inference | 3 | 3 | 12 |
| Day 2: Tests and regression | 3 | 3 | 12 |
| Day 3: Prediction and reproducibility | 3 | 3 | 12 |

## Important usage note

These data are selected for teaching statistical reasoning. They are not a substitute for carefully documented research data, and they do not automatically support causal interpretations. The app identifies their source file but does not alter the original public data other than removing the archive's row-name column during display.

## References

[1] [Vincent Arel-Bundock, *Rdatasets*: a collection of datasets originally distributed with R and its add-on packages](https://github.com/vincentarelbundock/Rdatasets)
