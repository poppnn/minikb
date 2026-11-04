"""MiniKB : boîtier, plaque et keycaps paramétriques pour Fusion.

Relançable : supprime puis recrée les composants MiniKB_Assembly et Keycap_2u,
mais garde les User Parameters existants (tes réglages ne sont pas écrasés).
La plaque, le boîtier et les switches factices suivent cols/rows directement
dans la timeline ; les keycaps (une par légende) sont créées par ce script.
"""
import adsk.core
import adsk.fusion

# Légendes des keycaps, dans l'ordre des touches (ligne par ligne, depuis l'avant).
# None = "1", "2", ... jusqu'à cols*rows.
LEGENDS = None

# (nom, expression, unité, commentaire). Les valeurs incertaines sont signalées « à vérifier ».
PARAMS = [
    ("cols", "2", "", "Colonnes de touches"),
    ("rows", "4", "", "Rangées de touches"),
    ("key_pitch", "19.05 mm", "mm", "Pas MX"),
    ("wall", "2.4 mm", "mm", "Épaisseur des parois (6 lignes de 0,4)"),
    ("plate_thickness", "1.5 mm", "mm", "Épaisseur plaque, standard des clips MX"),
    ("switch_cutout", "14 mm", "mm", "Découpe MX nominale"),
    ("tolerance", "0.2 mm", "mm", "Jeu d'impression FDM"),
    ("case_height", "15 mm", "mm", "Du dessous du fond au dessus de la plaque"),
    ("screw_d", "2 mm", "mm", "Vis M2 (2.5 pour M2.5)"),
    ("insert_d", "3.2 mm", "mm", "Trou d'insert M2 à chaud (4.0 pour M2.5) à vérifier"),
    ("insert_depth", "5 mm", "mm", "Profondeur du trou d'insert"),
    ("pillar_d", "5.6 mm", "mm", "Diamètre des piliers"),
    ("pillar_inset", "4.6 mm", "mm", "Axe des piliers depuis la paroi intérieure"),
    ("side_gap", "1 mm", "mm", "Jeu latéral entre grille et paroi"),
    ("front_margin", "6 mm", "mm", "Zone avant (piliers)"),
    ("floor_t", "2 mm", "mm", "Épaisseur du fond"),
    ("corner_r", "3 mm", "mm", "Rayon des coins extérieurs"),
    ("ef_chamfer", "0.4 mm", "mm", "Chanfrein anti elephant foot"),
    ("lip_t", "1.2 mm", "mm", "Épaisseur de la lèvre d'emboîtement"),
    ("lip_h", "2.5 mm", "mm", "Hauteur de la lèvre sous la plaque"),
    ("notch_d", "0.8 mm", "mm", "Profondeur des encoches de clip"),
    ("notch_l", "3.1 mm", "mm", "Longueur des encoches"),
    ("notch_off", "1 mm", "mm", "Distance encoche - coin de la découpe"),
    ("board_w", "18 mm", "mm", "Largeur SuperMini"),
    ("board_l", "22.5 mm", "mm", "Longueur SuperMini"),
    ("pcb_t", "1 mm", "mm", "Épaisseur PCB SuperMini à vérifier"),
    ("board_gap", "0.5 mm", "mm", "Jeu carte - paroi arrière"),
    ("board_lift", "1.5 mm", "mm", "Hauteur des appuis sous la carte"),
    ("ledge_w", "1.5 mm", "mm", "Largeur des appuis sous la carte"),
    ("cradle_wall", "1.2 mm", "mm", "Épaisseur des butées de la carte"),
    ("cradle_h", "board_lift + pcb_t + 1 mm", "mm", "Hauteur des butées"),
    ("usb_w", "9 mm", "mm", "Largeur prise USB-C"),
    ("usb_l", "7.3 mm", "mm", "Profondeur prise USB-C"),
    ("usb_h", "3.2 mm", "mm", "Hauteur prise USB-C"),
    ("usb_x", "0 mm", "mm", "Décalage X de l'USB-C / centre carte"),
    ("usb_cut_w", "11 mm", "mm", "Découpe USB-C largeur (fiche)"),
    ("usb_cut_h", "5 mm", "mm", "Découpe USB-C hauteur"),
    ("led_x", "4 mm", "mm", "LED GPIO8 / centre carte, à vérifier sur ta carte"),
    ("led_y", "2 mm", "mm", "LED GPIO8, +Y vers l'USB, à vérifier"),
    ("led_hole", "3 mm", "mm", "Trou de LED"),
    ("boot_x", "-5.5 mm", "mm", "Bouton BOOT / centre carte, à vérifier"),
    ("boot_y", "7.5 mm", "mm", "Bouton BOOT, +Y vers l'USB, à vérifier"),
    ("boot_hole", "2 mm", "mm", "Trou d'accès BOOT (trombone)"),
    ("battery", "0", "", "1 = petite LiPo + TP4056 USB-C (relancer le script après changement)"),
    ("front_tp", "0", "", "1 = TP4056 sous les touches avant, USB-C en façade (relancer le script)"),
    ("tp_l", "28 mm", "mm", "Longueur TP4056 USB-C avec protection, à vérifier"),
    ("tp_w", "17.5 mm", "mm", "Largeur TP4056, à vérifier"),
    ("tp_pcb_t", "1 mm", "mm", "Épaisseur PCB TP4056, à vérifier"),
    ("tp_led_x", "0 mm", "mm", "LED de charge / centre TP4056, à vérifier"),
    ("tp_led_y", "-6 mm", "mm", "LED de charge, +Y vers l'USB, à vérifier"),
    ("bat_l", "30 mm", "mm", "Longueur LiPo, sens avant-arrière (502030 ~ 250 mAh)"),
    ("bat_w", "20 mm", "mm", "Largeur LiPo"),
    ("bat_t", "5 mm", "mm", "Épaisseur LiPo"),
    ("bat_zone", "bat_l + 4 mm", "mm", "Longueur ajoutée pour la LiPo si battery = 1"),
    ("board_zone", "28 mm + battery * (tp_l - board_l)", "mm", "Zone arrière des cartes"),
    ("sw_hole_w", "9 mm", "mm", "Trou interrupteur à glissière (SS12D00)"),
    ("sw_hole_h", "4.5 mm", "mm", "Trou interrupteur hauteur"),
    ("sw_hole_z", "4 mm", "mm", "Axe interrupteur au-dessus du fond"),
    ("sw_below", "5 mm", "mm", "Corps du switch sous le dessus de plaque"),
    ("sw_pins", "3.3 mm", "mm", "Pattes du switch sous le corps"),
    ("sw_housing", "6.6 mm", "mm", "Boîtier du switch au-dessus de la plaque, à vérifier"),
    ("sw_stem_top", "11.6 mm", "mm", "Sommet de la croix au-dessus de la plaque, à vérifier"),
    ("stem_insert", "3.6 mm", "mm", "Hauteur de croix engagée dans la keycap"),
    ("cap_gap", "1.05 mm", "mm", "Jeu entre keycaps voisines"),
    ("cap_h", "6.5 mm", "mm", "Hauteur keycap"),
    ("cap_draft", "1.5 mm", "mm", "Rétrécissement par côté entre base et dessus"),
    ("cap_r", "2 mm", "mm", "Rayon des coins de keycap"),
    ("cap_wall", "1.5 mm", "mm", "Paroi keycap (>= 1.2 pour buse 0.4)"),
    ("cap_chamfer", "0.4 mm", "mm", "Chanfrein du dessus (posé sur le plateau)"),
    ("stem_d", "5.5 mm", "mm", "Diamètre du stem MX"),
    ("cross_l", "4 mm", "mm", "Longueur des bras de la croix MX"),
    ("cross_w", "1.3 mm", "mm", "Épaisseur des bras de la croix MX"),
    ("stem_hole_l", "cross_l + tolerance / 2", "mm", "Trou de croix : 4.1 avec tolerance 0.2"),
    ("stem_hole_w", "cross_w + tolerance / 4", "mm", "Trou de croix : 1.35 avec tolerance 0.2"),
    ("stem_depth", "4 mm", "mm", "Profondeur du trou de croix"),
    ("stab_off", "11.938 mm", "mm", "Entraxe stabilisateur 2u"),
    ("legend_h", "6 mm", "mm", "Hauteur du texte de légende"),
    ("legend_depth", "0.4 mm", "mm", "Gravure de la légende"),
    ("inner_w", "cols * key_pitch + 2 * side_gap", "mm", "Largeur intérieure (calculée)"),
    ("inner_l", "front_margin + rows * key_pitch + battery * bat_zone + board_zone", "mm", "Longueur intérieure (calculée)"),
    ("board_cx", "inner_w / 2 - battery * (tp_w + 2 * tolerance + cradle_wall) / 2", "mm", "Centre X de la SuperMini (décalée si TP4056)"),
    ("tp_cx", "board_cx + (board_w + tp_w) / 2 + 2 * tolerance + cradle_wall", "mm", "Centre X du TP4056"),
    ("z_wall", "case_height - plate_thickness", "mm", "Haut des parois = dessous de plaque"),
    ("cap_seat", "sw_stem_top - stem_insert", "mm", "Bas de keycap au repos au-dessus de la plaque"),
]

