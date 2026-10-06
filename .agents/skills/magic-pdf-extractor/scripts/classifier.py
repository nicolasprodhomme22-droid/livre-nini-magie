import json
import os
import sys
import re
from typing import Tuple, Dict, List

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.config import load_taxonomies, TAXONOMY_PATH

# Thésaurus magique bilingue expert enrichi (termes techniques, anglicismes et français)
THESAURUS = {
    # --- TECHNIQUES PIÈCES ---
    'pieces': [
        # (Keywords Regex, Partie, Chapitre, Section, Score)
        (r'\b(?:classic palm|finger palm|thumb palm|edge palm|edge grip|downs palm|back palm|tenkai|finger clip|galea|nowhere palm|empalmage|cacher|tenue|hold|concealment)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 1 : Cacher', 'Général', 12),
        (r'\b(?:french drop|tourniquet|vanish|disparition|pinch vanish|retention vanish|retention pass|snap vanish|click vanish|pass vanish)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 2 : Faire disparaître', 'Général', 12),
        (r'\b(?:switch|bobo switch|roth switch|shuttle pass|échange|troc|substitut|fingertip pass)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 3 : Échanger', 'Général', 12),
        (r'\b(?:production|appear|apparition|produire|miser\'s dream|rêve de l\'avare|aerial catch)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 4 : Faire apparaître', 'Général', 12),
        (r'\b(?:spellbound|transformer|transformation|transposition|changement de métal|silver extraction)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 5 : Transformer', 'Général', 12),
        (r'\b(?:load|charge|charger|chargement|body load|pocket load)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 6 : Charger', 'Général', 12),
        (r'\b(?:steal|vol|voler|dérober|pocket steal|jacket steal)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 7 : Voler', 'Général', 12),
        (r'\b(?:click pass|tromper|bruit de pièce|auditory illusion|sound subtlety)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 8 : Tromper', 'Général', 12),
        (r'\b(?:lapping|sleeving|manche|giron|au giron|dans la manche)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 9 : Lapping & Sleeving', 'Général', 12),
        (r'\b(?:flourish|coin roll|steeplechase|fioriture|dextérité|jonglage|coin star|roll down|arm roll)\b',
         'PARTIE 1 : PIÈCES NORMALES', 'Chapitre 10 : Fioritures & Dextérité', 'Général', 12),
        # Pièces Truquées
        (r'\b(?:expanded shell|shell|coquille|coquille expansée|coquille ajustée)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 1 : La Coquille Expansée', 'Général', 15),
        (r'\b(?:copper\s*/\s*silver|copper silver|cuivre\s*/\s*argent|c/s coin)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 2 : La Pièce Cuivre / Argent', 'Général', 15),
        (r'\b(?:folding coin|pliante|pièce pliante|folding half|folding quarter)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 3 : La Pièce Pliante', 'Général', 15),
        (r'\b(?:flipper|flipper coin|pièce flipper)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 4 : La Flipper Coin', 'Général', 15),
        (r'\b(?:magnetic|magnétique|aimant|aimantée|steel core|raven)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 5 : Les Pièces Magnétiques et Aimantées', 'Général', 15),
        (r'\b(?:scotch\s*&\s*soda|sun\s*&\s*moon|scotch and soda|sun and moon)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 6 : Scotch & Soda et Sun & Moon', 'Général', 15),
        (r'\b(?:copper silver brass|csb|c/s/b|centavo)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 7 : Copper / Silver / Brass', 'Général', 15),
        (r'\b(?:double face|double pile|double head|double tail|two headed)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 8 : Pièces Double Face et Double Pile', 'Général', 15),
        (r'\b(?:bite coin|bitten coin|mordue|pièce trouée|chiseled)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 9 : Pièces Trouées et Pièces Mordues', 'Général', 15),
        (r'\b(?:hook coin|crochet|pièce à crochet)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 10 : Pièces à Crochet', 'Général', 15),
        (r'\b(?:tuc|triple tuc|tango ultimate)\b',
         'PARTIE 2 : PIÈCES TRUQUÉES', 'Chapitre 11 : Pièce TUC et Triple TUC', 'Général', 15),
        # Boîtes à Pièces
        (r'\b(?:okito|boîte okito|okito box)\b',
         'PARTIE 3 : BOÎTES À PIÈCES', 'Chapitre 1 : La Boîte Okito', 'Général', 15),
        (r'\b(?:boston|boîte boston|boston box)\b',
         'PARTIE 3 : BOÎTES À PIÈCES', 'Chapitre 2 : La Boîte Boston', 'Général', 15),
        (r'\b(?:duvivier|duvivier coin box|boîte duvivier)\b',
         'PARTIE 3 : BOÎTES À PIÈCES', 'Chapitre 3 : La Duvivier Coin Box', 'Général', 15),
    ],

    # --- TECHNIQUES CARTES ---
    'cartes': [
        (r'\b(?:grip|tenue du jeu|mechanic\'s grip|biddle grip|fondamentaux|posture|biddle)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 1 : Les Fondamentaux', 'Général', 10),
        (r'\b(?:classic pass|herrmann pass|turnover pass|spread pass|saut de coupe|pass|shift)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 2 : Les Contrôles', 'Section 1 : Saut de coupe', 15),
        (r'\b(?:control|contrôle|injog|outjog|side slip|tilt|break|jog|crimp|key card|carte clef)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 2 : Les Contrôles', 'Section 2 : Autres contrôles', 12),
        (r'\b(?:false shuffle|faux mélange|zarrow|push through|triumph shuffle|overhand shuffle|riffle shuffle)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 3 : Faux Mélange et Fausse Coupe', 'Section 1 : Faux mélange total', 12),
        (r'\b(?:false cut|fausse coupe|charlier cut|running cut|triple cut|fausse coupe totale)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 3 : Faux Mélange et Fausse Coupe', 'Section 3 : Fausse coupe totale', 12),
        (r'\b(?:force|forçage|classic force|riffle force|cross cut force|countdown force)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 4 : Les Forçages', 'Général', 15),
        (r'\b(?:palm|empalmage|top palm|bottom palm|diagonal palm|gambler\'s cop|dissimulation)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 5 : Empalmages et Dissimulations', 'Général', 15),
        (r'\b(?:double lift|levée double|top change|bottom change|glide|elmsley|jordan|hamman|count|comptage|change)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 6 : Changes et Faux Comptages', 'Général', 12),
        (r'\b(?:flourish|fioriture|cascade|ruban|fan|éventail|spring|dribble|waterfall|pirouette)\b',
         'PARTIE 1 : TECHNIQUES DE MAGIE', 'Chapitre 7 : Fioritures et Esthétique', 'Général', 12),
        # Triche
        (r'\b(?:second deal|bottom deal|center deal|greek deal|donne|donnes|donne en second|donne du dessous)\b',
         'PARTIE 2 : TECHNIQUES DU TRICHEUR', 'Chapitre 2 : Les Donnes Frauduleuses', 'Général', 15),
        (r'\b(?:stack|montage|cull|classement|charlier shuffle|stocking)\b',
         'PARTIE 2 : TECHNIQUES DU TRICHEUR', 'Chapitre 3 : Montages et Classements', 'Général', 12),
        (r'\b(?:crimp|daub|punch|peeker|repérage|marque tactile|ombre)\b',
         'PARTIE 2 : TECHNIQUES DU TRICHEUR', 'Chapitre 6 : Repérages et Marques Tactiles', 'Général', 12),
        # Jeux et cartes truqués
        (r'\b(?:stripper|biseauté|jeu biseauté)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 1 : Les Jeux Biseautés', 'Général', 15),
        (r'\b(?:marked deck|marqué|jeu marqué|marquage)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 2 : Les Jeux Marqués', 'Général', 15),
        (r'\b(?:forcing deck|forçage à 1 voie|forçage à 2 voies|jeu à forcer)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 3 : Les Jeux à Forçage', 'Général', 15),
        (r'\b(?:svengali|mirage|rough and smooth|mene tekel|rugueux)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 4 : Les Jeux à Principe', 'Général', 15),
        (r'\b(?:gaff|carte truquée|double dos|double face|carte courte|thick card)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 5 : Cartes Truquées à l\'Unité', 'Général', 15),
        (r'\b(?:key card|carte clef|carte repère)\b',
         'PARTIE 3 : CARTES ET JEUX TRUQUÉS', 'Chapitre 6 : Cartes Clefs', 'Général', 15),
    ],

    # --- TOURS DE CARTES ---
    'tours': [
        (r'\b(?:double back|double dos)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 1 : Cartes Gaffes à l\'Unité', 'Section 1 : Cartes Double Dos & Double Dos Couleur', 15),
        (r'\b(?:double face|double-faced)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 1 : Cartes Gaffes à l\'Unité', 'Section 2 : Cartes Double Face', 15),
        (r'\b(?:blank card|carte blanche|blank face|blank deck)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 1 : Cartes Gaffes à l\'Unité', 'Section 3 : Cartes Blanches', 15),
        (r'\b(?:stripper deck|jeu biseauté)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 2 : Les Jeux Truqués Classiques', 'Section 1 : Le Jeu Biseauté (Stripper Deck)', 15),
        (r'\b(?:marked deck|jeu marqué|marked cards)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 2 : Les Jeux Truqués Classiques', 'Section 2 : Le Jeu Marqué', 15),
        (r'\b(?:invisible deck|jeu invisible|ultra mental)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 2 : Les Jeux Truqués Classiques', 'Section 3 : Le Jeu Invisible', 15),
        (r'\b(?:svengali|mirage deck)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 2 : Les Jeux Truqués Classiques', 'Section 4 : Le Svengali et Mirage Deck', 15),
        (r'\b(?:esp deck|symboles esp|rhine)\b',
         'PARTIE 1 : TOURS AVEC MATÉRIEL TRUQUÉ (Gimmicks)', 'Chapitre 2 : Les Jeux Truqués Classiques', 'Section 5 : Le ESP Deck', 15),
        # Tours automatiques
        (r'\b(?:out of this world|coïncidence|prédiction|curry|mentalism)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 1 : Tours Automatiques (Sans manipulation)', 'Section 3 : Prédictions et Coïncidences (Out of this World...)', 15),
        (r'\b(?:mathématique|automatique|self-working|21 card trick|horloge|clock trick)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 1 : Tours Automatiques (Sans manipulation)', 'Section 1 : Tours Mathématiques et Épellations', 15),
        # Tours avec manipulation
        (r'\b(?:packet trick|twisting the aces|petits paquets|elmsley|oil and water|huile et eau)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 2 : Tours avec Manipulation', 'Section 1 : Magie de Petits Paquets (Twisting the aces...)', 15),
        (r'\b(?:sandwich|révélation|ambitious card|carte ambitieuse|as|aces|assembly)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 2 : Tours avec Manipulation', 'Section 2 : Révélations et Sandwichs', 15),
        (r'\b(?:transposition|voyageuse|cannibale|cards across|voyage|card to pocket)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 2 : Tours avec Manipulation', 'Section 3 : Transpositions et Cartes Voyageuses', 15),
        (r'\b(?:three card monte|bonneteau|triche|gambling demonstration)\b',
         'PARTIE 2 : TOURS AVEC UN JEU NORMAL (Non truqué)', 'Chapitre 2 : Tours avec Manipulation', 'Section 4 : Démonstrations de Triche et Bonneteau', 15),
    ],

    # --- TOURS DE PIÈCES ---
    'tours_pieces': [
        # Voyages
        (r'\b(?:three fly|retro fly|fingertip coins across)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 1 : Voyages de Pièces (Coins Across & Déplacements)', 'Section 2 : Three Fly', 18),
        (r'\b(?:winged silver|downs coins across|edge grip coins across)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 1 : Voyages de Pièces (Coins Across & Déplacements)', 'Section 3 : Winged Silver & Déplacements aériens', 18),
        (r'\b(?:coins across|flying coins|jumping coins|voyage de pièces|across)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 1 : Voyages de Pièces (Coins Across & Déplacements)', 'Section 1 : Coins Across classiques', 15),
        # Matrices
        (r'\b(?:chink-a-chink|chink a chink|bare handed|shadow coins|mains nues)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 2 : Matrices et Assemblages (Coin Assemblies)', 'Section 3 : Chink-a-Chink', 18),
        (r'\b(?:reverse matrix|backfire matrix|instant return|matrice inversée)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 2 : Matrices et Assemblages (Coin Assemblies)', 'Section 2 : Reverse Matrix', 18),
        (r'\b(?:matrix|matrice|assembly|assemblage|four coins to one)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 2 : Matrices et Assemblages (Coin Assemblies)', 'Section 1 : Matrix classique', 15),
        # Métamorphoses
        (r'\b(?:spellbound|continuous spellbound|ultimate silver extraction)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 3 : Métamorphoses et Changements Visuels', 'Section 1 : Routines de Spellbound', 18),
        (r'\b(?:wild coin|twilight zone|pièce sauvage)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 3 : Métamorphoses et Changements Visuels', 'Section 2 : Wild Coin', 18),
        (r'\b(?:copper / silver|copper/silver|cuivre / argent|digital copper|tabled copper)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 3 : Métamorphoses et Changements Visuels', 'Section 3 : Transpositions Cuivre / Argent impromptues', 15),
        # Traversées
        (r'\b(?:coins through the table|through table|à travers la table)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 4 : Traversées et Pénétrations Physiques', 'Section 1 : Pièces à travers la table', 18),
        (r'\b(?:coins through silk|through handkerchief|through card|à travers foulard|à travers tissu)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 4 : Traversées et Pénétrations Physiques', 'Section 2 : Pièces à travers un foulard, tissu ou carte', 18),
        (r'\b(?:coins through hand|through fist|à travers la main)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 4 : Traversées et Pénétrations Physiques', 'Section 3 : Pièces à travers la main', 18),
        # Productions, Flurry & Solo
        (r'\b(?:flurry|one coin routine|routine à une pièce|jumbo coin)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 5 : Productions, Flurry et Routines Solo', 'Section 1 : One Coin Routine & Flurry', 18),
        (r'\b(?:hanging coins|original hanging|roth hanging|pièces suspendues)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 5 : Productions, Flurry et Routines Solo', 'Section 2 : Hanging Coins', 18),
        (r'\b(?:miser\'s dream|aerial treasury|rêve de l\'avare|seau aux pièces)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 5 : Productions, Flurry et Routines Solo', 'Section 3 : Le Rêve de l\'Avare', 18),
        # Accessoires combinés
        (r'\b(?:cylinder and coins|ramsay|cylindre et pièces)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 6 : Pièces et Accessoires Combinés', 'Section 1 : Le Cylindre et les Pièces', 18),
        (r'\b(?:voodoo revelation|coin to card|cards and coins|pièces et cartes)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 6 : Pièces et Accessoires Combinés', 'Section 2 : Routines Pièces et Cartes combinées', 18),
        (r'\b(?:wand and coin|poker chip|chips|jetons|baguette)\b',
         'PARTIE 1 : TOURS AVEC PIÈCES NORMALES', 'Chapitre 6 : Pièces et Accessoires Combinés', 'Section 3 : Routines Pièces et Baguette, Gobelet ou Jetons de Poker', 15),
        # Pièces truquées
        (r'\b(?:shell|coquille|expanded shell)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 1 : Routines avec Coquille Expansée (Expanded Shell)', 'Section 2 : Voyages et matrices sous coquille', 16),
        (r'\b(?:scotch & soda|sun & moon|scotch and soda|sun and moon)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 2 : Transpositions et Sets Gimmickés Classiques', 'Section 2 : Scotch & Soda / Sun & Moon', 18),
        (r'\b(?:copper silver brass|csb|c\.s\.b\.)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 2 : Transpositions et Sets Gimmickés Classiques', 'Section 3 : Copper / Silver / Brass (C.S.B.)', 18),
        (r'\b(?:hopping half|hopping halves)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 2 : Transpositions et Sets Gimmickés Classiques', 'Section 4 : Hopping Halves & Sets multi-effets', 18),
        (r'\b(?:gaffed copper|copper/silver routine|cuivre argent truqué)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 2 : Transpositions et Sets Gimmickés Classiques', 'Section 1 : Cuivre / Argent truqué', 16),
        (r'\b(?:folding coin|coin in bottle|pièce pliante|bouteille)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 3 : Pièces Mécaniques et Spéciales', 'Section 1 : Pièce Pliante (Folding Coin / Pièce dans la bouteille)', 18),
        (r'\b(?:flipper|flipper coin|pièce flipper)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 3 : Pièces Mécaniques et Spéciales', 'Section 2 : Flipper Coin (pièce à clapet)', 18),
        (r'\b(?:magnetic|magnétique|aimant|raven)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 3 : Pièces Mécaniques et Spéciales', 'Section 3 : Pièces Magnétiques et Aimantées', 18),
        (r'\b(?:tuc|triple tuc|tango ultimate)\b',
         'PARTIE 2 : TOURS AVEC PIÈCES TRUQUÉES', 'Chapitre 3 : Pièces Mécaniques et Spéciales', 'Section 4 : Pièce TUC et Sets de précision moderne', 18),
        # Boîtes à pièces
        (r'\b(?:okito through table|okito table|okito box|boîte okito|okito)\b',
         'PARTIE 3 : TOURS AVEC BOÎTES À PIÈCES', 'Chapitre 1 : Routines de Boîte Okito', 'Section 1 : Traversées de boîte et de table', 16),
        (r'\b(?:boston|boston box|boîte boston)\b',
         'PARTIE 3 : TOURS AVEC BOÎTES À PIÈCES', 'Chapitre 2 : Routines de Boîte Boston', 'Section 1 : Pénétrations visuelles boîte fermée', 16),
        (r'\b(?:slot box|plug box)\b',
         'PARTIE 3 : TOURS AVEC BOÎTES À PIÈCES', 'Chapitre 3 : Boîtes Spéciales et Hybrides', 'Section 1 : Boîtes à encoche et bouchon (Slot Box & Plug Box)', 18),
        (r'\b(?:duvivier|duvivier coin box|boîte duvivier)\b',
         'PARTIE 3 : TOURS AVEC BOÎTES À PIÈCES', 'Chapitre 3 : Boîtes Spéciales et Hybrides', 'Section 2 : Boîte Duvivier (Duvivier Coin Box)', 18),
        (r'\b(?:nest of boxes|nest of coin boxes|nid de boîtes)\b',
         'PARTIE 3 : TOURS AVEC BOÎTES À PIÈCES', 'Chapitre 3 : Boîtes Spéciales et Hybrides', 'Section 3 : Nids de Boîtes (Nest of Boxes / Nest of Purses)', 18),
    ]
}

