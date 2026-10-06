/**
 * Livre nini magie — Application Frontend Logic
 * Design épuré, minimaliste, centré sur l'essentiel.
 * Couleurs : Blanc, Noir, Bleu (#2563EB), Rouge (#DC2626).
 * 3 Onglets : Bibliothèque, Sommaire, PDF à télécharger.
 */

// =============================================================================
// LISTE STATIQUE OFFICIELLE DES 19 PDF SOURCES LISIBLES
// =============================================================================
const PDF_CATALOG = {
  cartes: {
    categoryTitle: '🃏 Techniques de Cartes',
    files: [
      { name: 'TECHNIQUE the-royal-road-to-card-magic (1).pdf', size: '2.56 Mo', path: 'Sources/sources_lisibles/sources techniques Cartes/TECHNIQUE  the-royal-road-to-card-magic (1).pdf' },
      { name: 'TECHNIQUES the-expert-at-the-card-table-s-w-erdnase.pdf', size: '60.13 Mo', path: 'Sources/sources_lisibles/sources techniques Cartes/TECHNIQUES  the-expert-at-the-card-table-s-w-erdnase-madisonx27spdf-3-pdf-free.pdf' },
      { name: 'TECHNIQUES Roberto Giobbi - Cours De Cartomagie Vol 1.pdf', size: '22.29 Mo', path: 'Sources/sources_lisibles/sources techniques Cartes/TECHNIQUES Roberto Giobbi - Cours De Cartomagie Moderne- Vol 1.pdf' },
      { name: 'TECNIQUE EN expert-card-technique.pdf', size: '6.67 Mo', path: 'Sources/sources_lisibles/sources techniques Cartes/TECNIQUE EN expert-card-technique-close-up-table-magic.pdf' },
      { name: 'TECNIQUE FR expert-card-technique.pdf', size: '19.03 Mo', path: 'Sources/sources_lisibles/sources techniques Cartes/TECNIQUE FR expert-card-technique-close-up-table-magic.pdf' }
    ]
  },
  pieces: {
    categoryTitle: '🪙 Traités de Pièces (Techniques & Tours)',
    files: [
      { name: 'Magic Secrets - Modern Coin Magic (Bobo).pdf', size: '5.79 Mo', path: 'Sources/sources_lisibles/sources techniques Pièces/Magic Secrets - Modern Coin Magic.pdf' },
      { name: 'Michael Rubinstein - Coin Magic (ROPS Press 2020).pdf', size: '129.72 Mo', path: 'Sources/sources_lisibles/sources techniques Pièces/michael-rubinstein-coin-magic-rops-press-2020-pdf-free.pdf' },
      { name: 'Richard Kaufman & David Roth - Expert Coin Magic.pdf', size: '23.47 Mo', path: 'Sources/sources_lisibles/sources techniques Pièces/pdfcoffee.com_richard-kaufman-david-roth-expert-coin-magicpdf-4-pdf-free.pdf' }
    ]
  },
  tours: {
    categoryTitle: '🎩 Tours de Cartes & Routines',
    files: [
      { name: 'GENERAL - The Code (Fenik).pdf', size: '121.85 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/GENERAL - the code fenik.pdf' },
      { name: 'GENERAL - The Very Best of Dai Vernon (Richard Vollmer).pdf', size: '64.40 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/GENERAL - the-very-best-of-dai-vernon-richard-vollmer-5-pdf-free.pdf' },
      { name: 'GENERAL - Card College Light (Roberto Giobbi).pdf', size: '4.18 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/GENERAL _card-college-light-pdfdrivecom-pdf-pdf-free.pdf' },
      { name: 'GENERAL - Jean Hugard - Encyclopedia of Card Tricks.pdf', size: '2.24 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/GENERAL _JEAN HUGARD encyclopedia-of-card-tricks-pdf-free.pdf' },
      { name: 'GENERAL - Nick Trost - Subtle Card Creations Vol 2.pdf', size: '15.39 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/GENERAL _nick-trost-subtle-card-creations-vol-2pdf-pdf-free.pdf' },
      { name: 'MARKED DECK - Boris Wild - Transparency.pdf', size: '27.42 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/MARKED DECK boris-wild-transparency-pdf-free.pdf' },
      { name: 'MARKED DECK - Routines for Phoenix Double Decker.pdf', size: '1.84 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/MARKED DECK Routines for the Phoenix Double Decker - Content.pdf' },
      { name: 'MARKED DECK - Passport to Marked Cards.pdf', size: '7.10 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/MARKED DECK toaz.info-passport-to-marked-cards-ebook-pr_8d455400e697007bfe7ee830b25761e0.pdf' },
      { name: 'MARKED DECK - Cartes Marquées.pdf', size: '2.49 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/MARKED DECK_cartes-marquees180424-pdf-free.pdf' },
      { name: 'STRIPPER DECK - Jean Hugard - Miracle Methods 1.pdf', size: '209.91 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/STRIPPER DECK jean-hugards-miracle-methods-1-pdf-free.pdf' },
      { name: 'STRIPPER DECK - Al Stevenson - 75 Tricks.pdf', size: '0.23 Mo', path: 'Sources/sources_lisibles/sources tours de Cartes/STRIPPER DECK _al-stevenson-75-tricks-with-a-stripper-deck-pdf-free.pdf' }
    ]
  }
};

// =============================================================================
// ÉTAT GLOBAL DE L'APPLICATION
// =============================================================================
const state = {
  currentView: 'library',       // 'library' | 'sommaire' | 'classement' | 'downloads'
  currentBook: 'cartes',        // 'cartes' | 'pieces' | 'tours' | 'tours_pieces'
  classementBook: 'cartes',     // 'cartes' | 'pieces' | 'tours' | 'tours_pieces'
  currentTech: null,
  booksData: null,              // Données complètes issues de data_cache.json
  isAllExpanded: false,
  treeSearchQuery: '',
  classementSearchQuery: '',
  classementData: {             // Cache mémoire des classements personnalisés
    cartes: null,
    pieces: null,
    tours: null,
    tours_pieces: null
  },
  isClassementAllExpanded: false
};

// =============================================================================
// SÉLECTEURS DU DOM
// =============================================================================
const dom = {
  // Navigation & En-tête
  appHomeLink: document.getElementById('app-home-link'),
  tabLibrary: document.getElementById('tab-library'),
  tabSommaire: document.getElementById('tab-sommaire'),
  tabClassement: document.getElementById('tab-classement'),
  tabDownloads: document.getElementById('tab-downloads'),
  headerTotalCount: document.getElementById('header-total-count'),

  // Vues
  viewLibrary: document.getElementById('view-library'),
  viewSommaire: document.getElementById('view-sommaire'),
  viewClassement: document.getElementById('view-classement'),
  viewDownloads: document.getElementById('view-downloads'),

  // Vue 1 : Bibliothèque (3 boutons)
  bookCards: document.querySelectorAll('.book-card'),
  homeCountCartes: document.getElementById('home-count-cartes'),
  homeCountPieces: document.getElementById('home-count-pieces'),
  homeCountTours: document.getElementById('home-count-tours'),
  homeCountToursPieces: document.getElementById('home-count-tours_pieces'),

  // Vue 2 : Sommaire
  screenSommaireTree: document.getElementById('screen-sommaire-tree'),
  screenTechniqueDetail: document.getElementById('screen-technique-detail'),
  bookSelectButtons: document.querySelectorAll('.btn-book-select'),
  btnToggleExpand: document.getElementById('btn-toggle-expand'),
  searchInput: document.getElementById('search-input'),
  searchCountBadge: document.getElementById('search-count-badge'),
  btnSearchClear: document.getElementById('btn-search-clear'),
  treeWrapper: document.getElementById('tree-wrapper'),

  // Fiche Technique Dédiée
  btnBackTree: document.getElementById('btn-back-tree'),
  detailId: document.getElementById('detail-id'),
  detailBreadcrumb: document.getElementById('detail-breadcrumb'),
  detailTitle: document.getElementById('detail-title'),
  btnOpenPdfPage: document.getElementById('btn-open-pdf-page'),
  btnOpenPageNum: document.getElementById('btn-open-page-num'),
  btnOpenPdfTab: document.getElementById('btn-open-pdf-tab'),
  btnDownloadPdf: document.getElementById('btn-download-pdf'),
  detailEffetText: document.getElementById('detail-effet-text'),
  detailMethodeText: document.getElementById('detail-methode-text'),
  detailSourceValue: document.getElementById('detail-source-value'),

  // Lecteur PDF Modal Plein Écran (S'ouvre uniquement au clic sur le bouton)
  pdfModal: document.getElementById('pdf-modal'),
  pdfModalTitle: document.getElementById('pdf-modal-title'),
  btnModalPrev: document.getElementById('btn-modal-prev'),
  modalCurrentPage: document.getElementById('modal-current-page'),
  modalTotalPages: document.getElementById('modal-total-pages'),
  btnModalNext: document.getElementById('btn-modal-next'),
  btnModalZoomOut: document.getElementById('btn-modal-zoom-out'),
  modalZoomIndicator: document.getElementById('modal-zoom-indicator'),
  btnModalZoomIn: document.getElementById('btn-modal-zoom-in'),
  pdfModalExternal: document.getElementById('pdf-modal-external'),
  btnClosePdfModal: document.getElementById('btn-close-pdf-modal'),
  modalRenderStatus: document.getElementById('modal-render-status'),
  modalPdfCanvas: document.getElementById('modal-pdf-canvas'),
  pdfModalBody: document.getElementById('pdf-modal-body'),
  modalPageInput: document.getElementById('modal-page-input'),

  // Vue 4 : Classement Personnalisé & Réordonnancement
  screenClassement: document.getElementById('screen-classement'),
  btnClassementExportExcel: document.getElementById('btn-classement-export-excel'),
  btnClassementAddTech: document.getElementById('btn-classement-add-tech'),
  btnClassementReset: document.getElementById('btn-classement-reset'),
  classementBookSelector: document.getElementById('classement-book-selector'),
  btnClassementBookCartes: document.getElementById('btn-classement-book-cartes'),
  btnClassementBookPieces: document.getElementById('btn-classement-book-pieces'),
  btnClassementBookTours: document.getElementById('btn-classement-book-tours'),
  btnClassementBookToursPieces: document.getElementById('btn-classement-book-tours_pieces'),
  classementSaveStatus: document.getElementById('classement-save-status'),
  btnClassementToggleExpand: document.getElementById('btn-classement-toggle-expand'),
  classementSearchInput: document.getElementById('classement-search-input'),
  classementSearchBadge: document.getElementById('classement-search-badge'),
  btnClassementSearchClear: document.getElementById('btn-classement-search-clear'),
  classementTreeWrapper: document.getElementById('classement-tree-wrapper'),

  // Modals : Ajout Technique
  modalAddTechnique: document.getElementById('modal-add-technique'),
  modalAddTechBackdrop: document.getElementById('modal-add-tech-backdrop'),
  btnCloseAddModal: document.getElementById('btn-close-add-modal'),
  formAddTechnique: document.getElementById('form-add-technique'),
  formTechBook: document.getElementById('form-tech-book'),
  formTechPartie: document.getElementById('form-tech-partie'),
  formTechChapitre: document.getElementById('form-tech-chapitre'),
  formTechSection: document.getElementById('form-tech-section'),
  formTechName: document.getElementById('form-tech-name'),
  formTechPage: document.getElementById('form-tech-page'),
  formTechSource: document.getElementById('form-tech-source'),
  formTechEffet: document.getElementById('form-tech-effet'),
  formTechMethode: document.getElementById('form-tech-methode'),
  formTechPosition: document.getElementById('form-tech-position'),
  btnCancelAddTech: document.getElementById('btn-cancel-add-tech'),

  // Modals : Export Excel
  modalExportExcel: document.getElementById('modal-export-excel'),
  modalExportBackdrop: document.getElementById('modal-export-backdrop'),
  btnCloseExportModal: document.getElementById('btn-close-export-modal'),
  exportModalBookTitle: document.getElementById('export-modal-book-title'),
  btnConfirmExportCurrent: document.getElementById('btn-confirm-export-current'),
  btnConfirmExportAll: document.getElementById('btn-confirm-export-all'),
  btnCancelExport: document.getElementById('btn-cancel-export'),

  // Toast Notification
  classementToast: document.getElementById('classement-toast'),

  // Vue 3 : Téléchargements PDF
  downloadsContainer: document.getElementById('downloads-container')
};

