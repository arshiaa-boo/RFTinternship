

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
