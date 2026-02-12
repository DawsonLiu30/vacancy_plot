from __future__ import annotations

"""
Structure input/output helpers.

Responsibilities:
- Handle legacy POSCAR text input normalization.
- Resolve which structure file should be fed to the plotting pipeline.
"""

from pathlib import Path


def fix_poscar_header(input_file: str = "poscar.txt", output_file: str = "POSCAR_fixed") -> bool:
    """
    Normalize a non-standard POSCAR text file into a readable POSCAR.

    Keeps original coordinate mode (Direct/Cartesian).
    Returns True on success, False on missing/invalid input.
    """
    clean_header_template = """Al
1.0
 40.0000000000000000    0.0000000000000000    0.0000000000000000
  0.0000000000000000   40.0000000000000000    0.0000000000000000
  0.0000000000000000    0.0000000000000000   20.1946484659124970
Al
{natom}
{coord_mode}
"""
    coords_lines = []
    coord_mode = None
    try:
        with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_s = line.strip()
                if line_s in ("Direct", "Cartesian"):
                    coord_mode = line_s
                    continue
                if coord_mode and line_s:
                    coords_lines.append(line)
        if not coord_mode or not coords_lines:
            return False
        clean_header = clean_header_template.format(natom=len(coords_lines), coord_mode=coord_mode)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(clean_header)
            f.writelines(coords_lines)
        return True
    except FileNotFoundError:
        return False


def resolve_structure_path(source: str, poscar_path: str) -> Path:
    """
    Resolve final structure path for plotting.

    source='vasp': use provided poscar_path.
    source='txt': normalize poscar.txt into POSCAR_fixed and return it.
    """
    if source == "txt":
        if not fix_poscar_header("poscar.txt", "POSCAR_fixed"):
            raise ValueError("poscar.txt not found or invalid POSCAR body.")
        return Path("POSCAR_fixed")
    return Path(poscar_path)
