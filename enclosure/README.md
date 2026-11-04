# MiniKB : boîtier, plaque et keycaps

Modèle paramétrique Fusion généré par script. Défaut : 2 × 4 touches, boîtier de 44,9 × 115 × 15 mm, keycaps de 18 mm.

| Fichier | Rôle |
|---|---|
| `minikb_fusion.py` | Construit tout le modèle (User Parameters, composants, timeline). Relançable. |
| `fusion_checks.py` | Contrôles : santé de la timeline, esquisses contraintes, test de régénération 3×3. |
| `fusion_export.py` | Exporte `stl/raw/*.stl` et les captures `png/`. |
| `orient_and_check.py` | Pose les STL pour l'impression dans `stl/` et vérifie qu'ils sont fermés (trimesh). |
| `minikb.f3d` | Archive Fusion du modèle paramétrique (Fichier → Ouvrir → depuis mon ordinateur). |
| `stl/case.stl`, `stl/plate.stl`, `stl/keycap_1..8.stl`, `stl/keycap_2u.stl` | Prêts à trancher. |
| `stl/assembly.stl` | Assemblage complet, pour visualiser seulement (pas à imprimer). |
| `png/` | Vues iso, dessus, dessous, arrière (USB-C), intérieur du boîtier, éclatée. |

## Variantes 2 / 4 / 6 / 8 touches

Chaque variante est enregistrée dans Fusion (projet « 1 », dossier `MiniKB`) et exportée dans `variants/<n>_touches/` (`stl/` prêts à imprimer, `stl/raw/` bruts, `png/`). Le dossier `stl/` à la racine correspond à la version 8 touches.

| Touches | Grille | Document Fusion | Boîtier (L × l × h) | GPIO par défaut |
|---|---|---|---|---|
| 2 | 2 × 1 | MiniKB 2 touches (2x1) | 44,9 × 57,9 × 15 mm | 0, 1 |
| 4 | 2 × 2 | MiniKB 4 touches (2x2) | 44,9 × 76,9 × 20 mm | 0, 1, 3, 4 |
| 6 | 2 × 3 | MiniKB 6 touches (2x3) | 44,9 × 96,0 × 15 mm | 0, 1, 3, 4, 5, 6 |
| 8 | 2 × 4 | MiniKB 8 touches (2x4) | 44,9 × 115,0 × 15 mm | 0, 1, 3, 4, 5, 6, 7, 10 |
| 2 + batterie | 2 × 1 | MiniKB 2 touches batterie (2x1) | 44,9 × 97,3 × 15 mm | 0, 1 |
| 4 + batterie | 2 × 2 | MiniKB 4 touches batterie (2x2) | 44,9 × 116,4 × 15 mm | 0, 1, 3, 4 |
| 6 + batterie | 2 × 3 | MiniKB 6 touches batterie (2x3) | 44,9 × 135,5 × 15 mm | 0, 1, 3, 4, 5, 6 |
| 8 + batterie | 2 × 4 | MiniKB 8 touches batterie (2x4) | 44,9 × 154,5 × 15 mm | 0, 1, 3, 4, 5, 6, 7, 10 |

Les variantes batterie sont dans `variants/<n>_touches_batterie/`.

**4 touches sans batterie : inserts M3, vis M3 × 14 et TP4056 en façade.** Ce document seul (`MiniKB 4 touches (2x2)` et `variants/4_touches/`) diffère des autres :
- boîtier épaissi à 20 mm (`case_height`), même plaque, même empreinte et même entraxe des vis ;
- inserts M3 à chaud dans des trous de Ø 4 mm (`insert_d`), profonds de 13 mm (`insert_depth`) pour laisser passer le reste de la vis ; piliers Ø 7,2 mm (`pillar_d`), la lèvre de la plaque est dégagée autour ;
- vis M3 × 14 : pointe à 6 mm du dessous, fond du trou à 5,5 mm ;
- TP4056 USB-C 26 × 17 mm (`tp_l`, `tp_w`) sous les touches avant, prise dans la façade, ESP32-C3 à l'arrière (`front_tp` = 1) ; 4 mm de jeu entre le haut de sa prise et les pattes des switches pour les fils.

- berceau de la SuperMini rallongé de 1 mm (`board_l` = 23,5) : la carte ne rentrait pas à 22,5 ;
- trou d'interrupteur à glissière (SS12D00, 9 × 4,5 mm) dans la paroi gauche, à mi-longueur (`ftp_sw_y`), entre le TP4056 et la SuperMini : à coller par l'intérieur ;
- prises USB-C à fleur de la face (`usb_flush` = 1) : le bord de chaque carte entre dans une poche de la paroi, et il ne reste devant qu'une peau de 0,8 mm percée juste à la forme de la prise (oblong, 0,2 mm de jeu). Cette peau empêche aussi la carte de ressortir. **Mesure de combien la prise dépasse du PCB sur tes cartes** et reporte-le dans `usb_overhang` (SuperMini) et `tp_usb_overhang` (TP4056), 0,8 mm par défaut : c'est l'épaisseur de la peau. Pour poser une carte, engage d'abord la prise dans son trou, carte légèrement inclinée, puis rabats l'autre bout dans le berceau.

