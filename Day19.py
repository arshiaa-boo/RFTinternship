import matplotlib
matplotlib.use("Agg")  # Fix for Python 3.13 PNG backend error

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import argrelextrema

# ─────────────────────────────────────────
#  DATASET CREATION — 3 STOCKS, 1 YEAR
# ─────────────────────────────────────────

np.random.seed(42)
dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="B")  # Business days only

def generate_stock(start_price, volatility, trend):
    prices = [start_price]
    for _ in range(len(dates) - 1):
        change = np.random.normal(trend, volatility)
        prices.append(round(max(prices[-1] + change, 1), 2))
    return prices

stock_data = {
    "Date":    dates,
    "AAPL":    generate_stock(185, 2.5,  0.08),
    "GOOGL":   generate_stock(140, 3.0,  0.05),
    "TSLA":    generate_stock(250, 6.0, -0.03),
}

df = pd.DataFrame(stock_data)
df.set_index("Date", inplace=True)

print("=" * 65)
print("       STOCK / TIME-SERIES ANALYSIS — DAY 19 PROJECT")
print("=" * 65)
print(f"\nDataset: {len(df)} trading days  |  Stocks: AAPL, GOOGL, TSLA")
print("\nFirst 5 rows:")
print(df.head().to_string())
print("\nLast 5 rows:")
print(df.tail().to_string())


# ─────────────────────────────────────────
#  MOVING AVERAGES (7-day and 30-day)
# ─────────────────────────────────────────

for stock in ["AAPL", "GOOGL", "TSLA"]:
    df[f"{stock}_MA7"]  = df[stock].rolling(window=7).mean()
    df[f"{stock}_MA30"] = df[stock].rolling(window=30).mean()

print("\n" + "=" * 65)
print("  MOVING AVERAGES (sample — AAPL)")
print("=" * 65)
print(df[["AAPL", "AAPL_MA7", "AAPL_MA30"]].dropna().head(10).to_string())


# ─────────────────────────────────────────
#  IDENTIFY PEAKS & DROPS
# ─────────────────────────────────────────

def find_peaks_drops(series, order=10):
    prices = series.values
    peak_idx = argrelextrema(prices, np.greater, order=order)[0]
    drop_idx = argrelextrema(prices, np.less,    order=order)[0]
    peaks = series.iloc[peak_idx]
    drops = series.iloc[drop_idx]
    return peaks, drops

print("\n" + "=" * 65)
print("  PEAKS & DROPS ANALYSIS")
print("=" * 65)

for stock in ["AAPL", "GOOGL", "TSLA"]:
    peaks, drops = find_peaks_drops(df[stock])
    print(f"\n  {stock}:")
    print(f"    Peaks ({len(peaks)}) — Top 3 highest:")
    for date, val in peaks.nlargest(3).items():
        print(f"      {date.strftime('%Y-%m-%d')}  :  ${val:.2f}")
    print(f"    Drops ({len(drops)}) — Top 3 lowest:")
    for date, val in drops.nsmallest(3).items():
        print(f"      {date.strftime('%Y-%m-%d')}  :  ${val:.2f}")


# ─────────────────────────────────────────
#  BONUS: VOLATILITY DETECTION
# ─────────────────────────────────────────

print("\n" + "=" * 65)
print("  BONUS: VOLATILITY ANALYSIS (30-day rolling std dev)")
print("=" * 65)

for stock in ["AAPL", "GOOGL", "TSLA"]:
    df[f"{stock}_VOL"] = df[stock].rolling(window=30).std()
    avg_vol  = df[f"{stock}_VOL"].mean()
    max_vol  = df[f"{stock}_VOL"].max()
    max_date = df[f"{stock}_VOL"].idxmax()
    print(f"\n  {stock}:")
    print(f"    Average Volatility : {avg_vol:.2f}")
    print(f"    Max Volatility     : {max_vol:.2f}  on {max_date.strftime('%Y-%m-%d')}")
    level = "High" if avg_vol > 5 else "Moderate" if avg_vol > 2 else "Low"
    print(f"    Volatility Level   : {level}")


# ─────────────────────────────────────────
#  BONUS: STOCK COMPARISON SUMMARY
# ─────────────────────────────────────────

print("\n" + "=" * 65)
print("  BONUS: STOCK COMPARISON SUMMARY")
print("=" * 65)

for stock in ["AAPL", "GOOGL", "TSLA"]:
    start = df[stock].iloc[0]
    end   = df[stock].iloc[-1]
    ret   = ((end - start) / start) * 100
    high  = df[stock].max()
    low   = df[stock].min()
    print(f"\n  {stock}:")
    print(f"    Start Price   : ${start:.2f}")
    print(f"    End Price     : ${end:.2f}")
    print(f"    Annual Return : {ret:+.2f}%")
    print(f"    52-Week High  : ${high:.2f}")
    print(f"    52-Week Low   : ${low:.2f}")


# ─────────────────────────────────────────
#  VISUALIZATIONS
# ─────────────────────────────────────────

STOCK_COLORS = {
    "AAPL":  "#00D4AA",
    "GOOGL": "#4D9FFF",
    "TSLA":  "#FF6B6B",
}

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor("#0D1117")
fig.suptitle("Stock / Time-Series Analysis — Day 19", fontsize=20,
             fontweight="bold", color="white", y=0.98)

# ── Plot 1: AAPL Price Trend + Moving Averages ──
ax1 = fig.add_subplot(3, 2, (1, 2))   # full-width top row
ax1.set_facecolor("#161B22")
for spine in ax1.spines.values():
    spine.set_edgecolor("#30363D")

