"""
shared/regression_guard.py — Garde anti-régression pour la pipeline « Livre nini magie ».

Garantit que :
1. Le nombre de techniques ne diminue JAMAIS après un sync (zéro perte)
2. Un snapshot est pris AVANT chaque opération critique
3. Un log d'exécution immutable est écrit après chaque pipeline
4. Le déploiement est BLOQUÉ si une régression est détectée
"""

import os
import sys
import json
import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.config import APP_DATA_DIR, BASE_DIR

CACHE_FILE = os.path.join(APP_DATA_DIR, 'data_cache.json')
SNAPSHOT_FILE = os.path.join(APP_DATA_DIR, 'last_snapshot.json')
PIPELINE_LOG_FILE = os.path.join(APP_DATA_DIR, 'pipeline_log.jsonl')


def take_snapshot() -> dict:
    """
    Prend un snapshot de l'état actuel du cache (nombre de techniques par livre).
    Sauvegarde le snapshot dans last_snapshot.json.
    Retourne le snapshot.
    """
    snapshot = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'books': {},
        'total': 0
    }

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for book_id, book_data in data.get('books', {}).items():
                count = book_data.get('count', 0)
                snapshot['books'][book_id] = count
                snapshot['total'] += count
        except Exception:
            pass

    # Sauvegarder le snapshot
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    return snapshot


def load_snapshot() -> dict:
    """Charge le dernier snapshot pris."""
    if not os.path.exists(SNAPSHOT_FILE):
        return {'books': {}, 'total': 0, 'timestamp': 'aucun'}
    try:
        with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'books': {}, 'total': 0, 'timestamp': 'erreur'}


def check_regression(new_cache_path: str = None) -> tuple:
    """
    Compare le nouveau cache avec le dernier snapshot.
    
    Retourne (is_ok: bool, report: str).
    - is_ok = True si aucune régression détectée (nombre >= snapshot)
    - is_ok = False si une régression est détectée (nombre < snapshot)
    """
    path = new_cache_path or CACHE_FILE
    snapshot = load_snapshot()

    if snapshot['total'] == 0:
        return True, "Aucun snapshot précédent — première exécution, pas de comparaison."

    if not os.path.exists(path):
        return False, f"❌ RÉGRESSION CRITIQUE : Le cache {path} n'existe pas alors que le snapshot indique {snapshot['total']} techniques."

    try:
        with open(path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except Exception as e:
        return False, f"❌ RÉGRESSION CRITIQUE : Impossible de lire le nouveau cache : {e}"

    new_books = new_data.get('books', {})
    new_total = sum(b.get('count', 0) for b in new_books.values())

    report_lines = []
    report_lines.append(f"📊 Comparaison avec le snapshot du {snapshot['timestamp']} :")
    report_lines.append(f"   Total précédent : {snapshot['total']:,} techniques")
    report_lines.append(f"   Total actuel    : {new_total:,} techniques")

    has_regression = False

    for book_id, old_count in snapshot['books'].items():
        new_count = new_books.get(book_id, {}).get('count', 0)
        delta = new_count - old_count
        if delta < 0:
            has_regression = True
            report_lines.append(f"   ❌ {book_id} : {old_count:,} → {new_count:,} (PERTE DE {abs(delta)} TECHNIQUES)")
        elif delta > 0:
            report_lines.append(f"   ✅ {book_id} : {old_count:,} → {new_count:,} (+{delta})")
        else:
            report_lines.append(f"   ✅ {book_id} : {new_count:,} (inchangé)")

    if new_total < snapshot['total']:
        has_regression = True
        report_lines.append(f"\n   ⛔ RÉGRESSION GLOBALE DÉTECTÉE : {snapshot['total'] - new_total} techniques perdues !")
        report_lines.append(f"   ⛔ DÉPLOIEMENT BLOQUÉ — Investiguer la perte de données.")
    else:
        report_lines.append(f"\n   ✅ AUCUNE RÉGRESSION — Le cache est sain.")

    return (not has_regression), "\n".join(report_lines)


def log_pipeline_execution(raccourci: str, steps: list, success: bool, details: str = ""):
    """
    Écrit une ligne dans le journal d'exécution immutable (pipeline_log.jsonl).
    Chaque exécution est tracée avec horodatage, étapes, résultat.
    """
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'raccourci': raccourci,
        'steps': steps,
        'success': success,
        'details': details
    }
    with open(PIPELINE_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
