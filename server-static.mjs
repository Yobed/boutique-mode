import { createServer } from 'node:http';
import { existsSync, statSync, createReadStream } from 'node:fs';
import { resolve, join, extname } from 'node:path';

const PORT = parseInt(process.env.PORT || '10000', 10);
const HOST = '0.0.0.0';
const OUT_DIR = resolve(process.cwd(), 'out');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.mp4': 'video/mp4',
};

const server = createServer((req, res) => {
  const urlPath = (req.url || '/').split('?')[0];

  // Health check endpoint pour Render et UptimeRobot
  if (urlPath === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok', service: 'elsi-boutique', timestamp: new Date().toISOString() }));
  }

  // Résolution du fichier statique
  let filePath = join(OUT_DIR, decodeURIComponent(urlPath));

  // Traitement si dossier ou racine
  if (urlPath === '/' || urlPath === '') {
    filePath = join(OUT_DIR, 'index.html');
  } else if (!extname(filePath)) {
    // Si pas d'extension, tester .html direct ou /index.html
    if (existsSync(`${filePath}.html`)) {
      filePath = `${filePath}.html`;
    } else if (existsSync(join(filePath, 'index.html'))) {
      filePath = join(filePath, 'index.html');
    }
  }

  if (existsSync(filePath) && statSync(filePath).isFile()) {
    const ext = extname(filePath).toLowerCase();
    const mime = MIME_TYPES[ext] || 'application/octet-stream';
    const headers = { 'Content-Type': mime };

    // Support RSC Next.js pour la navigation client
    if (ext === '.txt') {
      headers['Content-Type'] = 'text/x-component; charset=utf-8';
      headers['Vary'] = 'RSC, Next-Router-State-Tree, Next-Router-Prefetch';
    }

    // Cache control
    if (urlPath.startsWith('/_next/static/') || ext === '.glb') {
      headers['Cache-Control'] = 'public, max-age=31536000, immutable';
    } else {
      headers['Cache-Control'] = 'public, max-age=0, must-revalidate';
    }

    res.writeHead(200, headers);
    return createReadStream(filePath).pipe(res);
  }

  // Fallback 404
  const notFoundPath = join(OUT_DIR, '404.html');
  if (existsSync(notFoundPath)) {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    return createReadStream(notFoundPath).pipe(res);
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

server.listen(PORT, HOST, () => {
  console.log(`✅ Boutique ELSI en ligne sur http://${HOST}:${PORT} (Static Next.js SSG)`);
});