// =============================================================================
// GESTIONNAIRE UNIFIÉ DU LECTEUR PDF (PDF.js)
// =============================================================================
if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/vendor/pdf.worker.min.js';
}

class UniversalPdfViewer {
  constructor() {
    this.doc = null;
    this.currentPath = '';
    this.currentPage = 1;
    this.scale = 1.3;
    this.renderTask = null;
  }

  normalizeUrl(pdfPath) {
    if (!pdfPath) return '';
    let p = pdfPath.split('#')[0].replace(/\\/g, '/');
    try {
      p = decodeURI(p);
    } catch (e) {}
    if (!p.startsWith('/')) p = '/' + p;
    return encodeURI(p);
  }

  async loadDocument(pdfPath) {
    if (!pdfPath) return null;
    const cleanUrl = this.normalizeUrl(pdfPath);

    if (this.currentPath === cleanUrl && this.doc) {
      return this.doc;
    }

    this.currentPath = cleanUrl;
    if (this.renderTask) {
      try { this.renderTask.cancel(); } catch (e) {}
      this.renderTask = null;
    }

    const loadingTask = pdfjsLib.getDocument({
      url: cleanUrl,
      rangeChunkSize: 65536
    });

    this.doc = await loadingTask.promise;
    return this.doc;
  }

  async renderPage(pdfPath, pageNum) {
    const canvas = dom.modalPdfCanvas;
    const status = dom.modalRenderStatus;
    const pageDisplay = dom.modalCurrentPage;
    const pageInput = dom.modalPageInput;
    const totalDisplay = dom.modalTotalPages;
    const zoomDisplay = dom.modalZoomIndicator;
    const btnPrev = dom.btnModalPrev;
    const btnNext = dom.btnModalNext;

    if (!pdfPath) {
      status.style.display = 'block';
      canvas.style.display = 'none';
      status.textContent = 'Aucun document PDF associé.';
      return;
    }

    status.style.display = 'block';
    status.textContent = `Chargement du PDF à la page ${pageNum}...`;

    try {
      const doc = await this.loadDocument(pdfPath);
      if (!doc) throw new Error('Impossible de charger le document.');

      this.currentPage = Math.max(1, Math.min(pageNum, doc.numPages));
      if (pageInput) {
        pageInput.value = this.currentPage;
        pageInput.max = doc.numPages;
      }
      if (pageDisplay) pageDisplay.textContent = this.currentPage;
      if (totalDisplay) totalDisplay.textContent = doc.numPages;
      if (zoomDisplay) zoomDisplay.textContent = `${Math.round(this.scale * 100)}%`;

      if (btnPrev) btnPrev.disabled = this.currentPage <= 1;
      if (btnNext) btnNext.disabled = this.currentPage >= doc.numPages;

      if (this.renderTask) {
        try { this.renderTask.cancel(); } catch (e) {}
        this.renderTask = null;
      }

      const page = await doc.getPage(this.currentPage);
      const dpr = window.devicePixelRatio || 1;
      const viewport = page.getViewport({ scale: this.scale * dpr });

      const ctx = canvas.getContext('2d');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.style.width = `${viewport.width / dpr}px`;
      canvas.style.height = `${viewport.height / dpr}px`;

      const renderContext = {
        canvasContext: ctx,
        viewport: viewport
      };

      const task = page.render(renderContext);
      this.renderTask = task;
      await task.promise;
      this.renderTask = null;

      status.style.display = 'none';
      canvas.style.display = 'block';

      if (dom.pdfModalBody) {
        dom.pdfModalBody.scrollTop = 0;
      }
    } catch (err) {
      if (err.name !== 'RenderingCancelledException') {
        console.error('Erreur rendu PDF:', err);
        status.textContent = `Erreur chargement PDF (${err.message}).`;
        status.style.display = 'block';
        canvas.style.display = 'none';
      }
    }
  }

  changePage(delta) {
    const newPage = this.currentPage + delta;
    if (this.doc && newPage >= 1 && newPage <= this.doc.numPages) {
      this.renderPage(this.currentPath, newPage);
    }
  }

  goToPage(pageNum) {
    const target = parseInt(pageNum, 10);
    if (this.doc && !isNaN(target) && target >= 1 && target <= this.doc.numPages) {
      this.renderPage(this.currentPath, target);
    } else if (dom.modalPageInput) {
      dom.modalPageInput.value = this.currentPage;
    }
  }

  changeZoom(delta) {
    this.scale = Math.max(0.6, Math.min(2.5, Math.round((this.scale + delta) * 10) / 10));
    this.renderPage(this.currentPath, this.currentPage);
  }
}

const pdfViewer = new UniversalPdfViewer();

// =============================================================================
// INITIALISATION DE L'APPLICATION
// =============================================================================
document.addEventListener('DOMContentLoaded', async () => {
  initEventListeners();
  renderDownloadsTab();
  initPwa();
  await loadDatabase();
});

// Enregistrement PWA & Nettoyage strict du cache
function initPwa() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(regs => {
      for (const reg of regs) {
        reg.update();
      }
    });
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  }
  if ('caches' in window) {
    caches.keys().then(keys => {
      keys.forEach(k => {
        if (k !== 'livre-nini-magie-v5') caches.delete(k);
      });
    });
  }
}

// =============================================================================
// CHARGEMENT DE LA BASE DE DONNÉES DEPUIS data_cache.json DIRECTEMENT
// =============================================================================
async function loadDatabase() {
  try {
    const res = await fetch('/data/data_cache.json');
    if (!res.ok) {
      throw new Error(`Erreur réseau HTTP ${res.status}`);
    }
    const data = await res.json();
    state.booksData = data.books;

    let total = 0;
    if (state.booksData.cartes) {
      dom.homeCountCartes.textContent = `${state.booksData.cartes.count.toLocaleString()} techniques`;
      total += state.booksData.cartes.count;
    }
    if (state.booksData.pieces) {
      dom.homeCountPieces.textContent = `${state.booksData.pieces.count.toLocaleString()} techniques`;
      total += state.booksData.pieces.count;
    }
    if (state.booksData.tours) {
      dom.homeCountTours.textContent = `${state.booksData.tours.count.toLocaleString()} routines`;
      total += state.booksData.tours.count;
    }
    if (state.booksData.tours_pieces && dom.homeCountToursPieces) {
      dom.homeCountToursPieces.textContent = `${state.booksData.tours_pieces.count.toLocaleString()} routines`;
      total += state.booksData.tours_pieces.count;
    }

    dom.headerTotalCount.textContent = `${total.toLocaleString()} fiches certifiées`;

    // Si la vue sommaire est affichée, construire l'arborescence complète
    if (state.currentView === 'sommaire') {
      renderCurrentBookTree();
    } else if (state.currentView === 'classement') {
      renderClassementTree();
    }
  } catch (err) {
    console.error('Erreur critique lors du chargement de data_cache.json:', err);
    dom.treeWrapper.innerHTML = `<div class="tree-loading" style="color: var(--color-red);">Erreur de chargement des données. Veuillez actualiser la page.</div>`;
  }
}

