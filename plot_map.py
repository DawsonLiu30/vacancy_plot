from __future__ import annotations

"""
CLI entrypoint and workflow orchestrator.

Responsibilities:
- Parse user arguments.
- Orchestrate data loading, energy mapping, and plotting.
- Delegate file normalization and plotting logic to dedicated modules.
"""

from argparse import ArgumentParser

from vacancy_data import attach_formation_energy, read_vacancy_data
from vacancy_io import resolve_structure_path
from vacancy_plotter import load_atoms, map_formation_energy, plot_vacancy_map

ANCHOR_EF = 0.67


def plot_vacancy_and_structure(
    file_name_vasp: str,
    csv_path: str,
    output_path: str = "vacancy_map_final.png",
    anchor_ef: float = ANCHOR_EF,
    d_side_col: str = "d_side",
    total_e_col: str = "total_e",
    formation_e_col: str = "formation_e",
    d_tol: float = 0.1,
    energy_scale: int | None = None,
    angle_threshold: float = 22.5,
    title: str = "Vacancy Formation Energy Map (High Contrast)",
    cmap: str = "coolwarm",
    marker_size: float = 280.0,
    dpi: int = 300,
    elev: float = 90.0,
    azim: float = -90.0,
    perspective: bool = False,
    center_zero: bool = False,
) -> str:
    atoms = load_atoms(file_name_vasp)
    df = read_vacancy_data(
        csv_path,
        d_side_col=d_side_col,
        total_e_col=total_e_col,
        formation_e_col=formation_e_col,
    )
    df = attach_formation_energy(
        df,
        anchor_ef=anchor_ef,
        natoms=len(atoms),
        energy_scale=energy_scale,
    )
    mapped_values = map_formation_energy(
        atoms,
        df,
        d_tol=d_tol,
        d_side_col="d_side",
        formation_e_col="formation_e",
        angle_threshold=angle_threshold,
    )
    out = plot_vacancy_map(
        atoms,
        mapped_values,
        output_path=output_path,
        title=title,
        cmap=cmap,
        marker_size=marker_size,
        dpi=dpi,
        elev=elev,
        azim=azim,
        orthographic=not perspective,
        center_zero=center_zero,
    )
    return str(out)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Plot vacancy formation energy map from structure + CSV")
    parser.add_argument("--poscar", default="poscar.vasp", help="Input POSCAR/vasp structure path")
    parser.add_argument("--csv", default="vacancy_data.csv", help="Vacancy table CSV path")
    parser.add_argument(
        "--source",
        choices=["txt", "vasp"],
        default="vasp",
        help="Use poscar.txt + header fix or read poscar.vasp directly",
    )
    parser.add_argument("--out", default="vacancy_map_final.png", help="Output image path")
    parser.add_argument("--anchor-ef", type=float, default=ANCHOR_EF, help="Anchor formation energy in eV")
    parser.add_argument("--d-side-col", default="d_side", help="Distance column name in CSV")
    parser.add_argument("--total-e-col", default="total_e", help="Total energy column name in CSV")
    parser.add_argument("--formation-e-col", default="formation_e", help="Formation energy column name in CSV")
    parser.add_argument("--d-tol", type=float, default=0.1, help="Distance matching tolerance")
    parser.add_argument("--energy-scale", type=int, default=None, help="Override energy scaling factor")
    parser.add_argument("--angle-threshold", type=float, default=22.5, help="Symmetry branch threshold in degree")
    parser.add_argument("--title", default="Vacancy Formation Energy Map (High Contrast)", help="Plot title")
    parser.add_argument("--cmap", default="coolwarm", help="Matplotlib colormap name")
    parser.add_argument("--marker-size", type=float, default=280.0, help="Scatter marker size")
    parser.add_argument("--dpi", type=int, default=300, help="Output PNG DPI")
    parser.add_argument("--elev", type=float, default=90.0, help="Camera elevation angle")
    parser.add_argument("--azim", type=float, default=-90.0, help="Camera azimuth angle")
    parser.add_argument("--perspective", action="store_true", help="Use perspective projection")
    parser.add_argument("--center-zero", action="store_true", help="Center color normalization at 0 when valid")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        poscar_path = resolve_structure_path(args.source, args.poscar)
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc

    output = plot_vacancy_and_structure(
        file_name_vasp=str(poscar_path),
        csv_path=args.csv,
        output_path=args.out,
        anchor_ef=args.anchor_ef,
        d_side_col=args.d_side_col,
        total_e_col=args.total_e_col,
        formation_e_col=args.formation_e_col,
        d_tol=args.d_tol,
        energy_scale=args.energy_scale,
        angle_threshold=args.angle_threshold,
        title=args.title,
        cmap=args.cmap,
        marker_size=args.marker_size,
        dpi=args.dpi,
        elev=args.elev,
        azim=args.azim,
        perspective=args.perspective,
        center_zero=args.center_zero,
    )
    print(f"Saved vacancy map to {output}")


if __name__ == "__main__":
    main()
