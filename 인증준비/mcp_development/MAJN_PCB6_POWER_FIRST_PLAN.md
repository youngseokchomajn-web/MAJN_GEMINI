# MAJN PCB6 — 전원-우선 재설계 계획 + 컨텍스트 요약 (자립 문서)

작성 2026-06-23. **이 문서 하나로 새 세션에서 바로 이어갈 수 있게** 작성됨.
대상: 마중 스마트 배시넷 (KC 인증 준비). 4층 PCB, EasyEDA Pro (Full Online).

---

## 0. 왜 PCB6인가 (트리거)

PCB5는 **DRC 클린 + 기능 완성**까지 갔으나, **전원 트레이스가 전부 ~10mil(≈1A)** 이고 **조밀하게(4mil 클리어런스) 오토라우팅**돼 있어 **제자리에서 못 넓힌다**(넓히면 클리어런스 15~43개 폭발 = R2 교훈 재현).

확정된 **진동 트랜스듀서 스펙**:
- 8Ω, **10W RMS / 30W Max**, 20-80Hz, FS 40Hz, **Force Peak 30 lbs** (= bass shaker, 물리 진동용), 페라이트, 250g, 케이블 200cm.

→ TAS5805M가 12V에서 8Ω에 **최대 ~8W** 구동. 이때 전류:
| 구간 | 최대(~8W) | 필요 폭 |
|---|---|---|
| AMP_OUT (8Ω) | 1.0A RMS / 1.4A 피크 | **≥15-20mil** |
| PVDD_12V | 0.75A 평균 / 1.5A 피크 | **≥20-25mil** |
| VBUS_5V (부스트입력+3V3) | **~2.6A** | **≥35-40mil** |
| BOOST_SW | 2A 평균 / **4A 펄스** | **≥30mil**(+짧게) |
| VCC_3V3 | ESP32 ~0.5A | 12-15mil |

**결론: 10W 트랜스듀서를 제대로 구동하려면 전원선을 굵게 깔아야 하고, 그건 전원-우선 재배선(PCB6)으로만 가능.**

---

## 1. 설계 사실 (검증됨)

- **프로젝트**: `eaca910eadcb42049fff04c549930a59` / Board1_2 / **Schematic1 uuid `1b62a2b269c7d7ab`**.
- **PCB5** = 현재 클린 백업(보존). PCB6 = 새로 만들 보드.
- **BOM 44부품** (D2 제거 후):
  - U1 = **ESP32-WROOM-32E-N8** (두뇌, WiFi/BLE, 8MB플래시 OTA가능, 내장안테나)
  - U2 = **SGM2036-3.3** (LDO 5V→3.3V) ⚠️ ESP32 피크 ~500mA 대비 정격 확인 권장
  - U3 = **MP3426** (부스트 5V→12V)
  - U4 = **TAS5805M** (Class-D 오디오앰프, I2S입력, I2C제어, PVDD=12V, BTL출력)
  - U5 = **LSM6DSOX** (6축 IMU, SPI연결, 진동 피드백)
  - D1 = SMAJ5.0A (5V TVS 보호)
  - **D2 = 제거됨** (USBLC6-2SC6, USB데이터 ESD였으나 USB데이터선 부재로 미사용 → 회로도+PCB 삭제 완료)
  - L1 = 부스트 인덕터, R1~R11, C1~C22(C16없음)
  - **USB_C** = TYPE-C-31-M-12 (**충전 전용** — D+/D- 없음, VBUS_5V+CC1/CC2만)
  - **UART_HDR** = B-2100S06P (6핀: `1=3V3, 2=EN, 3=IO0, 4=TXD, 5=RXD, 6=GND`) ← 유선 플래싱/통신 (외부 USB-UART 어댑터)
  - J1, J2 = B-2100S02P (2핀, 트랜스듀서/스피커 출력)
- **38넷**: VBUS_5V, VCC_3V3, PVDD_12V, AVDD, BOOST_SW/EN/FB/FSET/COMP/VDD, COMP_RC, VR_DIG, AMP_OUT_A±/B±, BST_A±/B±, AMP_I2C_SCL/SDA, AMP_PDN, I2S_BCLK/LRCLK/DIN, SPI_MOSI/MISO/SCLK/CS, SENSOR_INT1, ESP_EN/IO0/RXD/TXD, USB_CC1/CC2, GND.
- **전원 흐름**: USB-C 5V → U2(LDO)→3.3V(ESP32+IMU) / U3(부스트)→12V(PVDD)→U4(앰프)→AMP_OUT→J1/J2(트랜스듀서)
- **통신**: 무선=ESP32 WiFi/BLE / 유선=UART_HDR(외부어댑터). USB-C는 충전만. (ESP32-WROOM은 USB네이티브 없음 → USB직결통신 불가, UART헤더만)
- **안전(12V 차단)**: BOOST_EN(U1 IO26 제어) + R11(100k 풀다운=기본 OFF). ESP32가 부스트 켜고/끔.
- **부팅 스트래핑(검증됨, 정상)**: EN(R5 1k풀업+C17 0.1µF→GND), IO0(R6 1k풀업), IO12 플로팅(=3.3V플래시), IO2 플로팅, IO15=AMP_PDN(내부풀업), IO5=SPI_CS(내부풀업).