// =============================================================================
// CONFIGURATION DES ÉCOUTEURS D'ÉVÉNEMENTS
// =============================================================================
function initEventListeners() {
  // Clic Logo
  dom.appHomeLink.addEventListener('click', () => switchView('library'));

  // 4 Onglets principaux
  dom.tabLibrary.addEventListener('click', () => switchView('library'));
  dom.tabSommaire.addEventListener('click', () => {
    switchView('sommaire');
    renderCurrentBookTree();
  });
  dom.tabClassement.addEventListener('click', () => {
    switchView('classement');
    renderClassementTree();
  });
  dom.tabDownloads.addEventListener('click', () => switchView('downloads'));

  // Clic sur les 3 grands boutons de la Bibliothèque ➔ Bascule immédiate sur le Sommaire !
  dom.bookCards.forEach(card => {
    card.addEventListener('click', () => {
      const bookId = card.dataset.book;
      state.currentBook = bookId;
      switchView('sommaire');
      updateBookSelectorTabs(bookId);
      renderCurrentBookTree();
    });
  });

  // Sélecteur de livres dans l'onglet Sommaire
  dom.bookSelectButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const bookId = btn.dataset.book;
      state.currentBook = bookId;
      updateBookSelectorTabs(bookId);
      renderCurrentBookTree();
    });
  });

  // Bouton retour au sommaire depuis la fiche technique
  dom.btnBackTree.addEventListener('click', () => {
    dom.screenTechniqueDetail.style.display = 'none';
    dom.screenSommaireTree.style.display = 'flex';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // Bouton principal d'action : OUVRIR LE PDF PLEIN ÉCRAN À LA BONNE PAGE
  dom.btnOpenPdfPage.addEventListener('click', () => {
    if (!state.currentTech) return;
    openPdfModalForTech(state.currentTech);
  });

  // Recherche dans le sommaire
  let searchTimer = null;
  dom.searchInput.addEventListener('input', (e) => {
    state.treeSearchQuery = e.target.value.trim().toLowerCase();
    dom.btnSearchClear.style.display = state.treeSearchQuery ? 'block' : 'none';
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      filterTree(state.treeSearchQuery);
    }, 150);
  });

  dom.btnSearchClear.addEventListener('click', () => {
    dom.searchInput.value = '';
    state.treeSearchQuery = '';
    dom.btnSearchClear.style.display = 'none';
    dom.searchCountBadge.style.display = 'none';
    filterTree('');
  });

  // Bouton Tout déplier / Tout replier
  dom.btnToggleExpand.addEventListener('click', () => {
    state.isAllExpanded = !state.isAllExpanded;
    dom.btnToggleExpand.textContent = state.isAllExpanded ? 'Tout replier' : 'Tout déplier';
    toggleAllNodes(state.isAllExpanded);
  });

  // Contrôles du Lecteur PDF Modal Plein Écran
  dom.btnModalPrev.addEventListener('click', () => pdfViewer.changePage(-1));
  dom.btnModalNext.addEventListener('click', () => pdfViewer.changePage(1));
  dom.btnModalZoomIn.addEventListener('click', () => pdfViewer.changeZoom(0.2));
  dom.btnModalZoomOut.addEventListener('click', () => pdfViewer.changeZoom(-0.2));
  dom.btnClosePdfModal.addEventListener('click', closePdfModal);

  // Saisie directe de page dans le lecteur PDF
  if (dom.modalPageInput) {
    dom.modalPageInput.addEventListener('change', (e) => {
      pdfViewer.goToPage(e.target.value);
    });
    dom.modalPageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        pdfViewer.goToPage(e.target.value);
      }
    });
  }

  // Navigation clavier : Échap pour fermer, Flèches Gauche/Droite pour tourner les pages
  window.addEventListener('keydown', (e) => {
    if (dom.pdfModal && dom.pdfModal.style.display !== 'none') {
      if (e.key === 'Escape') {
        closePdfModal();
      } else if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        if (document.activeElement !== dom.modalPageInput) {
          e.preventDefault();
          pdfViewer.changePage(1);
        }
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        if (document.activeElement !== dom.modalPageInput) {
          e.preventDefault();
          pdfViewer.changePage(-1);
        }
      } else if (e.key === '+' || e.key === '=') {
        if (document.activeElement !== dom.modalPageInput) {
          e.preventDefault();
          pdfViewer.changeZoom(0.2);
        }
      } else if (e.key === '-') {
        if (document.activeElement !== dom.modalPageInput) {
          e.preventDefault();
          pdfViewer.changeZoom(-0.2);
        }
      }
    } else {
      if (e.key === 'Escape') {
        if (dom.modalAddTechnique && dom.modalAddTechnique.style.display !== 'none') closeAddTechModal();
        if (dom.modalExportExcel && dom.modalExportExcel.style.display !== 'none') closeExportModal();
      }
    }
  });

  // Initialisation des écouteurs du module Classement
  initClassementEventListeners();
}

// =============================================================================
// NAVIGATION ENTRE LES 4 ONGLETS
// =============================================================================
function switchView(viewName) {
  state.currentView = viewName;

  dom.tabLibrary.classList.toggle('active', viewName === 'library');
  dom.tabSommaire.classList.toggle('active', viewName === 'sommaire');
  dom.tabClassement.classList.toggle('active', viewName === 'classement');
  dom.tabDownloads.classList.toggle('active', viewName === 'downloads');

  dom.viewLibrary.style.display = viewName === 'library' ? 'flex' : 'none';
  dom.viewSommaire.style.display = viewName === 'sommaire' ? 'flex' : 'none';
  dom.viewClassement.style.display = viewName === 'classement' ? 'flex' : 'none';
  dom.viewDownloads.style.display = viewName === 'downloads' ? 'flex' : 'none';

  if (viewName === 'sommaire') {
    dom.screenSommaireTree.style.display = 'flex';
    dom.screenTechniqueDetail.style.display = 'none';
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateBookSelectorTabs(bookId) {
  dom.bookSelectButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.book === bookId);
  });
}

// =============================================================================
// CONSTRUCTION DE L'ARBORESCENCE DANS L'ONGLET SOMMAIRE
// =============================================================================
function renderCurrentBookTree() {
  if (!state.booksData || !state.booksData[state.currentBook]) {
    dom.treeWrapper.innerHTML = '<div class="tree-loading">Chargement des données du livre...</div>';
    return;
  }

  const book = state.booksData[state.currentBook];
  const hierarchy = book.hierarchy;
  const techniques = book.techniques;

  dom.treeWrapper.innerHTML = '';
  dom.searchInput.value = '';
  state.treeSearchQuery = '';
  dom.btnSearchClear.style.display = 'none';
  dom.searchCountBadge.style.display = 'none';

  // Indexer les techniques par clé combinée
  const techMap = {};
  techniques.forEach(t => {
    const key = `${t.partie}|||${t.chapitre}|||${t.section}`;
    if (!techMap[key]) techMap[key] = [];
    techMap[key].push(t);
  });

  // Construction de l'arborescence complète (100% des chapitres et sections Word)
  for (const [partie, chapitres] of Object.entries(hierarchy)) {
    const partieEl = document.createElement('div');
    partieEl.className = 'partie-node';

    let totalPartie = 0;
    for (const [chap, secs] of Object.entries(chapitres)) {
      for (const [sec, count] of Object.entries(secs)) {
        totalPartie += count;
      }
    }

    const pHeader = document.createElement('div');
    pHeader.className = 'partie-header';
    pHeader.innerHTML = `
      <div class="partie-title">
        <span class="chevron">▶</span>
        <span>${escapeHtml(partie)}</span>
      </div>
      <span class="partie-count">${totalPartie}</span>
    `;

    const pBody = document.createElement('div');
    pBody.className = 'partie-body';

    pHeader.addEventListener('click', () => {
      const isOpen = pHeader.classList.toggle('open');
      pBody.classList.toggle('open', isOpen);
    });

    for (const [chapitre, sections] of Object.entries(chapitres)) {
      const chapEl = document.createElement('div');
      chapEl.className = 'chapitre-node';

      let totalChap = 0;
      for (const [sec, count] of Object.entries(sections)) {
        totalChap += count;
      }

      const cHeader = document.createElement('div');
      cHeader.className = 'chapitre-header';
      cHeader.innerHTML = `
        <div class="partie-title">
          <span class="chevron">▶</span>
          <span>${escapeHtml(chapitre)}</span>
        </div>
        <span class="chapitre-count">${totalChap}</span>
      `;

      const cBody = document.createElement('div');
      cBody.className = 'chapitre-body';

      cHeader.addEventListener('click', () => {
        const isOpen = cHeader.classList.toggle('open');
        cBody.classList.toggle('open', isOpen);
      });

      const secKeys = Object.keys(sections);
      const isSingleGeneral = secKeys.length === 1 && secKeys[0] === 'Général';

      if (isSingleGeneral) {
        const directListKey = `${partie}|||${chapitre}|||Général`;
        const directTechs = techMap[directListKey] || [];
        if (directTechs.length === 0) {
          const emptyNotice = document.createElement('div');
          emptyNotice.className = 'tree-empty-note';
          emptyNotice.textContent = 'Aucune technique répertoriée dans ce chapitre.';
          cBody.appendChild(emptyNotice);
        } else {
          renderTechItemList(cBody, directTechs);
        }
      } else {
        for (const [section, count] of Object.entries(sections)) {
          const secEl = document.createElement('div');
          secEl.className = 'section-node';

          const sHeader = document.createElement('div');
          sHeader.className = 'section-header';
          sHeader.innerHTML = `
            <div class="partie-title">
              <span class="chevron">▶</span>
              <span>${escapeHtml(section)}</span>
            </div>
            <span class="section-count">${count}</span>
          `;

          const sBody = document.createElement('div');
          sBody.className = 'section-body';

          sHeader.addEventListener('click', () => {
            const isOpen = sHeader.classList.toggle('open');
            sBody.classList.toggle('open', isOpen);
          });

          const secListKey = `${partie}|||${chapitre}|||${section}`;
          const secTechs = techMap[secListKey] || [];
          if (secTechs.length === 0) {
            const emptyNotice = document.createElement('div');
            emptyNotice.className = 'tree-empty-note';
            emptyNotice.textContent = 'Aucune technique répertoriée dans cette section.';
            sBody.appendChild(emptyNotice);
          } else {
            renderTechItemList(sBody, secTechs);
          }

          secEl.appendChild(sHeader);
          secEl.appendChild(sBody);
          cBody.appendChild(secEl);
        }
      }

      chapEl.appendChild(cHeader);
      chapEl.appendChild(cBody);
      pBody.appendChild(chapEl);
    }

    partieEl.appendChild(pHeader);
    partieEl.appendChild(pBody);
    dom.treeWrapper.appendChild(partieEl);
  }
}

