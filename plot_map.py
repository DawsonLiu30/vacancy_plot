import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
import pandas as pd
import os
from matplotlib.colors import TwoSlopeNorm

# ================= 參數設定 =================
ANCHOR_EF = 0.67

# ================= 1. 讀取結構 =================
def fix_poscar_header(input_file="poscar.vasp", output_file="POSCAR_fixed"):
    clean_header_template = """Al
1.0
 40.0000000000000000    0.0000000000000000    0.0000000000000000
  0.0000000000000000   40.0000000000000000    0.0000000000000000
  0.0000000000000000    0.0000000000000000   20.1946484659124970
Al
{natom}
Direct
"""
    coords_lines = []
    found_direct = False
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if ("Direct" in line) or ("Cartesian" in line):
                    found_direct = True
                    continue
                if found_direct:
                    s = line.strip()
                    if not s: continue
                    coords_lines.append(line)
        if not found_direct or len(coords_lines) == 0: return False
        natom = len(coords_lines)
        clean_header = clean_header_template.format(natom=natom)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_header)
            f.writelines(coords_lines)
        return True
    except FileNotFoundError: return False

if not fix_poscar_header("poscar.txt", "POSCAR_fixed"):
    print("Error: poscar.txt not found.")
    exit()

atoms = read("POSCAR_fixed")
pos = atoms.get_positions()
natoms_system = len(atoms)
vac_natoms = natoms_system - 1

# 計算幾何
cx, cy = np.mean(pos[:, 0]), np.mean(pos[:, 1])
r_dist = np.sqrt((pos[:, 0] - cx)**2 + (pos[:, 1] - cy)**2)
theta = np.arctan2(pos[:, 1] - cy, pos[:, 0] - cx)
theta_deg = np.degrees(theta) % 360
theta_90 = theta_deg % 90
theta_45 = np.minimum(theta_90, 90 - theta_90)
geometric_id = np.column_stack((np.round(r_dist, 3), np.round(theta_45, 3)))
unique_rows, inverse_indices = np.unique(geometric_id, axis=0, return_inverse=True)

# ================= 2. 數據 =================
data = {
    "case": ["vac_L1_001", "vac_L1_006", "vac_L2_001", "vac_L1_000", "vac_L2_000",
             "vac_L2_004", "vac_L2_006", "vac_L1_004", "vac_L1_005", "vac_L2_002",
             "vac_L1_002", "vac_L2_005", "vac_L2_009", "vac_L1_003", "vac_L2_003",
             "vac_L1_009", "vac_L2_007", "vac_L1_007", "vac_L2_010", "vac_L1_008",
             "vac_L2_008", "vac_L2_011", "vac_L1_010", "vac_L2_012"],
    "total_e": [-56.11657, -56.11570, -56.11541, -56.11517, -56.11511,
                -56.11394, -56.11379, -56.11317, -56.11308, -56.11306,
                -56.11307, -56.11298, -56.11309, -56.11297, -56.11306,
                -56.11311, -56.11310, -56.11283, -56.11303, -56.11309,
                -56.11312, -56.11305, -56.11285, -56.11275],
    "d_side": [0.000000, 0.557526, 0.844575, 1.437010, 1.743220,
               1.743220, 2.056725, 2.707877, 3.395800, 3.395800,
               3.755661, 4.512689, 4.912680, 5.329358, 5.765005,
               6.222474, 7.218628, 7.768634, 7.768634, 9.020819,
               9.759875, 10.624589, 11.715466, 13.480543]
}
df = pd.DataFrame(data)
center_idx = df['d_side'].idxmax()
center_energy_per_atom = df.loc[center_idx, 'total_e']
df['delta_sys'] = (df['total_e'] - center_energy_per_atom) * vac_natoms
df['formation_e'] = ANCHOR_EF + df['delta_sys']

# ================= 3. 繪圖 =================
max_r = np.max(r_dist)
mapped_values = np.zeros(len(unique_rows))

for i, geom in enumerate(unique_rows):
    u_r, u_theta = geom
    calc_d = max_r - u_r
    matches = df[np.abs(df['d_side'] - calc_d) < 0.1]
    if len(matches) == 0: mapped_values[i] = np.nan
    elif len(matches) == 1: mapped_values[i] = matches.iloc[0]['formation_e']
    else:
        val_high = matches['formation_e'].max()
        val_low = matches['formation_e'].min()
        if u_theta > 22.5: mapped_values[i] = val_low
        else: mapped_values[i] = val_high

final_values = mapped_values[inverse_indices]

vmin = np.nanmin(final_values)
vmax = np.max(final_values)
norm = TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# 【關鍵修改】設定為正交投影 (Orthographic)
ax.set_proj_type('ortho')  

sc = ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2],
                c=final_values, cmap='coolwarm', norm=norm,
                s=280, edgecolors='none', alpha=1.0)

cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.05)
cbar.set_label('Vacancy Formation Energy (eV)', fontsize=14, rotation=270, labelpad=25)

ax.set_title(f"Vacancy Formation Energy Map (Orthographic)\n[Internal Ref: Center = {ANCHOR_EF} eV, White = 0 eV]", fontsize=16, fontweight='bold', pad=20)
ax.set_axis_off()
ax.view_init(elev=90, azim=-90)

plt.subplots_adjust(top=0.9, bottom=0.05, left=0.05, right=0.95)
outfile = "vacancy_formation_energy_ortho.png"
plt.savefig(outfile, dpi=300)
print(f"Saved as {outfile} (Orthographic Projection)")
plt.show()