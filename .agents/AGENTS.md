# Règles Globales du Projet

## 1. Source Documentaire Prioritaire
Pour toutes les opérations liées aux documents PDF de ce projet (lecture, analyse, extraction, ocr), tu dois **TOUJOURS et EXCLUSIVEMENT** utiliser les fichiers présents dans le dossier :
`Sources/sources_lisibles/`

**Interdiction stricte :** 
Il est formellement interdit de traiter les PDF originaux situés dans le dossier `Sources/` parent, car ils peuvent contenir des images non consultables. Le dossier `sources_lisibles` est certifié à 100% avec du texte OCR et doit être la seule vérité terrain.


## 2. Protocole Officiel des 6 Raccourcis (Langage Naturel & Slash Commands)

L'agent reconnaît et exécute automatiquement les workflows métier ci-dessous, qu'ils soient invoqués en langage naturel (Façon 1), en commande Slash (Façon 2) ou via le chef d'orchestre unifié `python scripts/pipeline_orchestrator.py` :

### 🚀 Raccourci 1 : « Mets à jour livre [X] à la partie/chapitre/section [Y] » ou `/maj-livre [X] [Y]`
- **Mode** : Tout automatique de A à Z sur le périmètre ciblé (`python scripts/pipeline_orchestrator.py --maj-livre --book [X]`).
- **Chaînage** :
  1. **Skill 1 (`magic-pdf-extractor`)** : Extraction des techniques et structuration taxonomique.
  2. **Skill 2 (`magic-desc-enhancer`)** : Rédaction des descriptions standard `[Effet] | [Méthode]`.
  3. **Skill 3 (`magic-link-builder`)** : Construction et validation physique des hyperliens PDF.
  4. **Skill 4 (`magic-db-sync`)** : Audit d'intégrité, génération du cache applicatif et rechargement de l'app web.
- **Retour** : Résumé des ajouts avec liens cliquables.

### 🔍 Raccourci 2 : « Recherche livre [X] partie [Y] des techniques » ou `/recherche [X] [Y]`
- **Mode** : Pas-à-pas interactif avec validation humaine obligatoire (`python scripts/pipeline_orchestrator.py --recherche --book [X] --query [Y]`).
- **Chaînage** :
  1. Exécuter **Skill 1 (`magic-pdf-extractor`)** pour identifier les techniques dans les PDF sources lisibles.
  2. **Pause obligatoire** : Présenter la liste des techniques candidates (Nom, Chapitre, Section, Page).
  3. **Attendre le retour de l'utilisateur** (validation « OK » ou ajustements).
  4. Exécuter **Skill 2 (`magic-desc-enhancer`)** et afficher les descriptions `[Effet] | [Méthode]`.
  5. **Attendre la validation de l'utilisateur**.
  6. Exécuter **Skill 3 (`magic-link-builder`)** pour créer les hyperliens cliquables et **Skill 4 (`magic-db-sync`)** pour synchroniser l'application web.

### ✍️ Raccourci 3 : « Mets à jour description technique du livre [X] partie [Y] » ou `/maj-description [X] [Y]`
- **Mode** : Amélioration rédactionnelle ciblée (`python scripts/pipeline_orchestrator.py --maj-desc --book [X]`).
- **Chaînage** :
  1. Exécuter **Skill 2 (`magic-desc-enhancer`)** sur le livre et la partie demandée.
  2. Exécuter **Skill 4 (`magic-db-sync`)** pour rafraîchir l'application web.
- **Retour** : Échantillon représentatif de descriptions enrichies (Avant / Après).

### 🔗 Raccourci 4 : « Mets à jour lien » ou `/maj-liens [livre]`
- **Mode** : Réparation et vérification des hyperliens physiques (`python scripts/pipeline_orchestrator.py --maj-liens [--book X | --all]`).
- **Chaînage** :
  1. Exécuter **Skill 3 (`magic-link-builder`)** sur le ou les livres cibles.
  2. Exécuter **Skill 4 (`magic-db-sync`)** pour actualiser l'application web.
- **Retour** : Bilan chiffré des liens résolus (100% sans liens morts).

### 🔄 Raccourci 5 : « Mise à jour application » ou `/maj-app`
- **Mode** : Synchronisation et rafraîchissement express de l'application web locale et distante (`python scripts/pipeline_orchestrator.py --maj-app`).
- **Chaînage** :
  1. Exécuter **Skill 4 (`magic-db-sync`)** pour consolider le cache de données.
  2. Exécuter **Skill 5 (`magic-app-guardian`)** pour contrôler l'intégrité de l'interface et déployer sur Netlify.
- **Retour** : Nombre total de techniques consolidées (chiffre dynamique depuis le cache) et statut du site en direct sur `https://encyclopedie-magique.netlify.app`.

### 🚀 Raccourci 6 : « Déploie l'application » ou `/deploy`
- **Mode** : Déploiement et audit qualité 1-clic sur Netlify (`python scripts/pipeline_orchestrator.py --deploy`).
- **Chaînage** :
  1. Exécuter `python .agents/skills/magic-app-guardian/scripts/verify_app.py` (Zéro erreur DOM, concordance des boutons).
  2. Exécuter `node scripts/prepare_netlify.js` (Compilation du dossier `dist/`).
  3. Exécuter `npx netlify deploy --dir dist --no-build --site encyclopedie-magique --prod`.
  4. Tester la réponse en ligne du site.
- **Retour** : Rapport qualité 100% vert et lien de production Netlify direct.


## 3. Règle Fondamentale d'Inviolabilité des Données (Zéro Écrasement)

La préservation intégrale des données existantes est un impératif absolu et non négociable pour tous les skills :

