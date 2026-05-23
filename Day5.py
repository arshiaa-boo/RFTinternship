# PROJECT 5 — BASIC CSV READER (WITHOUT PANDAS)
# Concepts: File Handling, String Splitting, Data Structuring

def read_csv(filename):
    """Read a CSV file and return data as a list of dictionaries."""
    records = []

    with open(filename, 'r') as file:
        lines = file.read().splitlines()

    if not lines:
        return records

    headers = lines[0].split(',')

    for line in lines[1:]:
        if not line.strip():  # skip empty lines
            continue

        values = line.split(',')
        record = {}

        for i, header in enumerate(headers):
            # Handle missing values
            if i < len(values) and values[i].strip() != '':
                value = values[i].strip()
                # Convert numeric values
                try:
                    record[header.strip()] = int(value)
                except ValueError:
                    try:
                        record[header.strip()] = float(value)
                    except ValueError:
                        record[header.strip()] = value
            else:
                record[header.strip()] = None  # missing value → None

        records.append(record)

    return records


def calculate_average_marks(records, marks_key='MARKS'):
    """BONUS: Calculate average marks, ignoring missing values."""
    marks = [r[marks_key] for r in records if r.get(marks_key) is not None]
    if not marks:
        return None
    return sum(marks) / len(marks)


# ── Create sample CSV file ──────────────────────────────────────────────────
sample_csv = "students.csv"

with open(sample_csv, 'w') as f:
    f.write("NAME,AGE,MARKS\n")
    f.write("AMIT,20,85\n")
    f.write("RIYA,21,90\n")
    f.write("JOHN,,78\n")   # missing AGE  → demonstrates missing-value handling
    f.write("SARA,22,\n")   # missing MARKS → demonstrates missing-value handling

# ── Run ─────────────────────────────────────────────────────────────────────
data = read_csv(sample_csv)

print("=" * 45)
print("        CSV DATA (List of Dictionaries)")
print("=" * 45)
print("[")
for record in data:
    print(f"  {record},")
print("]")

avg = calculate_average_marks(data)
print("=" * 45)
if avg is not None:
    print(f"  BONUS → Average Marks : {avg:.2f}")
    print(f"          (missing values ignored automatically)")
print("=" * 45)