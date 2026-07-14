#!/usr/bin/env node
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const dir = resolve(fileURLToPath(new URL('.', import.meta.url)));
const client = new Client({ name: 'service-graph-toolkit-smoke', version: '0.1.0' });
await client.connect(new StdioClientTransport({ command: process.execPath, args: ['index.mjs'], cwd: dir, env: Object.fromEntries(Object.entries(process.env).filter(([, value]) => value !== undefined)) }));
const tools = await client.listTools();
const names = tools.tools.map(tool => tool.name).sort();
for (const required of ['list_projects', 'get_project_context', 'get_service_details', 'get_service_map', 'validate_project']) {
  if (!names.includes(required)) throw new Error(`missing tool: ${required}`);
}
const projects = await client.callTool({ name: 'list_projects', arguments: {} });
const details = await client.callTool({ name: 'get_service_details', arguments: { project: 'sock-shop', service: 'orders' } });
const impact = process.env.MCP_SMOKE_CODE ? await client.callTool({ name: 'get_change_impact', arguments: { project: 'sock-shop', service: 'orders', symbol: 'OrdersController', direction: 'upstream' } }) : undefined;
console.log(JSON.stringify({ tools: names, projects: projects.content, sockShopOrders: details.content, ...(impact ? { ordersImpact: impact.content } : {}) }, null, 2));
await client.close();
