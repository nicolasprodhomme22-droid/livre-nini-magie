---
name: magic-desc-enhancer
description: Agent d'enrichissement sémantique et de clarification des techniques magiques : standardisation des titres incompréhensibles (Colonne 5) et rédaction des descriptions au format [Effet] + [Méthode] (Colonne 6).
---

# ✍️ Skill Agent 2 : magic-desc-enhancer

## Rôle & Mission
Le rôle de cet agent est d'élever la clarté et la qualité pédagogique de deux colonnes clés dans les 3 classeurs Excel :
1. **Colonne 5 : Nom technique / tour** : Clarifier, normaliser et rendre immédiatement compréhensibles les titres obscurs, tronqués, ou pollués par le bruit OCR (phrases brutes en anglais, résidus de découpage).
2. **Colonne 6 : Description (Quoi et Comment)** : Rédiger ou enrichir chaque description au standard strict :
   `[Effet] ... | [Méthode] ...`

---

## 🎯 Périmètre d'Action Autorisé
- **Colonne 5 (`Nom technique / tour`)** :
  - **Élimination du bruit OCR** : Supprimer les artéfacts, les prépositions orphelines, les phrases tronquées (ex: `111e`, `Grip the entire pack`, `To Finger Palm`, `Form a break under the injog`).
  - **Clarification sémantique** : Reformuler en un titre magique net, explicite et élégant (titre français clair avec nom technique usuel ou bilingue entre parenthèses si pertinent, ex: *Contrôle à l'Injog (Pinky Break)*, *Empalmage des doigts (Finger Palm)*, *Saut de coupe classique (Classic Pass)*).
  - **Sanctuarisation** : Si un titre est déjà clair, propre et canonique, il est **conservé intact**.
- **Colonne 6 (`Description`)** :
  - Structure bipartite obligatoire :
    - `[Effet]` : L'illusion perçue par le spectateur (ce qui est visible et mystérieux).
    - `[Méthode]` : La manipulation technique secrète ou le principe mécanique utilisé (ce qui est caché).
  - Si une description possède déjà le format `[Effet] ... | [Méthode] ...` avec une longueur suffisante (≥ 30 caractères), elle est **sanctuarisée et conservée intacte**.
- **Colonnes Sanctuarisées (Interdiction Formelle de Modifier)** :
  - Les colonnes 1 (`Clé`), 2 (`Partie`), 3 (`Chapitre`), 4 (`Section`), 7 (`Référence PDF`) et 8 (`Lien PDF`) sont **strictement inviolables**.

---

## 📐 Règles de Traitement des Titres (Colonne 5)
1. **Intelligibilité Immédiate** : L'utilisateur doit comprendre en 1 seconde de quelle manipulation ou de quel tour il s'agit.
2. **Harmonisation Typographique** : Utiliser la casse titre standardisée (Majuscule initiale aux mots significatifs).
3. **Zéro Bruit Résiduel** : Éliminer les symboles typographiques résiduels (`«`, `»`, `...`, `---`, numéros de page ou d'exercice orphelins).
4. **Sécurité Excel** : Tout titre commence par une lettre ou un mot clair, jamais par un symbole interprétable comme une formule (`=`, `+`, `-`, `@`).

---

## 🛠️ Outils & Scripts du Skill
- `scripts/desc_enhancer.py` : Moteur de clarification des titres (Colonne 5) et de génération des descriptions Effet/Méthode (Colonne 6).
- `scripts/run_enhancement.py` : Script d'exécution par livre (`--book cartes|pieces|tours`), par lot (`--limit`), en simulation (`--dry-run`) ou global (`--all`).
