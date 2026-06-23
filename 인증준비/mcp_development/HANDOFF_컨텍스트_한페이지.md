# 마중 배시넷 PCB — 컨텍스트 핸드오프 (한 페이지, 2026-06-22)

## 1. 목표 & 결정
**마중 스마트 배시넷**(KC 인증 영유아 진정기기)의 PCB를 **회로도(Schematic1)에서 처음부터 새로 빌드**한다 — 배선 효율 최우선. 기존 보드는 안 씀(아래 2번 이유).
- 제품: IMU 피드백 30–65Hz 진동(보이스코일)으로 달램 + **낙하감지 시 12V 비상차단(BOOST_EN/GPIO4, KC 핵심안전)** + 오디오알림 + ESP32 무선.
- 전원: USB-C 5V → U2(LDO)→3.3V(로직) / U3(MP3426 부스트)→12V(진동액추에이터+앰프). 12V 주부하=진동(~2A)이라 전원폭 중요.
- 부품: U1 ESP32 / U2 LDO / U3 MP3426부스트 / U4 TAS5805M앰프 / U5 LSM6DSOX IMU / L1·D3 부스트 / J1·J2 액추에이터·스피커 / USB_C / UART_HDR. (45부품, 38넷)

## 2. 보드 현황 (프로젝트 "New Project_2026-06-20", Board1_2, Schematic1)
- **회로도=정정 완료**(원설계자 오류 S1~S7 수정: U4 EP 12V→GND, PVDD 4핀, I2C SDA=10/SCL=11, I2S LRCLK=6/DIN=8, U5 VDD/VDDIO=3.3V, U3 풋프린트 2패드→15패드, USB CC1/CC2, 디커플·풀업). pinmap_master.md가 SSOT.
- **PCB3**(uuid 41d3decccb60fc44): 592트랙, ✅**DRC 0**(브릿지+UI 확인), EP=GND·열비아 12개 GND. 정상이나 전원 ~10mil.
- **PCB3_1**(uuid 30406c0292c8bbfc): PCB3와 **넷리스트 동일**, 레이아웃만 다른 **망가진 복사본**(DRC 50). 작업금지.
- 사용자 결정: 둘 다 안 쓰고 **새 PCB 처음부터**. (이전 세션 내내 PCB3_1을 잘못 붙잡아 헛수고함.)

## 3. PCB3_1에서 겪은 오류(=새 보드에서 막아야 할 것) & 근본원인
- **A. U4 열패드 32개**: EP밑 비아 12개 빈-네트. (GND지정+동박재생성하면 Copper Region 53개 폭발=EasyEDA quirk; PCB3는 깨끗이 해결됨)
- **B. USB-C 충돌 8개**: R3/R4가 장착홀에 0mil 겹침 → 클리어런스+미연결.
- **C. 미세핀 미배선 10개**: U4 0.65mm핀으로 I2C/I2S/VR_DIG/BOOST_FB/I2S_LRCLK 마지막홉 미완(U1↔U4 원거리 탓).
- **잠복**: 전원 전부 10mil(설계의도 VBUS1.2/PVDD1.0/SW0.8mm), GND 트랙 168개 난립(평면 무시), pour 클리어런스 2mil↔규칙 6mil 불일치.
- **두더지잡기 근원 3개**: ①U1↔U4 원거리 ②GND 트랙 난립 ③규칙없이 사후 전원폭 확대.

## 4. 확정 규칙 (Phase1에서 UI로 설정)
- 넷클래스 폭: **VBUS_5V 1.2 / PVDD_12V 1.0 / BOOST_SW 0.8 / AMP_OUT 0.5 / VCC·신호 0.25mm**, GND=평면.
- 클리어런스 6mil, 홀↔동박 6.9mil, **pour 클리어런스 6mil**(규칙일치), **같은-넷 via-in-pad 허용**(열비아).
- 레이어: L1 Top(부품+신호+전원)·**L15 Inner1=솔리드 GND평면**·L16 Inner2(전원분배+신호)·L2 Bottom. 1oz(전원 빡빡하면 2oz). 보드 80×60mm, ESP32 안테나 keepout.

## 5. 빌드 플랜 (5 Phase, 각 단계가 위 오류를 원천차단)
- **P0** 새 빈 PCB 생성 → 회로도 Import(45부품+래트선, 배선0).
- **P1** 규칙 먼저(위 4번) ← 클리어런스/전원미흡 차단.
- **P2** Inner1 솔리드 GND평면 + 스티칭비아(**GND 트랙 금지**) ← Track-Via 군집 차단.
- **P3 ★** 배치=배선효율 핵심: 선형흐름(USB-C→부스트→앰프→J1/J2) + **U1↔U4 인접**(I2C/I2S 6넷)·U1↔U5 인접(SPI)·부스트루프 최소·**R3/R4 홀이격**·디커플캡 겹침금지·미세핀 팬아웃 사전계획. (좌표 확정 전 플로어플랜 그림으로 합의)
- **P4** 전원 동맥 먼저(정폭) → 핵심신호(이미 짧음) → 나머지. **사후 폭확대 금지**.
- **P5** 동박(UI Shift+B) → **UI DRC 0** → 넷리스트대조 → Gerber 재출력.

## 6. 도구(EasyEDA 브릿지) 주의 — 필수
- 브릿지 `POST http://127.0.0.1:49620/execute {code, windowId}`. 코드는 **최상위 return + await** 필요. 헬퍼 `/tmp/bridge.js`(=%TEMP%, AppData\Local\Temp).
- **창 바인딩**: 재시작/리로드 후 브릿지가 빈 호스트창에 붙어 `getAll()`이 null. 해결: 활성창에서 `globalThis.location.reload()` 실행 → `curl /health`로 PCB 가진 새 activeWindowId 잡아 bridge.js에 박기.
- **무거운 작업(DRC·clearRouting·동박재생성)은 UI로** — 브릿지 동박재생성 rpcCall이 DRC degrade(120s timeout) 방아쇠. 브릿지는 **부품이동(modify)·읽기 전용**.
- 저장 직후 리로드 금지(클라우드 동기 후). 단계마다 JSON 백업. DRC 구조: `eda.pcb_Drc.check(true,false,true)` → 3카테고리 {name,count,list}.

## 7. 핵심 파일 & 다음 행동
- 상세: `인증준비/mcp_development/MAJN_PCB_종합정리_재생성계획.md`(컨텍스트+오류), `MAJN_PCB_FROMSCRATCH_빌드플랜.md`(빌드플랜), `pinmap_master.md`(핀맵 SSOT). 백업: `PRELAYOUT_BACKUP_*.json`.
- **다음 행동: Phase 0 — 새 빈 PCB 생성 + 회로도 Import부터 시작.**
