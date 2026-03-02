"""Apply RTL axis formatting to bar charts, scatter charts, and table data bars on RTL pages."""
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

TRUE_EXPR = {"expr": {"Literal": {"Value": "true"}}}

BAR_TYPES = {"barChart", "clusteredBarChart", "stackedBarChart", "hundredPercentStackedBarChart"}
SCATTER_TYPES = {"scatterChart"}
TABLE_TYPES = {"tableEx", "pivotTable"}


def set_nested_prop(obj_dict: dict, obj_name: str, prop_name: str, value) -> bool:
    """Set a property on a visual object entry, creating the entry if needed."""
    obj_list = obj_dict.get(obj_name)
    if not obj_list:
        obj_dict[obj_name] = [{"properties": {prop_name: value}}]
        return True
    props = obj_list[0].get("properties", {})
    if props.get(prop_name) == value:
        return False
    props[prop_name] = value
    obj_list[0]["properties"] = props
    return True


def fix_bar_or_scatter(visual_obj: dict) -> list[str]:
    """Add switchAxisPosition + invertAxis for bar/scatter charts."""
    objects = visual_obj.setdefault("objects", {})
    changes = []
    if set_nested_prop(objects, "categoryAxis", "switchAxisPosition", TRUE_EXPR):
        changes.append("categoryAxis.switchAxisPosition")
    if set_nested_prop(objects, "valueAxis", "invertAxis", TRUE_EXPR):
        changes.append("valueAxis.invertAxis")
    return changes


def fix_table_databars(visual_obj: dict) -> list[str]:
    """Set reverseDirection=true on all data bar entries in columnFormatting."""
    objects = visual_obj.get("objects", {})
    col_fmt = objects.get("columnFormatting", [])
    if not col_fmt:
        return []
    changes = []
    for entry in col_fmt:
        db = entry.get("properties", {}).get("dataBars")
        if not db:
            continue
        rd = db.get("reverseDirection", {})
        current = rd.get("expr", {}).get("Literal", {}).get("Value")
        if current != "true":
            db["reverseDirection"] = TRUE_EXPR
            changes.append("dataBars.reverseDirection")
    return changes


def process_visual(vj_path: Path) -> list[str]:
    with open(vj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    visual = data.get("visual", {})
    vtype = visual.get("visualType", "")
    changes = []

    if vtype in BAR_TYPES or vtype in SCATTER_TYPES:
        changes = fix_bar_or_scatter(visual)
    elif vtype in TABLE_TYPES:
        changes = fix_table_databars(visual)

    if changes:
        with open(vj_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return changes


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
            changes = process_visual(vj)
            if changes:
                total += 1
                print(f"  {page_dir.name}/{vis_dir.name}: {', '.join(changes)}")

    print(f"\nTotal visuals updated: {total}")


if __name__ == "__main__":
    main()
