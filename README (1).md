# 📱 Social Media Trend Analyzer — Day 27

An end-to-end Python project that reads social media post data,
identifies trending hashtags, finds the most active users, calculates
engagement, detects the best posting times, runs sentiment analysis,
generates charts, and exports a full analytics report to CSV. Includes
a bonus interactive Streamlit dashboard with search and filters.

## 📁 Project Structure

```
trend_analyzer/
├── generate_sample_data.py    # Creates sample_posts.csv (400 realistic sample posts)
├── analyzer.py                 # Core analytics: hashtags, users, engagement, timing
├── sentiment.py                 # Bonus: VADER-based sentiment analysis
├── main.py                     # CLI pipeline: analyze -> chart -> export CSV
├── streamlit_app.py            # Bonus: interactive dashboard with search/filters
├── sample_posts.csv            # Pre-generated sample dataset (400 posts, 30 days)
├── requirements.txt
└── README.md
```

## 🚀 Setup

```bash
pip install -r requirements.txt
```

The sample dataset (`sample_posts.csv`) is already included, so you
can run everything immediately. If you want to regenerate it (or make
a bigger one):

```bash
python generate_sample_data.py
```

## 📄 Expected CSV format

Your input CSV needs these columns (case-sensitive):

| Column | Description |
|---|---|
| `post_id` | Unique ID for the post |
| `username` | Who posted it |
| `date` | `YYYY-MM-DD` |
| `time` | `HH:MM` (24-hour) |
| `content` | The post's text |
| `hashtags` | Space or comma-separated hashtags, e.g. `#python #ai` |
| `likes` | Integer |
| `comments` | Integer |
| `shares` | Integer |
| `category` | Content category, e.g. `Technology`, `Food`, `Travel` |

## ▶️ Run the CLI version

```bash
python main.py --input sample_posts.csv --output_dir output --top_n 10
```

This prints a full analysis to the console (engagement summary, top
hashtags, most active users, best posting hours, sentiment breakdown)
and writes to `output/`:

- **`analytics_report.csv`** — the full text/number report, one row per metric
- **`posts_enriched.csv`** — your original data plus computed `engagement` and `sentiment` columns
- **`top_hashtags_chart.png`** — 📊 bar chart of trending hashtags
- **`daily_engagement_trend.png`** — 📈 line chart of likes/comments/shares over time
- **`content_category_distribution.png`** — 🥧 pie chart of post categories

Skip sentiment analysis (slightly faster) with `--no_sentiment`.

## 🌐 Run the Streamlit dashboard (bonus)

```bash
streamlit run streamlit_app.py
```

In the browser sidebar you can:
- Upload your own CSV, or use the bundled sample data
- **Search** post content/hashtags by keyword
- **Filter** by category, username, sentiment, and date range
- Adjust the Top-N shown for hashtags/users

The main panel updates live with: engagement metrics, the three
required charts, most active users, best posting hours, a sentiment
pie chart, the filtered post table, and two CSV download buttons
(analytics report + filtered posts).

## 🧮 How things are calculated

- **Engagement** = likes + comments + shares, per post.
- **Top hashtags** — hashtags are read from the `hashtags` column and
  also scraped from `#tags` inside the post text, deduplicated per
  post, then counted across the dataset.
- **Most active users** — ranked by post count, with total/average
  engagement shown alongside.
- **Best posting time** — posts are grouped by hour-of-day, ranked by
  *average* engagement (not just volume), so it surfaces "post at 9am,
  not just 6pm when everyone else posts."
- **Sentiment** — uses [VADER](https://github.com/cjhutto/vaderSentiment),
  a lexicon/rule-based analyzer built for short, informal social text
  (handles emphasis, punctuation, emojis). Compound score ≥ 0.05 →
  Positive, ≤ -0.05 → Negative, else Neutral.

## ✏️ Customizing

- Add more categories/hashtags by editing `generate_sample_data.py` if
  you want a bigger or differently-shaped sample dataset.
- Swap VADER for a transformer-based sentiment model in `sentiment.py`
  if you need higher accuracy on longer or more nuanced text (trade-off:
  slower, needs more dependencies).
- All chart styling lives in `main.py` (CLI charts) and
  `streamlit_app.py` (dashboard charts) — tweak colors/figsize there.
