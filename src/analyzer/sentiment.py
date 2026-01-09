from typing import List, Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_news_sentiment(news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    For each item, compute sentiment_score in [-1,1], then aggregate.
    """
    scored_items = []
    total_weight = 0.0
    weighted_sum = 0.0

    for item in news_items:
        text = (item.get("title", "") + " " + item.get("summary", "")).strip()
        if not text:
            score = 0.0
        else:
            vs = _analyzer.polarity_scores(text)
            score = float(vs["compound"])

        impact_tag = (item.get("impact_tag") or "medium").lower()
        if impact_tag == "high":
            w = 3.0
        elif impact_tag == "low":
            w = 1.0
        else:
            w = 2.0

        total_weight += w
        weighted_sum += w * score

        item = dict(item)
        item["sentiment_score"] = score
        scored_items.append(item)

    avg = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "average_score": avg,
        "items": scored_items,
    }