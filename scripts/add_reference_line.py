"""Add y1AxisReferenceLine (zero line) to all RTL bar charts that are missing it."""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PAGES_DIR = Path(
    r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio"
    r"\PBIP-PortfolioReport\Portfolio Report.Report\definition\pages"
)

RTL_PAGES = {
    "9901ef1bd1854b738da4",
    "665677beaa724871b7a8",
    "a807f88b4f3d4ce39fcc",
    "9369177f48414d41a95f",
    "01808cd02ce34c308d6c",
    "17b97c85e6f84edf87cf",
    "0c4bdf54206c4d10ae7b",
}

BAR_TYPES = {
    "barChart", "clusteredBarChart", "stackedBarChart",
    "hundredPercentStackedBarChart",
}

REFERENCE_LINE = [
    {
        "properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "displayName": {"expr": {"Literal": {"Value": "'X-Axis Constant Line 1'"}}},
            "lineColor": {
                "solid": {
                    "color": {
                        "expr": {
                            "ThemeDataColor": {"ColorId": 1, "Percent": 0.6}
                        }
                    }
                }
            },
            "transparency": {"expr": {"Literal": {"Value": "0D"}}},
            "style": {"expr": {"Literal": {"Value": "'solid'"}}},
            "width": {"expr": {"Literal": {"Value": "1D"}}},
        },
        "selector": {"id": "1"},
    }
]


def process_visual(vj_path: Path) -> bool:
    with open(vj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    visual = data.get("visual", {})
    vtype = visual.get("visualType", "")
    if vtype not in BAR_TYPES:
        return False

    objects = visual.get("objects", {})
    if "y1AxisReferenceLine" in objects:
        return False

    objects["y1AxisReferenceLine"] = REFERENCE_LINE
    visual["objects"] = objects

    with open(vj_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def main():
    total = 0
    for page_dir in sorted(PAGES_DIR.iterdir()):
        if not page_dir.is_dir() or page_dir.name not in RTL_PAGES:
            continue
        visuals_dir = page_dir / "visuals"
        if not visuals_dir.exists():
            continue
        for vis_dir in sorted(visuals_dir.iterdir()):
            vj = vis_dir / "visual.json"
            if not vj.exists():
                continue
            if process_visual(vj):
                total += 1
                print(f"  Added: {page_dir.name}/{vis_dir.name}")

    print(f"\nTotal visuals updated: {total}")


if __name__ == "__main__":
    main()
