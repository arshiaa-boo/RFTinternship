import numpy as np
import pandas as pd

from expense_tracker import load_transactions, add_categories, DATA_FILE, OUTPUTS_DIR
import os


def predict_series(values: pd.Series) -> float:
    """Fit a straight line to `values` (indexed 0..n-1) and extrapolate one step."""
    if len(values) == 1:
        return float(values.iloc[0])  # not enough history for a trend, just repeat
    x = np.arange(len(values))
    y = values.values
    slope, intercept = np.polyfit(x, y, 1)
    next_x = len(values)
    pred = slope * next_x + intercept
    return max(pred, 0)  # spending can't be negative


def predict_next_month(df: pd.DataFrame) -> pd.DataFrame:
    exp = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp["amount"] = -exp["amount"]

    monthly_cat = exp.groupby(["month", "category"])["amount"].sum().unstack(fill_value=0)
    monthly_cat = monthly_cat.sort_index()

    predictions = {}
    for cat in monthly_cat.columns:
        predictions[cat] = predict_series(monthly_cat[cat])

    pred_df = pd.DataFrame({
        "category": list(predictions.keys()),
        "predicted_next_month": [round(v, 2) for v in predictions.values()],
    }).sort_values("predicted_next_month", ascending=False).reset_index(drop=True)

    total_predicted = pred_df["predicted_next_month"].sum()
    return pred_df, total_predicted, monthly_cat


def main():
    df = load_transactions(DATA_FILE)
    df = add_categories(df)

    pred_df, total_predicted, monthly_cat = predict_next_month(df)

    print("Historical monthly spend by category:")
    print(monthly_cat.round(0))
    print()
    print("Predicted spend for next month, by category:")
    print(pred_df.to_string(index=False))
    print()
    print(f"Predicted TOTAL spend next month: Rs {total_predicted:,.0f}")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    pred_df.to_csv(os.path.join(OUTPUTS_DIR, "next_month_prediction.csv"), index=False)


if __name__ == "__main__":
    main()
