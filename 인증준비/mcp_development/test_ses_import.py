#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""importAutoRouteSesFile 검증: SENSOR_INT1 한 넷만 TopLayer 직선으로 라우팅한
최소 SES를 import → 트랙이 올바른 넷으로 들어오는지 확인 → 테스트 트랙 삭제."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
SES = '''(session "majn_pcb2.ses"
  (base_design "majn_pcb2.dsn")
  (placement
    (resolution mil 1000)
    (component u1
      (place u1 0 0 front 0)
    )
  )
  (was_is
  )
  (routes
    (resolution mil 1000)
    (library_out
    )
    (network_out
      (net SENSOR_INT1
        (wire
          (path TopLayer 10 1470.37 3858.27 757.87 2999.02)
        )
      )
    )
  )
)
'''

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    ses_js = json.dumps(SES)
    js = f"""
    const out={{}};
    await eda.dmt_EditorControl.openDocument("{PCB2}");
    await new Promise(r=>setTimeout(r,1500));
    await eda.dmt_EditorControl.activateDocument("{PCB2}");
    await new Promise(r=>setTimeout(r,1500));
    const before=(await eda.pcb_PrimitiveLine.getAll()||[]).length;
    out.before=before;
    // import 시도 (여러 인자 형태 대비)
    const ses={ses_js};
    try{{ out.r_str = await eda.pcb_Document.importAutoRouteSesFile(ses); }}catch(e){{ out.err_str=e.message; }}
    await new Promise(r=>setTimeout(r,2500));
    let lines=await eda.pcb_PrimitiveLine.getAll()||[];
    out.after=lines.length;
    // 새 라인들의 net 확인 + 삭제
    out.newNets=[];
    const delIds=[];
    for(const l of lines){{
      let net=null; try{{net=l.net??(l.getState_Net?l.getState_Net():null);}}catch(e){{}}
      let id=null; try{{id=l.getState_PrimitiveId?l.getState_PrimitiveId():l.primitiveId;}}catch(e){{}}
      out.newNets.push(net); if(id) delIds.push(id);
    }}
    // 테스트 트랙 삭제(상태 복구)
    if(delIds.length){{ try{{ await eda.pcb_PrimitiveLine.delete(delIds); out.deleted=delIds.length; }}catch(e){{ out.del_err=e.message; }} }}
    out.afterDelete=(await eda.pcb_PrimitiveLine.getAll()||[]).length;
    return out;
    """
    res = c.execute_js(js)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
