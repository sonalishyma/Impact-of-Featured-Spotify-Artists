# Data provenance

**File:** `dataset.csv` (~20 MB, 114,000 rows)

**Source:** [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)
by maharshipandya, distributed via Kaggle (also mirrored on Hugging Face). One
row per track–genre pairing; columns include Spotify's `popularity` score
(0–100), `explicit` flag, audio features (`danceability`, `energy`,
`loudness`, `valence`, etc.), and `track_genre`.

**Why this dataset:** the original COGS 108 team's processed files were lost
after the course ended. This source was re-identified by matching summary
statistics reported in the team's final presentation (89,740 unique tracks
after dedup; explicit split 82,036/7,704; group means 32.81/34.26 for
solo/featured tracks) — see `notebooks/analysis.ipynb` section 1 for the
fingerprint comparison, which reproduces those numbers to within one row.

**Regenerating this file:** run `python src/get_data.py` from the repo root
(requires `kagglehub`, or download manually from the Kaggle page above and
place the CSV here).
