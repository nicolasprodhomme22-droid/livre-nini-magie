import subprocess
import sys
import os
import urllib.request
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

def run_command(cmd, desc):
    print(f"\n🚀 {desc}...")
    res = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res.returncode != 0:
        print(f"❌ Échec de : {desc}")
        print(res.stderr)
        return False, res.stderr
    print(f"✅ {desc} réussi.")
    return True, res.stdout

def deploy():
    print("=" * 60)
    print("⚡ [DEPLOY GITHUB PAGES] Déploiement automatisé certifié")
    print("=" * 60)

    # 1. Vérification interne
    ok, _ = run_command("python .agents/skills/magic-app-guardian/scripts/verify_app.py", "1. Contrôle qualité et intégrité de l'application")
    if not ok:
        print("⛔ Déploiement annulé car des erreurs ont été détectées.")
        return False

    # 2. Préparation du dossier dist/
    ok, _ = run_command("node scripts/prepare_netlify.js", "2. Compilation du dossier dist/")
    if not ok:
        return False

    # 3. Déploiement vers GitHub Pages via gh-pages
    ok, out = run_command('npx gh-pages -d dist -m "Deploy: Livre nini magie [automated]"', "3. Déploiement sur la branche GitHub Pages")
    if not ok:
        print("💡 Astuce : Assurez-vous d'avoir configuré le remote Git (git remote add origin ...).")
        return False

    print("\n" + "=" * 60)
    print("🎉 DÉPLOIEMENT GITHUB PAGES TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = deploy()
    sys.exit(0 if success else 1)
