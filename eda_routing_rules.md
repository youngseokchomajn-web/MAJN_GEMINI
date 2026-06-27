# EasyEDA PCB 설계 절대 철칙 (eda_routing_rules.md)

> **이 문서는 Claude의 "자아성찰용 족쇄"다.** EasyEDA 브릿지로 PCB 코드를 짜기 전에 **반드시 먼저 로드**하고, 각 단계마다 §4 자기검증을 통과해야 한다.
> 제정 근거: 마중 PCB 작업 중 반복된 실패(`MAJN_프로세스_오류정리_2026-06-27.md` P-01~P-28) + 현존 결함(`MAJN_에러케이스_정리_2026-06-27.md` E-01~E-15).
> 나의 약점: **공간감각(Spatial Blindness)·물리법칙(Physics Blindness)·연결성 오판(False-Positive Connectivity)·없는 API 창조(API Hallucination).** 이 문서는 그걸 원천 차단한다.

---

## 0. 절대 원칙 (Top-level, 위반 즉시 중단)

1. **전체 코드를 한 번에 짜지 않는다.** 반드시 §2의 4단계로 쪼개고, 각 단계는 사용자 컨펌 + 자기검증 통과 전에는 다음으로 넘어가지 않는다.
2. **DRC만 믿지 않는다.** DRC가 못 잡는 결함(디커플링 거리·스위칭 루프·EP 써멀·안테나·pour 넥)이 진짜 위험이다. 전 도메인을 **기하로 직접 검증**한다.
3. **연결성은 union-find/flood-fill로 단정하지 않는다.** (P-01~P-04에서 반복 거짓양성.) §4-E의 **직접 갭분석** 또는 권위 DRC만 신뢰한다.
4. **없는 API를 창조하지 않는다.** §5의 검증된 메서드/getter만 쓴다. 불확실하면 멈추고 `references/`를 읽는다.
5. **영속/비속 구분.** 저장해도 복귀되는 작업(§5-D)을 "수정 완료"로 보고하지 않는다.

---

## 1. 작업 시작 전 의무 (Pre-flight Checklist)

```
□ 브릿지 살아있나?  curl http://127.0.0.1:49620/health → edaConnected:true 확인
   (없으면: node .agents/skills/easyeda-api/scripts/bridge-server.mjs 백그라운드 기동
            → EasyEDA Start Page → 메뉴 "API Gateway" → Reconnect)
□ PCB 문서가 활성인가?  getCurrentDocumentInfo().documentType == PCB (Start Page면 미연결)
□ 좌표계 인지:  단위 = mil (1mm = 39.37mil).  화면 Y축은 보드와 반전(보드 y=0 = 화면 하단).
□ 레이어 번호:  1=Top, 2=Bottom, 15=Inner1(GND평면=pour), 16=Inner2, 3=Top실크, 11=보드외곽.
□ 이 보드는 전원을 POUR로 운반(전 트레이스 10mil). 광폭 트레이스 가정 금지.
```

---

## 2. 단계별 설계 프로세스 (한 번에 한 단계만)

| 단계 | 내용 | 완료 게이트 (다음으로 넘어가기 전 통과 필수) |
|---|---|---|
| **1. 배치(Placement)** | 부품 좌표·회전 확정 | §4-A 부품 겹침 0 + 데이터플로 + **전원무결성 동시 고려**(P-24 교훈) |
| **2. 전원(Power)** | VBUS/PVDD/BOOST_SW/GND pour·전원 트레이스·전원 비아·EP 써멀비아 | §4-B 폭/넥/전류용량 + EP비아 GND + 스티칭 |
| **3. 신호(Signal)** | 데이터·제어 신호 트레이스 | §4-C 클리어런스 + §4-E 연결성(직접 갭) |
| **4. 동박(Copper Pour)** | GND 평면 re-pour, 전원 pour 채우기 | §4-D pour 넥 + 안테나 키프아웃 + 고립섬 |

> 각 단계가 끝나면 **반드시 멈추고** 결과를 사용자에게 보고 → 컨펌 받기. "1단계 컨펌 전엔 2단계 코드 생성 금지."

---

## 3. Net Class 물리 제약 (마중 보드 기준값)

> 보드: 80×60mm, 4층, 2oz 외층. USB-C 5V → MP3426 부스트 12.12V(PVDD) → TAS5805M Class-D → 2×8Ω(10W RMS/30W Max).

