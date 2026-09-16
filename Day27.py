

import argparse
import os
import matplotlib
matplotlib.use("Agg")  # headless backend, safe for scripts/servers
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from analyzer import (
    load_posts, top_hashtags, most_active_users, engagement_summary,
    daily_engagement_trend, content_category_distribution,
    most_popular_posting_time, build_full_report,
)
from sentiment import add_sentiment_column


def plot_top_hashtags(df_tags, out_path):
    plt.figure(figsize=(9, 5.5))
    plt.barh(df_tags["hashtag"][::-1], df_tags["count"][::-1], color="#4C72B0")
    plt.xlabel("Number of Posts")
    plt.title("Top Trending Hashtags")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_daily_engagement(df_daily, out_path):
    plt.figure(figsize=(10, 5.5))
    plt.plot(df_daily["date"], df_daily["likes"], marker="o", label="Likes")
    plt.plot(df_daily["date"], df_daily["comments"], marker="o", label="Comments")
    plt.plot(df_daily["date"], df_daily["shares"], marker="o", label="Shares")
    plt.xlabel("Date")
    plt.ylabel("Total Count")
    plt.title("Daily Engagement Trend")
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_category_distribution(df_cat, out_path):
    plt.figure(figsize=(7, 7))
    plt.pie(
        df_cat["posts"], labels=df_cat["category"], autopct="%1.1f%%",
        startangle=90, colors=plt.cm.Set3.colors,
    )
    plt.title("Content Category Distribution")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def run(input_csv, output_dir="output", top_n=10, with_sentiment=True):
    os.makedirs(output_dir, exist_ok=True)

    df = load_posts(input_csv)
    if with_sentiment:
        df = add_sentiment_column(df, text_column="content")

    # --- Console summary ---
    summary = engagement_summary(df)
    print("\n=== Overall Engagement Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    hashtags = top_hashtags(df, top_n)
    print(f"\n=== Top {top_n} Hashtags ===")
    print(hashtags.to_string(index=False))

    users = most_active_users(df, top_n)
    print(f"\n=== Top {top_n} Most Active Users ===")
    print(users.to_string(index=False))

    best_hours = most_popular_posting_time(df)
    print("\n=== Best Posting Hours (by avg engagement) ===")
    print(best_hours.head(5).to_string(index=False))

    if with_sentiment:
        print("\n=== Sentiment Breakdown ===")
        print(df["sentiment"].value_counts().to_string())

    # --- Charts ---
    daily = daily_engagement_trend(df)
    categories = content_category_distribution(df)

    plot_top_hashtags(hashtags, os.path.join(output_dir, "top_hashtags_chart.png"))
    plot_daily_engagement(daily, os.path.join(output_dir, "daily_engagement_trend.png"))
    plot_category_distribution(categories, os.path.join(output_dir, "content_category_distribution.png"))
    print(f"\nCharts saved to '{output_dir}/'")

    # --- Full report export ---
    report_df = build_full_report(df, top_n_hashtags=top_n, top_n_users=top_n)
    report_path = os.path.join(output_dir, "analytics_report.csv")
    report_df.to_csv(report_path, index=False)
    print(f"Full analytics report exported to '{report_path}'")

    # Also export the enriched raw data (with engagement + sentiment columns)
    enriched_path = os.path.join(output_dir, "posts_enriched.csv")
    df.drop(columns=["datetime"]).to_csv(enriched_path, index=False)
    print(f"Enriched post-level data exported to '{enriched_path}'")

    return df, report_df


def _parse_args():
    p = argparse.ArgumentParser(description="Social Media Trend Analyzer")
    p.add_argument("--input", default="sample_posts.csv", help="Path to posts CSV")
    p.add_argument("--output_dir", default="output", help="Folder for charts/report")
    p.add_argument("--top_n", type=int, default=10, help="Top N hashtags/users to show")
    p.add_argument("--no_sentiment", action="store_true", help="Skip sentiment analysis")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(
        input_csv=args.input,
        output_dir=args.output_dir,
        top_n=args.top_n,
        with_sentiment=not args.no_sentiment,
    )


import random
import csv
from datetime import datetime, timedelta

random.seed(42)

USERNAMES = [
    "@aisha_codes", "@rohan.tech", "@priya_designs", "@karan_vibes",
    "@dev_naina", "@thefoodie_raj", "@travel_with_meera", "@fit_arjun",
    "@musicby_sara", "@startup_vik", "@gamer_ananya", "@photo_kabir",
    "@bookworm_ira", "@chef_ishaan", "@artsy_diya",
]

HASHTAG_POOL = [
    "#python", "#ai", "#machinelearning", "#coding", "#tech",
    "#travel", "#foodie", "#fitness", "#motivation", "#music",
    "#startup", "#gaming", "#photography", "#books", "#art",
    "#datascience", "#webdev", "#opensource", "#productivity", "#news",
]

CATEGORIES = ["Technology", "Food", "Travel", "Fitness", "Entertainment",
              "Business", "Lifestyle", "Sports"]

CATEGORY_HASHTAGS = {
    "Technology": ["#python", "#ai", "#machinelearning", "#coding", "#tech",
                   "#datascience", "#webdev", "#opensource"],
    "Food": ["#foodie"],
    "Travel": ["#travel", "#photography"],
    "Fitness": ["#fitness", "#motivation"],
    "Entertainment": ["#music", "#gaming"],
    "Business": ["#startup", "#productivity", "#news"],
    "Lifestyle": ["#books", "#art", "#motivation"],
    "Sports": ["#fitness", "#motivation"],
}

POSITIVE_TEMPLATES = [
    "Absolutely loving the new {topic} update, this is amazing! {tags}",
    "Best {topic} experience ever, highly recommend it to everyone! {tags}",
    "So excited to share this incredible {topic} milestone with you all {tags}",
    "This {topic} community is so supportive and inspiring {tags}",
    "Grateful for such a wonderful {topic} journey this year {tags}",
]
NEUTRAL_TEMPLATES = [
    "Here's an update on my {topic} project, more details soon {tags}",
    "Sharing some notes on {topic} today {tags}",
    "A quick look at what I learned about {topic} this week {tags}",
    "Working on a new {topic} post, stay tuned {tags}",
    "Some thoughts on the current state of {topic} {tags}",
]
NEGATIVE_TEMPLATES = [
    "Really frustrated with how this {topic} launch turned out {tags}",
    "Disappointed by the recent {topic} changes, not a fan {tags}",
    "This {topic} issue has been such a headache to deal with {tags}",
    "Not happy with the {topic} experience today, needs work {tags}",
    "Struggling with {topic} problems again, so annoying {tags}",
]

TOPICS = ["python", "AI", "travel", "food", "fitness", "startup", "music",
          "gaming", "photography", "reading", "art", "productivity"]


def random_post(post_id, day):
    username = random.choice(USERNAMES)
    category = random.choice(CATEGORIES)
    possible_tags = CATEGORY_HASHTAGS[category] + random.sample(HASHTAG_POOL, 2)
    tags = random.sample(possible_tags, k=min(3, len(possible_tags)))
    tag_str = " ".join(sorted(set(tags)))

    sentiment_bucket = random.choices(
        ["pos", "neu", "neg"], weights=[0.45, 0.35, 0.20]
    )[0]
    template = random.choice(
        {"pos": POSITIVE_TEMPLATES, "neu": NEUTRAL_TEMPLATES,
         "neg": NEGATIVE_TEMPLATES}[sentiment_bucket]
    )
    content = template.format(topic=random.choice(TOPICS), tags=tag_str)

    # Posting time skewed toward common social-media active hours
    hour = random.choices(
        population=list(range(24)),
        weights=[1,1,1,1,1,2,3,4,5,6,7,8,9,8,7,6,7,8,9,10,9,7,4,2],
    )[0]
    minute = random.randint(0, 59)
    post_datetime = day.replace(hour=hour, minute=minute)

    likes = max(0, int(random.gauss(150, 120)))
    comments = max(0, int(random.gauss(15, 12)))
    shares = max(0, int(random.gauss(8, 7)))

    # Popular categories/sentiment get a small engagement boost
    if category == "Technology":
        likes = int(likes * 1.3)
    if sentiment_bucket == "pos":
        likes = int(likes * 1.15)

    return {
        "post_id": post_id,
        "username": username,
        "date": post_datetime.strftime("%Y-%m-%d"),
        "time": post_datetime.strftime("%H:%M"),
        "content": content,
        "hashtags": tag_str,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "category": category,
    }


def generate(num_posts=400, num_days=30, output_path="sample_posts.csv"):
    start_date = datetime.now() - timedelta(days=num_days)
    rows = []
    for i in range(1, num_posts + 1):
        day_offset = random.randint(0, num_days - 1)
        day = start_date + timedelta(days=day_offset)
        rows.append(random_post(i, day))

    rows.sort(key=lambda r: (r["date"], r["time"]))

    fieldnames = ["post_id", "username", "date", "time", "content",
                  "hashtags", "likes", "comments", "shares", "category"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} sample posts -> {output_path}")


if __name__ == "__main__":
    generate()

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def classify_sentiment(text: str) -> dict:
    """Return the compound score and a Positive/Neutral/Negative label."""
    if not text or not str(text).strip():
        return {"compound": 0.0, "label": "Neutral"}

    scores = _analyzer.polarity_scores(str(text))
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {"compound": compound, "label": label}


def add_sentiment_column(df, text_column: str = "content"):
    """Add 'sentiment' and 'sentiment_score' columns to a DataFrame."""
    results = df[text_column].apply(classify_sentiment)
    df = df.copy()
    df["sentiment"] = results.apply(lambda r: r["label"])
    df["sentiment_score"] = results.apply(lambda r: r["compound"])
    return df
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
"""
streamlit_app.py
-----------------
Bonus challenge: an interactive Streamlit dashboard for the Social
Media Trend Analyzer, with search + filters, live charts, and a
downloadable analytics report.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyzer import (
    load_posts, top_hashtags, most_active_users, engagement_summary,
    daily_engagement_trend, content_category_distribution,
    most_popular_posting_time, build_full_report,
)
from sentiment import add_sentiment_column

st.set_page_config(page_title="Social Media Trend Analyzer", layout="wide")
st.title("📱 Social Media Trend Analyzer")
st.caption("Upload a post-level CSV (or use the bundled sample data) to "
           "explore hashtags, active users, engagement trends, and sentiment.")

# ---------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("📂 Data Source")
    uploaded = st.file_uploader("Upload posts CSV", type=["csv"])
    use_sample = st.checkbox("Use bundled sample_posts.csv", value=uploaded is None)

if uploaded is not None:
    df = load_posts(uploaded)
elif use_sample:
    df = load_posts("sample_posts.csv")
else:
    st.info("Upload a CSV or check 'Use bundled sample data' to get started.")
    st.stop()

with st.spinner("Running sentiment analysis..."):
    df = add_sentiment_column(df, text_column="content")

# ---------------------------------------------------------------------
# Sidebar: search & filters
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Search & Filters")
    search_text = st.text_input("Search post content or hashtags")

    all_categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Category", all_categories, default=all_categories)

    all_users = sorted(df["username"].dropna().unique().tolist())
    selected_users = st.multiselect("Username", all_users, default=[])

    sentiment_options = ["Positive", "Neutral", "Negative"]
    selected_sentiments = st.multiselect("Sentiment", sentiment_options, default=sentiment_options)

    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)

    top_n = st.slider("Top N (hashtags / users)", 5, 20, 10)

# ---------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------
filtered = df.copy()

if search_text:
    mask = (
        filtered["content"].str.contains(search_text, case=False, na=False)
        | filtered["hashtags"].str.contains(search_text, case=False, na=False)
    )
    filtered = filtered[mask]

if selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]

if selected_users:
    filtered = filtered[filtered["username"].isin(selected_users)]

if selected_sentiments:
    filtered = filtered[filtered["sentiment"].isin(selected_sentiments)]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["datetime"].dt.date >= start) & (filtered["datetime"].dt.date <= end)
    ]

if filtered.empty:
    st.warning("No posts match the current filters. Try widening your search.")
    st.stop()

st.caption(f"Showing **{len(filtered)}** of {len(df)} posts after filters.")

# ---------------------------------------------------------------------
# Top metrics
# ---------------------------------------------------------------------
summary = engagement_summary(filtered)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Posts", summary["total_posts"])
c2.metric("Total Likes", summary["total_likes"])
c3.metric("Total Comments", summary["total_comments"])
c4.metric("Total Shares", summary["total_shares"])
c5.metric("Avg Engagement / Post", summary["avg_engagement_per_post"])

st.markdown("---")

# ---------------------------------------------------------------------
# Charts row
# ---------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Trending Hashtags")
    hashtags = top_hashtags(filtered, top_n)
    if hashtags.empty:
        st.info("No hashtags found in the filtered data.")
    else:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.barh(hashtags["hashtag"][::-1], hashtags["count"][::-1], color="#4C72B0")
        ax.set_xlabel("Number of Posts")
        st.pyplot(fig)
        plt.close(fig)

with col2:
    st.subheader("Content Category Distribution")
    categories = content_category_distribution(filtered)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.pie(categories["posts"], labels=categories["category"], autopct="%1.1f%%",
           startangle=90, colors=plt.cm.Set3.colors)
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Daily Engagement Trend")
daily = daily_engagement_trend(filtered)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(daily["date"], daily["likes"], marker="o", label="Likes")
ax.plot(daily["date"], daily["comments"], marker="o", label="Comments")
ax.plot(daily["date"], daily["shares"], marker="o", label="Shares")
ax.set_xlabel("Date")
ax.set_ylabel("Total Count")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)
plt.close(fig)

st.markdown("---")

# ---------------------------------------------------------------------
# Active users, posting time, sentiment
# ---------------------------------------------------------------------
col3, col4, col5 = st.columns(3)

with col3:
    st.subheader("👥 Most Active Users")
    st.dataframe(most_active_users(filtered, top_n), use_container_width=True)

with col4:
    st.subheader("🕐 Best Posting Hours")
    st.dataframe(most_popular_posting_time(filtered).head(top_n), use_container_width=True)

with col5:
    st.subheader("💬 Sentiment Breakdown")
    sentiment_counts = filtered["sentiment"].value_counts()
    fig, ax = plt.subplots(figsize=(4, 4))
    colors = {"Positive": "#4CAF50", "Neutral": "#9E9E9E", "Negative": "#E53935"}
    ax.pie(
        sentiment_counts.values, labels=sentiment_counts.index, autopct="%1.1f%%",
        colors=[colors.get(l, "#999") for l in sentiment_counts.index], startangle=90,
    )
    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")

# ---------------------------------------------------------------------
# Filtered post table + report export
# ---------------------------------------------------------------------
st.subheader("📄 Filtered Posts")
st.dataframe(
    filtered[["post_id", "username", "date", "time", "content", "hashtags",
              "likes", "comments", "shares", "category", "sentiment"]],
    use_container_width=True,
)

report_df = build_full_report(filtered, top_n_hashtags=top_n, top_n_users=top_n)
report_csv = report_df.to_csv(index=False).encode("utf-8")
posts_csv = filtered.drop(columns=["datetime"]).to_csv(index=False).encode("utf-8")

dl1, dl2 = st.columns(2)
dl1.download_button("⬇️ Download Analytics Report (CSV)", data=report_csv,
                     file_name="analytics_report.csv", mime="text/csv")
dl2.download_button("⬇️ Download Filtered Posts (CSV)", data=posts_csv,
                     file_name="filtered_posts.csv", mime="text/csv")
