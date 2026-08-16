"""Validate the seminar module manifest and locally bundled public datasets."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_DIR / "data" / "module_manifest.json"
DATA_DIR = PROJECT_DIR / "data" / "public"


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = manifest["days"]
    assert len(days) == 3, "The curriculum must contain three days."

    modules = [module for day in days for module in day["modules"]]
    assert len(modules) == 9, "The curriculum must contain nine modules."

    verified_files: set[str] = set()
    for day in days:
        assert len(day["modules"]) == 3, f"{day['title']} must contain three modules."
        for module in day["modules"]:
            assert module["presentation_focus"], f"{module['id']} lacks a presentation focus."
            assert module["notation"], f"{module['id']} lacks formal notation."
            assert module["results"], f"{module['id']} lacks stated results."
            assert module["worked_example"], f"{module['id']} lacks a worked example."
            assert 3 <= len(module["byod"]) <= 5, f"{module['id']} must have 3–5 BYOD datasets."
            files = [module["worked_example"]["file"], *[entry["file"] for entry in module["byod"]]]
            for filename in files:
                path = DATA_DIR / filename
                assert path.exists(), f"Missing required data file: {filename}"
                data = pd.read_csv(path)
                assert not data.empty, f"Dataset is empty: {filename}"
                verified_files.add(filename)

    print(f"Validated {len(days)} days, {len(modules)} modules, and {len(verified_files)} referenced public datasets.")


if __name__ == "__main__":
    main()
