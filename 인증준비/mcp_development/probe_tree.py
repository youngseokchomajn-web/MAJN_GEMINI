#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EasyEDA 프로젝트/폴더/문서 트리 조회 — 'new start' 폴더 찾기 (read-only)."""
import json, urllib.request

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

CODE = r"""
const out = {};
out.dmt = Object.keys(eda).filter(k => k.startsWith('dmt_'));
// methods on Workspace / Project / Folder
for (const ns of ['dmt_Workspace','dmt_Project','dmt_Folder']) {
  if (eda[ns]) out[ns] = Object.getOwnPropertyNames(Object.getPrototypeOf(eda[ns])).filter(x => typeof eda[ns][x]==='function');
}
// try to list projects
for (const m of ['getAllProjectsInfo','getCurrentProjectInfo','getProjectsInfo','getAllProjects']) {
  try { if (eda.dmt_Project && eda.dmt_Project[m]) { const r = await eda.dmt_Project[m](); out['proj_'+m] = JSON.stringify(r).slice(0,1500); break; } } catch(e){ out['proj_'+m+'_err']=e.message; }
}
// schematics & pcbs
try { out.schematics = JSON.stringify(await eda.dmt_Schematic.getAllSchematicsInfo()).slice(0,800); } catch(e){ out.sch_err=e.message; }
try { out.pcbs = JSON.stringify(await eda.dmt_Pcb.getAllPcbsInfo()).slice(0,800); } catch(e){ out.pcb_err=e.message; }
return out;
"""

if __name__ == "__main__":
    try:
        print(json.dumps(ejs(CODE), ensure_ascii=False, indent=1)[:5000])
    except Exception as e:
        print("ERR", e)
