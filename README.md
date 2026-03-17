# Portfolio Report (PBIP)

Bilingual (English / Arabic) Power BI Portfolio Report with Right-to-Left (RTL) layout support, dynamic language switching, and developer documentation for maintenance.

---

## Project Summary

This report started as an English-only Power BI portfolio dashboard and was extended to support **English and Arabic** with:

- **7 LTR pages** (English) and **7 RTL pages** (Arabic) with mirrored layout
- **Language** and **Translations** tables plus **67 Label measures** for dynamic titles, subtitles, and KPI labels
- **RTL formatting** on Arabic pages: right-aligned text, switched/inverted axes on bar and scatter charts, inverted data bars on tables, zero reference lines on bar charts
- **Schema-compliant navigation** using `visualLink` / `navigationSection` (replacing deprecated `vcActions`)
- **Developer guide** and **measure display folders** (including `saveForDeletion` for unused measures)
- **Reusable visual templates** (LTR and RTL) in `templates/`

Detailed implementation summary: **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**  
Developer maintenance guide: **[docs/PORTFOLIO_REPORT_DEVELOPER_GUIDE.md](docs/PORTFOLIO_REPORT_DEVELOPER_GUIDE.md)**

---

## Folder Structure

```
PBIP-PortfolioReport/
├── .cursor/                    # Cursor rules and project config
├── .venv/                      # Python virtual environment (uv)
├── docs/                       # Documentation
│   └── PORTFOLIO_REPORT_DEVELOPER_GUIDE.md
├── Portfolio Report.Report/     # Power BI report (PBIR)
│   ├── .pbi/
│   ├── definition/
│   │   ├── bookmarks/
│   │   └── pages/              # 14 pages (7 LTR + 7 RTL), each with visuals/
│   ├── StaticResources/
├── Portfolio Report.SemanticModel/  # Semantic model (TMDL)
│   ├── .pbi/
│   ├── DAXQueries/
│   ├── definition/
│   │   ├── cultures/
│   │   ├── tables/             # Portfolio, Date, Language, Translations, _Measures, etc.
│   │   └── relationships.tmdl
│   └── diagramLayout.json
├── scripts/                    # Python automation (bilingual/RTL setup)
│   ├── main.py
│   ├── bind_and_duplicate.py
│   ├── bind_remaining.py
│   ├── verify_bilingual.py
│   ├── rtl_alignment.py
│   ├── rtl_axis_format.py
│   ├── add_reference_line.py
│   ├── translate_kpi_cards.py
│   ├── fix_nav_buttons.py
│   ├── fix_nav_buttons_v2.py
│   └── md_to_pdf.py            # PROJECT_SUMMARY.md → PDF
├── templates/                  # Reusable visual JSON templates (LTR + RTL)
├── theme/                      # Report theme assets
├── PROJECT_SUMMARY.md          # Bilingual implementation summary
├── PROJECT_SUMMARY.pdf        # Same content, PDF (generated)
└── README.md                   # This file
```

---

## Summary of Prompts and Conversations

The following summarises the main prompts and outcomes from agent/Cursor sessions used for this project.

### 1. Bilingual implementation and RTL (this repo)

- **Evaluate report pages and visuals** – Extract all translatable text (titles, subtitles, labels, headers) and add keys to the Translations table; duplicate each page into an RTL variant with Arabic display names and mirrored layout.
- **RTL layout** – Mirror visual positions horizontally on RTL pages; right-align titles, subtitles, and axis labels; apply RTL-specific formatting (bar/scatter: switch Y-axis position, invert X-axis range; matrix: invert data bar direction; add zero reference lines to bar charts).
- **Navigation and schema** – Replace invalid `vcActions` with `visualLink`, and `destinationSection` with `navigationSection`, so the `.pbip` opens without schema errors.
- **KPI card translation** – Add translation keys and Label measures for KPI names and reference labels; bind card visuals to these measures and set RTL page card labels to Arabic where appropriate.
- **Distribution page** – Bind bar/column chart titles on the RTL Distribution page (التوزيع) to `Label - Rent to Area by Region`, `Label - Strategic Countries`, and `Label - KPI Sites Owned`; fix “table of multiple values” error by **removing duplicate keys** in the Translations table (`KPI_TOTAL_SITES`, `KPI_SITES_LEASED`, `KPI_SITES_OWNED` were each defined twice).
- **Project summary and PDF** – Add PROJECT_SUMMARY.md (approach, tools, scripts, time estimate, next steps) and a Python script to generate PROJECT_SUMMARY.pdf for sharing.
- **README** – Add README.md with project summary, folder structure, and summary of prompts/conversations (this section).

