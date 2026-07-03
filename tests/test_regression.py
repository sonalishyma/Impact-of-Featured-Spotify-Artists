"""Sanity checks on the regression results: this is what stops a future edit
to the notebook from silently reversing the "small effect" finding or
reintroducing multicollinearity.
"""
from pathlib import Path

import pytest
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from clean import load_and_clean

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"


@pytest.fixture(scope="module")
def d():
    if not DATA_PATH.exists():
        pytest.skip(f"data file not found at {DATA_PATH}; run src/get_data.py first")
    return load_and_clean(str(DATA_PATH))


@pytest.fixture(scope="module")
def spec1(d):
    return smf.ols(
        "popularity ~ has_feature + duration_sec + explicit + energy + danceability", d
    ).fit(cov_type="HC3")


@pytest.fixture(scope="module")
def spec2(d):
    return smf.ols(
        "popularity ~ has_feature + duration_sec + explicit + energy + danceability "
        "+ valence + loudness + C(track_genre)",
        d,
    ).fit(cov_type="HC3")


def test_spec1_coefficient_is_positive_and_bounded(spec1):
    coef = spec1.params["has_feature"]
    assert 0 < coef < 2.0


def test_spec2_coefficient_shrinks_relative_to_spec1(spec1, spec2):
    assert spec2.params["has_feature"] < spec1.params["has_feature"]


def test_spec2_coefficient_is_small(spec2):
    # The whole point of the reanalysis: adjusted effect stays under 1 point
    # on the 0-100 scale.
    assert 0 <= spec2.params["has_feature"] < 1.0


def test_spec2_genre_fe_explains_far_more_variance(spec1, spec2):
    assert spec2.rsquared > 5 * spec1.rsquared


def test_vif_below_conventional_threshold(d):
    X = d[
        ["has_feature", "duration_sec", "explicit", "energy", "danceability", "valence", "loudness"]
    ].astype(float)
    Xz = (X - X.mean()) / X.std()
    Xz.insert(0, "const", 1.0)
    vifs = [
        variance_inflation_factor(Xz.values, i)
        for i, c in enumerate(Xz.columns)
        if c != "const"
    ]
    assert max(vifs) < 5.0


def test_genre_decomposition_sums_to_raw_gap(d):
    # Exact shift-share decomposition (mirrors notebooks/analysis.ipynb section 3):
    # composition = sum_g (p1_g - p0_g) * m0_g, within = sum_g p1_g * (m1_g - m0_g).
    # These two terms must sum to the raw gap with no residual, by construction.
    # A naive version that compares each group's exposure to the *blended*
    # genre-level mean does NOT satisfy this identity — that was a bug caught
    # while writing this test (see README "What changed" section).
    g0 = d.loc[d.has_feature == 0, "popularity"]
    g1 = d.loc[d.has_feature == 1, "popularity"]
    raw_gap = g1.mean() - g0.mean()

    n1 = d[d.has_feature == 1].groupby("track_genre").size()
    n0 = d[d.has_feature == 0].groupby("track_genre").size()
    m1 = d[d.has_feature == 1].groupby("track_genre")["popularity"].mean()
    m0 = d[d.has_feature == 0].groupby("track_genre")["popularity"].mean()
    assert n1.index.equals(n0.index)
    p1, p0 = n1 / n1.sum(), n0 / n0.sum()

    composition = ((p1 - p0) * m0).sum()
    within = (p1 * (m1 - m0)).sum()

    assert composition + within == pytest.approx(raw_gap, abs=1e-6)
    # Composition should dominate the raw gap, per the notebook's finding.
    assert composition / raw_gap > 0.9
