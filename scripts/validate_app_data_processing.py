"""Validate that every bundled public CSV is readable by the app's generic data workflow."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "public"


def main() -> None:
    files = sorted(DATA_DIR.glob("*.csv"))
    assert files, "No bundled public CSV files were found."

    rows: list[dict[str, object]] = []
    for path in files:
        data = pd.read_csv(path).drop(columns="rownames", errors="ignore")
        assert not data.empty, f"{path.name} is empty."
        numeric = data.select_dtypes(include=np.number).columns.tolist()
        categorical = data.select_dtypes(exclude=np.number).columns.tolist()

        # These are the generic non-mutating steps used by the app's profile workbench.
        if numeric:
            _ = data[numeric].describe()
            _ = np.histogram(data[numeric[0]].dropna(), bins=min(30, max(5, int(np.sqrt(len(data))))) )
        if categorical:
            _ = data[categorical[0]].astype(str).value_counts(dropna=False)
        if len(numeric) >= 2:
            _ = data[numeric[:2]].dropna()

        rows.append(
            {
                "file": path.name,
                "rows": len(data),
                "columns": len(data.columns),
                "numeric_columns": len(numeric),
                "categorical_columns": len(categorical),
            }
        )

    report = pd.DataFrame(rows)
    assert len(report) == len(files)
    print(f"Processed {len(files)} bundled public CSV datasets through the generic app workbench checks.")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
