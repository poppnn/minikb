"""Captures PNG et export STL du modèle MiniKB (à lancer après minikb_fusion.py)."""
import os

import adsk.core
import adsk.fusion

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
app = adsk.core.Application.get()
VO = adsk.core.ViewOrientations


def occs(d):
    asm = d.rootComponent.occurrences.itemByName("MiniKB_Assembly:1")
    return asm, {o.component.name: o for o in asm.childOccurrences}


def shot(name, orientation, w=1400, h=1000):
    vp = app.activeViewport
    cam = vp.camera
    cam.viewOrientation = orientation
    cam.isFitView = True
    vp.camera = cam
    vp.refresh()
    adsk.doEvents()
    vp.saveAsImageFile(os.path.join(OUT, "png", name), w, h)


def show(parts, names, visible):
    for n, o in parts.items():
        if n in names:
            o.isLightBulbOn = visible


def export_stl(d, entity, name):
    em = d.exportManager
    opt = em.createSTLExportOptions(entity, os.path.join(OUT, "stl", "raw", name))
    opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    opt.sendToPrintUtility = False
    em.execute(opt)


def run(_context):
    d = adsk.fusion.Design.cast(app.activeProduct)
    os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "stl", "raw"), exist_ok=True)
    for comp in d.allComponents:
        comp.isSketchFolderLightBulbOn = False
        comp.isConstructionFolderLightBulbOn = False
    k2u = d.rootComponent.occurrences.itemByName("Keycap_2u:1")
    asm, parts = occs(d)

    # Exports : chaque pièce dans son repère assemblé ; orient_and_check.py les pose pour l'impression.
    export_stl(d, parts["Case"], "case.stl")
    export_stl(d, parts["Plate"], "plate.stl")
    for n, o in parts.items():
        if n.startswith("Keycap_"):
            export_stl(d, o, n.lower() + ".stl")
    export_stl(d, k2u, "keycap_2u.stl")
    export_stl(d, asm, "assembly.stl")

    k2u.isLightBulbOn = False
    shot("assembly_iso.png", VO.IsoTopRightViewOrientation)
    shot("top.png", VO.TopViewOrientation)
    shot("bottom.png", VO.BottomViewOrientation)
    shot("back_usb.png", VO.BackViewOrientation)

    # Intérieur : plaque, switches et keycaps masqués pour voir berceau, piliers et USB-C
    upper = [n for n in parts if n == "Plate" or n == "Switches_dummy" or n.startswith("Keycap_")]
    show(parts, upper, False)
    shot("case_inside_top.png", VO.TopViewOrientation)
    shot("case_inside_iso.png", VO.IsoTopLeftViewOrientation)
    show(parts, upper, True)

    # Vue éclatée temporaire, puis retour aux positions d'origine
    lift = {"Plate": 3.0, "Switches_dummy": 3.0}
    saved = {}
    for n, o in parts.items():
        dz = lift.get(n, 5.5 if n.startswith("Keycap_") else 0)
        if not dz:
            continue
        saved[n] = o.transform2.copy()
        m = o.transform2
        t = m.translation
        t.z += dz
        m.translation = t
        o.transform2 = m
    shot("exploded_iso.png", VO.IsoTopRightViewOrientation)
    for n, m in saved.items():
        parts[n].transform2 = m
    k2u.isLightBulbOn = True
    print("exports et captures dans", OUT)