app = adsk.core.Application.get()
design = None
H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(expr):
    """Valeur d'une expression, en cm (unité interne de Fusion)."""
    return design.unitsManager.evaluateExpression(expr, "mm")


def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(x, y, z)


def coll(items):
    c = adsk.core.ObjectCollection.create()
    for i in items:
        c.add(i)
    return c


# Anciennes valeurs par défaut remplacées : mises à jour seulement si tu ne les avais pas changées.
OLD_DEFAULTS = {"board_zone": "28 mm", "bat_l": "50 mm", "bat_zone": "bat_l + tp_w + 6 mm"}
OBSOLETE = ("tp_usb_z", "tp_usb_cut_w", "tp_usb_cut_h")


def set_params():
    ups = design.userParameters
    for name, expr, unit, comment in PARAMS:
        if not ups.itemByName(name):
            ups.add(name, vi(expr), unit, comment)
    for name, old in OLD_DEFAULTS.items():
        p = ups.itemByName(name)
        if p and p.expression.replace(" ", "") == old.replace(" ", ""):
            new = next(e for n, e, _, _ in PARAMS if n == name)
            p.expression = new
            p.comment = next(c for n, _, _, c in PARAMS if n == name)
    design.computeAll()  # sinon les paramètres dérivés (inner_l...) gardent leur ancienne valeur


