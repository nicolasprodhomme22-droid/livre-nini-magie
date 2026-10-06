"""
shared/config.py — Module de configuration centralisé pour la pipeline « Livre nini magie ».

Centralise :
- BASE_DIR : Chemin racine du projet
- BOOKS_CONFIG : Dictionnaire unique des 3 livres (chemins Excel, dossiers PDF, préfixes ID)
- normalize_book_key() : Normalisation unique des clés de livre
- find_data_sheet() : Sélection robuste de la feuille de données dans un classeur Excel
- ensure_utf8() : Reconfiguration UTF-8 de stdout (appelé 1 seule fois)
- backup_excel() : Règle stricte zéro fichier tiers (modifications 100% en place)
- load_taxonomies() : Chargement et cache du fichier taxonomies_reference.json
"""

import os
import sys
import json
import shutil
from functools import lru_cache

# ─── Chemin racine du projet ───
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# ─── Chemins structurels ───
SOURCES_LISIBLES_DIR = os.path.join(BASE_DIR, 'Sources', 'sources_lisibles')
APP_DATA_DIR = os.path.join(BASE_DIR, 'app', 'data')
TAXONOMY_PATH = os.path.join(BASE_DIR, 'taxonomies_reference.json')
SKILLS_DIR = os.path.join(BASE_DIR, '.agents', 'skills')

# ─── Configuration unifiée des 3 livres ───
BOOKS_CONFIG = {
    'cartes': {
        'id': 'cartes',
        'title': 'Techniques de Cartes',
        'icon': '🃏',
        'excel': os.path.join(BASE_DIR, 'Livre Techniques Cartes.xlsx'),
        'prefix': 'TECH_CARTE',
        'folder': os.path.join(SOURCES_LISIBLES_DIR, 'sources techniques Cartes'),
        'rel_folder': 'Sources/sources_lisibles/sources techniques Cartes'
    },
    'pieces': {
        'id': 'pieces',
        'title': 'Techniques de Pièces',
        'icon': '🪙',
        'excel': os.path.join(BASE_DIR, 'Livre Techniques Pièces.xlsx'),
        'prefix': 'TECH_PIECE',
        'folder': os.path.join(SOURCES_LISIBLES_DIR, 'sources techniques Pièces'),
        'rel_folder': 'Sources/sources_lisibles/sources techniques Pièces'
    },
    'tours': {
        'id': 'tours',
        'title': 'Tours de Cartes',
        'icon': '🎩',
        'excel': os.path.join(BASE_DIR, 'Livre Tours de Cartes.xlsx'),
        'prefix': 'TOUR_CARTE',
        'folder': os.path.join(SOURCES_LISIBLES_DIR, 'sources tours de Cartes'),
        'rel_folder': 'Sources/sources_lisibles/sources tours de Cartes'
    },
    'tours_pieces': {
        'id': 'tours_pieces',
        'title': 'Tours de Pièces',
        'icon': '🪙',
        'excel': os.path.join(BASE_DIR, 'Livre Tours de Pièces.xlsx'),
        'prefix': 'TOUR_PIECE',
        'folder': os.path.join(SOURCES_LISIBLES_DIR, 'sources tours de pièces'),
        'rel_folder': 'Sources/sources_lisibles/sources tours de pièces'
    }
}

# Alias de compatibilité
BOOKS_CONFIG_ALIASES = {
    'cartes_techniques': 'cartes',
    'pieces_techniques': 'pieces',
    'cartes_tours': 'tours',
    'pieces_tours': 'tours_pieces',
    'tour_piece': 'tours_pieces',
    'tours_piece': 'tours_pieces',
    'livre_tours_pieces': 'tours_pieces',
}


def ensure_utf8():
    """Configure stdout en UTF-8 si nécessaire. Appeler une seule fois au démarrage."""
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass


def normalize_book_key(key: str) -> str:
    """
    Normalise toute variante de clé de livre vers une clé canonique ('cartes', 'pieces', 'tours', 'tours_pieces').
    
    Accepte : 'cartes', 'pieces', 'tours', 'tours_pieces', 'pieces_tours', etc.
    
    Lève ValueError si la clé est invalide ou vide.
    """
    if not key or not str(key).strip():
        raise ValueError("Clé de livre vide ou absente. Clés valides : 'cartes', 'pieces', 'tours', 'tours_pieces'.")

    k = str(key).strip().lower()

    # 1. Vérification directe dans la config principale
    if k in BOOKS_CONFIG:
        return k

    # 2. Vérification dans les alias
    if k in BOOKS_CONFIG_ALIASES:
        return BOOKS_CONFIG_ALIASES[k]

    # 3. Correspondance sémantique tolérante
    if ('tour' in k or 'routine' in k) and ('pièce' in k or 'piece' in k):
        return 'tours_pieces'
    if 'tour' in k:
        return 'tours'
    if 'pièce' in k or 'piece' in k:
        return 'pieces'
    if 'carte' in k:
        return 'cartes'

    raise ValueError(f"Clé de livre inconnue : '{key}'. Clés valides : 'cartes', 'pieces', 'tours', 'tours_pieces'.")


def get_book_config(key: str) -> dict:
    """Retourne la configuration complète d'un livre par sa clé normalisée."""
    return BOOKS_CONFIG[normalize_book_key(key)]


def find_data_sheet(wb):
    """
    Sélection robuste de la feuille de données dans un classeur Excel.
    
    Recherche dans l'ordre :
    1. Feuille contenant 'tableau' ou 'donn' dans son nom
    2. La 2ème feuille (index 1) si elle existe
    3. La feuille active
    
    Retourne la feuille trouvée.
    Lève ValueError si le classeur est vide.
    """
    if not wb.sheetnames:
        raise ValueError("Le classeur Excel est vide (aucune feuille).")

    # 1. Recherche par nom conventionnel
    for name in wb.sheetnames:
        if 'tableau' in name.lower() or 'donn' in name.lower():
            return wb[name]

    # 2. Fallback sur la 2ème feuille (la 1ère est souvent un sommaire)
    if len(wb.sheetnames) > 1:
        return wb[wb.sheetnames[1]]

    # 3. Dernier recours : feuille active
    return wb.active


def backup_excel(excel_path: str) -> str:
    """
    Règle absolue du projet : AUCUN fichier .bak ni nouveau fichier créé.
    Toutes les modifications sont appliquées strictement en place sur le fichier d'origine.
    
    Retourne directement le chemin du fichier Excel de référence.
    """
    return excel_path


@lru_cache(maxsize=1)
def load_taxonomies() -> dict:
    """
    Charge et met en cache le fichier taxonomies_reference.json.
    Grâce au @lru_cache, le fichier n'est lu qu'une seule fois par exécution,
    même si plusieurs skills l'appellent.
    """
    if not os.path.exists(TAXONOMY_PATH):
        return {}
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
