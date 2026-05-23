# PROJECT 6 — SALES DATA ANALYZER
# Concepts: Reading CSV, Basic Aggregation, Column Operations

def read_csv(filename):
    """Read CSV and return list of dictionaries."""
    records = []
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    if not lines:
        return records
    headers = [h.strip() for h in lines[0].split(',')]
    for line in lines[1:]:
        if not line.strip():
            continue
        values = [v.strip() for v in line.split(',')]
        record = {}
        for i, header in enumerate(headers):
            val = values[i] if i < len(values) else None
            try:
                record[header] = int(val)
            except (ValueError, TypeError):
                try:
                    record[header] = float(val)
                except (ValueError, TypeError):
                    record[header] = val
        records.append(record)
    return records


def add_total_column(records):
    """BONUS: Add TOTAL = QUANTITY * PRICE column to each record."""
    for record in records:
        qty   = record.get('QUANTITY', 0) or 0
        price = record.get('PRICE', 0)    or 0
        record['TOTAL'] = qty * price
    return records


def calculate_sales_per_product(records):
    """Aggregate total revenue and total quantity sold per product."""
    sales = {}
    for record in records:
        product = record['PRODUCT']
        total   = record.get('TOTAL', 0)
        qty     = record.get('QUANTITY', 0)
        if product not in sales:
            sales[product] = {'REVENUE': 0, 'QUANTITY': 0}
        sales[product]['REVENUE']  += total
        sales[product]['QUANTITY'] += qty
    return sales


def sort_by_revenue(sales):
    """BONUS: Sort products by revenue descending."""
    return dict(sorted(sales.items(), key=lambda x: x[1]['REVENUE'], reverse=True))


def display_table(records):
    """Pretty-print the data table with TOTAL column."""
    headers = ['PRODUCT', 'QUANTITY', 'PRICE', 'TOTAL']
    col_w   = [max(len(h), max(len(str(r.get(h, ''))) for r in records)) for h in headers]
    sep     = '+' + '+'.join('-' * (w + 2) for w in col_w) + '+'
    header_row = '|' + '|'.join(f" {h:<{col_w[i]}} " for i, h in enumerate(headers)) + '|'
    print(sep)
    print(header_row)
    print(sep)
    for r in records:
        row = '|' + '|'.join(f" {str(r.get(h, '')):<{col_w[i]}} " for i, h in enumerate(headers)) + '|'
        print(row)
    print(sep)


# ── Create sample CSV ────────────────────────────────────────────────────────
with open('sales.csv', 'w') as f:
    f.write("PRODUCT,QUANTITY,PRICE\n")
    f.write("A,2,100\n")
    f.write("B,1,200\n")
    f.write("A,3,100\n")
    f.write("C,5,50\n")

# ── Main ─────────────────────────────────────────────────────────────────────
records = read_csv('sales.csv')
records = add_total_column(records)         # BONUS: add TOTAL column

print("\n" + "=" * 45)
print("         RAW DATA WITH TOTAL COLUMN")
print("=" * 45)
display_table(records)

# Aggregate
sales   = calculate_sales_per_product(records)
sales   = sort_by_revenue(sales)            # BONUS: sort by revenue

total_revenue    = sum(v['REVENUE'] for v in sales.values())
top_product      = next(iter(sales))        # first key after sort = highest revenue

print("\n" + "=" * 45)
print("       SALES SUMMARY PER PRODUCT")
print("=" * 45)
print(f"  {'PRODUCT':<10} {'TOTAL QTY':>10} {'REVENUE':>10}")
print("  " + "-" * 33)
for product, info in sales.items():
    print(f"  {product:<10} {info['QUANTITY']:>10} {info['REVENUE']:>10}")
print("  " + "-" * 33)

print("\n" + "=" * 45)
print("              KEY METRICS")
print("=" * 45)
print(f"  Total Revenue     : ₹ {total_revenue}")
print(f"  Top-Selling Product: {top_product}  "
      f"(Revenue: ₹ {sales[top_product]['REVENUE']})")
print("=" * 45 + "\n")