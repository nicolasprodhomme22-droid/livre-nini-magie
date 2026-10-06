import re

OCR_REPLACEMENTS = [
    (r'\b111e\b', 'The'),
    (r'\b11e\b', 'He'),
    (r'\bTbe\b', 'The'),
    (r'\btbe\b', 'the'),
    (r'[\u2018\u2019`´]', "'"),
    (r'[\u201c\u201d]', '"'),
    (r'\xa0', ' '),
]

BOILERPLATE_PATTERNS = [
    r'Next\s*\|\s*Previous\s*\|\s*(?:Chapter\s*Contents|Main\s*Contents|Contents)',
    r'Chapter\s*Contents\s*\|\s*Main\s*Contents',
    r'J\.B\.\s*Bobo\'s\s+Modern\s*Coin\s*Magic',
    r'The\s*Royal\s*Road\s*to\s*Card\s*Magic',
    r'Jean\s*Hugard\s*and\s*Frederick\s*Braue',
    r'Roberto\s*Giobbi\s*-\s*Cours\s*De\s*Cartomagie\s*Moderne',
]

def clean_ocr_text(text: str) -> str:
    """Nettoie le bruit OCR et les artéfacts courants."""
    if not text:
        return ""
    
    # Remplacement des motifs connus
    for pattern, repl in OCR_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
        
    # Suppression des lignes d'en-tête / pied de page répétitives
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        is_boilerplate = False
        for bp in BOILERPLATE_PATTERNS:
            if re.search(bp, stripped, re.IGNORECASE):
                is_boilerplate = True
                break
        if not is_boilerplate:
            cleaned_lines.append(stripped)
            
    content = " ".join(cleaned_lines)
    # Suppression des césures (ex: "tech- nique" -> "technique")
    content = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', content)
    # Rétablissement des apostrophes collées
    content = re.sub(r'\s+([\'’])\s+', r'\1', content)
    # Espaces multiples
    content = re.sub(r'\s{2,}', ' ', content)
    
    return content.strip()

STOP_WORDS_TITLES = {
    'contents', 'table of contents', 'sommaire', 'foreword', 'preface', 'introduction',
    'copyright', 'acknowledgements', 'enter book', 'advertisement', 'index', 'dedication',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
    'section one', 'section two', 'section three', 'chapter', 'part one', 'part two',
    'page', 'bibliography', 'appendix', 'glossary', 'back', 'next', 'previous'
}

NOISE_PATTERNS = [
    r'^(?:chapter|chapitre)\s+[ivxlcdm0-9]+.*$',
    r'^(?:part|partie)\s+[ivxlcdm0-9]+.*$',
    r'^(?:page\s+\d+|\d+)$',
    r'^(?:figure|fig\.|illustration|illust\.)\b.*$',
    r'^[_\-\=\*\.\s]{2,}$',
    r'^[0-9\W]+$',
]

def is_noise(nom: str) -> bool:
    """Détecte les résidus OCR, bribes et faux positifs."""
    if not nom or not str(nom).strip():
        return True
    clean = str(nom).strip()
    clean_lower = clean.lower()

    if len(clean) < 4 and clean_lower not in ['c/s', 'jog', 'cut', 'fan']:
        return True

    if clean_lower in STOP_WORDS_TITLES:
        return True

    for pat in NOISE_PATTERNS:
        if re.search(pat, clean, re.IGNORECASE):
            return True

    # Ratio de symboles anormaux
    symbol_ratio = len(re.findall(r'[^a-zA-Z0-9\sàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]', clean)) / max(len(clean), 1)
    if symbol_ratio > 0.35 and len(clean) > 5:
        return True

    # Détection de bribes OCR tronquées ou corrompues
    if any(garbage in clean_lower for garbage in ['che-coin', 'chraepe', 'iapubis', 'mpparencly', 'rabbic', 'blew che', 'e ain weno']):
        return True

    if clean[0].islower() and ('fig' in clean_lower or len(clean) > 40):
        return True

    return False

def clean_title(title: str) -> str:
    """Nettoie un titre de technique ou tour."""
    if not title:
        return ""
    title = clean_ocr_text(title)
    
    # Normalisation des titres à lettres espacées (ex: "V A N I S H" -> "VANISH")
    if re.match(r'^[A-ZÀ-ÿ](\s+[A-ZÀ-ÿ]){2,}$', title):
        title = "".join(title.split())

    if is_noise(title):
        return ""

    return title.strip()

def format_effect_method(text: str) -> str:
    """Structure la description en [Effet] et [Méthode] si les marqueurs sont présents."""
    cleaned = clean_ocr_text(text)
    if not cleaned:
        return ""

    effect_pat = r'(?i)\b(?:effect|effet|the effect|l\'effet|routine)\s*(?:\([a-z0-9]+\))?\s*[:\.]?\s*'
    method_pat = r'(?i)\b(?:method|m[ée]thode|working|explication|the method|modus operandi|secret|performance|pr[ée]paration)\s*(?:\([a-z0-9]+\))?\s*[:\.]?\s*'

    m_eff = re.search(effect_pat, cleaned)
    m_met = re.search(method_pat, cleaned)

    if m_eff and m_met:
        # Les deux marqueurs sont présents
        if m_eff.start() < m_met.start():
            eff_text = cleaned[m_eff.end():m_met.start()].strip()
            met_text = cleaned[m_met.end():].strip()
        else:
            met_text = cleaned[m_met.end():m_eff.start()].strip()
            eff_text = cleaned[m_eff.end():].strip()
            
        eff_text = eff_text[:250].strip()
        met_text = met_text[:250].strip()
        return f"[Effet] {eff_text} | [Méthode] {met_text}".strip()
    elif m_eff:
        eff_text = cleaned[m_eff.end():].strip()[:400]
        return f"[Effet] {eff_text}".strip()
    elif m_met:
        met_text = cleaned[m_met.end():].strip()[:400]
        return f"[Méthode] {met_text}".strip()

    # Si aucun marqueur formel, limiter à 400 caractères
    return cleaned[:400].strip()

