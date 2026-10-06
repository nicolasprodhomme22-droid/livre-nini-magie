import os
import sys
import argparse
import subprocess
import time

# Ajout du module partagé au path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.config import ensure_utf8
from shared.regression_guard import log_pipeline_execution
ensure_utf8()

SKILLS_DIR = os.path.join(ROOT_DIR, '.agents', 'skills')

EXTRACTOR_SCRIPT = os.path.join(SKILLS_DIR, 'magic-pdf-extractor', 'scripts', 'run_extraction.py')
ENHANCER_SCRIPT = os.path.join(SKILLS_DIR, 'magic-desc-enhancer', 'scripts', 'run_enhancement.py')
LINKER_SCRIPT = os.path.join(SKILLS_DIR, 'magic-link-builder', 'scripts', 'link_builder.py')
SYNC_SCRIPT = os.path.join(SKILLS_DIR, 'magic-db-sync', 'scripts', 'sync_engine.py')
VERIFY_SCRIPT = os.path.join(SKILLS_DIR, 'magic-app-guardian', 'scripts', 'verify_app.py')
DEPLOY_SCRIPT = os.path.join(SKILLS_DIR, 'magic-app-guardian', 'scripts', 'deploy_github.py')

def run_step(desc: str, cmd: str) -> bool:
    print(f"\n{'=' * 65}")
    print(f"▶️  ÉTAPE : {desc}")
    print(f"💻 COMMANDE : {cmd}")
    print(f"{'=' * 65}")
    
    start_t = time.time()
    res = subprocess.run(cmd, shell=True, cwd=ROOT_DIR)
    elapsed = time.time() - start_t
    
    if res.returncode != 0:
        print(f"\n❌ Échec de l'étape '{desc}' (Code sortie: {res.returncode}, Durée: {elapsed:.1f}s)")
        return False
    print(f"\n✅ Étape '{desc}' réussie en {elapsed:.1f}s.")
    return True

# -------------------------------------------------------------
# RACCOURCIS OFFICIELS DU WORKFLOW
# -------------------------------------------------------------

def shortcut_1_maj_livre(book: str, dry_run: bool = False, pdf: str = None, deduplicate: bool = False) -> bool:
    """Raccourci 1 : Mise à jour automatique complète d'un livre (Skill 1 -> 2 -> 3 -> 4)"""
    print("\n🚀 [RACCOURCI 1] Mise à jour complète de livre (Extraction -> Description -> Liens -> Sync DB)")
    dry_flag = " --dry-run" if dry_run else ""
    pdf_flag = f' --pdf \"{pdf}\"' if pdf else ""

    # 0. Déduplication préalable (optionnelle)
    if deduplicate and not dry_run:
        if not run_step("0. Consolidation et déduplication préalable", f'python \"{DEDUP_SCRIPT}\" --book {book}'):
            return False

    # 1. Skill 1 : magic-pdf-extractor
    if not run_step("1. Extraction & Déduplication (Skill 1)", f'python \"{EXTRACTOR_SCRIPT}\" --book {book}{pdf_flag}{dry_flag}'):
        return False

    # 2. Skill 2 : magic-desc-enhancer
    if not run_step("2. Normalisation [Effet] | [Méthode] (Skill 2)", f'python \"{ENHANCER_SCRIPT}\" --book {book}{dry_flag}'):
        return False

    # 3. Skill 3 : magic-link-builder
    if not run_step("3. Résolution des hyperliens PDF physiques (Skill 3)", f'python \"{LINKER_SCRIPT}\" --book {book}{dry_flag}'):
        return False

    # 4. Skill 4 : magic-db-sync
    if not dry_run:
        if not run_step("4. Synchronisation Cache & DB (Skill 4)", f'python \"{SYNC_SCRIPT}\"'):
            return False

    print("\n🎉 [RACCOURCI 1 TERMINÉ AVEC SUCCÈS]")
    return True

