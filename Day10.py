# ─── Dataset ───────────────────────────────────────────────────────────────────
LOGS = [
    "ERROR DISK FULL",
    "INFO STARTED",
    "ERROR FILE MISSING",
    "WARNING MEMORY LOW",
    "info connection established",
    "Error timeout occurred",
    "WARNING CPU HIGH",
    "INFO USER LOGGED IN"
]

print("=" * 45)
print("          SIMPLE LOG ANALYZER")
print("=" * 45)
print("\nRaw Logs:")
for i, log in enumerate(LOGS, 1):
    print(f"   [{i}] {log}")

# ─── BONUS: Ignore Case Sensitivity ────────────────────────────────────────────
normalized = [log.upper() for log in LOGS]

# ─── 1. Count ERROR, INFO, WARNING ─────────────────────────────────────────────
error_logs   = [log for log in normalized if log.startswith("ERROR")]
info_logs    = [log for log in normalized if log.startswith("INFO")]
warning_logs = [log for log in normalized if log.startswith("WARNING")]

error_count   = len(error_logs)
info_count    = len(info_logs)
warning_count = len(warning_logs)

print("\nLog Type Count:")
print(f"   ERROR   : {error_count}")
print(f"   INFO    : {info_count}")
print(f"   WARNING : {warning_count}")

# ─── Display Each Category ─────────────────────────────────────────────────────
print("\nERROR Logs:")
for log in error_logs:
    print(f"   -> {log}")

print("\nINFO Logs:")
for log in info_logs:
    print(f"   -> {log}")

print("\nWARNING Logs:")
for log in warning_logs:
    print(f"   -> {log}")

# ─── BONUS 1: Find Most Frequent Log Type ──────────────────────────────────────
counts = {
    'ERROR':   error_count,
    'INFO':    info_count,
    'WARNING': warning_count
}

most_frequent = max(counts, key=counts.get)
print(f"\nMost Frequent Log Type: {most_frequent} ({counts[most_frequent]} times)")

# ─── Pattern Detection Summary ─────────────────────────────────────────────────
total = len(LOGS)
print("\n" + "=" * 45)
print("           PATTERN DETECTION")
print("=" * 45)
print(f"   Total Logs : {total}")
for log_type, count in counts.items():
    bar = "#" * count
    pct = (count / total) * 100
    print(f"   {log_type:<8} : {bar:<10} {count} ({pct:.1f}%)")

print("\nAnalysis Complete!")