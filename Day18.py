import matplotlib
matplotlib.use("Agg")  # Fix for Python 3.13 PNG backend error

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ─────────────────────────────────────────
#  DATASET CREATION
# ─────────────────────────────────────────

data = {
    "Movie Name": [
        "Inception", "The Dark Knight", "Interstellar", "Avengers: Endgame",
        "The Lion King", "Titanic", "Joker", "Parasite",
        "Spider-Man: No Way Home", "Top Gun: Maverick",
        "The Godfather", "Forrest Gump", "Pulp Fiction", "The Matrix",
        "Gladiator", "Toy Story", "Finding Nemo", "Frozen",
        "The Avengers", "Black Panther"
    ],
    "Rating": [
        8.8, 9.0, 8.6, 8.4, 8.5, 7.9, 8.4, 8.6,
        8.2, 8.3, 9.2, 8.8, 8.9, 8.7,
        8.5, 8.3, 8.1, 7.4, 8.0, 7.3
    ],
    "Genre": [
        "Sci-Fi", "Action", "Sci-Fi", "Action",
        "Animation", "Drama", "Drama", "Drama",
        "Action", "Action",
        "Drama", "Drama", "Drama", "Sci-Fi",
        "Action", "Animation", "Animation", "Animation",
        "Action", "Action"
    ],
    "Revenue (Million $)": [
        836, 1005, 701, 2798, 1663, 2187, 1079, 258,
        1901, 1493, 245, 678, 213, 463,
        457, 362, 940, 1280, 1519, 1347
    ]
}

df = pd.DataFrame(data)

print("=" * 60)
print("       MOVIE DATASET ANALYSIS — DAY 18 PROJECT")
print("=" * 60)
print(f"\nDataset Shape: {df.shape[0]} movies, {df.shape[1]} columns")
print("\nFirst 5 rows:")
print(df.head().to_string(index=False))


# ─────────────────────────────────────────
#  ANALYSIS 1: HIGHEST RATED MOVIES
# ─────────────────────────────────────────

print("\n" + "=" * 60)
print("  TOP 10 HIGHEST RATED MOVIES")
print("=" * 60)

top_rated = df.sort_values("Rating", ascending=False).head(10)
print(top_rated[["Movie Name", "Genre", "Rating"]].to_string(index=False))


# ─────────────────────────────────────────
#  ANALYSIS 2: MOST PROFITABLE GENRES
# ─────────────────────────────────────────

print("\n" + "=" * 60)
print("  MOST PROFITABLE GENRES")
print("=" * 60)

genre_revenue = (
    df.groupby("Genre")["Revenue (Million $)"]
    .agg(["sum", "mean", "count"])
    .rename(columns={"sum": "Total Revenue", "mean": "Avg Revenue", "count": "Movie Count"})
    .sort_values("Total Revenue", ascending=False)
)
genre_revenue["Total Revenue"] = genre_revenue["Total Revenue"].map("${:,.0f}M".format)
genre_revenue["Avg Revenue"]   = genre_revenue["Avg Revenue"].map("${:,.0f}M".format)
print(genre_revenue.to_string())


# ─────────────────────────────────────────
#  BONUS: CORRELATION — RATING vs REVENUE
# ─────────────────────────────────────────

print("\n" + "=" * 60)
print("  BONUS: CORRELATION — RATING vs REVENUE")
print("=" * 60)

corr, p_value = stats.pearsonr(df["Rating"], df["Revenue (Million $)"])
print(f"  Pearson Correlation Coefficient : {corr:.4f}")
print(f"  P-Value                         : {p_value:.4f}")

if abs(corr) >= 0.7:
    strength = "Strong"
elif abs(corr) >= 0.4:
    strength = "Moderate"
else:
    strength = "Weak"
direction = "positive" if corr > 0 else "negative"
print(f"  Interpretation                  : {strength} {direction} correlation")


# ─────────────────────────────────────────
#  BONUS: TOP 5 MOVIES BY REVENUE
# ─────────────────────────────────────────

print("\n" + "=" * 60)
print("  BONUS: TOP 5 MOVIES BY REVENUE")
print("=" * 60)

top5 = df.sort_values("Revenue (Million $)", ascending=False).head(5)
for rank, (_, row) in enumerate(top5.iterrows(), 1):
    print(f"  {rank}. {row['Movie Name']:<30} ${row['Revenue (Million $)']:,}M   Rating: {row['Rating']}")


# ─────────────────────────────────────────
#  VISUALIZATIONS
# ─────────────────────────────────────────

