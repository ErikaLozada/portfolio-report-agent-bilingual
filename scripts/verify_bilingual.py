"""Verify the bilingual report setup is correct."""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPORT_DIR = Path(r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio\PBIP-PortfolioReport")
PAGES_DIR = REPORT_DIR / "Portfolio Report.Report" / "definition" / "pages"

LTR_PAGES = [
    "a94a0faa68953005c758",
    "fb2af5ee013969b10d97",
    "7bf3b52072bc0010dc4c",
    "2e769a070bd14019d45b",
    "bbd89d7022b1b0b40b43",
    "a355a9de5d8b8a070096",
    "6b069f6587ebdd241049",
    "f1a2b3c4d5e6f7081920",
    "a2b3c4d5e6f70819202a",
]

def check_pages_json():
    with open(PAGES_DIR / "pages.json", encoding="utf-8") as f:
        data = json.load(f)
    order = data["pageOrder"]
    print(f"pages.json has {len(order)} pages")
    assert len(order) == 18, f"Expected 18 pages, got {len(order)}"
    for pid in LTR_PAGES:
        assert pid in order, f"LTR page {pid} missing from pageOrder"
    rtl_pages = [p for p in order if p not in LTR_PAGES]
    print(f"  LTR: {len(LTR_PAGES)}, RTL: {len(rtl_pages)}")
    return rtl_pages


def check_page_filters(page_ids, expected_label, label_name):
    ok = 0
    for pid in page_ids:
        page_json = PAGES_DIR / pid / "page.json"
        with open(page_json, encoding="utf-8") as f:
            data = json.load(f)
        filters = data.get("filterConfig", {}).get("filters", [])
        lang_filters = [
            f for f in filters
            if f.get("field", {}).get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity") == "Language"
        ]
        if not lang_filters:
            print(f"  FAIL: {pid} ({data.get('displayName')}) has no Language filter")
            continue
        val = lang_filters[0]["filter"]["Where"][0]["Condition"]["In"]["Values"][0][0]["Literal"]["Value"]
        if val == f"'{expected_label}'":
            ok += 1
        else:
            print(f"  WARN: {pid} ({data.get('displayName')}) filter is {val}, expected '{expected_label}'")
    print(f"  {label_name} pages with correct Language filter: {ok}/{len(page_ids)}")


def check_rtl_display_names(rtl_pages):
    for pid in rtl_pages:
        page_json = PAGES_DIR / pid / "page.json"
        with open(page_json, encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("displayName", "")
        has_arabic = any("\u0600" <= c <= "\u06FF" for c in name)
        if has_arabic:
            print(f"  OK: {pid} -> {name}")
        else:
            print(f"  WARN: {pid} -> {name} (no Arabic characters)")


def check_nav_buttons(page_ids, direction):
    found = 0
    for pid in page_ids:
        visuals_dir = PAGES_DIR / pid / "visuals"
        if not visuals_dir.exists():
            continue
        for vdir in visuals_dir.iterdir():
            vj = vdir / "visual.json"
            if not vj.exists():
                continue
            with open(vj, encoding="utf-8") as f:
                data = json.load(f)
            actions = data.get("visual", {}).get("vcActions", [])
            if actions:
                dest = actions[0].get("action", {}).get("PageNavigation", {}).get("DestinationExpression", {}).get("Literal", {}).get("Value", "")
                if dest:
                    found += 1
                    break
    print(f"  {direction} pages with nav button: {found}/{len(page_ids)}")


def check_measure_bindings():
    """Count visuals that have title/subtitle bound to measures (not Literals)."""
    measure_bound = 0
    literal_titles = []
    for page_dir in PAGES_DIR.iterdir():
        if not page_dir.is_dir() or page_dir.name == "pages.json":
            continue
        visuals_dir = page_dir / "visuals"
        if not visuals_dir.exists():
            continue
        for vdir in visuals_dir.iterdir():
            vj = vdir / "visual.json"
            if not vj.exists():
                continue
            with open(vj, encoding="utf-8") as f:
                data = json.load(f)
            vco = data.get("visual", {}).get("visualContainerObjects", {})
            for key in ["title", "subTitle"]:
                for item in vco.get(key, []):
                    text = item.get("properties", {}).get("text", {})
                    expr = text.get("expr", {})
                    if "Measure" in expr:
                        measure_bound += 1
                    elif "Literal" in expr:
                        val = expr["Literal"].get("Value", "")
                        if val and val not in ("true", "false") and not val.endswith("D"):
                            literal_titles.append(f"{page_dir.name}/{vdir.name}: {key}={val}")
    print(f"  Measure-bound title/subtitle: {measure_bound}")
    if literal_titles:
        print(f"  Remaining Literal titles/subtitles ({len(literal_titles)}):")
        for t in literal_titles[:10]:
            print(f"    {t}")


def main():
    print("=" * 60)
    print("BILINGUAL REPORT VERIFICATION")
    print("=" * 60)

    print("\n1. Pages count and order:")
    rtl_pages = check_pages_json()

    print("\n2. LTR page Language filters (should be English):")
    check_page_filters(LTR_PAGES, "English", "LTR")

    print("\n3. RTL page Language filters (should be العربية):")
    check_page_filters(rtl_pages, "العربية", "RTL")

    print("\n4. RTL display names (should be Arabic):")
    check_rtl_display_names(rtl_pages)

    print("\n5. Navigation buttons:")
    check_nav_buttons(LTR_PAGES, "LTR")
    check_nav_buttons(rtl_pages, "RTL")

    print("\n6. Measure bindings (title/subtitle):")
    check_measure_bindings()

    print("\nVerification complete!")


if __name__ == "__main__":
    main()
