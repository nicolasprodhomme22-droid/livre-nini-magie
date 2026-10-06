import os
import sys
import json
import datetime
import openpyxl
import urllib.request
import re

# Ajout du module partagé au path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.config import (
    ensure_utf8, find_data_sheet, load_taxonomies,
    BOOKS_CONFIG, BASE_DIR, APP_DATA_DIR
)
from shared.regression_guard import take_snapshot, check_regression

ensure_utf8()

os.makedirs(APP_DATA_DIR, exist_ok=True)
CACHE_FILE = os.path.join(APP_DATA_DIR, 'data_cache.json')

# Liste structurée des livres pour le sync (avec icônes)
BOOKS_LIST = [
    {**BOOKS_CONFIG['cartes'], 'sources_folder': BOOKS_CONFIG['cartes']['folder']},
    {**BOOKS_CONFIG['pieces'], 'sources_folder': BOOKS_CONFIG['pieces']['folder']},
    {**BOOKS_CONFIG['tours'], 'sources_folder': BOOKS_CONFIG['tours']['folder']},
    {**BOOKS_CONFIG['tours_pieces'], 'sources_folder': BOOKS_CONFIG['tours_pieces']['folder']},
]

def audit_and_sync():
    print("=" * 60)
    print("🔄 SKILL AGENT 4 : magic-db-sync (Optimisé)")
    print("=" * 60)

    # 1. Snapshot de sécurité AVANT synchronisation (garde anti-régression)
    print("📸 Prise de snapshot de sécurité avant synchronisation...")
    snapshot = take_snapshot()
    if snapshot.get('total', 0) > 0:
        print(f"   Référence actuelle en base : {snapshot['total']:,} techniques")

    consolidated_db = {
        'version': '1.0.0',
        'last_sync': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'books': {}
    }

    total_techniques_all = 0
    all_taxonomies = load_taxonomies()

    for book_info in BOOKS_LIST:
        book_id = book_info['id']
        excel_path = book_info['excel']
        print(f"\n📖 Synchronisation : {book_info['title']} ({os.path.basename(excel_path)})")
        
        if not os.path.exists(excel_path):
            print(f"   ❌ Erreur : Fichier introuvable ({excel_path})")
            continue

        wb = openpyxl.load_workbook(excel_path, data_only=False)
        target_sheet = find_data_sheet(wb)

        print(f"   📑 Onglet : '{target_sheet.title}'")

        techniques = []
        # Chargement de la structure officielle depuis le cache de taxonomies
        canonical_hierarchy = {}
        tax_map = {
            'cartes': 'livre_cartes_techniques',
            'pieces': 'livre_pieces_techniques',
            'tours': 'livre_tours_cartes',
            'tours_pieces': 'livre_tours_pieces',
        }
        tax_key = tax_map.get(book_id, f"livre_{book_id}_techniques")
        if tax_key in all_taxonomies:
            ref_struct = all_taxonomies[tax_key]['structure']
            for p in ref_struct:
                p_titre = p['titre']
                canonical_hierarchy[p_titre] = {}
                for c in p['chapitres']:
                    c_titre = c['titre']
                    canonical_hierarchy[p_titre][c_titre] = {}
                    if c.get('sections'):
                        for s in c['sections']:
                            canonical_hierarchy[p_titre][c_titre][s['titre']] = 0
                    else:
                        canonical_hierarchy[p_titre][c_titre]['Général'] = 0

        ids_seen = set()

        for r in range(2, target_sheet.max_row + 1):
            tech_id = target_sheet.cell(r, 1).value
            if not tech_id:
                continue

            tech_id = str(tech_id).strip()
            if tech_id in ids_seen:
                print(f"   ⚠️ Attention : Doublon de clé primaire ({tech_id}) ligne {r}")
            ids_seen.add(tech_id)

            partie = str(target_sheet.cell(r, 2).value or 'PARTIE 1').strip()
            chapitre = str(target_sheet.cell(r, 3).value or 'Chapitre 1 : Général').strip()
            section = str(target_sheet.cell(r, 4).value or 'Général').strip()
            nom = str(target_sheet.cell(r, 5).value or 'Sans titre').strip()
            description = str(target_sheet.cell(r, 6).value or '').strip()
            pdf_ref = str(target_sheet.cell(r, 7).value or '').strip()

            # Récupérer l'hyperlien réel de la cellule (colonne 8) et les cibles multiples
            cell_link = target_sheet.cell(r, 8)
            raw_targets = str(cell_link.value or '').strip()
            
            target_list = [t.strip().replace('\\', '/') for t in raw_targets.split(' | ') if t.strip() and '.pdf' in t.lower()]
            if not target_list and cell_link.hyperlink and cell_link.hyperlink.target:
                target_list = [cell_link.hyperlink.target.replace('\\', '/')]

            ref_list = [rf.strip() for rf in pdf_ref.split(' | ') if rf.strip()]

            # Construction des sources structurées pour le multi-PDF
            sources = []
            num_sources = max(len(ref_list), len(target_list), 1 if (pdf_ref or target_list) else 0)

            for idx in range(num_sources):
                rf = ref_list[idx] if idx < len(ref_list) else (ref_list[0] if ref_list else '')
                tg = target_list[idx] if idx < len(target_list) else (target_list[0] if target_list else '')
                
                # Extraction du numéro de page
                pg = 1
                m = re.search(r'#page=(\d+)', tg)
                if m:
                    pg = int(m.group(1))
                else:
                    m2 = re.search(r'p\.\s*(\d+)', rf, re.IGNORECASE)
                    if m2:
                        pg = int(m2.group(1))
                
                # Extraction du nom du livre / document
                book_name = ''
                if tg:
                    clean_fn = tg.split('#')[0].split('/')[-1]
                    book_name = clean_fn.replace('.pdf', '')
                elif rf:
                    book_name = rf.split(',')[0].strip().replace('.pdf', '')

                sources.append({
                    'ref': rf,
                    'target': tg,
                    'page': pg,
                    'book': book_name
                })

            primary_target = target_list[0] if target_list else (cell_link.hyperlink.target.replace('\\', '/') if cell_link.hyperlink and cell_link.hyperlink.target else "")

            # Rapprochement avec la taxonomie officielle
            matched_p = None
            for cp in canonical_hierarchy.keys():
                if cp.split(' : ')[0].strip().lower() == partie.split(' : ')[0].strip().lower():
                    matched_p = cp
                    break
            if not matched_p:
                matched_p = partie
                if matched_p not in canonical_hierarchy:
                    canonical_hierarchy[matched_p] = {}

            matched_c = None
            if matched_p in canonical_hierarchy:
                for cc in canonical_hierarchy[matched_p].keys():
                    if cc.split(' : ')[0].strip().lower() == chapitre.split(' : ')[0].strip().lower():
                        matched_c = cc
                        break
            if not matched_c:
                matched_c = chapitre
                if matched_c not in canonical_hierarchy[matched_p]:
                    canonical_hierarchy[matched_p][matched_c] = {}

            matched_s = None
            sec_dict = canonical_hierarchy[matched_p][matched_c]
            if 'Général' in sec_dict and len(sec_dict) == 1:
                matched_s = 'Général'
            else:
                for cs in sec_dict.keys():
                    if cs.split(' : ')[0].strip().lower() == section.split(' : ')[0].strip().lower():
                        matched_s = cs
                        break
                if not matched_s:
                    matched_s = list(sec_dict.keys())[0] if sec_dict else section

            if matched_s not in sec_dict:
                sec_dict[matched_s] = 0
            sec_dict[matched_s] += 1

            techniques.append({
                'id': tech_id,
                'partie': matched_p,
                'chapitre': matched_c,
                'section': matched_s,
                'nom': nom,
                'description': description,
                'pdf_ref': pdf_ref,
                'pdf_target': primary_target,
                'sources': sources
            })

        print(f"   ✅ {len(techniques)} techniques extraites.")
        print(f"   📊 Sommaire officiel complet : {len(canonical_hierarchy)} parties, {sum(len(ch) for ch in canonical_hierarchy.values())} chapitres")

        consolidated_db['books'][book_id] = {
            'id': book_id,
            'title': book_info['title'],
            'icon': book_info.get('icon', '📖'),
            'count': len(techniques),
            'hierarchy': canonical_hierarchy,
            'techniques': techniques
        }
        total_techniques_all += len(techniques)

    # Sauvegarde atomique et contrôle anti-régression
    temp_cache = CACHE_FILE + ".tmp"
    with open(temp_cache, 'w', encoding='utf-8') as f:
        json.dump(consolidated_db, f, ensure_ascii=False, indent=2)

    # 2. Vérification anti-régression stricte AVANT écrasement du cache
    is_ok, report = check_regression(temp_cache)
    print(f"\n{report}")

    if not is_ok:
        if os.path.exists(temp_cache):
            os.remove(temp_cache)
        print("❌ OPÉRATION ANNULÉE : Le nouveau cache contient moins de techniques que la version précédente.")
        print("   Vos données existantes sont protégées et le cache actuel n'a PAS été modifié.")
        sys.exit(1)

    # 3. Écrasement atomique sans fichier tiers
    os.replace(temp_cache, CACHE_FILE)

    print(f"\n💾 Cache applicatif généré en toute sécurité : {CACHE_FILE}")
    print(f"🌟 Total général : {total_techniques_all} techniques synchronisées dans les 3 bases !")

    # Notification passive de l'application web si elle tourne (route reload passive, SANS boucle récursive)
    try:
        req = urllib.request.Request(
            "http://localhost:3000/api/reload",
            data=b'{}',
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=0.5) as resp:
            print("🚀 Notification envoyée au serveur web (rechargement de base effectué en mémoire).")
    except Exception:
        # C'est normal si le serveur n'est pas démarré lors de l'exécution standalone
        pass

if __name__ == '__main__':
    audit_and_sync()
