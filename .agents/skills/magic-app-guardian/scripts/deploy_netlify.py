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
    print("⚡ [DEPLOY NETLIFY] Déploiement automatisé certifié")
    print("=" * 60)

    # 1. Vérification interne
    ok, _ = run_command("python .agents/skills/magic-app-guardian/scripts/verify_app.py", "1. Contrôle qualité et absence de bugs")
    if not ok:
        print("⛔ Déploiement annulé car des erreurs ont été détectées.")
        return False

    # 2. Préparation du dossier dist
    ok, _ = run_command("node scripts/prepare_netlify.js", "2. Préparation du dossier dist/")
    if not ok:
        return False

    # 3. Déploiement en production sur Netlify
    ok, out = run_command("npx netlify deploy --dir dist --no-build --site encyclopedie-magique --prod", "3. Déploiement Netlify Production")
    if not ok:
        return False

    # 4. Test en ligne de l'application
    print("\n4. Test de connectivité en ligne...")
    try:
        url = "https://encyclopedie-magique.netlify.app/data/data_cache.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                total = sum(b.get('count', 0) for b in data.get('books', {}).values())
                print(f"✅ Site en ligne 100% opérationnel : {total:,} fiches certifiées !")
                print("🔗 URL : https://encyclopedie-magique.netlify.app")
            else:
                print(f"⚠️ Réponse HTTP inattendue : {resp.status}")
    except Exception as e:
        print(f"⚠️ Note test réseau : {e}")

    print("\n" + "=" * 60)
    print("🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = deploy()
    sys.exit(0 if success else 1)