# Pré-compilation du thésaurus expert pour éliminer la recompilation dynamique
COMPILED_THESAURUS = {
    cat: [
        (re.compile(pattern, re.IGNORECASE), partie, chap, sec, weight)
        for pattern, partie, chap, sec, weight in rules
    ]
    for cat, rules in THESAURUS.items()
}

class MagicClassifier:
    def __init__(self, taxonomy_file=None):
        self.taxonomies = load_taxonomies()
        self.precompiled_tax = {}
        if self.taxonomies:
            self._precompile_taxonomies()

    def _precompile_taxonomies(self):
        """Pré-compile les expressions régulières et ensembles de mots-clés de la taxonomie."""
        tax_key_map = {
            'cartes': 'livre_cartes_techniques',
            'pieces': 'livre_pieces_techniques',
            'tours': 'livre_tours_cartes',
            'tours_pieces': 'livre_tours_pieces',
        }
        for book_cat, tax_book_key in tax_key_map.items():
            book_tax = self.taxonomies.get(tax_book_key, {})
            structure = book_tax.get('structure', [])

            nodes = []
            for partie in structure:
                p_name = partie.get('titre', '')
                for chap in partie.get('chapitres', []):
                    c_name = chap.get('titre', '')
                    c_def = chap.get('definition', '').lower()
                    c_kw = [kw.lower() for kw in chap.get('mots_cles', [])]

                    sections = chap.get('sections', [])
                    if not sections:
                        sections = [{'titre': 'Général', 'definition': '', 'mots_cles': []}]

                    for sec in sections:
                        s_name = sec.get('titre', '')
                        s_def = sec.get('definition', '').lower()
                        s_kw = [kw.lower() for kw in sec.get('mots_cles', [])]

                        all_kw = list(set(c_kw + s_kw))
                        all_def = f"{c_def} {s_def}".strip()
                        def_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', all_def))
                        title_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', f"{c_name} {s_name}".lower()))

                        kw_compiled = [
                            re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE)
                            for kw in all_kw if kw
                        ]

                        nodes.append({
                            'candidate': (p_name, c_name, s_name),
                            'kw_patterns': kw_compiled,
                            'def_words': def_words,
                            'title_words': title_words
                        })

            self.precompiled_tax[book_cat] = {
                'structure': structure,
                'nodes': nodes
            }

    def _normalize_key(self, book_key: str) -> str:
        """Normalise la clé de livre (cartes, pieces, tours, tours_pieces)."""
        k = book_key.lower()
        if ('tour' in k or 'routine' in k) and ('piece' in k or 'pièce' in k):
            return 'tours_pieces'
        if 'piece' in k:
            return 'pieces'
        elif 'tour' in k:
            return 'tours'
        return 'cartes'

    def classify_technique(self, book_key: str, title: str, description: str = "") -> Tuple[str, str, str]:
        """
        Détermine sémantiquement la Partie, le Chapitre et la Section appropriés.
        Combine avec performance :
        1. L'analyse directe de la taxonomie (Définitions conceptuelles + Mots-clés précompilés)
        2. Le matching de thésaurus magique expert précompilé
        3. Le repli structuré par défaut
        """
        normalized_cat = self._normalize_key(book_key)
        corpus = f"{title} {description}".lower()
        title_lower = title.lower()
        corpus_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', corpus))

        tax_data = self.precompiled_tax.get(normalized_cat, {})
        nodes = tax_data.get('nodes', [])
        structure = tax_data.get('structure', [])

        best_candidate = None
        best_score = 0

        # --- ÉTAPE 1 : Scoring par Définition & Mots-clés précompilés ---
        for node in nodes:
            score = 0
            for pat in node['kw_patterns']:
                if pat.search(title_lower):
                    score += 35
                elif pat.search(corpus):
                    score += 20

            # Similarité de vocabulaire avec la définition
            if node['def_words']:
                score += len(corpus_words & node['def_words']) * 3

            # Similarité avec les intitulés de chapitres/sections
            if node['title_words']:
                score += len(corpus_words & node['title_words']) * 4

            if score > best_score:
                best_score = score
                best_candidate = node['candidate']

        if best_candidate and best_score >= 20:
            final_p, final_c, final_s = best_candidate
            final_s = self.enforce_section_rule(normalized_cat, final_p, final_c, final_s, title, description)
            return (final_p, final_c, final_s)

        # --- ÉTAPE 2 : Repli sur le Thésaurus Expert précompilé ---
        thesaurus_rules = COMPILED_THESAURUS.get(normalized_cat, [])
        for pat, partie, chap, sec, weight in thesaurus_rules:
            matches = len(pat.findall(corpus))
            if matches > 0:
                score = matches * weight
                if pat.search(title):
                    score += 15
                if score > best_score:
                    best_score = score
                    best_candidate = (partie, chap, sec)

        if best_candidate and best_score >= 10:
            final_p, final_c, final_s = best_candidate
            final_s = self.enforce_section_rule(normalized_cat, final_p, final_c, final_s, title, description)
            return (final_p, final_c, final_s)

        # --- ÉTAPE 3 : Repli structuré par défaut ---
        if structure and structure[0].get('chapitres'):
            default_p = structure[0]['titre']
            default_c = structure[0]['chapitres'][0]['titre']
            default_s = structure[0]['chapitres'][0]['sections'][0]['titre'] if structure[0]['chapitres'][0].get('sections') else "Général"
            default_s = self.enforce_section_rule(normalized_cat, default_p, default_c, default_s, title, description)
            return (default_p, default_c, default_s)

        return ("PARTIE 1", "Chapitre 1 : Général", "Général")

    def enforce_section_rule(self, book_cat: str, partie: str, chapitre: str, current_section: str, title: str, description: str = "") -> str:
        """
        Règle d'or de taxonomie :
        'Général' est STRICTEMENT RÉSERVÉ aux chapitres sans sous-sections.
        Si un chapitre possède des sections dans la taxonomie de référence, la technique
        DOIT obligatoirement être classée dans l'une de ces sections.
        """
        norm_cat = self._normalize_key(book_cat)
        tax_book_map = {
            'cartes': 'livre_cartes_techniques',
            'pieces': 'livre_pieces_techniques',
            'tours': 'livre_tours_cartes',
            'tours_pieces': 'livre_tours_pieces',
        }
        tax_book_key = tax_book_map.get(norm_cat, 'livre_cartes_techniques')
        book_tax = self.taxonomies.get(tax_book_key, {})

        target_chap = None
        for p in book_tax.get('structure', []):
            for c in p.get('chapitres', []):
                if c.get('titre', '').strip().lower() == chapitre.strip().lower():
                    target_chap = c
                    break
            if target_chap:
                break

        # Si le chapitre n'a pas de sous-sections définies, 'Général' est la seule valeur légitime
        if not target_chap or not target_chap.get('sections'):
            return "Général"

        defined_sections = target_chap.get('sections', [])
        valid_section_titles = [s['titre'] for s in defined_sections]

        # Si la section actuelle est déjà une des sections valides (et non 'Général')
        if current_section and current_section.lower() != 'général' and current_section in valid_section_titles:
            return current_section

        # Sinon, attribution obligatoire de la meilleure section par scoring sémantique
        corpus = f"{title} {description}".lower()
        title_lower = title.lower()

        best_sec = valid_section_titles[0]
        best_score = -1

        for sec in defined_sections:
            sec_title = sec.get('titre', '')
            score = 0

            # 1. Mots-clés de la section
            for kw in sec.get('mots_cles', []):
                kw_low = kw.lower()
                if kw_low in title_lower:
                    score += 45
                elif kw_low in corpus:
                    score += 25

            # 2. Mots significatifs du titre de la section
            sec_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', sec_title.lower())) - {'section', 'chapitre', 'cartes', 'tours', 'partie'}
            for w in sec_words:
                if w in title_lower:
                    score += 15
                elif w in corpus:
                    score += 8

            # 3. Mots de la définition conceptuelle
            def_words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', sec.get('definition', '').lower())) - {'dans', 'pour', 'avec', 'sans', 'cette', 'fait'}
            matching_def = len(set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', corpus)) & def_words)
            score += matching_def * 3

            if score > best_score:
                best_score = score
                best_sec = sec_title

        return best_sec

