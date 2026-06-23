# MAJN PCB6 진행 기록 — 2026-06-23

전원-우선 재설계(PCB6) 세션 기록. 권위 계획서: [`MAJN_PCB6_POWER_FIRST_PLAN.md`](./MAJN_PCB6_POWER_FIRST_PLAN.md).

---

## 완료 상태 요약

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 브릿지 셋업 + 게이트 | ✅ 완료 |
| 1 | 풋프린트 EP GND | ✅ (import로 처리, 보드레벨 EP비아는 Phase7) |
| 2 | PCB6 생성 + 회로도 import | ✅ 완료·검증 |
| 3 | 전원-인식 배치 | ✅ 완료·검증 |
| 4 | 전원 FIRST 라우팅 | ✅ pour 방식으로 완료 (clearance 155→0) |
| 5 | GND평면 | ✅ Inner1 GND pour |
| 6 | 신호 라우팅 | ⏳ 진행 예정 (오토라우트) |
| 7~8 | 비아·검증 | 대기 |

## ★Phase 4 재작업 — pour 방식 성공 (clearance 155→0)
굵은 직선 트레이스(155 위반) 폐기 → **네이티브 구리 pour** 방식으로 전환, **클리어런스 위반 0** 달성:
- **VBUS_5V, PVDD_12V = Top 구리 pour** (`pcb_PrimitivePour.create`). pour가 장애물 자동회피 + 전류용량 + U4/U3 미세피치 핀 자동 클리어.
- **GND = Inner1(layer15) 평면 pour**.
- 충전(fill) = **Shift+B**(UI; API에 repour 없음). `pcb_PrimitivePoured.getAll()`로 충전 확인.
- BOOST_SW = 미세피치 영역이 좁아 pour 충전 불가 → 오토라우트에 위임(짧아서 thin 허용).
- 배치 4곳(C5↔D1, C22↔R2, R5↔U1) 패드충돌 → 부품 살짝 이동으로 해소.
- 결과: **DRC Clearance Error = 0**, Connection Error 160(미라우팅 신호+GND비아, 예정).

### pour API 주의 (확정)
- `pcb_PrimitivePour.create(net, layer, complexPolygon, fillMethod?, preserveSilos?, pourName?, **pourPriority**?, lineWidth?, lock?)` — **pourPriority에 숫자를 주면 생성 실패**("对象参数不正确"). **priority=undefined로 호출**해야 함.
- complexPolygon: `eda.pcb_MathPolygon.createPolygon(['R', x, y, w, h, 0, 0])` — **'R'의 x,y=위쪽-왼쪽 모서리, height는 아래로 확장**(y=maxy 사용). 'L' 모드는 거부됨.
- create가 에러를 던져도 pour는 실제 생성되는 경우 있음(`getAll()`로 확인).
- 레이어: Top=1, Bottom=2, Inner1=15, Inner2=16.

---

## PCB6 구조 (EasyEDA 클라우드)

- 프로젝트 `eaca910eadcb42049fff04c549930a59`
- **Board1_1** = { **schematic1_1**(uuid `2009e7facc9c626c`, Schematic1 복제본) + **PCB6**(uuid `b6705c1de2a76ac3`) }
- **PCB5 / Schematic1 / Board1_2 = 완전 보존**(별개 백업 쌍)

### 왜 회로도를 복제했나
EasyEDA는 **보드 1개 = 회로도 1개 + PCB 1개**를 강제한다. `createPcb("Board1_2")`는 PCB5가 이미 있어 실패. 같은 Schematic1에 두 번째 PCB를 붙일 수 없으므로:
`copySchematic(Schematic1)` → `createBoard(복제본, PCB6)` 로 PCB6 전용 보드 쌍을 만들었다. (사용자 승인)

### Phase 2 검증값
- 4층 / **44부품** / **38넷** / D2 부재 확인 ✓
- import 절차: `createPcb()`(독립PCB) → openDocument → `setTheNumberOfCopperLayers(4)` → copySchematic+createBoard → **PCB를 프로젝트 트리에서 더블클릭(에디터 렌더 필수)** → 자동으로 뜨는 "Confirm Importing changes" 대화상자에서 **Apply Changes 클릭** (API `importChanges`는 true만 반환, 실제 적용은 UI 클릭 필요)

---

## Phase 3 — 전원-우선 배치 (완료)

- **보드 외곽선 88×60mm** (PCB5 80×52에서 확장; 사용자 승인). 4선 layer 11.
- 44부품 전부 외곽선 안, 보드 밖 패드 0개.
- 좌표 단위 = **mil** (확인: U1 ESP32 풋프린트 708.9mil = 18.0mm). +x=오른쪽, +y=위, 부품 x,y=중심.
- 부품 이동 API: `eda.pcb_PrimitiveComponent.modify(comp, {x, y, rotation})` (mil).

