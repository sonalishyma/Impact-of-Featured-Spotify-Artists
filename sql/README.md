# SQL analysis

This SQLite analysis reproduces the principal data cleaning and aggregation steps used in the Spotify featured artist study. It complements the Python notebook: SQLite handles the reproducible descriptive summaries and genre decomposition, while the notebook remains the source for OLS regression, HC3 robust standard errors, confidence intervals, and hypothesis tests.

## Run the analysis

From the repository root:

```bash
sqlite3 :memory: < sql/analysis.sql
```

The script imports `data/dataset.csv`, keeps the first row for each `track_id`, removes nonpositive durations, constructs the `has_feature` field, and runs seven documented queries. No database file is required.

## Queries

1. Data cleaning audit
2. Popularity by collaboration status
3. Raw difference in mean popularity
4. Genres with the highest collaboration share
5. Popularity gaps within genres
6. Exact shift share genre decomposition
7. Sensitivity after excluding zero popularity tracks

The checked output is recorded in [results.md](./results.md).
