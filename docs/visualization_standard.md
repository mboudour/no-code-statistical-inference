# Visualization Standard for No-Code Statistical Inference

## Purpose

The seminar uses graphics to make data, uncertainty, and evidence inspectable rather than decorative. The no-code interface selects an appropriate chart from the variable types supplied by the participant, while retaining the underlying choices and summaries in view.

> **Rule:** A graphic is a display of an observed dataset or an estimated distribution. It does not by itself justify a causal claim, establish a model, or replace a statement of design and assumptions.

## Chart selection standard

| Data structure | Primary interactive display | Supporting display | Interpretation focus |
|---|---|---|---|
| One numeric variable | Histogram | Boxplot | Shape, centre, spread, skewness, and unusual observations |
| One categorical variable | Bar chart of counts or proportions | Frequency table | Level frequencies and denominators |
| Numeric outcome by category | Grouped boxplot with outliers | Jittered observations in static figures | Conditional distributions, medians, spread, overlap, and sample sizes |
| Two categorical variables | Count table and heatmap | Proportion table when appropriate | Joint and conditional distributions; possible association |
| Two numeric variables | Scatterplot | Fitted line only when the model is stated | Functional form, variation, unusual observations, and conditional association |

A boxplot is therefore **not** a plot for a categorical variable by itself. It is appropriate when a categorical variable forms the groups on one axis and the plotted response is numeric.

## Python implementation

The participant-facing Streamlit app uses **Plotly Express** as its primary Python plotting interface. Plotly Express is the high-level Python interface for rapid figure construction and returns standard Plotly figures; its browser-oriented figures make hover, zoom, and inspection useful in a no-code setting.[1] The app provides interactive histograms, univariate boxplots, count/proportion bar charts, grouped boxplots, and categorical association heatmaps.

**Seaborn** and **Matplotlib** are retained for static instructional figures, handouts, and slide-ready outputs. Seaborn is a statistical visualization library built on Matplotlib and provides a high-level interface for statistical graphics.[2] The app’s *Static figure* tab shows a Seaborn/Matplotlib histogram or grouped boxplot so that participants can compare an interactive exploratory graphic with a fixed-format figure.

| Python library | Seminar role | Default use |
|---|---|---|
| `plotly.express` | Interactive no-code exploration in Streamlit | Primary app charts |
| `seaborn` | Concise static statistical figures | Slide and handout figures; static figure tab |
| `matplotlib` | Low-level figure control and export | Foundation for static outputs and custom formatting |

## R implementation

For the R analysis engine, **ggplot2** is the visualization standard. ggplot2 is a declarative implementation of the Grammar of Graphics in which data variables are mapped to aesthetics and combined with geometric layers.[3] It is the appropriate tidyverse-compatible counterpart to the Python visual standard.

```r
library(ggplot2)

# One numeric variable
ggplot(data, aes(x = outcome)) +
  geom_histogram(bins = 30, fill = "#2C7FB8", colour = "white") +
  theme_minimal()

# Numeric outcome by categorical group
ggplot(data, aes(x = group, y = outcome, fill = group)) +
  geom_boxplot(outlier.alpha = 0.7) +
  geom_jitter(width = 0.10, alpha = 0.35) +
  guides(fill = "none") +
  theme_minimal()

# One categorical variable
ggplot(data, aes(x = category)) +
  geom_bar(fill = "#2C7FB8") +
  theme_minimal()
```

## Reproducibility expectations

Every exported or instructor-generated figure should state the dataset, selected variables, handling of missing values, grouping/filtering choices, and visualization type. When a chart supports an inferential statement, the associated model, estimand, uncertainty method, and assumptions must be reported separately.

## References

[1] [Plotly Express documentation](https://plotly.com/python/plotly-express/)

[2] [Seaborn documentation](https://seaborn.pydata.org/)

[3] [ggplot2 documentation](https://ggplot2.tidyverse.org/)