// Rendu progressif par lots de 50 pour éliminer tout gel de l'interface
function renderTechItemList(container, techs) {
  const CHUNK_SIZE = 50;
  let currentlyRendered = 0;

  function renderNextChunk() {
    const nextChunk = techs.slice(currentlyRendered, currentlyRendered + CHUNK_SIZE);
    nextChunk.forEach(tech => {
      const item = createTechItemElement(tech);
      container.appendChild(item);
    });
    currentlyRendered += nextChunk.length;
  }

  // Rendu initial du premier lot
  renderNextChunk();

  // Si d'autres techniques restent, ajouter la barre de chargement progressif
  if (currentlyRendered < techs.length) {
    const loadMoreBar = document.createElement('div');
    loadMoreBar.className = 'tree-load-more-bar';

    const btnMore = document.createElement('button');
    btnMore.type = 'button';
    btnMore.className = 'btn-load-more';
    btnMore.textContent = `Afficher 50 de plus (${currentlyRendered} / ${techs.length})...`;

    const btnAll = document.createElement('button');
    btnAll.type = 'button';
    btnAll.className = 'btn-load-more';
    btnAll.textContent = `Tout afficher (${techs.length})`;

    btnMore.addEventListener('click', (e) => {
      e.stopPropagation();
      renderNextChunk();
      if (currentlyRendered >= techs.length) {
        loadMoreBar.remove();
      } else {
        btnMore.textContent = `Afficher 50 de plus (${currentlyRendered} / ${techs.length})...`;
      }
    });

    btnAll.addEventListener('click', (e) => {
      e.stopPropagation();
      while (currentlyRendered < techs.length) {
        renderNextChunk();
      }
      loadMoreBar.remove();
    });

    loadMoreBar.appendChild(btnMore);
    loadMoreBar.appendChild(btnAll);
    container.appendChild(loadMoreBar);
  }
}

function createTechItemElement(tech) {
  const item = document.createElement('div');
  item.className = 'tech-item';
  item.dataset.techName = (tech.nom || '').toLowerCase();
  item.dataset.techDesc = (tech.description || '').toLowerCase();

  const numSources = (tech.sources && tech.sources.length) || 1;
  const targetPage = extractPageNumber(tech);
  const pageText = numSources > 1 ? `📚 ${numSources} sources PDF` : (targetPage ? `Page ${targetPage}` : '');

  item.innerHTML = `
    <span class="tech-item-name">${escapeHtml(tech.nom)}</span>
    ${pageText ? `<span class="tech-item-page ${numSources > 1 ? 'badge-multi-sources' : ''}">${escapeHtml(pageText)}</span>` : ''}
    <span class="tech-item-arrow">➔</span>
  `;

  item.addEventListener('click', (e) => {
    e.stopPropagation();
    openTechniqueDetail(tech);
  });

  return item;
}

// =============================================================================
// RECHERCHE DANS LE SOMMAIRE
// =============================================================================
function filterTree(query) {
  const items = dom.treeWrapper.querySelectorAll('.tech-item');
  if (!query) {
    items.forEach(el => el.style.display = 'flex');
    dom.searchCountBadge.style.display = 'none';
    return;
  }

  let matchCount = 0;
  items.forEach(el => {
    const nameMatch = el.dataset.techName && el.dataset.techName.includes(query);
    const descMatch = el.dataset.techDesc && el.dataset.techDesc.includes(query);
    const match = nameMatch || descMatch;
    el.style.display = match ? 'flex' : 'none';
    if (match) matchCount++;
  });

  dom.searchCountBadge.style.display = 'inline-block';
  dom.searchCountBadge.textContent = `${matchCount} résultat${matchCount > 1 ? 's' : ''}`;

  if (query.length >= 2) {
    toggleAllNodes(true);
  }
}

function toggleAllNodes(open) {
  const headers = dom.treeWrapper.querySelectorAll('.partie-header, .chapitre-header, .section-header');
  const bodies = dom.treeWrapper.querySelectorAll('.partie-body, .chapitre-body, .section-body');

  headers.forEach(h => h.classList.toggle('open', open));
  bodies.forEach(b => b.classList.toggle('open', open));
}

