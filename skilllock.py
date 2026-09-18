#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import skilldock

VERSION="0.4.0"
ROOT=skilldock.ROOT
DEFAULT_LOCK=ROOT/"skilldock.lock.json"

def load_json(path,default):
    try:return json.loads(Path(path).read_text(encoding="utf8"))
    except Exception:return default

def build_lock(lib=skilldock.LIB,sources=skilldock.SOURCES):
    meta=load_json(sources,{});skills=[]
    if Path(lib).exists():
        for p in sorted(x for x in Path(lib).iterdir() if x.is_dir() and (x/"SKILL.md").exists()):
            src=meta.get(p.name,{});skills.append({"name":p.name,"hash":skilldock.skill_hash(p),"source":src.get("source"),"subdir":src.get("subdir","")})
    return {"version":1,"skilldock_version":VERSION,"skills":skills}

def write_lock(path=DEFAULT_LOCK,lib=skilldock.LIB,sources=skilldock.SOURCES):
    data=build_lock(lib,sources);p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2),encoding="utf8");return data

def verify_lock(lock_path=DEFAULT_LOCK,lib=skilldock.LIB):
    lock=load_json(lock_path,{"skills":[]});by={x.get("name"):x for x in lock.get("skills",[])};rows=[]
    for name,item in sorted(by.items()):
        p=Path(lib)/name
        if not p.exists():status="missing"
        else:status="ok" if skilldock.skill_hash(p)==item.get("hash") else "drifted"
        rows.append({"name":name,"status":status,"expected":item.get("hash"),"actual":skilldock.skill_hash(p) if p.exists() else None})
    locked=set(by);current={p.name for p in Path(lib).iterdir() if p.is_dir() and (p/"SKILL.md").exists()} if Path(lib).exists() else set()
    for name in sorted(current-locked):rows.append({"name":name,"status":"unlocked","expected":None,"actual":skilldock.skill_hash(Path(lib)/name)})
    return rows

def update_sources(names=None,sources=skilldock.SOURCES):
    meta=load_json(sources,{});wanted=names or sorted(meta);done=[]
    for name in wanted:
        item=meta.get(name)
        if not item:raise SystemExit(f"No recorded source for {name}")
        skilldock.source_add(name,item["source"],item.get("subdir",""),True);done.append(name)
    return done

def main():
    ap=argparse.ArgumentParser(description="SkillDock v0.4 lock/update helper");sp=ap.add_subparsers(dest="cmd",required=True);l=sp.add_parser("lock");l.add_argument("--file",default=str(DEFAULT_LOCK));v=sp.add_parser("verify");v.add_argument("--file",default=str(DEFAULT_LOCK));v.add_argument("--strict",action="store_true");u=sp.add_parser("update");u.add_argument("skills",nargs="*");u.add_argument("--lock-file",default=str(DEFAULT_LOCK));u.add_argument("--no-lock",action="store_true");s=sp.add_parser("show");s.add_argument("--file",default=str(DEFAULT_LOCK));a=ap.parse_args()
    if a.cmd=="lock":d=write_lock(a.file);print(json.dumps(d,indent=2))
    elif a.cmd=="verify":
        rows=verify_lock(a.file);[print(f"{x['name']:<24} {x['status']}") for x in rows]
        if a.strict and any(x["status"]!="ok" for x in rows):raise SystemExit(4)
    elif a.cmd=="update":
        done=update_sources(a.skills or None);print("Updated:",", ".join(done))
        if not a.no_lock:write_lock(a.lock_file)
    elif a.cmd=="show":print(json.dumps(load_json(a.file,{"skills":[]}),indent=2))
if __name__=="__main__":main()
