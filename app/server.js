const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const { exec } = require('child_process');

const PORT = process.env.PORT || 3000;
const BASE_DIR = path.resolve(__dirname, '..');
const SOURCES_DIR = path.resolve(BASE_DIR, 'Sources');
const PUBLIC_DIR = path.resolve(__dirname, 'public');
const DATA_CACHE_PATH = path.resolve(__dirname, 'data', 'data_cache.json');

let database = null;

function loadDatabase() {
    try {
        if (fs.existsSync(DATA_CACHE_PATH)) {
            const raw = fs.readFileSync(DATA_CACHE_PATH, 'utf-8');
            database = JSON.parse(raw);
            const bookCount = Object.keys(database.books || {}).length;
            console.log(`[DB] Base chargée en mémoire : ${bookCount} livres.`);
        } else {
            console.warn('[DB] data_cache.json introuvable. Lancement automatique de sync_engine.py...');
            runSyncAgent();
        }
    } catch (e) {
        console.error('[DB] Erreur chargement base:', e);
    }
}

function runSyncAgent(callback) {
    const scriptPath = path.join(BASE_DIR, '.agents', 'skills', 'magic-db-sync', 'scripts', 'sync_engine.py');
    console.log('[SYNC] Exécution de sync_engine.py...');
    exec(`python "${scriptPath}"`, { maxBuffer: 1024 * 1024 * 10 }, (err, stdout, stderr) => {
        if (err) {
            console.error('[SYNC] Erreur exécution sync_engine.py:', err);
            if (callback) callback(false, err.message);
            return;
        }
        console.log('[SYNC] sync_engine.py exécuté avec succès.');
        loadDatabase();
        if (callback) callback(true);
    });
}

// Chargement initial
loadDatabase();

const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

/**
 * Envoie un fichier avec support natif du streaming et des requêtes Range (HTTP 206)
 * Essentiel pour la fluidité d'affichage des gros fichiers PDF (jusqu'à 65 Mo).
 */
function serveFileWithRange(req, res, filePath, contentType) {
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
            res.end('404 Fichier non trouvé');
            return;
        }

        const fileSize = stats.size;
        const range = req.headers.range;

        const isDownload = req.url.includes('download=1');
        if (isDownload) {
            res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(path.basename(filePath))}"`);
        }

        if (range) {
            const parts = range.replace(/bytes=/, '').split('-');
            const start = parseInt(parts[0], 10);
            const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

            if (start >= fileSize || end >= fileSize || start > end) {
                res.writeHead(416, {
                    'Content-Range': `bytes */${fileSize}`,
                    'Content-Type': 'text/plain; charset=utf-8'
                });
                res.end('416 Plage non satisfaisante');
                return;
            }

            const chunkSize = (end - start) + 1;
            res.writeHead(206, {
                'Content-Range': `bytes ${start}-${end}/${fileSize}`,
                'Accept-Ranges': 'bytes',
                'Content-Length': chunkSize,
                'Content-Type': contentType
            });

            const stream = fs.createReadStream(filePath, { start, end });
            stream.on('error', (streamErr) => {
                console.error('[STREAM] Erreur de lecture segmentée:', streamErr);
                if (!res.headersSent) res.writeHead(500);
                res.end();
            });
            stream.pipe(res);
        } else {
            res.writeHead(200, {
                'Content-Length': fileSize,
                'Accept-Ranges': 'bytes',
                'Content-Type': contentType
            });

            const stream = fs.createReadStream(filePath);
            stream.on('error', (streamErr) => {
                console.error('[STREAM] Erreur de lecture:', streamErr);
                if (!res.headersSent) res.writeHead(500);
                res.end();
            });
            stream.pipe(res);
        }
    });
}

