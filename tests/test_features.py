"""Basic tests for landslide_lk.features.

Run with: pytest tests/
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent / "src"))
from landslide_lk.features import (
    frequency_ratio,
    information_gain_ratio,
    rank_conditioning_factors,
    bin_continuous_column,
)


def _make_synthetic_df(seed: int = 0, n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    slope_class = rng.choice(["flat", "moderate", "steep"], size=n, p=[0.4, 0.4, 0.2])
    prob_map = {"flat": 0.05, "moderate": 0.3, "steep": 0.8}
    label = np.array(
        [rng.random() < prob_map[c] for c in slope_class]
    ).astype(int)
    noise_class = rng.choice(["a", "b", "c"], size=n)
    return pd.DataFrame(
        {"slope_class": slope_class, "noise_class": noise_class, "label": label}
    )


def test_frequency_ratio_direction():
    df = _make_synthetic_df()
    fr = frequency_ratio(df, "slope_class").set_index("slope_class")["frequency_ratio"]
    assert fr["steep"] > 1
    assert fr["flat"] < 1


def test_information_gain_ratio_ranks_signal_above_noise():
    df = _make_synthetic_df()
    igr_slope = information_gain_ratio(df, "slope_class")["information_gain_ratio"]
    igr_noise = information_gain_ratio(df, "noise_class")["information_gain_ratio"]
    assert igr_slope > igr_noise


def test_rank_conditioning_factors_sorted_descending():
    df = _make_synthetic_df()
    ranked = rank_conditioning_factors(df, ["slope_class", "noise_class"])
    igrs = ranked["information_gain_ratio"].tolist()
    assert igrs == sorted(igrs, reverse=True)


def test_bin_continuous_column_methods():
    rng = np.random.default_rng(1)
    series = pd.Series(rng.uniform(0, 80, 200))
    for method in ["equal_interval", "quantile"]:
        binned = bin_continuous_column(series, n_classes=5, method=method)
        assert binned.nunique() <= 5
