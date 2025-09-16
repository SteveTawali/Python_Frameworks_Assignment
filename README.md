CORD-19 Frameworks Assignment (Beginner)

This repo contains a minimal workflow to analyze the CORD-19 metadata.csv and a Streamlit app to explore findings.

Quick Start

1) Create and activate a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Download the dataset
- From Kaggle: CORD-19-research-challenge → download only metadata.csv
- Place it at data/metadata.csv (create the data/ folder if needed)

4) Run the analysis script
```bash
python scripts/analyze.py --csv data/metadata.csv --out out
```
- Figures will be saved in out/

5) Launch the Streamlit app
```bash
streamlit run app/streamlit_app.py
```
- The app will prefer `data/metadata_sample.csv` if present, otherwise `data/metadata.csv`, or an uploaded file.

Included
- src/data_utils.py: loading, cleaning, and summary utilities
- scripts/analyze.py: generates basic figures (year counts, top journals, sources, title word cloud)
- app/streamlit_app.py: simple interactive explorer with filters
- notebooks/Starter.ipynb: optional playground for exploration

Mapping to Assignment Parts
- Part 1 (Loading & Exploration): use load_metadata, df.head(), df.info(), df.isna().sum()
- Part 2 (Cleaning): basic_clean converts dates, adds year, abstract_word_count, fills categories
- Part 3 (Analysis & Viz): scripts/analyze.py and Streamlit charts
- Part 4 (Streamlit): app/streamlit_app.py with sliders and filters
- Part 5 (Docs & Reflection): edit this README to add your insights

Notes
- If the full file is too large, you can sample rows quickly:
```python
import pandas as pd
# Option A: take first N rows
sample = pd.read_csv('data/metadata.csv', nrows=50000)
sample.to_csv('data/metadata_sample.csv', index=False)

# Option B: random sample (requires knowing total rows or reading once)
df = pd.read_csv('data/metadata.csv')
df.sample(n=50000, random_state=42).to_csv('data/metadata_sample.csv', index=False)
```
- The Streamlit app will automatically use `data/metadata_sample.csv` if it exists.

License
MIT


