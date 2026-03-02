"""Convert PROJECT_SUMMARY.md to a styled PDF."""

import markdown
from pathlib import Path
from xhtml2pdf import pisa

ROOT = Path(__file__).resolve().parent.parent
MD_FILE = ROOT / "PROJECT_SUMMARY.md"
PDF_FILE = ROOT / "PROJECT_SUMMARY.pdf"

CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 11px;
    line-height: 1.6;
    color: #1a1a1a;
}
h1 {
    font-size: 22px;
    color: #0b3d91;
    border-bottom: 3px solid #0b3d91;
    padding-bottom: 8px;
    margin-top: 0;
}
h2 {
    font-size: 16px;
    color: #0b3d91;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 24px;
}
h3 {
    font-size: 13px;
    color: #333;
    margin-top: 18px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 18px 0;
    font-size: 10px;
}
th {
    background-color: #0b3d91;
    color: #ffffff;
    padding: 8px 10px;
    text-align: left;
    font-weight: bold;
}
td {
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
}
tr:nth-child(even) td {
    background-color: #f5f7fa;
}
code {
    background-color: #eef1f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: "Courier New", monospace;
    font-size: 10px;
}
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}
ul, ol {
    margin: 8px 0;
    padding-left: 24px;
}
li {
    margin-bottom: 4px;
}
strong {
    color: #0b3d91;
}
em {
    color: #666;
}
"""

md_text = MD_FILE.read_text(encoding="utf-8")

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "nl2br"],
)

full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

with open(PDF_FILE, "wb") as f:
    status = pisa.CreatePDF(full_html, dest=f)

if status.err:
    print(f"ERROR: PDF generation failed with {status.err} error(s)")
else:
    print(f"PDF created: {PDF_FILE}")
