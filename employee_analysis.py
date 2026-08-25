"""
EMPLOYEE PERFORMANCE ANALYSIS
------------------------------
Reads employee performance CSV, cleans it, calculates department-wise
averages, finds top 10 performers and low-attendance employees,
generates charts, and exports a final report CSV.

Expected CSV columns (rename in CONFIG if yours differ):
    EmployeeID, EmployeeName, Department, PerformanceScore,
    AttendancePct, ProjectsCompleted
"""

import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# CONFIG — change these to match your actual CSV's column names
# ------------------------------------------------------------------
CSV_PATH = "employee_performance.csv"
COL_ID = "EmployeeID"
COL_NAME = "EmployeeName"
COL_DEPT = "Department"
COL_PERFORMANCE = "PerformanceScore"
COL_ATTENDANCE = "AttendancePct"

ATTENDANCE_THRESHOLD = 75  # below this % is flagged
OUTPUT_DIR = "."

# ------------------------------------------------------------------
# 1. IMPORT DATA
# ------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)
print(f"Raw data shape: {df.shape}")

# ------------------------------------------------------------------
# 2. CLEAN DATA
# ------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=[COL_ID])
print(f"Removed {before - len(df)} duplicate employee records")

missing_perf = df[COL_PERFORMANCE].isna().sum()
df[COL_PERFORMANCE] = df[COL_PERFORMANCE].fillna(df[COL_PERFORMANCE].median())
print(f"Filled {missing_perf} missing performance scores with median")

df[COL_PERFORMANCE] = pd.to_numeric(df[COL_PERFORMANCE], errors="coerce")
df[COL_ATTENDANCE] = pd.to_numeric(df[COL_ATTENDANCE], errors="coerce")
print(f"Clean data shape: {df.shape}")

# ------------------------------------------------------------------
# 3. DEPARTMENT-WISE AVERAGE PERFORMANCE
# ------------------------------------------------------------------
dept_avg_performance = (
    df.groupby(COL_DEPT)[COL_PERFORMANCE]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)
print("\nDepartment-wise Average Performance:")
print(dept_avg_performance.to_string())

# ------------------------------------------------------------------
# 4. TOP 10 PERFORMERS
# ------------------------------------------------------------------
top_10 = df.sort_values(COL_PERFORMANCE, ascending=False).head(10)
print("\nTop 10 Performers:")
print(top_10[[COL_NAME, COL_DEPT, COL_PERFORMANCE]].to_string(index=False))

# ------------------------------------------------------------------
# 5. LOW ATTENDANCE EMPLOYEES (< 75%)
# ------------------------------------------------------------------
low_attendance = df[df[COL_ATTENDANCE] < ATTENDANCE_THRESHOLD].sort_values(COL_ATTENDANCE)
print(f"\nEmployees with attendance below {ATTENDANCE_THRESHOLD}%: {len(low_attendance)}")
print(low_attendance[[COL_NAME, COL_DEPT, COL_ATTENDANCE]].to_string(index=False))

# ------------------------------------------------------------------
# 6. CHARTS
# ------------------------------------------------------------------

# --- 6a. BAR CHART: Performance Comparison across departments ---
plt.figure(figsize=(10, 5))
plt.bar(dept_avg_performance.index, dept_avg_performance.values, color="#2563eb")
plt.title("Department-wise Average Performance", fontsize=14, fontweight="bold")
plt.xlabel("Department")
plt.ylabel("Average Performance Score")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/1_performance_comparison.png", dpi=150)
plt.close()

# --- 6b. LINE CHART: Attendance Trend (sorted by employee performance rank) ---
df_sorted = df.sort_values(COL_PERFORMANCE, ascending=False).reset_index(drop=True)
plt.figure(figsize=(10, 5))
plt.plot(df_sorted.index, df_sorted[COL_ATTENDANCE], color="#16a34a", linewidth=1.5)
plt.axhline(y=ATTENDANCE_THRESHOLD, color="#dc2626", linestyle="--",
            label=f"{ATTENDANCE_THRESHOLD}% threshold")
plt.title("Attendance Trend (Employees Ranked by Performance)", fontsize=14, fontweight="bold")
plt.xlabel("Employee Rank (by performance, high to low)")
plt.ylabel("Attendance (%)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/2_attendance_trend.png", dpi=150)
plt.close()

# --- 6c. PIE CHART: Department Distribution (headcount) ---
dept_counts = df[COL_DEPT].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(
    dept_counts.values,
    labels=dept_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#2563eb", "#f97316", "#16a34a", "#dc2626", "#9333ea", "#0891b2"]
)
plt.title("Employee Distribution by Department", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/3_department_distribution.png", dpi=150)
plt.close()

print("\nCharts saved: performance comparison, attendance trend, department distribution")

# ------------------------------------------------------------------
# 7. EXPORT FINAL REPORT AS CSV
# ------------------------------------------------------------------
df["TopPerformer"] = df[COL_ID].isin(top_10[COL_ID])
df["LowAttendanceFlag"] = df[COL_ATTENDANCE] < ATTENDANCE_THRESHOLD
df["DeptAvgPerformance"] = df[COL_DEPT].map(dept_avg_performance)

report_path = f"{OUTPUT_DIR}/employee_performance_report.csv"
df.to_csv(report_path, index=False)
print(f"\nFinal report exported to: {report_path}")