// =============================================================================
// FICHE TECHNIQUE DÉDIÉE & OUVERTURE DU LECTEUR PDF À LA BONNE PAGE
// =============================================================================
function openTechniqueDetail(tech) {
  state.currentTech = tech;

  dom.detailId.textContent = tech.id || '';
  dom.detailBreadcrumb.textContent = `${tech.partie} › ${tech.chapitre} › ${tech.section}`;
  dom.detailTitle.textContent = tech.nom;

  let effet = '';
  let methode = '';

  if (tech.description) {
    if (tech.description.includes('| [Méthode]')) {
      const parts = tech.description.split('| [Méthode]');
      effet = parts[0].replace('[Effet]', '').trim();
      methode = parts[1].trim();
    } else if (tech.description.startsWith('[Effet]')) {
      effet = tech.description.replace('[Effet]', '').trim();
      methode = 'Détails techniques consultables dans le PDF original.';
    } else {
      effet = tech.description;
      methode = 'Voir manipulations détaillées à la page indiquée.';
    }
  }

  dom.detailEffetText.textContent = effet || 'Description non renseignée.';
  dom.detailMethodeText.textContent = methode || 'Détails secrets décrits dans le PDF source.';

  // Sources multiples
  const sources = (tech.sources && tech.sources.length > 0) ? tech.sources : [{
    ref: tech.pdf_ref,
    target: tech.pdf_target,
    page: extractPageNumber(tech),
    book: (tech.pdf_target ? tech.pdf_target.split('#')[0].split('/').pop().replace('.pdf', '') : (tech.pdf_ref ? tech.pdf_ref.split(',')[0] : 'PDF'))
  }];

  // Affichage dans la zone métadonnées Source
  if (sources.length > 1) {
    dom.detailSourceValue.innerHTML = sources.map((s, idx) => 
      `<div class="source-item-line"><strong>${escapeHtml(s.book || ('Livre ' + (idx + 1)))}</strong> : <em>p. ${s.page}</em> (${escapeHtml(s.ref)})</div>`
    ).join('');
  } else {
    dom.detailSourceValue.textContent = tech.pdf_ref || 'Source certifiée non spécifiée';
  }

  // Configuration des boutons PDF
  const multiContainer = document.getElementById('detail-multi-sources-container');
  if (sources.length > 1) {
    // Masquer les boutons simples
    dom.btnOpenPdfPage.style.display = 'none';
    dom.btnOpenPdfTab.style.display = 'none';
    dom.btnDownloadPdf.style.display = 'none';

    // Remplir et afficher le conteneur multi-sources
    if (multiContainer) {
      multiContainer.style.display = 'flex';
      multiContainer.innerHTML = `
        <div class="multi-sources-header">
          <span class="badge badge-blue">📚 ${sources.length} SOURCES PDF DISPONIBLES</span>
          <span class="multi-sources-subtitle">Cette technique est décrite dans plusieurs livres. Cliquez pour ouvrir la source de votre choix :</span>
        </div>
        <div class="multi-sources-grid">
          ${sources.map((s, idx) => {
            const cleanPdf = s.target ? s.target.split('#')[0] : '';
            const encPdf = cleanPdf ? (cleanPdf.startsWith('/') ? cleanPdf : '/' + cleanPdf) : '';
            const bName = s.book || ('Livre ' + (idx + 1));
            return `
              <div class="multi-source-card">
                <div class="multi-source-info">
                  <span class="multi-source-book" title="${escapeHtml(bName)}">📖 ${escapeHtml(bName)}</span>
                  <span class="multi-source-page">Page ${s.page}</span>
                </div>
                <div class="multi-source-actions">
                  <button type="button" class="btn btn-primary btn-sm btn-open-specific-source" data-target="${escapeHtml(s.target)}" data-page="${s.page}" data-book="${escapeHtml(bName)}">
                    📖 Ouvrir page ${s.page}
                  </button>
                  ${encPdf ? `
                    <a class="btn btn-outline btn-sm" href="${encodeURI(encPdf)}#page=${s.page}" target="_blank" title="Ouvrir dans un nouvel onglet natif">↗ Onglet</a>
                    <a class="btn btn-outline btn-sm" href="${encodeURI(encPdf)}?download=1" download title="Télécharger le fichier complet">📥 PDF</a>
                  ` : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `;

      // Brancher le clic sur chaque bouton d'ouverture
      multiContainer.querySelectorAll('.btn-open-specific-source').forEach(btn => {
        btn.addEventListener('click', () => {
          const tTarget = btn.dataset.target;
          const tPage = parseInt(btn.dataset.page, 10) || 1;
          const tBook = btn.dataset.book;
          openPdfModalForTech(tech, tTarget, tPage, tBook);
        });
      });
    }
  } else {
    // Mode classique (source unique)
    if (multiContainer) {
      multiContainer.style.display = 'none';
      multiContainer.innerHTML = '';
    }

    const s = sources[0];
    const targetPage = s.page || extractPageNumber(tech);
    let cleanPdfPath = s.target ? s.target.split('#')[0] : '';
    if (!cleanPdfPath && s.ref) {
      const filenameMatch = s.ref.split(',')[0].trim();
      cleanPdfPath = findPdfPathByName(filenameMatch);
    }

    if (cleanPdfPath && !cleanPdfPath.startsWith('/')) {
      cleanPdfPath = '/' + cleanPdfPath;
    }

    dom.btnOpenPageNum.textContent = targetPage;
    dom.btnOpenPdfPage.style.display = cleanPdfPath ? 'inline-flex' : 'none';

    if (cleanPdfPath) {
      const encodedUrl = encodeURI(cleanPdfPath);
      dom.btnOpenPdfTab.href = `${encodedUrl}#page=${targetPage}`;
      dom.btnOpenPdfTab.style.display = 'inline-flex';

      dom.btnDownloadPdf.href = `${encodedUrl}?download=1`;
      dom.btnDownloadPdf.style.display = 'inline-flex';
    } else {
      dom.btnOpenPdfTab.style.display = 'none';
      dom.btnDownloadPdf.style.display = 'none';
    }
  }

  // Bascule d'affichage
  dom.screenSommaireTree.style.display = 'none';
  dom.screenTechniqueDetail.style.display = 'flex';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Ouvrir le lecteur PDF Modal plein écran pour la technique (uniquement au clic sur le bouton)
function openPdfModalForTech(tech, customTarget, customPage, customBook) {
  const targetPage = customPage || extractPageNumber(tech);
  const targetUrl = customTarget || tech.pdf_target || '';
  let cleanPdfPath = targetUrl ? targetUrl.split('#')[0] : '';
  if (!cleanPdfPath && tech.pdf_ref) {
    const filenameMatch = tech.pdf_ref.split(',')[0].trim();
    cleanPdfPath = findPdfPathByName(filenameMatch);
  }

  if (cleanPdfPath && !cleanPdfPath.startsWith('/')) {
    cleanPdfPath = '/' + cleanPdfPath;
  }

  let filename = customBook || (cleanPdfPath ? cleanPdfPath.split('/').pop().replace('.pdf', '') : 'Document');
  try {
    filename = decodeURIComponent(filename);
  } catch (e) {}

  dom.pdfModalTitle.textContent = `${tech.nom} — ${filename} (Page ${targetPage})`;

  if (cleanPdfPath) {
    let cleanExt = cleanPdfPath;
    try { cleanExt = decodeURI(cleanExt); } catch (e) {}
    dom.pdfModalExternal.href = `${encodeURI(cleanExt)}#page=${targetPage}`;
    dom.pdfModalExternal.style.display = 'inline-flex';
  } else {
    dom.pdfModalExternal.style.display = 'none';
  }

  dom.pdfModal.style.display = 'flex';
  document.body.style.overflow = 'hidden';

  pdfViewer.renderPage(cleanPdfPath, targetPage);
}

function closePdfModal() {
  dom.pdfModal.style.display = 'none';
  document.body.style.overflow = '';
}

// Utilitaire d'extraction de page
function extractPageNumber(tech) {
  if (tech.pdf_target && tech.pdf_target.includes('#page=')) {
    const match = tech.pdf_target.match(/#page=(\d+)/);
    if (match) return parseInt(match[1], 10);
  }
  if (tech.pdf_ref) {
    const match = tech.pdf_ref.match(/p\.\s*(\d+)/i);
    if (match) return parseInt(match[1], 10);
  }
  return 1;
}

function findPdfPathByName(filename) {
  if (!filename) return '';
  const cleanFn = filename.trim().toLowerCase();
  for (const cat of Object.values(PDF_CATALOG)) {
    for (const file of cat.files) {
      const fNameLower = file.name.toLowerCase();
      const fPathLower = file.path.toLowerCase();
      if (fNameLower === cleanFn || fPathLower.endsWith(cleanFn) || cleanFn.includes(fNameLower)) {
        return '/' + file.path;
      }
    }
  }
  return '';
}

// =============================================================================
// VUE 3 : RENDU DE L'ONGLET « PDF À TÉLÉCHARGER »
// =============================================================================
function renderDownloadsTab() {
  dom.downloadsContainer.innerHTML = '';

  for (const [key, cat] of Object.entries(PDF_CATALOG)) {
    const catSection = document.createElement('div');
    catSection.className = 'download-cat-section';

    const titleEl = document.createElement('h3');
    titleEl.className = 'download-cat-title';
    titleEl.innerHTML = `<span>${cat.categoryTitle}</span><span style="font-size: 13px; font-weight: 500; color: var(--color-gray-muted);">${cat.files.length} livres</span>`;
    catSection.appendChild(titleEl);

    const listEl = document.createElement('div');
    listEl.className = 'download-pdf-list';

    cat.files.forEach(file => {
      const row = document.createElement('div');
      row.className = 'download-pdf-row';

      const cleanUrl = '/' + file.path;

      row.innerHTML = `
        <div class="download-pdf-info">
          <span class="download-pdf-name">${escapeHtml(file.name)}</span>
          <span class="download-pdf-size">Taille certifiée : ${file.size}</span>
        </div>
        <div class="download-pdf-actions">
          <button type="button" class="btn btn-outline btn-sm btn-read-pdf" data-path="${escapeHtml(cleanUrl)}" data-name="${escapeHtml(file.name)}">📖 Lire</button>
          <a class="btn btn-primary btn-sm" href="${encodeURI(cleanUrl)}?download=1" download="${escapeHtml(file.name)}">📥 Télécharger</a>
        </div>
      `;

      // Clic sur "Lire" : ouvre la fiche avec le lecteur PDF
      row.querySelector('.btn-read-pdf').addEventListener('click', () => {
        openPdfDirectly(cleanUrl, file.name);
      });

      listEl.appendChild(row);
    });

    catSection.appendChild(listEl);
    dom.downloadsContainer.appendChild(catSection);
  }
}

// Ouvrir directement un PDF depuis l'onglet téléchargement
function openPdfDirectly(pdfPath, fileName) {
  state.currentTech = {
    id: 'DOCUMENT_PDF',
    nom: fileName,
    partie: 'DOCUMENTATION COMPLÈTE',
    chapitre: 'Livre Source',
    section: 'Texte Intégral',
    description: `Lecture intégrale du document certifié OCR : ${fileName}`,
    pdf_ref: `${fileName}, p. 1`,
    pdf_target: `${pdfPath}#page=1`
  };

  openTechniqueDetail(state.currentTech);
  switchView('sommaire');
  openPdfModalForTech(state.currentTech, pdfPath, 1, fileName);
}

// Utilitaires
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// =============================================================================
// MODULE CLASSEMENT PERSONNALISÉ & EXPORT EXCEL
// =============================================================================
let draggedItemInfo = null;

function initClassementEventListeners() {
  // Sélecteur des 3 livres
  if (dom.btnClassementBookCartes) {
    dom.btnClassementBookCartes.addEventListener('click', () => switchClassementBook('cartes'));
  }
  if (dom.btnClassementBookPieces) {
    dom.btnClassementBookPieces.addEventListener('click', () => switchClassementBook('pieces'));
  }
  if (dom.btnClassementBookTours) {
    dom.btnClassementBookTours.addEventListener('click', () => switchClassementBook('tours'));
  }
  if (dom.btnClassementBookToursPieces) {
    dom.btnClassementBookToursPieces.addEventListener('click', () => switchClassementBook('tours_pieces'));
  }

  // Boutons du haut
  if (dom.btnClassementExportExcel) {
    dom.btnClassementExportExcel.addEventListener('click', openExportModal);
  }
  if (dom.btnClassementAddTech) {
    dom.btnClassementAddTech.addEventListener('click', () => openAddTechModal(state.classementBook));
  }
  if (dom.btnClassementReset) {
    dom.btnClassementReset.addEventListener('click', () => resetClassement(state.classementBook));
  }

  // Tout déplier / replier
  if (dom.btnClassementToggleExpand) {
    dom.btnClassementToggleExpand.addEventListener('click', () => {
      state.isClassementAllExpanded = !state.isClassementAllExpanded;
      dom.btnClassementToggleExpand.textContent = state.isClassementAllExpanded ? 'Tout replier' : 'Tout déplier';
      toggleAllClassementNodes(state.isClassementAllExpanded);
    });
  }

  // Recherche dans le classement
  if (dom.classementSearchInput) {
    let timer = null;
    dom.classementSearchInput.addEventListener('input', (e) => {
      state.classementSearchQuery = e.target.value.trim().toLowerCase();
      if (dom.btnClassementSearchClear) {
        dom.btnClassementSearchClear.style.display = state.classementSearchQuery ? 'block' : 'none';
      }
      clearTimeout(timer);
      timer = setTimeout(() => filterClassementTree(state.classementSearchQuery), 150);
    });
  }

  if (dom.btnClassementSearchClear) {
    dom.btnClassementSearchClear.addEventListener('click', () => {
      dom.classementSearchInput.value = '';
      state.classementSearchQuery = '';
      dom.btnClassementSearchClear.style.display = 'none';
      if (dom.classementSearchBadge) dom.classementSearchBadge.style.display = 'none';
      filterClassementTree('');
    });
  }

  // Modal Ajout
  if (dom.btnCloseAddModal) dom.btnCloseAddModal.addEventListener('click', closeAddTechModal);
  if (dom.btnCancelAddTech) dom.btnCancelAddTech.addEventListener('click', closeAddTechModal);
  if (dom.modalAddTechBackdrop) dom.modalAddTechBackdrop.addEventListener('click', closeAddTechModal);
  if (dom.formAddTechnique) dom.formAddTechnique.addEventListener('submit', handleAddTechniqueSubmit);

  // Cascading selects dans la modal d'ajout
  if (dom.formTechBook) {
    dom.formTechBook.addEventListener('change', (e) => {
      populateAddModalParties(e.target.value);
    });
  }
  if (dom.formTechPartie) {
    dom.formTechPartie.addEventListener('change', (e) => {
      populateAddModalChapitres(dom.formTechBook.value, e.target.value);
    });
  }
  if (dom.formTechChapitre) {
    dom.formTechChapitre.addEventListener('change', (e) => {
      populateAddModalSections(dom.formTechBook.value, dom.formTechPartie.value, e.target.value);
    });
  }

  // Modal Export Excel
  if (dom.btnCloseExportModal) dom.btnCloseExportModal.addEventListener('click', closeExportModal);
  if (dom.btnCancelExport) dom.btnCancelExport.addEventListener('click', closeExportModal);
  if (dom.modalExportBackdrop) dom.modalExportBackdrop.addEventListener('click', closeExportModal);
  if (dom.btnConfirmExportCurrent) {
    dom.btnConfirmExportCurrent.addEventListener('click', () => exportBookToExcel(state.classementBook));
  }
  if (dom.btnConfirmExportAll) {
    dom.btnConfirmExportAll.addEventListener('click', exportAllBooksToExcel);
  }
}

function switchClassementBook(bookId) {
  state.classementBook = bookId;
  if (dom.btnClassementBookCartes) dom.btnClassementBookCartes.classList.toggle('active', bookId === 'cartes');
  if (dom.btnClassementBookPieces) dom.btnClassementBookPieces.classList.toggle('active', bookId === 'pieces');
  if (dom.btnClassementBookTours) dom.btnClassementBookTours.classList.toggle('active', bookId === 'tours');
  if (dom.btnClassementBookToursPieces) dom.btnClassementBookToursPieces.classList.toggle('active', bookId === 'tours_pieces');
  if (dom.classementSearchInput) {
    dom.classementSearchInput.value = '';
    state.classementSearchQuery = '';
    if (dom.btnClassementSearchClear) dom.btnClassementSearchClear.style.display = 'none';
    if (dom.classementSearchBadge) dom.classementSearchBadge.style.display = 'none';
  }
  renderClassementTree();
}

function getClassementStorageKey(bookId) {
  return `livre_magie_classement_v1_${bookId}`;
}

function loadClassementData(bookId) {
  if (state.classementData[bookId]) return state.classementData[bookId];
  const raw = localStorage.getItem(getClassementStorageKey(bookId));
  if (raw) {
    try {
      state.classementData[bookId] = JSON.parse(raw);
      return state.classementData[bookId];
    } catch (e) {
      console.warn('Erreur lecture localStorage classement:', e);
    }
  }
  state.classementData[bookId] = {
    bookId,
    lastUpdated: new Date().toISOString(),
    sections: {}
  };
  return state.classementData[bookId];
}

function saveClassementData(bookId) {
  const data = state.classementData[bookId] || loadClassementData(bookId);
  data.lastUpdated = new Date().toISOString();
  try {
    localStorage.setItem(getClassementStorageKey(bookId), JSON.stringify(data));
    if (dom.classementSaveStatus) {
      const timeStr = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      dom.classementSaveStatus.textContent = `💾 Enregistré à ${timeStr}`;
    }
  } catch (e) {
    console.error('Erreur sauvegarde classement localStorage:', e);
    showToast('Erreur lors de la sauvegarde du classement');
  }
}

function resetClassement(bookId) {
  const bookName = getBookDisplayTitle(bookId);
  if (!confirm(`Voulez-vous réinitialiser le classement pour "${bookName}" ?\n\nL'ordre d'origine sera restauré et les techniques personnalisées de ce livre seront supprimées.`)) {
    return;
  }
  localStorage.removeItem(getClassementStorageKey(bookId));
  state.classementData[bookId] = null;
  renderClassementTree();
  showToast(`Classement de ${bookName} réinitialisé.`);
}

// =============================================================================
// GESTION DU CLASSEMENT : LECTURE, RECHERCHE RAPIDE ET CACHE DES TECHNIQUES
// =============================================================================
function getOrCreateSectionList(bookId, secKey, partie, chapitre, section) {
  const data = loadClassementData(bookId);
  if (!data.sections) data.sections = {};
  if (data.sections[secKey]) {
    return data.sections[secKey];
  }

  // Indexation instantanée pour éliminer toute latence
  if (!state._bookTechMap) state._bookTechMap = {};
  if (!state._bookTechMap[bookId]) {
    const book = state.booksData ? state.booksData[bookId] : null;
    const map = {};
    if (book && book.techniques) {
      book.techniques.forEach(t => {
        const k = `${t.partie}|||${t.chapitre}|||${t.section}`;
        if (!map[k]) map[k] = [];
        map[k].push({
          id: t.id,
          nom: t.nom,
          partie: t.partie,
          chapitre: t.chapitre,
          section: t.section,
          description: t.description || '',
          pdf_ref: t.pdf_ref || '',
          pdf_target: t.pdf_target || '',
          isCustom: false
        });
      });
    }
    state._bookTechMap[bookId] = map;
  }

  const list = state._bookTechMap[bookId][secKey] ? [...state._bookTechMap[bookId][secKey]] : [];
  data.sections[secKey] = list;
  return list;
}

// =============================================================================
// RENDU DE L'ARBORESCENCE DANS L'ONGLET CLASSEMENT (PARTIE > CHAPITRE > SECTION)
// =============================================================================
function renderClassementTree() {
  if (!state.booksData || !state.booksData[state.classementBook]) {
    if (dom.classementTreeWrapper) {
      dom.classementTreeWrapper.innerHTML = '<div class="tree-loading">Chargement des données du classement...</div>';
    }
    return;
  }

  const bookId = state.classementBook;
  const book = state.booksData[bookId];
  const hierarchy = book.hierarchy;

  dom.classementTreeWrapper.innerHTML = '';
  state.isClassementAllExpanded = false;
  if (dom.btnClassementToggleExpand) {
    dom.btnClassementToggleExpand.textContent = 'Tout déplier';
  }

  // Synchronisation visuelle des 3 boutons de livre
  if (dom.btnClassementBookCartes) dom.btnClassementBookCartes.classList.toggle('active', bookId === 'cartes');
  if (dom.btnClassementBookPieces) dom.btnClassementBookPieces.classList.toggle('active', bookId === 'pieces');
  if (dom.btnClassementBookTours) dom.btnClassementBookTours.classList.toggle('active', bookId === 'tours');
  if (dom.btnClassementBookToursPieces) dom.btnClassementBookToursPieces.classList.toggle('active', bookId === 'tours_pieces');

  let partieIndex = 0;
  for (const [partie, chapitres] of Object.entries(hierarchy)) {
    partieIndex++;
    const partieEl = document.createElement('div');
    partieEl.className = 'partie-node';

    let totalPartie = 0;
    for (const [chap, secs] of Object.entries(chapitres)) {
      for (const [sec, count] of Object.entries(secs)) {
        totalPartie += count;
      }
    }

    const pHeader = document.createElement('div');
    pHeader.className = 'partie-header';
    pHeader.innerHTML = `
      <div class="partie-title">
        <span class="chevron">▶</span>
        <span>${escapeHtml(partie)}</span>
      </div>
      <span class="partie-count">${totalPartie}</span>
    `;

    const pBody = document.createElement('div');
    pBody.className = 'partie-body';

    // Premier volet ouvert par défaut pour visibilité immédiate
    if (partieIndex === 1) {
      pHeader.classList.add('open');
      pBody.classList.add('open');
    }

    pHeader.addEventListener('click', () => {
      const isOpen = pHeader.classList.toggle('open');
      pBody.classList.toggle('open', isOpen);
    });

    let chapIndex = 0;
    for (const [chapitre, sections] of Object.entries(chapitres)) {
      chapIndex++;
      const chapEl = document.createElement('div');
      chapEl.className = 'chapitre-node';

      let totalChap = 0;
      for (const [sec, count] of Object.entries(sections)) {
        totalChap += count;
      }

      const cHeader = document.createElement('div');
      cHeader.className = 'chapitre-header';
      cHeader.innerHTML = `
        <div class="partie-title">
          <span class="chevron">▶</span>
          <span>${escapeHtml(chapitre)}</span>
        </div>
        <span class="chapitre-count">${totalChap}</span>
      `;

      const cBody = document.createElement('div');
      cBody.className = 'chapitre-body';

      if (partieIndex === 1 && chapIndex === 1) {
        cHeader.classList.add('open');
        cBody.classList.add('open');
      }

      cHeader.addEventListener('click', () => {
        const isOpen = cHeader.classList.toggle('open');
        cBody.classList.toggle('open', isOpen);
      });

      const secKeys = Object.keys(sections);
      const isSingleGeneral = secKeys.length === 1 && secKeys[0] === 'Général';

      if (isSingleGeneral) {
        // Chapitre à section unique Général : techniques directement accessibles
        const secKey = `${partie}|||${chapitre}|||Général`;

        const topBar = document.createElement('div');
        topBar.className = 'classement-sec-actions';
        topBar.style.padding = '4px 0 8px 0';
        topBar.innerHTML = `
          <button type="button" class="btn-add-section-tech" title="Ajouter une technique dans ce chapitre">➕ Ajouter une technique à ce chapitre</button>
        `;
        topBar.querySelector('.btn-add-section-tech').addEventListener('click', (e) => {
          e.stopPropagation();
          openAddTechModal(bookId, partie, chapitre, 'Général');
        });
        cBody.appendChild(topBar);

        const listContainer = document.createElement('div');
        listContainer.className = 'classement-section-list';
        cBody.appendChild(listContainer);

        renderSectionClassementItems(listContainer, secKey, partie, chapitre, 'Général');
      } else {
        // Chapitre à sous-sections multiples
        for (const [section, count] of Object.entries(sections)) {
          const secKey = `${partie}|||${chapitre}|||${section}`;
          const secEl = document.createElement('div');
          secEl.className = 'section-node';

          const sHeader = document.createElement('div');
          sHeader.className = 'section-header';

          const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);

          sHeader.innerHTML = `
            <div class="partie-title">
              <span class="chevron">▶</span>
              <span>${escapeHtml(section)}</span>
            </div>
            <div class="classement-sec-actions">
              <span class="section-count" id="badge-count-${escapeHtml(secKey).replace(/[^a-zA-Z0-9]/g, '_')}">${list.length}</span>
              <button type="button" class="btn-add-section-tech" title="Ajouter une technique dans cette section">➕ Ajouter</button>
            </div>
          `;

          const sBody = document.createElement('div');
          sBody.className = 'section-body';

          if (partieIndex === 1 && chapIndex === 1) {
            sHeader.classList.add('open');
            sBody.classList.add('open');
          }

          sHeader.addEventListener('click', () => {
            const isOpen = sHeader.classList.toggle('open');
            sBody.classList.toggle('open', isOpen);
          });

          // Bouton Ajouter
          const btnAddSec = sHeader.querySelector('.btn-add-section-tech');
          btnAddSec.addEventListener('click', (e) => {
            e.stopPropagation();
            openAddTechModal(bookId, partie, chapitre, section);
          });

          const listContainer = document.createElement('div');
          listContainer.className = 'classement-section-list';
          sBody.appendChild(listContainer);

          renderSectionClassementItems(listContainer, secKey, partie, chapitre, section);

          secEl.appendChild(sHeader);
          secEl.appendChild(sBody);
          cBody.appendChild(secEl);
        }
      }

      chapEl.appendChild(cHeader);
      chapEl.appendChild(cBody);
      pBody.appendChild(chapEl);
    }

    partieEl.appendChild(pHeader);
    partieEl.appendChild(pBody);
    dom.classementTreeWrapper.appendChild(partieEl);
  }
}

// =============================================================================
// RENDU DES TECHNIQUES PAR SECTION AVEC RANGS, FLÈCHES, DRAG-DROP ET CHUNKING
// =============================================================================
function renderSectionClassementItems(container, secKey, partie, chapitre, section) {
  container.innerHTML = '';
  const bookId = state.classementBook;
  const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);

  // Mettre à jour le badge de compteur
  const badgeId = `badge-count-${secKey.replace(/[^a-zA-Z0-9]/g, '_')}`;
  const badgeEl = document.getElementById(badgeId);
  if (badgeEl) badgeEl.textContent = list.length;

  if (list.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'tree-empty-note';
    empty.style.display = 'flex';
    empty.style.justifyContent = 'space-between';
    empty.style.alignItems = 'center';
    empty.innerHTML = `
      <span>Aucune technique répertoriée dans cette section.</span>
      <button type="button" class="btn btn-outline btn-sm">+ Ajouter</button>
    `;
    empty.querySelector('button').addEventListener('click', () => {
      openAddTechModal(bookId, partie, chapitre, section);
    });
    container.appendChild(empty);
    return;
  }

  const CHUNK_SIZE = 50;
  let currentlyRendered = 0;

  function renderNextClassementChunk() {
    const nextChunk = list.slice(currentlyRendered, currentlyRendered + CHUNK_SIZE);
    nextChunk.forEach((tech, localIdx) => {
      const index = currentlyRendered + localIdx;
      const item = createClassementItemElement(tech, index, list, secKey, partie, chapitre, section, container);
      container.appendChild(item);
    });
    currentlyRendered += nextChunk.length;
  }

  // Rendu initial du premier lot
  renderNextClassementChunk();

  // Si d'autres techniques restent, ajouter le contrôleur de chargement progressif
  if (currentlyRendered < list.length) {
    const loadMoreBar = document.createElement('div');
    loadMoreBar.className = 'tree-load-more-bar';

    const btnMore = document.createElement('button');
    btnMore.type = 'button';
    btnMore.className = 'btn-load-more';
    btnMore.textContent = `Afficher 50 de plus (${currentlyRendered} / ${list.length})...`;

    const btnAll = document.createElement('button');
    btnAll.type = 'button';
    btnAll.className = 'btn-load-more';
    btnAll.textContent = `Tout afficher (${list.length})`;

    btnMore.addEventListener('click', (e) => {
      e.stopPropagation();
      loadMoreBar.remove();
      renderNextClassementChunk();
      if (currentlyRendered < list.length) {
        btnMore.textContent = `Afficher 50 de plus (${currentlyRendered} / ${list.length})...`;
        container.appendChild(loadMoreBar);
      }
    });

    btnAll.addEventListener('click', (e) => {
      e.stopPropagation();
      loadMoreBar.remove();
      while (currentlyRendered < list.length) {
        renderNextClassementChunk();
      }
    });

    loadMoreBar.appendChild(btnMore);
    loadMoreBar.appendChild(btnAll);
    container.appendChild(loadMoreBar);
  }
}

function createClassementItemElement(tech, index, list, secKey, partie, chapitre, section, container) {
  const item = document.createElement('div');
  item.className = 'classement-item';
  item.draggable = true;
  item.dataset.secKey = secKey;
  item.dataset.index = index;
  item.dataset.techName = (tech.nom || '').toLowerCase();

  const numSources = (tech.sources && tech.sources.length) || 1;
  const targetPage = extractPageNumber(tech);
  const pageText = numSources > 1 ? `📚 ${numSources} sources PDF` : (targetPage ? `Page ${targetPage}` : '');
  const customBadgeHtml = tech.isCustom ? `<span class="badge-custom">✨ Personnalisée</span>` : '';

  item.innerHTML = `
    <div class="classement-drag-handle" title="Glisser-déposer pour changer la position">⠿</div>
    <div class="classement-rank-badge">#${index + 1}</div>
    <div class="classement-tech-info" title="Cliquer pour afficher la fiche détaillée et ouvrir le PDF">
      <div class="classement-tech-title">
        <span>${escapeHtml(tech.nom)}</span>
        ${customBadgeHtml}
      </div>
      <div class="classement-tech-sub">
        ${pageText ? `<span>${escapeHtml(pageText)}</span>` : ''}
        ${tech.pdf_ref ? `<span>· ${escapeHtml(tech.pdf_ref)}</span>` : ''}
      </div>
    </div>
    <div class="classement-tech-actions">
      <button type="button" class="btn-rank-move btn-move-up" title="Monter d'un rang" ${index === 0 ? 'disabled style="opacity:0.3;cursor:default;"' : ''}>▲</button>
      <button type="button" class="btn-rank-move btn-move-down" title="Descendre d'un rang" ${index === list.length - 1 ? 'disabled style="opacity:0.3;cursor:default;"' : ''}>▼</button>
      <button type="button" class="btn-rank-pos" title="Définir un rang précis (ex: passer en #1)">#</button>
      <button type="button" class="btn-rank-delete" title="${tech.isCustom ? 'Supprimer cette technique' : 'Retirer du classement personnalisé'}">🗑️</button>
    </div>
  `;

  // Clic sur l'info pour ouvrir la fiche et le PDF
  item.querySelector('.classement-tech-info').addEventListener('click', (e) => {
    e.stopPropagation();
    openTechniqueDetail(tech);
  });

  // Bouton Monter
  const btnUp = item.querySelector('.btn-move-up');
  if (index > 0) {
    btnUp.addEventListener('click', (e) => {
      e.stopPropagation();
      moveTech(secKey, partie, chapitre, section, container, index, index - 1);
    });
  }

  // Bouton Descendre
  const btnDown = item.querySelector('.btn-move-down');
  if (index < list.length - 1) {
    btnDown.addEventListener('click', (e) => {
      e.stopPropagation();
      moveTech(secKey, partie, chapitre, section, container, index, index + 1);
    });
  }

  // Bouton Rang précis (#)
  item.querySelector('.btn-rank-pos').addEventListener('click', (e) => {
    e.stopPropagation();
    promptChangeRank(secKey, partie, chapitre, section, container, index, tech);
  });

  // Bouton Supprimer (🗑️)
  item.querySelector('.btn-rank-delete').addEventListener('click', (e) => {
    e.stopPropagation();
    deleteOrRemoveTech(secKey, partie, chapitre, section, container, index, tech);
  });

  // Événements Drag & Drop
  item.addEventListener('dragstart', (e) => {
    draggedItemInfo = { secKey, index, bookId: state.classementBook };
    item.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', index.toString());
  });

  item.addEventListener('dragend', () => {
    item.classList.remove('dragging');
    container.querySelectorAll('.classement-item').forEach(el => el.classList.remove('drag-over'));
    draggedItemInfo = null;
  });

  item.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (draggedItemInfo && draggedItemInfo.secKey === secKey) {
      e.dataTransfer.dropEffect = 'move';
      item.classList.add('drag-over');
    }
  });

  item.addEventListener('dragleave', () => {
    item.classList.remove('drag-over');
  });

  item.addEventListener('drop', (e) => {
    e.preventDefault();
    item.classList.remove('drag-over');
    if (draggedItemInfo && draggedItemInfo.secKey === secKey && draggedItemInfo.index !== index) {
      moveTech(secKey, partie, chapitre, section, container, draggedItemInfo.index, index);
    }
  });

  return item;
}

