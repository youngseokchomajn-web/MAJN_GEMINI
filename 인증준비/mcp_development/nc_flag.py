#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""floating 핀에 No-Connect(setState_NoConnected) 부착. 컴포넌트 1개씩(작은 단위) 처리.
사용: python nc_flag.py U1            # 특정 컴포넌트만
      python nc_flag.py ALL           # floating_pins.json 전체
처리 후 저장. (연결성은 변하지 않음 — NC 는 '의도적 미연결' 표시일 뿐)"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

def get_primids(client):
    js = r"""
    const out={};
    const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();
    if(pages&&pages.length){await eda.dmt_EditorControl.activateDocument(pages[0].uuid);await new Promise(r=>setTimeout(r,800));}
    const cs=await eda.sch_PrimitiveComponent.getAll();
    out.map={};
    for(const c of (cs||[])){let t='?';try{t=c.getState_ComponentType&&c.getState_ComponentType();}catch(e){}
      if(t==='part'){let d=null;try{d=c.getState_Designator&&c.getState_Designator();}catch(e){} if(d) out.map[d]=c.getState_PrimitiveId();}}
    return out;
    """
    return client.execute_js(js).get("map", {})

def nc_component(client, primid, nums):
    js = """
    const primid=%s; const want=%s;
    const out={set:[], skip:[]};
    try{
      const pins=await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(primid);
      for(const p of (pins||[])){
        const num=String(p.getState_PinNumber());
        if(want.includes(num)){
          try{ p.setState_NoConnected(true); out.set.push(num); }
          catch(e){ out.skip.push(num+':'+e.message); }
        }
      }
    }catch(e){ out.err=e.message; }
    return out;
    """ % (json.dumps(primid), json.dumps(nums))
    return client.execute_js(js)

def save(client):
    return client.execute_js("try{await eda.sch_Document.save();return {saved:true};}catch(e){return{saved:false,err:e.message};}")

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "ALL"
    floats = json.load(open("floating_pins.json", encoding="utf-8"))
    client = EasyEDAMCPClient()
    if not client.connect(): sys.exit(1)
    primids = get_primids(client)
    todo = list(floats.keys()) if target == "ALL" else [target]
    for des in todo:
        nums = floats.get(des, [])
        pid = primids.get(des)
        if not pid:
            print(f"  [SKIP] {des}: primId 없음"); continue
        res = nc_component(client, pid, nums)
        print(f"  [{des}] set={res.get('set')} skip={res.get('skip')} err={res.get('err')}")
    s = save(client)
    print("save:", s)

if __name__ == "__main__":
    main()
