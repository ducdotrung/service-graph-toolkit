#!/usr/bin/env python3
"""Project-scoped, credential-free graph toolkit commands."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent; PROJECTS=ROOT/'projects'; WORK=ROOT/'.graph-work'
def load(name):
 p=PROJECTS/name; meta=yaml.safe_load((p/'project.yaml').read_text()) or {}; inv=yaml.safe_load((p/'inventory.yaml').read_text()) or {}
 if meta.get('id')!=name: raise ValueError('project id must match directory')
 return p,meta,inv
def validate(name):
 _,_,inv=load(name); repos=inv.get('repos',{}); services=inv.get('services',{}); errors=[]
 for rid,r in repos.items():
  q=Path(str(r.get('path',''))); errors += [f'repo {rid}: unsafe path'] if not str(q) or q.is_absolute() or '..' in q.parts else []
 for sid,s in services.items():
  if s.get('repo') not in repos: errors.append(f'service {sid}: unknown repo')
 for e in inv.get('edges',[]):
  if e.get('from') not in services or e.get('to') not in services: errors.append('edge references unknown service')
 if errors: raise ValueError('\n'.join(errors))
 print(f'{name}: valid ({len(services)} services)')
def output(name):
 p=WORK/name; p.mkdir(parents=True,exist_ok=True); return p
def generate(name):
 validate(name); p,m,_=load(name); out=output(name); inv=str(p/'inventory.yaml')
 cmds=[['inventory-to-group.py','--inventory',inv,'--out',str(out/'group.yaml'),'--name',m['id'],'--project-id',name],['inventory-to-json.py','--inventory',inv,'--out',str(out/'inventory.json'),'--schema',str(out/'inventory.schema.json')],['inventory-to-service-map.py','--inventory',inv,'--out',str(out/'service-map.md')],['inventory-to-pages.py','--inventory',inv,'--out',str(out/'services')]]
 for c in cmds: subprocess.run([sys.executable,str(ROOT/'scripts'/c[0]),*c[1:]],check=True)
def index(name):
 p,_,inv=load(name); f=p/'.local.yaml'
 if not f.exists(): raise ValueError('copy .local.yaml.example to .local.yaml first')
 root=Path((yaml.safe_load(f.read_text()) or {})['source_root'])
 for sid,s in inv.get('services',{}).items():
  i=s.get('gitnexus_index') or {}; rel=i.get('analyze_path')
  if rel: subprocess.run(['gitnexus','analyze',str(root/rel),'--name',f'{name}--{sid}','--force']+(['--skip-git'] if i.get('skip_git') else []),check=True)
def main():
 a=argparse.ArgumentParser(); a.add_argument('command',choices=['init','validate','generate','index','refresh','mcp-config']); a.add_argument('project'); x=a.parse_args()
 if x.command=='init': shutil.copytree(PROJECTS/'example-platform',PROJECTS/x.project)
 elif x.command=='validate': validate(x.project)
 elif x.command=='generate': generate(x.project)
 elif x.command=='index': index(x.project)
 elif x.command=='refresh': index(x.project); generate(x.project)
 else:
  server=str(ROOT/'mcp-server'/'index.mjs')
  output(x.project).joinpath('mcp.json').write_text(json.dumps({'mcpServers':{f'service-graph-{x.project}':{'command':'node','args':[server]},f'gitnexus-{x.project}':{'command':'gitnexus','args':['mcp']}}},indent=2)+'\n')
if __name__=='__main__':
 try: main()
 except (ValueError,FileNotFoundError,subprocess.CalledProcessError) as e: print(f'error: {e}',file=sys.stderr); raise SystemExit(2)
