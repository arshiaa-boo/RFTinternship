from __future__ import annotations

import io
import re
import csv
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Union

from datetime import date

import pandas as pd
import streamlit as st

from invoice_processor import (
    parse_csv_invoices,
    parse_pdf_invoice,
    build_report,
    generate_summary,
    summary_to_text,
)


st.set_page_config(
    page_title="Automated Invoice Processing System",
    page_icon="🧾",
    layout="wide",
)

st.title("🧾 Automated Invoice Processing System")
st.caption("Upload CSV and/or PDF invoices to generate a consolidated report, "
           "flag overdue invoices, and export the results.")

# --------------------------------------------------------------------
# Sidebar: uploads + options
# --------------------------------------------------------------------
with st.sidebar:
    st.header("1. Upload Invoices")
    csv_files = st.file_uploader(
        "CSV file(s)", type=["csv"], accept_multiple_files=True,
        help="Each row = one line item. Rows with the same invoice number are grouped."
    )
    pdf_files = st.file_uploader(
        "PDF file(s)", type=["pdf"], accept_multiple_files=True,
        help="Each PDF is treated as one invoice."
    )

    st.header("2. Options")
    as_of_date = st.date_input("Evaluate overdue status as of", value=date.today())

    process_clicked = st.button("🚀 Process Invoices", type="primary", use_container_width=True)

    st.divider()
    st.caption("No file? Generate sample data with `python generate_sample_data.py`, "
               "then upload the resulting `sample_invoices.csv`.")

# --------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------
if "report_df" not in st.session_state:
    st.session_state.report_df = None
    st.session_state.summary = None

# --------------------------------------------------------------------
# Processing
# --------------------------------------------------------------------
if process_clicked:
    if not csv_files and not pdf_files:
        st.warning("Please upload at least one CSV or PDF file before processing.")
    else:
        invoices = []
        errors = []

        for f in csv_files or []:
            try:
                f.seek(0)
                text_stream = io.StringIO(f.read().decode("utf-8"))
                text_stream.name = f.name
                invoices.extend(parse_csv_invoices(text_stream))
            except Exception as e:
                errors.append(f"{f.name}: {e}")

        for f in pdf_files or []:
            try:
                f.seek(0)
                byte_stream = io.BytesIO(f.read())
                byte_stream.name = f.name
                invoices.append(parse_pdf_invoice(byte_stream))
            except Exception as e:
                errors.append(f"{f.name}: {e}")

        if errors:
            for err in errors:
                st.error(f"⚠️ Failed to process {err}")

        if invoices:
            report_df = build_report(invoices, as_of=as_of_date)
            st.session_state.report_df = report_df
            st.session_state.summary = generate_summary(report_df)
            st.success(f"Processed {len(invoices)} invoice(s) successfully.")
        elif not errors:
            st.warning("No invoices could be extracted from the uploaded files.")

# --------------------------------------------------------------------
# Results
# --------------------------------------------------------------------
report_df = st.session_state.report_df
summary = st.session_state.summary

