"""
Bind visual titles/subtitles to label measures and duplicate pages for RTL layout.

Steps performed:
1. Replace static Literal title/subtitle text in visualContainerObjects with measure references
2. Duplicate all 7 pages into RTL variants with mirrored horizontal positions
3. On RTL pages, replace textbox content with Arabic equivalents
4. Set Language filter on LTR pages to EN, RTL pages to AR
5. Update pages.json with the full 14-page order
"""
import json
import os
import shutil
import uuid
from pathlib import Path

REPORT_DIR = Path(r"c:\Users\erika.lozada\OneDrive - JLL\Documents\KSA\Porfolio\PBIP-PortfolioReport")
PAGES_DIR = REPORT_DIR / "Portfolio Report.Report" / "definition" / "pages"
PAGE_WIDTH = 1920
PAGE_HEIGHT = 1080

TITLE_TEXT_TO_MEASURE: dict[str, str] = {
    "'KPIs'": "Label - KPIs",
    "'Filter Panel'": "Label - Filter Panel",
    "'Cost and Area Detail'": "Label - Cost and Area Detail",
    "'Rent to Area Ratio Distribution'": "Label - Rent to Area Distribution",
    "'Rent v Area by Region '": "Label - Rent v Area by Region",
    "'Rent to Area Ratio by Region'": "Label - Rent to Area by Region",
    "'Filters'": "Label - Button Filters",
    "'Filters ON'": "Label - Filters ON",
    "'Filters OFF'": "Label - Filters OFF",
    "'info'": "Button - Info",
    "'Upcoming Lease Renewals (< 3 years)'": "Label - Upcoming Lease Renewals",
}

SUBTITLE_TEXT_TO_MEASURE: dict[str, str] = {
    "'Each bubble represent a property. Hover for more details.'": "Label - Bubble Property Hover",
    "'Excludes properties with missing area m2. Each bubble represent a property. Hover for more details.'": "Label - Rent Area Excludes M2",
    "'(Number of strategic countries)'": "Label - Strategic Countries",
    "'All properties with no area or rent information are excluded in this report.'": "Label - Cost Area Exclusion",
    "'(Number of Sites)'": "Label - Number of Sites",
    "'Rent to Area Ratio ($/sqm)'": "Label - Rent to Area Ratio SQM",
}

TEXTBOX_EN_TO_AR: dict[str, str] = {
    "Portfolio Strategy | Overview": "استراتيجية المحفظة | نظرة عامة",
    "Portfolio Strategy | Distribution": "استراتيجية المحفظة | التوزيع",
    "Portfolio Strategy | Property Information": "استراتيجية المحفظة | معلومات العقار",
    "Portfolio Strategy | Owned": "استراتيجية المحفظة | المملوكة",
    "Portfolio Strategy | Lease Expiring": "استراتيجية المحفظة | انتهاء الإيجار",
    "Filters": "التصفية",
    "Expiring Year Range:": "نطاق سنة الانتهاء:",
    "  Dimension Filter:": "  تصفية البعد:",
    "  Metric Filter:": "  تصفية المقياس:",
    "Portfolio Strategy Report": "تقرير استراتيجية المحفظة",
    "Description | MoFA portfolio": "الوصف | محفظة وزارة الخارجية",
    "Data Source(s) and Data Refresh Schedules(s) | Dummy data (csv)": "مصادر البيانات وجداول التحديث | بيانات تجريبية (csv)",
    "Current Version Create By | Erika Lozada": "النسخة الحالية من إعداد | إريكا لوزادا",
    "Dashboard Business Owner |": "مالك لوحة المعلومات |",
}

PAGE_ORDER = [
    "a94a0faa68953005c758",
    "fb2af5ee013969b10d97",
    "7bf3b52072bc0010dc4c",
    "2e769a070bd14019d45b",
    "bbd89d7022b1b0b40b43",
    "a355a9de5d8b8a070096",
    "6b069f6587ebdd241049",
]

PAGE_DISPLAY_NAMES = {
    "a94a0faa68953005c758": "Portfolio Overview",
    "fb2af5ee013969b10d97": "Expiring",
    "7bf3b52072bc0010dc4c": "Owned",
    "2e769a070bd14019d45b": "Distribution",
    "bbd89d7022b1b0b40b43": "Property Info",
    "a355a9de5d8b8a070096": "info",
    "6b069f6587ebdd241049": "Page 1",
}

RTL_DISPLAY_NAMES = {
    "a94a0faa68953005c758": "نظرة عامة على المحفظة",
    "fb2af5ee013969b10d97": "انتهاء الإيجار",
    "7bf3b52072bc0010dc4c": "المملوكة",
    "2e769a070bd14019d45b": "التوزيع",
    "bbd89d7022b1b0b40b43": "معلومات العقار",
    "a355a9de5d8b8a070096": "معلومات",
    "6b069f6587ebdd241049": "الصفحة 1",
}


def make_measure_ref(measure_name: str) -> dict:
    return {
        "expr": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "_Measures"}},
                "Property": measure_name,
            }
        }
    }


def make_page_id() -> str:
    return uuid.uuid4().hex[:20]


