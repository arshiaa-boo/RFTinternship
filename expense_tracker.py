
import re
import csv
import os
from datetime import datetime
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------

DATA_FILE = "data/transactions.csv"
CHARTS_DIR = "charts"
OUTPUTS_DIR = "outputs"

# A simple, extensible keyword -> category map. Add new keywords any time;
# no need to touch the categorization logic itself.
CATEGORY_RULES = {
    "Groceries":   ["grocery", "bazaar", "supermarket", "big bazaar", "dmart"],
    "Food & Dining": ["zomato", "swiggy", "restaurant", "cafe", "dinner", "lunch"],
    "Transport":   ["uber", "ola", "petrol", "fuel", "metro", "cab"],
    "Utilities":   ["electricity", "water bill", "internet", "airtel", "bses", "recharge", "jio"],
    "Rent":        ["rent payment", "rent"],
    "Entertainment": ["netflix", "spotify", "movie", "pvr", "prime video", "hotstar"],
    "Health & Fitness": ["pharmacy", "apollo", "gym", "hospital", "doctor"],
    "Shopping":    ["amazon", "flipkart", "myntra", "shopping"],
    "Income":      ["salary", "freelance", "income", "payment received", "bonus"],
}
DEFAULT_CATEGORY = "Other"

MONTHLY_BUDGETS = {
    "Groceries": 6000,
    "Food & Dining": 1800,
    "Transport": 800,
    "Utilities": 3500,
    "Rent": 15000,
    "Entertainment": 700,
    "Health & Fitness": 1200,
    "Shopping": 4000,
    "Other": 1000,
}


# ---------------------------------------------------------------------
# 1. Import monthly expense data
# ---------------------------------------------------------------------

def load_transactions(path: str) -> pd.DataFrame:
    """Load raw transactions from CSV and parse dates/amounts."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


# ---------------------------------------------------------------------
# 2. Categorize expenses automatically
# ---------------------------------------------------------------------

def categorize(description: str) -> str:
    text = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if re.search(re.escape(kw), text):
                return category
    return DEFAULT_CATEGORY


def add_categories(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category"] = df["description"].apply(categorize)
    df["type"] = df["amount"].apply(lambda a: "Income" if a > 0 else "Expense")
    return df


# ---------------------------------------------------------------------
# 3. Calculate monthly savings
# ---------------------------------------------------------------------

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("month").apply(
        lambda g: pd.Series({
            "income": g.loc[g["amount"] > 0, "amount"].sum(),
            "expenses": -g.loc[g["amount"] < 0, "amount"].sum(),
        }),
        include_groups=False,
    )
    grp["savings"] = grp["income"] - grp["expenses"]
    grp["savings_rate_%"] = (grp["savings"] / grp["income"] * 100).round(1)
    return grp.reset_index()


# ---------------------------------------------------------------------
# 4. Generate budget summary
# ---------------------------------------------------------------------

def budget_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-category spend vs budget, using only expense rows (excludes Income)."""
    exp = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp["amount"] = -exp["amount"]

    n_months = exp["month"].nunique() or 1
    cat_totals = exp.groupby("category")["amount"].sum()

    rows = []
    for cat, total in cat_totals.items():
        avg_monthly = total / n_months
        budget = MONTHLY_BUDGETS.get(cat, 1500)
        rows.append({
            "category": cat,
            "total_spent": round(total, 2),
            "avg_monthly_spent": round(avg_monthly, 2),
            "monthly_budget": budget,
            "status": "Over Budget" if avg_monthly > budget else "Within Budget",
            "variance": round(budget - avg_monthly, 2),
        })

    result = pd.DataFrame(rows).sort_values("total_spent", ascending=False)
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------
# 5. Visualize spending trends
# ---------------------------------------------------------------------

