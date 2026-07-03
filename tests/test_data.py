"""Data integrity checks: dedup, has_feature labeling, and the fingerprint
match against the original team's final-presentation summary statistics.
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from clean import load_and_clean

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"


@pytest.fixture(scope="module")
def d():
    if not DATA_PATH.exists():
        pytest.skip(f"data file not found at {DATA_PATH}; run src/get_data.py first")
    return load_and_clean(str(DATA_PATH))


def test_row_count_matches_original_within_one_row(d):
    assert abs(len(d) - 89740) <= 1


def test_track_id_is_unique(d):
    assert d["track_id"].is_unique


def test_no_zero_duration_tracks(d):
    assert (d["duration_sec"] > 0).all()


def test_explicit_split_matches_original(d):
    assert int((d.explicit == 0).sum()) == 82036
    assert int((d.explicit == 1).sum()) == 7704


def test_has_feature_is_binary(d):
    assert set(d["has_feature"].unique()) <= {0, 1}


def test_group_means_match_original_within_tolerance(d):
    solo_mean = d.loc[d.has_feature == 0, "popularity"].mean()
    feat_mean = d.loc[d.has_feature == 1, "popularity"].mean()
    assert solo_mean == pytest.approx(32.81, abs=0.1)
    assert feat_mean == pytest.approx(34.26, abs=0.1)


def test_popularity_in_valid_range(d):
    assert d["popularity"].between(0, 100).all()
