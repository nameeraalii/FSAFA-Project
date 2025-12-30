import pandas as pd
import numpy as np

# -----------------------------
# Normalization helpers
# -----------------------------
def normalize_series(series, lower, upper, invert=False):
    x = (series - lower) / (upper - lower)
    x = x.clip(0, 1)
    return 1 - x if invert else x


# -----------------------------
# Composite Forensic Risk Score
# -----------------------------
def compute_frs(m, sloan, f, z, weights=None):
    """
    Returns DataFrame with normalized scores + FRS
    """
    if weights is None:
        weights = {"m": 0.4, "s": 0.2, "f": 0.2, "z": 0.2}

    m_n = normalize_series(m, -3, 3, invert=False)      # Beneish
    s_n = normalize_series(sloan, -0.2, 0.2, invert=False)
    f_n = normalize_series(f, 0, 9, invert=True)        # Piotroski (high = good)
    z_n = normalize_series(z, 0, 5, invert=True)        # Altman (high = safe)

    frs = (
        weights["m"] * m_n +
        weights["s"] * s_n +
        weights["f"] * f_n +
        weights["z"] * z_n
    )

    return pd.DataFrame({
        "M_norm": m_n,
        "Sloan_norm": s_n,
        "F_norm": f_n,
        "Z_norm": z_n,
        "FRS": frs.round(4)
    })


# -----------------------------
# Signal + Position Sizing
# -----------------------------
def position_engine(
    frs_df,
    current_weight=0.05,
    aggressiveness=0.10,
    min_w=-0.02,
    max_w=0.08
):
    out = frs_df.copy()

    out["Signal"] = np.select(
        [
            out["FRS"] < 0.3,
            out["FRS"] > 0.7
        ],
        ["LONG", "SHORT"],
        default="HOLD"
    )

    out["Δ_weight"] = aggressiveness * (out["FRS"] - 0.5)
    out["Target_weight"] = (
        current_weight + out["Δ_weight"]
    ).clip(min_w, max_w)

    return out
def execution_engine(
    engine_df,
    portfolio_value,
    price,
    current_weight
):
    out = engine_df.copy()

    # Guard rails
    if price <= 0 or portfolio_value <= 0:
        raise ValueError("Price and portfolio value must be positive")

    # Current exposure
    current_value = portfolio_value * current_weight
    current_shares = current_value / price

    # Target exposure
    out["Target_value"] = portfolio_value * out["Target_weight"]
    out["Target_shares"] = out["Target_value"] / price

    # Replace inf / NaN safely
    out["Target_shares"] = (
        out["Target_shares"]
        .replace([float("inf"), float("-inf")], pd.NA)
        .fillna(0)
    )

    shares_to_trade = out["Target_shares"] - current_shares

    out["Shares_to_trade"] = (
        shares_to_trade
        .replace([float("inf"), float("-inf")], pd.NA)
        .fillna(0)
        .round(0)
        .astype(int)
    )

    return out
