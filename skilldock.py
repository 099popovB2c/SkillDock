#!/usr/bin/env python3
import argparse,difflib,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CFG=ROOT/'skilldock.json';LIB=ROOT/'skills';BACK=ROOT/'backups'
def config():return json.loads(CFG.read_text())
def target(name):
 p=config()['targets'].get(name)
 if not p:raise SystemExit(f'Unknown target: {name}')
 return Path(p).expanduser()
def init():
 LIB.mkdir(exist_ok=True);BACK.mkdir(exist_ok=True)
 if not CFG.exists():CFG.write_text('{"targets":{}}')
 print('Initialized SkillDock.')
def listall():
 print('Skills:');[print(' -',p.name) for p in sorted(LIB.iterdir()) if p.is_dir()]
 print('Targets:');[print(f' - {k}: {v}') for k,v in config().get('targets',{}).items()]
def install(skill,names):
 src=LIB/skill
 if not src.exists():raise SystemExit('Skill not found')
 for n in names:
  base=target(n);base.mkdir(parents=True,exist_ok=True);dst=base/skill
  if dst.exists():
   b=BACK/f'{n}-{skill}-{int(time.time())}';b.parent.mkdir(exist_ok=True);shutil.copytree(dst,b)
   shutil.rmtree(dst)
  shutil.copytree(src,dst);print(f'Installed {skill} -> {n}: {dst}')
def diff(skill,name):
 src=LIB/skill/'SKILL.md';dst=target(name)/skill/'SKILL.md'
 if not dst.exists():return print('Not installed')
 a=src.read_text().splitlines(True);b=dst.read_text().splitlines(True);print(''.join(difflib.unified_diff(b,a,fromfile='installed',tofile='library')) or 'No differences.')
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('init');sp.add_parser('list');i=sp.add_parser('install');i.add_argument('skill');i.add_argument('--to',required=True);d=sp.add_parser('diff');d.add_argument('skill');d.add_argument('--to',required=True);a=ap.parse_args()
 if a.cmd=='init':init()
 elif a.cmd=='list':listall()
 elif a.cmd=='install':install(a.skill,[x.strip() for x in a.to.split(',') if x.strip()])
 elif a.cmd=='diff':diff(a.skill,a.to)
if __name__=='__main__':main()