function moveTech(secKey, partie, chapitre, section, container, fromIndex, toIndex) {
  const bookId = state.classementBook;
  const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);
  if (fromIndex < 0 || fromIndex >= list.length || toIndex < 0 || toIndex >= list.length) return;

  const [moved] = list.splice(fromIndex, 1);
  list.splice(toIndex, 0, moved);

  saveClassementData(bookId);
  renderSectionClassementItems(container, secKey, partie, chapitre, section);
  showToast(`"${moved.nom}" déplacé au rang #${toIndex + 1}`);
}

function promptChangeRank(secKey, partie, chapitre, section, container, currentIndex, tech) {
  const bookId = state.classementBook;
  const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);
  const input = prompt(`Entrez le nouveau rang souhaité pour :\n"${tech.nom}"\n(Valeur entre 1 et ${list.length}) :`, currentIndex + 1);
  if (!input) return;

  const rank = parseInt(input.trim(), 10);
  if (isNaN(rank) || rank < 1 || rank > list.length) {
    alert(`Veuillez entrer un nombre valide entre 1 et ${list.length}.`);
    return;
  }

  const targetIndex = rank - 1;
  if (targetIndex === currentIndex) return;

  moveTech(secKey, partie, chapitre, section, container, currentIndex, targetIndex);
}