---

## 2. 전원-우선 목표 폭 (PCB6 핵심)

| 넷 | 목표 폭 | 비고 |
|---|---|---|
| VBUS_5V | **40mil** 또는 **전원 pour** | 전체 입력전류 ~2.6A |
| BOOST_SW | **30mil** | 짧게(<10mm), 입력루프(VBUS-L1-SW) 타이트, EMI |
| PVDD_12V | **25mil** 또는 pour | 앰프 공급 ~1.5A |
| AMP_OUT_A/B | **20mil** | 트랜스듀서 출력 ~1.4A |
| VCC_3V3 | 15mil | 여유 |
| GND | Inner1 평면 | OK |

**스택업 결정 (Phase0)**:
- **옵션1: 4층 + 전원-우선 굵은 트레이스 + 전원 pour**(VBUS/PVDD를 Top/Bottom 일부에 폴리곤으로). 비용↓, 배치 여유 필요.
- **옵션2: 6층** (Top/GND/Signal/**Power평면**/Signal/Bottom). 전원분배 깔끔·견고, 비용↑. 10W 진동 제품엔 정당화 가능.
- 권장: 4층 전원-우선 먼저 시도, 굵은 전원이 안 들어가면 6층.

---

## 3. 실수·오류 카탈로그 + 회피법 (★PCB6에서 반드시 반영)

### 배선 (★PCB6의 존재 이유)
| # | 실수 | 회피법 |
|---|---|---|
| **R2** | **라우팅 끝난 뒤 전원 정폭→클리어런스 폭발** | **전원을 먼저, 굵게 깔고 LOCK → 그 다음 신호 라우팅**. 절대 사후 확장 금지 |
| R1 | 블라인드 수동배선(조밀)→577 클리어런스 | 조밀구역=오토라우터(신호만). 전원은 수동 굵게 |
| R3 | 한 층 과밀→512 | Top/Bottom/Inner2 3신호층 + Inner1 GND평면 |
| 신규 | 오토라우터가 ~4mil 클리어런스로 빽빽→여유0 | 신호 오토라우트 시 **전원 트레이스 LOCK** + 클리어런스 여유 확보 |

### 규칙 (★하드 제약)
| # | 함정 | 회피법 |
|---|---|---|
| **S3** | **Design Rule 대화상자 무한멈춤(설치 전반, PC재부팅으로도 복구 안 됨 — 이번에 확정)** | 규칙값(클리어런스/폭/via-in-pad면제) **대화상자로 설정 불가**. → 폭은 **Net Class Manager**(Design메뉴) 시도 OR 라우팅 시 툴바 폭 지정 OR 수동. via-in-pad 면제 불가 → 해당 플래그는 문서화 |
| B3 | 규칙쓰기 API 전부 no-op | 규칙 API 신뢰 금지 |

### 브릿지 API (이번 세션 검증)
| # | 사실 | 활용 |
|---|---|---|
| B1 | 라인 `create()`+`await .done()` 필요 | 라인 생성 |
| **신규** | **라인 `modify(obj,{lineWidth:X})`+`await .done()` 작동** | 폭 변경 가능(라인은 됨) |
| B2 | 비아 `create`만(자동커밋), `.done()` 금지 | 비아 생성 |
| **신규** | **region/keepout `modify`는 실패**(.done→"getSource is not a function", 라이브 UI객체 필요) | keepout/region 편집은 **UI 속성패널**로(숫자 Start X/Y/W/H 필드 작동) |
| 신규 | 회로도 부품삭제 `eda.sch_PrimitiveComponent.delete(id)`+`sch_Document.save()` 작동 | + PCB는 Design→Import Changes로 동기화 |
| 신규 | 실행규약: 코드는 async함수 본문, **최상위 `return`** 값이 결과 (IIFE는 null) | 모든 브릿지 스크립트 |

