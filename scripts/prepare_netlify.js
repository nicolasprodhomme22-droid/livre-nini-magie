const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DIST = path.join(ROOT, 'dist');
const PUBLIC = path.join(ROOT, 'app', 'public');
const DATA = path.join(ROOT, 'app', 'data');
const SOURCES_LISIBLES = path.join(ROOT, 'Sources', 'sources_lisibles');

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const item of fs.readdirSync(src)) {
      copyRecursive(path.join(src, item), path.join(dest, item));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

console.log('🚀 [Netlify Build] Préparation du dossier de déploiement dist/ ...');

// 1. Reset dist
if (fs.existsSync(DIST)) {
  fs.rmSync(DIST, { recursive: true, force: true });
}
fs.mkdirSync(DIST, { recursive: true });

// 2. Copier app/public vers dist
console.log('📦 Copie des fichiers publics frontend...');
copyRecursive(PUBLIC, DIST);

// 3. Copier app/data/data_cache.json vers dist/data/data_cache.json
console.log('💾 Copie du cache des données (data_cache.json)...');
const destData = path.join(DIST, 'data');
fs.mkdirSync(destData, { recursive: true });
fs.copyFileSync(path.join(DATA, 'data_cache.json'), path.join(destData, 'data_cache.json'));

// 4. Copier Sources/sources_lisibles vers dist/Sources/sources_lisibles
console.log('📑 Copie des 19 PDF certifiés de sources_lisibles...');
const destSources = path.join(DIST, 'Sources', 'sources_lisibles');
fs.mkdirSync(destSources, { recursive: true });
copyRecursive(SOURCES_LISIBLES, destSources);

// 5. Créer .nojekyll pour désactiver le traitement Jekyll sur GitHub Pages
fs.writeFileSync(path.join(DIST, '.nojekyll'), '');

console.log('✅ [Netlify Build] Déploiement dist/ prêt avec succès !');
