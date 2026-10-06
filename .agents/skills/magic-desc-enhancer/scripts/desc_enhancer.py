import os
import sys
import re
import json

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.config import load_taxonomies, BASE_DIR
from shared.ocr_cleaner import clean_ocr_text

class MagicDescEnhancer:
    def __init__(self, taxonomy_file=None):
        self.taxonomies = load_taxonomies()

    def clean_raw_text(self, text: str) -> str:
        """Nettoie les artéfacts OCR, caractères de formule et coupures de mots."""
        if not text:
            return ""
        s = str(text).strip()
        # Élimination des caractères interdits en début de chaîne pour Excel
        while s and s[0] in ('=', '+', '-', '@', '«', '"', "'", '“', ' '):
            s = s[1:].strip()
        while s and s[-1] in ('»', '"', "'", '”', ' '):
            s = s[:-1].strip()

        # Nettoyage des résidus OCR courants
        s = re.sub(r'\b111e\b', 'The', s)
        s = re.sub(r'\b11e\b', 'He', s)
        s = re.sub(r'\bTbe\b', 'The', s)
        s = re.sub(r'\btbe\b', 'the', s)
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
        # Recollage des césures
        s = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', s)
        # Espaces multiples
        s = re.sub(r'\s{2,}', ' ', s)
        return s.strip()

    def _extract_from_markers(self, text: str) -> tuple:
        """Tente d'extraire les blocs Effet et Méthode à partir des marqueurs du texte."""
        cleaned = self.clean_raw_text(text)
        eff_match = re.search(r'(?i)\b(?:effect|effet|routine|the effect|l\'effet)\b\s*[:\.]?\s*', cleaned)
        met_match = re.search(r'(?i)\b(?:method|méthode|working|explication|secret|performance|the method)\b\s*[:\.]?\s*', cleaned)

        eff_text = ""
        met_text = ""

        if eff_match and met_match:
            if eff_match.start() < met_match.start():
                eff_text = cleaned[eff_match.end():met_match.start()].strip()
                met_text = cleaned[met_match.end():].strip()
            else:
                met_text = cleaned[met_match.end():eff_match.start()].strip()
                eff_text = cleaned[eff_match.end():].strip()
        elif eff_match:
            eff_text = cleaned[eff_match.end():].strip()
        elif met_match:
            met_text = cleaned[met_match.end():].strip()

        return eff_text, met_text

    def _get_category_archetype(self, book_id: str, partie: str, chapitre: str, section: str, nom: str) -> tuple:
        """Génère un archétype précis d'Effet et de Méthode selon la taxonomie officielle."""
        nom_lower = nom.lower()
        chap_lower = chapitre.lower()
        partie_lower = partie.lower()
        sec_lower = section.lower()

        # ================= CARTES =================
        if 'carte' in book_id:
            # 1. Contrôles & Sauts de coupe
            if 'saut de coupe' in sec_lower or 'pass' in nom_lower or 'shift' in nom_lower:
                return (
                    "Une carte librement choisie et replacée au centre du jeu semble définitivement perdue.",
                    f"Transposition secrète des deux moitiés du jeu ({nom}) ramenant la carte cible au sommet ou en dessous sans mouvement apparent."
                )
            if 'contrôle' in chap_lower or 'control' in nom_lower or 'break' in nom_lower or 'jog' in nom_lower:
                return (
                    "La carte sélectionnée est insérée au milieu du paquet qui est immédiatement rassemblé.",
                    f"Maintien discret de la position de la carte ({nom}) via une brisure secrète (break ou jog) pour un contrôle ultérieur."
                )
            # 2. Faux mélanges & Fausses coupes
            if 'faux mélange' in chap_lower or 'shuffle' in nom_lower:
                return (
                    "Le jeu de cartes est battu et mélangé de manière convaincante sous les yeux du spectateur.",
                    f"Simulation d'un brassage complet ({nom}) conservant l'ordre intégral ou un chapelet de cartes prédéterminé."
                )
            if 'fausse coupe' in chap_lower or 'cut' in nom_lower:
                return (
                    "Le paquet est coupé en plusieurs portions étalées sur la table puis réassemblé.",
                    f"Coupe en plusieurs temps ({nom}) créant l'illusion d'une séparation des cartes tout en conservant leur empilement d'origine."
                )
            # 3. Forçages
            if 'forçage' in chap_lower or 'force' in nom_lower:
                return (
                    "Le spectateur est invité à désigner ou arrêter une carte avec une liberté en apparence totale.",
                    f"Synchronisation gestuelle et psychologique ({nom}) forçant une carte cible prédéterminée par le magicien."
                )
            # 4. Empalmages & Dissimulations
            if 'empalmage' in chap_lower or 'palm' in nom_lower:
                return (
                    "Les mains du magicien semblent naturelles et vides alors qu'il manipule le jeu de cartes.",
                    f"Dissimulation secrète d'une ou plusieurs cartes dans la paume ({nom}) prête à être volée, chargée ou escamotée."
                )
            # 5. Changes & Levées Doubles
            if 'double lift' in nom_lower or 'levée double' in nom_lower:
                return (
                    "La carte supérieure du jeu est montrée clairement au public avant d'être retournée ou posée.",
                    f"Saisie coordonnée et manipulation indétectable de deux cartes comme une seule ({nom})."
                )
            if 'change' in chap_lower or 'change' in nom_lower:
                return (
                    "Une carte clairement visible se transmute instantanément en une autre carte au contact de la main.",
                    f"Permutation instantanée ({nom}) effectuée sous la couverture d'un geste naturel ou d'une mise au carré."
                )
            # 6. Fioritures & Esthétique
            if 'fioriture' in chap_lower or 'flourish' in nom_lower or 'fan' in nom_lower:
                return (
                    "Démonstration visuelle de virtuosité et d'élégance technique avec le jeu de cartes.",
                    f"Contrôle rythmé des pressions digitales ({nom}) pour créer un étalement, un éventail ou un ruban impeccable."
                )
            # Glide (Retrait de la carte du dessous)
            if 'glide' in nom_lower or 'glisse' in nom_lower:
                return (
                    "Le magicien montre la carte du dessous du jeu, puis la pose en apparence sur la table face cachée.",
                    f"Recul secret de la carte de face du bout des doigts ({nom}) permettant de distribuer en réalité la carte immédiatement au-dessus."
                )
            # Tenues & Fondamentaux
            if 'grip' in nom_lower or 'tenue' in nom_lower or 'fondamentaux' in chap_lower:
                return (
                    "Prise en main académique et naturelle du jeu de cartes face au public.",
                    f"Positionnement ergonomique des doigts ({nom}) préparant secrètement les angles et la mise en œuvre des passes."
                )
            # Donnes frauduleuses (Triche)
            if 'donne' in chap_lower or 'deal' in nom_lower:
                return (
                    "Le magicien distribue les cartes normalement autour de la table pour une démonstration de jeu.",
                    f"Donne frauduleuse indétectable ({nom}) permettant de distribuer la seconde carte, la carte du dessous ou du centre."
                )
            # Montages & Chapelets
            if 'montage' in chap_lower or 'stack' in nom_lower or 'chapelet' in nom_lower:
                return (
                    "Le jeu semble ordinaire et mélangé avant le début de l'expérience.",
                    f"Ordre préétabli ou mémorisé ({nom}) conférant au cartomane un avantage d'information total sur chaque tirage."
                )

        # ================= PIÈCES =================
        elif 'piece' in book_id:
            # Lapping & Sleeving
            if 'lapping' in chap_lower or 'lapping' in nom_lower or 'giron' in nom_lower:
                return (
                    "Une pièce posée sur le tapis de table disparaît net au passage naturel de la main.",
                    f"Glissement discret de la pièce sur le bord de table vers les genoux ({nom})."
                )
            if 'sleeving' in chap_lower or 'sleeving' in nom_lower or 'manche' in nom_lower:
                return (
                    "Évaporation visuelle instantanée d'une pièce au moment où la main effectue un geste en l'air.",
                    f"Propulsion secrète et silencieuse de la pièce à l'intérieur de la manche de veste ({nom})."
                )
            # Fioritures pièces
            if 'fioriture' in chap_lower or 'roll' in nom_lower or 'dextérité' in chap_lower:
                return (
                    "Démonstration de virtuosité et d'aisance digitale où la pièce danse entre les doigts.",
                    f"Roulement fluide de la tranche de la pièce ({nom}) sur les phalanges d'une seule main."
                )
            # 1. Empalmages (Cacher)
            if 'cacher' in chap_lower or 'palm' in nom_lower:
                return (
                    "La main du magicien paraît totalement détendue, vide et ouverte aux regards du public.",
                    f"Maintien secret de la pièce ({nom}) par pression anatomique invisible (empalmage classique, des doigts ou à l'italienne)."
                )
            # 2. Disparitions
            if 'disparaître' in chap_lower or 'vanish' in nom_lower or 'drop' in nom_lower:
                return (
                    "Une pièce tenue au bout des doigts s'évapore mystérieusement dans les airs dès que la main s'ouvre.",
                    f"Fausse prise coordonnée ({nom}) avec rétention visuelle, la pièce demeurant secrètement dans la main opposée."
                )
            # 3. Échanges
            if 'échanger' in chap_lower or 'switch' in nom_lower:
                return (
                    "Une pièce montrée distinctement se métamorphose en une autre pièce d'aspect ou de valeur différente.",
                    f"Substitution instantanée ({nom}) de la pièce visible par une pièce dissimulée lors d'un geste de transfert."
                )
            # 4. Apparitions
            if 'apparaître' in chap_lower or 'appear' in nom_lower or 'production' in nom_lower:
                return (
                    "Une pièce de monnaie solide se matérialise soudainement au bout des doigts dans l'espace vide.",
                    f"Dégagement secret et production fluide de la pièce préalablement empalmée ({nom})."
                )
            # 5. Transformations & Spellbound
            if 'transformer' in chap_lower or 'spellbound' in nom_lower:
                return (
                    "Une pièce de monnaie change visiblement de couleur ou de métal (cuivre en argent) au simple frottement de la main.",
                    f"Permutation visuelle dynamique ({nom}) exploitant un contact rapproché entre les deux paumes."
                )
            # 6. Gimmicks (Coquille, Flipper, etc.)
            if 'coquille' in chap_lower or 'shell' in nom_lower:
                return (
                    "Multiplication, disparition ou voyage instantané d'une pièce à travers la table.",
                    f"Utilisation de la coquille expansée ({nom}) pour imbriquer ou libérer la pièce à l'insu des spectateurs."
                )
            if 'pliante' in chap_lower or 'folding' in nom_lower:
                return (
                    "Une pièce solide pénètre visuellement dans une bouteille en verre au goulot trop étroit.",
                    f"Exploitation de la pièce pliante articulée ({nom}) permettant son passage temporaire dans l'ouverture étroite."
                )
            if 'boîte' in partie_lower or 'okito' in chap_lower or 'boston' in chap_lower:
                return (
                    "Des pièces enfermées dans une boîte métallique traversent la boîte ou la table de manière inexplicable.",
                    f"Manipulation secrète de la boîte à pièces ({nom}) exploitant un retournement subtil ou un compartiment truqué."
                )
            # 7. Routines de Tours de Pièces (Coins Across, Three Fly, Matrix, Flurry, Ramsay...)
            if 'voyage' in chap_lower or 'across' in nom_lower or 'three fly' in nom_lower or 'fly' in nom_lower:
                return (
                    "Plusieurs pièces voyagent invisiblement et une à une d'une main à l'autre ou dans la main du spectateur.",
                    f"Enchaînement coordonné de faux transferts et de chargements secrets ({nom}) maintenant une avance d'une pièce."
                )
            if 'matrice' in chap_lower or 'matrix' in nom_lower or 'chink' in nom_lower or 'assemblage' in chap_lower:
                return (
                    "Quatre pièces disposées aux quatre coins d'un tapis se rassemblent mystérieusement sous une seule carte ou sous la main.",
                    f"Routine d'assemblage méthodique ({nom}) dérobant et chargeant alternativement chaque pièce sous la couverture des gestes."
                )
            if 'traversée' in chap_lower or 'table' in nom_lower or 'through' in nom_lower:
                return (
                    "Des pièces posées sur le plateau de table traversent le bois massif pour être récupérées dans la main placée en dessous.",
                    f"Détournement d'attention et passe secrète de pénétration ({nom}) transférant les pièces sous le tapis à l'insu du public."
                )
            if 'flurry' in nom_lower or 'hanging' in nom_lower or 'avare' in chap_lower or 'miser' in nom_lower:
                return (
                    "Démonstration spectaculaire où les pièces apparaissent, disparaissent continuellement dans les airs ou culminent par une pièce géante.",
                    f"Enchaînement rythmé d'escamotages et d'empalmages multiples ({nom}) exploitant un rythme visuel soutenu."
                )
            if 'cylindre' in chap_lower or 'cylinder' in nom_lower:
                return (
                    "Quatre pièces voyagent mystérieusement sous un cylindre de cuir en remplaçant un bouchon de liège.",
                    f"Chef-d'œuvre de gestion d'attention ({nom}) combinant transferts secrets et charges sous le cylindre."
                )

        # ================= TOURS DE CARTES =================
        else:
            # 1. Tours automatiques
            if 'automatique' in chap_lower or 'self-working' in nom_lower or 'mathématique' in sec_lower:
                return (
                    "Le spectateur effectue lui-même toutes les distributions et coupes du jeu, aboutissant à une révélation impossible.",
                    f"Principe mathématique ou parité intrinsèque ({nom}) assurant le résultat sans aucune manipulation manuelle."
                )
            # 2. Tours avec gimmicks
            if 'gimmick' in partie_lower or 'truqué' in partie_lower or 'matériel' in partie_lower:
                return (
                    "Phénomène visuel inexplicable : cartes qui s'effacent, prédictions impossibles ou faces qui se dédoublent.",
                    f"Exploitation du matériel truqué ({nom}) dissimulé au sein du jeu pour produire l'illusion sans difficulté technique."
                )
            # 3. Petits paquets
            if 'petits paquets' in sec_lower or 'packet' in nom_lower:
                return (
                    "Une série de retournements et métamorphoses magiques se produit sur un petit groupe de cartes sélectionnées.",
                    f"Enchaînement de faux comptages et de subtilités d'exposition ({nom}) masquant les cartes indésirables."
                )
            # 4. Révélations & Sandwich
            if 'révélation' in sec_lower or 'sandwich' in sec_lower or 'ambitious' in nom_lower:
                return (
                    "La carte choisie est instantanément retrouvée ou capturée de manière spectaculaire entre deux cartes sentinelles.",
                    f"Contrôle préalable et décharge ciblée ({nom}) créant la surprise lors du déploiement des cartes."
                )

        # Repli par défaut soigné
        return (
            f"Illusion magique percutante et visuelle : {nom}.",
            f"Enchaînement technique structuré ({nom}) respectant les fondamentaux de {chapitre}."
        )

    def enhance_description(self, book_id: str, partie: str, chapitre: str, section: str, nom: str, current_desc: str) -> str:
        """
        Enrichit et standardise la description au format strict :
        [Effet] ... | [Méthode] ...
        """
        clean_desc = self.clean_raw_text(current_desc)
        
        # 1. Vérifier si un format bipartite [Effet] ... | [Méthode] existe déjà et est de bonne qualité
        if '[Effet]' in clean_desc and '[Méthode]' in clean_desc:
            parts = clean_desc.split('|')
            eff_part = parts[0].replace('[Effet]', '').strip()
            met_part = parts[1].replace('[Méthode]', '').strip() if len(parts) > 1 else ""

            # Si le contenu est substantiel (> 30 caractères) et non générique, on le nettoie et on le garde
            if len(eff_part) >= 25 and len(met_part) >= 20 and 'technique décrite' not in eff_part.lower():
                return f"[Effet] {eff_part} | [Méthode] {met_part}"

        # 2. Chercher des marqueurs explicites dans le texte OCR d'origine
        extracted_eff, extracted_met = self._extract_from_markers(clean_desc)
        if len(extracted_eff) >= 25 and len(extracted_met) >= 20:
            return f"[Effet] {extracted_eff[:220]} | [Méthode] {extracted_met[:220]}"

        # 3. Synthèse experte basée sur l'archétype magique et la taxonomie
        archetype_eff, archetype_met = self._get_category_archetype(book_id, partie, chapitre, section, nom)

        # Si l'extrait OCR contenait un détail descriptif concret exploitable, l'intégrer
        if len(clean_desc) >= 20 and 'technique décrite' not in clean_desc.lower() and 'relevant de' not in clean_desc.lower():
            # Supprimer le préambule répétitif "« Titre » :" ou "Titre :"
            snippet = re.sub(r'^[«"\'“]?\s*[^»"\'”:\.]{2,30}\s*[»"\'”]?\s*:\s*', '', clean_desc).strip()
            # Supprimer les guillemets et scories
            snippet = re.sub(r'[«»"\'”]', '', snippet).strip()
            if len(snippet) >= 15:
                snippet = snippet[:140].strip()
                if snippet.endswith('.'):
                    snippet = snippet[:-1]
                return f"[Effet] {archetype_eff} | [Méthode] {archetype_met} (Contexte source : {snippet})."

        return f"[Effet] {archetype_eff} | [Méthode] {archetype_met}"

    def enhance_title(self, raw_name: str, book_id: str, partie: str, chapitre: str, section: str, desc: str = "") -> str:
        """
        Clarifie et normalise le titre de la technique (Colonne 5) :
        - Élimine le bruit OCR et les caractères parasites
        - Corrige les inversions ('Title, The' -> 'The Title')
        - Traduit les phrases ou termes obscurs en français clair avec nom canonique
        - Préserve les titres déjà propres et intelligibles
        """
        s = self.clean_raw_text(raw_name)
        if not s:
            return "Technique Magique"

        # 1. Correction d'inversion : "Joker Spelling Routine, The" -> "The Joker Spelling Routine"
        inv_match = re.match(r'^(.*?),\s*(the|a|an|le|la|les|l\')\b', s, re.I)
        if inv_match:
            s = f"{inv_match.group(2)} {inv_match.group(1)}".strip()

        # Élimination des scories de début et de fin
        s = re.sub(r'^[«"\'“\s\-\.:;]+', '', s)
        s = re.sub(r'[»"\'”\s\-\.:;,]+$', '', s)
        s = re.sub(r'\s{2,}', ' ', s)

        s_lower = s.lower()

        # 2. Si le titre est déjà en bon français clair et concis, le sanctuariser
        french_starters = ['le ', 'la ', 'les ', 'un ', 'une ', 'des ', 'du ', 'saut de coupe', 'levée double', 'empalmage', 'contrôle', 'faux mélange', 'fausse coupe', 'donne', 'boîte okito', 'boîte boston']
        if any(s_lower.startswith(fs) or f" {fs}" in s_lower for fs in french_starters) and len(s) < 55 and not re.search(r'[a-z][A-Z]|[\(\)\[\]]{2,}', s):
            return s[0].upper() + s[1:]

        # 3. Dictionnaire canonique des termes magiques récurrents
        MAGIC_CANONICAL_TERMS = {
            # Pièces
            r'\bboston palm load\b': "Chargement en empalmage Boston (Boston Palm Load)",
            r'\bedge grip\b': "Tenue sur tranche (Edge Grip)",
            r'\bfinger palm\b': "Empalmage des doigts (Finger Palm)",
            r'\bclassic palm\b': "Empalmage classique (Classic Palm)",
            r'\bthumb palm\b': "Empalmage au pouce (Thumb Palm)",
            r'\bdowns palm\b': "Empalmage Downs (Downs Palm)",
            r'\bgoshman pinch\b': "Pincement Goshman (Goshman Pinch)",
            r'\bretention (?:pass|vanish)\b': "Disparition à rétention visuelle (Retention Vanish)",
            r'\bfrench drop\b': "Tourniquet / Disparition à la française (French Drop)",
            r'\bbobo switch\b': "Change de pièce Bobo (Bobo Switch)",
            r'\bclick pass\b': "Passe au son (Click Pass)",
            r'\bshuttle pass\b': "Passe navette (Shuttle Pass)",
            r'\bspellbound\b': "Change visuel Spellbound (Spellbound)",
            r'\bcoins across\b': "Voyage des pièces (Coins Across)",
            r'\bokito\b': "Boîte Okito",
            r'\bboston box\b': "Boîte Boston",
            r'\bexpanded shell\b': "Coquille expansée (Expanded Shell)",
            r'\bcopper\s*/?\s*silver\b': "Pièce Cuivre / Argent (Copper/Silver)",
            r'\bflipper coin\b': "Pièce pliante (Flipper Coin)",
            r'\bscotch and soda\b': "Scotch & Soda",
            r'\bchink-a-chink\b': "Matrice de pièces mains nues (Chink-a-Chink)",
            r'\bcoin matrix\b': "Matrice de pièces aux cartes (Coin Matrix)",

            # Cartes
            r'\bclassic pass\b': "Saut de coupe classique (Classic Pass)",
            r'\bherrmann pass\b': "Saut de coupe Herrmann (Herrmann Pass)",
            r'\bturnover pass\b': "Saut de coupe retourné (Turnover Pass)",
            r'\bspread pass\b': "Saut de coupe en étalement (Spread Pass)",
            r'\bside slip\b': "Glissement latéral (Side Slip)",
            r'\btilt\b': "Illusion de profondeur (Tilt)",
            r'\bdouble lift\b': "La Levée double (Double Lift)",
            r'\btop change\b': "Change par le dessus (Top Change)",
            r'\bbottom change\b': "Change par le dessous (Bottom Change)",
            r'\bglide\b': "Le Glissage (Glide)",
            r'\belmsley count\b': "Comptage Elmsley (Elmsley Count)",
            r'\bjordan count\b': "Comptage Jordan (Jordan Count)",
            r'\bhamman count\b': "Comptage Hamman (Hamman Count)",
            r'\bzarrow shuffle\b': "Faux mélange Zarrow (Zarrow Shuffle)",
            r'\bpush-through\b': "Faux mélange Push-Through",
            r'\bcharlier cut\b': "Coupe Charlier à une main (Charlier Cut)",
            r'\bclassic force\b': "Forçage classique (Classic Force)",
            r'\briffle force\b': "Forçage au Riffle (Riffle Force)",
            r'\bcross-cut force\b': "Forçage en croix (Cross-Cut Force)",
            r'\bbottom deal\b': "Donne du dessous (Bottom Deal)",
            r'\bsecond deal\b': "Donne en second (Second Deal)",
            r'\bcenter deal\b': "Donne du milieu (Center Deal)",
            r'\bcull\b': "Triage secret (Cull)",
            r'\berdnase shift\b': "S.W.E. Shift (Erdnase)",
            r'\bgambler\'?s cop\b': "Empalmage du tricheur (Gambler's Cop)",
            r'\bribbon spread\b': "Étalement en ruban (Ribbon Spread)",
            r'\bspring\b': "Le Ressort de cartes (Spring)",
            r'\bwaterfall\b': "La Cascade (Waterfall)",

            # Tours
            r'\bblank stripper\b': "Jeu biseauté à faces blanches (Blank Stripper)",
            r'\btransparency\b': "Routine Transparency (Boris Wild)",
            r'\bcard to pocket\b': "Carte à la poche (Card to Pocket)",
            r'\btriumph\b': "Le Triomphe (Triumph)",
            r'\boil and water\b': "L'Huile et l'Eau (Oil and Water)",
            r'\bcannibal cards\b': "Les Cartes Cannibales (Cannibal Cards)",
            r'\bambitious card\b': "La Carte Ambitieuse (Ambitious Card)",
            r'\bcard in lemon\b': "La Carte dans le citron (Card in Lemon)",
            r'\bout of this world\b': "Hors de ce monde (Out of This World)",
            r'\btwisting the aces\b': "Les As qui se retournent (Twisting the Aces)"
        }

        # 4. Formats spécifiques et manipulations expertes (Ordre du plus spécifique au plus général)
        if re.search(r'\bcover\s+for\s+the\s+ambitious\s+card\b', s_lower):
            return "Couverture de levée double (Carte Ambitieuse)"
        if re.search(r'\bestablishing\s+a\s+break\b', s_lower):
            return "Prise de brisure sur pont (Bridge Break)"
        if re.search(r'\btransfer\s+of\b.*\bbreak\b', s_lower):
            return "Transfert de brisure (Break Transfer)"
        if re.search(r'\bdouble\s+lift\s+turnover\b', s_lower):
            return "Levée double avec retournement (Double Lift Turnover)"
        if re.match(r'^(the\s+|a\s+)?double\s+lift\b', s_lower) and len(s.split()) <= 4:
            return "La Levée double (Double Lift)"
        if re.search(r'\bthumb[-\s]?count\b', s_lower):
            return "Comptage au pouce (Thumb Count)"
        if re.search(r'\bpinky[-\s]?count\b', s_lower):
            return "Comptage à l'auriculaire (Pinky Count)"
        if re.search(r'\bholding\s+a\s+break\b', s_lower):
            return "Maintien d'une brisure discrète (Pinky Break)"
        if re.search(r'\bform\s+a\s+break\s+under\b', s_lower):
            return "Contrôle par brisure sous l'injog (Injog Break)"
        if re.search(r'\bgrip\s+the\s+entire\s+pack\b', s_lower):
            return "Prise en main complète du jeu (Mechanic's Grip)"
        if re.search(r'\ba\s+new\s+glide\b', s_lower):
            return "Le Glissage moderne (New Glide)"
        if re.match(r'^(the\s+|a\s+)?glide$', s_lower) or s_lower == 'glide':
            return "Le Glissage classique (The Glide)"
        if re.search(r'\bthe\s+jokers\s+are\s+in\s+the\s+card\s+case\b', s_lower):
            return "Les Jokers dans l'étui (Card Case Jokers)"
        if re.search(r'\bthe\s+joker\s+spell', s_lower):
            return "L'Épellation du Joker (Joker Spelling Routine)"

        # 5. Vérification directe des termes canoniques
        for pattern, replacement in MAGIC_CANONICAL_TERMS.items():
            if re.search(pattern, s_lower):
                if len(s.split()) <= 5:
                    return replacement

        # Détection de verbes d'action anglais débutants
        if re.match(r'^to\s+([a-z\s]+)$', s_lower):
            action_term = re.match(r'^to\s+([a-z\s]+)$', s_lower).group(1).strip()
            for pattern, replacement in MAGIC_CANONICAL_TERMS.items():
                if re.search(pattern, action_term):
                    return replacement
            return f"Technique de {action_term.capitalize()}"

        # 6. Réparation de bruit OCR flagrant
        if 'finges-palm' in s_lower or 'finger palm' in s_lower:
            return "Empalmage des doigts (Finger Palm)"
        if 'chum palm' in s_lower or 'thumb palm' in s_lower:
            return "Empalmage au pouce (Thumb Palm)"
        if 'right-bind' in s_lower or 'palm down' in s_lower:
            return "Dépôt secret en main droite (Secret Drop)"

        # 7. Élimination des prépositions orphelines en fin de chaîne
        s = re.sub(r'\s+(?:to|the|of|and|in|on|with|for|a|an|from|by|at)\s*$', '', s, flags=re.I)

        return s[0].upper() + s[1:]