1. **Skill 1 (`magic-pdf-extractor`) : Mode AJOUT PUR (`max_row + 1`)**
   - Déduplication stricte par nom et référence source.
   - Si une technique existe déjà, elle est obligatoirement ignorée.
   - Les nouvelles entrées sont écrites uniquement tout en bas du tableau.
   - **Interdiction formelle** d'écraser, de remplacer ou de supprimer une ligne déjà présente.

2. **Skill 2 (`magic-desc-enhancer`) : Périmètre Colonne 5 (`Nom`) et Colonne 6 (`Description`)**
   - Agit sur la **Colonne 5** pour clarifier et normaliser les titres incompréhensibles ou bruités. Si un titre est déjà propre et clair, il est sanctuarisé.
   - Agit sur la **Colonne 6** pour rédiger les descriptions au format `[Effet] ... | [Méthode] ...`. Si une description est déjà conforme, elle est sanctuarisée.
   - **Interdiction formelle** de modifier les colonnes 1, 2, 3, 4, 7 et 8.

3. **Skill 3 (`magic-link-builder`) : Périmètre exclusif Colonne 8**
   - Agit **exclusivement** sur la Colonne 8 (`Lien vers la page du pdf`).
   - Lit la colonne 7 pour localiser le PDF et injecter l'hyperlien cliquable.
   - **Interdiction formelle** de modifier ou d'altérer les colonnes 1 à 7.

4. **Skill 4 (`magic-db-sync`) : LECTURE SEULE STRICTE**
   - Ouvre les classeurs Excel en lecture seule (`data_only=False`) pour construire le cache JSON.
   - **Interdiction formelle** d'appeler `wb.save()` ou de modifier les classeurs Excel.


## 4. Règle Stricte d'Attribution des Sections (Zéro 'Général' indu)

La valeur `Général` en Colonne 4 est **STRICTEMENT RÉSERVÉE** aux seuls chapitres qui ne possèdent aucune sous-section dans la taxonomie Word de référence (`taxonomies_reference.json`) :
- **Si un chapitre possède des sous-sections définies** (ex: *Chapitre 2 : Les Contrôles* ou *Chapitre 1 : Tours Automatiques*), l'entrée **DOIT OBLIGATOIREMENT** être affectée à l'une de ces sous-sections spécifiques selon son principe magique.
- **Interdiction formelle** de laisser ou d'écrire `Général` pour une technique dès lors que son chapitre comporte des sections dédiées.


## 5. Règles Inviolables de l'Application Web (« Livre nini magie »)

Pour toute modification du frontend (`index.html`, `style.css`, `app.js`) ou du déploiement :
1. **Nom Officiel Unique** : Strictement `Livre nini magie` dans `<title>`, l'en-tête et le manifest.
2. **4 Onglets Officiels** : `Bibliothèque`, `Sommaire`, `Classement` (réordonnancement, ajouts & export Excel), `PDF à télécharger`.
3. **Charte Épurée 4 Couleurs** : Blanc (`#ffffff`), Noir (`#111827`), Bleu (`#2563EB`), Rouge (`#DC2626`). Typographie unique `Inter`.
4. **Sommaires Intégraux Inaltérables** : Les 20 chapitres Cartes, 24 chapitres Pièces, 5 chapitres Tours de Cartes, 12 chapitres Tours de Pièces doivent **toujours être affichés à 100%**. Les chapitres à 0 technique affichent `Aucune technique répertoriée dans ce chapitre.`
5. **Règle Anti-Gel (Chunking 50)** : Chargement obligatoire par lots de 50 items avec bouton `Afficher 50 de plus` pour garantir une fluidité absolue sur mobile et PC (jamais 10 000 éléments injectés d'un coup).
6. **Ouverture du Lecteur PDF Exclusivement au Clic** : Présence obligatoire du bouton `📖 Ouvrir le PDF à la page [XX]`. Le lecteur PDF ne doit **JAMAIS** s'ouvrir automatiquement en arrière-plan ; il s'ouvre **exclusivement** lorsque l'utilisateur clique sur ce bouton.
7. **Module Classement Interactif & Sauvegarde** : Rendu fidèle Partie > Chapitre > Section avec 1ʳᵉ Partie et 1ᵉʳ Chapitre ouverts par défaut, itération stricte du dictionnaire des sections via `Object.entries` / `Object.keys`, réordonnancement (▲/▼/#/drag-drop), ajout de techniques (`✨ Personnalisée`), sauvegarde locale automatique et export Excel (.xlsx) autonome.
8. **Validation Automatique Avant Clôture** : Toujours exécuter `python .agents/skills/magic-app-guardian/scripts/verify_app.py` avant de valider (syntaxe, concordance des IDs DOM, présence de SheetJS local, et simulation d'exécution du Classement et des exports Excel sur les 4 livres).


## 6. Règle Stricte d'Unicité des Fichiers (Zéro Fichier .bak, Zéro Nouveau Fichier)

1. **Conservation exclusive des 4 fichiers Excel officiels** :
   - `Livre Techniques Cartes.xlsx`
   - `Livre Techniques Pièces.xlsx`
   - `Livre Tours de Cartes.xlsx`
   - `Livre Tours de Pièces.xlsx`
2. **Interdiction formelle de créer des fichiers `.bak`, doublons ou nouveaux fichiers Excel** :
   - Aucun script ne doit générer de copie de sauvegarde `.bak`, de version temporaire résiduelle ou de fichier dérivé (ex: `*_v2.xlsx`, `*_backup.xlsx`).
   - Toutes les modifications de la pipeline (Skill 1, 2, 3) s'effectuent **strictement et exclusivement en place** sur les 4 fichiers de référence (`wb.save(excel_path)`).