| Net Class | 예시 넷 | 전류 | 최소 폭 / 방식 | 비고 |
|---|---|---|---|---|
| **고전류 전원** | VBUS_5V | **5A** | **POUR 필수** (또는 트레이스 ≥80mil@2oz). pour 넥 ≥40mil 유지 | USB-C→U3 경로 |
| **부스트 SW** | BOOST_SW | ~5A | POUR, 단 **노드 면적 최소화**(L1·D3을 U3 2mm내) | 고 dv/dt = EMI |
| **중전류 전원** | PVDD_12V | 1.87A | POUR 또는 트레이스 ≥30mil | D3→U4 |
| **앰프 출력** | AMP_OUT_x | 1.12A | 트레이스 ≥20mil | BTL 필터까지 |
| **로직 전원** | VCC_3V3 | <0.5A | 트레이스 ≥15mil | |
| **신호** | I2C/I2S/SPI/제어 | — | **10mil (0.25mm)** 표준 | |
| **Clearance(이격)** | 모든 다른넷 | — | **기본 ≥8mil. JLC 최소 6mil. 12V(PVDD) 인접은 ≥10mil** | 6mil 룰은 sub-6 위반 양산(E-11) |
| **비아** | 전원 | — | 드릴 12mil·환형 ≥6mil. **전원 비아는 전류당 충분히**(5A면 다수 병렬) | |
| **EP 써멀비아** | U3·U4 EP | — | **반드시 net=GND**(net='' 금지) + EP당 다수 + re-pour로 평면 본딩 | E-01 근본 |

> **폭을 블랭킷으로 키우지 말 것**(P 교훈: clearance 폭발). 전원은 trace 폭이 아니라 **pour**로 용량 확보.

---

## 4. 코드 출력 전 자기검증 (Self-Correction — 혼잣말로 수학 검증 강제)

> 코드를 출력하기 **전에**, 해당 단계 항목을 혼잣말(reasoning)로 **수치 계산**해 통과를 확인한다. 눈대중 금지.

### A. 배치 검증 (1단계)
- [ ] 모든 부품쌍의 패드 bbox가 **겹치지 않는가?** `gap = AABB거리`; 다른 부품끼리 겹침 0. (E-03: R13이 U1핀 13.65mil 침범 사례 재발 방지 — 다른넷 패드 0.5mil이라도 겹치면 중단.)
- [ ] **디커플링 캡이 IC 전원핀 ≤2mm**에 있는가? (E-05) 재배치가 캡을 핀에서 흩지 않았는가?
- [ ] **스위칭 부품(U3·L1·D3)이 ≤2mm 클러스터**인가? (E-04)
- [ ] 안테나(ESP32) 아래/주변에 부품·구리 금지 영역 확보했는가? (E-02)

### B. 전원 검증 (2단계)
- [ ] 각 전원넷 폭/방식이 §3 표 충족? VBUS는 pour인가? pour **넥(최협점) ≥40mil**인가?
- [ ] 전원 비아 전류용량 충분? (5A 경로에 비아 1개 = 부족)
- [ ] **EP 써멀비아가 net=GND**이고 re-pour 후 평면에 본딩되는가? (net='' = 단절, E-01)
- [ ] 전원부 GND **스티칭 비아가 IC 근처**에 있는가? (E-06: 비아가 1100mil 밖이면 실패)

### C. 신호 검증 (3단계)
- [ ] 모든 다른넷 트레이스/비아/패드 **최소거리 ≥ clearance(§3)**? `seg-seg / pt-seg 거리 - 폭/2 - 반경` 계산.
- [ ] 트레이스가 전원 pour를 과도하게 관통해 **넥을 만들지 않는가?** (E-08)

### D. 동박 검증 (4단계)
- [ ] re-pour 후 **고립 섬(island) 0**? 모든 같은넷이 한 덩어리?
- [ ] 안테나 키프아웃 void가 실제로 생겼는가? (E-02)

### E. 연결성 검증 (★union-find 금지)
```
거짓양성을 막는 유일하게 신뢰가능한 방법:
넷의 각 패드에 대해 → 같은넷 트레이스/비아/pour 중 최근접 구리와의 gap 계산.
  gap ≤ -(trace_width/2)  → 트레이스가 패드를 덮음 = 연결됨 ✓
  gap > 30mil             → 진짜 개방 후보 (좌표와 함께 보고)
pour넷(GND 등)은 패드가 pour rect 안 + 도달 레이어인지 추가 확인.
```
- [ ] 모든 넷이 위 방식으로 **패드 전부 구리 접촉**? union-find/flood-fill 결과는 참고만, 단정 금지.

