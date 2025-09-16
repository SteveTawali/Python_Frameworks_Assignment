from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd


IMPORTANT_COLUMNS = [
    "title",
    "abstract",
    "publish_time",
    "journal",
    "authors",
    "source_x",
]


def load_metadata(csv_path: str, usecols: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """Load the CORD-19 metadata CSV with safe defaults.

    Parameters
    ----------
    csv_path: str
        Path to the metadata.csv file
    usecols: Optional[Iterable[str]]
        Optional subset of columns to load. Defaults to commonly used columns.

    Returns
    -------
    pd.DataFrame
        Raw dataframe as loaded from disk
    """
    columns = list(usecols) if usecols is not None else None
    try:
        df = pd.read_csv(csv_path, low_memory=False, usecols=columns)
    except ValueError:
        # Fallback when some requested columns are missing: load all, then subset safely
        df = pd.read_csv(csv_path, low_memory=False)
        if usecols is not None:
            present = [c for c in usecols if c in df.columns]
            df = df[present]
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned dataframe with common fields prepared for analysis.

    Steps:
    - Ensure expected columns exist (add if missing)
    - Normalize string fields and fill missing categorical values with 'Unknown'
    - Parse publish_time to datetime and extract year
    - Drop rows missing critical fields (title or publish_time)
    - Add abstract_word_count feature
    """
    df = df.copy()

    # Ensure required columns exist
    for col in IMPORTANT_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    # Normalize text fields
    for text_col in ["title", "abstract", "journal", "authors", "source_x"]:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).replace({"nan": np.nan})

    # Fill non-critical categorical columns
    for cat_col in ["journal", "authors", "source_x"]:
        if cat_col in df.columns:
            df[cat_col] = df[cat_col].fillna("Unknown")

    # Parse date and extract year
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df = df.dropna(subset=["title", "publish_time"])  # keep rows with essential info
    df["year"] = df["publish_time"].dt.year

    # Feature: abstract word count
    df["abstract_word_count"] = (
        df["abstract"].fillna("").map(lambda x: len(str(x).split()))
    )

    return df


def publications_by_year(df: pd.DataFrame) -> pd.Series:
    """Return counts of publications grouped by year (ascending by year)."""
    counts = df["year"].value_counts(dropna=True).sort_index()
    return counts


def top_journals(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Return top N journals by publication count."""
    if "journal" not in df.columns:
        return pd.Series(dtype=int)
    counts = df["journal"].fillna("Unknown").value_counts().head(n)
    return counts


def source_distribution(df: pd.DataFrame) -> pd.Series:
    """Return counts by source (e.g., PMC, CZI, etc.)."""
    if "source_x" not in df.columns:
        return pd.Series(dtype=int)
    return df["source_x"].fillna("Unknown").value_counts()


def _tokenize(text: str) -> Iterable[str]:
    # Keep letters, numbers, and spaces; remove other punctuation
    cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", str(text).lower())
    for token in cleaned.split():
        if token:
            yield token


def title_word_frequencies(
    df: pd.DataFrame, stopwords: Optional[Iterable[str]] = None, top_k: int = 50
) -> pd.Series:
    """Compute simple word frequencies from titles.

    Parameters
    ----------
    df: pd.DataFrame with a 'title' column
    stopwords: optional iterable of stop words to exclude
    top_k: number of most frequent words to return
    """
    stop_set = set(stopwords) if stopwords is not None else {
        # Basic English stopwords plus domain-generic terms
        "the",
        "and",
        "of",
        "in",
        "to",
        "a",
        "for",
        "on",
        "with",
        "is",
        "by",
        "from",
        "an",
        "using",
        "covid",
        "covid-19",
        "sars",
        "sars-cov-2",
        "coronavirus",
    }

    counter: Counter[str] = Counter()
    for title in df.get("title", pd.Series(dtype=str)).fillna(""):
        for token in _tokenize(title):
            if len(token) < 3:
                continue
            if token in stop_set:
                continue
            counter[token] += 1

    most_common = counter.most_common(top_k)
    if not most_common:
        return pd.Series(dtype=int)
    words, freqs = zip(*most_common)
    return pd.Series(list(freqs), index=list(words), dtype=int)