def shortcut_2_recherche(book: str, query: str) -> bool:
    """Raccourci 2 : Recherche ciblée dans les sources PDF lisibles"""
    print(f"\n🔍 [RACCOURCI 2] Recherche ciblée de '{query}' dans le livre '{book}'")
    return run_step("Recherche plein-texte dans les traités OCR (Skill 1)", f'python "{EXTRACTOR_SCRIPT}" --book {book} --search "{query}"')

def shortcut_3_maj_description(book: str, partie: str = None, chapitre: str = None, limit: int = None, dry_run: bool = False) -> bool:
    """Raccourci 3 : Enrichissement rédactionnel ciblé (Skill 2 -> Skill 4)"""
    print(f"\n✍️ [RACCOURCI 3] Amélioration rédactionnelle des fiches ({book})")
    dry_flag = " --dry-run" if dry_run else ""
    partie_flag = f' --partie "{partie}"' if partie else ""
    chapitre_flag = f' --chapitre "{chapitre}"' if chapitre else ""
    limit_flag = f' --limit {limit}' if limit else ""

    if not run_step("Enrichissement des descriptions [Effet] | [Méthode] (Skill 2)", f'python "{ENHANCER_SCRIPT}" --book {book}{partie_flag}{chapitre_flag}{limit_flag}{dry_flag}'):
        return False

    if not dry_run:
        if not run_step("Synchronisation Cache applicatif (Skill 4)", f'python "{SYNC_SCRIPT}"'):
            return False

    print("\n🎉 [RACCOURCI 3 TERMINÉ AVEC SUCCÈS]")
    return True

def shortcut_4_maj_liens(book: str = None, all_books: bool = False, dry_run: bool = False) -> bool:
    """Raccourci 4 : Réparation et vérification des hyperliens (Skill 3 -> Skill 4)"""
    print(f"\n🔗 [RACCOURCI 4] Vérification et reconstruction des liens PDF ({'Tous les livres' if all_books else book})")
    dry_flag = " --dry-run" if dry_run else ""
    target_flag = "--all" if all_books else f"--book {book}"

    if not run_step("Reconstruction des hyperliens physiques (Skill 3)", f'python "{LINKER_SCRIPT}" {target_flag}{dry_flag}'):
        return False

    if not dry_run:
        if not run_step("Synchronisation Cache applicatif (Skill 4)", f'python "{SYNC_SCRIPT}"'):
            return False

    print("\n🎉 [RACCOURCI 4 TERMINÉ AVEC SUCCÈS]")
    return True

def shortcut_5_maj_app() -> bool:
    """Raccourci 5 : Synchronisation cache et déploiement express (Skill 4 -> Skill 5)"""
    print("\n🔄 [RACCOURCI 5] Mise à jour complète de l'application (Sync DB -> Audit -> Déploiement)")
    steps_log = []

    # 1. Skill 4 : Sync DB avec garde anti-régression
    s1 = run_step("1. Synchronisation de la base Excel vers le cache (Skill 4)", f'python "{SYNC_SCRIPT}"')
    steps_log.append(('Sync DB', s1))
    if not s1:
        log_pipeline_execution("Raccourci 5 (/maj-app)", steps_log, False, "Échec lors de la synchronisation de la base")
        return False

    # 2. Skill 5 : Audit intégrité
    s2 = run_step("2. Contrôle qualité frontend et compatibilité DOM (Skill 5)", f'python "{VERIFY_SCRIPT}"')
    steps_log.append(('Audit Qualité', s2))
    if not s2:
        log_pipeline_execution("Raccourci 5 (/maj-app)", steps_log, False, "Échec du contrôle qualité frontend")
        return False

    # 3. Skill 5 : Déploiement GitHub Pages
    s3 = run_step("3. Déploiement production sur GitHub Pages (Skill 5)", f'python "{DEPLOY_SCRIPT}"')
    steps_log.append(('Déploiement GitHub Pages', s3))
    if not s3:
        log_pipeline_execution("Raccourci 5 (/maj-app)", steps_log, False, "Échec du déploiement GitHub Pages")
        return False

    log_pipeline_execution("Raccourci 5 (/maj-app)", steps_log, True, "Synchronisation et déploiement réussis")
    print("\n🎉 [RACCOURCI 5 TERMINÉ AVEC SUCCÈS]")
    return True

