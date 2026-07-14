#!/usr/bin/env node
// Fetch a public HTML page or PDF to a cited local Markdown artifact.
import { Readability } from '@mozilla/readability';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { JSDOM } from 'jsdom';
import TurndownService from 'turndown';

const MAX_RESPONSE_BYTES = 5 * 1024 * 1024;

export function htmlToMarkdown(html, url) {
  const dom = new JSDOM(html, { url });
  dom.window.document.querySelectorAll('nav, header, footer, aside').forEach((node) => node.remove());
  const article = new Readability(dom.window.document).parse();
  if (!article?.content) throw new Error('could not extract readable article content');
  const turndown = new TurndownService({ codeBlockStyle: 'fenced', headingStyle: 'atx' });
  const markdown = turndown.turndown(article.content).trim();
  const title = article.title?.trim() || dom.window.document.title?.trim() || 'document';
  return `# ${title}\n\n${markdown}`;
}

export async function fetchToMarkdown(url, outputPath) {
  const output = resolve(outputPath);
  const response = await fetch(url, { headers: { 'user-agent': 'service-graph-toolkit/1.0' }, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const type = response.headers.get('content-type') || '';
  const buffer = Buffer.from(await response.arrayBuffer());
  if (buffer.length > MAX_RESPONSE_BYTES) throw new Error('response exceeds 5 MiB limit');
  let body;
  if (type.includes('pdf') || new URL(url).pathname.endsWith('.pdf')) {
    const pdfPath = output.endsWith('.md') ? `${output.slice(0, -2)}pdf` : `${output}.pdf`;
    await mkdir(resolve(pdfPath, '..'), { recursive: true });
    await writeFile(pdfPath, buffer);
    body = `PDF downloaded to \`${pdfPath}\`. Extract text with a local PDF tool before analysis.\n\nSaved binary size: ${buffer.length} bytes.`;
  } else {
    body = htmlToMarkdown(buffer.toString('utf8'), url);
  }
  await mkdir(resolve(output, '..'), { recursive: true });
  await writeFile(output, `> Source: ${url}\n> Fetched: ${new Date().toISOString()}\n> Content-Type: ${type}\n\n${body}\n`);
  return output;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [url, ...rest] = process.argv.slice(2);
  const outFlag = rest.indexOf('--out');
  if (!url || outFlag < 0 || !rest[outFlag + 1]) {
    console.error('usage: fetch-web.mjs <url> --out <file.md>');
    process.exit(2);
  }
  console.log(await fetchToMarkdown(url, rest[outFlag + 1]));
}
