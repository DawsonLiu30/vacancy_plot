# Vacancy Plot Integration Notes

## This repo's role
This project should stay as an analysis/post-processing module:
- Input: structure file (POSCAR/vasp) + vacancy CSV.
- Output: vacancy formation energy map PNG.

## Recommended boundaries
- `nanostructure_mod`: generate and mutate structures.
- `nano_tensile_TFvW`: run tensile simulations.
- `vacancy_plot`: convert structure + vacancy energies into visualization.

## Public functions to call
- `vacancy_io.resolve_structure_path(source, poscar_path)`
- `vacancy_data.read_vacancy_data(csv_path)`
- `vacancy_data.attach_formation_energy(df, anchor_ef, natoms)`
- `vacancy_plotter.load_atoms(poscar_path)`
- `vacancy_plotter.map_formation_energy(atoms, df, d_tol=0.1)`
- `vacancy_plotter.plot_vacancy_map(atoms, mapped_values, output_path)`

## CLI entrypoint
Use `/Users/dawson666/Desktop/vacancy_plot/plot_map.py`:

```bash
python3 plot_map.py --poscar poscar.vasp --csv vacancy_data.csv --out vacancy_map_final.png
```

This keeps integration lightweight: other repos only need to provide files, then call this script or import the public functions above.