def shortcut_6_deploy() -> bool:
    """Raccourci 6 : Audit et déploiement GitHub Pages direct"""
    print("\n⚡ [RACCOURCI 6] Audit qualité et déploiement GitHub Pages direct")
    return run_step("Déploiement certifié GitHub Pages", f'python "{DEPLOY_SCRIPT}"')

# -------------------------------------------------------------
# CLI ENTRYPOINT
# -------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="🚀 Orchestrateur Maître du Pipeline 'Livre nini magie'")
    parser.add_argument('--shortcut', type=int, choices=[1, 2, 3, 4, 5, 6], default=None, help="Numéro du raccourci à exécuter (1 à 6)")
    parser.add_argument('--book', type=str, default='cartes', help="Livre cible ('cartes', 'pieces', 'tours', 'tours_pieces')")
    parser.add_argument('--all', action='store_true', help="Traiter tous les livres (pour Raccourci 4)")
    parser.add_argument('--query', type=str, default=None, help="Terme ou sujet de recherche (pour Raccourci 2)")
    parser.add_argument('--partie', type=str, default=None, help="Filtre partie (pour Raccourcis 1 et 3)")
    parser.add_argument('--chapitre', type=str, default=None, help="Filtre chapitre (pour Raccourcis 1 et 3)")
    parser.add_argument('--pdf', type=str, default=None, help="Fichier PDF spécifique (pour Raccourci 1)")
    parser.add_argument('--limit', type=int, default=None, help="Limite de fiches (pour Raccourci 3)")
    parser.add_argument('--dry-run', action='store_true', help="Mode simulation sans écriture")
    parser.add_argument('--deduplicate', action='store_true', help="Lancer la consolidation/déduplication avant le pipeline (Raccourci 1)")
    
    # Raccourcis sous forme de drapeaux directs
    parser.add_argument('--maj-livre', action='store_true', help="Alias Raccourci 1")
    parser.add_argument('--recherche', action='store_true', help="Alias Raccourci 2")
    parser.add_argument('--maj-desc', action='store_true', help="Alias Raccourci 3")
    parser.add_argument('--maj-liens', action='store_true', help="Alias Raccourci 4")
    parser.add_argument('--maj-app', action='store_true', help="Alias Raccourci 5")
    parser.add_argument('--deploy', action='store_true', help="Alias Raccourci 6")

    args = parser.parse_args()

    sc = args.shortcut
    if args.maj_livre: sc = 1
    elif args.recherche: sc = 2
    elif args.maj_desc: sc = 3
    elif args.maj_liens: sc = 4
    elif args.maj_app: sc = 5
    elif args.deploy: sc = 6

    if sc == 1:
        ok = shortcut_1_maj_livre(args.book, dry_run=args.dry_run, pdf=args.pdf, deduplicate=args.deduplicate)
    elif sc == 2:
        if not args.query:
            print("❌ Erreur : Le Raccourci 2 nécessite un paramètre --query 'terme de recherche'")
            sys.exit(1)
        ok = shortcut_2_recherche(args.book, args.query)
    elif sc == 3:
        ok = shortcut_3_maj_description(args.book, partie=args.partie, chapitre=args.chapitre, limit=args.limit, dry_run=args.dry_run)
    elif sc == 4:
        ok = shortcut_4_maj_liens(book=args.book, all_books=args.all, dry_run=args.dry_run)
    elif sc == 5:
        ok = shortcut_5_maj_app()
    elif sc == 6:
        ok = shortcut_6_deploy()
    else:
        print("ℹ️ Aucun raccourci spécifié. Utilisez --shortcut [1-6] ou un alias (--maj-app, --maj-livre, etc.)")
        parser.print_help()
        sys.exit(0)

    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
