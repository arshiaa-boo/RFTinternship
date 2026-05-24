import pandas as pd

# ─── Dataset ───────────────────────────────────────────────────────────────────
data = {
    'NAME':    ['AMIT', 'RIYA', 'JOHN'],
    'MATH':    [80, 90, 60],
    'SCIENCE': [70, 88, 65],
    'ENGLISH': [85, 92, 70]
}

df = pd.DataFrame(data)
print("=" * 45)
print("       STUDENT PERFORMANCE DASHBOARD")
print("=" * 45)
print("\n📋 Original Dataset:")
print(df.to_string(index=False))

# ─── 1. Average Marks Per Student ──────────────────────────────────────────────
df['AVERAGE'] = df[['MATH', 'SCIENCE', 'ENGLISH']].mean(axis=1).round(2)
print("\n📊 Average Marks Per Student:")
print(df[['NAME', 'AVERAGE']].to_string(index=False))

# ─── 2. Find Topper ────────────────────────────────────────────────────────────
topper = df.loc[df['AVERAGE'].idxmax()]
print(f"\n🏆 Topper: {topper['NAME']}  (Average: {topper['AVERAGE']})")

# ─── 3. Count Students Above Overall Average ───────────────────────────────────
overall_avg = df['AVERAGE'].mean()
above_avg_count = (df['AVERAGE'] > overall_avg).sum()
print(f"\n📈 Overall Class Average: {overall_avg:.2f}")
print(f"✅ Students Above Average: {above_avg_count}")

# ─── BONUS 1: Add Grade Column ─────────────────────────────────────────────────
def assign_grade(avg):
    if avg >= 90:   return 'A'
    elif avg >= 75: return 'B'
    elif avg >= 60: return 'C'
    else:           return 'D'

df['GRADE'] = df['AVERAGE'].apply(assign_grade)
print("\n🎓 Grade Report:")
print(df[['NAME', 'AVERAGE', 'GRADE']].to_string(index=False))

# ─── BONUS 2: Subject-wise Average ─────────────────────────────────────────────
subject_avg = df[['MATH', 'SCIENCE', 'ENGLISH']].mean()
print("\n📚 Subject-wise Class Average:")
for subject, avg in subject_avg.items():
    print(f"   {subject:<10}: {avg:.2f}")

print("\n" + "=" * 45)
print("           FULL REPORT")
print("=" * 45)
print(df.to_string(index=False))