const server = http.createServer((req, res) => {
    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    let pathname = decodeURIComponent(parsedUrl.pathname);

    // En-têtes CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Range');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // --- API ROUTES ---

    // 1. Métadonnées des livres et arborescences
    if (pathname === '/api/books' && req.method === 'GET') {
        if (!database) loadDatabase();
        const summary = Object.values(database ? database.books || {} : {}).map(b => ({
            id: b.id,
            title: b.title,
            icon: b.icon,
            count: b.count,
            hierarchy: b.hierarchy
        }));
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ last_sync: database ? database.last_sync : '', books: summary }));
        return;
    }

    // 2. Consultation et filtrage d'un livre
    if (pathname.startsWith('/api/book/') && req.method === 'GET') {
        const bookId = pathname.replace('/api/book/', '').split('/')[0];
        if (!database || !database.books || !database.books[bookId]) {
            res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify({ error: 'Livre non trouvé' }));
            return;
        }

        const book = database.books[bookId];
        const query = (parsedUrl.searchParams.get('q') || '').toLowerCase().trim();
        const partieFilter = parsedUrl.searchParams.get('partie');
        const chapFilter = parsedUrl.searchParams.get('chapitre');
        const secFilter = parsedUrl.searchParams.get('section');
        const page = parseInt(parsedUrl.searchParams.get('page') || '1', 10);
        const limit = parseInt(parsedUrl.searchParams.get('limit') || '50', 10);

        let filtered = book.techniques;

        if (partieFilter) {
            filtered = filtered.filter(t => t.partie === partieFilter);
        }
        if (chapFilter) {
            filtered = filtered.filter(t => t.chapitre === chapFilter);
        }
        if (secFilter) {
            filtered = filtered.filter(t => t.section === secFilter);
        }
        if (query) {
            filtered = filtered.filter(t => 
                (t.nom && t.nom.toLowerCase().includes(query)) ||
                (t.description && t.description.toLowerCase().includes(query)) ||
                (t.pdf_ref && t.pdf_ref.toLowerCase().includes(query)) ||
                (t.id && t.id.toLowerCase().includes(query))
            );
        }

        const isAll = parsedUrl.searchParams.get('all') === '1';
        const total = filtered.length;
        const paginated = isAll ? filtered : filtered.slice((page - 1) * limit, (page - 1) * limit + limit);

        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({
            book_id: bookId,
            title: book.title,
            icon: book.icon,
            total,
            page: isAll ? 1 : page,
            limit: isAll ? total : limit,
            techniques: paginated
        }));
        return;
    }

    // 3. Déclenchement de la synchronisation (Agent 2)
    if (pathname === '/api/sync' && req.method === 'POST') {
        runSyncAgent((success, err) => {
            if (success) {
                res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({
                    success: true,
                    message: 'Synchronisation réussie',
                    last_sync: database ? database.last_sync : ''
                }));
            } else {
                res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ success: false, error: err }));
            }
        });
        return;
    }

    // 4. Rechargement passif de la base en mémoire (sans relancer sync_engine)
    if (pathname === '/api/reload' && req.method === 'POST') {
        loadDatabase();
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({
            success: true,
            message: 'Base rechargée en mémoire',
            last_sync: database ? database.last_sync : ''
        }));
        return;
    }

    // --- CACHE APPLICATIF DIRECT ---
    if (pathname === '/data/data_cache.json' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        fs.createReadStream(DATA_CACHE_PATH).pipe(res);
        return;
    }

    // --- FICHIERS STATIQUES SOURCES (PDF) ---
    if (pathname.startsWith('/Sources/')) {
        const relativeSubPath = pathname.slice('/Sources/'.length);
        const resolvedPath = path.resolve(SOURCES_DIR, relativeSubPath);

        // Sécurité : Vérification stricte anti-traversal
        if (!resolvedPath.startsWith(SOURCES_DIR)) {
            res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
            res.end('403 Accès interdit');
            return;
        }

        const ext = path.extname(resolvedPath).toLowerCase();
        const mime = MIME_TYPES[ext] || 'application/octet-stream';
        serveFileWithRange(req, res, resolvedPath, mime);
        return;
    }

    // --- FICHIERS STATIQUES FRONTEND (app/public) ---
    let targetFile = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
    const resolvedPublicPath = path.resolve(PUBLIC_DIR, targetFile);

    // Sécurité : Vérification stricte anti-traversal
    if (!resolvedPublicPath.startsWith(PUBLIC_DIR)) {
        res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('403 Accès interdit');
        return;
    }

    fs.stat(resolvedPublicPath, (err, stats) => {
        if (!err && stats.isFile()) {
            const ext = path.extname(resolvedPublicPath).toLowerCase();
            const mime = MIME_TYPES[ext] || 'text/plain; charset=utf-8';
            res.writeHead(200, {
                'Content-Type': mime,
                'Content-Length': stats.size,
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            });
            fs.createReadStream(resolvedPublicPath).pipe(res);
            return;
        }

        // Fallback 404
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('404 Page ou ressource non trouvée');
    });
});

server.listen(PORT, () => {
    console.log(`✨ Application de consultation de magie en ligne sur : http://localhost:${PORT}`);
});
