from datetime import datetime
from collections import Counter
import spacy

# Load English and French models
nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")

# Combine English and French stopwords
stop_words = nlp_en.Defaults.stop_words.union(nlp_fr.Defaults.stop_words)


def process_trend_data(dates):
    date_objs = []
    for date in dates:
        try:
            if isinstance(date, str):
                date_objs.append(datetime.fromisoformat(date))
            elif isinstance(date, datetime):
                date_objs.append(date)
        except Exception:
            continue

    if not date_objs:
        return {"labels": [], "data": []}

    formatted_dates = [date.strftime('%b %d') for date in date_objs]
    date_counts = Counter(formatted_dates)
    unique_dates = sorted(set(date_objs))
    sorted_labels = [date.strftime('%b %d') for date in unique_dates]

    return {
        "labels": sorted_labels,
        "data": [date_counts[label] for label in sorted_labels]
    }


# --- Text Processing Functions ---
def extract_keywords_cloud(titles, top_n=30):
    all_words = []

    for title in titles:
        doc = nlp_en(title.lower())
        words = [token.text for token in doc if token.is_alpha and token.text not in stop_words]
        all_words.extend(words)

    freq = Counter(all_words)
    return [{"text": word.title(), "size": count} for word, count in freq.most_common(top_n)]