def replace_title_subtitle_with_measures(visual: dict) -> int:
    """Replace static Literal title/subtitle text with measure references. Returns count of replacements."""
    count = 0
    vco = visual.get("visual", {}).get("visualContainerObjects", {})

    for section_key, mapping in [("title", TITLE_TEXT_TO_MEASURE), ("subTitle", SUBTITLE_TEXT_TO_MEASURE)]:
        items = vco.get(section_key, [])
        for item in items:
            props = item.get("properties", {})
            text_node = props.get("text", {})
            literal = text_node.get("expr", {}).get("Literal", {})
            val = literal.get("Value", "")
            if val in mapping:
                props["text"] = make_measure_ref(mapping[val])
                count += 1

    return count


def mirror_position(pos: dict) -> dict:
    """Mirror a visual's horizontal position for RTL layout."""
    x = pos.get("x", 0)
    w = pos.get("width", 0)
    new_x = PAGE_WIDTH - x - w
    if new_x < 0:
        new_x = 0
    return {**pos, "x": new_x}


def translate_textbox_runs(visual: dict) -> int:
    """For RTL pages, replace English textbox runs with Arabic equivalents."""
    count = 0
    vtype = visual.get("visual", {}).get("visualType", "")
    if vtype != "textbox":
        return 0

    config = visual.get("visual", {}).get("objects", {})
    paragraphs_list = config.get("general", [])
    for general_item in paragraphs_list:
        props = general_item.get("properties", {})
        paragraphs = props.get("paragraphs", [])
        for para in paragraphs:
            for text_run in para.get("textRuns", []):
                en_val = text_run.get("value", "")
                if en_val in TEXTBOX_EN_TO_AR:
                    text_run["value"] = TEXTBOX_EN_TO_AR[en_val]
                    count += 1
    return count


def make_language_filter(language_label: str) -> dict:
    return {
        "name": uuid.uuid4().hex[:20],
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": "Language"}},
                "Property": "Label",
            }
        },
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "l", "Entity": "Language", "Type": 0}],
            "Where": [
                {
                    "Condition": {
                        "In": {
                            "Expressions": [
                                {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "l"}},
                                        "Property": "Label",
                                    }
                                }
                            ],
                            "Values": [[{"Literal": {"Value": f"'{language_label}'"}}]],
                        }
                    }
                }
            ],
        },
        "howCreated": "User",
    }


