
import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = "employee_performance.csv"
COL_ID = "EmployeeID"
COL_NAME = "EmployeeName"
COL_DEPT = "Department"
COL_PERFORMANCE = "PerformanceScore"
COL_ATTENDANCE = "AttendancePct"

ATTENDANCE_THRESHOLD = 75  # below this % is flagged
OUTPUT_DIR = "."

df = pd.read_csv(CSV_PATH)
print(f"Raw data shape: {df.shape}")

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
plt.show()
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
plt.show()
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
plt.show()
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
"""
EMPLOYEE PERFORMANCE DASHBOARD (Streamlit)
--------------------------------------------
Run with:  streamlit run dashboard.py

Interactive dashboard with department/attendance filters,
KPI cards, and the same 3 charts as the main analysis script.
"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
CSV_PATH = "employee_performance.csv"
COL_ID = "EmployeeID"
COL_NAME = "EmployeeName"
COL_DEPT = "Department"
COL_PERFORMANCE = "PerformanceScore"
COL_ATTENDANCE = "AttendancePct"

st.set_page_config(page_title="Employee Performance Dashboard", layout="wide")

# ------------------------------------------------------------------
# LOAD & CLEAN DATA (cached so it doesn't re-run on every filter click)
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df.drop_duplicates(subset=[COL_ID])
    df[COL_PERFORMANCE] = df[COL_PERFORMANCE].fillna(df[COL_PERFORMANCE].median())
    df[COL_PERFORMANCE] = pd.to_numeric(df[COL_PERFORMANCE], errors="coerce")
    df[COL_ATTENDANCE] = pd.to_numeric(df[COL_ATTENDANCE], errors="coerce")
    return df

df = load_data()

st.title("📊 Employee Performance Dashboard")

# ------------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------------
st.sidebar.header("Filters")

departments = sorted(df[COL_DEPT].unique())
selected_depts = st.sidebar.multiselect(
    "Department", options=departments, default=departments
)

min_perf, max_perf = float(df[COL_PERFORMANCE].min()), float(df[COL_PERFORMANCE].max())
perf_range = st.sidebar.slider(
    "Performance Score Range",
    min_value=min_perf, max_value=max_perf,
    value=(min_perf, max_perf)
)

attendance_threshold = st.sidebar.slider(
    "Show employees with attendance below (%)",
    min_value=0, max_value=100, value=100
)

# Apply filters
filtered = df[
    (df[COL_DEPT].isin(selected_depts)) &
    (df[COL_PERFORMANCE].between(perf_range[0], perf_range[1])) &
    (df[COL_ATTENDANCE] <= attendance_threshold)
]

st.sidebar.markdown(f"**{len(filtered)}** employees match filters")

# ------------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", len(filtered))
col2.metric("Avg Performance", f"{filtered[COL_PERFORMANCE].mean():.1f}" if len(filtered) else "N/A")
col3.metric("Avg Attendance", f"{filtered[COL_ATTENDANCE].mean():.1f}%" if len(filtered) else "N/A")
col4.metric("Below 75% Attendance", int((filtered[COL_ATTENDANCE] < 75).sum()))

st.divider()

# ------------------------------------------------------------------
# CHARTS
# ------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Department-wise Average Performance")
    dept_avg = filtered.groupby(COL_DEPT)[COL_PERFORMANCE].mean().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    ax1.bar(dept_avg.index, dept_avg.values, color="#2563eb")
    ax1.set_ylabel("Avg Performance Score")
    plt.xticks(rotation=20)
    st.pyplot(fig1)

with chart_col2:
    st.subheader("Department Distribution")
    dept_counts = filtered[COL_DEPT].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(dept_counts.values, labels=dept_counts.index, autopct="%1.1f%%", startangle=90)
    st.pyplot(fig2)

st.subheader("Attendance Trend (Ranked by Performance)")
sorted_df = filtered.sort_values(COL_PERFORMANCE, ascending=False).reset_index(drop=True)
fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.plot(sorted_df.index, sorted_df[COL_ATTENDANCE], color="#16a34a")
ax3.axhline(y=75, color="#dc2626", linestyle="--", label="75% threshold")
ax3.set_xlabel("Employee Rank (by performance)")
ax3.set_ylabel("Attendance (%)")
ax3.legend()
st.pyplot(fig3)

st.divider()

# ------------------------------------------------------------------
# TOP 10 PERFORMERS TABLE
# ------------------------------------------------------------------
st.subheader("🏆 Top 10 Performers (within current filters)")
top_10 = filtered.sort_values(COL_PERFORMANCE, ascending=False).head(10)
st.dataframe(top_10[[COL_NAME, COL_DEPT, COL_PERFORMANCE, COL_ATTENDANCE]], use_container_width=True)

# ------------------------------------------------------------------
# LOW ATTENDANCE TABLE
# ------------------------------------------------------------------
st.subheader("⚠️ Employees Below 75% Attendance")
low_att = filtered[filtered[COL_ATTENDANCE] < 75].sort_values(COL_ATTENDANCE)
st.dataframe(low_att[[COL_NAME, COL_DEPT, COL_ATTENDANCE]], use_container_width=True)

# ------------------------------------------------------------------
# DOWNLOAD FILTERED DATA
# ------------------------------------------------------------------
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_employee_report.csv",
    mime="text/csv"
)
