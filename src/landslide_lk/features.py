"""Feature-selection statistics for landslide conditioning factors.

Reimplements, in pandas, the two correlation/relevance measures used in prior
Sri Lankan landslide susceptibility literature (Frequency Ratio and Information
Gain Ratio) — previously computed by hand via QGIS raster pixel counts. Working
on the extracted point-feature table directly is equivalent and far faster to
iterate on.

Both functions expect a DataFrame with:
  - one column per conditioning factor (categorical, or already binned if the
    factor is continuous — see `bin_continuous_column` below)
  - a binary label column (1 = landslide, 0 = non-landslide)
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def bin_continuous_column(
    series: pd.Series, n_classes: int = 5, method: str = "equal_interval"
) -> pd.Series:
    """Bin a continuous conditioning factor (slope, TWI, rainfall, ...) into classes.

    Parameters
    ----------
    method
        "equal_interval" reproduces the approach used in prior work (min-to-max
        divided into n equal-width bins) — simple but can concentrate most of the
        data in one or two bins for skewed variables like rainfall.
        "quantile" gives each bin roughly equal sample counts instead.
        "natural_breaks" (Jenks) groups by natural gaps in the data — usually the
        most defensible choice, requires the `jenkspy` package.
    """
    if method == "equal_interval":
        return pd.cut(series, bins=n_classes, labels=False)
    if method == "quantile":
        return pd.qcut(series, q=n_classes, labels=False, duplicates="drop")
    if method == "natural_breaks":
        import jenkspy

        breaks = jenkspy.jenks_breaks(series.dropna().values, n_classes=n_classes)
        return pd.cut(series, bins=breaks, labels=False, include_lowest=True)
    raise ValueError(f"Unknown method: {method}")


def frequency_ratio(df: pd.DataFrame, factor_col: str, label_col: str = "label") -> pd.DataFrame:
    """Compute Frequency Ratio for each class of one conditioning factor.

    FR = (landslide pixels/points in class / total landslide pixels/points)
         / (total pixels/points in class / total pixels/points in study area)

    FR > 1  → class is over-represented among landslides (positive association)
    FR < 1  → class is under-represented (negative association)
    FR ≈ 1  → no meaningful association

    Returns a tidy DataFrame with one row per class, sorted by FR descending, so
    the highest-association classes are immediately visible — worth sanity
    checking that "high association" classes actually show FR > 1 before writing
    conclusions from this table (see docs/baseline_comparison.md for a case in
    prior work where this wasn't checked).
    """
    total_positive = (df[label_col] == 1).sum()
    total_count = len(df)

    rows = []
    for cls, group in df.groupby(factor_col, observed=True):
        class_positive = (group[label_col] == 1).sum()
        class_count = len(group)

        numerator = class_positive / total_positive if total_positive else np.nan
        denominator = class_count / total_count if total_count else np.nan
        fr = numerator / denominator if denominator else np.nan

        rows.append(
            {
                factor_col: cls,
                "n_points": class_count,
                "n_landslide": class_positive,
                "frequency_ratio": fr,
            }
        )

    result = pd.DataFrame(rows).sort_values("frequency_ratio", ascending=False)
    result = result.reset_index(drop=True)
    return result


def _entropy(labels: pd.Series) -> float:
    """Shannon entropy of a binary (or multi-class) label column."""
    probs = labels.value_counts(normalize=True)
    return float(-(probs * np.log2(probs)).sum())


def information_gain_ratio(
    df: pd.DataFrame, factor_col: str, label_col: str = "label"
) -> dict:
    """Compute Information Gain and Information Gain Ratio for one conditioning factor.

    Higher Information Gain Ratio → higher predictive ability for that factor.
    A factor with IGR == 0 has no predictive value for the label and is a
    reasonable candidate to drop from the feature pool.
    """
    base_entropy = _entropy(df[label_col])

    weighted_entropy = 0.0
    split_info = 0.0
    n_total = len(df)

    for _, group in df.groupby(factor_col, observed=True):
        weight = len(group) / n_total
        weighted_entropy += weight * _entropy(group[label_col])
        if weight > 0:
            split_info -= weight * np.log2(weight)

    info_gain = base_entropy - weighted_entropy
    igr = info_gain / split_info if split_info > 0 else 0.0

    return {
        "factor": factor_col,
        "base_entropy": base_entropy,
        "weighted_entropy": weighted_entropy,
        "split_info": split_info,
        "information_gain": info_gain,
        "information_gain_ratio": igr,
    }


def rank_conditioning_factors(
    df: pd.DataFrame, factor_cols: list[str], label_col: str = "label"
) -> pd.DataFrame:
    """Run Information Gain Ratio across every candidate conditioning factor at once.

    Use this as the first cell of notebooks/06b_feature_selection.ipynb to get
    a single ranked table — factors with the lowest IGR are your first candidates
    to drop, but check against Frequency Ratio too before removing anything, since
    a factor can have a weak *overall* IGR while still having one strongly
    predictive class.
    """
    results = [information_gain_ratio(df, col, label_col) for col in factor_cols]
    ranked = pd.DataFrame(results).sort_values(
        "information_gain_ratio", ascending=False
    )
    return ranked.reset_index(drop=True)
