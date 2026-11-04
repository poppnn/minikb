"""Pose les STL bruts de Fusion (stl/raw) dans l'orientation d'impression et vérifie qu'ils sont fermés.

Usage : python orient_and_check.py [dossier]   (nécessite trimesh ; défaut : ce dossier)
Sortie : <dossier>/stl/*.stl prêts pour le slicer ; code retour 1 si un maillage n'est pas manifold.
"""
import pathlib
import sys

import numpy as np
import trimesh

HERE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else __file__).resolve()
HERE = HERE if HERE.is_dir() else HERE.parent
RAW, OUT = HERE / "stl" / "raw", HERE / "stl"
FLIP = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])

# Plaque et keycaps : face visible sur le plateau (surface lisse, légende gravée nette, sans support).
FLIPPED = ("plate", "keycap")


def main():
    ok = True
    for src in sorted(RAW.glob("*.stl")):
        mesh = trimesh.load_mesh(src)
        if src.stem.startswith(FLIPPED):
            mesh.apply_transform(FLIP)
        if src.stem != "assembly":
            lo, hi = mesh.bounds
            mesh.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
        mesh.export(OUT / src.name)
        manifold = mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        bodies = mesh.split(only_watertight=False)
        size = mesh.extents
        if src.stem == "assembly":
            # Visualisation seulement : les pièces se touchent dans un seul STL, pas à imprimer.
            print(f"{src.stem:12s} (visualisation, non imprimable)  {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:5.1f} mm")
            continue
        ok &= manifold
        print(f"{src.stem:12s} {'OK ' if manifold else 'NON'} manifold  corps={len(bodies):2d}  "
              f"{size[0]:6.1f} x {size[1]:6.1f} x {size[2]:5.1f} mm  volume={mesh.volume / 1000:6.2f} cm3")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
