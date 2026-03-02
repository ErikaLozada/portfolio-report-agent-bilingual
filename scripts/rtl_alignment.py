"""Right-align titles, subtitles, and textbox paragraphs on all RTL page visuals."""
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

RIGHT_ALIGN_EXPR = {"expr": {"Literal": {"Value": "'right'"}}}


def set_alignment_on_object(vco: dict, obj_name: str) -> bool:
    """Add alignment: right to a visualContainerObjects entry (title/subtitle)."""
    obj_list = vco.get(obj_name)
    if not obj_list:
        return False
    changed = False
    for entry in obj_list:
        props = entry.get("properties", {})
        if props.get("alignment") != RIGHT_ALIGN_EXPR:
            props["alignment"] = RIGHT_ALIGN_EXPR
            entry["properties"] = props
            changed = True
    return changed


def right_align_textbox(visual_obj: dict) -> bool:
    """Set paragraph alignment to right for textbox visuals."""
    if visual_obj.get("visualType") != "textbox":
        return False
    general_list = visual_obj.get("objects", {}).get("general", [])
    if not general_list:
        return False
    changed = False
    for entry in general_list:
        paragraphs = entry.get("properties", {}).get("paragraphs")
        if not paragraphs:
            continue
        for para in paragraphs:
            runs = para.get("textRuns", [])
            for run in runs:
                style = run.get("textStyle", {})
                if style.get("textAlignment") != "right":
                    style["textAlignment"] = "right"
                    run["textStyle"] = style
                    changed = True
    return changed


def process_visual(vj_path: Path) -> list[str]:
    with open(vj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    visual = data.get("visual", {})
    vco = visual.get("visualContainerObjects", {})
    changes = []

    if set_alignment_on_object(vco, "title"):
        changes.append("title")
    if set_alignment_on_object(vco, "subTitle"):
        changes.append("subTitle")
    if right_align_textbox(visual):
        changes.append("textbox")

    if changes:
        with open(vj_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return changes


def main():
    total_changed = 0
    for page_dir in sorted(PAGES_DIR.iterdir()):
        if not page_dir.is_dir():
            continue
        if page_dir.name not in RTL_PAGES:
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
                total_changed += 1
                print(f"  {page_dir.name}/{vis_dir.name}: {', '.join(changes)}")

    print(f"\nTotal visuals updated: {total_changed}")


if __name__ == "__main__":
    main()
