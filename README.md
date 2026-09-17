# 🧾 Automated Invoice Processing System

A Python project that reads invoice data from **CSV and PDF files**, extracts
key fields, calculates totals, flags **overdue invoices**, builds a
**consolidated report**, and exports it to CSV — with a bonus **Streamlit**
web interface.

## What it does

- Reads invoice data from **CSV** files (one row per line item, grouped by invoice number)
- Reads invoice data from **PDF** files (regex-based text extraction, via `pdfplumber`)
- Extracts: Invoice Number, Customer Name & Email, Invoice Date, Due Date, Item & Price details
- Calculates the **total amount** per invoice
- Identifies **overdue invoices** (due date passed and not marked "Paid")
- Builds a **consolidated report** across all invoices
- Exports the report as **CSV**
- Generates a plain-text **summary report** (totals, overdue amount, top customers, etc.)
- Provides a **Streamlit** UI: upload files, view/filter the report, see charts, download results

## Project structure

```
invoice_project/
├── invoice_processor.py     # Core engine: parsing, calculations, report + summary generation
├── app.py                   # Streamlit web interface
├── generate_sample_data.py  # Creates sample_invoices.csv for testing
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create/activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Usage

### Option A — Command line

```bash
# Generate some sample data to play with (optional)
python generate_sample_data.py

# Process CSV and/or PDF invoices, export a consolidated CSV report
python invoice_processor.py --csv sample_invoices.csv --out consolidated_invoice_report.csv

# You can mix multiple CSVs and PDFs
python invoice_processor.py --csv invoices1.csv invoices2.csv --pdf inv1.pdf inv2.pdf --out report.csv
```

This prints a summary report to the terminal and writes the consolidated CSV report.

### Option B — Streamlit web app (bonus)

```bash
streamlit run app.py
```

Then in the browser:
1. Upload one or more CSV and/or PDF invoice files in the sidebar
2. Click **Process Invoices**
3. View KPIs, the consolidated report table (overdue rows highlighted), charts, and the overdue-invoices tab
4. Download the consolidated report (CSV) or the summary report (TXT)

### Option C — Use it as a library

```python
from invoice_processor import process_files, export_report_csv, summary_to_text

result = process_files(csv_paths=["sample_invoices.csv"], pdf_paths=["sample_invoice.pdf"])

export_report_csv(result["report_df"], "consolidated_invoice_report.csv")
print(summary_to_text(result["summary"]))
```

## Expected CSV format

One row per **line item**. Rows sharing the same `invoice_number` are grouped into one invoice.
Column names are matched flexibly (case-insensitive, common aliases supported — see
`COLUMN_ALIASES` in `invoice_processor.py`).

| invoice_number | customer_name | customer_email   | invoice_date | due_date   | item_description | quantity | unit_price | status  |
|----------------|---------------|-------------------|--------------|------------|-------------------|----------|------------|---------|
| INV-1001       | Acme Corp     | billing@acme.com | 2026-08-01   | 2026-08-31 | Web Design        | 1        | 500        | Pending |
| INV-1001       | Acme Corp     | billing@acme.com | 2026-08-01   | 2026-08-31 | Hosting           | 2        | 45         | Pending |

Only `invoice_number` is strictly required — everything else has sane fallbacks.

## Expected PDF format

PDF invoices are parsed with text extraction + regex matching. Extraction works best when the
PDF text contains recognizable labels, e.g.:

```
Invoice No: INV-1001
Invoice Date: 2026-08-01
Due Date: 2026-08-31
Bill To: Acme Corp
Email: billing@acme.com

Web Design Services   1   150.00   150.00
Cloud Hosting         3   45.00    135.00

Total: $285.00
```

Because real-world invoice layouts vary a lot, treat PDF extraction as a **starting point** —
always spot-check extracted fields in the report table. The regex patterns
(`PDF_PATTERNS`, `PDF_ITEM_LINE` in `invoice_processor.py`) can be tuned per vendor template.

## How "overdue" is determined

An invoice is **overdue** if:
- it has a due date, **and**
- that due date is before the evaluation date (defaults to today, adjustable in the Streamlit sidebar), **and**
- its status is not `"Paid"`

## Extending this project

- **Multiple PDF layouts**: add per-vendor regex profiles and auto-detect which one to use
- **Database storage**: swap the CSV export for writing to SQLite/Postgres
- **Email reminders**: use the overdue list to trigger automated reminder emails (e.g. via `smtplib`)
- **OCR support**: for scanned (image-based) PDFs, pipe pages through `pytesseract` before regex matching
- **Currency handling**: extend `_to_float` and the report schema to track multiple currencies
