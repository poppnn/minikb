"""Vérifications du modèle MiniKB dans Fusion (santé, contraintes, jeux, régénération cols/rows)."""
import adsk.core
import adsk.fusion

app = adsk.core.Application.get()


def health(d):
    bad = []
    for comp in d.allComponents:
        for f in comp.features:
            if not f.isSuppressed and f.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                bad.append(f"{comp.name}/{f.name}: {f.errorOrWarningMessage}")
    return bad


def unconstrained(d):
    # Les esquisses de texte (légendes) ne peuvent pas être totalement contraintes.
    return [f"{c.name}/{s.name}" for c in d.allComponents for s in c.sketches
            if not s.isFullyConstrained and s.sketchTexts.count == 0]


def boxes(d):
    asm = d.rootComponent.occurrences.itemByName("MiniKB_Assembly:1")
    out = {}
    for o in asm.childOccurrences:
        if o.component.name in ("Case", "Plate", "Switches_dummy"):
            # La boîte de l'occurrence n'est pas à jour juste après computeAll ; celle des corps l'est.
            bbs = [b.boundingBox for b in o.component.bRepBodies]
            w = max(b.maxPoint.x for b in bbs) - min(b.minPoint.x for b in bbs)
            l = max(b.maxPoint.y for b in bbs) - min(b.minPoint.y for b in bbs)
            out[o.component.name] = (round(w * 10, 2), round(l * 10, 2), len(bbs))
    return out


def run(_context):
    d = adsk.fusion.Design.cast(app.activeProduct)
    print("santé:", health(d) or "OK")
    print("esquisses non contraintes:", unconstrained(d) or "aucune")
    print("2x4:", boxes(d))
    ups = d.userParameters
    ups.itemByName("cols").expression = "3"
    ups.itemByName("rows").expression = "3"
    d.computeAll()
    print("3x3 santé:", health(d) or "OK", boxes(d))
    ups.itemByName("cols").expression = "2"
    ups.itemByName("rows").expression = "4"
    d.computeAll()
    print("retour 2x4 santé:", health(d) or "OK", boxes(d))
