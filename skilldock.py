#!/usr/bin/env python3
import argparse,difflib,hashlib,json,os,shutil,subprocess,tempfile,time,urllib.request
from pathlib import Path
VERSION='0.3.0';ROOT=Path(__file__).resolve().parent;CFG=ROOT/'skilldock.json';LIB=ROOT/'skills';BACK=ROOT/'backups';STATE=ROOT/'.skilldock-state.json';SOURCES=ROOT/'.skilldock-sources.json'
def config():return json.loads(CFG.read_text())
def write_config(c):CFG.write_text(json.dumps(c,indent=2),encoding='utf8')
def load_json(p,default):
 try:return json.loads(p.read_text())
 except:return default
def load_state():return load_json(STATE,{'installations':{}})
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
def init():LIB.mkdir(exist_ok=True);BACK.mkdir(exist_ok=True);CFG.write_text(CFG.read_text() if CFG.exists() else '{"targets":{},"profiles":{}}');print('Initialized SkillDock.')
def listall():
 print('Skills:');[print(' -',p.name) for p in sorted(LIB.iterdir()) if p.is_dir()];print('Targets:');[print(f' - {k}: {v}') for k,v in config().get('targets',{}).items()]
def backup(dst,name,skill):
 if dst.exists():b=BACK/f'{name}-{skill}-{int(time.time())}';b.parent.mkdir(exist_ok=True);shutil.copytree(dst,b);return b
def validate_skill(p):
 if not p.is_dir() or not (p/'SKILL.md').exists():raise SystemExit(f'Not a valid skill directory (missing SKILL.md): {p}')
 if any(x.is_symlink() for x in p.rglob('*')):raise SystemExit('Refusing skill source containing symlinks')
def install_one(skill,name,dry=False):
 src=LIB/skill
 if not src.exists():raise SystemExit(f'Skill not found: {skill}')
 validate_skill(src);base=target(name);dst=base/skill;digest=skill_hash(src);state=load_state()
 if dry:return print(f'[dry-run] {skill} -> {name}: {dst} ({"update" if dst.exists() else "install"})')
 base.mkdir(parents=True,exist_ok=True);backup(dst,name,skill)
 if dst.exists():shutil.rmtree(dst)
 shutil.copytree(src,dst);state['installations'].setdefault(name,{})[skill]={'hash':digest,'installed_at':int(time.time())};save_state(state);print(f'Installed {skill} -> {name}: {dst}')
def install(skill,names,dry=False):
 for n in names:install_one(skill,n,dry)
def status():
 state=load_state();rows=[]
 for name in config().get('targets',{}):
  base=target(name);skills=set([p.name for p in LIB.iterdir() if p.is_dir()])|set(state['installations'].get(name,{}))
  if base.exists():skills|={p.name for p in base.iterdir() if p.is_dir() and (p/'SKILL.md').exists()}
  for skill in sorted(skills):
   src,dst=LIB/skill,base/skill;managed=skill in state['installations'].get(name,{})
   st='missing' if managed and not dst.exists() else 'not-installed' if not dst.exists() else 'orphaned-managed' if not src.exists() and managed else 'unmanaged' if not managed else 'synced' if skill_hash(src)==skill_hash(dst) else 'drifted';rows.append((name,skill,st))
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
 for skill in [p.name for p in sorted(LIB.iterdir()) if p.is_dir()]:install(skill,names,dry)
def adopt(skill,name,force=False):
 src=target(name)/skill;dst=LIB/skill;validate_skill(src)
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
def is_git_source(s):return s.startswith(('https://','ssh://','git@')) or s.endswith('.git')
def source_add(name,source,subdir='',force=False):
 dst=LIB/name
 if dst.exists() and not force:raise SystemExit('Library skill exists; use --force')
 with tempfile.TemporaryDirectory() as td:
  base=Path(td)/'source'
  if is_git_source(source):subprocess.run(['git','clone','--depth','1',source,str(base)],check=True)
  else:
   src=Path(source).expanduser().resolve()
   if not src.exists():raise SystemExit(f'Source not found: {src}')
   shutil.copytree(src,base)
  src=(base/subdir).resolve() if subdir else base
  if base.resolve() not in [src,*src.parents]:raise SystemExit('Invalid subdir')
  validate_skill(src)
  if dst.exists():backup(dst,'library',name);shutil.rmtree(dst)
  LIB.mkdir(exist_ok=True);shutil.copytree(src,dst)
 meta=load_json(SOURCES,{});meta[name]={'source':source,'subdir':subdir,'hash':skill_hash(dst),'added_at':int(time.time())};SOURCES.write_text(json.dumps(meta,indent=2),encoding='utf8');print(f'Added {name} to library from {source}')
