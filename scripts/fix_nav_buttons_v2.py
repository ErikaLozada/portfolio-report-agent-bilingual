"""Fix navigation buttons: rename destinationSection -> navigationSection per PBIR schema."""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PAGES_DIR = Path(r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio\PBIP-PortfolioReport\Portfolio Report.Report\definition\pages")


def fix_visual(vj_path: Path) -> bool:
    with open(vj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vco = data.get("visual", {}).get("visualContainerObjects", {})
    vl_list = vco.get("visualLink", [])
    if not vl_list:
        return False

    changed = False
    for entry in vl_list:
        props = entry.get("properties", {})
        if "destinationSection" in props:
            props["navigationSection"] = props.pop("destinationSection")
            changed = True

    if not changed:
        return False

    with open(vj_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def main():
    fixed = 0
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
            if fix_visual(vj):
                fixed += 1
                print(f"  Fixed: {page_dir.name}/{vis_dir.name}")
    print(f"\nTotal fixed: {fixed}")


if __name__ == "__main__":
    main()