ax1.plot(df.index, df["AAPL"], color=STOCK_COLORS["AAPL"],
         linewidth=1.2, label="AAPL Price", alpha=0.9)
ax1.plot(df.index, df["AAPL_MA7"],  color="#F4A261", linewidth=1.5,
         linestyle="--", label="7-Day MA")
ax1.plot(df.index, df["AAPL_MA30"], color="#E63946", linewidth=2.0,
         linestyle="-",  label="30-Day MA")

# Mark peaks and drops on AAPL
aapl_peaks, aapl_drops = find_peaks_drops(df["AAPL"])
ax1.scatter(aapl_peaks.index, aapl_peaks.values, color="#FFD700",
            s=60, zorder=5, label="Peaks", marker="^")
ax1.scatter(aapl_drops.index, aapl_drops.values, color="#FF4444",
            s=60, zorder=5, label="Drops", marker="v")

ax1.set_title("AAPL — Price Trend with Moving Averages, Peaks & Drops",
              color="white", fontsize=13, fontweight="bold", pad=10)
ax1.set_ylabel("Price ($)", color="#8B949E", fontsize=10)
ax1.tick_params(colors="#C9D1D9")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax1.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=9)
ax1.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax1.xaxis.set_tick_params(labelcolor="#C9D1D9")


# ── Plot 2: GOOGL Price Trend + MA ──
ax2 = fig.add_subplot(3, 2, 3)
ax2.set_facecolor("#161B22")
for spine in ax2.spines.values(): spine.set_edgecolor("#30363D")

ax2.plot(df.index, df["GOOGL"], color=STOCK_COLORS["GOOGL"],
         linewidth=1.2, label="GOOGL Price", alpha=0.9)
ax2.plot(df.index, df["GOOGL_MA7"],  color="#F4A261", linewidth=1.4,
         linestyle="--", label="7-Day MA")
ax2.plot(df.index, df["GOOGL_MA30"], color="#E63946", linewidth=1.8,
         label="30-Day MA")
ax2.set_title("GOOGL — Price Trend + Moving Averages",
              color="white", fontsize=11, fontweight="bold", pad=8)
ax2.set_ylabel("Price ($)", color="#8B949E", fontsize=9)
ax2.tick_params(colors="#C9D1D9")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax2.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=8)
ax2.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax2.xaxis.set_tick_params(labelcolor="#C9D1D9")


# ── Plot 3: TSLA Price Trend + MA ──
ax3 = fig.add_subplot(3, 2, 4)
ax3.set_facecolor("#161B22")
for spine in ax3.spines.values(): spine.set_edgecolor("#30363D")

ax3.plot(df.index, df["TSLA"], color=STOCK_COLORS["TSLA"],
         linewidth=1.2, label="TSLA Price", alpha=0.9)
ax3.plot(df.index, df["TSLA_MA7"],  color="#F4A261", linewidth=1.4,
         linestyle="--", label="7-Day MA")
ax3.plot(df.index, df["TSLA_MA30"], color="#E63946", linewidth=1.8,
         label="30-Day MA")
ax3.set_title("TSLA — Price Trend + Moving Averages",
              color="white", fontsize=11, fontweight="bold", pad=8)
ax3.set_ylabel("Price ($)", color="#8B949E", fontsize=9)
ax3.tick_params(colors="#C9D1D9")
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax3.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=8)
ax3.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax3.xaxis.set_tick_params(labelcolor="#C9D1D9")


# ── Plot 4: Volatility Comparison (Bonus) ──
ax4 = fig.add_subplot(3, 2, 5)
ax4.set_facecolor("#161B22")
for spine in ax4.spines.values(): spine.set_edgecolor("#30363D")

for stock in ["AAPL", "GOOGL", "TSLA"]:
    ax4.plot(df.index, df[f"{stock}_VOL"], color=STOCK_COLORS[stock],
             linewidth=1.4, label=f"{stock} Volatility")
ax4.set_title("Volatility Comparison — 30-Day Rolling Std Dev",
              color="white", fontsize=11, fontweight="bold", pad=8)
ax4.set_ylabel("Std Deviation ($)", color="#8B949E", fontsize=9)
ax4.tick_params(colors="#C9D1D9")
ax4.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax4.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=8)
ax4.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax4.xaxis.set_tick_params(labelcolor="#C9D1D9")


# ── Plot 5: Multiple Stock Comparison — Normalized (Bonus) ──
ax5 = fig.add_subplot(3, 2, 6)
ax5.set_facecolor("#161B22")
for spine in ax5.spines.values(): spine.set_edgecolor("#30363D")

for stock in ["AAPL", "GOOGL", "TSLA"]:
    normalized = (df[stock] / df[stock].iloc[0]) * 100  # base 100
    ax5.plot(df.index, normalized, color=STOCK_COLORS[stock],
             linewidth=1.4, label=stock)
ax5.axhline(100, color="#444", linewidth=1, linestyle="--")
ax5.set_title("Stock Comparison — Normalized to Base 100",
              color="white", fontsize=11, fontweight="bold", pad=8)
ax5.set_ylabel("Normalized Price", color="#8B949E", fontsize=9)
ax5.tick_params(colors="#C9D1D9")
ax5.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax5.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax5.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", fontsize=8)
ax5.yaxis.set_tick_params(labelcolor="#C9D1D9")
ax5.xaxis.set_tick_params(labelcolor="#C9D1D9")


plt.tight_layout(rect=[0, 0, 1, 0.96])
output_path = "stock_analysis.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
plt.close()
print("\nChart saved to:", output_path)
print("\nAnalysis complete.")