def load_registry(source):
 if source.startswith(('http://','https://')):
  with urllib.request.urlopen(source,timeout=10) as r:d=json.loads(r.read().decode())
 else:d=json.loads(Path(source).expanduser().read_text())
 items=d.get('skills',d if isinstance(d,list) else [])
 if not isinstance(items,list):raise SystemExit('Registry must contain a skills list')
 return [x for x in items if isinstance(x,dict) and x.get('name') and x.get('source')]
def registry_list(source,query=''):
 items=load_registry(source);q=query.lower()
 for x in items:
  text=f"{x.get('name','')} {x.get('description','')} {' '.join(x.get('tags',[]))}".lower()
  if not q or q in text:print(f"{x['name']:<24} {x.get('description','')} — {x['source']}")
 return items
def registry_install(name,source,force=False):
 for x in load_registry(source):
  if x['name']==name:return source_add(name,x['source'],x.get('subdir',''),force)
 raise SystemExit(f'No registry skill named {name}')
def profile_save(name,skills):
 c=config();c.setdefault('profiles',{})[name]=skills;write_config(c);print(f'Saved profile {name}: {", ".join(skills)}')
def profile_list():
 for n,s in config().get('profiles',{}).items():print(f'{n}: {", ".join(s)}')
def profile_install(name,targets,dry=False):
 skills=config().get('profiles',{}).get(name)
 if not skills:raise SystemExit(f'Unknown profile: {name}')
 for skill in skills:install(skill,targets,dry)
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('init');sp.add_parser('list');sp.add_parser('scan');sp.add_parser('status');i=sp.add_parser('install');i.add_argument('skill');i.add_argument('--to',required=True);i.add_argument('--dry-run',action='store_true');sy=sp.add_parser('sync');sy.add_argument('--to',required=True);sy.add_argument('--dry-run',action='store_true');d=sp.add_parser('diff');d.add_argument('skill');d.add_argument('--to',required=True);ad=sp.add_parser('adopt');ad.add_argument('skill');ad.add_argument('--from-target',required=True);ad.add_argument('--force',action='store_true');u=sp.add_parser('uninstall');u.add_argument('skill');u.add_argument('--from-target',required=True);u.add_argument('--force',action='store_true');sa=sp.add_parser('source-add');sa.add_argument('name');sa.add_argument('source');sa.add_argument('--subdir',default='');sa.add_argument('--force',action='store_true');rl=sp.add_parser('registry-list');rl.add_argument('registry');rl.add_argument('--query',default='');ri=sp.add_parser('registry-install');ri.add_argument('name');ri.add_argument('registry');ri.add_argument('--force',action='store_true');ps=sp.add_parser('profile-save');ps.add_argument('name');ps.add_argument('--skills',required=True);sp.add_parser('profile-list');pi=sp.add_parser('profile-install');pi.add_argument('name');pi.add_argument('--to',required=True);pi.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 if a.cmd=='init':init()
 elif a.cmd=='list':listall()
 elif a.cmd=='scan':scan()
 elif a.cmd=='status':status()
 elif a.cmd=='install':install(a.skill,names(a.to),a.dry_run)
 elif a.cmd=='sync':sync(names(a.to),a.dry_run)
 elif a.cmd=='diff':diff(a.skill,a.to)
 elif a.cmd=='adopt':adopt(a.skill,a.from_target,a.force)
 elif a.cmd=='uninstall':uninstall(a.skill,a.from_target,a.force)
 elif a.cmd=='source-add':source_add(a.name,a.source,a.subdir,a.force)
 elif a.cmd=='registry-list':registry_list(a.registry,a.query)
 elif a.cmd=='registry-install':registry_install(a.name,a.registry,a.force)
 elif a.cmd=='profile-save':profile_save(a.name,names(a.skills))
 elif a.cmd=='profile-list':profile_list()
 elif a.cmd=='profile-install':profile_install(a.name,names(a.to),a.dry_run)
if __name__=='__main__':main()
