---
name: magic-link-builder
description: Agent de vérification, de résolution physique et de génération des hyperliens PDF dans les classeurs Excel.
---

# 🔗 Skill Agent 3 : magic-link-builder

## Rôle & Mission
Le rôle de cet agent est de garantir à 100% l'intégrité et la validité de la **Colonne 8 (Lien vers la page du PDF)** pour chaque technique des 3 classeurs Excel.
Il inspecte la référence documentaire (Colonne 7), résout le chemin physique exact du fichier dans `Sources/sources_lisibles/`, injecte l'ancre de page `#page=XX` et crée l'hyperlien Excel cliquable.

## Place dans le Pipeline
- **Entrée** : Références de la Colonne 7 (`PDF concerné avec numéro de page`) produites par l'Agent 1 (`magic-pdf-extractor`).
- **Action** : Scan de l'index physique de `Sources/sources_lisibles/`, extraction robuste du numéro de page, et résolution d'ancre `#page=XX`.
- **Sortie** : Colonne 8 enrichie avec libellé `Ouvrir page XX` et hyperlien direct cliquable, sans toucher aux autres colonnes.

## Règles Métier Invariants
1. **Source Unique et Conforme** :
   - Seuls les fichiers du dossier `Sources/sources_lisibles/` sont autorisés, conformément aux règles d'[AGENTS.md](file:///c:/Users/nipro/OneDrive/Bureau/antigravity/appli%20magie%20vf/.agents/AGENTS.md).
2. **Format Standardisé de la Colonne 8** :
   - Libellé de cellule : `Ouvrir page {numero_page}`
   - Hyperlien cible : `Sources/sources_lisibles/{dossier_livre}/{nom_fichier}.pdf#page={numero_page}`
   - Encodage sécurisé : gestion sans faille des espaces et parenthèses dans les noms de fichiers.
3. **Zéro Liens Morts** :
   - Si un PDF n'est pas indexé, la cellule est marquée explicitement `PDF non indexé`.
4. **Inviolabilité des Données Existantes (Zéro Écrasement)** :
   - Action strictement limitée à la **Colonne 8** (`Lien vers la page du pdf`).
   - Les colonnes 1 à 7 (Identifiants, Partie, Chapitre, Section, Nom, Description, Référence) sont strictement sanctuarisées et ne sont jamais modifiées.

## Outils & Scripts du Skill
- `scripts/link_builder.py` : Moteur de scan, résolution physique et mise à jour des hyperliens de la colonne 8 dans les 3 classeurs Excel (`--book`, `--all`, `--dry-run`).