class Sk:
    """Esquisse dont chaque cote est pilotée par une expression de paramètres."""

    def __init__(self, comp, plane, name):
        self.s = comp.sketches.add(plane)
        self.s.name = name
        self.o = self.s.originPoint
        self.dims = self.s.sketchDimensions
        self.cons = self.s.geometricConstraints
        self.k = 0

    def _eps(self):
        # Fusion refuse une cote depuis l'origine si un point déjà coté a exactement la même
        # coordonnée à la création : on décale un peu, la cote ramène à la valeur exacte.
        self.k += 1
        return 0.002 * self.k

    def _place(self, p, x, y, sx, sy):
        # Position d'un point / origine : None = sur l'axe (contrainte), sinon cote = |expr|.
        g = p.geometry
        tp = pt(g.x / 2 - 0.3, g.y / 2 - 0.3)
        if x is None and y is None:
            self.cons.addCoincident(p, self.o)
            return
        if x is None:
            self.cons.addVerticalPoints(self.o, p)
        else:
            self._dim(p, H, x, sx * ev(x), tp)
        if y is None:
            self.cons.addHorizontalPoints(self.o, p)
        else:
            self._dim(p, V, y, sy * ev(y), tp)

    def _dim(self, p, orient, expr, target, tp):
        # Une cote n'a pas de signe : le solveur de Fusion place parfois le point du mauvais côté de
        # l'origine. On vérifie, on ramène le point et on repose la cote.
        for _ in range(2):
            d = self.dims.addDistanceDimension(self.o, p, orient, tp)
            d.parameter.expression = expr
            cur = p.geometry.x if orient == H else p.geometry.y
            if abs(cur - target) < 1e-5:
                return
            d.deleteMe()
            delta = target - cur
            p.move(adsk.core.Vector3D.create(delta, 0, 0) if orient == H else adsk.core.Vector3D.create(0, delta, 0))
        raise RuntimeError(f"{self.s.name}: cote {expr} placée du mauvais côté")

    def rect(self, x, y, w, h, sx=1, sy=1):
        e = self._eps()
        X = sx * ev(x) + e if x else 0.0
        Y = sy * ev(y) + e if y else 0.0
        W, Hh = ev(w), ev(h)
        lines = self.s.sketchCurves.sketchLines.addTwoPointRectangle(pt(X, Y), pt(X + W, Y + Hh))
        # L'API n'ajoute pas les contraintes horizontales/verticales du rectangle.
        horiz = [l for l in lines if abs(l.startSketchPoint.geometry.y - l.endSketchPoint.geometry.y) < 1e-6]
        vert = [l for l in lines if l not in horiz]
        for l in horiz:
            self.cons.addHorizontal(l)
        for l in vert:
            self.cons.addVertical(l)
        bottom = min(horiz, key=lambda l: l.startSketchPoint.geometry.y)
        left = min(vert, key=lambda l: l.startSketchPoint.geometry.x)
        self.dims.addDistanceDimension(bottom.startSketchPoint, bottom.endSketchPoint, H, pt(X + W / 2, Y - 0.4)).parameter.expression = w
        self.dims.addDistanceDimension(left.startSketchPoint, left.endSketchPoint, V, pt(X - 0.4, Y + Hh / 2)).parameter.expression = h
        pts = [l.startSketchPoint for l in lines]
        corner = min(pts, key=lambda p: (p.geometry.x - X) ** 2 + (p.geometry.y - Y) ** 2)
        self._place(corner, x, y, sx, sy)
        return lines

    def centered_rect(self, w, h, cx=None, sx=1):
        """Rectangle w x h centré en (sx * cx, 0) ; cx = None pour l'origine."""
        if cx is None:
            x, rsx = f"({w}) / 2", -1
        elif sx > 0:
            x, rsx = f"({cx}) - ({w}) / 2", 1
        else:
            x, rsx = f"({cx}) + ({w}) / 2", -1
        return self.rect(x, f"({h}) / 2", w, h, sx=rsx, sy=-1)

    def circle(self, cx, cy, d, sx=1, sy=1):
        e = self._eps()
        X = sx * ev(cx) + e if cx else 0.0
        Y = sy * ev(cy) + e if cy else 0.0
        c = self.s.sketchCurves.sketchCircles.addByCenterRadius(pt(X, Y), ev(d) / 2)
        self.dims.addDiameterDimension(c, pt(X + ev(d), Y + ev(d))).parameter.expression = d
        self._place(c.centerSketchPoint, cx, cy, sx, sy)
        return c

    def profile_at(self, x, y):
        """Plus petit profil dont la boîte englobante contient (x, y) (cm, espace esquisse)."""
        best, best_area = None, None
        for p in self.s.profiles:
            bb = p.boundingBox
            if bb.minPoint.x <= x <= bb.maxPoint.x and bb.minPoint.y <= y <= bb.maxPoint.y:
                area = (bb.maxPoint.x - bb.minPoint.x) * (bb.maxPoint.y - bb.minPoint.y)
                if best is None or area < best_area:
                    best, best_area = p, area
        if best is None:
            raise RuntimeError(f"{self.s.name}: aucun profil en ({x}, {y})")
        return best

    def all_profiles(self):
        return [p for p in self.s.profiles]


