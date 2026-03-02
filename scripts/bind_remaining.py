"""Bind remaining literal title/subtitle texts to label measures across all pages."""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PAGES_DIR = Path(r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio\PBIP-PortfolioReport\Portfolio Report.Report\definition\pages")

TITLE_MAP = {
    "'Total Head Count'": "Label - Total Head Count",
    "'Total Capcity'": "Label - Total Capacity",
    "'Total Area'": "Label - Total Area Title",
    "'Total Area (m2)'": "Label - Total Area M2",
    "'Total Annual Rent '": "Label - Total Annual Rent Title",
    "'Total Building Capacity'": "Label - Total Building Capacity",
    "'Total Adquisition Cost'": "Label - Total Acquisition Cost",
    "'Number of Sites'": "Label - Number of Sites Title",
    "'Total Annual Rent for Upcoming Lease End Date '": "Label - Rent by Upcoming End",
    "'Total Area for Upcoming Lease End Date '": "Label - Area for Upcoming End",
    "'Rent and Area Detail'": "Label - Rent and Area Detail",
}

SUBTITLE_MAP = {
    "'Total Annual Rent by Upcoming End Date  (<=36 months)'": "Label - Rent by Upcoming End Subtitle",
    "'Total Annual Rent for Upcoming Lease End Date '": "Label - Rent by Upcoming End",
}

ALL_MAPS = {"title": TITLE_MAP, "subTitle": SUBTITLE_MAP}


def make_measure_ref(measure_name: str) -> dict:
    return {
        "expr": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "_Measures"}},
                "Property": measure_name,
            }
        }
    }


def main():
    total = 0
    for page_dir in PAGES_DIR.iterdir():
        if not page_dir.is_dir():
            continue
        visuals_dir = page_dir / "visuals"
        if not visuals_dir.exists():
            continue
        for vis_dir in visuals_dir.iterdir():
            vj = vis_dir / "visual.json"
            if not vj.exists():
                continue
            with open(vj, "r", encoding="utf-8") as f:
                data = json.load(f)
            changed = False
            vco = data.get("visual", {}).get("visualContainerObjects", {})
            for section_key, mapping in ALL_MAPS.items():
                for item in vco.get(section_key, []):
                    props = item.get("properties", {})
                    text_node = props.get("text", {})
                    literal = text_node.get("expr", {}).get("Literal", {})
                    val = literal.get("Value", "")
                    if val in mapping:
                        props["text"] = make_measure_ref(mapping[val])
                        changed = True
                        total += 1
                        print(f"  {page_dir.name}/{vis_dir.name}: {section_key} {val} -> {mapping[val]}")
            if changed:
                with open(vj, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nTotal replacements: {total}")


if __name__ == "__main__":
    main()
