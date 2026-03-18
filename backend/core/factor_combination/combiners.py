"""MVP factor combination methods.

Inputs are factor value tables with schema: symbol, value.
All methods return a DataFrame with schema: symbol, value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd


def _align_on_symbol(
    factors: Mapping[str, pd.DataFrame],
    *,
    fill_value: float | None = None,
) -> pd.DataFrame:
    """Return wide matrix with index symbol and columns factor_name."""
    cols = []
    for name, df in factors.items():
        if df is None or df.empty:
            continue
        if "symbol" not in df.columns or "value" not in df.columns:
            raise ValueError(f"factor '{name}' must have columns: symbol, value")
        s = (
            df[["symbol", "value"]]
            .copy()
            .assign(symbol=lambda x: x["symbol"].astype(str))
            .set_index("symbol")["value"]
        )
        s = pd.to_numeric(s, errors="coerce")
        cols.append(s.rename(name))
    if not cols:
        raise ValueError("no factor inputs")
    wide = pd.concat(cols, axis=1)
    if fill_value is not None:
        wide = wide.fillna(fill_value)
    return wide


def combine_weighted_sum(
    factors: Mapping[str, pd.DataFrame],
    *,
    weights: Mapping[str, float] | None = None,
    normalize_weights: bool = True,
    fill_value: float = 0.0,
) -> pd.DataFrame:
    """Linear weighted sum across factors."""
    wide = _align_on_symbol(factors, fill_value=fill_value)
    w = {c: 1.0 for c in wide.columns}
    if weights:
        for k, v in weights.items():
            if k in w:
                w[k] = float(v)
    w_vec = np.array([w[c] for c in wide.columns], dtype=float)
    if normalize_weights:
        s = np.sum(np.abs(w_vec))
        if s > 0:
            w_vec = w_vec / s
    score = wide.to_numpy(dtype=float) @ w_vec
    out = pd.DataFrame({"symbol": wide.index.astype(str), "value": score})
    return out


def combine_rank_fusion(
    factors: Mapping[str, pd.DataFrame],
    *,
    method: str = "average",
    ascending: bool = False,
    fill_rank: float | None = None,
) -> pd.DataFrame:
    """Rank-based fusion.

Each factor is ranked cross-sectionally; then ranks are aggregated.
"""
    wide = _align_on_symbol(factors, fill_value=np.nan)
    ranks = wide.rank(axis=0, ascending=ascending, na_option="keep")
    if fill_rank is not None:
        ranks = ranks.fillna(float(fill_rank))
    if method == "average":
        agg = ranks.mean(axis=1)
    elif method == "sum":
        agg = ranks.sum(axis=1)
    elif method == "median":
        agg = ranks.median(axis=1)
    else:
        raise ValueError("rank fusion method must be one of: average, sum, median")
    # higher is better: invert if ascending ranks mean smaller value better
    score = -agg if ascending else agg
    return pd.DataFrame({"symbol": ranks.index.astype(str), "value": score.to_numpy(dtype=float)})


@dataclass(frozen=True)
class RegressionFit:
    weights: Dict[str, float]
    intercept: float
    r2: float


def fit_cross_sectional_regression(
    factors: Mapping[str, pd.DataFrame],
    *,
    target: pd.DataFrame,
    add_intercept: bool = True,
    fill_value: float = 0.0,
    ridge_alpha: float = 0.0,
) -> RegressionFit:
    """Fit OLS (optionally ridge) on cross-section: target ~ factors.

target schema: symbol, value (e.g., next-period returns).
"""
    if "symbol" not in target.columns or "value" not in target.columns:
        raise ValueError("target must have columns: symbol, value")
    y = (
        target[["symbol", "value"]]
        .copy()
        .assign(symbol=lambda x: x["symbol"].astype(str))
        .set_index("symbol")["value"]
    )
    y = pd.to_numeric(y, errors="coerce")

    wide = _align_on_symbol(factors, fill_value=np.nan)
    df = wide.join(y.rename("__y__"), how="inner")
    df = df.dropna(subset=["__y__"])
    if df.empty:
        raise ValueError("no overlapping symbols between factors and target")

    X = df[wide.columns].fillna(fill_value).to_numpy(dtype=float)
    yv = df["__y__"].to_numpy(dtype=float)

    if add_intercept:
        X = np.concatenate([np.ones((X.shape[0], 1), dtype=float), X], axis=1)
        names = ["__intercept__"] + list(wide.columns)
    else:
        names = list(wide.columns)

    # Closed-form ridge/OLS: beta = (X'X + aI)^-1 X'y
    XtX = X.T @ X
    if ridge_alpha > 0:
        XtX = XtX + ridge_alpha * np.eye(XtX.shape[0], dtype=float)
    Xty = X.T @ yv
    beta = np.linalg.solve(XtX, Xty)

    yhat = X @ beta
    ss_res = float(np.sum((yv - yhat) ** 2))
    ss_tot = float(np.sum((yv - np.mean(yv)) ** 2)) if yv.size > 1 else 0.0
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    weights = {n: float(b) for n, b in zip(names, beta)}
    intercept = float(weights.pop("__intercept__", 0.0)) if add_intercept else 0.0
    return RegressionFit(weights=weights, intercept=intercept, r2=r2)

