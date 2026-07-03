"""Re-download the Spotify Tracks Dataset and write it to data/dataset.csv.

Source: maharshipandya/spotify-tracks-dataset on Kaggle (114,000 track-genre
rows). A copy is already included at data/dataset.csv so the notebook runs
without this script; use it only to refresh or verify provenance.
"""
import shutil
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEST = DATA_DIR / "dataset.csv"
KAGGLE_HANDLE = "maharshipandya/spotify-tracks-dataset"


def main() -> None:
    try:
        import kagglehub
    except ImportError:
        sys.exit(
            "kagglehub is required: pip install kagglehub\n"
            f"Alternatively, download '{KAGGLE_HANDLE}' manually from "
            "https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset "
            f"and place the CSV at {DEST}"
        )

    download_path = Path(kagglehub.dataset_download(KAGGLE_HANDLE))
    csv_candidates = list(download_path.glob("*.csv"))
    if not csv_candidates:
        sys.exit(f"No CSV found in downloaded dataset at {download_path}")

    DATA_DIR.mkdir(exist_ok=True)
    shutil.copy(csv_candidates[0], DEST)
    print(f"Wrote {DEST} ({DEST.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
