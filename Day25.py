
import os
import sys
import argparse
import numpy as np
import pandas as pd

# ============================================================
# 0. CONFIG / CONSTANTS
# ============================================================
DEFAULT_CSV_PATH = "transactions.csv"
OUTPUT_DIR = "txn_report_output"
DEFAULT_HIGH_VALUE_THRESHOLD = 8000       # currency units
SUSPICIOUS_TXN_COUNT_STD = 2              # accounts w/ count > mean + N*std flagged
TOP_N_HIGHEST = 10


# ============================================================
# 1. SAMPLE DATA GENERATION (used only if no CSV is supplied)
# ============================================================
def generate_sample_data(path=DEFAULT_CSV_PATH, seed=42):
    rng = np.random.default_rng(seed)

    categories = ["Groceries", "Electronics", "Travel", "Utilities",
                  "Entertainment", "Healthcare", "Transfer", "Dining"]
    accounts = [f"ACC{1000 + i}" for i in range(25)]

    dates = pd.date_range("2024-01-01", periods=45, freq="D")

    rows = []
    txn_id = 1

    # normal transactions
    for _ in range(700):
        date = rng.choice(dates)
        account = rng.choice(accounts)
        category = rng.choice(categories)
        amount = round(float(rng.gamma(shape=2.0, scale=800)), 2)  # skewed, mostly small
        rows.append([txn_id, pd.Timestamp(date), account, amount, category])
        txn_id += 1

    # inject some high-value transactions
    for _ in range(15):
        date = rng.choice(dates)
        account = rng.choice(accounts)
        category = rng.choice(categories)
        amount = round(float(rng.uniform(9000, 25000)), 2)
        rows.append([txn_id, pd.Timestamp(date), account, amount, category])
        txn_id += 1

    # inject a "suspicious" account with an unusually high transaction count
    suspicious_account = "ACC9999"
    for _ in range(60):
        date = rng.choice(dates)
        category = rng.choice(categories)
        amount = round(float(rng.gamma(shape=2.0, scale=500)), 2)
        rows.append([txn_id, pd.Timestamp(date), suspicious_account, amount, category])
        txn_id += 1

    df = pd.DataFrame(rows, columns=["transaction_id", "date", "account_id", "amount", "category"])

    # inject exact duplicate transactions (same account/amount/date/category)
    dupes = df.sample(12, random_state=seed).copy()
    dupes["transaction_id"] = range(txn_id, txn_id + len(dupes))
    df = pd.concat([df, dupes], ignore_index=True)

    df = df.sort_values("date").reset_index(drop=True)
    df.to_csv(path, index=False)
    return df


# ============================================================
# 2. DATA LOADING
# ============================================================
def load_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"'{csv_path}' not found. Generating a sample dataset instead...")
        return generate_sample_data(csv_path)

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    if "account_id" not in df.columns:
        raise ValueError("CSV must contain an 'account_id' column.")
    if "amount" not in df.columns:
        raise ValueError("CSV must contain an 'amount' column.")
    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'date' column.")

    if "transaction_id" not in df.columns:
        df["transaction_id"] = range(1, len(df) + 1)
    if "category" not in df.columns:
        df["category"] = "Uncategorized"

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"]).reset_index(drop=True)

    return df


# ============================================================
# 3. ANALYSIS FUNCTIONS
# ============================================================
def detect_duplicates(df):
    """Flags rows that share the same account, amount, date, and category."""
    dup_cols = ["account_id", "amount", "date", "category"]
    is_dup = df.duplicated(subset=dup_cols, keep=False)
    return is_dup


def detect_high_value(df, threshold):
    return df["amount"] > threshold


def detect_suspicious_accounts(df, std_multiplier=SUSPICIOUS_TXN_COUNT_STD):
    """Accounts with a transaction count more than `std_multiplier` standard
    deviations above the mean are flagged as suspicious (unusually frequent)."""
    counts = df.groupby("account_id").size()
    mean, std = counts.mean(), counts.std(ddof=0)
    cutoff = mean + std_multiplier * std
    suspicious_accounts = counts[counts > cutoff].index.tolist()
    return suspicious_accounts, counts


def compute_risk_score(df, high_value_mask, dup_mask, suspicious_accounts):
    """
    Simple weighted risk score (0-100) per transaction:
      - Duplicate transaction:        +35
      - High-value transaction:       +30
      - Belongs to suspicious account: +25
      - Odd-hour-ish proxy (amount is a round number, e.g. ends in 000): +10
    Capped at 100.
    """
    score = pd.Series(0, index=df.index, dtype=float)
    score += dup_mask.astype(int) * 35
    score += high_value_mask.astype(int) * 30
    score += df["account_id"].isin(suspicious_accounts).astype(int) * 25
    round_amount_bonus = (df["amount"] % 1000 == 0).astype(int) * 10
    score += round_amount_bonus
    score = score.clip(upper=100)
    return score


