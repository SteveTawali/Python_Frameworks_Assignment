from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

import pandas as pd

from src.data_utils import (
    basic_clean,
    load_metadata,
    publications_by_year,
    source_distribution,
    title_word_frequencies,
    top_journals,
)


def ensure_dirs(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)


def plot_publications_by_year(series: pd.Series, out_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    sns.barplot(x=series.index.astype(int), y=series.values, color="#4C78A8")
    plt.title("Publications by Year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_top_journals(series: pd.Series, out_path: Path) -> None:
    plt.figure(figsize=(9, 5))
    sns.barplot(y=series.index, x=series.values, color="#F58518")
    plt.title("Top Journals by Publication Count")
    plt.xlabel("Count")
    plt.ylabel("Journal")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_source_distribution(series: pd.Series, out_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    sns.barplot(x=series.index, y=series.values, color="#54A24B")
    plt.title("Distribution by Source")
    plt.xlabel("Source")
    plt.ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_title_wordcloud(freqs: pd.Series, out_path: Path) -> None:
    if freqs.empty:
        return
    wc = WordCloud(width=900, height=500, background_color="white")
    wc.generate_from_frequencies(freqs.to_dict())
    plt.figure(figsize=(9, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic CORD-19 analysis")
    parser.add_argument(
        "--csv",
        type=str,
        default="data/metadata.csv",
        help="Path to metadata.csv",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="out",
        help="Directory to save figures",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out)
    ensure_dirs(out_dir)

    print(f"Loading data from: {csv_path}")
    df = load_metadata(str(csv_path))
    print(f"Raw shape: {df.shape}")
    print(df.dtypes.head())

    df_clean = basic_clean(df)
    print(f"Clean shape: {df_clean.shape}")
    print("Missing values after clean (selected):")
    print(df_clean[["title", "publish_time", "journal", "source_x"]].isna().sum())

    # Summaries
    year_counts = publications_by_year(df_clean)
    journals = top_journals(df_clean, n=10)
    sources = source_distribution(df_clean)
    title_freqs = title_word_frequencies(df_clean, top_k=100)

    # Plots
    plot_publications_by_year(year_counts, out_dir / "publications_by_year.png")
    plot_top_journals(journals, out_dir / "top_journals.png")
    plot_source_distribution(sources, out_dir / "source_distribution.png")
    plot_title_wordcloud(title_freqs, out_dir / "title_wordcloud.png")

    print(f"Saved figures to: {out_dir.resolve()}")


if __name__ == "__main__":
    main()


