#!/usr/bin/env node
// Fetch a public HTML page or PDF to a cited local Markdown artifact.
import { mkdir, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
const [url, ...rest] = process.argv.slice(2);
const outFlag = rest.indexOf('--out');
if (!url || outFlag < 0 || !rest[outFlag + 1]) {
  console.error('usage: fetch-web.mjs <url> --out <file.md>'); process.exit(2);
}
const output = resolve(rest[outFlag + 1]);
const response = await fetch(url, { headers: { 'user-agent': 'service-graph-toolkit/1.0' }, signal: AbortSignal.timeout(30000) });
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const type = response.headers.get('content-type') || '';
const buffer = Buffer.from(await response.arrayBuffer());
if (buffer.length > 5 * 1024 * 1024) throw new Error('response exceeds 5 MiB limit');
let body;
if (type.includes('pdf') || new URL(url).pathname.endsWith('.pdf')) {
  const pdfPath = output.endsWith('.md') ? `${output.slice(0, -3)}pdf` : `${output}.pdf`;
  await mkdir(resolve(pdfPath, '..'), { recursive: true });
  await writeFile(pdfPath, buffer);
  body = `PDF downloaded to \`${pdfPath}\`. Extract text with a local PDF tool before analysis.\n\nSaved binary size: ${buffer.length} bytes.`;
} else {
  const html = buffer.toString('utf8');
  const title = (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || 'document').replace(/<[^>]+>/g, '').trim();
  const text = html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, '').replace(/<[^>]+>/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  body = `# ${title}\n\n${text}`;
}
await mkdir(resolve(output, '..'), { recursive: true });
await writeFile(output, `> Source: ${url}\n> Fetched: ${new Date().toISOString()}\n> Content-Type: ${type}\n\n${body}\n`);
console.log(output);