Enfonce les inserts à fleur du haut des piliers : le trou continue en dessous, ne pousse pas plus loin. La LED de charge du TP4056 n'est pas visible (sous les touches). Les autres variantes et les valeurs par défaut du script restent en M2 + inserts, sans `front_tp`.

Pour chaque variante : timeline sans erreur, toutes les pièces fermées (manifold), et aucune interférence (vérifiée sur la 2 touches sans batterie, la plus compacte, et sur les quatre variantes batterie). Le firmware reste le même : la config par défaut a 8 touches, supprime celles en trop dans le web UI. Jusqu'à 4 touches, toutes peuvent réveiller le clavier de la veille (GPIO 0 à 5).

## Ce qu'il faut acheter

- 8 switches MX (Cherry, Gateron ou Kailh), version 3 ou 5 pattes (couper les 2 picots plastiques des 5 pattes si besoin)
- 1 ESP32-C3 SuperMini
- 4 inserts filetés à chaud M2, Ø ext. 3,2 mm, longueur 4 mm (ou M2.5 : passer `screw_d` = 2.5 et `insert_d` = 4)
- 4 vis M2 × 6 mm, tête cylindrique ou bombée
- Fil fin (AWG 26-28), un peu d'adhésif double face ou de mousse pour tenir la carte en place
- Option batterie : LiPo 502030 (~250 mAh, 5 × 20 × 30 mm, avec connecteur ou fils), module TP4056 USB-C avec protection (28 × 17,5 mm), interrupteur à glissière SS12D00

## Impression

Réglages communs : PLA ou PETG, couche 0,2 mm, buse 0,4 mm, 3 périmètres, aucun support.

| Pièce | Orientation (déjà appliquée dans `stl/`) | Remplissage | Remarques |
|---|---|---|---|
| Boîtier | Fond sur le plateau | 20 % | La découpe USB-C fait un pont de 11 mm. |
| Plaque | Dessus sur le plateau, lèvre vers le haut | 100 % | 1,5 mm, soit 7-8 couches : du 100 % pour la rigidité. |
| Keycaps | Dessus sur le plateau, croix vers le haut | 100 % | La légende gravée de 0,4 mm sort nette au plateau. La croix est imprimée verticalement, donc précise en XY. Le surplomb des flancs fait environ 13°. |

J'ai choisi cette orientation des keycaps parce qu'à l'envers (croix en bas), il faudrait des supports sous le plafond intérieur. Avec le dessus au plateau, tout monte en pente douce. En contrepartie, le dessus est plat (pas de creux concave, qui demanderait des supports).

Toutes les pièces ont un chanfrein de 0,4 mm sur l'arête posée au plateau (`ef_chamfer`, `cap_chamfer`) pour compenser l'elephant foot.

Avant d'imprimer les 8 keycaps, imprime-en une seule et teste-la sur un switch. Si elle est trop dure, monte `tolerance` à 0,25. Si elle a du jeu, descends à 0,15. Le trou de la croix vaut `cross_l + tolerance/2` × `cross_w + tolerance/4`, soit 4,1 × 1,35 mm avec 0,2.

## Montage

1. Insérer les 4 inserts à chaud dans les piliers du boîtier.
2. Clipser les switches dans la plaque (par le dessus). Ils tiennent sans colle avec une plaque de 1,5 mm.
3. Souder une patte de chaque switch à son GPIO et relier l'autre patte au GND en guirlande (voir `../docs/wiring.svg`).
4. Poser la SuperMini dans son berceau, USB-C contre la paroi arrière, et la caler avec un adhésif double face.
5. Poser la plaque (la lèvre rentre dans les parois) puis visser les 4 vis M2 × 6.
6. Emboîter les keycaps.

Le trou de 3 mm au-dessus de la carte laisse voir la LED. Le trou de 2 mm permet d'appuyer sur BOOT avec un trombone (3 s pour le mode config).

## Changer le nombre de touches

Dans Fusion : Modifier → Modifier les paramètres, puis change `cols` et `rows`. La plaque, le boîtier, les piliers, le berceau, la découpe USB et les switches factices se recalculent dans la timeline. Je l'ai vérifié en 3 × 3 : boîtier de 63,95 × 95,95 mm, timeline saine.

Les keycaps sont créées par le script, une par légende. Après avoir changé `cols`/`rows`, relance `minikb_fusion.py` pour obtenir le bon nombre de keycaps, bien placées. Tes paramètres sont conservés. Exemples :

- 2 × 3 : `cols = 2`, `rows = 3` (6 touches)
- 3 × 3 : `cols = 3`, `rows = 3` (9 touches)
- 1 × 4 : la largeur intérieure tombe à 21 mm, trop étroite pour la SuperMini (18 mm + butées). Garde `cols` ≥ 2.

Pour changer les légendes, modifie `LEGENDS = ["Mail", "Sig", ...]` en haut de `minikb_fusion.py`, puis relance-le. L'ordre est ligne par ligne, en partant de l'avant à gauche. Fusion ne peut pas lier un texte d'esquisse à un User Parameter, d'où cette liste dans le script.

