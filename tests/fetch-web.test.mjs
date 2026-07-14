import assert from 'node:assert/strict';
import { mkdtemp, readFile } from 'node:fs/promises';
import http from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { htmlToMarkdown, fetchToMarkdown } from '../scripts/fetch-web.mjs';

test('htmlToMarkdown retains article structure, links, and code blocks', () => {
  const markdown = htmlToMarkdown('<html><head><title>Useful article</title></head><body><nav>Navigation</nav><article><h1>Useful article</h1><p>First <a href="/guide">link</a>.</p><h2>Details</h2><pre><code>const answer = 42;</code></pre></article></body></html>', 'https://example.test/posts/1');
  assert.match(markdown, /^# Useful article/m);
  assert.match(markdown, /\[link\]\(https:\/\/example\.test\/guide\)/);
  assert.match(markdown, /## Details/);
  assert.match(markdown, /```[\s\S]*const answer = 42;[\s\S]*```/);
  assert.doesNotMatch(markdown, /Navigation/);
});

test('fetchToMarkdown writes cited Markdown and a PDF sidecar', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'fetch-web-'));
  const pdf = Buffer.from('%PDF-1.4 sample');
  const server = await new Promise((resolve) => {
    const instance = http.createServer((request, response) => {
      response.writeHead(200, { 'content-type': 'application/pdf' }); response.end(pdf);
    }).listen(0, '127.0.0.1', () => resolve(instance));
  });
  try {
    const output = join(directory, 'report.md');
    const url = `http://127.0.0.1:${server.address().port}/report.pdf`;
    await fetchToMarkdown(url, output);
    assert.ok((await readFile(output, 'utf8')).includes(`> Source: ${url}`));
    assert.deepEqual(await readFile(join(directory, 'report.pdf')), pdf);
  } finally {
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
});
