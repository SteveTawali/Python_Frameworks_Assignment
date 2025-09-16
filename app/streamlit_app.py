from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

from src.data_utils import (
    basic_clean,
    load_metadata,
    publications_by_year,
    source_distribution,
    title_word_frequencies,
    top_journals,
)


st.set_page_config(page_title="CORD-19 Data Explorer", layout="wide")

st.title("CORD-19 Data Explorer")
st.write("Simple exploration of COVID-19 research papers (metadata only)")


def load_dataframe(file_buffer_or_path: str | io.BytesIO) -> pd.DataFrame:
    if isinstance(file_buffer_or_path, (io.BytesIO, io.StringIO)):
        df = pd.read_csv(file_buffer_or_path, low_memory=False)
    else:
        df = load_metadata(str(file_buffer_or_path))
    return basic_clean(df)


sample_path = Path("data/metadata_sample.csv")
default_path = Path("data/metadata.csv")
uploaded = st.file_uploader("Upload metadata.csv (optional)", type=["csv"]) 

if uploaded is not None:
    df_clean = load_dataframe(uploaded)
    st.caption("Using uploaded file")
elif sample_path.exists():
    df_clean = load_dataframe(sample_path)
    st.caption("Using local data/metadata_sample.csv")
elif default_path.exists():
    df_clean = load_dataframe(default_path)
    st.caption("Using local data/metadata.csv")
else:
    st.info("Please upload the CORD-19 metadata.csv to begin.")
    st.stop()


st.sidebar.header("Filters")
years = sorted(df_clean["year"].dropna().unique().tolist())
if years:
    min_year, max_year = min(years), max(years)
else:
    min_year, max_year = (2020, 2021)

year_range = st.sidebar.slider(
    "Select year range", min_value=int(min_year), max_value=int(max_year), value=(int(min_year), int(max_year))
)

selected_journals = st.sidebar.multiselect(
    "Filter by journal (optional)", options=sorted(df_clean["journal"].dropna().unique().tolist())[:200]
)

mask = (df_clean["year"].between(year_range[0], year_range[1]))
if selected_journals:
    mask &= df_clean["journal"].isin(selected_journals)

filtered = df_clean.loc[mask]

st.subheader("Dataset snapshot")
st.dataframe(filtered.head(50))
st.caption(f"Rows: {len(filtered):,} (of {len(df_clean):,})")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Publications by Year**")
    series = publications_by_year(filtered)
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(x=series.index.astype(int), y=series.values, color="#4C78A8", ax=ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    st.pyplot(fig)

with col2:
    st.markdown("**Top Journals**")
    journals = top_journals(filtered, n=10)
    fig2, ax2 = plt.subplots(figsize=(6, 3.2))
    sns.barplot(y=journals.index, x=journals.values, color="#F58518", ax=ax2)
    ax2.set_xlabel("Count")
    ax2.set_ylabel("Journal")
    st.pyplot(fig2)

st.markdown("**Source Distribution**")
sources = source_distribution(filtered)
fig3, ax3 = plt.subplots(figsize=(10, 3.2))
sns.barplot(x=sources.index, y=sources.values, color="#54A24B", ax=ax3)
ax3.set_xlabel("Source")
ax3.set_ylabel("Count")
plt.setp(ax3.get_xticklabels(), rotation=30, ha="right")
st.pyplot(fig3)

st.markdown("**Common Title Words**")
freqs = title_word_frequencies(filtered, top_k=30)
st.bar_chart(freqs)

st.markdown("---")
st.markdown("Data columns available:")
st.code(", ".join(df_clean.columns))


