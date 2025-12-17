import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
import pandas as pd
import os
from matplotlib.colors import TwoSlopeNorm


def handle_symmetry():
    ...

def get_colors():
    ...

def plot_vacancy_and_structure(file_name_vasp):

    # read structure
    atoms = read(file_name_vasp)

    #if len(atoms)!=1:
    #    atoms=atoms[-1]

    # get positions
    x,y,z = atoms.get_positions()[:, 0], atoms.get_positions()[:, 1], atoms.get_positions()[:, 2]


    # todo: get colors
    #get_colors()



    # todo: prepare plot
    #vmin = np.nanmin(final_values)
    #vmax = np.max(final_values)
    #norm = TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
    # todo: symmetry adapations
    #handle_symmetry()

    # plot
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 【關鍵修改】設定為正交投影 (Orthographic)
    ax.set_proj_type('ortho')

    sc = ax.scatter(x,y,z,
                    #c=final_values, cmap='coolwarm', norm=norm,
                    s=280, edgecolors='none', alpha=1.0)

    #cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.05)
    #cbar.set_label('Vacancy Formation Energy (eV)', fontsize=14, rotation=270, labelpad=25)

    #ax.set_title(f"Vacancy Formation Energy Map (Orthographic)\n[Internal Ref: Center = {ANCHOR_EF} eV, White = 0 eV]", fontsize=16, fontweight='bold', pad=20)
    #ax.set_axis_off()
    ax.view_init(elev=90, azim=-90)

    plt.subplots_adjust(top=0.9, bottom=0.05, left=0.05, right=0.95)
    outfile = "vacancy_formation_energy_ortho.png"
    plt.savefig(outfile, dpi=300)
    print(f"Saved as {outfile} (Orthographic Projection)")
    plt.show()