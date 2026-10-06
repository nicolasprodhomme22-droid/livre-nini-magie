import os
import sys
import argparse

# Ajout du module partagé au path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.config import ensure_utf8, get_book_config, normalize_book_key, BOOKS_CONFIG, backup_excel

ensure_utf8()

from ocr_cleaner import clean_ocr_text, clean_title, is_noise
from pdf_extractor import PDFTechniqueExtractor
from classifier import MagicClassifier
from excel_manager import ExcelManager

ENHANCER_PATH = os.path.join(_PROJECT_ROOT, '.agents', 'skills', 'magic-desc-enhancer', 'scripts')
if ENHANCER_PATH not in sys.path:
    sys.path.insert(0, ENHANCER_PATH)

try:
    from desc_enhancer import MagicDescEnhancer
    HAS_ENHANCER = True
except ImportError:
    HAS_ENHANCER = False


def run_agent(book_key: str, max_pages_per_pdf: int = None, single_pdf: str = None, use_toc: bool = True, dry_run: bool = False) -> int:
    config = get_book_config(book_key)

    classifier = MagicClassifier()
    excel_mgr = ExcelManager(config['excel'], config['prefix'])
    enhancer = MagicDescEnhancer() if HAS_ENHANCER else None
    folder = config['folder']

    print(f"\n=======================================================")
    print(f"🚀 SKILL AGENT 1 : magic-pdf-extractor")
    print(f"=======================================================")
    print(f"📖 Livre cible      : {config['title']} ({config['id']})")
    print(f"📁 Dossier sources  : {folder}")
    print(f"📊 Fichier Excel    : {os.path.basename(config['excel'])}")
    print(f"🔖 Extraction TOC   : {'Activée' if use_toc else 'Désactivée'}")
    print(f"📑 Pages max par PDF: {'Toutes les pages' if max_pages_per_pdf is None else max_pages_per_pdf}")
    print(f"🔒 Mode simulation  : {'OUI (Dry Run)' if dry_run else 'NON (Écriture Excel)'}\n")

    if not os.path.exists(folder):
        print(f"❌ Erreur: Dossier introuvable : {folder}")
        return 0

    if single_pdf:
        pdf_files = [single_pdf]
    else:
        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]

    total_added = 0
    total_skipped = 0

    for pdf_name in pdf_files:
        pdf_path = os.path.join(folder, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"⚠️ Fichier introuvable: {pdf_name}")
            continue

        print(f"📄 Analyse de : {pdf_name}...")
        try:
            extractor = PDFTechniqueExtractor(pdf_path)
            techniques = extractor.extract_techniques(start_page=1, end_page=max_pages_per_pdf, use_toc=use_toc)
            print(f"   -> {len(techniques)} candidats identifiés (source: {techniques[0]['source'] if techniques else 'aucune'})")
            
            added_for_pdf = 0
            for item in techniques:
                # 1. Vérification stricte anti-bruit OCR / faux positifs
                if is_noise(item['nom']):
                    total_skipped += 1
                    continue

                # 2. Vérification stricte anti-doublon pour compléter uniquement le manquant
                if excel_mgr.is_duplicate(item['nom'], item['pdf_reference']):
                    total_skipped += 1
                    continue

                partie, chap, sec = classifier.classify_technique(config['id'], item['nom'], item['description'])
                rel_link = f"{config['rel_folder']}/{pdf_name}#page={item['page_physique']}"
                
                final_desc = enhancer.enhance_description(config['id'], partie, chap, sec, item['nom'], item['description']) if enhancer else item['description']
                desc_snippet = final_desc[:50] + "..." if len(final_desc) > 50 else final_desc

                if not dry_run:
                    tech_id = excel_mgr.add_technique(
                        partie=partie,
                        chapitre=chap,
                        section=sec,
                        nom=item['nom'],
                        description=final_desc,
                        pdf_reference=item['pdf_reference'],
                        pdf_link=rel_link
                    )
                    print(f"      [+] {tech_id} | {item['nom'][:35]} | {chap[:20]}")
                else:
                    print(f"      [SIMULATION] {item['nom'][:35]} -> {chap[:20]} (p.{item['page_physique']})")

                total_added += 1
                added_for_pdf += 1

            if added_for_pdf > 0:
                print(f"   ✨ {added_for_pdf} nouvelles techniques ajoutées pour ce PDF.")
            else:
                print(f"   ℹ️ Aucune nouvelle technique manquante (déjà complètes).")

        except Exception as e:
            print(f"   ⚠️ Erreur sur {pdf_name}: {e}")

    if not dry_run and excel_mgr.has_changes:
        backup_excel(config['excel'])
        excel_mgr.save()
        print(f"\n💾 Sauvegarde réussie dans {os.path.basename(config['excel'])} (+{excel_mgr.added_count} techniques ajoutées, {excel_mgr.updated_count} liens mis à jour, {total_skipped} doublons traités).")
    else:
        print(f"\n🏁 Fin : 0 modification à enregistrer ({total_skipped} techniques déjà présentes dans la base).")

    return total_added