Pour reconstruire depuis Fusion : Utilitaires → Scripts et compléments → `+` → Script depuis l'appareil. Choisis un dossier qui contient `minikb_fusion.py` (le dossier doit porter le même nom que le fichier). Ensuite, lance `fusion_export.py` puis `python orient_and_check.py`.

## Option batterie

Mets `battery = 1`, puis relance `minikb_fusion.py`. Le script active alors toutes les fonctions `BAT_*` (boîtier, plaque, pièces factices) ; il les suspend quand `battery = 0`.

- **À l'arrière** : la SuperMini à gauche et le TP4056 à droite, chacun dans son berceau. Les deux berceaux partagent une butée, et les deux USB-C sortent **côte à côte par la paroi arrière** (entraxe 19,35 mm, 8,35 mm de paroi entre les deux découpes). Le boîtier ne s'élargit pas : les deux cartes tiennent pile dans les 40,1 mm intérieurs d'une grille à 2 colonnes, donc garde `cols` ≥ 2.
- **Au milieu** : la LiPo se pose à plat sur le fond entre les touches et les cartes, tenue par deux rails latéraux de 2 mm. Le boîtier s'allonge de 39,5 mm : `bat_zone` (34 mm) pour la LiPo, plus 5,5 mm parce que le TP4056 est plus long que la SuperMini.
- **Piliers arrière** : ils avancent de part et d'autre de la LiPo, car les berceaux occupent toute la largeur.
- **Interrupteur** : il passe par la paroi gauche, au niveau de la LiPo.
- **Plaque** : un trou de 3 mm au-dessus de la LED de charge du TP4056.

Câblage : LiPo → B+/B- du TP4056, OUT+ → interrupteur → broche 5V de la SuperMini, OUT- → GND. Ne branche pas l'USB de la SuperMini pendant que l'interrupteur est sur ON : la sortie du TP4056 et l'USB seraient reliées sans diode. Pour charger, branche l'USB-C du TP4056 ; pour flasher, mets l'interrupteur sur OFF puis branche l'USB-C de la SuperMini.

Pour une autre batterie, change `bat_l` (sens avant-arrière), `bat_w` et `bat_t`. Avec la grille à 2 colonnes, `bat_w` peut aller jusqu'à environ 24 mm sans toucher les piliers.

## Cotes à vérifier sur ton matériel

Ces valeurs sont des paramètres, avec un défaut raisonnable. Mesure-les sur tes pièces :

| Paramètre | Défaut | Pourquoi |
|---|---|---|
| `led_x`, `led_y`, `boot_x`, `boot_y` | (4 ; 2), (-5,5 ; 7,5) mm depuis le centre de la carte, +Y vers l'USB | L'implantation varie selon les clones de SuperMini. **À mesurer en priorité.** |
| `pcb_t` | 1,0 mm | Épaisseur du PCB, qui fixe la hauteur de la découpe USB-C. |
| `sw_housing`, `sw_stem_top` | 6,6 et 11,6 mm au-dessus de la plaque | Fixent la hauteur des keycaps dans l'assemblage. Varie un peu selon la marque. |
| `tp_l`, `tp_w`, `tp_pcb_t` | 28 × 17,5 mm, PCB 1 mm | Format courant du TP4056 USB-C avec protection. Fixent le berceau et la hauteur de sa découpe USB. |
| `tp_led_x`, `tp_led_y` | (0 ; -6) mm depuis le centre du TP4056, +Y vers l'USB | Position de la LED de charge, variable selon les modules. |
| `insert_d` | 3,2 mm | Dépend de la marque des inserts. |
| `stem_d` | 5,5 mm | Standard MX. La paroi en bout de bras de croix ne fait que 0,7 mm. 5,7 donnerait 0,8 mm, mais risque de frotter dans le boîtier du switch en fin de course. |

## Vérifications faites

- Timeline : 182 éléments, aucune erreur. Toutes les esquisses sont totalement contraintes, sauf les légendes (un texte ne se contraint pas).
- Régénération : 2 × 4 → 3 × 3 → 2 × 4 sans erreur.
- Option batterie (quatre tailles) : timeline saine, esquisses contraintes, 0 interférence entre boîtier, plaque, SuperMini, TP4056, LiPo et switches. Les découpes USB sont centrées sur les deux prises.
- Jeu entre keycaps voisines : 1,05 mm partout (minimum demandé : 0,8).
- Interférences dans l'assemblage au repos : 0.
- Alignements mesurés : trous LED/BOOT centrés sur les repères de la carte, trous de vis sur les inserts, découpe USB-C centrée sur la prise (X 20,05 mm, Z 6,1 mm), keycaps centrées sur les switches.
- Empilement : plaque à 15 mm, bas de keycap au repos à 23 mm, en fin de course à 19 mm, sommet à 29,5 mm. Sous la plaque, les pattes des switches descendent à 6,7 mm et le fond est à 2 mm, ce qui laisse 4,7 mm pour les fils. Le haut de la prise USB est à 7,7 mm, le dessous de la plaque à 13,5 mm.
- `orient_and_check.py` : toutes les pièces imprimables sont fermées (manifold).
