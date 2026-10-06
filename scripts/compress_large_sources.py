import os
import sys
import fitz

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

FILES_TO_COMPRESS = [
    {
        'rel_path': r'Sources\sources_lisibles\sources tours de Cartes\STRIPPER DECK jean-hugards-miracle-methods-1-pdf-free.pdf',
        'dpi_target': 0,
        'quality': 75,
        'name': 'Stripper Deck (Hugard)'
    },
    {
        'rel_path': r'Sources\sources_lisibles\sources tours de Cartes\GENERAL - the code fenik.pdf',
        'dpi_target': 150,
        'quality': 70,
        'name': 'The Code (Fenik)'
    },
    {
        'rel_path': r'Sources\sources_lisibles\sources techniques Pièces\michael-rubinstein-coin-magic-rops-press-2020-pdf-free.pdf',
        'dpi_target': 120,
        'quality': 60,
        'name': 'Rubinstein Coin Magic'
    }
]

def compress_file(item):
    full_path = os.path.join(ROOT, item['rel_path'])
    if not os.path.exists(full_path):
        print(f"[WARN] Fichier non trouvé : {full_path}")
        return False

    sz_orig = os.path.getsize(full_path) / (1024 * 1024)
    print(f"\n[OPTIMISATION] {item['name']}")
    print(f"  Chemin : {item['rel_path']}")
    print(f"  Taille actuelle : {sz_orig:.2f} MB")

    temp_path = full_path + '.opt.tmp'
    doc = fitz.open(full_path)
    page_count = len(doc)
    text_sample_before = len(doc[min(10, page_count - 1)].get_text())

    print(f"  Pages : {page_count} | Échantillon texte page test : {text_sample_before} caractères")
    print(f"  Traitement des flux d'images (dpi_target={item['dpi_target']}, quality={item['quality']})...")

    if item['dpi_target'] > 0:
        doc.rewrite_images(dpi_target=item['dpi_target'], quality=item['quality'])
    else:
        doc.rewrite_images(quality=item['quality'])

    doc.save(temp_path, garbage=4, deflate=True)
    doc.close()

    doc_test = fitz.open(temp_path)
    text_sample_after = len(doc_test[min(10, page_count - 1)].get_text())
    doc_test.close()

    sz_new = os.path.getsize(temp_path) / (1024 * 1024)
    print(f"  Nouvelle taille : {sz_new:.2f} MB")
    print(f"  Vérification couche texte OCR : {text_sample_after} caractères (Intacte : {text_sample_before == text_sample_after})")

    if sz_new < 95.0 and text_sample_before == text_sample_after:
        os.replace(temp_path, full_path)
        print(f"  [SUCCES] Remplacement effectif. Gain : -{sz_orig - sz_new:.2f} MB")
        return True
    else:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"  [ERREUR] Condition non remplie (Taille: {sz_new:.2f} MB, Texte: {text_sample_after})")
        return False

def main():
    print("=" * 65)
    print("🚀 OPTIMISATION DES 3 PDF > 100 MO POUR GITHUB")
    print("=" * 65)
    success = True
    for item in FILES_TO_COMPRESS:
        ok = compress_file(item)
        if not ok:
            success = False

    print("\n" + "=" * 65)
    if success:
        print("[SUCCÈS TOTAL] Les 3 fichiers sont maintenant sous la limite de 100 Mo !")
    else:
        print("[ATTENTION] Une ou plusieurs optimisations ont échoué.")
    print("=" * 65)
    return success

if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