def run_targeted_search(book_key: str, query: str, dry_run: bool = True):
    config = get_book_config(book_key)
    folder = config['folder']
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    print(f"\n🔎 Recherche ciblée du terme/sujet '{query}' dans {len(pdf_files)} PDF(s) de {config['rel_folder']}...")
    total_found = 0
    for pdf_name in pdf_files:
        pdf_path = os.path.join(folder, pdf_name)
        try:
            extractor = PDFTechniqueExtractor(pdf_path)
            hits = extractor.search_topic(topic_title=query, keywords=[query])
            if hits:
                print(f"\n📄 {pdf_name} : {len(hits)} occurrence(s)")
                for h in hits[:5]:
                    print(f"   -> p. {h['page_physique']} | {h['nom']}")
                    print(f"      📝 {h['description'][:120]}...")
                total_found += len(hits)
        except Exception as e:
            print(f"⚠️ Erreur de lecture sur {pdf_name}: {e}")
    print(f"\n🏁 Total trouvé : {total_found} occurrence(s).")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Skill Agent 1 : magic-pdf-extractor")
    parser.add_argument('--book', default=None, help="Clé du livre à traiter ('cartes', 'pieces', 'tours')")
    parser.add_argument('--all', action='store_true', help="Traiter les 3 livres séquentiellement")
    parser.add_argument('--pages', type=int, default=None, help="Nombre max de pages par PDF (défaut: toutes les pages)")
    parser.add_argument('--pdf', type=str, default=None, help="Nom d'un fichier PDF spécifique à traiter")
    parser.add_argument('--no-toc', action='store_true', help="Désactiver l'extraction par TOC native")
    parser.add_argument('--dry-run', action='store_true', help="Mode simulation sans écriture Excel")
    parser.add_argument('--search', type=str, default=None, help="Effectuer une recherche plein-texte ciblée sur un mot-clé ou sujet")
    args = parser.parse_args()

    if args.search:
        target_book = args.book or 'cartes'
        run_targeted_search(target_book, args.search, dry_run=args.dry_run)
    elif args.all:
        grand_total = 0
        for bk in BOOKS_CONFIG.keys():
            added = run_agent(bk, max_pages_per_pdf=args.pages, single_pdf=args.pdf, use_toc=not args.no_toc, dry_run=args.dry_run)
            grand_total += added
        print(f"\n=======================================================")
        print(f"🎉 EXTRACTION TERMINÉE SUR LES 3 LIVRES : +{grand_total} techniques ajoutées !")
        print(f"=======================================================")
    else:
        target_book = args.book or 'pieces'
        run_agent(target_book, max_pages_per_pdf=args.pages, single_pdf=args.pdf, use_toc=not args.no_toc, dry_run=args.dry_run)