### 플로어플랜 (좌→우 전원 흐름)
- 좌하단: **USB_C**(9,16,rot90) → 입력 D1/C3/C5/R3/R4
- 중앙좌측: **L1**(22,16) · **U3 부스트**(29,15) · D3(34,19) + 부스트 지원 패시브
- 좌상단: **U2 LDO**(12,27) + C10/C11/C18
- 중앙: **U4 앰프**(54,16) + PVDD/AVDD/I2C/부트스트랩 패시브
- 우측 가장자리: **J1**(84,20,rot180) · **J2**(84,12,rot180) 트랜스듀서 출력
- 상단: **U1 ESP32**(54,42,**rot270**=안테나 위쪽 가장자리) · **U5 IMU**(40,45) · ESP 패시브
- 하단: **UART_HDR**(32,4)

### 핵심 성과 — 전원체인 거리
| 경로 | PCB6 | PCB5 |
|---|---|---|
| **USB→U3 (VBUS 2.6A)** | **20mm** | 52mm |
| L1→U3 (부스트 입력루프) | 7mm | — |
| U3→U4 (PVDD) | 25mm | — |
| U4→J1 (AMP_OUT) | 30mm | — |

**VBUS 경로 52→20mm (60%↓)** — 전원-우선 재설계의 핵심 목표 달성.

---

## Phase 4 — 전원 라우팅: 방식 재검토 (중요)

### 시도와 실패
전원넷을 **최소신장트리(MST) 직선 트레이스, 넷별 굵은 폭**(VBUS40/BOOST_SW30/PVDD25/AMP_OUT20/BST20 mil)으로 그렸으나 → **네이티브 DRC 클리어런스 위반 155개**.

### 원인 (배치 문제 아님 — 방식 문제)
1. 직선 트레이스가 부품/패드를 가로지름 (장애물 회피 안 함)
2. 굵은 트레이스가 U4(TAS5805M 미세피치)에서 인접핀과 충돌
→ **굵기(전류용량) vs 미세피치 진입(가늘어야) vs 장애물 회피**를 직선 그리기로는 동시 충족 불가.

### 결정된 방향 — "오류 없이 가장 정확한 방법"
네이티브 도구(클리어런스를 구조적으로 보장)를 사용한다:
1. 크루드 전원 트레이스 정리
2. **Inner1 = GND 평면(pour)** → GND 배선 제거, 라우팅 단순화
3. **VBUS·PVDD = 구리 pour** (장애물 자동 회피 + 전류용량 + 미세피치 핀 자동 진입/클리어)
4. 나머지 신호·저전류 = **네이티브 오토라우터** (클리어런스 위반 구조적으로 0)
5. 재시작 → **권위 DRC** (재시작 직후 1회)

핵심: pour와 오토라우터는 **클리어런스를 위반하지 않도록 설계된 엔진**이라, 수동 직선보다 정확.

---

## 인프라 — 브릿지 (이번 세션 수정)

- **IPv6 듀얼스택 버그 수정**: `easyeda-api-skill/scripts/bridge-server.mjs`의 `LISTEN_HOST`를 `'127.0.0.1'`→`'::'`로 변경. Windows에서 `localhost`가 `::1`(IPv6)로 먼저 해석되는데 서버가 IPv4 전용이면 EasyEDA 확장이 "Bridge not found"로 못 찾는 문제. 듀얼스택으로 자동 재연결됨.
- **멀티윈도우 stale 복구**: 재로딩 시 easyeda-pro가 여러 webview로 분열 → 캔버스 API "no relevant subscription" 에러. 해결: `Stop-Process -Name easyeda-pro -Force`(전부 종료) → 재기동(듀얼스택이라 자동연결) → 단일 윈도우 → 프로젝트/PCB 트리 더블클릭(에디터 렌더). openDocument API만으론 캔버스 구독 안 됨.
- 넷클래스/규칙 API는 전부 MISSING(`pcb_NetClass`/`Rule`/`DesignRule`). 전원폭은 pour 또는 (UI) Net Class Manager로.

---

## 다음 세션 시작 절차
1. 브릿지: `node bridge-server.mjs`(TEMP 또는 리포 scripts) → EasyEDA API Gateway → Reconnect → `/health`로 activeWindowId 확인(bridge.js가 자동 발견)
2. 프로젝트 트리에서 **PCB6 더블클릭**(캔버스 렌더)
3. Phase 4 방향(위 5단계)대로: GND평면 → VBUS/PVDD pour → 신호 오토라우트 → DRC
