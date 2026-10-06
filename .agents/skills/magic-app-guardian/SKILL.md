---
name: magic-app-guardian
description: Agent gardien de l'application web Livre nini magie, garant du design épuré, des 4 onglets officiels (Bibliothèque, Sommaire, Classement, PDF à télécharger), de l'intégrité des sommaires complets (20 chap Cartes, 24 chap Pièces, 5 chap Tours), du lecteur PDF exclusif au clic, et du déploiement Netlify certifié zéro régression.
---

# 🛡️ Skill Agent 5 : magic-app-guardian

## Rôle & Mission
Le rôle de cet agent est de garantir l'excellence, la pérennité et la fluidité absolue de l'application de consultation web **« Livre nini magie »**.
Il est le garant du respect absolu des volontés de l'utilisateur, empêche toute régression visuelle ou technique (boutons non connectés, gel d'écran sur mobile, omission de chapitres) et orchestre le déploiement sécurisé en production sur Netlify.

---

## 📌 Les 6 Invariants Sacrés (Intouchables)

Toute modification de l'application (frontend, design ou logique) doit **rigoureusement et obligatoirement** respecter les 6 principes suivants :

### 1. Nom Officiel Invariable
- L'application s'appelle **strictement et exclusivement** : `Livre nini magie`.
- Présent dans la balise `<title>`, l'en-tête principal (`.app-title`), et le manifeste PWA.