def make_charts(df: pd.DataFrame, summary: pd.DataFrame, budget: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    # --- Chart 1: Income vs Expenses vs Savings per month ---
    fig, ax = plt.subplots(figsize=(8, 5))
    x = summary["month"]
    width = 0.35
    idx = range(len(x))
    ax.bar([i - width / 2 for i in idx], summary["income"], width, label="Income", color="#2e7d32")
    ax.bar([i + width / 2 for i in idx], summary["expenses"], width, label="Expenses", color="#c62828")
    ax.plot(idx, summary["savings"], marker="o", color="#1565c0", linewidth=2, label="Savings")
    ax.set_xticks(list(idx))
    ax.set_xticklabels(x)
    ax.set_ylabel("Amount (Rs)")
    ax.set_title("Monthly Income vs Expenses vs Savings")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "monthly_income_vs_expense.png"), dpi=150)
    plt.close(fig)

    # --- Chart 2: Spend by category (pie) ---
    exp_by_cat = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp_by_cat["amount"] = -exp_by_cat["amount"]
    cat_totals = exp_by_cat.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        cat_totals.values,
        labels=cat_totals.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.tab20.colors,
    )
    ax.set_title("Total Spending by Category")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "spending_by_category.png"), dpi=150)
    plt.close(fig)

    # --- Chart 3: Budget vs actual (avg monthly) per category ---
    fig, ax = plt.subplots(figsize=(9, 5))
    idx = range(len(budget))
    ax.bar([i - 0.2 for i in idx], budget["avg_monthly_spent"], width=0.4, label="Avg Monthly Spent", color="#ef6c00")
    ax.bar([i + 0.2 for i in idx], budget["monthly_budget"], width=0.4, label="Budget", color="#455a64")
    ax.set_xticks(list(idx))
    ax.set_xticklabels(budget["category"], rotation=35, ha="right")
    ax.set_ylabel("Amount (Rs)")
    ax.set_title("Average Monthly Spend vs Budget by Category")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "budget_vs_actual.png"), dpi=150)
    plt.close(fig)

    # --- Chart 4: Daily spending trend (all months) ---
    daily = df[df["amount"] < 0].groupby("date")["amount"].sum().abs()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily.index, daily.values, color="#6a1b9a", linewidth=1.5)
    ax.fill_between(daily.index, daily.values, alpha=0.2, color="#6a1b9a")
    ax.set_title("Daily Spending Trend")
    ax.set_ylabel("Amount (Rs)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "daily_spending_trend.png"), dpi=150)
    plt.close(fig)

    return [
        "monthly_income_vs_expense.png",
        "spending_by_category.png",
        "budget_vs_actual.png",
        "daily_spending_trend.png",
    ]


# ---------------------------------------------------------------------
# 6. Export final report
# ---------------------------------------------------------------------

def export_report(df, summary, budget, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # Categorized transactions (CSV)
    df.to_csv(os.path.join(out_dir, "categorized_transactions.csv"), index=False)

    # Monthly summary (CSV)
    summary.to_csv(os.path.join(out_dir, "monthly_summary.csv"), index=False)

    # Budget summary (CSV)
    budget.to_csv(os.path.join(out_dir, "budget_summary.csv"), index=False)

    # Human-readable text report
    lines = []
    lines.append("=" * 60)
    lines.append("  SMART EXPENSE TRACKER — BUDGET REPORT")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("MONTHLY SUMMARY")
    lines.append("-" * 60)
    for _, row in summary.iterrows():
        lines.append(
            f"{row['month']}: Income ₹{row['income']:,.0f} | "
            f"Expenses ₹{row['expenses']:,.0f} | "
            f"Savings ₹{row['savings']:,.0f} ({row['savings_rate_%']}%)"
        )
    lines.append("")
    avg_savings_rate = summary["savings_rate_%"].mean()
    lines.append(f"Average savings rate across all months: {avg_savings_rate:.1f}%")
    lines.append("")
    lines.append("BUDGET vs ACTUAL (average monthly)")
    lines.append("-" * 60)
    for _, row in budget.iterrows():
        flag = "⚠️ " if row["status"] == "Over Budget" else "✅ "
        lines.append(
            f"{flag}{row['category']:<18} spent ₹{row['avg_monthly_spent']:>8,.0f} "
            f"/ budget ₹{row['monthly_budget']:>8,.0f}  ({row['status']})"
        )
    lines.append("")
    over_budget = budget[budget["status"] == "Over Budget"]
    if not over_budget.empty:
        lines.append("Categories exceeding budget: " + ", ".join(over_budget["category"]))
    else:
        lines.append("All categories are within budget. 🎉")
    lines.append("")
    lines.append("=" * 60)

    report_text = "\n".join(lines)
    with open(os.path.join(out_dir, "budget_report.txt"), "w") as f:
        f.write(report_text)

    return report_text


# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------

def main():
    print("Step 1/6: Importing transaction data...")
    df = load_transactions(DATA_FILE)
    print(f"  Loaded {len(df)} transactions across {df['month'].nunique()} months.")

    print("Step 2/6: Categorizing expenses...")
    df = add_categories(df)

    print("Step 3/6: Calculating monthly savings...")
    summary = monthly_summary(df)

    print("Step 4/6: Generating budget summary...")
    budget = budget_summary(df)

    print("Step 5/6: Creating visualizations...")
    charts = make_charts(df, summary, budget, CHARTS_DIR)
    print(f"  Saved charts: {charts}")

    print("Step 6/6: Exporting final report...")
    report_text = export_report(df, summary, budget, OUTPUTS_DIR)

    print("\n" + report_text)
    print(f"\nAll outputs saved in '{OUTPUTS_DIR}/' and charts in '{CHARTS_DIR}/'.")


if __name__ == "__main__":
    main()
