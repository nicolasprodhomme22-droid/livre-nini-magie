---
name: magic-db-sync
description: Agent de contrôle d'intégrité, de validation et de synchronisation des 3 fichiers Excel vers la base de données et le cache de l'application de consultation.
---

# 🔄 Skill Agent 4 : magic-db-sync

## Rôle & Mission
Le rôle de cet agent est d'assurer la passerelle sécurisée et performante entre les classeurs Excel (`Livre Techniques Cartes.xlsx`, `Livre Techniques Pièces.xlsx`, `Livre Tours de Cartes.xlsx`) et l'application unique de consultation web.
Il valide la conformité stricte aux 8 colonnes, vérifie l'absence de doublons de clés primaires, s'assure de l'existence des hyperliens PDF et compile le cache haute performance (`data_cache.json`) pour l'interface utilisateur.

## Place dans le Pipeline
- **Entrée** : Les 3 classeurs Excel enrichis par l'Agent 1, l'Agent 2 et l'Agent 3.
- **Action** : Audit complet des 8 colonnes, vérification des règles de gestion, génération du cache JSON atomique (`data_cache.json`).
- **Sortie** : Notification passive `POST /api/reload` envoyée au serveur web local (`http://localhost:3000`) pour rafraîchissement immédiat des données sans redémarrage.

## Règles Métier Invariants
1. **Validation d'Intégrité** :
   - Vérifier l'unicité stricte des clés primaires (`TECH_CARTE_XXX`, `TECH_PIECE_XXX`, `TOUR_CARTE_XXX`).
   - S'assurer qu'aucune cellule `Section` n'est nulle, et que la mention `Général` est strictement confinée aux seuls chapitres qui ne possèdent aucune sous-section dans le sommaire Word de référence.
   - Vérifier que chaque lien PDF pointe vers un fichier réellement existant sur le disque.
2. **Synchronisation à Chaud Sans Boucle** :
   - Génération de `data_cache.json` structuré par univers pour permettre un temps de réponse instantané dans l'application.
   - Envoi d'un signal HTTP passif `POST /api/reload` évitant toute boucle de récursion.
3. **Inviolabilité des Données Existantes (Zéro Écrasement)** :
   - Mode **LECTURE SEULE STRICTE** sur les classeurs Excel.
   - Interdiction formelle d'appeler `wb.save()` ou de modifier les classeurs Excel. L'intégrité des fichiers sources est garantie à 100%.

## Outils & Scripts du Skill
- `scripts/sync_engine.py` : Moteur d'audit, validation et extraction des 3 fichiers Excel vers le cache JSON de l'application et notification du serveur.
- `scripts/deduplicate_techniques.py` : Outil de consolidation et déduplication des lignes Excel. Fusionne les doublons en conservant la meilleure description et en consolidant les références multi-PDF. Intégré dans le pipeline via le flag `--deduplicate` du Raccourci 1.

