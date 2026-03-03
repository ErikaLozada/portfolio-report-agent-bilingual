"""
Assign displayFolder to every measure in _Measures.tmdl.
Measures are categorised into meaningful folders; unused measures go to saveForDeletion.
"""
import re, pathlib, shutil

TMDL = pathlib.Path(
    r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio"
    r"\PBIP-PortfolioReport\Portfolio Report.SemanticModel"
    r"\definition\tables\_Measures.tmdl"
)

FOLDER_MAP: dict[str, str] = {
    # ── Core KPIs ──
    "Total Sites":                  "Core KPIs",
    "Sites Leased":                 "Core KPIs",
    "Sites Owned":                  "Core KPIs",
    "Sites Leased %":               "Core KPIs",
    "Sites Owned %":                "Core KPIs",
    "Total Area (sqm)":             "Core KPIs",
    "Total Headcount":              "Core KPIs",
    "Total Capacity":               "Core KPIs",
    "Average Utilization Rate":     "Core KPIs",
    "Expiring <=36 Months":         "Core KPIs",
    "Count of strategic countries":  "Core KPIs",
    "Sites Leased with Area Data":  "Core KPIs",
    "Underutilized Properties Count": "Core KPIs",

    # ── Currency & Cost ──
    "Total Annual Rent (SAR)":           "Currency & Cost",
    "Total Annual Rent (USD)":           "Currency & Cost",
    "Total Annual Rent":                 "Currency & Cost",
    "Total Annual Rent with Area (SAR)": "Currency & Cost",
    "Total Annual Rent with Area(USD)":  "Currency & Cost",
    "Total Annual Rent with area":       "Currency & Cost",
    "Total Leased Area (m2)":            "Currency & Cost",
    "Total Owned Area (m2)":             "Currency & Cost",
    "Total Acquisition Cost":            "Currency & Cost",
    "Total Adquisition Cost (SAR)":      "Currency & Cost",
    "Total Acquisition Cost (USD)":      "Currency & Cost",
    "Total Cost":                        "Currency & Cost",
    "Net Rent to Area Ratio ($/sqm)":    "Currency & Cost",

    # ── Expiring & Lease ──
    "Upcoming Total Rent Lease Ending < 3 yrs": "Expiring & Lease",
    "Upcoming End of Leases Total Area (sqm)":  "Expiring & Lease",
    "CF Rent at Risk":                          "Expiring & Lease",

    # ── Quadrant Analysis (used measures only) ──
    "Global Median Area":                     "Quadrant Analysis",
    "Global Median Annual Rent":              "Quadrant Analysis",
    "Quadrant 1 - High Area, High Rent":      "Quadrant Analysis",

    # ── Distribution (keep existing – all are transitive deps) ──
    "Median Rent to Area Ratio":  "Distribution",
    "Median Annual Rent":         "Distribution",
    "Median Area":                "Distribution",
    "Q1 Rent to Area Ratio":      "Distribution",
    "Q3 Rent to Area Ratio":      "Distribution",
    "IQR Rent to Area Ratio":     "Distribution",
    "Min Rent to Area Ratio":     "Distribution",
    "Max Rent to Area Ratio":     "Distribution",
    "Q1 Annual Rent":             "Distribution",
    "Q3 Annual Rent":             "Distribution",
    "IQR Annual Rent":            "Distribution",
    "Q1 Area":                    "Distribution",
    "Q3 Area":                    "Distribution",
    "IQR Area":                   "Distribution",
    "Max Annual Rent":            "Distribution",
    "Max Area":                   "Distribution",
    "Min Area":                   "Distribution",
    "Min Annual Rent":            "Distribution",

    # ── Visual Titles ──
    "Visual Title - Expiring Metric":              "Visual Titles",
    "Visual Title - Expiring Metric running Total": "Visual Titles",
    "Button - Info":                                "Visual Titles",
    "Footer":                                       "Visual Titles",

    # ── Bilingual ──
    "Selected Language": "Bilingual",

    # ── saveForDeletion (not used in any visual, filter, label, or DAX chain) ──
    "Sharing Ratio":                              "saveForDeletion",
    "Total Area at Risk (sqm)":                   "saveForDeletion",
    "Expired Leases Count":                       "saveForDeletion",
    "Expired Leases Total Rent":                  "saveForDeletion",
    "Expired Leases Total Area (sqm)":            "saveForDeletion",
    "Net Rent to Area Ratio (USD/sqm)":           "saveForDeletion",
    "Net Rent to Area Ratio (SAR/sqm)":           "saveForDeletion",
    "Total Rent at Risk (USD)":                   "saveForDeletion",
    "Total Rent at Risk (SAR)":                   "saveForDeletion",
    "Expired Leases Total Rent (USD)":            "saveForDeletion",
    "Average Rent to Area Ratio":                 "saveForDeletion",
    "Rent to Area Ratio Std Dev":                 "saveForDeletion",
    "Outlier Threshold High":                     "saveForDeletion",
    "Outlier Threshold Low":                      "saveForDeletion",
    "Properties Above 20% Variance":              "saveForDeletion",
    "Outlier Properties Count":                   "saveForDeletion",
    "Properties Above Median Rent":               "saveForDeletion",
    "Properties Above Median Area":               "saveForDeletion",
    "Properties Above Both Medians":              "saveForDeletion",
    "Properties in Low Ratio Bucket":             "saveForDeletion",
    "Properties in High Ratio Bucket":            "saveForDeletion",
    "Properties Above Median Rent by Continent":  "saveForDeletion",
    "Properties Above Median Area by Continent":  "saveForDeletion",
    "Properties Above Both Medians by Continent": "saveForDeletion",
    "Average Rent to Area Ratio by Continent":    "saveForDeletion",
    "Median Rent to Area Ratio by Continent":     "saveForDeletion",
    "Min Rent to Area Ratio by Continent":        "saveForDeletion",
    "Max Rent to Area Ratio by Continent":        "saveForDeletion",
    "Property Count by Continent":                "saveForDeletion",
    "Q1 Rent to Area Ratio by Continent":         "saveForDeletion",
    "Q3 Rent to Area Ratio by Continent":         "saveForDeletion",
    "IQR Rent to Area Ratio by Continent":        "saveForDeletion",
    "Quadrant 2 - Low Area, High Rent":           "saveForDeletion",
    "Quadrant 3 - Low Area, Low Rent":            "saveForDeletion",
    "Quadrant 4 - High Area, Low Rent":           "saveForDeletion",
    "Total Properties in Quadrant Analysis":      "saveForDeletion",
    "Quadrant 1 - % of Total":                    "saveForDeletion",
    "Quadrant 2 - % of Total":                    "saveForDeletion",
    "Quadrant 3 - % of Total":                    "saveForDeletion",
    "Quadrant 4 - % of Total":                    "saveForDeletion",
    "Portfolio Efficiency Score":                  "saveForDeletion",
    "Properties with Missing Rent/Acquisition Data": "saveForDeletion",
    "Properties with Missing Area Data":          "saveForDeletion",
    "Average Rent per Sqm by Property Type":      "saveForDeletion",
    "ROI on Owned Properties":                    "saveForDeletion",
    "Properties in Poor Condition":               "saveForDeletion",
    "Potential Rent Recovery (Underutilized)":     "saveForDeletion",
    "Portfolio Health Score":                      "saveForDeletion",
    "Data Completeness %":                         "saveForDeletion",
    "Properties by Country":                       "saveForDeletion",
    "Total Area by Country":                       "saveForDeletion",
    "Total Annual Rent by Country":                "saveForDeletion",
    "Avg Rent per Sqm by Country":                 "saveForDeletion",
    "Avg Utilization by Country":                  "saveForDeletion",
    "Leased Properties by Country":                "saveForDeletion",
    "Owned Properties by Country":                 "saveForDeletion",
    "Allocated Properties by Country":             "saveForDeletion",
    "Poor Condition by Country":                   "saveForDeletion",
    "Underutilized by Country":                    "saveForDeletion",
    "Portfolio Health Score by Country":            "saveForDeletion",
    "Properties Expiring by Country":              "saveForDeletion",
    "Properties with Area and Cost Data":          "saveForDeletion",
    "Properties with Missing Area and Cost":       "saveForDeletion",
    "Upcoming Renewal Sites":                      "saveForDeletion",
    "detail Rank":                                 "saveForDeletion",
}