### 검증
| # | 실수 | 회피법 |
|---|---|---|
| V1 | 자체 기하검사가 레이어 무시→"완료" 오판 | **네이티브 DRC `eda.pcb_Drc.check(true,false,true)`(verbose필수)만 신뢰** |
| V3 | 브릿지 DRC 몇 회 후 degrade | **재시작 직후 1회**가 권위 DRC |
| 신규 | 자체 union-find 연결성추적이 DRC와 불일치 | 연결성 판단은 **DRC만** 신뢰(자체추적 금지) |

### 풋프린트/EP
| # | 문제 | 회피법 |
|---|---|---|
| F1/F2 | U4/U1 EP 열비아 넷없음 | 풋프린트에서 EP비아 GND확정, 또는 배치후 GND비아 추가. **고전류라 U4 EP 접지 견고히** |

### 안테나 keepout (이번에 해결법 확정)
| # | 문제 | 회피법(검증됨) |
|---|---|---|
| R6 | keepout이 U1 코너핀(1,38) 덮어 접지 차단 + "Device to Prohibited Region" | **keepout을 핀 밖으로**(속성패널 Start Y/Height 숫자편집) + **"Component" 금지 해제**(모듈이 자기 keepout 위에 있는 건 정상). Track/Copper 금지는 유지 |

### 접지 (이번에 작동 확인)
| # | 사실 | 방법 |
|---|---|---|
| 신규 | Inner1 GND 평면은 same-net 비아에 연결됨 | 부유 GND핀 → **GND비아 추가 + Inner1 활성화 후 Shift+B 재충전** → 평면 접지 |
| R5 | autoroute가 GND핀 누락 | GND평면+비아로 접지, DRC로 검증 |

### 프로세스
| # | 실수 | 회피법 |
|---|---|---|
| P1 | 깨진 방법에 오래 매달림 | 2회 no-op/실패면 즉시 우회 |
| P2 | 재시작 남발(DRC degrade) | 변경 일괄→재시작1회→DRC1회 |
| 신규 | PC재부팅 시 브릿지 서버 죽음 | §4 절차로 재기동 |

---

## 4. 브릿지 셋업 (새 세션에서 재연결 절차) ★중요

**구조**: `bridge-server.mjs`(Node, 포트49620-49629) ↔ EasyEDA 확장(API Gateway) + `bridge.js`(클라이언트).

**파일 위치** (TEMP — 재부팅 시 정리될 수 있으니 존재 확인):
- 서버: `C:\Users\newdo\AppData\Local\Temp\MAJN_GEMINI\인증준비\mcp_development\easyeda-api-skill\scripts\bridge-server.mjs`
- 클라이언트: `C:\Users\newdo\AppData\Local\Temp\bridge.js` (argv2=코드파일, argv3=출력파일; WINID 기본값을 /health의 activeWindowId로 갱신)

**재연결 절차**:
1. 서버 기동: `cd <scripts dir>` → `node bridge-server.mjs` (백그라운드). `ws` 없으면 `npm install ws` 먼저.
2. `/health` 확인: `curl http://127.0.0.1:49620/health` → `edaConnected`, `activeWindowId`.
3. EasyEDA: 시작페이지 상단 **API Gateway 메뉴 → Reconnect**. (자동연결 안 되면)
4. `bridge.js`의 WINID를 /health의 activeWindowId로 갱신.
5. **테스트**: `return JSON.stringify({t:typeof eda, n:(await eda.pcb_PrimitiveComponent.getAll()).length})` — null/에러나면 **컨텍스트 stale** → **EasyEDA 깨끗이 재시작 + 프로젝트 트리에서 PCB 더블클릭으로 열기**(탭전환만으론 안 됨) → WINID 재갱신.

**실행규약**: 코드는 `async (eda)=>{...}` 본문으로 실행 → **최상위 `return`** 으로 값 반환.

**핵심 API**:
- DRC: `await eda.pcb_Drc.check(true,false,true)` → 카테고리 배열, 각 `.list[].list[]`에 인스턴스(obj1/obj2 suffix, pos, errData). pos는 **mil/10 단위**(×10=mil).
- 라인: `getAll()` / `create(net,layer,x1,y1,x2,y2,width,false)`+`.done()` / `modify(obj,{lineWidth})`+`.done()` / `delete(id)`.
- 비아: `create(net,x,y,holeDia,dia,viaType,"",null,false)` (.done 금지) / `delete(id)`.
- 패드/부품: `getAll()`, 패드 primitiveId는 부품 primitiveId로 시작.
- region: getAll/get/delete OK, **modify 실패→UI로**.
- 레이어: `pcb_Layer.getTheNumberOfCopperLayers()`. 층: Top=1, Inner1=15, Inner2=16, Bottom=2, BoardOutline=11, Multi=12.
- 저장: `eda.pcb_Document.save()`. 동기화: Design→Import Changes(UI).

---

