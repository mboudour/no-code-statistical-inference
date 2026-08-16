"""Build metadata cards for every bundled seminar dataset.

The cards provide auditable local metadata while directing users to upstream
Rdatasets documentation for original collection, attribution, and licensing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "public"
MANIFEST_PATH = PROJECT_DIR / "data" / "module_manifest.json"
OUTPUT_PATH = PROJECT_DIR / "data" / "dataset_catalog.json"
SOURCE = "Rdatasets public archive; consult upstream package documentation for original collection and attribution."
SOURCE_URL = "https://vincentarelbundock.github.io/Rdatasets/datasets.html"


def inferred_type(series: pd.Series) -> str:
    values = series.dropna()
    if pd.api.types.is_numeric_dtype(series):
        if values.nunique() <= 2:
            return "binary numeric"
        if values.nunique() <= 12 and (values % 1 == 0).all():
            return "discrete numeric"
        return "continuous / numeric"
    return "binary categorical" if values.nunique() <= 2 else "categorical"


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    names: dict[str, str] = {}
    modules_for_file: dict[str, list[str]] = {}
    for day in manifest["days"]:
        for module in day["modules"]:
            for item in [module["demonstration"], *module["byod"]]:
                names[item["file"]] = item["name"]
                modules_for_file.setdefault(item["file"], []).append(module["id"].upper())
    catalog: dict[str, dict] = {}
    for path in sorted(DATA_DIR.glob("*.csv")):
        data = pd.read_csv(path).drop(columns="rownames", errors="ignore")
        variables = []
        for column in data.columns:
            series = data[column]
            variables.append({
                "name": column,
                "inferred_type": inferred_type(series),
                "missing_values": int(series.isna().sum()),
                "distinct_values": int(series.nunique(dropna=True)),
                "description": "Local CSV column; confirm substantive meaning in the upstream dataset documentation.",
            })
        catalog[path.name] = {
            "name": names.get(path.name, path.stem.replace("_", " ").title()),
            "source": SOURCE,
            "source_url": SOURCE_URL,
            "license": "Consult the upstream original dataset/package documentation before use outside classroom demonstration.",
            "unit_of_observation": "Not fully specified in the local CSV; participants must identify the unit from the upstream documentation before inference.",
            "known_limitations": "Teaching dataset. The CSV alone does not establish sampling frame, measurement process, target population, or causal design.",
            "rows": int(len(data)),
            "columns": int(len(data.columns)),
            "variables": variables,
            "suitable_modules": sorted(set(modules_for_file.get(path.name, []))),
        }
    OUTPUT_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote metadata cards for {len(catalog)} datasets to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