# Label measures all stay in their current Labels / Labels\KPI folders.
# They are not in the map because we leave them untouched.


def run():
    backup = TMDL.with_suffix(".tmdl.bak")
    shutil.copy2(TMDL, backup)
    print(f"Backup -> {backup}")

    text = TMDL.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Parse measure names and their line ranges
    measure_re = re.compile(r"^\tmeasure '(.+?)' =")
    measures: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = measure_re.match(line)
        if m:
            measures.append((m.group(1), i))

    stats = {"added": 0, "changed": 0, "kept": 0, "skipped_label": 0}

    for idx, (name, start_line) in enumerate(measures):
        end_line = measures[idx + 1][0] if idx + 1 < len(measures) else None
        end_idx = measures[idx + 1][1] if idx + 1 < len(measures) else len(lines)

        # Find lineageTag line for this measure
        lineage_idx = None
        existing_folder_idx = None
        for j in range(start_line, end_idx):
            if lines[j].strip().startswith("lineageTag:"):
                lineage_idx = j
            if lines[j].strip().startswith("displayFolder:"):
                existing_folder_idx = j

        if name.startswith("Label -"):
            stats["skipped_label"] += 1
            continue

        target_folder = FOLDER_MAP.get(name)
        if target_folder is None:
            print(f"  WARNING: No folder mapping for '{name}' – skipping")
            continue

        if existing_folder_idx is not None:
            current = lines[existing_folder_idx].strip()
            current_folder = current.split(":", 1)[1].strip()
            if current_folder == target_folder:
                stats["kept"] += 1
            else:
                indent = "\t\t"
                lines[existing_folder_idx] = f"{indent}displayFolder: {target_folder}"
                stats["changed"] += 1
                print(f"  CHANGED '{name}': {current_folder} -> {target_folder}")
        else:
            if lineage_idx is not None:
                indent = "\t\t"
                lines.insert(lineage_idx, f"{indent}displayFolder: {target_folder}")
                # Shift all subsequent indices
                for k in range(idx + 1, len(measures)):
                    measures[k] = (measures[k][0], measures[k][1] + 1)
                end_idx += 1
                stats["added"] += 1
                print(f"  ADDED   '{name}': -> {target_folder}")
            else:
                print(f"  WARNING: No lineageTag for '{name}' – skipping")

    result = "\n".join(lines)
    TMDL.write_text(result, encoding="utf-8")

    print(f"\nDone: {stats['added']} added, {stats['changed']} changed, "
          f"{stats['kept']} kept, {stats['skipped_label']} labels skipped")


if __name__ == "__main__":
    run()
