import pandas as pd

# ─── Dataset ───────────────────────────────────────────────────────────────────
data = {
    'NAME':   ['A', 'B', 'C', 'D'],
    'DEPT':   ['IT', 'HR', 'IT', 'HR'],
    'SALARY': [50000, 40000, 60000, 45000]
}

df = pd.DataFrame(data)
print("=" * 45)
print("       EMPLOYEE SALARY INSIGHTS")
print("=" * 45)
print("\n📋 Original Dataset:")
print(df.to_string(index=False))

# ─── 1. Average Salary Per Department ──────────────────────────────────────────
avg_salary = df.groupby('DEPT')['SALARY'].mean()
print("\n💰 Average Salary Per Department:")
for dept, avg in avg_salary.items():
    print(f"   {dept:<6}: ₹{avg:,.0f}")

# ─── 2. Highest Paid Employee Per Department ───────────────────────────────────
highest_paid = df.loc[df.groupby('DEPT')['SALARY'].idxmax()]
print("\n🏆 Highest Paid Employee Per Department:")
print(highest_paid[['DEPT', 'NAME', 'SALARY']].to_string(index=False))

# ─── BONUS 1: Count Employees Per Department ───────────────────────────────────
emp_count = df.groupby('DEPT')['NAME'].count()
print("\n👥 Employee Count Per Department:")
for dept, count in emp_count.items():
    print(f"   {dept:<6}: {count} employee(s)")

# ─── BONUS 2: Sort Departments by Average Salary ───────────────────────────────
sorted_avg = avg_salary.sort_values(ascending=False)
print("\n📊 Departments Sorted by Average Salary:")
for dept, avg in sorted_avg.items():
    print(f"   {dept:<6}: ₹{avg:,.0f}")

# ─── Full GroupBy Summary ───────────────────────────────────────────────────────
print("\n" + "=" * 45)
print("        FULL DEPARTMENT SUMMARY")
print("=" * 45)
summary = df.groupby('DEPT')['SALARY'].agg(
    AVG_SALARY='mean',
    MAX_SALARY='max',
    MIN_SALARY='min',
    EMP_COUNT='count'
).reset_index()

summary['AVG_SALARY'] = summary['AVG_SALARY'].round(0)
print(summary.to_string(index=False))