def risk_level(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


def run_full_analysis(df, threshold):
    dup_mask = detect_duplicates(df)
    high_value_mask = detect_high_value(df, threshold)
    suspicious_accounts, account_counts = detect_suspicious_accounts(df)
    suspicious_mask = df["account_id"].isin(suspicious_accounts)

    risk_scores = compute_risk_score(df, high_value_mask, dup_mask, suspicious_accounts)

    result = df.copy()
    result["is_duplicate"] = dup_mask
    result["is_high_value"] = high_value_mask
    result["is_suspicious_account"] = suspicious_mask
    result["risk_score"] = risk_scores
    result["risk_level"] = result["risk_score"].apply(risk_level)

    return result, suspicious_accounts, account_counts


# ============================================================
# 4. CLI MODE: charts (matplotlib) + CSV export + text report
# ============================================================
def run_cli(csv_path, threshold):
    import matplotlib.pyplot as plt

    df = load_data(csv_path)
    result, suspicious_accounts, account_counts = run_full_analysis(df, threshold)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # ---- Chart 1: Transaction Category Chart ----
    cat_summary = result.groupby("category")["amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 6))
    bars = plt.bar(cat_summary.index, cat_summary.values, color="steelblue")
    plt.title("Transaction Category Breakdown (Total Amount)")
    plt.xlabel("Category")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=30, ha="right")
    for bar, val in zip(bars, cat_summary.values):
        plt.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,.0f}",
                  ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    cat_chart_path = os.path.join(OUTPUT_DIR, "transaction_category_chart.png")
    plt.savefig(cat_chart_path, dpi=150)
    plt.show()
    plt.close()

    # ---- Chart 2: Daily Transaction Trend ----
    daily = result.groupby(result["date"].dt.date)["amount"].sum()
    plt.figure(figsize=(10, 6))
    plt.plot(daily.index, daily.values, marker="o", markersize=3, color="darkorange")
    plt.title("Daily Transaction Trend (Total Amount)")
    plt.xlabel("Date")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    trend_chart_path = os.path.join(OUTPUT_DIR, "daily_transaction_trend.png")
    plt.savefig(trend_chart_path, dpi=150)
    plt.show()
    plt.close()

    # ---- Chart 3: Top 10 Highest Transactions ----
    top10 = result.sort_values("amount", ascending=False).head(TOP_N_HIGHEST)
    plt.figure(figsize=(10, 6))
    labels = [f"{row.account_id}\n#{row.transaction_id}" for row in top10.itertuples()]
    bars = plt.bar(labels, top10["amount"], color="crimson")
    plt.title(f"Top {TOP_N_HIGHEST} Highest Transactions")
    plt.xlabel("Account / Transaction ID")
    plt.ylabel("Amount")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    for bar, val in zip(bars, top10["amount"]):
        plt.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,.0f}",
                  ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    top10_chart_path = os.path.join(OUTPUT_DIR, "top10_highest_transactions.png")
    plt.savefig(top10_chart_path, dpi=150)
    plt.show()
    plt.close()

    # ---- Export suspicious transactions CSV ----
    # "Suspicious" = duplicate OR high-value OR from a suspicious account OR risk_level != Low
    suspicious_txns = result[
        result["is_duplicate"] | result["is_high_value"] |
        result["is_suspicious_account"] | (result["risk_level"] != "Low")
    ].sort_values("risk_score", ascending=False)

    suspicious_csv_path = os.path.join(OUTPUT_DIR, "suspicious_transactions.csv")
    suspicious_txns.to_csv(suspicious_csv_path, index=False)

    # ---- Full results CSV (with risk scores) ----
    full_csv_path = os.path.join(OUTPUT_DIR, "all_transactions_with_risk_scores.csv")
    result.to_csv(full_csv_path, index=False)

    # ---- Text report ----
    report_path = os.path.join(OUTPUT_DIR, "transaction_report.txt")
    with open(report_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("        TRANSACTION DATA ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Data source: {csv_path}\n")
        f.write(f"Total transactions: {len(result)}\n")
        f.write(f"Date range: {result['date'].min().date()} to {result['date'].max().date()}\n")
        f.write(f"High-value threshold: {threshold:,.2f}\n\n")

        f.write("-" * 60 + "\n")
        f.write("DUPLICATE TRANSACTIONS\n")
        f.write("-" * 60 + "\n")
        f.write(f"  Count: {int(result['is_duplicate'].sum())}\n\n")

        f.write("-" * 60 + "\n")
        f.write("HIGH-VALUE TRANSACTIONS\n")
        f.write("-" * 60 + "\n")
        f.write(f"  Count: {int(result['is_high_value'].sum())}\n\n")

        f.write("-" * 60 + "\n")
        f.write("SUSPICIOUS ACCOUNTS (unusually frequent transactions)\n")
        f.write("-" * 60 + "\n")
        f.write(f"  Mean txns/account: {account_counts.mean():.2f} | Std: {account_counts.std(ddof=0):.2f}\n")
        if suspicious_accounts:
            for acc in suspicious_accounts:
                f.write(f"    {acc}: {account_counts[acc]} transactions\n")
        else:
            f.write("    None found.\n")
        f.write("\n")

        f.write("-" * 60 + "\n")
        f.write("RISK LEVEL BREAKDOWN\n")
        f.write("-" * 60 + "\n")
        for level, count in result["risk_level"].value_counts().items():
            f.write(f"    {level:<8} {count}\n")
        f.write("\n")

        f.write("-" * 60 + "\n")
        f.write(f"TOP {TOP_N_HIGHEST} HIGHEST TRANSACTIONS\n")
        f.write("-" * 60 + "\n")
        for row in top10.itertuples():
            f.write(f"    #{row.transaction_id}  {row.account_id}  {row.amount:,.2f}  "
                     f"({row.category})  risk={row.risk_score:.0f}\n")
        f.write("\n")

        f.write("-" * 60 + "\n")
        f.write("FILES GENERATED\n")
        f.write("-" * 60 + "\n")
        f.write(f"  {cat_chart_path}\n  {trend_chart_path}\n  {top10_chart_path}\n")
        f.write(f"  {suspicious_csv_path}\n  {full_csv_path}\n")

    # ---- Console summary ----
    print("\n=== SUMMARY ===")
    print(f"Total transactions: {len(result)}")
    print(f"Duplicates: {int(result['is_duplicate'].sum())}")
    print(f"High-value (> {threshold:,.0f}): {int(result['is_high_value'].sum())}")
    print(f"Suspicious accounts: {suspicious_accounts if suspicious_accounts else 'None'}")
    print(f"Risk levels: {dict(result['risk_level'].value_counts())}")
    print(f"\nCharts + report + CSVs saved to: {OUTPUT_DIR}/")
    print(f"  - {cat_chart_path}")
    print(f"  - {trend_chart_path}")
    print(f"  - {top10_chart_path}")
    print(f"  - {suspicious_csv_path}")
    print(f"  - {full_csv_path}")
    print(f"  - {report_path}")


# ============================================================
# 5. STREAMLIT DASHBOARD MODE (bonus)
# ============================================================
def run_dashboard(default_csv_path, default_threshold):
    import streamlit as st
    import plotly.express as px

    st.set_page_config(page_title="Transaction Risk Dashboard", layout="wide")
    st.title("Transaction Analysis & Fraud Risk Dashboard")
    st.caption("Duplicate detection • high-value flags • suspicious accounts • risk scoring")

    # ---- Sidebar: data source & controls ----
    st.sidebar.header("Data")
    uploaded = st.sidebar.file_uploader("Upload a transactions CSV", type="csv")

    if uploaded is not None:
        raw_df = pd.read_csv(uploaded)
        raw_df.columns = [c.strip().lower() for c in raw_df.columns]
        if "transaction_id" not in raw_df.columns:
            raw_df["transaction_id"] = range(1, len(raw_df) + 1)
        if "category" not in raw_df.columns:
            raw_df["category"] = "Uncategorized"
        raw_df["date"] = pd.to_datetime(raw_df["date"], errors="coerce")
        raw_df["amount"] = pd.to_numeric(raw_df["amount"], errors="coerce")
        df = raw_df.dropna(subset=["date", "amount"]).reset_index(drop=True)
    else:
        df = load_data(default_csv_path)

    st.sidebar.header("Settings")
    threshold = st.sidebar.number_input(
        "High-value threshold", min_value=0.0,
        value=float(default_threshold), step=500.0
    )
    std_mult = st.sidebar.slider(
        "Suspicious-account sensitivity (std devs above mean)", 1.0, 4.0,
        float(SUSPICIOUS_TXN_COUNT_STD), 0.5
    )

    dup_mask = detect_duplicates(df)
    high_value_mask = detect_high_value(df, threshold)
    suspicious_accounts, account_counts = detect_suspicious_accounts(df, std_mult)
    risk_scores = compute_risk_score(df, high_value_mask, dup_mask, suspicious_accounts)

    result = df.copy()
    result["is_duplicate"] = dup_mask
    result["is_high_value"] = high_value_mask
    result["is_suspicious_account"] = result["account_id"].isin(suspicious_accounts)
    result["risk_score"] = risk_scores
    result["risk_level"] = result["risk_score"].apply(risk_level)

    # ---- Sidebar: search & filters ----
    st.sidebar.header("Search & Filters")
    search_term = st.sidebar.text_input("Search account ID or transaction ID")

    all_categories = sorted(result["category"].unique())
    selected_categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)

    risk_filter = st.sidebar.multiselect(
        "Risk level", ["Low", "Medium", "High"], default=["Low", "Medium", "High"]
    )

    date_min, date_max = result["date"].min(), result["date"].max()
    date_range = st.sidebar.date_input("Date range", (date_min, date_max))

    only_flagged = st.sidebar.checkbox("Show only flagged transactions (dup / high-value / suspicious)")

    # apply filters
    filtered = result[
        result["category"].isin(selected_categories) &
        result["risk_level"].isin(risk_filter)
    ]
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]
    if search_term:
        term = search_term.strip().lower()
        filtered = filtered[
            filtered["account_id"].astype(str).str.lower().str.contains(term) |
            filtered["transaction_id"].astype(str).str.lower().str.contains(term)
        ]
    if only_flagged:
        filtered = filtered[
            filtered["is_duplicate"] | filtered["is_high_value"] | filtered["is_suspicious_account"]
        ]

    if filtered.empty:
        st.warning("No transactions match the current filters.")
        st.stop()

    # ---- KPI row ----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Transactions", len(filtered))
    c2.metric("Duplicates", int(filtered["is_duplicate"].sum()))
    c3.metric("High-Value", int(filtered["is_high_value"].sum()))
    c4.metric("Suspicious Accounts", len(suspicious_accounts))
    c5.metric("High Risk Txns", int((filtered["risk_level"] == "High").sum()))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Category Breakdown", "Daily Trend", "Top 10 Highest", "Suspicious & Risk Table"
    ])

    with tab1:
        cat_summary = filtered.groupby("category")["amount"].sum().reset_index()
        fig = px.bar(cat_summary, x="category", y="amount", color="amount",
                     color_continuous_scale="Blues", title="Total Amount by Category")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        daily = filtered.groupby(filtered["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["date", "amount"]
        fig = px.line(daily, x="date", y="amount", markers=True, title="Daily Transaction Trend")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        top10 = filtered.sort_values("amount", ascending=False).head(TOP_N_HIGHEST)
        fig = px.bar(
            top10, x="transaction_id", y="amount", color="risk_level",
            hover_data=["account_id", "category"],
            title=f"Top {TOP_N_HIGHEST} Highest Transactions",
            color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"}
        )
        fig.update_xaxes(type="category", title="Transaction ID")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top10, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Suspicious Accounts")
        if suspicious_accounts:
            sus_df = account_counts.loc[suspicious_accounts].reset_index()
            sus_df.columns = ["account_id", "transaction_count"]
            st.dataframe(sus_df.sort_values("transaction_count", ascending=False),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No suspicious accounts detected at the current sensitivity.")

        st.subheader("Flagged / Filtered Transactions (with risk scores)")
        display_cols = ["transaction_id", "date", "account_id", "amount", "category",
                         "is_duplicate", "is_high_value", "is_suspicious_account",
                         "risk_score", "risk_level"]
        st.dataframe(
            filtered[display_cols].sort_values("risk_score", ascending=False),
            use_container_width=True, hide_index=True
        )

        csv_bytes = filtered[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered transactions as CSV", csv_bytes,
                            file_name="filtered_transactions.csv", mime="text/csv")


# ============================================================
# 6. ENTRY POINT
# Detects whether it's running under `streamlit run` or plain `python`
# ============================================================
def _running_under_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if _running_under_streamlit():
    # Args after `--` in `streamlit run file.py -- path threshold` land in sys.argv
    _csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    _threshold = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HIGH_VALUE_THRESHOLD
    run_dashboard(_csv_path, _threshold)
else:
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Transaction analysis & fraud risk toolkit")
        parser.add_argument("csv_path", nargs="?", default=DEFAULT_CSV_PATH,
                             help="Path to transactions CSV (default: transactions.csv, auto-generated if missing)")
        parser.add_argument("--threshold", type=float, default=DEFAULT_HIGH_VALUE_THRESHOLD,
                             help=f"High-value transaction threshold (default: {DEFAULT_HIGH_VALUE_THRESHOLD})")
        args = parser.parse_args()
        run_cli(args.csv_path, args.threshold)