function deleteOrRemoveTech(secKey, partie, chapitre, section, container, index, tech) {
  const bookId = state.classementBook;
  const promptText = tech.isCustom
    ? `Supprimer définitivement la technique personnalisée :\n"${tech.nom}" ?`
    : `Retirer "${tech.nom}" de votre classement personnalisé pour cette section ?\n(Elle reste présente dans le catalogue officiel)`;

  if (!confirm(promptText)) return;

  const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);
  const [removed] = list.splice(index, 1);

  saveClassementData(bookId);
  renderSectionClassementItems(container, secKey, partie, chapitre, section);
  showToast(`"${removed.nom}" retiré du classement.`);
}

function openAddTechModal(bookId, defaultPartie, defaultChapitre, defaultSection) {
  if (!dom.modalAddTechnique) return;
  dom.formAddTechnique.reset();

  const targetBook = bookId || 'cartes';
  if (dom.formTechBook) dom.formTechBook.value = targetBook;
  populateAddModalParties(targetBook, defaultPartie);

  if (defaultPartie) {
    populateAddModalChapitres(targetBook, defaultPartie, defaultChapitre);
    if (defaultChapitre) {
      populateAddModalSections(targetBook, defaultPartie, defaultChapitre, defaultSection);
    }
  }

  dom.modalAddTechnique.style.display = 'flex';
  if (dom.formTechName) dom.formTechName.focus();
}