### 2. Bilingual field parameter (prm_metric)

*Cursor agent transcript: `6729aa80-9edd-43e5-975d-64061f0351cf`*

- **prm_metric with Arabic and Language column** – User asked to extend the DAX table to include translated metric names and a Language column (EN/AR). A 4-column structure was proposed; implementing it broke **field parameter** behavior (Power BI expects exactly 3 columns for NAMEOF-based parameters).
- **Visual Title - Expiring Metric** – Title measure was updated to use `[Selected Language]` and a translated suffix (“ by End of Lease Date” / “ حسب تاريخ انتهاء العقد”). When the 4-column prm_metric was used, `SELECTEDVALUE(prm_metric[Field])` returned blank because the parameter no longer resolved correctly.
- **Keeping slicer bilingual vs keeping axis binding** – User needed the metric slicer to show translated names. Replacing the field parameter with a DATATABLE and a SWITCH measure would make the slicer bilingual but **break dynamic axis binding** (charts need the field parameter for the axis to switch measures).
- **Options agreed** – **(A)** Two field parameters (EN + AR) with duplicate visuals and bookmarks to toggle visibility for full bilingual slicer and axis; **(B)** Keep one field parameter (English slicer/axis), translate only titles and labels via measures (current approach in the report).

### 3. Developer documentation and measure folders

*Cursor agent transcript: `69852fa5-8533-4d1b-aa98-3e1f666805c1`*

- **Developer documentation** – User requested documentation for future developers: data model, metrics (including dependency chains and complex DAX), maintenance points, and visuals that depend on complex DAX (not about using AI for bilingual implementation).
- **Measure display folders and saveForDeletion** – Extend the plan to assign every measure to a meaningful display folder (Core KPIs, Currency & Cost, Distribution, Quadrant Analysis, Visual Titles, Labels, etc.) and to put measures **not used** in any visual, filter, label, or reference label into a folder named **saveForDeletion** for later review/removal.
- **Plan implementation** – Used report JSON and TMDL to build “used” vs “unused” measure sets (including transitive DAX dependencies), applied display folders via a Python script to `_Measures.tmdl`, and wrote **docs/PORTFOLIO_REPORT_DEVELOPER_GUIDE.md** with data model, dependency chains, folder map, saveForDeletion list, complex-DAX visuals, maintenance points, and quick reference.
- **Developer documentation skill** – User asked for a Cursor skill to write developer documentation for existing reports. A skill was added (`powerbi-developer-documentation`) that codifies the discovery → categorize → write → verify workflow used for this report.

---

## Quick Start

- **Open the report:** Open the `.pbip` folder in Power BI Desktop (Feb 2026+).
- **Data source:** Portfolio table path is in `Portfolio Report.SemanticModel/definition/tables/Portfolio.tmdl` and related expressions; update for production (see developer guide).
- **Language:** Use the Language slicer (EN/AR) to switch labels; RTL pages are the Arabic-named pages (e.g. نظرة عامة على المحفظة, التوزيع).
- **Regenerate PDF summary:** From project root, `uv run python scripts/md_to_pdf.py` (requires `.venv` and `xhtml2pdf`).

---

*Last updated: March 2026*
