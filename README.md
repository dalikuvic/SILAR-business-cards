# SILAR — business cards (recto)

Ce dépôt contient maintenant **deux PDF imprimables livrés** (un par carte), générés depuis les SVG éditables.

## Fichiers fournis

- `SILAR_Mohamed_Ali_recto.svg` (source éditable, fond transparent)
- `SILAR_Abdellatif_recto.svg` (source éditable, fond transparent)
- `SILAR_Mohamed_Ali_recto.pdf` (1 page)
- `SILAR_Abdellatif_recto.pdf` (1 page)
- `scripts/generate_print_pdfs.py` (génération + vérification)

## Données carte

- **CHEOUR MOHAMED ALI**
  - Manager
  - +216 50 71 68 74
  - cheour.mohamedali@gmail.com
- **SAANOUN ABDELLATIF**
  - Manager
  - +216 23 23 28 17
  - saanoun_abdel@hotmail.com
- Ligne société: **TUNISIA - IMPORT - EXPORT**

## Spécifications de mise en page (vérifiées)

- Format fini (TrimBox): **85 × 55 mm**
- Fond perdu demandé: **3 mm**
- Taille page PDF (MediaBox/BleedBox): **91 × 61 mm**
- Recto uniquement, **1 page par PDF**, sans verso
- Pas de fond opaque pleine page (arrière-plan supprimé dans les SVG)
- Transparence PDF présente (pixels alpha 0 et 255 détectés)

## Génération reproductible

Prérequis:
- Inkscape (CLI)
- Python 3
- `pypdf`
- `pymupdf`

Commande:

```bash
python3 scripts/generate_print_pdfs.py
```

Cette commande:
1. exporte les SVG vers PDF via Inkscape (`--export-text-to-path`)
2. impose les boîtes PDF (MediaBox/TrimBox/BleedBox/ArtBox)
3. vérifie page unique, dimensions et présence de transparence

Vérification seule:

```bash
python3 scripts/generate_print_pdfs.py --verify-only
```

## Transparence et fond perdu

Le fond de page n’est pas rempli en opaque (transparent hors artwork).  
Avec un fond transparent, le fond perdu n’existe que là où des éléments graphiques touchent les bords; les rubans/éléments de bord ont été conservés jusqu’aux bords de page.

## Clarifications (correction des affirmations précédentes)

- Les fichiers n’étaient pas initialement fournis en PDF final dans ce dépôt: ils le sont maintenant.
- Aucun claim de certification PDF/X n’est fait ici.
- Aucun claim de conversion CMYK n’est fait ici (export PDF standard).
- Aucun claim de reproduction photo exacte n’est fait: le visuel est une illustration vectorielle existante dans les SVG du dépôt.
