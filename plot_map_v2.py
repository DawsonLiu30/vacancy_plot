import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
import pandas as pd
from matplotlib.colors import Normalize
import os
import sys

ANCHOR_EF = 0.67

def handle_symmetry(atoms):
    """"
    # todo
    ADD Documentation
    """
    pos = atoms.get_positions()
    cx, cy = np.mean(pos[:, 0]), np.mean(pos[:, 1])
    r_dist = np.sqrt((pos[:, 0] - cx)**2 + (pos[:, 1] - cy)**2)
    theta = np.arctan2(pos[:, 1] - cy, pos[:, 0] - cx)
    
    theta_deg = np.degrees(theta) % 360
    theta_fold = np.minimum(theta_deg % 90, 90 - (theta_deg % 90))
    d_surf = np.max(r_dist) - r_dist
    return r_dist, theta_fold, d_surf

def get_colors(atoms, df):
    """"
       # todo
       ADD Documentation
    """
    _, theta_fold, d_surf = handle_symmetry(atoms)
    mapped_values = np.zeros(len(atoms))
    
    for i in range(len(atoms)):
        matches = df[np.abs(df['d_side'] - d_surf[i]) < 0.1]
        if len(matches) == 0:
            mapped_values[i] = np.nan
        elif len(matches) == 1:
            mapped_values[i] = matches.iloc[0]['formation_e']
        else:
            if theta_fold[i] > 22.5:
                mapped_values[i] = matches['formation_e'].min()
            else:
                mapped_values[i] = matches['formation_e'].max()
    return mapped_values

def plot_vacancy_and_structure(file_name_vasp, csv_path):
    """"
       # todo
       ADD Documentation
    """
    if not os.path.exists(file_name_vasp) or not os.path.exists(csv_path):
        return

    try:
        atoms = read(file_name_vasp)
    except:
        return

    if 'X' in atoms.get_chemical_formula():
        atoms.set_chemical_symbols(['Al'] * len(atoms))

    df = pd.read_csv(csv_path)
    center_e = df.loc[df['d_side'].idxmax(), 'total_e']
    df['formation_e'] = ANCHOR_EF + (df['total_e'] - center_e) * (len(atoms) - 1)

    final_values = get_colors(atoms, df)
    valid = final_values[~np.isnan(final_values)]
    
    if len(valid) == 0: return

    norm = Normalize(vmin=np.min(valid), vmax=np.max(valid))

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_proj_type('ortho')

    sc = ax.scatter(atoms.positions[:, 0], atoms.positions[:, 1], atoms.positions[:, 2],
                    c=final_values, cmap='coolwarm', norm=norm, s=280, edgecolors='none', alpha=1.0)

    cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.05)
    cbar.set_label('Vacancy Formation Energy (eV)', fontsize=14, rotation=270, labelpad=25)
    
    ax.set_title("Vacancy Formation Energy Map (High Contrast)", fontsize=16, fontweight='bold', pad=20)
    ax.set_axis_off()
    ax.view_init(elev=90, azim=-90)

    plt.subplots_adjust(top=0.9, bottom=0.05, left=0.05, right=0.95)
    plt.savefig("vacancy_map_final.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    plot_vacancy_and_structure("poscar.vasp", "vacancy_data.csv")