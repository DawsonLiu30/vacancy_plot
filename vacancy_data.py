from __future__ import annotations

"""
Vacancy table data operations.

Responsibilities:
- Read/validate CSV vacancy tables.
- Normalize column names for downstream workflow.
- Compute formation energy when only total energy is provided.
"""

from pathlib import Path
from typing import Union

import pandas as pd

PathLike = Union[str, Path]


def read_vacancy_data(
    csv_path: PathLike,
    d_side_col: str = "d_side",
    total_e_col: str = "total_e",
    formation_e_col: str = "formation_e",
) -> pd.DataFrame:
    """
    Read vacancy input table from CSV.

    Requires a distance column and either total energy or formation energy.
    Output is normalized to:
    - d_side
    - total_e (optional)
    - formation_e (optional)
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Vacancy data file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if d_side_col not in df.columns:
        raise ValueError(f"Missing required column '{d_side_col}' in {csv_path}")

    has_total = total_e_col in df.columns
    has_formation = formation_e_col in df.columns
    if not has_total and not has_formation:
        raise ValueError(
            f"CSV must contain either '{total_e_col}' or '{formation_e_col}' column."
        )

    out = pd.DataFrame({"d_side": df[d_side_col]})
    if has_total:
        out["total_e"] = df[total_e_col]
    if has_formation:
        out["formation_e"] = df[formation_e_col]
    return out.copy()


def attach_formation_energy(
    df: pd.DataFrame,
    anchor_ef: float,
    natoms: int,
    energy_scale: int | None = None,
) -> pd.DataFrame:
    """
    Compute formation energy and return a new DataFrame.

    formation_e = anchor_ef + (total_e - center_e) * scale
    center_e uses the row with maximum d_side.
    """
    if "formation_e" in df.columns:
        return df.copy()

    if "total_e" not in df.columns:
        raise ValueError("No total_e column found to compute formation_e")

    out = df.copy()
    if energy_scale is None:
        if natoms < 2:
            raise ValueError("natoms must be >= 2 for vacancy calculation")
        scale = natoms - 1
    else:
        scale = energy_scale

    center_idx = out["d_side"].idxmax()
    center_e = out.loc[center_idx, "total_e"]
    out["formation_e"] = anchor_ef + (out["total_e"] - center_e) * scale
    return out


def write_vacancy_data(df: pd.DataFrame, csv_path: PathLike) -> None:
    """Write vacancy DataFrame to CSV."""
    csv_path = Path(csv_path)
    df.to_csv(csv_path, index=False)
