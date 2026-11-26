"""公开构建入口：所有资产和配置均在本工程内。"""
from pathlib import Path
import argparse,importlib.util,json,shutil
ROOT=Path(__file__).resolve().parent

def build(config_path,out=None):
    spec=importlib.util.spec_from_file_location("nana_core",ROOT/"scripts/构建.py")
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    config=core.read_config(config_path);shots=config["scenes"]
    assert len(shots)>0 and len({s["id"] for s in shots})==len(shots)
    for row in shots:assert row["start"]>=0 and row["duration"]>0 and row["template"] in core.FUNCTIONS
    target=Path(out or ROOT/"index.html");target.parent.mkdir(parents=True,exist_ok=True)
    core.build_project(target.parent,shots,config)
    if target.name!="index.html":shutil.copy2(target.parent/"index.html",target)
    return {"scene_count":len(shots),"duration":max(x["start"]+x["duration"] for x in shots),"output":str(target)}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--config",type=Path,default=ROOT/"配置.json");p.add_argument("--output",type=Path,default=ROOT/"index.html");a=p.parse_args();print(json.dumps(build(a.config,a.output),ensure_ascii=False))