COLORS = {
    "Action":    "#E63946",
    "Drama":     "#457B9D",
    "Sci-Fi":    "#2A9D8F",
    "Animation": "#F4A261",
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor("#0D1117")
fig.suptitle(
    "Movie Dataset Analysis — Day 18",
    fontsize=20, fontweight="bold", color="white", y=0.98
)

for ax in axes.flat:
    ax.set_facecolor("#161B22")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363D")


# ── Plot 1: Genre vs Total Revenue ──────
ax1 = axes[0, 0]
genre_rev_raw = (
    df.groupby("Genre")["Revenue (Million $)"]
    .sum()
    .sort_values(ascending=False)
)
bar_colors = [COLORS.get(g, "#888") for g in genre_rev_raw.index]
bars = ax1.bar(genre_rev_raw.index, genre_rev_raw.values, color=bar_colors,
               edgecolor="#0D1117", linewidth=1.2, width=0.6)
ax1.set_title("Genre vs Total Revenue", color="white", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Genre", color="#8B949E", fontsize=10)
ax1.set_ylabel("Total Revenue (Million $)", color="#8B949E", fontsize=10)
ax1.tick_params(colors="#C9D1D9")
ax1.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax1.xaxis.set_tick_params(labelcolor="#C9D1D9")
for bar in bars:
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 40,
        f"${int(bar.get_height()):,}M",
        ha="center", va="bottom", color="white", fontsize=8.5, fontweight="bold"
    )
ax1.set_ylim(0, genre_rev_raw.max() * 1.18)


# ── Plot 2: Rating Distribution (Histogram) ──
ax2 = axes[0, 1]
n, bins, patches = ax2.hist(
    df["Rating"], bins=8, color="#2A9D8F",
    edgecolor="#0D1117", linewidth=1.2
)
ax2.set_title("Rating Distribution", color="white", fontsize=13, fontweight="bold", pad=10)
ax2.set_xlabel("Rating", color="#8B949E", fontsize=10)
ax2.set_ylabel("Number of Movies", color="#8B949E", fontsize=10)
ax2.tick_params(colors="#C9D1D9")
ax2.axvline(df["Rating"].mean(), color="#F4A261", linewidth=2, linestyle="--", label=f"Mean: {df['Rating'].mean():.2f}")
ax2.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=9)


# ── Plot 3: Rating vs Revenue Scatter (Bonus) ──
ax3 = axes[1, 0]
genre_list = df["Genre"].unique()
for genre in genre_list:
    subset = df[df["Genre"] == genre]
    ax3.scatter(
        subset["Rating"], subset["Revenue (Million $)"],
        color=COLORS.get(genre, "#888"), s=90, label=genre,
        edgecolors="white", linewidths=0.5, alpha=0.9, zorder=3
    )
# Regression line
m, b, *_ = stats.linregress(df["Rating"], df["Revenue (Million $)"])
x_line = np.linspace(df["Rating"].min(), df["Rating"].max(), 100)
ax3.plot(x_line, m * x_line + b, color="#F4A261", linewidth=1.8,
         linestyle="--", label=f"Trend (r={corr:.2f})")
ax3.set_title("Rating vs Revenue (Correlation)", color="white", fontsize=13, fontweight="bold", pad=10)
ax3.set_xlabel("Rating", color="#8B949E", fontsize=10)
ax3.set_ylabel("Revenue (Million $)", color="#8B949E", fontsize=10)
ax3.tick_params(colors="#C9D1D9")
ax3.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=8.5)


# ── Plot 4: Top 5 Movies by Revenue (Bonus) ──
ax4 = axes[1, 1]
top5_sorted = top5.sort_values("Revenue (Million $)")
bar_cols4 = [COLORS.get(g, "#888") for g in top5_sorted["Genre"]]
hbars = ax4.barh(
    top5_sorted["Movie Name"], top5_sorted["Revenue (Million $)"],
    color=bar_cols4, edgecolor="#0D1117", linewidth=1.1, height=0.55
)
ax4.set_title("Top 5 Movies by Revenue", color="white", fontsize=13, fontweight="bold", pad=10)
ax4.set_xlabel("Revenue (Million $)", color="#8B949E", fontsize=10)
ax4.tick_params(colors="#C9D1D9")
for bar in hbars:
    ax4.text(
        bar.get_width() + 30,
        bar.get_y() + bar.get_height() / 2,
        f"${int(bar.get_width()):,}M",
        va="center", color="white", fontsize=8.5, fontweight="bold"
    )
ax4.set_xlim(0, top5_sorted["Revenue (Million $)"].max() * 1.2)


plt.tight_layout(rect=[0, 0, 1, 0.96])
output_path = "movie_analysis.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
plt.close()
print("\nChart saved to:", output_path)
print("\nAnalysis complete.")