"""
analyzer.py
-----------
Core analytics engine for the Social Media Trend Analyzer.

All functions take a pandas DataFrame with (at minimum) these columns:
    username, date, time, content, hashtags, likes, comments, shares, category

and return summary DataFrames/dicts ready to chart or export.
"""

import re
import pandas as pd

REQUIRED_COLUMNS = ["username", "date", "time", "content", "hashtags",
                    "likes", "comments", "shares", "category"]


def load_posts(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required column(s): {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    # Combine date + time into a real datetime for time-based analysis
    df["datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str),
        errors="coerce",
    )
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.day_name()

    for col in ["likes", "comments", "shares"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["engagement"] = df["likes"] + df["comments"] + df["shares"]
    return df


def extract_hashtags(df: pd.DataFrame) -> pd.Series:
    """Flatten the hashtags column (space or comma separated) into one
    long Series of individual hashtags, also pulling any #tags out of
    the free-text content in case they weren't listed separately."""
    all_tags = []
    for _, row in df.iterrows():
        tags = set()
        raw = str(row.get("hashtags", "") or "")
        for piece in re.split(r"[,\s]+", raw):
            piece = piece.strip()
            if piece.startswith("#") and len(piece) > 1:
                tags.add(piece.lower())
        for tag in re.findall(r"#\w+", str(row.get("content", "") or "")):
            tags.add(tag.lower())
        all_tags.extend(tags)
    return pd.Series(all_tags)


def top_hashtags(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    tags = extract_hashtags(df)
    if tags.empty:
        return pd.DataFrame(columns=["hashtag", "count"])
    counts = tags.value_counts().head(n)
    return counts.rename_axis("hashtag").reset_index(name="count")


def most_active_users(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    summary = (
        df.groupby("username")
        .agg(posts=("username", "count"),
             total_engagement=("engagement", "sum"),
             avg_engagement=("engagement", "mean"))
        .sort_values("posts", ascending=False)
        .head(n)
        .reset_index()
    )
    summary["avg_engagement"] = summary["avg_engagement"].round(1)
    return summary


def engagement_summary(df: pd.DataFrame) -> dict:
    return {
        "total_posts": len(df),
        "total_likes": int(df["likes"].sum()),
        "total_comments": int(df["comments"].sum()),
        "total_shares": int(df["shares"].sum()),
        "total_engagement": int(df["engagement"].sum()),
        "avg_engagement_per_post": round(df["engagement"].mean(), 2) if len(df) else 0,
    }


def daily_engagement_trend(df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        df.groupby(df["datetime"].dt.date)
        .agg(likes=("likes", "sum"), comments=("comments", "sum"),
             shares=("shares", "sum"), engagement=("engagement", "sum"),
             posts=("engagement", "count"))
        .reset_index()
        .rename(columns={"datetime": "date"})
    )
    return daily


def content_category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    dist = (
        df.groupby("category")
        .agg(posts=("category", "count"), total_engagement=("engagement", "sum"))
        .sort_values("posts", ascending=False)
        .reset_index()
    )
    return dist


def most_popular_posting_time(df: pd.DataFrame) -> pd.DataFrame:
    """Average engagement by hour of day, to find the best time to post."""
    by_hour = (
        df.groupby("hour")
        .agg(posts=("hour", "count"), avg_engagement=("engagement", "mean"))
        .reset_index()
        .sort_values("avg_engagement", ascending=False)
    )
    by_hour["avg_engagement"] = by_hour["avg_engagement"].round(1)
    return by_hour


def build_full_report(df: pd.DataFrame, top_n_hashtags: int = 10,
                       top_n_users: int = 10) -> pd.DataFrame:
    """Combine everything into one tidy report DataFrame for CSV export."""
    rows = []

    summary = engagement_summary(df)
    for key, val in summary.items():
        rows.append({"section": "Overall Summary", "metric": key, "value": val})

    hashtags = top_hashtags(df, top_n_hashtags)
    for _, r in hashtags.iterrows():
        rows.append({"section": "Top Hashtags", "metric": r["hashtag"], "value": r["count"]})

    users = most_active_users(df, top_n_users)
    for _, r in users.iterrows():
        rows.append({"section": "Most Active Users", "metric": r["username"],
                     "value": f"{r['posts']} posts, {int(r['total_engagement'])} total engagement"})

    categories = content_category_distribution(df)
    for _, r in categories.iterrows():
        rows.append({"section": "Category Distribution", "metric": r["category"],
                     "value": f"{r['posts']} posts, {int(r['total_engagement'])} engagement"})

    best_hours = most_popular_posting_time(df).head(5)
    for _, r in best_hours.iterrows():
        rows.append({"section": "Best Posting Hours", "metric": f"{int(r['hour']):02d}:00",
                     "value": f"avg engagement {r['avg_engagement']}"})

    if "sentiment" in df.columns:
        sentiment_counts = df["sentiment"].value_counts()
        for label, count in sentiment_counts.items():
            rows.append({"section": "Sentiment Breakdown", "metric": label, "value": count})

    return pd.DataFrame(rows)
