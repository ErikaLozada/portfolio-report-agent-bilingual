import json
from pathlib import Path

BASE = Path(r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio\PBIP-PortfolioReport")
REPORT = BASE / "Portfolio Report.Report" / "definition" / "pages"

CARD_VISUALS = [
    REPORT / "9901ef1bd1854b738da4" / "visuals" / "81ff5745395cdc6d0b19" / "visual.json",  # Overview
    REPORT / "665677beaa724871b7a8" / "visuals" / "1ed1c40028b382ed150c" / "visual.json",  # Lease Expiry
    REPORT / "a807f88b4f3d4ce39fcc" / "visuals" / "1381f3110771e070c404" / "visual.json",  # Owned
    REPORT / "9369177f48414d41a95f" / "visuals" / "64382bb6b8b8911b047b" / "visual.json",  # Distribution
    REPORT / "0c4bdf54206c4d10ae7b" / "visuals" / "9b4d5f277090c0100e1e" / "visual.json",  # Data Quality
]

NATIVE_QUERY_REF_MAP = {
    "Total Sites": "إجمالي المواقع",
    "Sites Leased": "مواقع مؤجرة",
    "Sites Owned": "مواقع مملوكة",
    "Total Area (sqm)": "إجمالي المساحة (م²)",
    "Total Leased Area (Sqm)": "إجمالي المساحة المؤجرة (م²)",
    "Total Annual Rent": "إجمالي الإيجار السنوي",
    "Total Acquisition Cost": "إجمالي تكلفة الاستحواذ",
    "Total Headcount": "إجمالي عدد الموظفين",
    "Total Capacity": "إجمالي السعة",
    "Average Utilization Rate": "متوسط معدل الاستخدام",
    "Expiring <=36 Months": "تنتهي خلال ≤36 شهراً",
    "Net Rent to Area Ratio ($/sqm)": "صافي نسبة الإيجار إلى المساحة (دولار/م²)",
    "Upcoming Total Rent Lease Ending < 3 yrs": "إجمالي الإيجار القادم لعقود تنتهي < 3 سنوات",
    "Upcoming End of Leases Total Area (sqm)": "إجمالي مساحة العقود المنتهية القادمة (م²)",
    "Underutilized Properties Count": "عدد العقارات غير المستغلة",
    "Properties with Missing Rent/Acquisition Data": "عقارات بدون بيانات إيجار/استحواذ",
    "Properties with Missing Area Data": "عقارات بدون بيانات مساحة",
    "Data Completeness %": "نسبة اكتمال البيانات %",
    "Properties with Area and Cost Data": "عقارات ببيانات مساحة وتكلفة",
    "Properties with Missing Area and Cost": "عقارات بدون بيانات مساحة وتكلفة",
}

MEASURE_REF_TEMPLATE = {
    "expr": {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": "_Measures"}},
            "Property": None
        }
    }
}

TITLE_TEXT_TO_MEASURE = {
    "'with Area (sqm)'": "Label - With Area SQM",
    "' with area (sqm)'": "Label - With Area SQM",
    "'Rent to Area Ratio ($/sqm)'": "Label - Rent to Area Ratio SQM",
}


def replace_native_query_refs(data):
    """Recursively find and replace nativeQueryRef values in projections."""
    count = 0
    if isinstance(data, dict):
        if "nativeQueryRef" in data and data["nativeQueryRef"] in NATIVE_QUERY_REF_MAP:
            old = data["nativeQueryRef"]
            data["nativeQueryRef"] = NATIVE_QUERY_REF_MAP[old]
            count += 1
        for v in data.values():
            count += replace_native_query_refs(v)
    elif isinstance(data, list):
        for item in data:
            count += replace_native_query_refs(item)
    return count


def replace_title_text_literals(data):
    """Replace titleText Literal values with Measure references."""
    count = 0
    if isinstance(data, dict):
        if "titleText" in data:
            tt = data["titleText"]
            if isinstance(tt, dict) and "expr" in tt and "Literal" in tt["expr"]:
                val = tt["expr"]["Literal"]["Value"]
                if val in TITLE_TEXT_TO_MEASURE:
                    measure_name = TITLE_TEXT_TO_MEASURE[val]
                    ref = json.loads(json.dumps(MEASURE_REF_TEMPLATE))
                    ref["expr"]["Measure"]["Property"] = measure_name
                    data["titleText"] = ref
                    count += 1
        for v in data.values():
            count += replace_title_text_literals(v)
    elif isinstance(data, list):
        for item in data:
            count += replace_title_text_literals(item)
    return count


def main():
    total_nqr = 0
    total_tt = 0
    for path in CARD_VISUALS:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        nqr = replace_native_query_refs(data)
        tt = replace_title_text_literals(data)
        total_nqr += nqr
        total_tt += tt

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print(f"{path.parent.parent.parent.name}: {nqr} nativeQueryRef replaced, {tt} titleText replaced")

    print(f"\nTotal: {total_nqr} nativeQueryRef, {total_tt} titleText replacements")


if __name__ == "__main__":
    main()
