"""
Day 13 - Project 13: Distribution Analysis using Seaborn
GOW AI Academy | Python Internship
Concepts: Histograms, Distribution Understanding, KDE Curve, Skewness
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ─────────────────────────────────────────────
# 1. GENERATE SAMPLE DATASETS
# ─────────────────────────────────────────────

np.random.seed(42)

# Student Marks Dataset (slightly left-skewed — most students score well)
student_marks = np.concatenate([
    np.random.normal(loc=72, scale=10, size=150),
    np.random.normal(loc=85, scale=5,  size=50),
])
student_marks = np.clip(student_marks, 0, 100)  # Marks must be 0–100

# Salary Dataset (right-skewed — few people earn very high)
salary_data = np.concatenate([
    np.random.normal(loc=40000, scale=8000, size=200),
    np.random.exponential(scale=20000,      size=50),
])
salary_data = np.clip(salary_data, 15000, None)  # Minimum wage floor

# Wrap in DataFrames
df_marks  = pd.DataFrame({"Marks":  student_marks})
df_salary = pd.DataFrame({"Salary": salary_data})

# ─────────────────────────────────────────────
# 2. HELPER: DETECT SKEWNESS
# ─────────────────────────────────────────────

def describe_skewness(skew_val: float) -> str:
    """Return a human-readable skewness label."""
    if skew_val > 0.5:
        return f"Right-skewed (positive skew = {skew_val:.2f})"
    elif skew_val < -0.5:
        return f"Left-skewed (negative skew = {skew_val:.2f})"
    else:
        return f"Approximately symmetric (skew = {skew_val:.2f})"

# ─────────────────────────────────────────────
# 3. PLOT — STUDENT MARKS DISTRIBUTION
# ─────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Day 13 — Distribution Analysis (Seaborn)", fontsize=16, fontweight="bold", y=1.02)

## --- Plot A: Student Marks ---
ax1 = axes[0]

sns.histplot(
    data=df_marks, x="Marks",
    bins=20,
    kde=True,               # ← KDE curve (bonus requirement)
    color="#4C72B0",
    edgecolor="white",
    linewidth=0.5,
    ax=ax1,
)

# Overlay a normal-fit curve for comparison
mu, sigma = stats.norm.fit(student_marks)
x_range = np.linspace(student_marks.min(), student_marks.max(), 200)
pdf_fitted = stats.norm.pdf(x_range, mu, sigma)
# Scale to histogram height
bin_width = (student_marks.max() - student_marks.min()) / 20
pdf_scaled = pdf_fitted * len(student_marks) * bin_width
ax1.plot(x_range, pdf_scaled, "r--", linewidth=2, label="Normal Fit")

# Vertical lines for mean & median
ax1.axvline(df_marks["Marks"].mean(),   color="red",    linestyle="--", linewidth=1.5, label=f"Mean  = {df_marks['Marks'].mean():.1f}")
ax1.axvline(df_marks["Marks"].median(), color="green",  linestyle=":",  linewidth=1.5, label=f"Median = {df_marks['Marks'].median():.1f}")

skew_marks = df_marks["Marks"].skew()
ax1.set_title(f"Student Marks Distribution\n{describe_skewness(skew_marks)}", fontsize=13)
ax1.set_xlabel("Marks (out of 100)", fontsize=11)
ax1.set_ylabel("Frequency", fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3)

## --- Plot B: Salary Distribution ---
ax2 = axes[1]

sns.histplot(
    data=df_salary, x="Salary",
    bins=25,
    kde=True,               # ← KDE curve (bonus requirement)
    color="#DD8452",
    edgecolor="white",
    linewidth=0.5,
    ax=ax2,
)

ax2.axvline(df_salary["Salary"].mean(),   color="red",   linestyle="--", linewidth=1.5, label=f"Mean   = ₹{df_salary['Salary'].mean():,.0f}")
ax2.axvline(df_salary["Salary"].median(), color="green", linestyle=":",  linewidth=1.5, label=f"Median = ₹{df_salary['Salary'].median():,.0f}")

skew_salary = df_salary["Salary"].skew()
ax2.set_title(f"Salary Distribution\n{describe_skewness(skew_salary)}", fontsize=13)
ax2.set_xlabel("Annual Salary (₹)", fontsize=11)
ax2.set_ylabel("Frequency", fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(axis="y", alpha=0.3)
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))

plt.tight_layout()
plt.savefig("distribution_analysis.png", dpi=150, bbox_inches="tight")
plt.show()
print("✅  Plot saved as distribution_analysis.png")

# ─────────────────────────────────────────────
# 4. BONUS — KDE-ONLY OVERLAY COMPARISON
# ─────────────────────────────────────────────

fig2, ax3 = plt.subplots(figsize=(10, 5))

# Normalise both datasets to [0,1] so they share an x-axis
marks_norm  = (student_marks - student_marks.min()) / (student_marks.max() - student_marks.min())
salary_norm = (salary_data   - salary_data.min())   / (salary_data.max()   - salary_data.min())

sns.kdeplot(marks_norm,  ax=ax3, fill=True, color="#4C72B0", alpha=0.4, label="Student Marks (normalised)")
sns.kdeplot(salary_norm, ax=ax3, fill=True, color="#DD8452", alpha=0.4, label="Salary (normalised)")

ax3.set_title("KDE Comparison — Marks vs Salary (normalised scale)", fontsize=13)
ax3.set_xlabel("Normalised Value", fontsize=11)
ax3.set_ylabel("Density", fontsize=11)
ax3.legend(fontsize=10)
ax3.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("kde_comparison.png", dpi=150, bbox_inches="tight")
plt.show()
print("✅  KDE comparison saved as kde_comparison.png")

# ─────────────────────────────────────────────
# 5. SUMMARY STATISTICS
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("         DISTRIBUTION ANALYSIS — SUMMARY")
print("="*55)

for label, series in [("Student Marks", df_marks["Marks"]), ("Salary", df_salary["Salary"])]:
    skew = series.skew()
    kurt = series.kurt()
    print(f"\n📊  {label}")
    print(f"    Count   : {len(series)}")
    print(f"    Mean    : {series.mean():.2f}")
    print(f"    Median  : {series.median():.2f}")
    print(f"    Std Dev : {series.std():.2f}")
    print(f"    Skewness: {skew:.4f}  → {describe_skewness(skew)}")
    print(f"    Kurtosis: {kurt:.4f}  → {'Leptokurtic (heavy tails)' if kurt > 0 else 'Platykurtic (light tails)'}")

print("\n" + "="*55)
print("Key Insight:")
print("  • Mean > Median  →  Right-skewed distribution")
print("  • Mean < Median  →  Left-skewed  distribution")
print("  • Mean ≈ Median  →  Symmetric    distribution")
print("="*55)