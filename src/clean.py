"""Shared cleaning/labeling logic for the Spotify featured-artist analysis.

Used by both notebooks/analysis.ipynb and the test suite, so the two never
drift apart.
"""
import pandas as pd

FEATURE_MARKER_RE = r"\b(?:feat\.?|ft\.?|featuring|with)\b"


def load_and_clean(csv_path: str) -> pd.DataFrame:
    """Load the raw Kaggle CSV and apply the dedup + has_feature pipeline."""
    df = pd.read_csv(csv_path)
    d = df.drop(columns=["Unnamed: 0"]).drop_duplicates(subset="track_id").copy()
    d = d[d["duration_ms"] > 0].copy()
    d["explicit"] = d["explicit"].astype(bool).astype(int)
    d["duration_sec"] = d["duration_ms"] / 1000

    t = d["track_name"].fillna("").str.lower()
    a = d["artists"].fillna("")
    d["multi_artist"] = a.str.contains(";")
    d["title_feat"] = t.str.contains(FEATURE_MARKER_RE, regex=True)
    d["has_feature"] = (d["multi_artist"] | d["title_feat"]).astype(int)
    return d
