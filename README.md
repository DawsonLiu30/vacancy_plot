# Vacancy Plot Tool

This project is a standalone post-processing tool.
It converts a structure file + vacancy energy table into a vacancy energy map PNG.

## Project structure

```text
vacancy_plot/
├── plot_map.py          # CLI entrypoint, workflow orchestration
├── vacancy_io.py        # structure input helpers (legacy poscar.txt normalization)
├── vacancy_data.py      # CSV reading/validation + formation energy conversion
├── vacancy_plotter.py   # geometry mapping + figure rendering
├── requirements.txt     # runtime dependencies
├── README.md            # user guide
└── INTEGRATION_NOTES.md # integration boundary notes
```

Responsibility rule:
- `plot_map.py` does not implement heavy logic.
- Data logic stays in `vacancy_data.py`.
- Structure file normalization stays in `vacancy_io.py`.
- Geometry and plotting stay in `vacancy_plotter.py`.

## Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Quick start

```bash
python3 plot_map.py \
  --poscar poscar.vasp \
  --csv vacancy_data.csv \
  --out vacancy_map_final.png
```

## Input modes

1. CSV provides `total_e` + `d_side`:
- Tool computes `formation_e` from `total_e`.
- Formula: `formation_e = anchor_ef + (total_e - center_e) * scale`.
- Default `scale = natoms - 1` unless `--energy-scale` is given.

2. CSV already provides `formation_e` + `d_side`:
- Tool uses `formation_e` directly.
- No conversion needed.

## Custom column names

```bash
python3 plot_map.py \
  --poscar my_structure.vasp \
  --csv my_vacancy_table.csv \
  --d-side-col distance_to_surface \
  --total-e-col energy_total \
  --formation-e-col vf_energy \
  --out my_vacancy_map.png
```

If `vf_energy` exists, it will be used directly.
If not, `energy_total` is used to compute formation energy.

## Quality controls

Useful rendering options:
- `--cmap coolwarm`
- `--marker-size 280`
- `--dpi 300`
- `--center-zero`
- `--elev 90 --azim -90`
- `--perspective` (default is orthographic)

## POSCAR txt compatibility

If your old workflow uses `poscar.txt`, run:

```bash
python3 plot_map.py --source txt --csv vacancy_data.csv --out vacancy_formation_energy_ortho.png
```
