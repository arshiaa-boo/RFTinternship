


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─────────────────────────────────────────────
# 1. DATASET
# ─────────────────────────────────────────────

categories = ["FOOD", "TRAVEL", "SHOPPING"]
expenses   = [500, 300, 200]

# ─────────────────────────────────────────────
# 2. FIND HIGHEST CATEGORY (for explode/highlight)
# ─────────────────────────────────────────────

max_index = expenses.index(max(expenses))

# Explode the highest slice outward
explode = [0.0] * len(categories)
explode[max_index] = 0.12          # Pull out the biggest slice

# ─────────────────────────────────────────────
# 3. COLORS
# ─────────────────────────────────────────────

colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]
# Make the highest slice slightly brighter by using full opacity,
# others slightly muted
alphas = [1.0 if i == max_index else 0.75 for i in range(len(categories))]

# ─────────────────────────────────────────────
# 4. PERCENTAGE LABEL FORMATTER
# ─────────────────────────────────────────────

def autopct_format(pct):
    """Show percentage AND actual value."""
    total = sum(expenses)
    val   = int(round(pct * total / 100.0))
    return f"{pct:.1f}%\n(₹{val})"

# ─────────────────────────────────────────────
# 5. FIGURE SETUP
# ─────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.patch.set_facecolor("#F8F9FA")
fig.suptitle(
    "Day 14 — Category Breakdown of Expenses",
    fontsize=16, fontweight="bold", y=1.02, color="#2C3E50"
)

# ─────────────────────────────────────────────
# 6. PLOT A — STANDARD PIE CHART WITH BONUS FEATURES
# ─────────────────────────────────────────────

ax1 = axes[0]
ax1.set_facecolor("#F8F9FA")

wedges, texts, autotexts = ax1.pie(
    expenses,
    labels      = categories,
    explode     = explode,
    colors      = colors,
    autopct     = autopct_format,       # ← Percentage labels (bonus)
    startangle  = 140,
    pctdistance = 0.75,
    wedgeprops  = dict(edgecolor="white", linewidth=2.5),
    textprops   = dict(fontsize=11, fontweight="bold"),
    shadow      = True,
)

# Style percentage text
for i, autotext in enumerate(autotexts):
    autotext.set_fontsize(9)
    autotext.set_color("white")
    autotext.set_fontweight("bold")

# Style category labels
for i, text in enumerate(texts):
    text.set_fontsize(12)
    text.set_fontweight("bold")
    if i == max_index:
        text.set_color("#E74C3C")       # ← Highlight highest label in red
        text.set_fontsize(13)

# Draw a circle in the middle → Donut effect (modern look)
centre_circle = plt.Circle((0, 0), 0.45, fc="#F8F9FA", linewidth=1.5,
                             edgecolor="white")
ax1.add_patch(centre_circle)

# Centre annotation
ax1.text(0, 0.05, "Total", ha="center", va="center",
         fontsize=11, color="#7F8C8D", fontweight="bold")
ax1.text(0, -0.18, f"₹{sum(expenses)}", ha="center", va="center",
         fontsize=14, color="#2C3E50", fontweight="bold")

ax1.set_title("Expense Distribution\n(Highest Category Highlighted)",
              fontsize=12, pad=15, color="#2C3E50")

# ─────────────────────────────────────────────
# 7. PLOT B — HORIZONTAL BAR CHART (Composition Context)
# ─────────────────────────────────────────────

ax2 = axes[1]
ax2.set_facecolor("#F8F9FA")

bars = ax2.barh(
    categories,
    expenses,
    color   = [c for c in colors],
    edgecolor = "white",
    linewidth = 1.5,
    height  = 0.5,
)

# Highlight highest bar with a border
bars[max_index].set_edgecolor("#E74C3C")
bars[max_index].set_linewidth(3)

# Add value + percentage labels inside/outside bars
total = sum(expenses)
for i, (bar, val) in enumerate(zip(bars, expenses)):
    pct = val / total * 100
    ax2.text(
        val + 8, bar.get_y() + bar.get_height() / 2,
        f"₹{val}  ({pct:.1f}%)",
        va="center", ha="left", fontsize=11, fontweight="bold",
        color="#E74C3C" if i == max_index else "#2C3E50"
    )

# Star annotation on highest bar
ax2.annotate(
    f"** Highest",
    xy=(expenses[max_index], max_index),
    xytext=(expenses[max_index] - 120, max_index + 0.35),
    fontsize=10, color="#E74C3C", fontweight="bold",
)

ax2.set_xlim(0, max(expenses) * 1.45)
ax2.set_xlabel("Amount Spent (₹)", fontsize=11, color="#2C3E50")
ax2.set_title("Expense Comparison by Category", fontsize=12, pad=15, color="#2C3E50")
ax2.spines[["top", "right"]].set_visible(False)
ax2.tick_params(colors="#2C3E50", labelsize=11)
ax2.grid(axis="x", alpha=0.3, linestyle="--")

# ─────────────────────────────────────────────
# 8. SHARED LEGEND
# ─────────────────────────────────────────────

legend_patches = [
    mpatches.Patch(color=colors[i],
                   label=f"{categories[i]}: ₹{expenses[i]} ({expenses[i]/total*100:.1f}%)")
    for i in range(len(categories))
]
fig.legend(
    handles=legend_patches,
    loc="lower center",
    ncol=3,
    fontsize=10,
    frameon=True,
    fancybox=True,
    shadow=True,
    bbox_to_anchor=(0.5, -0.04),
)

plt.tight_layout()
plt.savefig("category_breakdown.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.show()
print("Plot saved as category_breakdown.png")

# ─────────────────────────────────────────────
# 9. SUMMARY
# ─────────────────────────────────────────────

print("\n" + "="*45)
print("      EXPENSE CATEGORY BREAKDOWN")
print("="*45)
for cat, exp in zip(categories, expenses):
    bar   = "█" * (exp // 20)
    pct   = exp / total * 100
    tag   = " << HIGHEST" if exp == max(expenses) else ""
    print(f"  {cat:<10} ₹{exp:>5}  ({pct:>5.1f}%)  {bar}{tag}")
print("-"*45)
print(f"  {'TOTAL':<10} ₹{total:>5}  (100.0%)")
print("="*45)
