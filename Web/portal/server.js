import express from 'express';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';

const app = express();
const PORT = process.env.PORT || 8097; // unique default port
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const webRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname));

// Static site
app.use('/', express.static(path.join(webRoot, 'static')));

// Helper to read markdown files from docs
const docsDir = path.join(root, 'docs');

app.get('/api/readme', async (_req, res) => {
  try {
    const md = await readFile(path.join(root, 'README.md'), 'utf-8');
    res.json({ ok: true, markdown: md });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e) });
  }
});

app.get('/api/docs', async (_req, res) => {
  try {
    const entries = await readdir(docsDir, { withFileTypes: true });
    const files = entries.filter(e => e.isFile() && e.name.toLowerCase().endsWith('.md')).map(e => e.name);
    res.json({ ok: true, files });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e) });
  }
});

app.get('/api/docs/:name', async (req, res) => {
  try {
    const safe = req.params.name.replace(/[^a-zA-Z0-9_.-]/g, '');
    const p = path.join(docsDir, safe);
    const md = await readFile(p, 'utf-8');
    res.json({ ok: true, markdown: md });
  } catch (e) {
    res.status(404).json({ ok: false, error: 'Not found' });
  }
});

// Gallery: list images from Comfy output
const outputsDir = path.join(root, 'Tools', 'Comfy', 'ComfyUI-API', 'output');
app.get('/api/gallery', async (_req, res) => {
  try {
    const entries = await readdir(outputsDir, { withFileTypes: true });
    const images = entries.filter(e => e.isFile() && /\.(png|jpg|jpeg|webp)$/i.test(e.name)).map(e => `/gallery/${e.name}`);
    res.json({ ok: true, images });
  } catch (e) {
    res.json({ ok: true, images: [] });
  }
});
app.use('/gallery', express.static(outputsDir));

app.listen(PORT, () => {
  console.log(`Portal listening on http://0.0.0.0:${PORT}`);
});