def process_ltr_pages():
    """Step 1: On existing LTR pages, replace static titles/subtitles with measure references."""
    total = 0
    for page_id in PAGE_ORDER:
        page_dir = PAGES_DIR / page_id
        visuals_dir = page_dir / "visuals"
        if not visuals_dir.exists():
            continue
        for vis_dir in visuals_dir.iterdir():
            vj = vis_dir / "visual.json"
            if not vj.exists():
                continue
            with open(vj, "r", encoding="utf-8") as f:
                data = json.load(f)
            n = replace_title_subtitle_with_measures(data)
            if n > 0:
                with open(vj, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                total += n
    print(f"[LTR] Replaced {total} static title/subtitle texts with measure references")


def set_page_language_filter(page_dir: Path, language_label: str):
    """Set or update the language filter on a page."""
    page_json = page_dir / "page.json"
    with open(page_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_filters = data.get("filterConfig", {}).get("filters", [])
    non_lang_filters = [
        flt for flt in existing_filters
        if not (
            flt.get("field", {}).get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity") == "Language"
        )
    ]
    non_lang_filters.append(make_language_filter(language_label))
    data.setdefault("filterConfig", {})["filters"] = non_lang_filters

    with open(page_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def duplicate_pages_rtl() -> dict[str, str]:
    """Step 2: Duplicate each page with mirrored layout for RTL. Returns mapping old_id -> new_id."""
    mapping: dict[str, str] = {}
    for page_id in PAGE_ORDER:
        src = PAGES_DIR / page_id
        if not src.exists():
            print(f"  [WARN] Page {page_id} directory not found, skipping")
            continue

        new_id = make_page_id()
        dst = PAGES_DIR / new_id
        shutil.copytree(src, dst)

        page_json_path = dst / "page.json"
        with open(page_json_path, "r", encoding="utf-8") as f:
            page_data = json.load(f)
        page_data["name"] = new_id
        page_data["displayName"] = RTL_DISPLAY_NAMES.get(page_id, page_data.get("displayName", "") + " (AR)")
        with open(page_json_path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)

        visuals_dir = dst / "visuals"
        if visuals_dir.exists():
            vis_count = 0
            txt_count = 0
            for vis_dir in visuals_dir.iterdir():
                vj = vis_dir / "visual.json"
                if not vj.exists():
                    continue
                with open(vj, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "position" in data:
                    data["position"] = mirror_position(data["position"])
                    vis_count += 1

                txt_count += translate_textbox_runs(data)

                with open(vj, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  [RTL] {page_id} -> {new_id}: mirrored {vis_count} visuals, translated {txt_count} textboxes")

        set_page_language_filter(dst, "العربية")
        mapping[page_id] = new_id
    return mapping


def set_ltr_language_filters():
    """Step 3: Set English language filter on LTR pages."""
    for page_id in PAGE_ORDER:
        page_dir = PAGES_DIR / page_id
        if not page_dir.exists():
            continue
        set_page_language_filter(page_dir, "English")
    print(f"[LTR] Set English language filter on {len(PAGE_ORDER)} pages")


def update_pages_json(rtl_mapping: dict[str, str]):
    """Step 4: Update pages.json with all 14 pages (LTR first, then RTL in same order)."""
    pages_json_path = PAGES_DIR / "pages.json"
    with open(pages_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rtl_order = [rtl_mapping[pid] for pid in PAGE_ORDER if pid in rtl_mapping]
    data["pageOrder"] = PAGE_ORDER + rtl_order
    data["activePageName"] = PAGE_ORDER[0]

    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[pages.json] Updated with {len(data['pageOrder'])} pages ({len(PAGE_ORDER)} LTR + {len(rtl_order)} RTL)")
    return rtl_mapping


def add_nav_buttons(rtl_mapping: dict[str, str]):
    """Step 5: Add a language switch button to each page navigating to its LTR/RTL counterpart."""
    reverse_mapping = {v: k for k, v in rtl_mapping.items()}

    for page_id in PAGE_ORDER:
        page_dir = PAGES_DIR / page_id
        rtl_id = rtl_mapping.get(page_id)
        if not rtl_id or not page_dir.exists():
            continue
        _add_lang_button(page_dir, rtl_id, button_text_measure="Label - Button Filters",
                         label="العربية", is_rtl=False)

    for rtl_id, ltr_id in reverse_mapping.items():
        page_dir = PAGES_DIR / rtl_id
        if not page_dir.exists():
            continue
        _add_lang_button(page_dir, ltr_id, button_text_measure="Label - Button Filters",
                         label="English", is_rtl=True)

    print(f"[NAV] Added language-switch buttons to {len(rtl_mapping) * 2} pages")


def _add_lang_button(page_dir: Path, target_page_id: str, button_text_measure: str,
                     label: str, is_rtl: bool):
    """Create a small navigation button visual on the page."""
    visuals_dir = page_dir / "visuals"
    btn_id = uuid.uuid4().hex[:20]
    btn_dir = visuals_dir / btn_id
    btn_dir.mkdir(parents=True, exist_ok=True)

    x_pos = 20 if is_rtl else 1750
    button_visual = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": btn_id,
        "position": {
            "x": x_pos,
            "y": 10,
            "z": 20000,
            "height": 35,
            "width": 150,
            "tabOrder": 99000,
        },
        "visual": {
            "visualType": "actionButton",
            "drillFilterOtherVisuals": True,
            "objects": {
                "icon": [{"properties": {"shapeType": {"expr": {"Literal": {"Value": "'blank'"}}}}}],
                "outline": [{"properties": {"weight": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "fill": [
                    {
                        "properties": {
                            "fillColor": {
                                "solid": {
                                    "color": {"expr": {"Literal": {"Value": "'#E8E8E8'"}}}
                                }
                            },
                            "transparency": {"expr": {"Literal": {"Value": "20D"}}},
                        }
                    }
                ],
                "text": [
                    {
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{label}'"}}},
                            "fontFamily": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'''Segoe UI Light'', wf_segoe-ui_light, helvetica, arial, sans-serif'"
                                    }
                                }
                            },
                            "fontSize": {"expr": {"Literal": {"Value": "10D"}}},
                        }
                    }
                ],
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}},
                        }
                    }
                ],
                "background": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}},
                        }
                    }
                ],
            },
            "vcActions": [
                {
                    "name": uuid.uuid4().hex[:20],
                    "action": {
                        "PageNavigation": {
                            "DestinationExpression": {
                                "Literal": {"Value": f"'{target_page_id}'"}
                            }
                        }
                    },
                }
            ],
        },
    }

    with open(btn_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(button_visual, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("BILINGUAL PORTFOLIO REPORT: BIND & DUPLICATE")
    print("=" * 60)

    print("\n--- Step 1: Bind LTR visual titles/subtitles to measures ---")
    process_ltr_pages()

    print("\n--- Step 2: Duplicate pages for RTL layout ---")
    rtl_mapping = duplicate_pages_rtl()

    print("\n--- Step 3: Set language filters on pages ---")
    set_ltr_language_filters()

    print("\n--- Step 4: Update pages.json ---")
    update_pages_json(rtl_mapping)

    print("\n--- Step 5: Add navigation buttons ---")
    add_nav_buttons(rtl_mapping)

    print("\n--- SUMMARY ---")
    print(f"LTR pages: {len(PAGE_ORDER)}")
    print(f"RTL pages: {len(rtl_mapping)}")
    print("Mapping (LTR -> RTL):")
    for ltr, rtl in rtl_mapping.items():
        name = PAGE_DISPLAY_NAMES.get(ltr, ltr)
        rtl_name = RTL_DISPLAY_NAMES.get(ltr, name + " (AR)")
        print(f"  {name} ({ltr}) -> {rtl_name} ({rtl})")
    print("\nDone!")


if __name__ == "__main__":
    main()
