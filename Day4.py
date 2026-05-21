# Project 4 - Simple Log Analyzer
# GOW AI Academy - Python Internship Day 4

LOGS = [
    "ERROR DISK FULL",
    "INFO STARTED",
    "ERROR FILE MISSING",
    "WARNING MEMORY LOW"
]

# ── Core Functions ───────────────────────────────────────

def count_log_types(logs):
    counts = {"ERROR": 0, "INFO": 0, "WARNING": 0}
    for log in logs:
        log_upper = log.upper()
        if log_upper.startswith("ERROR"):
            counts["ERROR"] += 1
        elif log_upper.startswith("INFO"):
            counts["INFO"] += 1
        elif log_upper.startswith("WARNING"):
            counts["WARNING"] += 1
    return counts

def get_most_frequent(counts):
    return max(counts, key=counts.get)

def get_logs_by_type(logs, log_type):
    return [log for log in logs if log.upper().startswith(log_type.upper())]

# ── Main Program ─────────────────────────────────────────

counts      = count_log_types(LOGS)
most_common = get_most_frequent(counts)

print("=" * 40)
print("        LOG ANALYZER REPORT")
print("=" * 40)
print(f"  Total Logs Analyzed : {len(LOGS)}")
print("-" * 40)
print(f"   ERROR   count    : {counts['ERROR']}")
print(f"   INFO    count    : {counts['INFO']}")
print(f"   WARNING count    : {counts['WARNING']}")
print("-" * 40)
print(f"   Most Frequent    : {most_common}")
print("=" * 40)

# ── Detailed Log Breakdown ───────────────────────────────

print("\n Detailed Breakdown:\n")

for log_type in [("ERROR"), ("INFO"), ("WARNING")]:
    matched = get_logs_by_type(LOGS, log_type)
    print(f" {log_type} Logs:")
    if matched:
        for log in matched:
            print(f"   → {log}")
    else:
        print("   → None")
    print()