### 2. Les 4 Onglets Officiels de Navigation
La barre supérieure comporte les 4 onglets :
1. **Bibliothèque** : Accueil épuré avec les 3 grands boutons (Cartes, Pièces, Tours).
2. **Sommaire** : Arborescence dépliable interactive et consultation des fiches techniques.
3. **Classement** : Organisation de son propre ordre de techniques par section, drag & drop, boutons de rang (▲/▼/#), ajouts personnalisés de techniques, sauvegarde automatique locale et export direct vers Excel (.xlsx).
4. **PDF à télécharger** : Liste des 19 traités certifiés avec téléchargement direct et lecture immédiate.

### 3. Charte Visuelle Épurée & Minimaliste
- **Design sobre et fonctionnel** : Pas d'informations partout, seulement l'essentiel.
- **Palette stricte de 4 couleurs exclusives** :
  - **Blanc** (`#ffffff`) : Fond des cartes et lisibilité maximale.
  - **Noir** (`#111827`, `#000000`) : Typographie principale et contrastes forts.
  - **Bleu** (`#2563EB`) : Boutons d'action prioritaires, sélections actives, badges d'effet.
  - **Rouge** (`#DC2626`) : Badges de méthode secrète, bouton de fermeture, alertes.
- **Typographie unique** : Police classique, nette et lisible sur tout support (**Inter** / sans-serif).

### 4. Sommaires Complets Inaltérables (100% Taxonomie Word)
- Tous les chapitres de la taxonomie Word de référence (`taxonomies_reference.json`) doivent **toujours être affichés en intégralité** et dans l'ordre chronologique strict (1 à N) :
  - **Cartes** : 3 parties, 20 chapitres (1 à 20).
  - **Pièces** : 3 parties, 24 chapitres (1 à 24).
  - **Tours de Cartes** : 2 parties, 5 chapitres et 21 sous-sections.
- **Règle des chapitres à 0 technique** : Si un chapitre ou une sous-section ne contient aucune technique dans la base actuelle, il **DOIT OBLIGATOIREMENT** apparaître dans l'arborescence avec la mention claire : `Aucune technique répertoriée dans ce chapitre.` Il est formellement interdit de le masquer.

### 5. Fluidité Anti-Gel : Chargement Progressif (Chunking 50)
- Le chapitre 1 des Pièces (*Cacher*) compte à lui seul **10 045 fiches**.
- Il est **formellement interdit d'injecter 10 000 éléments DOM d'un coup**, ce qui fige instantanément l'écran d'un smartphone ou d'un ordinateur.
- Tout affichage de techniques doit s'effectuer **par lots de 50 items**, avec un bouton clair `Afficher 50 de plus` et `Tout afficher`.

### 6. Ouverture du Lecteur PDF Exclusivement au Clic
Chaque fiche technique comporte :
1. Un bouton proéminent en tête de fiche :
   ```text
   📖 Ouvrir le PDF à la page [XX]
   ```
2. **Ouverture manuelle sur demande** : C'est **exclusivement** lorsque l'utilisateur clique sur ce bouton que le lecteur PDF s'ouvre directement à la page cible (`#page=XX`).
3. **Interdiction de chargement automatique** : La fiche technique ne doit **jamais** charger ni ouvrir le PDF en arrière-plan d'elle-même sans action explicite de l'utilisateur.
4. Un lien natif `↗ Ouvrir dans un nouvel onglet` pointant vers `#page=XX`.

### 7. Le Module Classement & Sommaire Interactif
L'onglet **Classement** permet à l'utilisateur d'organiser ses techniques dans un ordre personnalisé, d'en ajouter et d'exporter sur Excel :
1. **Les 3 Boutons de Sélection** : `Cartes`, `Pièces`, `Tours` permettent d'ouvrir immédiatement le sommaire du livre choisi.
2. **Rendu Intégral du Sommaire (Partie > Chapitre > Section)** :
   - Structure arborescente complète identique au sommaire officiel Word.
   - **Ouverture par défaut** : La 1ʳᵉ Partie et le 1ᵉʳ Chapitre sont ouverts par défaut dès l'arrivée sur l'onglet pour une visibilité immédiate des techniques et de leurs rangs.
   - **Règle stricte d'itération du cache JSON** : Les sections étant stockées dans `data_cache.json` sous forme de dictionnaires d'objets (`{ [section]: count }`), elles doivent **impérativement** être itérées via `Object.entries(sections)` ou `Object.keys(sections)`, et JAMAIS par `for...of` direct (pour éviter l'erreur `secList is not iterable`).
3. **Fluidité Anti-Gel (Lots de 50)** : Affichage initial des 50 premières techniques avec contrôles `Afficher 50 de plus` et `Tout afficher`.
4. **Outils de Réordonnancement** : Badges de rangs `#1`, `#2`..., flèches `▲` et `▼`, saisie rapide de rang `#`, glisser-déposer `⠿`, et retrait `🗑️`.
5. **Ajout de Techniques Personnalisées** : Formulaire modal avec menus déroulants en cascade (Livre > Partie > Chapitre > Section) et badge distinctif `✨ Personnalisée`.
6. **Sauvegarde Automatique Immédiate** : Enregistrement instantané dans `localStorage` à chaque modification et bouton de réinitialisation.
7. **Export Excel (.xlsx) Autonome** : Génération directe via SheetJS local (`vendor/xlsx.full.min.js`), avec export du livre actif ou des 3 livres en 3 onglets.

---

## 🛠️ Protocole de Validation & Déploiement en 4 Étapes

Avant de clore une intervention ou d'annoncer à l'utilisateur que l'application est prête, l'agent doit **obligatoirement** exécuter les étapes suivantes :

### Étape 1 : Contrôle Qualité Automatique (Zéro Erreur DOM & Simulation Classement)
Exécuter le script de validation qui vérifie que 100% des identifiants DOM appelés dans `app.js` existent dans `index.html`, qu'aucune erreur de syntaxe n'est présente, que la bibliothèque locale SheetJS est prête, et simule l'arborescence du Classement et l'export Excel sur les 3 livres :
```powershell
python .agents/skills/magic-app-guardian/scripts/verify_app.py
```

### Étape 2 : Synchronisation de la Base de Données
Si les classeurs Excel ou les taxonomies ont évolué :
```powershell
python .agents/skills/magic-db-sync/scripts/sync_engine.py
```

### Étape 3 : Compilation et Déploiement Netlify
Exécuter le script de packaging et de déploiement en production :
```powershell
python .agents/skills/magic-app-guardian/scripts/deploy_netlify.py
```

### Étape 4 : Test de Validation en Ligne
Vérifier que le site de production répond avec le statut HTTP 200 à :
- **URL Publique** : `https://encyclopedie-magique.netlify.app`
- **Contrôle du cache** : Le total des fiches techniques est conforme au cache généré.

---

## 🧰 Scripts & Outils du Skill
- `scripts/verify_app.py` : Contrôleur d'intégrité HTML / JS / JSON (zéro bouton orphelin, zéro crash).
- `scripts/deploy_netlify.py` : Pilote automatique de publication Netlify avec vérification HTTP en direct.
