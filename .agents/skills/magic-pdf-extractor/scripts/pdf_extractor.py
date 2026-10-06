import fitz
import os
import re
from typing import List, Dict
from collections import Counter
from ocr_cleaner import clean_ocr_text, clean_title, format_effect_method

class PDFTechniqueExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = os.path.abspath(pdf_path)
        self.filename = os.path.basename(pdf_path)
        self.doc = fitz.open(self.pdf_path)
        self.total_pages = len(self.doc)

    def extract_from_toc(self) -> List[Dict]:
        """
        Extrait les techniques et chapitres directement depuis la table des matières (TOC) native du PDF.
        Garantit une précision de 100% sur le titre et la page physique d'origine quand le TOC existe.
        """
        raw_toc = self.doc.get_toc()
        if not raw_toc or len(raw_toc) < 3:
            return []

        techniques = []
        for item in raw_toc:
            # item = [level, title, page_physique]
            if len(item) < 3:
                continue
            lvl, raw_title, page_no = item[0], item[1], item[2]
            if page_no < 1 or page_no > self.total_pages:
                continue

            title = clean_title(raw_title)
            if not title:
                continue

            # Éviter les métadonnées de structure pure
            if any(x in title.lower() for x in ['contents', 'copyright', 'preface', 'foreword', 'index', 'cover', 'disque local']):
                continue

            # Extraire un extrait du texte sur la page concernée
            description = ""
            try:
                page = self.doc[page_no - 1]
                page_text = page.get_text()
                # Chercher le titre sur la page pour extraire le texte subséquent
                idx = page_text.lower().find(title.lower()[:20])
                sub_text = page_text[idx:] if idx != -1 else page_text
                description = format_effect_method(sub_text)
            except Exception:
                pass

            if not description:
                description = f"Technique détaillée dans l'ouvrage (p. {page_no})."

            techniques.append({
                'nom': title,
                'description': description,
                'page_physique': page_no,
                'pdf_nom': self.filename,
                'pdf_reference': f"{self.filename}, p. {page_no}",
                'lien_pdf': f"{self.filename}#page={page_no}",
                'source': 'toc'
            })

        return techniques

    def _get_page_typography(self, page) -> tuple:
        """Calcule la taille de police médiane du corps de texte et extrait les blocs enrichis."""
        try:
            d = page.get_text('dict')
        except Exception:
            return 10.0, []

        sizes = []
        blocks = d.get('blocks', [])
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    txt = s.get('text', '').strip()
                    if len(txt) > 4:
                        sizes.append(round(s.get('size', 10), 1))

        body_size = Counter(sizes).most_common(1)[0][0] if sizes else 10.0
        return body_size, blocks

    def extract_techniques(self, start_page: int = 1, end_page: int = None, use_toc: bool = True) -> List[Dict]:
        """
        Extrait les techniques détectées entre start_page et end_page (1-indexé).
        Combine l'extraction par TOC (si disponible) et l'analyse typographique avancée (polices, tailles, bold).
        """
        # 1. Tenter d'abord l'extraction native par TOC si activée
        if use_toc and start_page == 1 and (end_page is None or end_page >= self.total_pages):
            toc_techniques = self.extract_from_toc()
            if len(toc_techniques) >= 5:
                return toc_techniques

        if end_page is None or end_page > self.total_pages:
            end_page = self.total_pages

        techniques = []
        seen_titles = set()

        for pno in range(start_page - 1, end_page):
            physical_page = pno + 1
            try:
                page = self.doc[pno]
                body_size, blocks = self._get_page_typography(page)
            except Exception:
                continue

            for b_idx, b in enumerate(blocks):
                lines = b.get('lines', [])
                if not lines:
                    continue

                for l_idx, l in enumerate(lines):
                    spans = l.get('spans', [])
                    line_text = " ".join(s.get('text', '').strip() for s in spans).strip()
                    if not line_text or len(line_text) < 4 or len(line_text) > 65:
                        continue

                    # Typographie : Détecter si gras (bit 16 ou 4 ou 'bold' dans le nom) ou taille supérieure
                    is_large = any(s.get('size', 0) >= body_size * 1.20 for s in spans)
                    is_bold = any(('bold' in s.get('font', '').lower() or (s.get('flags', 0) & 16) or (s.get('flags', 0) & 4)) for s in spans)
                    
                    # Un vrai titre de technique :
                    # - Commence par une majuscule ou un chiffre (ex: "1. The Pass")
                    # - Ne se termine pas par une ponctuation de phrase ordinaire
                    # - Est typographiquement mis en valeur (grand ou gras)
                    if not (line_text[0].isupper() or line_text[0].isdigit()):
                        continue
                    if line_text.endswith(('.', ',', ';', ':', '?', '!')) and not re.match(r'^\d+\.', line_text):
                        continue

                    # Éviter les lignes introductives du type "Effect : ...", "Method : ..."
                    if re.match(r'^(?:Effect|Effet|Method|Méthode|Routine|Working|Note|Remarks|Preparation|Chapter|Part)\s*[:\.]', line_text, re.IGNORECASE):
                        continue

                    is_candidate = is_large or (is_bold and len(line_text) <= 50)

                    # Ignorer noms d'auteurs ou mentions d'édition récurrentes
                    if any(auth in line_text.lower() for auth in ['richard kaufman', 'david roth', 'alan greenberg', 'written and illustrated']):
                        continue

                    if is_candidate:
                        # Regarder si la ligne suivante dans le même bloc est également un titre candidat à fusionner (ex: RETENTION + VANISH)
                        combined_title = line_text
                        if l_idx + 1 < len(lines):
                            next_spans = lines[l_idx + 1].get('spans', [])
                            next_text = " ".join(s.get('text', '').strip() for s in next_spans).strip()
                            next_is_large = any(s.get('size', 0) >= body_size * 1.20 for s in next_spans)
                            next_is_bold = any(('bold' in s.get('font', '').lower() or (s.get('flags', 0) & 16) or (s.get('flags', 0) & 4)) for s in next_spans)
                            if (next_is_large or next_is_bold) and next_text and next_text[0].isupper() and len(next_text) <= 30 and not next_text.endswith('.'):
                                combined_title = f"{line_text} {next_text}"

                        nom = clean_title(combined_title)
                        if not nom or nom.lower() in seen_titles:
                            continue

                        # Éviter les faux titres de 1 mot trop générique
                        if len(nom.split()) == 1 and nom.lower() in {'pass', 'magic', 'coin', 'coins', 'card', 'cards', 'trick', 'hands', 'part', 'table'}:
                            continue

                        seen_titles.add(nom.lower())


                        # Récupérer le contexte subséquent pour l'effet et la méthode
                        context_parts = []
                        # Reste des lignes du bloc courant
                        for rem_l in lines[l_idx + 1:]:
                            txt = " ".join(s.get('text', '').strip() for s in rem_l.get('spans', [])).strip()
                            if txt:
                                context_parts.append(txt)

                        # Blocs suivants sur la même page
                        for next_idx in range(b_idx + 1, min(b_idx + 5, len(blocks))):
                            nxt_b = blocks[next_idx]
                            for nxt_l in nxt_b.get('lines', []):
                                txt = " ".join(s.get('text', '').strip() for s in nxt_l.get('spans', [])).strip()
                                if txt:
                                    context_parts.append(txt)

                        raw_context = " ".join(context_parts)
                        # Amélioration 4 : Découpage [Effet] vs [Méthode]
                        structured_desc = format_effect_method(raw_context)
                        if not structured_desc:
                            structured_desc = f"Technique décrite dans l'ouvrage (p. {physical_page})."

                        techniques.append({
                            'nom': nom,
                            'description': structured_desc,
                            'page_physique': physical_page,
                            'pdf_nom': self.filename,
                            'pdf_reference': f"{self.filename}, p. {physical_page}",
                            'lien_pdf': f"{self.filename}#page={physical_page}",
                            'source': 'typography'
                        })

        return techniques

    def search_topic(self, topic_title: str, keywords: List[str] = None, definition_text: str = "") -> List[Dict]:
        """
        Recherche plein-texte ciblée d'un sujet (chapitre/section) dans le document PDF.
        Combine la recherche des mots-clés canoniques et la proximité lexicale de la définition.
        Retourne la liste des occurrences avec page physique réelle et extrait contextuel.
        """
        results = []
        if not keywords:
            keywords = []
        
        def_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', definition_text.lower())) if definition_text else set()

        for pno in range(self.total_pages):
            physical_page = pno + 1
            try:
                page = self.doc[pno]
                text = page.get_text("text")
                if not text or len(text.strip()) < 20:
                    continue
                
                text_lower = text.lower()
                matched_kw = []
                for kw in keywords:
                    pattern = rf'\b{re.escape(kw.lower())}\b'
                    if re.search(pattern, text_lower):
                        matched_kw.append(kw)

                if not matched_kw:
                    continue

                page_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', text_lower))
                def_overlap = len(page_words & def_words)

                first_match = matched_kw[0]
                idx = text_lower.find(first_match.lower())
                start_snippet = max(0, idx - 100)
                end_snippet = min(len(text), idx + 400)
                snippet = text[start_snippet:end_snippet].replace('\n', ' ').strip()
                cleaned_desc = format_effect_method(snippet) or f"Mention et étude de {first_match} (p. {physical_page})."

                results.append({
                    'nom': f"{topic_title} - {first_match.title()}",
                    'description': cleaned_desc,
                    'page_physique': physical_page,
                    'pdf_nom': self.filename,
                    'pdf_reference': f"{self.filename}, p. {physical_page}",
                    'lien_pdf': f"{self.filename}#page={physical_page}",
                    'matched_keywords': matched_kw,
                    'definition_score': def_overlap,
                    'source': 'targeted_search'
                })
            except Exception:
                continue

        return results

