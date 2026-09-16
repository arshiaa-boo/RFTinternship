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
