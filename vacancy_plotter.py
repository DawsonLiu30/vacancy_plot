from __future__ import annotations

"""
Vacancy map geometry mapping and rendering.

Responsibilities:
- Load structure into ASE atoms.
- Map vacancy energies onto atomic positions via symmetry rules.
- Render and export high-quality vacancy map figures.
"""

from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ase import Atoms
from ase.io import read
from matplotlib.colors import Normalize, TwoSlopeNorm

PathLike = Union[str, Path]


def load_atoms(poscar_path: PathLike) -> Atoms:
    """Load structure and normalize placeholder symbol X -> Al."""
    poscar_path = Path(poscar_path)
    if not poscar_path.exists():
        raise FileNotFoundError(f"Structure file not found: {poscar_path}")

    atoms = read(str(poscar_path))
    if "X" in atoms.get_chemical_formula():
        atoms.set_chemical_symbols(["Al"] * len(atoms))
    return atoms


def handle_symmetry(atoms: Atoms) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return radius, folded angle and distance-to-surface per atom."""
    pos = atoms.get_positions()
    cx, cy = np.mean(pos[:, 0]), np.mean(pos[:, 1])
    r_dist = np.sqrt((pos[:, 0] - cx) ** 2 + (pos[:, 1] - cy) ** 2)
    theta = np.arctan2(pos[:, 1] - cy, pos[:, 0] - cx)
    theta_deg = np.degrees(theta) % 360
    theta_fold = np.minimum(theta_deg % 90, 90 - (theta_deg % 90))
    d_surf = np.max(r_dist) - r_dist
    return r_dist, theta_fold, d_surf


def map_formation_energy(
    atoms: Atoms,
    df: pd.DataFrame,
    d_tol: float = 0.1,
    d_side_col: str = "d_side",
    formation_e_col: str = "formation_e",
    angle_threshold: float = 22.5,
) -> np.ndarray:
    """Map each atom to a formation energy based on d_side and symmetry angle."""
    _, theta_fold, d_surf = handle_symmetry(atoms)
    mapped_values = np.zeros(len(atoms))

    for i in range(len(atoms)):
        matches = df[np.abs(df[d_side_col] - d_surf[i]) < d_tol]
        if len(matches) == 0:
            mapped_values[i] = np.nan
        elif len(matches) == 1:
            mapped_values[i] = matches.iloc[0][formation_e_col]
        elif theta_fold[i] > angle_threshold:
            mapped_values[i] = matches[formation_e_col].min()
        else:
            mapped_values[i] = matches[formation_e_col].max()
    return mapped_values


def plot_vacancy_map(
    atoms: Atoms,
    mapped_values: np.ndarray,
    output_path: PathLike = "vacancy_map_final.png",
    title: str = "Vacancy Formation Energy Map (High Contrast)",
    cmap: str = "coolwarm",
    marker_size: float = 280.0,
    dpi: int = 300,
    elev: float = 90.0,
    azim: float = -90.0,
    orthographic: bool = True,
    center_zero: bool = False,
) -> Path:
    """Render and save the vacancy map."""
    valid = mapped_values[~np.isnan(mapped_values)]
    if len(valid) == 0:
        raise ValueError("No valid mapped values to plot")

    output_path = Path(output_path)
    if center_zero and np.min(valid) < 0 < np.max(valid):
        norm = TwoSlopeNorm(vmin=np.min(valid), vcenter=0.0, vmax=np.max(valid))
    else:
        norm = Normalize(vmin=np.min(valid), vmax=np.max(valid))

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")
    if orthographic:
        ax.set_proj_type("ortho")

    sc = ax.scatter(
        atoms.positions[:, 0],
        atoms.positions[:, 1],
        atoms.positions[:, 2],
        c=mapped_values,
        cmap=cmap,
        norm=norm,
        s=marker_size,
        edgecolors="none",
        alpha=1.0,
    )

    cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.05)
    cbar.set_label("Vacancy Formation Energy (eV)", fontsize=14, rotation=270, labelpad=25)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_axis_off()
    ax.view_init(elev=elev, azim=azim)
    plt.subplots_adjust(top=0.9, bottom=0.05, left=0.05, right=0.95)
    plt.savefig(output_path, dpi=dpi)
    plt.close(fig)
    return output_path
