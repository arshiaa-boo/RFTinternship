
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