## 5. 전원-우선 실행 순서 (PCB6)

**Phase 0 — 셋업+게이트**: 브릿지연결(§4). 스택업 결정(4층 전원우선 vs 6층). Net Class Manager로 전원 폭 설정 가능한지 확인(규칙 대화상자는 고장).

**Phase 1 — 풋프린트 EP**: U4/U1 EP 열비아 GND 확정(고전류라 견고히).

**Phase 2 — PCB6 생성**: `createPcb`+`importChanges(Schematic1 uuid 1b62a2b269c7d7ab)`. 4/6층 설정. 검증: 44부품·38넷. (D2는 이미 회로도에서 제거됨)

**Phase 3 — 배치(전원 인식)**: 전원체인(USB_C→U2/U3→L1→U4) 가깝게 + **굵은 전원 경로 공간 확보**. U1 안테나는 보드 가장자리, keepout이 U1 핀 안 덮게. PCB5 검증좌표 참고하되 전원폭 위해 조정.

**Phase 4 — ★전원 FIRST 라우팅**: VBUS40/BOOST_SW30/PVDD25/AMP_OUT20/VCC15mil로 **전원 먼저 굵게**(수동 또는 폭지정). 또는 VBUS/PVDD를 **pour**로. BOOST_SW 짧고 타이트. **완료 후 전원 트레이스 LOCK**.

**Phase 5 — GND평면+keepout**: Inner1 GND solid pour. 안테나 keepout = 안테나만(U1패드 제외) + "Component" 금지해제, Track/Copper 금지유지.

**Phase 6 — 신호 라우팅**: 전원 LOCK 상태에서 신호(SPI/I2S/I2C/UART/ESP제어)를 오토라우트(All, Remove existing, 45°, Top/Bottom/Inner2; Inner1=GND평면 제외). SPI_MOSI↔GND 단락 같은 것 주의.

**Phase 7 — GND비아+재충전**: U1(1/15/38/EP)·U4 EP GND비아, 스티칭. **Inner1 활성→Shift+B 재충전**.

**Phase 8 — 검증(§6)**: 재시작→권위 DRC 0 → 넷무결성 → 회로도일치 → 스트래핑 → **전원폭 확인** → (사용자확인 후)거버.

---

## 6. 검증 방법 (이번 세션에서 확립, 그대로 사용)

1. **재시작 직후 네이티브 DRC 1회** = 0 오류 목표 (`check(true,false,true)`).
2. **넷 무결성**: 모든 넷 pad≥2 (singleton 0). NC핀은 의도된 것만(U1 미사용GPIO, USB-C 데이터).
3. **회로도↔PCB**: Design→Import Changes → "No changes, schematic already matches PCB".
4. **부팅 스트래핑**: EN/IO0 풀업, IO12 플로팅, IO2/IO15/IO5 확인.
5. **전원 트레이스 폭**: 목표폭 달성 확인 (`getAll().filter(net).map(lineWidth)`).
6. **통신**: UART헤더 6신호 배선, 무선(안테나·접지·플래시).
7. **층/외곽선**: copperLayers, 보드 외곽선.
8. 거버: `pcb_ManufactureData.getGerberFile` 등은 **파일 다운로드라 사용자 명시 허락 필요**.

---

## 7. 컨텍스트 요약 (새 세션용 한눈에)

- **목표**: 마중 스마트 배시넷(KC인증준비) 4/6층 PCB. ESP32 두뇌 + IMU 진동피드백 + TAS5805M로 **10W/8Ω 진동 트랜스듀서** 구동 + 충전USB-C + 무선/UART통신.
- **현 상태**: PCB5 = DRC클린·기능완성 백업이나 **전원선 10mil로 트랜스듀서 풀파워엔 부족**(R2로 제자리 보강 불가) → **PCB6를 전원-우선으로 재설계**하기로 결정.
- **이번 세션 성과**: 브릿지 복구법 확립 / Design Rule 대화상자 복구불가 확정(PC재부팅도 실패) / D2(미사용 USB ESD) 제거 / 안테나 keepout 축소+코너GND 접지로 **PCB5 DRC 0 달성** / 전원폭 보강 시도→조밀해서 불가 확인(R2) / 트랜스듀서 스펙 확인→PCB6 결정.
- **핵심 제약**: ①규칙 대화상자 고장(폭/클리어런스 규칙 설정 어려움) ②region modify는 UI로 ③전원은 반드시 먼저·굵게.
- **다음 행동**: 새 세션에서 §4로 브릿지 연결 → §5 Phase0부터.

---

## 8. 진행 로그
- 2026-06-23: 본 계획 작성. PCB5 클린 저장됨(백업). PCB6 착수 대기.
