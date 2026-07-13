#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import * as z from 'zod';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import yaml from 'yaml';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const projects = resolve(root, 'projects');
const projectId = z.string().regex(/^[a-z0-9][a-z0-9-]*$/, 'invalid project id');
const envelope = (summary, data = {}, sources = [], nextAction) => ({
  summary, data, sources, truncated: false, ...(nextAction ? { nextAction } : {})
});
const text = (value) => ({ content: [{ type: 'text', text: JSON.stringify(value, null, 2) }] });
function project(id) {
  const dir = resolve(projects, id);
  if (!dir.startsWith(`${projects}/`) || !existsSync(resolve(dir, 'project.yaml'))) throw new Error(`unknown project: ${id}`);
  return dir;
}
function load(id) {
  const dir = project(id);
  return { dir, meta: yaml.parse(readFileSync(resolve(dir, 'project.yaml'), 'utf8')), inventory: yaml.parse(readFileSync(resolve(dir, 'inventory.yaml'), 'utf8')) };
}
function run(command, args) {
  return new Promise((resolveRun, reject) => {
    const child = spawn(command, args, { cwd: root, shell: false }); let stdout = '', stderr = '';
    child.stdout.on('data', d => { stdout += d; }); child.stderr.on('data', d => { stderr += d; });
    child.on('error', reject); child.on('close', code => code === 0 ? resolveRun({ stdout, stderr }) : reject(new Error(`${command} failed: ${stderr || stdout}`)));
  });
}
async function generate(id) { await run('python3', ['scripts/graph.py', 'generate', id]); }
const server = new McpServer({ name: 'service-graph-toolkit', version: '0.1.0' }, { instructions: 'Use project-scoped read-only tools. Start with list_projects, then validate_project or get_project_context. Evidence paths are authoritative; do not treat summaries as runtime truth.' });
server.registerTool('list_projects', { description: 'List available local graph projects.', inputSchema: z.object({}) }, async () => text(envelope('Available graph projects', { projects: readdirSync(projects, { withFileTypes: true }).filter(d => d.isDirectory() && existsSync(resolve(projects, d.name, 'project.yaml'))).map(d => yaml.parse(readFileSync(resolve(projects, d.name, 'project.yaml'), 'utf8'))) }, [{ id: 'projects/', version: 'local', accessScope: 'local' }])));
server.registerTool('validate_project', { description: 'Validate a project manifest without indexing sources.', inputSchema: z.object({ project: projectId }) }, async ({ project: id }) => { const r = await run('python3', ['scripts/graph.py', 'validate', id]); return text(envelope(r.stdout.trim(), {}, [{ id: `projects/${id}/inventory.yaml`, version: 'local', accessScope: 'local' }])); });
server.registerTool('get_project_context', { description: 'Return project metadata, services, edges, and generated-artifact paths.', inputSchema: z.object({ project: projectId }) }, async ({ project: id }) => { const { meta, inventory } = load(id); await generate(id); return text(envelope(`Context for ${id}`, { project: meta, services: Object.keys(inventory.services || {}), edgeCount: (inventory.edges || []).length, artifacts: `.graph-work/${id}/` }, [{ id: `projects/${id}/inventory.yaml`, version: 'local', accessScope: 'local' }])); });
server.registerTool('get_service_details', { description: 'Return one service manifest and its incoming/outgoing declared dependencies.', inputSchema: z.object({ project: projectId, service: z.string().min(1) }) }, async ({ project: id, service }) => { const { inventory } = load(id); const svc = inventory.services?.[service]; if (!svc) throw new Error(`unknown service: ${service}`); const edges = inventory.edges || []; return text(envelope(`Service details for ${service}`, { service: svc, incoming: edges.filter(e => e.to === service), outgoing: edges.filter(e => e.from === service) }, [{ id: `projects/${id}/inventory.yaml`, version: 'local', accessScope: 'local' }])); });
server.registerTool('get_service_map', { description: 'Generate and return the Mermaid service map for a project.', inputSchema: z.object({ project: projectId }) }, async ({ project: id }) => { await generate(id); const path = resolve(root, '.graph-work', id, 'service-map.md'); return text(envelope(`Service map for ${id}`, { markdown: readFileSync(path, 'utf8') }, [{ id: `.graph-work/${id}/service-map.md`, version: 'generated', accessScope: 'local' }])); });
async function codeTool(id, service, command, args) { const r = await run('gitnexus', [command, ...args, '-r', `${id}--${service}`]); return text(envelope(`GitNexus ${command} result`, { output: r.stdout.trim() }, [{ id: `${id}--${service}`, version: 'local-index', accessScope: 'local' }])); }
server.registerTool('search_code', { description: 'Search one project-namespaced GitNexus service index.', inputSchema: z.object({ project: projectId, service: z.string().min(1), query: z.string().min(1) }) }, async ({ project: id, service, query }) => codeTool(id, service, 'query', [query]));
server.registerTool('get_symbol_context', { description: 'Get GitNexus context for one symbol in one service.', inputSchema: z.object({ project: projectId, service: z.string().min(1), symbol: z.string().min(1) }) }, async ({ project: id, service, symbol }) => codeTool(id, service, 'context', [symbol]));
server.registerTool('get_change_impact', { description: 'Get code impact for one symbol plus declared cross-service edges.', inputSchema: z.object({ project: projectId, service: z.string().min(1), symbol: z.string().min(1), direction: z.enum(['upstream', 'downstream']).default('upstream') }) }, async ({ project: id, service, symbol, direction }) => { const { inventory } = load(id); const edges = (inventory.edges || []).filter(e => e.from === service || e.to === service); const r = await run('gitnexus', ['impact', symbol, '--direction', direction, '-r', `${id}--${service}`]); return text(envelope(`Impact for ${symbol}`, { codeImpact: r.stdout.trim(), declaredServiceEdges: edges }, [{ id: `${id}--${service}`, version: 'local-index', accessScope: 'local' }, { id: `projects/${id}/inventory.yaml`, version: 'local', accessScope: 'local' }])); });
await server.connect(new StdioServerTransport());