def offset_plane(comp, expr, name):
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(comp.xYConstructionPlane, vi(expr))
    p = comp.constructionPlanes.add(inp)
    p.name = name
    return p


def extrude(comp, profiles, dist, op, name, body=None):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(profiles if not isinstance(profiles, list) else coll(profiles), op)
    inp.setDistanceExtent(False, vi(dist))
    if body is not None and op != NEW:
        inp.participantBodies = [body]
    f = ext.add(inp)
    f.name = name
    return f


def vertical_corner_edges(body, xs, ys):
    res = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if e.geometry.objectType != adsk.core.Line3D.classType():
            continue
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if abs(a.x - b.x) > 1e-5 or abs(a.y - b.y) > 1e-5:
            continue
        if any(abs(a.x - x) < 1e-4 for x in xs) and any(abs(a.y - y) < 1e-4 for y in ys):
            res.add(e)
    return res


def planar_face_at_z(body, z, normal_z):
    for f in body.faces:
        if f.geometry.objectType != adsk.core.Plane.classType():
            continue
        ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)  # normale sortante, contrairement à Plane.normal
        if ok and abs(n.z - normal_z) < 1e-6 and abs(f.pointOnFace.z - z) < 1e-5:
            return f
    raise RuntimeError(f"pas de face plane à z={z}")


def outer_loop_edges(face):
    for loop in face.loops:
        if loop.isOuter:
            return coll([e for e in loop.edges])
    raise RuntimeError("pas de boucle extérieure")


def fillet(comp, edges, r, name):
    inp = comp.features.filletFeatures.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(edges, vi(r), True)
    f = comp.features.filletFeatures.add(inp)
    f.name = name
    return f


def chamfer(comp, edges, d, name):
    inp = comp.features.chamferFeatures.createInput2()
    inp.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, vi(d), True)
    f = comp.features.chamferFeatures.add(inp)
    f.name = name
    return f