---

## 5. EasyEDA API 방어 규칙 (Hallucination 차단)

### A. 검증된 생성 메서드 (영속 — 신뢰가능)
```js
// 트레이스 생성: (net, layer, x1,y1, x2,y2, width(mil), lock)
await eda.pcb_PrimitiveLine.create("VBUS_5V", 1, 100, 200, 500, 200, 40, false);
// 비아 생성: (net, x, y, holeDia, dia)
await eda.pcb_PrimitiveVia.create("GND", 300, 300, 12, 24);
// 패드 넷 변경 / 트레이스·비아 삭제 / pour 재생성
await eda.pcb_PrimitivePad.modify(padId, {net:"GND"});
await eda.pcb_PrimitiveLine.delete(lineId);
// pour: rebuildCopperRegion() 로 재채움
```

### B. 검증된 조회 getter (정확한 이름 — 오용 금지)
```
LINE: getState_Net() · getState_Layer()  [★ LayerId 아님] · getState_StartX/StartY/EndX/EndY() · getState_LineWidth()
VIA:  getState_Net() · getState_X/Y() · getState_HoleDiameter() · getState_Diameter()
PAD:  getState_Net() · getState_X/Y() · getState_Layer() · getState_PadNumber()
      getState_Pad() → [shape, w, h, rot]   ※ 가변길이! RECT=3숫자, ELLIPSE/OVAL=2, POLYGON=좌표배열 → 길이 검사 필수
POUR: getState_Net() · getState_Layer() · getState_ComplexPolygon() → {polygon:["R",x,y,w,h,..]}  (rect: X[x,x+w] Y[y-h,y])
COMP: getState_Designator() · getState_X/Y() · getState_Rotation() · getState_OtherProperty()["LCSC Part Name"=값]
```

### C. 코드 실행 패턴 (Python 헬퍼)
```python
# POST http://127.0.0.1:49620/execute  body {"code": "(async)=> {... return ...}"}
# 코드는 async, 반드시 return. console.log 안 잡힘. 모든 await.
```

### D. ★비영속(Non-persistent) — "수정 완료"로 보고 금지
- `setState_Rotation / setState_Designator / setState_UniqueId` → 저장해도 복귀 (부품 회전 브릿지 불가 → pad-net swap 등 우회).
- **풋프린트 정의 EP비아**의 `modify({net})` → 리로드시 net='' 재생성 (영속 GND화하려면 **별도 비아 추가**).
- `pcb_Drc.check()` → HTTP 500(무거움). 불리언만 반환, 위반 상세 API 없음 → UI패널 또는 기하검증.

### E. 모르면 멈춘다
- `references/classes/`에 없는 메서드 = 존재하지 않음. 추측해서 호출 금지. enum은 숫자 추측 말고 `EPCB_LayerId.TOP` 등 멤버 사용.

---

## 6. 절대 하지 말 것 (이번에 실제로 당한 실패)

1. ❌ union-find/flood-fill 결과로 "개방 N건" 단정 → ✅ 직접 갭분석. (P-01~04)
2. ❌ 폭을 전역으로 키우기 → clearance 폭발. ✅ 전원은 pour. (P 교훈)
3. ❌ autoroute 100% 위해 IC만 붙여 재배치 → 디커플링/부스트 부품 흩어짐(PI/EMI 결함). ✅ 배치는 데이터플로 **+ 전원무결성** 동시. (P-24→E-04/05/06)
4. ❌ EP비아 modify로 GND화 후 "완료" 보고 → 복귀. ✅ 별도 GND비아 + 영속 확인. (P-07,11→E-01)
5. ❌ 전체 배선을 한 번에 코드로 → ✅ 4단계 분할 + 단계별 컨펌.
6. ❌ DRC 0이면 끝 → ✅ DRC 못잡는 도메인(디커플링·루프·EP·안테나·넥) 별도 검증.
7. ❌ 좌표 Y축 그대로 가정 → ✅ 화면 반전 인지(보드 y=0=화면하단).

---

## 7. 단계 종료 보고 템플릿 (각 단계 후 이걸로 보고)
```
[N단계: XXX] 완료
- 한 것: ...
- 자기검증(§4-X): [통과/실패] — 수치: 최소 clearance __mil, 겹침 __건, 넥 __mil ...
- 영속 확인: [예/아니오]
- 다음 단계 진행 컨펌 요청
```
> **이 보고 없이는 다음 단계로 넘어가지 않는다.**
