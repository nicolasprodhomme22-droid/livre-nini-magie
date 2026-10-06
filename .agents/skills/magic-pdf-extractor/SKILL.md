---
name: magic-pdf-extractor
description: Agent autonome d'analyse des PDF de magie, d'extraction des techniques/tours à la page exacte, de nettoyage du bruit OCR, et d'enrichissement du classeur Excel selon le sommaire Word de référence.
---

# 🪄 Skill Agent 1 : magic-pdf-extractor

## Rôle & Mission
Le rôle de cet agent est d'analyser systématiquement les documents PDF sources certifiés OCR pour en extraire chaque technique ou tour, identifier la page exacte, et classer chaque entrée dans la taxonomie officielle du sommaire Word de référence (`taxonomies_reference.json`).

Dans le pipeline modulaire, cet agent est le **bâtisseur structurel** :
- Il remplit en priorité :
  - **Colonne 1** : `Clé d'identification` (`TECH_CARTE_XXX`, `TECH_PIECE_XXX`, `TOUR_CARTE_XXX`)
  - **Colonne 2** : `Partie`
  - **Colonne 3** : `Chapitre`
  - **Colonne 4** : `Section` (toujours renseignée, `Général` par défaut)
  - **Colonne 5** : `Nom technique / tour` (nettoyé de tout bruit OCR)
  - **Colonne 7** : `PDF concerné avec numéro de page` (référence documentaire)
- Il pré-remplit la **Colonne 6** avec le texte source brut nettoyé avant passage de l'Agent 2 (`magic-desc-enhancer`).
- Il prépare la référence pour l'Agent 3 (`magic-link-builder`) qui construira le lien physique certifié.

## Règles Métier Invariants
0. **Source Prioritaire Obligatoire** :
   - Tous les documents PDF doivent **exclusivement** être lus et analysés depuis le sous-dossier `Sources/sources_lisibles`. Ce dossier garantit que 100% des fichiers possèdent une couche de texte extractible. Interdiction formelle d'utiliser les PDF du dossier parent `Sources/`.

1. **8 Colonnes Strictes** :
   - Structure Excel immuable.
   - Les cellules textuelles sont systématiquement assainies (`sanitize_text()`) pour empêcher toute interprétation erronée comme formule Excel (`=`, `+`, `-`, `@`).

2. **Classification par Définitions & Mots-Clés Canoniques** :
   - Analyse comparative du titre et du contexte textuel avec les mots-clés bilingues (FR/EN) et les définitions de `taxonomies_reference.json`.
   - Assignation sémantique fidèle au sommaire Word de référence.

3. **Déduplication Stricte** :
   - Vérification de non-existence avant tout ajout (par nom normalisé et couple nom + référence).

4. **Inviolabilité des Données Existantes (Zéro Écrasement)** :
   - Mode **AJOUT PUR** exclusif (`sheet.max_row + 1`).
   - Interdiction formelle et absolue de modifier, réécrire ou supprimer une ligne existante dans les classeurs Excel.

5. **Règle Stricte d'Attribution des Sections (Zéro 'Général' indu)** :
   - La mention `Général` en Colonne 4 est **STRICTEMENT RÉSERVÉE** aux seuls chapitres qui n'ont aucune sous-section dans le sommaire Word (`taxonomies_reference.json`).
   - Dès lors qu'un chapitre possède des sous-sections définies, la technique **DOIT OBLIGATOIREMENT** être classée dans l'une de ces sous-sections officielles selon son principe magique.

## Outils & Scripts du Skill
- `scripts/ocr_cleaner.py` : Nettoyeur de texte OCR et réparateur de césures.
- `scripts/pdf_extractor.py` : Moteur d'extraction PyMuPDF (TOC native et analyse typographique par police/taille/graisse).
- `scripts/classifier.py` : Moteur de classification sémantique bilingue avec thésaurus expert.
- `scripts/excel_manager.py` : Gestionnaire Excel respectant rigoureusement les 8 colonnes, l'assainissement anti-formule et l'unicité des clés.
- `scripts/run_extraction.py` : Script CLI pour exécuter l'extraction en mode batch ou ciblé (`--book`, `--all`, `--dry-run`, `--search`).

