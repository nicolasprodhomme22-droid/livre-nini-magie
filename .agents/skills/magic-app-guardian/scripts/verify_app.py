import re
import sys
import os
import subprocess
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.regression_guard import check_regression

HTML_PATH = os.path.join(ROOT, 'app', 'public', 'index.html')
JS_PATH = os.path.join(ROOT, 'app', 'public', 'app.js')
DATA_PATH = os.path.join(ROOT, 'app', 'data', 'data_cache.json')

def verify():
    print("=" * 60)
    print("🔍 [VERIFY APP] Contrôle d'intégrité de l'application")
    print("=" * 60)
    errors = 0

    # 1. Vérification syntaxe JS
    print("\n1. Validation syntaxique de app.js...")
    res = subprocess.run(["node", "-c", JS_PATH], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Erreur de syntaxe JS dans app.js :\n{res.stderr}")
        errors += 1
    else:
        print("✅ Syntaxe JavaScript valide (0 erreur).")

    # 2. Vérification des IDs HTML vs getElementById
    print("\n2. Vérification de concordance des IDs DOM...")
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    with open(JS_PATH, 'r', encoding='utf-8') as f:
        js = f.read()

    ids = set(re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", js))
    missing_ids = []
    for el_id in ids:
        if f'id="{el_id}"' not in html and f"id='{el_id}'" not in html:
            missing_ids.append(el_id)

    if missing_ids:
        print(f"❌ {len(missing_ids)} ID(s) appelés dans app.js sont INTROUVABLES dans index.html :")
        for m in missing_ids:
            print(f"   - {m}")
        errors += 1
    else:
        print(f"✅ 100% des {len(ids)} IDs DOM de app.js sont bien présents dans index.html.")

    # 3. Vérification du cache de données (data_cache.json)
    print("\n3. Vérification de data_cache.json...")
    if not os.path.exists(DATA_PATH):
        print("❌ data_cache.json introuvable !")
        errors += 1
    else:
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            books = data.get('books', {})
            total_count = sum(b.get('count', 0) for b in books.values())
            print(f"✅ data_cache.json valide : {len(books)} livres, {total_count:,} techniques répertoriées.")
            if total_count < 18000:
                print(f"⚠️ Attention : nombre de techniques inhabituel ({total_count} < 18 000).")

            # Contrôle anti-régression strict
            is_ok, reg_report = check_regression(DATA_PATH)
            if not is_ok:
                print(f"\n❌ CONTRÔLE ANTI-RÉGRESSION ÉCHOUÉ :\n{reg_report}")
                errors += 1
            else:
                print("✅ Contrôle anti-régression validé (aucune perte de données).")
        except Exception as e:
            print(f"❌ Erreur de lecture de data_cache.json : {e}")
            errors += 1

    # 4. Vérification du nom et des 3 onglets
    print("\n4. Vérification de la charte (Titre et Onglets)...")
    if "<title>Livre nini magie</title>" not in html:
        print("❌ Le titre doit être strictement 'Livre nini magie'.")
        errors += 1
    else:
        print("✅ Titre officiel conforme ('Livre nini magie').")

    for tab in ['Bibliothèque', 'Sommaire', 'Classement', 'PDF à télécharger']:
        if tab not in html:
            print(f"❌ Onglet obligatoire manquant : '{tab}'")
            errors += 1
        else:
            print(f"✅ Onglet présent : '{tab}'")

    # 5. Contrôle du module Classement & simulation d'exécution
    print("\n5. Vérification du module Classement et simulation d'exécution...")
    xlsx_vendor_path = os.path.join(ROOT, 'app', 'public', 'vendor', 'xlsx.full.min.js')
    if not os.path.exists(xlsx_vendor_path):
        print(f"❌ vendor/xlsx.full.min.js introuvable dans {xlsx_vendor_path} !")
        errors += 1
    else:
        print("✅ Bibliothèque locale SheetJS présente (vendor/xlsx.full.min.js).")

    test_js = """
    const fs = require('fs');
    let js = fs.readFileSync('./app/public/app.js', 'utf-8');
    const data = JSON.parse(fs.readFileSync('./app/data/data_cache.json', 'utf-8'));
    global.XLSX = require('./app/public/vendor/xlsx.full.min.js');

    global.window = {};
    global.document = {
      addEventListener: () => {},
      getElementById: (id) => ({
        id,
        addEventListener: () => {},
        classList: { toggle: () => {}, add: () => {}, remove: () => {} },
        style: {},
        appendChild: () => {},
        innerHTML: '',
        querySelectorAll: () => []
      }),
      querySelectorAll: () => [],
      createElement: (tag) => ({
        tagName: tag,
        classList: { toggle: () => {}, add: () => {}, remove: () => {} },
        style: {},
        dataset: {},
        appendChild: () => {},
        addEventListener: () => {},
        querySelector: () => ({ addEventListener: () => {} }),
        querySelectorAll: () => []
      })
    };
    global.localStorage = { getItem: () => null, setItem: () => {} };
    js = js.replace('const state =', 'global.state =');
    js = js.replace('const dom =', 'global.dom =');
    eval(js);

    global.state.booksData = data.books;
    ['cartes', 'pieces', 'tours', 'tours_pieces'].forEach(b => {
      global.state.classementBook = b;
      global.renderClassementTree();
    });

    global.XLSX.writeFile = () => {};
    exportBookToExcel('cartes');
    exportAllBooksToExcel();
    console.log('CLASSEMENT_SIMULATION_OK');
    """
    res_sim = subprocess.run(["node", "-e", test_js], cwd=ROOT, capture_output=True, text=True)
    if "CLASSEMENT_SIMULATION_OK" not in res_sim.stdout:
        print(f"❌ Échec de la simulation du module Classement :\n{res_sim.stderr}")
        errors += 1
    else:
        print("✅ Simulation du module Classement réussie sur les 4 livres et l'export Excel (0 régression).")

    print("\n" + "=" * 60)
    if errors == 0:
        print("🎉 BILAN : SUCCÈS TOTAL — L'application est 100% saine et prête !")
        print("=" * 60)
        return True
    else:
        print(f"💥 BILAN : {errors} ERREUR(S) DÉTECTÉE(S) — Veuillez corriger avant déploiement.")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
