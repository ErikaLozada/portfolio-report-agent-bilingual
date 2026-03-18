# Real Estate Initiatives — Schema & Data Dictionary

> **Purpose:** Sales plan / pipeline of real estate initiatives (acquisitions, dispositions, renewals, new leases) for integration with the Portfolio Report.  
> **Audience:** Developers and report authors.  
> **Last updated:** March 2026

---

## 1. Overview

The **Real Estate Initiatives** table represents the organisation’s current sales plan: planned or in-progress deals such as new acquisitions, dispositions, lease renewals, and expansions. It is designed to:

- Align with the existing **Portfolio** model (same geography: `Country`, `Continent`).
- Support pipeline and value reporting (count by status, value by type, expected close dates).
- Work with the report’s **bilingual** setup (EN/AR) via optional name columns or via the **Translations** table for UI labels.

---

## 2. Table: Real Estate Initiatives

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| **initiative_id** | Text | Yes | Unique identifier (e.g. `INI-001`). Primary key. |
| **initiative_name_en** | Text | Yes | Initiative name (English). |
| **initiative_name_ar** | Text | No | Initiative name (Arabic). For bilingual visuals. |
| **initiative_type** | Text | Yes | Type of initiative. See [Initiative Type](#initiative-type) below. |
| **status** | Text | Yes | Pipeline stage. See [Status](#status) below. |
| **priority** | Text | No | High, Medium, Low. |
| **country** | Text | Yes | Country (must match **Portfolio**[Country] for integration). |
| **continent** | Text | Yes | Continent (must match **Portfolio**[Continent]). |
| **expected_value_sar** | Number | No | Expected deal value (SAR). |
| **expected_value_usd** | Number | No | Expected deal value (USD). Optional; can be derived from SAR. |
| **expected_area_sqm** | Number | No | Expected area (m²) if applicable. |
| **expected_close_date** | Date | No | Target close/signature date. |
| **start_date** | Date | No | Initiative start or creation date. |
| **owner** | Text | No | Responsible person or team. |
| **property_type** | Text | No | Optional; align with Portfolio property type if linking. |
| **notes** | Text | No | Free-text notes. |

---

## 3. Code Lists (Recommended Values)

### Initiative Type

Use consistently for filtering and grouping:

| Value | Description (EN) |
|-------|------------------|
| Acquisition | New property acquisition |
| Disposition | Sale or disposal of asset |
| Lease Renewal | Renewal of existing lease |
| New Lease | New lease on new or existing asset |
| Expansion | Expansion of current footprint |
| Refurbishment | CapEx / refurbishment initiative |

### Status

Pipeline stages for reporting:

| Value | Description (EN) |
|-------|------------------|
| Pipeline | Early pipeline |
| Qualified | Qualified opportunity |
| Negotiation | In negotiation |
| Due Diligence | Due diligence phase |
| Closed Won | Successfully closed |
| Closed Lost | Lost / dropped |
| On Hold | Paused |

### Priority

| Value |
|-------|
| High |
| Medium |
| Low |

---

## 4. Integration with Portfolio Report

### 4.1 Relationship (optional)

- **Real Estate Initiatives**[country] → **Portfolio**[Country]  
  Use a **many-to-one** relationship (single direction from Initiatives to Portfolio) if you want portfolio filters (e.g. Country/Continent) to filter initiatives.
- Alternatively, keep **Real Estate Initiatives** as a **disconnected** table and use it only for initiative-specific pages and slicers (Initiative Type, Status, Priority).

### 4.2 Geography

- Use the **same** `Country` and `Continent` values as in the Portfolio data so that:
  - Slicers on Country/Continent apply to both Portfolio and Initiatives when related, or
  - At least the same value set appears across the report.

### 4.3 Bilingual

- **initiative_name_en** and **initiative_name_ar** support bilingual tables and cards.
- For report UI (titles, axis labels, status/type labels), add keys to the **Translations** table and use existing `Label - *` measures with `[Selected Language]`.

### 4.4 Measures (suggested)

Once the table is in the model, consider measures such as:

- Count of initiatives (total and by status/type).
- Sum of **expected_value_sar** (or USD) by type, country, status.
- Count or value of initiatives with **expected_close_date** in current year or next 12 months.

---

## 5. File and Encoding

- **File:** `real_estate_initiatives.csv` (or equivalent).
- **Encoding:** UTF-8 (with BOM if consumed in Excel and Arabic is used).
- **Delimiter:** Comma.
- **Header row:** Yes; use the column names from the table above (snake_case).

---

## 6. Sample Data

Sample data is provided in:

- **File:** `data/real_estate_initiatives.csv`

It includes 15 records with a mix of initiative types (Acquisition, Disposition, Lease Renewal, New Lease, Expansion, Refurbishment), statuses (Pipeline, Qualified, Negotiation, Due Diligence, Closed Won, Closed Lost, On Hold), and priorities. Geography uses **Saudi Arabia**, **United Arab Emirates**, **Egypt**, and **Kuwait** with **Asia** and **Africa** continents so you can align with Portfolio. If your Portfolio CSV uses different country names (e.g. `KSA` instead of `Saudi Arabia`), either normalise them in the Initiatives CSV or in the model (e.g. M query or calculated column).

---

## 7. Adding the Table to the Semantic Model

1. In Power BI Desktop (or PBIP): **Get data** → **Text/CSV** → select `data/real_estate_initiatives.csv`.
2. Set column types (date columns as Date, numeric as Decimal, rest as Text).
3. **Optional relationship:** Create a relationship **Real Estate Initiatives**[country] → **Portfolio**[Country] (many-to-one, single direction) so Portfolio filters also filter initiatives.
4. Add measures as needed (e.g. initiative count, total expected value by status/type).
5. For bilingual labels in the report, add keys to the **Translations** table and use existing `Label - *` measures bound to titles/slicers.
