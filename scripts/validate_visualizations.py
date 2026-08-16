"""Smoke-test the public-data visualization paths used by the Streamlit app."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "public"


def main() -> None:
    files = sorted(DATA_DIR.glob("*.csv"))
    assert files, "No public CSV files found."
    charts = 0
    for path in files:
        data = pd.read_csv(path).drop(columns="rownames", errors="ignore")
        numeric = data.select_dtypes(include=np.number).columns.tolist()
        categorical = data.select_dtypes(exclude=np.number).columns.tolist()
        if numeric:
            variable = numeric[0]
            _ = px.histogram(data, x=variable, marginal="box")
            _ = px.box(data, y=variable, points="outliers")
            figure, axis = plt.subplots(figsize=(4, 3))
            sns.histplot(data=data, x=variable, ax=axis)
            plt.close(figure)
            charts += 3
        if categorical:
            variable = categorical[0]
            counts = data[variable].astype(str).value_counts().rename_axis(variable).reset_index(name="count")
            _ = px.bar(counts, x=variable, y="count")
            charts += 1
        if numeric and categorical:
            outcome, group = numeric[0], categorical[0]
            subset = data[[outcome, group]].dropna().copy()
            if not subset.empty:
                subset[group] = subset[group].astype(str)
                _ = px.box(subset, x=group, y=outcome, points="outliers")
                figure, axis = plt.subplots(figsize=(4, 3))
                sns.boxplot(data=subset, x=group, y=outcome, ax=axis)
                plt.close(figure)
                charts += 2
        if len(categorical) >= 2:
            table = pd.crosstab(data[categorical[0]].astype(str), data[categorical[1]].astype(str))
            _ = px.imshow(table)
            charts += 1
    print(f"Validated {charts} Plotly and Seaborn/Matplotlib chart constructions across {len(files)} public datasets.")


if __name__ == "__main__":
    main()