def grid_pattern(comp, entities, name):
    pats = comp.features.rectangularPatternFeatures
    inp = pats.createInput(coll(entities), comp.xConstructionAxis, vi("cols"), vi("key_pitch"),
                           adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    inp.setDirectionTwo(comp.yConstructionAxis, vi("rows"), vi("key_pitch"))
    f = pats.add(inp)
    f.name = name
    return f


# Positions partagées (expressions, origine = coin intérieur avant gauche)
# Avec la batterie, les piliers arrière avancent devant les berceaux (qui occupent toute la largeur).
BACK_Y = "inner_l - pillar_inset - battery * (tp_l + 2 mm)"
PILLARS = [("pillar_inset", "pillar_inset"), ("inner_w - pillar_inset", "pillar_inset"),
           ("pillar_inset", BACK_Y), ("inner_w - pillar_inset", BACK_Y)]
BOARD_CY = "inner_l - board_gap - board_l / 2"
TP_CY = "inner_l - board_gap - tp_l / 2"


def outer_rect(sk):
    return sk.rect("wall", "wall", "inner_w + 2 * wall", "inner_l + 2 * wall", sx=-1, sy=-1)


def outer_xy():
    w, il, iw = ev("wall"), ev("inner_l"), ev("inner_w")
    return [-w, iw + w], [-w, il + w]


BAT_Y0 = "front_margin + rows * key_pitch + 2 mm"  # début de la zone LiPo


def cradle(comp, plane, body, cx, w, l, height, prefix, front=False):
    """Butées en U ouvertes vers la paroi arrière (ou avant) + appuis sous les bords de la carte."""
    sk = Sk(comp, plane, prefix + "cradle")
    ow, iw = f"{w} + 2 * tolerance + 2 * cradle_wall", f"{w} + 2 * tolerance"
    if front:
        y = "board_gap"
        sk.rect(f"{cx} - {w} / 2 - tolerance - cradle_wall", "wall / 2", ow, f"wall / 2 + board_gap + {l} + tolerance + cradle_wall", sy=-1)
        sk.rect(f"{cx} - {w} / 2 - tolerance", "wall / 4", iw, f"wall / 4 + board_gap + {l} + tolerance", sy=-1)
        cy = ev(f"board_gap + {l} / 2")
    else:
        y = f"inner_l - board_gap - {l}"
        sk.rect(f"{cx} - {w} / 2 - tolerance - cradle_wall", f"{y} - tolerance - cradle_wall",
                ow, f"{l} + tolerance + cradle_wall + board_gap + wall / 2")
        sk.rect(f"{cx} - {w} / 2 - tolerance", f"{y} - tolerance", iw, f"{l} + tolerance + board_gap + wall / 4")
        cy = ev(f"inner_l - board_gap - {l} / 2")
    sk.rect(f"{cx} - {w} / 2 + ledge_w", f"{y} + ledge_w", f"{w} - 2 * ledge_w", f"{l} - 2 * ledge_w")
    extrude(comp, [sk.profile_at(ev(f"{cx} - {w} / 2 - tolerance - cradle_wall / 2"), cy)], height, JOIN, prefix + "stops", body)
    extrude(comp, [sk.profile_at(ev(f"{cx} - {w} / 2 + ledge_w / 2"), cy)], "board_lift", JOIN, prefix + "ledge", body)


def usb_cutout(comp, body, cx, pcb, prefix, front=False):
    """Découpe USB-C dans la paroi arrière (ou avant), centrée sur la prise d'une carte posée sur ses appuis."""
    p = offset_plane(comp, f"floor_t + board_lift + {pcb} + usb_h / 2 - usb_cut_h / 2", prefix + "PL")
    sk = Sk(comp, p, prefix + "cut")
    if front:
        sk.rect(f"{cx} - usb_cut_w / 2", "wall + 1 mm", "usb_cut_w", "wall + 2 mm", sy=-1)
    else:
        sk.rect(f"{cx} - usb_cut_w / 2", "inner_l - 1 mm", "usb_cut_w", "wall + 2 mm")
    extrude(comp, sk.all_profiles(), "usb_cut_h", CUT, prefix + "cutout", body)


def build_case(comp):
    sk = Sk(comp, comp.xYConstructionPlane, "CASE_outline")
    outer_rect(sk)
    sk.rect(None, None, "inner_w", "inner_l")
    wall_mid = -ev("wall") / 2
    ring = sk.profile_at(wall_mid, ev("inner_l") / 2)
    inner = sk.profile_at(ev("inner_w") / 2, ev("inner_l") / 2)
    floor = extrude(comp, [ring, inner], "floor_t", NEW, "Floor")
    body = floor.bodies.item(0)
    body.name = "Case"
    extrude(comp, [ring], "z_wall", JOIN, "Walls", body)
    xs, ys = outer_xy()
    fillet(comp, vertical_corner_edges(body, xs, ys), "corner_r", "Corners")

    # Piliers à insert
    p_floor = offset_plane(comp, "floor_t", "PL_floor_top")
    sk = Sk(comp, p_floor, "CASE_pillars")
    for x, y in PILLARS:
        sk.circle(x, y, "pillar_d")
    extrude(comp, sk.all_profiles(), "z_wall - floor_t", JOIN, "Pillars", body)
    p_top = offset_plane(comp, "z_wall", "PL_wall_top")
    sk = Sk(comp, p_top, "CASE_inserts")
    for x, y in PILLARS:
        sk.circle(x, y, "insert_d")
    extrude(comp, sk.all_profiles(), "-insert_depth", CUT, "Insert_holes", body)

    # Berceaux contre la paroi arrière : SuperMini, et TP4056 à sa droite si battery = 1
    cradle(comp, p_floor, body, "board_cx", "board_w", "board_l", "cradle_h", "Board_")
    usb_cutout(comp, body, "board_cx + usb_x", "pcb_t", "USB_")

    # Option batterie (features BAT_*, suspendues si battery = 0)
    cradle(comp, p_floor, body, "tp_cx", "tp_w", "tp_l", "board_lift + tp_pcb_t + 1 mm", "BAT_tp_")
    usb_cutout(comp, body, "tp_cx", "tp_pcb_t", "BAT_tp_usb_")
    # Rails de la LiPo, posée à plat entre les touches et les cartes
    sk = Sk(comp, p_floor, "BAT_lipo_rails")
    for x in ("inner_w / 2 - bat_w / 2 - tolerance - cradle_wall", "inner_w / 2 + bat_w / 2 + tolerance"):
        sk.rect(x, BAT_Y0, "cradle_wall", "bat_l")
    extrude(comp, sk.all_profiles(), "2 mm", JOIN, "BAT_lipo_rails", body)
    p = offset_plane(comp, "floor_t + sw_hole_z - sw_hole_h / 2", "BAT_PL_switch")
    sk = Sk(comp, p, "BAT_switch")
    sk.rect("wall + 1 mm", f"{BAT_Y0} + bat_l / 2 - sw_hole_w / 2", "wall + 2 mm", "sw_hole_w", sx=-1)
    extrude(comp, sk.all_profiles(), "sw_hole_h", CUT, "BAT_switch_cut", body)

    # Option front_tp (features FTP_*) : TP4056 sous les touches avant, USB-C dans la façade
    cradle(comp, p_floor, body, "inner_w / 2", "tp_w", "tp_l", "board_lift + tp_pcb_t + 1 mm", "FTP_tp_", front=True)
    usb_cutout(comp, body, "inner_w / 2", "tp_pcb_t", "FTP_usb_", front=True)

    chamfer(comp, outer_loop_edges(planar_face_at_z(body, 0, -1)), "ef_chamfer", "Elephant_foot")
    return body


def build_plate(comp):
    p_under = offset_plane(comp, "z_wall", "PL_plate_under")
    p_top = offset_plane(comp, "case_height", "PL_plate_top")
    sk = Sk(comp, p_under, "PLATE_outline")
    outer_rect(sk)
    plate = extrude(comp, sk.all_profiles(), "plate_thickness", NEW, "Plate")
    body = plate.bodies.item(0)
    body.name = "Plate"
    xs, ys = outer_xy()
    fillet(comp, vertical_corner_edges(body, xs, ys), "corner_r", "Corners")

    # Lèvre d'emboîtement qui rentre dans les parois
    sk = Sk(comp, p_under, "PLATE_lip")
    sk.rect("tolerance", "tolerance", "inner_w - 2 * tolerance", "inner_l - 2 * tolerance")
    sk.rect("tolerance + lip_t", "tolerance + lip_t", "inner_w - 2 * tolerance - 2 * lip_t", "inner_l - 2 * tolerance - 2 * lip_t")
    lip_mid = ev("tolerance + lip_t / 2")
    extrude(comp, [sk.profile_at(lip_mid, ev("inner_l") / 2)], "-lip_h", JOIN, "Lip", body)
    # shortcut: décidé à la construction, relancer le script si pillar_d ou pillar_inset change
    if ev("pillar_inset - pillar_d / 2 - tolerance") < ev("tolerance + lip_t"):
        sk = Sk(comp, p_under, "PLATE_lip_relief")
        for x, y in PILLARS:
            sk.circle(x, y, "pillar_d + 2 * tolerance")
        extrude(comp, sk.all_profiles(), "-lip_h", CUT, "Lip_relief", body)

    # Découpe MX de la touche (0, 0) avec encoches latérales, puis motif cols x rows
    sk = Sk(comp, p_top, "PLATE_switch")
    S = "(switch_cutout + tolerance)"
    x0 = f"side_gap + key_pitch / 2 - {S} / 2"
    y0 = f"front_margin + key_pitch / 2 - {S} / 2"
    sk.rect(x0, y0, S, S)
    for y in (f"{y0} + notch_off", f"{y0} + {S} - notch_off - notch_l"):
        sk.rect(f"{x0} - notch_d", y, "notch_d + 0.5 mm", "notch_l")
        sk.rect(f"{x0} + {S} - 0.5 mm", y, "notch_d + 0.5 mm", "notch_l")
    cut = extrude(comp, sk.all_profiles(), "-plate_thickness", CUT, "Switch_cutout", body)
    grid_pattern(comp, [cut], "Switch_grid")

    sk = Sk(comp, p_top, "PLATE_holes")
    for x, y in PILLARS:
        sk.circle(x, y, "screw_d + 2 * tolerance")
    sk.circle("board_cx + led_x", f"{BOARD_CY} + led_y", "led_hole")
    sk.circle("board_cx + boot_x", f"{BOARD_CY} + boot_y", "boot_hole")
    extrude(comp, sk.all_profiles(), "-plate_thickness", CUT, "Screw_LED_BOOT_holes", body)
    sk = Sk(comp, p_top, "BAT_tp_led")
    sk.circle("tp_cx + tp_led_x", f"{TP_CY} + tp_led_y", "led_hole")
    extrude(comp, sk.all_profiles(), "-plate_thickness", CUT, "BAT_tp_led_hole", body)

    chamfer(comp, outer_loop_edges(planar_face_at_z(body, ev("case_height"), 1)), "ef_chamfer", "Elephant_foot")
    return body


def build_board(comp):
    p = offset_plane(comp, "floor_t + board_lift", "PL_board")
    sk = Sk(comp, p, "BOARD_pcb")
    sk.rect("board_cx - board_w / 2", "inner_l - board_gap - board_l", "board_w", "board_l")
    body = extrude(comp, sk.all_profiles(), "pcb_t", NEW, "PCB").bodies.item(0)
    body.name = "SuperMini"
    p = offset_plane(comp, "floor_t + board_lift + pcb_t", "PL_board_top")
    sk = Sk(comp, p, "BOARD_usb")
    sk.rect("board_cx + usb_x - usb_w / 2", "inner_l - board_gap - usb_l", "usb_w", "usb_l")
    extrude(comp, sk.all_profiles(), "usb_h", JOIN, "USB_C", body)
    sk = Sk(comp, p, "BOARD_led_boot")
    sk.circle("board_cx + led_x", f"{BOARD_CY} + led_y", "1.5 mm")
    sk.circle("board_cx + boot_x", f"{BOARD_CY} + boot_y", "2.5 mm")
    extrude(comp, sk.all_profiles(), "1 mm", JOIN, "LED_BOOT_markers", body)

    # Factices de l'option batterie, pour vérifier les interférences
    p = offset_plane(comp, "floor_t + board_lift", "BAT_PL_tp")
    sk = Sk(comp, p, "BAT_tp_pcb")
    sk.rect("tp_cx - tp_w / 2", "inner_l - board_gap - tp_l", "tp_w", "tp_l")
    tp = extrude(comp, sk.all_profiles(), "tp_pcb_t", NEW, "BAT_TP4056").bodies.item(0)
    tp.name = "TP4056"
    p = offset_plane(comp, "floor_t + board_lift + tp_pcb_t", "BAT_PL_tp_top")
    sk = Sk(comp, p, "BAT_tp_usb")
    sk.rect("tp_cx - usb_w / 2", "inner_l - board_gap - usb_l", "usb_w", "usb_l")
    extrude(comp, sk.all_profiles(), "usb_h", JOIN, "BAT_TP_USB_C", tp)
    p = offset_plane(comp, "floor_t", "BAT_PL_lipo")
    sk = Sk(comp, p, "BAT_lipo")
    sk.rect("inner_w / 2 - bat_w / 2", BAT_Y0, "bat_w", "bat_l")
    extrude(comp, sk.all_profiles(), "bat_t", NEW, "BAT_LiPo").bodies.item(0).name = "LiPo"
    p = offset_plane(comp, "floor_t + board_lift", "FTP_PL_tp")
    sk = Sk(comp, p, "FTP_tp_pcb")
    sk.rect("inner_w / 2 - tp_w / 2", "board_gap", "tp_w", "tp_l")
    ftp = extrude(comp, sk.all_profiles(), "tp_pcb_t", NEW, "FTP_TP4056").bodies.item(0)
    ftp.name = "TP4056_front"
    p = offset_plane(comp, "floor_t + board_lift + tp_pcb_t", "FTP_PL_tp_top")
    sk = Sk(comp, p, "FTP_tp_usb")
    sk.rect("inner_w / 2 - usb_w / 2", "board_gap", "usb_w", "usb_l")
    extrude(comp, sk.all_profiles(), "usb_h", JOIN, "FTP_TP_USB_C", ftp)


def build_switches(comp):
    p_top = offset_plane(comp, "case_height", "PL_plate_top")
    cx = "side_gap + key_pitch / 2"
    cy = "front_margin + key_pitch / 2"
    sk = Sk(comp, p_top, "SW_bottom")
    sk.rect(f"{cx} - switch_cutout / 2", f"{cy} - switch_cutout / 2", "switch_cutout", "switch_cutout")
    body = extrude(comp, sk.all_profiles(), "-(sw_below + sw_pins)", NEW, "SW_body").bodies.item(0)
    body.name = "Switch_MX"
    sk = Sk(comp, p_top, "SW_top")
    sk.rect(f"{cx} - 7.8 mm", f"{cy} - 7.8 mm", "15.6 mm", "15.6 mm")
    extrude(comp, sk.all_profiles(), "sw_housing", JOIN, "SW_housing", body)
    p = offset_plane(comp, "case_height + sw_housing", "PL_sw_housing_top")
    sk = Sk(comp, p, "SW_stem")
    sk.rect(f"{cx} - cross_l / 2", f"{cy} - cross_w / 2", "cross_l", "cross_w")
    sk.rect(f"{cx} - cross_w / 2", f"{cy} - cross_l / 2", "cross_w", "cross_l")
    extrude(comp, sk.all_profiles(), "sw_stem_top - sw_housing", JOIN, "SW_stem", body)
    grid_pattern(comp, [body], "Switch_grid")


def build_keycap(comp, units, legend):
    w = f"{units} * key_pitch - cap_gap"
    top_w = f"{w} - 2 * cap_draft"
    sk_base = Sk(comp, comp.xYConstructionPlane, "CAP_base")
    sk_base.centered_rect(w, "key_pitch - cap_gap")
    p_top = offset_plane(comp, "cap_h", "PL_cap_top")
    sk_top = Sk(comp, p_top, "CAP_top")
    sk_top.centered_rect(top_w, "key_pitch - cap_gap - 2 * cap_draft")
    loft = comp.features.loftFeatures
    inp = loft.createInput(NEW)
    inp.loftSections.add(sk_base.all_profiles()[0])
    inp.loftSections.add(sk_top.all_profiles()[0])
    inp.isSolid = True
    f = loft.add(inp)
    f.name = "Cap_shape"
    body = f.bodies.item(0)
    body.name = comp.name

    side = adsk.core.ObjectCollection.create()
    for e in body.edges:
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if abs(a.z - b.z) > 1e-4:
            side.add(e)
    fillet(comp, side, "cap_r", "Cap_corners")
    chamfer(comp, outer_loop_edges(planar_face_at_z(body, ev("cap_h"), 1)), "cap_chamfer", "Cap_chamfer")
    shell = comp.features.shellFeatures
    sin = shell.createInput(coll([planar_face_at_z(body, 0, -1)]), False)
    sin.insideThickness = vi("cap_wall")
    shell.add(sin).name = "Cap_shell"

    # Stem MX (+ stems de stabilisateur en 2u)
    offsets = [None] if units == 1 else [None, "stab_off", "-stab_off"]
    sk = Sk(comp, comp.xYConstructionPlane, "CAP_stem")
    for off in offsets:
        if off == "-stab_off":
            sk.circle("stab_off", None, "stem_d", sx=-1)
        else:
            sk.circle(off, None, "stem_d")
    stem = extrude(comp, sk.all_profiles(), "cap_h - cap_wall", JOIN, "Stem", body)
    sk = Sk(comp, comp.xYConstructionPlane, "CAP_cross")
    for off in offsets:
        cx = None if off is None else "stab_off"
        sx = -1 if off == "-stab_off" else 1
        sk.centered_rect("stem_hole_l", "stem_hole_w", cx, sx=sx)
        sk.centered_rect("stem_hole_w", "stem_hole_l", cx, sx=sx)
    extrude(comp, sk.all_profiles(), "stem_depth", CUT, "Cross_hole", body)

    if legend:
        sk = Sk(comp, p_top, "CAP_legend")
        half = ev(top_w) / 2 - 0.1
        hy = ev("key_pitch - cap_gap - 2 * cap_draft") / 2 - 0.1
        ti = sk.s.sketchTexts.createInput2(legend, ev("legend_h"))
        ti.setAsMultiLine(pt(-half, -hy), pt(half, hy), adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                          adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
        ti.fontName = "Arial"
        text = sk.s.sketchTexts.add(ti)
        extrude(comp, text, "-legend_depth", CUT, "Legend", body)
    return body


def translate(x, y, z):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(x, y, z)
    return m


def new_comp(parent, name, m=None):
    occ = parent.occurrences.addNewComponent(m or adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ


def apply_options(comps):
    for prefix, name in (("BAT_", "battery"), ("FTP_", "front_tp")):
        off = design.userParameters.itemByName(name).value < 0.5
        for comp in comps:
            for f in list(comp.features.extrudeFeatures):
                if f.name.startswith(prefix):
                    f.timelineObject.isSuppressed = off


def run(_context):
    global design
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    for occ in list(root.occurrences):
        if occ.component.name in ("MiniKB_Assembly", "Keycap_2u"):
            occ.deleteMe()
    set_params()

    asm = new_comp(root, "MiniKB_Assembly").component
    case = new_comp(asm, "Case").component
    build_case(case)
    plate = new_comp(asm, "Plate").component
    build_plate(plate)
    board = new_comp(asm, "Board_SuperMini").component
    build_board(board)
    build_switches(new_comp(asm, "Switches_dummy").component)

    ups = design.userParameters
    cols, rows = int(round(ups.itemByName("cols").value)), int(round(ups.itemByName("rows").value))
    legends = LEGENDS or [str(i + 1) for i in range(cols * rows)]
    pitch, z = ev("key_pitch"), ev("case_height + cap_seat")
    for i in range(cols * rows):
        c, r = i % cols, i // cols
        x = ev("side_gap") + (c + 0.5) * pitch
        y = ev("front_margin") + (r + 0.5) * pitch
        occ = new_comp(asm, f"Keycap_{i + 1}", translate(x, y, z))
        build_keycap(occ.component, 1, legends[i] if i < len(legends) else "")

    # Variante 2u, posée à côté (hors assemblage)
    k2 = new_comp(root, "Keycap_2u", translate(-ev("wall") - 3.5, ev("inner_l") / 2, 0))
    build_keycap(k2.component, 2, "")

    apply_options([case, plate, board])
    for name in OBSOLETE:
        p = design.userParameters.itemByName(name)
        if p:
            p.deleteMe()
    print(f"MiniKB: {cols}x{rows}, inner {ev('inner_w') * 10:.2f} x {ev('inner_l') * 10:.2f} mm")
