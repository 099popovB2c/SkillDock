#!/usr/bin/env python3
import argparse,difflib,hashlib,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;CFG=ROOT/'skilldock.json';LIB=ROOT/'skills';BACK=ROOT/'backups';STATE=ROOT/'.skilldock-state.json'
def config():return json.loads(CFG.read_text())
def load_state():
 try:return json.loads(STATE.read_text())
 except:return {'installations':{}}
def save_state(s):STATE.write_text(json.dumps(s,indent=2),encoding='utf8')
def target(name):
 p=config().get('targets',{}).get(name)
 if not p:raise SystemExit(f'Unknown target: {name}')
 return Path(p).expanduser()
def skill_hash(path):
 h=hashlib.sha256()
 if not path.exists():return None
 for p in sorted(x for x in path.rglob('*') if x.is_file()):h.update(str(p.relative_to(path)).encode());h.update(b'\0');h.update(p.read_bytes());h.update(b'\0')
 return h.hexdigest()
def init():LIB.mkdir(exist_ok=True);BACK.mkdir(exist_ok=True);CFG.write_text(CFG.read_text() if CFG.exists() else '{"targets":{}}');print('Initialized SkillDock.')
def listall():
 print('Skills:');[print(' -',p.name) for p in sorted(LIB.iterdir()) if p.is_dir()];print('Targets:');[print(f' - {k}: {v}') for k,v in config().get('targets',{}).items()]
def backup(dst,name,skill):
 if dst.exists():b=BACK/f'{name}-{skill}-{int(time.time())}';b.parent.mkdir(exist_ok=True);shutil.copytree(dst,b);return b
def install_one(skill,name,dry=False):
 src=LIB/skill
 if not src.exists():raise SystemExit(f'Skill not found: {skill}')
 base=target(name);dst=base/skill;digest=skill_hash(src);state=load_state();old=state['installations'].get(name,{}).get(skill)
 if dry:return print(f'[dry-run] {skill} -> {name}: {dst} ({"update" if dst.exists() else "install"})')
 base.mkdir(parents=True,exist_ok=True);backup(dst,name,skill)
 if dst.exists():shutil.rmtree(dst)
 shutil.copytree(src,dst);state['installations'].setdefault(name,{})[skill]={'hash':digest,'installed_at':int(time.time())};save_state(state);print(f'Installed {skill} -> {name}: {dst}')
def install(skill,names,dry=False):
 for n in names:install_one(skill,n,dry)
def status():
 state=load_state();rows=[]
 for name in config().get('targets',{}):
  base=target(name)
  skills=set([p.name for p in LIB.iterdir() if p.is_dir()])|set(state['installations'].get(name,{}))
  if base.exists():skills|={p.name for p in base.iterdir() if p.is_dir() and (p/'SKILL.md').exists()}
  for skill in sorted(skills):
   src,dst=LIB/skill,base/skill;managed=skill in state['installations'].get(name,{})
   if not dst.exists():st='missing' if managed else 'not-installed'
   elif not src.exists():st='orphaned-managed' if managed else 'unmanaged'
   elif not managed:st='unmanaged'
   else:st='synced' if skill_hash(src)==skill_hash(dst) else 'drifted'
   rows.append((name,skill,st))
 for r in rows:print(f'{r[0]:<12} {r[1]:<24} {r[2]}')
 return rows
def scan():
 state=load_state()
 for name in config().get('targets',{}):
  base=target(name);print(f'[{name}] {base}')
  if not base.exists():print('  (target directory missing)');continue
  for p in sorted(base.iterdir()):
   if p.is_dir() and (p/'SKILL.md').exists():print(f"  {p.name:<24} {'managed' if p.name in state['installations'].get(name,{}) else 'unmanaged'}")
def sync(names,dry=False):
 skills=[p.name for p in sorted(LIB.iterdir()) if p.is_dir()]
 for skill in skills:install(skill,names,dry)
def adopt(skill,name,force=False):
 src=target(name)/skill;dst=LIB/skill
 if not src.exists():raise SystemExit('Installed skill not found')
 if dst.exists() and not force:raise SystemExit('Library skill exists; use --force to replace')
 if dst.exists():backup(dst,'library',skill);shutil.rmtree(dst)
 shutil.copytree(src,dst);print(f'Adopted {skill} from {name} into library')
def uninstall(skill,name,force=False):
 state=load_state();managed=skill in state['installations'].get(name,{})
 if not managed and not force:raise SystemExit('Refusing to delete unmanaged skill; use --force if intentional')
 dst=target(name)/skill
 if dst.exists():backup(dst,name,skill);shutil.rmtree(dst)
 state['installations'].get(name,{}).pop(skill,None);save_state(state);print(f'Removed {skill} from {name}')
def diff(skill,name):
 src=LIB/skill/'SKILL.md';dst=target(name)/skill/'SKILL.md'
 if not dst.exists():return print('Not installed')
 if not src.exists():return print('Missing from library')
 print(''.join(difflib.unified_diff(dst.read_text().splitlines(True),src.read_text().splitlines(True),fromfile='installed',tofile='library')) or 'No differences.')
def names(s):return [x.strip() for x in s.split(',') if x.strip()]
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('init');sp.add_parser('list');sp.add_parser('scan');sp.add_parser('status');i=sp.add_parser('install');i.add_argument('skill');i.add_argument('--to',required=True);i.add_argument('--dry-run',action='store_true');sy=sp.add_parser('sync');sy.add_argument('--to',required=True);sy.add_argument('--dry-run',action='store_true');d=sp.add_parser('diff');d.add_argument('skill');d.add_argument('--to',required=True);ad=sp.add_parser('adopt');ad.add_argument('skill');ad.add_argument('--from-target',required=True);ad.add_argument('--force',action='store_true');u=sp.add_parser('uninstall');u.add_argument('skill');u.add_argument('--from-target',required=True);u.add_argument('--force',action='store_true');a=ap.parse_args()
 if a.cmd=='init':init()
 elif a.cmd=='list':listall()
 elif a.cmd=='scan':scan()
 elif a.cmd=='status':status()
 elif a.cmd=='install':install(a.skill,names(a.to),a.dry_run)
 elif a.cmd=='sync':sync(names(a.to),a.dry_run)
 elif a.cmd=='diff':diff(a.skill,a.to)
 elif a.cmd=='adopt':adopt(a.skill,a.from_target,a.force)
 elif a.cmd=='uninstall':uninstall(a.skill,a.from_target,a.force)
if __name__=='__main__':main()
