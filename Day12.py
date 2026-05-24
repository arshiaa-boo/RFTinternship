import matplotlib.pyplot as plt
import numpy as np

# --- Dataset ------------------------------------------------------------------
STUDENTS = ["AMIT", "RIYA", "JOHN"]
MARKS     = [85, 92, 78]

# --- Console Output -----------------------------------------------------------
print("=" * 40)
print("  STUDENT PERFORMANCE DASHBOARD")
print("=" * 40)
for student, mark in zip(STUDENTS, MARKS):
    bar = "#" * (mark // 5)
    print(f"   {student:<6} : {mark}  {bar}")

avg = sum(MARKS) / len(MARKS)
topper = STUDENTS[MARKS.index(max(MARKS))]
print(f"\nAverage Marks : {avg:.1f}")
print(f"Topper        : {topper} ({max(MARKS)})")

# =============================================================================
# PART 1 — Simple Bar Chart
# =============================================================================
colors = ['steelblue' if m != max(MARKS) else 'green' for m in MARKS]

fig, ax = plt.subplots(figsize=(7, 5))

bars = ax.bar(STUDENTS, MARKS, color=colors, width=0.5, edgecolor='black', linewidth=0.8)

# Value labels on top of each bar
for bar, mark in zip(bars, MARKS):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(mark),
            ha='center', va='bottom',
            fontsize=11, fontweight='bold')

# Average line
ax.axhline(y=avg, color='red', linestyle='--',
           linewidth=1.5, label=f'Average: {avg:.1f}')

ax.set_title('Student Marks - Bar Chart', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Students', fontsize=11)
ax.set_ylabel('Marks', fontsize=11)
ax.set_ylim(0, 110)
ax.legend(fontsize=9)
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('simple_bar_chart.png', dpi=150)
plt.show()
print("\nSimple bar chart saved as: simple_bar_chart.png")

# =============================================================================
# PART 2 — BONUS: Grouped Bar Chart (Multiple Subjects)
# =============================================================================
MATH    = [85, 92, 78]
SCIENCE = [78, 88, 70]
ENGLISH = [90, 95, 82]

x     = np.arange(len(STUDENTS))
width = 0.25

fig2, ax2 = plt.subplots(figsize=(9, 6))

bar1 = ax2.bar(x - width,     MATH,    width, label='Math',    color='steelblue', edgecolor='black', linewidth=0.7)
bar2 = ax2.bar(x,             SCIENCE, width, label='Science', color='coral',     edgecolor='black', linewidth=0.7)
bar3 = ax2.bar(x + width,     ENGLISH, width, label='English', color='mediumseagreen', edgecolor='black', linewidth=0.7)

# Value labels on each bar
for bars in [bar1, bar2, bar3]:
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 1,
                 str(int(bar.get_height())),
                 ha='center', va='bottom', fontsize=8)

ax2.set_title('Student Performance - Grouped Bar Chart\n(Subject-wise Comparison)',
              fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Students', fontsize=11)
ax2.set_ylabel('Marks', fontsize=11)
ax2.set_xticks(x)
ax2.set_xticklabels(STUDENTS, fontsize=11)
ax2.set_ylim(0, 115)
ax2.legend(fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('grouped_bar_chart.png', dpi=150)
plt.show()
print("Grouped bar chart saved as: grouped_bar_chart.png")

# --- Subject-wise Summary -----------------------------------------------------
print("\n" + "=" * 40)
print("      SUBJECT-WISE SUMMARY")
print("=" * 40)
subjects = {'Math': MATH, 'Science': SCIENCE, 'English': ENGLISH}
for subj, scores in subjects.items():
    print(f"   {subj:<8} -> Avg: {sum(scores)/len(scores):.1f}  "
          f"High: {max(scores)}  Low: {min(scores)}")