if report_df is not None and not report_df.empty:

    # ---- KPI row -------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices", summary["total_invoices"])
    c2.metric("Total Billed", f"${summary['total_amount']:,.2f}")
    c3.metric("Overdue Invoices", summary["overdue_count"],
              delta=f"${summary['overdue_amount']:,.2f} at risk", delta_color="inverse")
    c4.metric("Avg Invoice Value", f"${summary['average_invoice_value']:,.2f}")

    st.divider()

    # ---- Tabs ------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📋 Consolidated Report", "📊 Summary & Charts", "⚠️ Overdue Invoices"])

    with tab1:
        st.subheader("Consolidated Invoice Report")

        status_filter = st.multiselect(
            "Filter by status", options=sorted(report_df["Status"].unique()),
            default=list(sorted(report_df["Status"].unique()))
        )
        filtered_df = report_df[report_df["Status"].isin(status_filter)]

        st.dataframe(
            filtered_df.style.apply(
                lambda row: ["background-color: #ffe5e5"] * len(row) if row["Overdue"] == "Yes" else [""] * len(row),
                axis=1
            ),
            use_container_width=True,
            hide_index=True,
        )

        csv_bytes = report_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Consolidated Report (CSV)",
            data=csv_bytes,
            file_name="consolidated_invoice_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab2:
        st.subheader("Summary Report")
        st.text(summary_to_text(summary))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Billed Amount by Customer**")
            by_customer = report_df.groupby("Customer Name")["Total Amount"].sum().sort_values(ascending=False)
            st.bar_chart(by_customer)

        with col2:
            st.markdown("**Invoice Status Breakdown**")
            status_counts = report_df["Status"].value_counts()
            st.bar_chart(status_counts)

        summary_text = summary_to_text(summary)
        st.download_button(
            "⬇️ Download Summary Report (TXT)",
            data=summary_text.encode("utf-8"),
            file_name="invoice_summary_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab3:
        st.subheader("Overdue Invoices")
        overdue_df = report_df[report_df["Overdue"] == "Yes"]
        if overdue_df.empty:
            st.success("🎉 No overdue invoices — everything is on track!")
        else:
            st.error(f"{len(overdue_df)} invoice(s) overdue, totaling ${overdue_df['Total Amount'].sum():,.2f}")
            st.dataframe(overdue_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Upload CSV or PDF invoices in the sidebar and click **Process Invoices** to get started.")

    with st.expander("Expected CSV format"):
        st.markdown("""
One row per **line item**. Rows sharing the same `invoice_number` are grouped into a single invoice.

| invoice_number | customer_name | customer_email | invoice_date | due_date | item_description | quantity | unit_price | status |
|---|---|---|---|---|---|---|---|---|
| INV-1001 | Acme Corp | billing@acme.com | 2026-08-01 | 2026-08-31 | Web Design | 1 | 500 | Pending |
| INV-1001 | Acme Corp | billing@acme.com | 2026-08-01 | 2026-08-31 | Hosting | 2 | 45 | Pending |
        """)

    with st.expander("Expected PDF format"):
        st.markdown("""
PDF invoices are parsed with text extraction + regex. Best results when the PDF contains
clear labels such as `Invoice No:`, `Invoice Date:`, `Due Date:`, `Bill To:`, and a total
amount line such as `Total: $500.00`. Layouts vary a lot in practice, so double-check
extracted PDF fields in the report table.
        """)


# pdfplumber is used for PDF text extraction. Imported lazily inside the
# PDF function so that CSV-only users don't need it installed.
# pip install pdfplumber

DATE_FORMATS = [
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
    "%d %b %Y", "%d %B %Y", "%Y/%m/%d",
]


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class InvoiceItem:
    """A single line item on an invoice."""
    description: str
    quantity: float
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Invoice:
    """A fully parsed invoice, possibly built from several CSV rows."""
    invoice_number: str
    customer_name: str = ""
    customer_email: str = ""
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    items: List[InvoiceItem] = field(default_factory=list)
    status: str = "Pending"          # Pending / Paid / Overdue (auto-computed)
    source_file: str = ""

    @property
    def total_amount(self) -> float:
        return round(sum(item.line_total for item in self.items), 2)

    @property
    def item_count(self) -> int:
        return len(self.items)

    def is_overdue(self, as_of: Optional[date] = None) -> bool:
        """An invoice is overdue if it has a due date in the past and has
        not already been marked Paid."""
        as_of = as_of or date.today()
        if self.status.lower() == "paid":
            return False
        if self.due_date is None:
            return False
        return self.due_date < as_of

    def to_dict(self) -> Dict:
        return {
            "Invoice Number": self.invoice_number,
            "Customer Name": self.customer_name,
            "Customer Email": self.customer_email,
            "Invoice Date": self.invoice_date.isoformat() if self.invoice_date else "",
            "Due Date": self.due_date.isoformat() if self.due_date else "",
            "Item Count": self.item_count,
            "Total Amount": self.total_amount,
            "Status": self.status,
            "Overdue": "Yes" if self.is_overdue() else "No",
            "Source File": self.source_file,
        }


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def parse_date(value: Union[str, None]) -> Optional[date]:
    """Try a handful of common date formats; return None if unparseable."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    # Last resort: let pandas try to guess
    try:
        parsed = pd.to_datetime(value, errors="raise")
        return parsed.date()
    except Exception:
        return None


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return default


# --------------------------------------------------------------------------
# CSV parsing
# --------------------------------------------------------------------------
#
# Expected CSV columns (case-insensitive, flexible order). One row = one
# line item. Rows sharing the same invoice_number are grouped together.
#
#   invoice_number, customer_name, customer_email, invoice_date, due_date,
#   item_description, quantity, unit_price, status
#
# Only invoice_number is strictly required; everything else has sane
# fallbacks so real-world messy CSVs still mostly work.

REQUIRED_COLUMN = "invoice_number"

COLUMN_ALIASES = {
    "invoice_number": ["invoice_number", "invoice no", "invoice id", "inv_no", "invoice#"],
    "customer_name": ["customer_name", "customer", "client_name", "bill_to"],
    "customer_email": ["customer_email", "email", "client_email"],
    "invoice_date": ["invoice_date", "date", "billing_date"],
    "due_date": ["due_date", "payment_due", "due"],
    "item_description": ["item_description", "item", "description", "product"],
    "quantity": ["quantity", "qty"],
    "unit_price": ["unit_price", "price", "rate", "item_price"],
    "status": ["status", "payment_status"],
}


def _normalize_columns(columns: List[str]) -> Dict[str, str]:
    """Map actual CSV column names -> canonical field names."""
    lower_cols = {c.lower().strip(): c for c in columns}
    mapping = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_cols:
                mapping[canonical] = lower_cols[alias]
                break
    return mapping


def parse_csv_invoices(source: Union[str, Path, io.StringIO]) -> List[Invoice]:
    """
    Parse a CSV file (path or file-like/StringIO object, e.g. from a
    Streamlit file_uploader) into a list of Invoice objects, grouping
    line-item rows by invoice number.
    """
    if isinstance(source, (str, Path)):
        df = pd.read_csv(source, dtype=str).fillna("")
        source_name = str(source)
    else:
        df = pd.read_csv(source, dtype=str).fillna("")
        source_name = getattr(source, "name", "uploaded.csv")

    colmap = _normalize_columns(list(df.columns))
    if "invoice_number" not in colmap:
        raise ValueError(
            "CSV must contain an invoice number column "
            "(e.g. 'invoice_number', 'Invoice No', 'Invoice ID')."
        )

    invoices: Dict[str, Invoice] = {}

    for _, row in df.iterrows():
        inv_no = str(row[colmap["invoice_number"]]).strip()
        if not inv_no:
            continue

        if inv_no not in invoices:
            invoices[inv_no] = Invoice(
                invoice_number=inv_no,
                customer_name=row.get(colmap.get("customer_name", ""), "") if "customer_name" in colmap else "",
                customer_email=row.get(colmap.get("customer_email", ""), "") if "customer_email" in colmap else "",
                invoice_date=parse_date(row.get(colmap.get("invoice_date", ""), "")) if "invoice_date" in colmap else None,
                due_date=parse_date(row.get(colmap.get("due_date", ""), "")) if "due_date" in colmap else None,
                status=(row.get(colmap.get("status", ""), "") or "Pending") if "status" in colmap else "Pending",
                source_file=source_name,
            )

        inv = invoices[inv_no]

        # Add the line item for this row, if item info is present
        if "item_description" in colmap or "unit_price" in colmap:
            desc = row.get(colmap.get("item_description", ""), "") if "item_description" in colmap else ""
            qty = _to_float(row.get(colmap.get("quantity", ""), 1)) if "quantity" in colmap else 1.0
            price = _to_float(row.get(colmap.get("unit_price", ""), 0)) if "unit_price" in colmap else 0.0
            if desc or price:
                inv.items.append(InvoiceItem(description=desc or "Item", quantity=qty or 1.0, unit_price=price))

    return list(invoices.values())


# --------------------------------------------------------------------------
# PDF parsing (Bonus)
# --------------------------------------------------------------------------
#
# Uses regex over extracted text. Because real invoices vary wildly in
# layout, these patterns are intentionally forgiving and can be tuned per
# vendor template. Designed for typical single-page simple invoices.

PDF_PATTERNS = {
    "invoice_number": r"(?:Invoice\s*(?:No\.?|Number|#)\s*[:\-]?\s*)([A-Za-z0-9\-\/]+)",
    "invoice_date": r"(?:Invoice\s*Date\s*[:\-]?\s*)([0-9A-Za-z\-\/, ]+?)(?:\n|$)",
    "due_date": r"(?:Due\s*Date\s*[:\-]?\s*)([0-9A-Za-z\-\/, ]+?)(?:\n|$)",
    "customer_name": r"(?:Bill\s*To|Customer|Client)\s*[:\-]?\s*([A-Za-z0-9 &.,'\-]+?)(?:\n)",
    "customer_email": r"([\w\.-]+@[\w\.-]+\.\w+)",
    "total_amount": r"(?:Total(?:\s*Amount)?|Grand\s*Total)\s*[:\-]?\s*\$?\s*([\d,]+\.\d{2}|[\d,]+)",
}

# Matches item lines like: "Widget A   2   10.00   20.00"
PDF_ITEM_LINE = re.compile(
    r"^(?P<desc>[A-Za-z][A-Za-z0-9 \-\_/]+?)\s+(?P<qty>\d+(?:\.\d+)?)\s+\$?(?P<price>[\d,]+\.\d{2})\s+\$?[\d,]+\.\d{2}\s*$",
    re.MULTILINE,
)


def parse_pdf_invoice(source: Union[str, Path, io.BytesIO]) -> Invoice:
    """
    Extract a single invoice's data from a PDF file using text extraction
    + regex. Requires `pdfplumber` (pip install pdfplumber).
    """
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError(
            "PDF parsing requires pdfplumber. Install it with: pip install pdfplumber"
        ) from e

    if isinstance(source, (str, Path)):
        source_name = str(source)
    else:
        source_name = getattr(source, "name", "uploaded.pdf")

    text = ""
    with pdfplumber.open(source) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    def find(pattern_key):
        m = re.search(PDF_PATTERNS[pattern_key], text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    inv_no = find("invoice_number") or f"UNKNOWN-{abs(hash(text)) % 10000}"
    inv_date = parse_date(find("invoice_date"))
    due_date = parse_date(find("due_date"))
    customer = find("customer_name")
    email = find("customer_email")

    invoice = Invoice(
        invoice_number=inv_no,
        customer_name=customer,
        customer_email=email,
        invoice_date=inv_date,
        due_date=due_date,
        status="Pending",
        source_file=source_name,
    )

    # Try to extract line items via the tabular regex first
    for m in PDF_ITEM_LINE.finditer(text):
        desc = m.group("desc").strip()
        qty = _to_float(m.group("qty"), 1.0)
        price = _to_float(m.group("price"), 0.0)
        invoice.items.append(InvoiceItem(description=desc, quantity=qty, unit_price=price))

    # Fallback: if no line items were detected but a total was printed,
    # record it as a single synthetic line item so totals still work.
    if not invoice.items:
        total_str = find("total_amount")
        total_val = _to_float(total_str, 0.0)
        if total_val:
            invoice.items.append(InvoiceItem(description="Invoice Total (from PDF)", quantity=1, unit_price=total_val))

    return invoice


def parse_pdf_invoices(sources: List[Union[str, Path, io.BytesIO]]) -> List[Invoice]:
    """Parse multiple PDF files into a list of Invoice objects."""
    return [parse_pdf_invoice(src) for src in sources]


# --------------------------------------------------------------------------
# Report generation
# --------------------------------------------------------------------------

def build_report(invoices: List[Invoice], as_of: Optional[date] = None) -> pd.DataFrame:
    """Turn a list of Invoice objects into a consolidated report DataFrame."""
    as_of = as_of or date.today()
    rows = []
    for inv in invoices:
        d = inv.to_dict()
        d["Overdue"] = "Yes" if inv.is_overdue(as_of) else "No"
        rows.append(d)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Invoice Number").reset_index(drop=True)
    return df


def export_report_csv(df: pd.DataFrame, output_path: Union[str, Path]) -> str:
    """Write the report DataFrame to a CSV file and return its path."""
    output_path = str(output_path)
    df.to_csv(output_path, index=False)
    return output_path


def generate_summary(df: pd.DataFrame) -> Dict:
    """Compute aggregate summary statistics for the consolidated report."""
    if df.empty:
        return {
            "total_invoices": 0,
            "total_amount": 0.0,
            "overdue_count": 0,
            "overdue_amount": 0.0,
            "paid_count": 0,
            "pending_count": 0,
            "average_invoice_value": 0.0,
            "top_customers": {},
        }

    overdue_df = df[df["Overdue"] == "Yes"]
    paid_df = df[df["Status"].str.lower() == "paid"]
    pending_df = df[(df["Status"].str.lower() != "paid") & (df["Overdue"] == "No")]

    top_customers = (
        df.groupby("Customer Name")["Total Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .round(2)
        .to_dict()
    )

    return {
        "total_invoices": int(len(df)),
        "total_amount": round(float(df["Total Amount"].sum()), 2),
        "overdue_count": int(len(overdue_df)),
        "overdue_amount": round(float(overdue_df["Total Amount"].sum()), 2),
        "paid_count": int(len(paid_df)),
        "pending_count": int(len(pending_df)),
        "average_invoice_value": round(float(df["Total Amount"].mean()), 2),
        "top_customers": top_customers,
    }


def summary_to_text(summary: Dict) -> str:
    """Render the summary dict as a readable plain-text report."""
    lines = [
        "=" * 50,
        "INVOICE PROCESSING - SUMMARY REPORT",
        "=" * 50,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 50,
        f"Total Invoices Processed : {summary['total_invoices']}",
        f"Total Amount Billed      : ${summary['total_amount']:,.2f}",
        f"Paid Invoices            : {summary['paid_count']}",
        f"Pending Invoices         : {summary['pending_count']}",
        f"Overdue Invoices         : {summary['overdue_count']}",
        f"Overdue Amount           : ${summary['overdue_amount']:,.2f}",
        f"Average Invoice Value    : ${summary['average_invoice_value']:,.2f}",
        "-" * 50,
        "Top Customers by Billed Amount:",
    ]
    for name, amount in summary.get("top_customers", {}).items():
        lines.append(f"  - {name or 'Unknown'}: ${amount:,.2f}")
    lines.append("=" * 50)
    return "\n".join(lines)


# --------------------------------------------------------------------------
# End-to-end convenience function
# --------------------------------------------------------------------------

def process_files(
    csv_paths: Optional[List[Union[str, Path]]] = None,
    pdf_paths: Optional[List[Union[str, Path]]] = None,
    as_of: Optional[date] = None,
) -> Dict:
    """
    Full pipeline: parse CSV(s) and/or PDF(s), build the report, compute
    the summary. Returns a dict with 'invoices', 'report_df', 'summary'.
    """
    invoices: List[Invoice] = []

    for path in (csv_paths or []):
        invoices.extend(parse_csv_invoices(path))

    for path in (pdf_paths or []):
        invoices.append(parse_pdf_invoice(path))

    report_df = build_report(invoices, as_of=as_of)
    summary = generate_summary(report_df)

    return {
        "invoices": invoices,
        "report_df": report_df,
        "summary": summary,
    }


if __name__ == "__main__":
    # Simple CLI smoke test / example usage
    import argparse

    parser = argparse.ArgumentParser(description="Automated Invoice Processing System")
    parser.add_argument("--csv", nargs="*", default=[], help="Path(s) to CSV invoice file(s)")
    parser.add_argument("--pdf", nargs="*", default=[], help="Path(s) to PDF invoice file(s)")
    parser.add_argument("--out", default="consolidated_invoice_report.csv", help="Output CSV path")
    args = parser.parse_args()

    result = process_files(csv_paths=args.csv, pdf_paths=args.pdf)
    export_report_csv(result["report_df"], args.out)
    print(f"Report written to {args.out}")
    print(summary_to_text(result["summary"]))


import csv
import random
from datetime import date, timedelta

OUTPUT_FILE = "sample_invoices.csv"

CUSTOMERS = [
    ("Acme Corp", "billing@acme.com"),
    ("Globex Inc", "ap@globex.com"),
    ("Initech", "finance@initech.com"),
    ("Umbrella Co", "accounts@umbrella.com"),
    ("Wayne Enterprises", "payables@wayne.com"),
    ("Stark Industries", "ap@stark.com"),
]

ITEMS = [
    ("Web Design Services", 150.00),
    ("Cloud Hosting (Monthly)", 45.00),
    ("Logo Design", 300.00),
    ("SEO Consultation", 120.00),
    ("Software License", 500.00),
    ("Technical Support (hrs)", 75.00),
    ("Domain Registration", 15.00),
    ("Content Writing", 60.00),
]

STATUSES = ["Paid", "Pending", "Pending", "Paid"]  # weighted


def generate_rows(num_invoices=15):
    rows = []
    today = date.today()

    for i in range(1, num_invoices + 1):
        inv_no = f"INV-{2026}{i:04d}"
        customer_name, customer_email = random.choice(CUSTOMERS)

        # Spread invoice dates over the last ~60 days
        inv_date = today - timedelta(days=random.randint(1, 60))
        # Payment terms: due 15 or 30 days after invoice date
        due_date = inv_date + timedelta(days=random.choice([15, 30]))
        status = random.choice(STATUSES)

        num_items = random.randint(1, 3)
        chosen_items = random.sample(ITEMS, num_items)

        for desc, price in chosen_items:
            qty = random.randint(1, 4)
            rows.append({
                "invoice_number": inv_no,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "invoice_date": inv_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "item_description": desc,
                "quantity": qty,
                "unit_price": price,
                "status": status,
            })

    return rows


def main():
    rows = generate_rows()
    fieldnames = [
        "invoice_number", "customer_name", "customer_email",
        "invoice_date", "due_date", "item_description",
        "quantity", "unit_price", "status",
    ]
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Sample data written to {OUTPUT_FILE} ({len(rows)} line items).")


if __name__ == "__main__":
    main()