function closeAddTechModal() {
  if (dom.modalAddTechnique) dom.modalAddTechnique.style.display = 'none';
}

function populateAddModalParties(bookId, selectedPartie) {
  if (!dom.formTechPartie || !state.booksData || !state.booksData[bookId]) return;
  const hierarchy = state.booksData[bookId].hierarchy;
  dom.formTechPartie.innerHTML = '';

  const parties = Object.keys(hierarchy);
  parties.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    if (selectedPartie && p === selectedPartie) opt.selected = true;
    dom.formTechPartie.appendChild(opt);
  });

  const currentPartie = dom.formTechPartie.value;
  populateAddModalChapitres(bookId, currentPartie);
}

function populateAddModalChapitres(bookId, partie, selectedChapitre) {
  if (!dom.formTechChapitre || !state.booksData || !state.booksData[bookId]) return;
  const hierarchy = state.booksData[bookId].hierarchy;
  dom.formTechChapitre.innerHTML = '';

  const chapMap = hierarchy[partie] || {};
  const chapitres = Object.keys(chapMap);
  chapitres.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    if (selectedChapitre && c === selectedChapitre) opt.selected = true;
    dom.formTechChapitre.appendChild(opt);
  });

  const currentChapitre = dom.formTechChapitre.value;
  populateAddModalSections(bookId, partie, currentChapitre);
}

function populateAddModalSections(bookId, partie, chapitre, selectedSection) {
  if (!dom.formTechSection || !state.booksData || !state.booksData[bookId]) return;
  const hierarchy = state.booksData[bookId].hierarchy;
  dom.formTechSection.innerHTML = '';

  const secMap = (hierarchy[partie] && hierarchy[partie][chapitre]) ? hierarchy[partie][chapitre] : {};
  const sections = Object.keys(secMap);
  sections.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = s;
    if (selectedSection && s === selectedSection) opt.selected = true;
    dom.formTechSection.appendChild(opt);
  });
}

function handleAddTechniqueSubmit(e) {
  e.preventDefault();
  const bookId = dom.formTechBook.value;
  const partie = dom.formTechPartie.value;
  const chapitre = dom.formTechChapitre.value;
  const section = dom.formTechSection.value;
  const name = dom.formTechName.value.trim();
  const page = dom.formTechPage.value.trim();
  const source = dom.formTechSource.value.trim();
  const effet = dom.formTechEffet.value.trim();
  const methode = dom.formTechMethode.value.trim();
  const position = dom.formTechPosition.value;

  if (!name) {
    alert('Veuillez renseigner le nom de la technique.');
    return;
  }

  let desc = '';
  if (effet && methode) {
    desc = `[Effet] ${effet} | [Méthode] ${methode}`;
  } else if (effet) {
    desc = `[Effet] ${effet}`;
  } else if (methode) {
    desc = `[Méthode] ${methode}`;
  }

  const customTech = {
    id: `CUSTOM_${bookId.toUpperCase()}_${Date.now()}`,
    nom: name,
    partie: partie,
    chapitre: chapitre,
    section: section,
    description: desc,
    pdf_ref: source ? `${source}${page ? ', p. ' + page : ''}` : (page ? `Page ${page}` : 'Ajout personnel'),
    pdf_target: '',
    isCustom: true
  };

  const secKey = `${partie}|||${chapitre}|||${section}`;
  const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);

  if (position === 'start') {
    list.unshift(customTech);
  } else {
    list.push(customTech);
  }

  saveClassementData(bookId);
  closeAddTechModal();

  if (state.classementBook === bookId) {
    renderClassementTree();
  } else {
    switchClassementBook(bookId);
  }

  showToast(`✨ Technique "${name}" ajoutée avec succès au classement !`);
}

function openExportModal() {
  if (!dom.modalExportExcel) return;
  if (dom.exportModalBookTitle) {
    dom.exportModalBookTitle.textContent = getBookDisplayTitle(state.classementBook);
  }
  dom.modalExportExcel.style.display = 'flex';
}

function closeExportModal() {
  if (dom.modalExportExcel) dom.modalExportExcel.style.display = 'none';
}

function exportBookToExcel(bookId) {
  if (typeof XLSX === 'undefined') {
    alert("Le module Excel (XLSX) est en cours de chargement ou indisponible.");
    return;
  }

  const book = state.booksData ? state.booksData[bookId] : null;
  if (!book) return;

  const rows = [];
  for (const [partie, chapMap] of Object.entries(book.hierarchy)) {
    for (const [chapitre, secMap] of Object.entries(chapMap)) {
      for (const section of Object.keys(secMap)) {
        const secKey = `${partie}|||${chapitre}|||${section}`;
        const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);
        list.forEach((t, idx) => {
          rows.push({
            "Rang": idx + 1,
            "Partie": partie,
            "Chapitre": chapitre,
            "Section": section,
            "Nom technique / tour": t.nom || '',
            "Description": t.description || '',
            "Référence PDF et Page": t.pdf_ref || '',
            "Lien vers la page du pdf": t.pdf_target || '',
            "Type": t.isCustom ? "Ajout personnalisé" : "Catalogue officiel"
          });
        });
      }
    }
  }

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(rows);
  ws['!cols'] = [
    { wch: 8 },
    { wch: 28 },
    { wch: 28 },
    { wch: 32 },
    { wch: 42 },
    { wch: 65 },
    { wch: 45 },
    { wch: 50 },
    { wch: 22 }
  ];

  const sheetTitle = (book.title || bookId).substring(0, 31);
  XLSX.utils.book_append_sheet(wb, ws, sheetTitle);

  const today = new Date().toISOString().slice(0, 10);
  const fileName = `Classement_${sheetTitle.replace(/[^a-zA-Z0-9_-]/g, '_')}_${today}.xlsx`;
  XLSX.writeFile(wb, fileName);

  closeExportModal();
  showToast(`📥 Fichier Excel "${fileName}" téléchargé avec succès !`);
}

function exportAllBooksToExcel() {
  if (typeof XLSX === 'undefined') {
    alert("Le module Excel (XLSX) est en cours de chargement ou indisponible.");
    return;
  }

  const wb = XLSX.utils.book_new();
  const bookIds = ['cartes', 'pieces', 'tours', 'tours_pieces'];

  bookIds.forEach(bookId => {
    const book = state.booksData ? state.booksData[bookId] : null;
    if (!book) return;

    const rows = [];
    for (const [partie, chapMap] of Object.entries(book.hierarchy)) {
      for (const [chapitre, secMap] of Object.entries(chapMap)) {
        for (const section of Object.keys(secMap)) {
          const secKey = `${partie}|||${chapitre}|||${section}`;
          const list = getOrCreateSectionList(bookId, secKey, partie, chapitre, section);
          list.forEach((t, idx) => {
            rows.push({
              "Rang": idx + 1,
              "Partie": partie,
              "Chapitre": chapitre,
              "Section": section,
              "Nom technique / tour": t.nom || '',
              "Description": t.description || '',
              "Référence PDF et Page": t.pdf_ref || '',
              "Lien vers la page du pdf": t.pdf_target || '',
              "Type": t.isCustom ? "Ajout personnalisé" : "Catalogue officiel"
            });
          });
        }
      }
    }

    const ws = XLSX.utils.json_to_sheet(rows);
    ws['!cols'] = [
      { wch: 8 },
      { wch: 28 },
      { wch: 28 },
      { wch: 32 },
      { wch: 42 },
      { wch: 65 },
      { wch: 45 },
      { wch: 50 },
      { wch: 22 }
    ];

    let tabName = 'Techniques Cartes';
    if (bookId === 'pieces') tabName = 'Techniques Pièces';
    else if (bookId === 'tours') tabName = 'Tours de Cartes';
    else if (bookId === 'tours_pieces') tabName = 'Tours de Pièces';
    XLSX.utils.book_append_sheet(wb, ws, tabName);
  });

  const today = new Date().toISOString().slice(0, 10);
  const fileName = `Classement_Magie_Complet_4_Livres_${today}.xlsx`;
  XLSX.writeFile(wb, fileName);

  closeExportModal();
  showToast(`📚 Fichier Excel complet des 4 livres téléchargé !`);
}

function getBookDisplayTitle(bookId) {
  if (bookId === 'cartes') return 'Techniques Cartes';
  if (bookId === 'pieces') return 'Techniques Pièces';
  if (bookId === 'tours') return 'Tours de Cartes';
  if (bookId === 'tours_pieces') return 'Tours de Pièces';
  return 'Livre';
}

function showToast(message) {
  if (!dom.classementToast) return;
  dom.classementToast.textContent = message;
  dom.classementToast.style.display = 'block';
  clearTimeout(dom.classementToast._timer);
  dom.classementToast._timer = setTimeout(() => {
    dom.classementToast.style.display = 'none';
  }, 3200);
}

function toggleAllClassementNodes(open) {
  if (!dom.classementTreeWrapper) return;
  const headers = dom.classementTreeWrapper.querySelectorAll('.partie-header, .chapitre-header, .section-header');
  const bodies = dom.classementTreeWrapper.querySelectorAll('.partie-body, .chapitre-body, .section-body');
  headers.forEach(h => h.classList.toggle('open', open));
  bodies.forEach(b => b.classList.toggle('open', open));
}

function filterClassementTree(query) {
  if (!dom.classementTreeWrapper) return;
  const items = dom.classementTreeWrapper.querySelectorAll('.classement-item');
  if (!query) {
    items.forEach(el => el.style.display = 'flex');
    if (dom.classementSearchBadge) dom.classementSearchBadge.style.display = 'none';
    return;
  }

  let matchCount = 0;
  items.forEach(el => {
    const nameMatch = el.dataset.techName && el.dataset.techName.includes(query);
    el.style.display = nameMatch ? 'flex' : 'none';
    if (nameMatch) matchCount++;
  });

  if (dom.classementSearchBadge) {
    dom.classementSearchBadge.style.display = 'inline-block';
    dom.classementSearchBadge.textContent = `${matchCount} résultat${matchCount > 1 ? 's' : ''}`;
  }

  if (query.length >= 2) {
    toggleAllClassementNodes(true);
  }
}

