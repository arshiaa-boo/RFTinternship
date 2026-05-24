import pandas as pd

# ─── Dataset ───────────────────────────────────────────────────────────────────
data = {
    'NAME':   ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
    'DEPT':   ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT'],
    'AGE':    [25, 32, 28, 35, 27, 30],
    'SALARY': [60000, 45000, 55000, 70000, 48000, 52000]
}

df = pd.DataFrame(data)
print("=" * 50)
print("          DATA FILTERING TOOL")
print("=" * 50)
print("\n📋 Original Dataset:")
print(df.to_string(index=False))

# ─── 1. Filter: SALARY > 50000 ─────────────────────────────────────────────────
high_salary = df[df['SALARY'] > 50000]
print("\n💰 Filter 1 — Employees with SALARY > 50000:")
print(high_salary.to_string(index=False))

# ─── 2. Filter: AGE < 30 ───────────────────────────────────────────────────────
young_emp = df[df['AGE'] < 30]
print("\n🧑 Filter 2 — Employees with AGE < 30:")
print(young_emp.to_string(index=False))

# ─── BONUS 1: Combine Multiple Conditions ──────────────────────────────────────
# AND condition: SALARY > 50000 AND AGE < 30
both = df[(df['SALARY'] > 50000) & (df['AGE'] < 30)]
print("\n✅ Combined Filter (SALARY > 50000 AND AGE < 30):")
if not both.empty:
    print(both.to_string(index=False))
else:
    print("   No records found.")

# OR condition: SALARY > 60000 OR AGE < 27
either = df[(df['SALARY'] > 60000) | (df['AGE'] < 27)]
print("\n🔀 Combined Filter (SALARY > 60000 OR AGE < 27):")
print(either.to_string(index=False))

# NOT condition: Employees NOT in IT
not_it = df[~(df['DEPT'] == 'IT')]
print("\n🚫 NOT Filter — Employees NOT in IT:")
print(not_it.to_string(index=False))

# ─── BONUS 2: Save Filtered Data to New File ───────────────────────────────────
high_salary.to_csv('high_salary_filter.csv', index=False)
young_emp.to_csv('young_employees_filter.csv', index=False)
both.to_csv('combined_filter.csv', index=False)
print("\n💾 Filtered data saved to:")
print("   → high_salary_filter.csv")
print("   → young_employees_filter.csv")
print("   → combined_filter.csv")

# ─── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("              FILTER SUMMARY")
print("=" * 50)
print(f"   Total Employees         : {len(df)}")
print(f"   SALARY > 50000          : {len(high_salary)}")
print(f"   AGE < 30                : {len(young_emp)}")
print(f"   SALARY > 50000 & AGE<30 : {len(both)}")
print(f"   SALARY > 60000 | AGE<27 : {len(either)}")
print(f"   NOT in IT dept          : {len(not_it)}")