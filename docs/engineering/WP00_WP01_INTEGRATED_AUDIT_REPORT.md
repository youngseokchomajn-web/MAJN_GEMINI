# [MAJN Engineering System] WP-00 및 WP-01 통합 조사·기준선 감사 보고서 (Authoritative Baseline Audit)

- **문서 식별자**: `MAJN-ENG-WP00-WP01-AUDIT-FINAL`
- **기준 브랜치**: [`origin/docs/engineering-system-plan`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/tree/docs/engineering-system-plan)
- **작업 브랜치**: `docs/engineering-system-wp00-wp01-baseline`
- **상태**: Draft for Human & Peer Review (Gate 0 Baseline Review)
- **실물 하드웨어 기준 (Physical Baseline)**: PCB #0005 (4층 기판, 12.00V 승압 및 50Hz 물리 진동 실측 완료)
- **최신 목재 가공 기준 (Housing SSOT)**: Rev 2 Master SSOT (4.5T 자작합판, 450.0 × 250.0 × 22.5 mm, 10볼트 체결, 캐비티 13.5 mm)

---

## 1. 개요 및 요약 (Executive Summary)

본 문서는 MAJN 스마트 배시넷 엔지니어링 통합 시스템 구축의 제1단계인 **WP-00(기존 자료 및 저장소 조사)**과 **WP-01(기준 형상·구성·불일치 감사)**의 공식 결과물입니다.

본 감사는 저장소 내 선행 분석 결과 및 작업 가설을 무비판적으로 수용하지 않고, 실제 소스 코드, 10종 DXF 도면(ezdxf 파싱), EasyEDA PCB 넷리스트 및 거버 파일, 실측 DMM/임피던스 CSV, 펌웨어 소스(FreeRTOS/OTA), 그리고 웹 기반 CAE 시뮬레이션 엔진을 교차 대조(Skeptical Verification)하여 독립적으로 수행되었습니다.

그 결과, 선행 분석에서 제기되었던 **기구 간섭 유발 치수 오류(그로밋 관통홀 오기재), CAE 시뮬레이션 자산의 존재 누락, 2대 제품 규격(가정용 450×250 vs 조리원용 720×390)의 혼동, 기구 DXF 내 PCB 마운팅 인터페이스 누락, 요구사항 정의서(E01) 및 펌웨어 드라이버 다수 누락, 익사이터 임피던스(공칭 8Ω vs 실측 21.6Ω) 모순 등 총 12가지 중대 결함과 오류를 적발하여 정밀 교정**하였습니다.

---

## 2. 선행 조사 12대 결함·오류 교정 대조표 (Claim vs Ground Truth)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         [ 선행 조사 12대 결함 및 팩트 교정 정합성 대조표 ]                       │
├────┬─────────────────────────────┬─────────────────────────────┬────────────────────────────────┤
│ No │ 선행 보고서 주장 (Claim)     │ 실제 코드/데이터 (Ground Truth) │ 교정된 공학적 판정 (Correction)│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 1  │ 주전원 그로밋이 단변 중앙   │ build_rev2_dxf.py 상 단변   │ [기구 간섭 교정] 중앙 Y=125mm   │
│    │ (Y=125mm, Z=6.75mm)에 위치  │ 레일 끝 X=30mm(Y≈50mm) 타공 │ 타공 시 16×14mm 나사보스와 충돌│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 2  │ E11 CAE 영역이 미구축/미보유│ bassinet_simulator/ 내 C3D10│ [CAE 맹점 복원] 브라우저 기반   │
│    │ 상태라고 단정               │ 솔버, .INP 생성기, FEA 가동 │ 솔버 가동 중. ccx CLI 연동 대상│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 3  │ 450×250 단일 치수만 분석하고│ 가정용(450×250×22.5mm)과     │ [제품군 분리] CFG-HOME-450과   │
│    │ 720×390은 단순 레거시로 취급│ 조리원용(720×390×45mm, IP67)│ CFG-HOSPITAL-720 2대 매니페스트│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 4  │ 8Ω 2직렬 16Ω 부하 구동이라  │ Resistance.csv 상 단품 10.8 │ [임피던스 모순 규명] #0005는   │
│    │ 면서 실측치 21.6Ω을 병기    │ 2직렬 21.6Ω(공칭 12Ω 샘플) │ 12Ω 샘플 계측. 8Ω 적용시 발열↑│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 5  │ 하우징 SSOT가 메인 결정 로그│ 메인 결정 10은 여전히 6볼트  │ [문서 불일치 적발] ADR과 메인  │
│    │ 와 완전히 일치한다고 서술   │ 도면 명시. 10볼트는 ADR에만 │ 결정 로그 간 Rev 2 ECO 동기화  │
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 6  │ E01 요구사항으로 일반 계획서│ 28개 구조화 ID(INT/FUN/SAF) │ [요구사항 복원] 10-12 문서 원본│
│    │ 2종만 수록                  │ 수록된 10-12 요구사항 누락  │ 을 requirements_register로 임포트│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 7  │ 3D 뷰어(view_3d_rev2)가     │ 뷰어에는 PCB, 안테나, 케이블│ [가시화 한계 식별] 뷰어는 목재 │
│    │ 전체 어셈블리 완벽 반영 주장│ 그로밋이 전혀 모델링 안 됨  │ 전용이며 전장 통합 모델링 필요 │
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 8  │ 기구 하판과 PCB 간 조립 적합│ 마스터 DXF 하판에 PCB 장착용│ [기구 결함 적발] 하판에 M3 스탠│
│    │ 성이 확보되었다고 판정      │ 4개 나사홀 가공이 완전 누락 │ 드오프홀 4개소 추가 가공 필요  │
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 9  │ E08 펌웨어를 7개 파일로 축소│ ble_manager, lsm6dsox, 8MB  │ [펌웨어 복원] 16개 파일 및 8MB │
│    │ 목록화                      │ 파티션 등 10개 핵심 파일 누락│ 커스텀 파티션 테이블 전수 복원 │
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 10 │ E12/E13 안전·계측 자산에서  │ BOOST/AMP 차단 FAULT_MATRIX │ [안전/계측 복원] 차단 계통도 및│
│    │ 계통도 및 5개 좌표 누락     │ 및 P1~P5 VIBRATION_PROTOCOL │ 5개 계측점 절대좌표 파이프라인 │
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 11 │ DXF 바운딩박스를 절단 크기로│ Y=-30mm 도면 제목 텍스트 포함│ [네스팅 정정] 실제 가공 크기는 │
│    │ 오인 (591×675.5mm 기재)     │ 수치임. 실제 판재는 591×645.5│ 591.0×645.5mm (600×900 베드 안착)│
├────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────┤
│ 12 │ 파일 크기 및 라인 번호의 광 │ 터미널 실측과 다수 불일치   │ [데이터 정규화] ls -l 및 해시  │
│    │ 범위한 부정확성             │ (SHA256SUMS 79B vs 152B 등) │ 명령어로 전수 실측 및 정규화   │
└────┴─────────────────────────────┴─────────────────────────────┴────────────────────────────────┘
```

---

## 3. WP-00: 18개 엔지니어링 도메인 전수 자산 목록 (Asset Inventory)

저장소 내 존재하는 모든 실물/설계/소프트웨어 엔지니어링 자산을 18개 도메인에 1:1 매핑하였습니다.

| 도메인 ID | 영역 명칭 | 파일 상대 경로 | 포맷 / 크기 | 형상 버전 / 상태 | 신뢰도 / 판정 | 핵심 내용 및 기능 |
|:---:|---|---|---|---|:---:|---|
| **E01** | 요구사항 | `docs/MAJUNG_PRODUCT_REQUIREMENTS_DRAFT_2026-10-12.md` | MD (9.1 KB) | 2026-10-12 Draft | **VERY HIGH** | INT(5), FUN(5), OUT(7), SAF(6), REG(4), CHG(3) 28개 구조화 ID |
| **E01** | 요구사항 | `docs/development/MASTER_DEVELOPMENT_PLAN.md` | MD (21.5 KB) | Commit `c63e60a` | HIGH | 6주 마스터 일정 및 14개 마일스톤 |
| **E01** | 요구사항 | `docs/development/MVP_RELEASE_CHECKLIST.md` | MD (4.8 KB) | v0.1.0-mvp | HIGH | 9대 릴리즈 게이트 및 체크포인트 |
| **E02** | 시스템 아키텍처 | `docs/MAJN_DECISION_AND_ENGINEERING_LOG.md` | MD (42.8 KB) | 승인본 (2026-10-31) | **VERY HIGH** | 26개 하드웨어 의사결정 및 ISSUE-01~07 |
| **E02** | 시스템 아키텍처 | `docs/MAJN_REV_C_COMPREHENSIVE_DEVELOPMENT_PLAN.md` | MD (13.2 KB) | 승인본 (v2.0) | HIGH | Rev-C 전기·기구 통합 설계서 |
| **E03** | 형상·BOM 제어 | `docs/engineering/ENGINEERING_DATA_SCHEMA.md` | MD (5.8 KB) | Draft (docs 브랜치) | **VERY HIGH** | 명명규칙 및 메타데이터 스키마 SSOT |
| **E03** | 형상·BOM 제어 | `docs/engineering/ENGINEERING_DOMAIN_REGISTER.md` | MD (6.6 KB) | Draft (docs 브랜치) | **VERY HIGH** | 18개 도메인 소유권 및 책임 매트릭스 |
| **E03** | 형상·BOM 제어 | `release/v0.1.0-mvp/SHA256SUMS` | TXT (79 B) | v0.1.0-mvp | HIGH | 공식 바이너리 무결성 해시 |
| **E04** | 3D CAD & 모델링 | `majn_housing/majung_bassinet_4.5T_rev2_master.dxf` | DXF R2010 (31.8 KB) | Rev 2 Master | **VERY HIGH** | 450×250×22.5mm, 10볼트, 4구 직사각 각인 (해광레이저 발주본) |
| **E04** | 3D CAD & 모델링 | `majn_housing/majung_silicone_gasket_rev2.dxf` | DXF R2010 (17.6 KB) | Rev 2 Gasket | **VERY HIGH** | 1.2T 식품등급 실리콘 가스켓 (10개 ⌀2.8mm 타공) |
| **E04** | 3D CAD & 모델링 | `majn_housing/rev2_params.py` | PY (3.2 KB) | Rev 2 SSOT | **VERY HIGH** | 기구 치수 및 공차 단일 진실 공급원 (SSOT) |
| **E04** | 3D CAD & 모델링 | `majn_housing/build_rev2_dxf.py` | PY (7.2 KB) | Generator | VERY HIGH | ezdxf 기반 마스터 및 가스켓 DXF 자동 생성 파이프라인 |
| **E04** | 3D CAD & 모델링 | `majn_housing/REV2_CAD_DECISION_RECORD.md` | MD (4.7 KB) | Accepted ADR | VERY HIGH | 10볼트 균일 피치(110~150mm), 12mm 림+러그 가스켓 ADR |
| **E04** | 3D CAD & 모델링 | `bassinet_simulator/cad_assembler.js` | JS (17.0 KB) | 720×390 Variant | HIGH | 조리원용 720×390×45mm 3D 기구 형상 생성기 |
| **E05** | 3D 가시화 | `majn_housing/view_3d_rev2_assembly.html` | HTML (27.8 KB) | Rev 2 Assembly | **VERY HIGH** | Three.js 오차 0.00mm 동기화 정밀 360° 목재 어셈블리 뷰어 |
| **E05** | 3D 가시화 | `bassinet_simulator/cad_viewer.html` | HTML (11.4 KB) | 720×390 Variant | HIGH | 조리원용 3D 뷰어 (상하판 투과, 와이어프레임) |
| **E06** | 전장·케이블링 | `docs/MAJN_DECISION_AND_ENGINEERING_LOG.md#L90` | MD | 확정 (결정 09) | VERY HIGH | 24AWG 실리콘 연선 25cm, JST 2P 압착, 직렬 16Ω |
| **E07** | 전자·PCB 회로 | `인증준비/pcb/Rev_C_mfg/MAJN_Rev_C.epro2` | EasyEDA (730 KB) | 4-layer Rev_C | HIGH | 차기 양산용 4층 기판 프로젝트 (우각 헤더, ⌀2.7mm 마운팅 홀) |
| **E07** | 전자·PCB 회로 | `인증준비/pcb/Rev_C_mfg/BOM_MAJN_Rev_C.csv` | CSV (1.1 KB) | 56 components | HIGH | 53 SMD + 3 직각 THT 부품 구성표 |
| **E07** | 전자·PCB 회로 | `인증준비/pcb/Rev_C_mfg/CPL_MAJN_Rev_C.csv` | CSV (1.6 KB) | 56 components | HIGH | SMT 픽앤플레이스 좌표 파일 |
| **E07** | 전자·PCB 회로 | `인증준비/pcb/Rev_C_mfg/Gerber_MAJN_Rev_C.zip` | ZIP (625 KB) | 20 Gerber files | MEDIUM | 제조용 정규화 거버 (U1 배선 간섭 검토로 발주 HOLD) |
| **E07** | 전자·PCB 회로 | `hardware_review/PCB_0005_original/Original.epro2` | EasyEDA (321 KB) | 2-layer #0005 | HIGH | 실물 보드(#0005) 1:1 대응 2층 기판 원본 |
| **E07** | 전자·PCB 회로 | `hardware_review/PCB_Rev_C/Rev_C.epro2` | EasyEDA (310 KB) | 70-part concept | MEDIUM | 외장 센서 3종 확장 개념 논리 회로도 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/platformio.ini` | INI (1.2 KB) | 4 envs | **VERY HIGH** | 빌드 환경 SSOT (Release, Debug, OTA, Native) |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/partitions_8mb_ota.csv` | CSV (305 B) | 8MB OTA Table | **VERY HIGH** | 3.19MB 대칭 OTA 파티션 테이블 SSOT |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/main.cpp` | C++ (14.8 KB) | v0.1.0-mvp | VERY HIGH | FreeRTOS 멀티태스킹 메인 루프 (100ms 가드) |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/system_controller.cpp` | C++ (17.6 KB) | State Machine | VERY HIGH | 시스템 상태 전이 제어 및 ESTOP 처리기 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/tas5805m.cpp` | C++ (8.2 KB) | 12V BTL Driver | VERY HIGH | 12V BTL I2C(0x2C) 및 I2S 48kHz DMA 드라이버 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/safety_manager.cpp` | C++ (2.3 KB) | Safety Guard | VERY HIGH | 30분 타이머, 135°C 과열 디레이팅 감시 루프 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/wifi_manager.cpp` | C++ (17.4 KB) | SoftAP / OTA | VERY HIGH | SoftAP 웹서버 및 HTTP `/update` 무선 배포 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/mobile_web_ui.h` | C++ Header (15.8 KB) | Web Controller | VERY HIGH | 스마트폰 브라우저 탑재용 경량 SPA 웹 UI |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/ota_ble_service.cpp` | C++ (9.0 KB) | BLE GATT OTA | VERY HIGH | BLE 무선 플래시 핸들러 (원자적 OTA 락) |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/ble_manager.cpp` | C++ (11.5 KB) | BLE Server | VERY HIGH | 커스텀 GATT 서비스 및 제어 프로토콜 |
| **E08** | 임베디드 펌웨어 | `인증준비/firmware/src/vibration_controller.cpp` | C++ (6.4 KB) | SVS Synthesis | VERY HIGH | 확률적 공명 진동(SVS) 파형 합성 엔진 |
| **E08** | 임베디드 펌웨어 | `release/v0.1.0-mvp/firmware.bin` | BIN (1.91 MB) | Release Binary | **VERY HIGH** | SHA-256 검증 완료 공식 릴리즈 바이너리 |
| **E09** | 도면·설계 검증 | `majn_housing/verify_rev2.py` | PY (6.3 KB) | DRC Verifier | **VERY HIGH** | ezdxf 기하학적 살 두께(4.9mm), 10홀 좌표 검증 (7/7 PASS) |
| **E09** | 도면·설계 검증 | `tools/verify_hardware_review.py` | PY (33.6 KB) | v2.4 Electrical | **VERY HIGH** | 넷리스트 논리 규칙 및 부스트/앰프 정합성 검증 (21/21 PASS) |
| **E09** | 도면·설계 검증 | `tools/verify_mfg_package.py` | PY (12.5 KB) | Rev_C.MFG DRC | **VERY HIGH** | BOM/CPL/Gerber FPT 3-Way 일치 및 Z-스택업 검증 (5/5 PASS) |
| **E10** | 조립·서비스성 | `majn_housing/REV2_CAD_DECISION_RECORD.md` | MD (4.7 KB) | Accepted ADR | HIGH | 10볼트 체결 및 실리콘 가스켓 장탈착성 가이드 |
| **E11** | CAE·물리 시뮬레이션 | `bassinet_simulator/c3d10_solver.js` | JS (6.1 KB) | C3D10 FEA | **VERY HIGH** | 2.5D Mindlin 쉘 및 C3D10 10절점 사면체 FEM 솔버 |
| **E11** | CAE·물리 시뮬레이션 | `bassinet_simulator/fem_wasm_solver.js` | JS (2.6 KB) | CalculiX Deck | **VERY HIGH** | 자작나무 직교이방성 물성 기반 Abaqus `.INP` 생성기 |
| **E11** | CAE·물리 시뮬레이션 | `bassinet_simulator/fem_simulator.html` | HTML (34.7 KB) | 3D WebGL FEA | **VERY HIGH** | 웹 브라우저 기반 3D 변위/응력 실시간 가시화 엔진 |
| **E11** | CAE·물리 시뮬레이션 | `bassinet_simulator/MAJN_3D_CAE_Simulator_Summary.md` | MD (5.9 KB) | 총정리 보고서 | VERY HIGH | CAE 시뮬레이터 아키텍처 및 검증 요약서 |
| **E11** | CAE·물리 시뮬레이션 | `majn_housing/익사이터_위치선정_역학검토_총정리.md` | MD (9.4 KB) | Mechanical Study | HIGH | 25개 고유진동모드 해석 및 Huber 판방정식 유도 |
| **E12** | 제품 안전 & FMEA | `docs/validation/SAFETY_RISK_REGISTER.md` | MD (4.2 KB) | Risk Register | VERY HIGH | 12대 위험 시나리오 FMEA 및 방어 대책 |
| **E12** | 제품 안전 & FMEA | `docs/FAULT_MATRIX.md` | MD (3.1 KB) | Shutdown Matrix | **VERY HIGH** | BOOST_EN, AMP_PDN, 1.5g ISR 하드웨어 차단 계통도 |
| **E12** | 제품 안전 & FMEA | `docs/validation/SAFETY_TEST_PROTOCOL.md` | MD (4.9 KB) | Test Protocol | HIGH | 고장 주입(Fault Injection) 시험 절차서 |
| **E13** | 검증 & 시험 계측 | `docs/validation/VIBRATION_TEST_PROTOCOL.md` | MD (5.1 KB) | P1~P5 Protocol | **VERY HIGH** | 매트리스 상부 5개소(P1~P5) 진동 계측 절대좌표 |
| **E13** | 검증 & 시험 계측 | `docs/MAJN_PCB_0005_EXCITER_SUCCESS_MEASUREMENT_RECORD.md` | MD (4.8 KB) | Physical Ground | **VERY HIGH** | 12.00V 승압, I2C 0x2C, 50Hz 진동 체감 실측 기록 |
| **E13** | 검증 & 시험 계측 | `hardware_review/Measurements/Voltage.csv` | CSV (495 B) | DMM Data | VERY HIGH | 전원 레일(5.02V, 3.20V, 12.00V) 실측 전압 로그 |
| **E13** | 검증 & 시험 계측 | `hardware_review/Measurements/Resistance.csv` | CSV (1.2 KB) | DCR Data | VERY HIGH | 익사이터 결선 저항(단품 10.8Ω, 2직렬 21.6Ω) 실측 로그 |
| **E13** | 검증 & 시험 계측 | `tools/test_command_parser.py` | PY (28.8 KB) | 92 Unit Tests | **VERY HIGH** | 펌웨어 커맨드 파서 및 상태머신 100% PASS 검증기 |
| **E14** | 사용성 & 인간공학 | `인증준비/user_manual_draft.md` | MD (4.7 KB) | User Manual | HIGH | 양육자 사용 시나리오 및 안전 주의사항 |
| **E15** | 연구·임상 협력 | `docs/MAJUNG_E001A_SMITH_2015_PRIMARY_EXTRACTION_2026-10-08.md` | MD (12.0 KB) | Clinical RCT | VERY HIGH | Smith 2015 영아 진동수면(SVS) 임상 논문 분석 |
| **E15** | 연구·임상 협력 | `docs/MAJUNG_E001D_PRAPELA_FDA_PRIMARY_EXTRACTION_2026-10-08.md` | MD (14.0 KB) | FDA De Novo | VERY HIGH | FDA Breakthrough 지정 Prapela SVS 규제 선례 |
| **E16** | 규제 & 전자파 인증 | `docs/MAJN_PCB_0005_CIRCUIT_CERTIFICATION_REVIEW.md` | MD (8.5 KB) | KC Compliance | HIGH | 어린이제품 공통안전기준 및 유해원소 기준 |
| **E16** | 규제 & 전자파 인증 | `docs/MAJN_PCB_0005_EMC_FEASIBILITY_AND_STRATEGY.md` | MD (8.2 KB) | EMC Strategy | HIGH | Class-D 384kHz 스위칭 노이즈 방사 차폐 대책 |
| **E17** | 생산 공학 & 품질 | `majn_housing/MASS_PRODUCTION_ROADMAP.md` | MD (6.1 KB) | Mfg Roadmap | HIGH | 금형 사출, 가공 공차, 수입 검사 기준 |
| **E18** | 수명주기 & 사후관리 | `majn_housing/REV2_CAD_DECISION_RECORD.md` | MD | Refurbish Spec | HIGH | 렌탈 회수 시 가스켓 교체 및 목재 재생 프로세스 |

---

## 4. WP-01: 형상·치수·버전·인터페이스 다차원 불일치 정밀 감사

### 4.1 기구·CAD·DXF 10개 파일 전수 파싱 및 네스팅 검증

저장소 내 10개 DXF 파일을 `ezdxf`로 전수 파싱하여 실물 가공 네스팅 규격과 도면 주석 영역을 분리 계측하였습니다:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         [ 저장소 내 10대 DXF 파일 전수 정밀 파싱 감사표 ]                       │
├────────────────────────────────────────┬────────┬───────┬──────┬─────────┬───────────────────────┤
│ DXF 파일 경로                          │ 버전   │ 요소수│ 홀 수│ 홀 반경 │ 핵심 사양 및 상태 판정│
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1024 │ 116개 │ 55개 │ 1.6, 2.1│ ★최신 정품 SSOT      │
│ majung_bassinet_4.5T_rev2_master.dxf   │ (R2010)│       │      │ 3.25,3.5│ (10볼트, ⌀7그로밋,   │
│                                        │        │       │      │ 7.0 mm  │  직사각 익사이터 INFO)│
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1024 │ 13개  │ 10개 │ 1.4 mm  │ 1.2T 실리콘 가스켓    │
│ majung_silicone_gasket_rev2.dxf        │ (R2010)│       │      │         │ (10개소 ⌀2.8 타공)    │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 125개 │ 23개 │ 1.6,2.75│ 구형 6볼트 + ⌀37 원형 │
│ majung_bassinet_order_4.5T_haptic.dxf  │ (R2004)│       │      │ 7.0,18.5│ 익사이터 + ⌀5.5 배선홀│
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 74개  │ 23개 │ 1.6,2.75│ 상동 (메이커스라운지  │
│ 견적요청_4.5T_메이커스라운지_haptic.dxf│ (R2004)│       │      │ 7.0,18.5│ 발주용 견적서 사본)   │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 85개  │ 7개  │ 1.6 mm  │ 구형 4.5T 기본 도면   │
│ majung_bassinet_order_4.5T.dxf         │ (R2004)│       │      │ 2.75 mm │ (6나사, ⌀5.5 배선홀)  │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 85개  │ 7개  │ 1.6 mm  │ 구형 4.0T 기본 도면   │
│ majung_bassinet_order.dxf              │ (R2004)│       │      │ 2.75 mm │ (4.0T 합판 기준)      │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1024 │ 85개  │ 7개  │ 1.6 mm  │ 구형 4.0T 보존본      │
│ 마중.dxf                               │ (R2010)│       │      │ 2.75 mm │ (아이베란다 가공용)   │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 34개  │ 7개  │ 1.6 mm  │ 메이커스라운지 제출본 │
│ 견적요청_4.5T_메이커스라운지.dxf       │ (R2004)│       │      │ 2.75 mm │ (단순 외곽선 추출)    │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ majn_housing/                          │ AC1018 │ 34개  │ 7개  │ 1.6 mm  │ 레이저 가공용 추출본  │
│ 견적요청_메이커스라운지_레이저용.dxf   │ (R2004)│       │      │ 2.75 mm │ (치수선 제거본)       │
├────────────────────────────────────────┼────────┼───────┼──────┼─────────┼───────────────────────┤
│ bassinet_simulator/fabrication/        │ AC1024 │ 67개  │ 29개 │ 1.0, 1.6│ NUCU Pad v3 CNC 도면  │
│ nucu_pad_v3_cnc.dxf                    │ (R2010)│       │      │ 2.75 mm │ (삼각 코너블록 적용)  │
└────────────────────────────────────────┴────────┴───────┴──────┴─────────┴───────────────────────┘
```

#### 기구 인터페이스 미결 결함: 하판 내 PCB 고정홀 누락
- **현상**: 마스터 DXF 하판에는 외곽 10개 볼트홀(`HOLE_BOLT_THROUGH = 3.2mm`)만 가공되어 있습니다.
- **영향**: 기판 크기 `81.3 × 62.2 mm` (마운팅 홀 간격 68.58 × 54.86 mm)의 PCB를 고정할 나사홀이 전혀 없어 시제품 조립 시 기판 유동 또는 양면테이프 고정이라는 임시방편에 의존해야 합니다.
- **해결 방안**: 하판 중앙 비간섭 영역에 M2.5/M3 스탠드오프용 ⌀2.7~3.0mm 카운터싱크 홀 4개소를 반영하는 ECO가 필수적입니다.

---

### 4.2 전자 회로·PCB 3대 세대 비교 및 발주 보류(HOLD) 근거

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         [ PCB 3대 세대 하드웨어 스펙 정밀 비교표 ]                               │
├──────────────────┬──────────────────────┬──────────────────────┬─────────────────────────────────┤
│ 비교 항목        │ ① PCB #0005 실물 보드│ ② Rev-C MFG 제조 패키지│ ③ Rev-C 확장 개념 회로         │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 저장소 경로      │ hardware_review/     │ 인증준비/pcb/        │ hardware_review/                │
│                  │ PCB_0005_original/   │ Rev_C_mfg/           │ PCB_Rev_C/                      │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 레이어 스택업    │ 2-Layer (Top, Bot)   │ 4-Layer (Top, GND,   │ 4-Layer (Top, GND, Sig, Bot)    │
│                  │                      │ Sig, Bot)            │                                 │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ BOM 부품 수      │ 37개 (유령부품 제거) │ 56개 (53 SMD+3 우각) │ 70개 (센서 풀업 및 0Ω 링크 포함)│
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 3.3V LDO         │ SGM2036-3.3 (300mA)  │ AP2112K-3.3 (600mA)  │ TLV75733 (1.0A 권장)            │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 12V 승압 저항    │ R1=16k, R2=150k      │ R1=143k, R2=16k      │ R1=150k, R2=16k                 │
│                  │ (수작업 스왑 12.00V) │ (12.17V 승압)        │ (12.45V 승압)                   │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ RF 안테나        │ ESP32-WROOM-32E      │ ESP32-WROOM-32UE     │ ESP32-WROOM-32UE-N8             │
│                  │ (PCB 패턴 온보드)    │ (외장 IPEX 커넥터)   │ (외장 IPEX 커넥터)              │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 헤더 커넥터      │ 수직 2.54mm 헤더     │ 직각 90° 우각 헤더   │ 직각 90° 우각 헤더              │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 외장 센서 포트   │ 없음                 │ 없음                 │ J_BCG(4P), J_RADAR(4P), ENV_MIC │
├──────────────────┼──────────────────────┼──────────────────────┼─────────────────────────────────┤
│ 현 상태 판정     │ ★실물 검증 완료 SSOT│ ★거버 동결 및 HOLD  │ 검토용 논리 회로도              │
└──────────────────┴──────────────────────┴──────────────────────┴─────────────────────────────────┘
```

#### `U1` (ESP32-WROOM-32UE) 14개소 쇼트 위험 및 발주 보류(HOLD) 근거:
EasyEDA Pro에서 배선을 재배치하지 않고 풋프린트만 교체할 경우:
1. Pin 3~14 패드가 안쪽으로 0.50mm 연장되어 상부 `VCC_3V3` 수평 버스 트레이스를 덮침 (-5.00 mil 쇼트, 12개소)
2. Pin 39 (EP #4)가 사선 `SPI_CS` 배선을 침범 (-4.96 mil GND–SPI_CS 쇼트)
3. Pin 15~24 패드가 수직 `ESP_IO0` 배선을 침범 (-5.00 mil 쇼트)
4. Pin 28 패드가 내부 GND 비아와 접촉 (-1.15 mil 쇼트)
$\rightarrow$ **경로 2-A(기존 검증된 동박 유지 및 CPL 정규화)** 또는 **경로 2-B(EasyEDA 4개 네트 재라우팅)**에 대한 인간 엔지니어의 공식 서명이 완료될 때까지 **제조 발주 보류(HOLD)**를 유지합니다.

---

### 4.3 펌웨어·통신·안전 차단 계통 정밀 감사

1. **무선 전용 불변 원칙 (Physical Button-less Constraint)**:
   - PCB #0005 보드에는 물리 버튼(BOOT/EN)이 전무하며, CP2102 헤더에 DTR/RTS 자동 부트로더 리셋 라인이 결선되어 있지 않습니다.
   - 따라서 유선 `esptool` 업로드는 물리적으로 불가하며, **오직 BLE GATT OTA(`tools/run_ble_ota.py`) 또는 Wi-Fi HTTP `/update`(`tools/run_wifi_ota.py`)**로만 펌웨어 배포가 가능합니다.
2. **상호 배제 OTA 잠금 (Cross-Transport Mutex Lock)**:
   - `wifi_manager.cpp`와 `ota_ble_service.cpp`가 원자적 플래그(`gOtaRunning`)를 공유하여 Wi-Fi와 BLE 간 동시 플래시 충돌을 원천 차단합니다.
   - 첫 1바이트 매직 바이트(`0xE9`) 및 파티션 최대 크기(3.19MB, `0x330000`) 검증을 통과해야 플래시 쓰기가 인가됩니다.
3. **다중 안전 차단 시퀀스 (`docs/FAULT_MATRIX.md`)**:
   - 고장(과열 135°C, 통신 단절 5초, 충격 1.5g, 비상정지 ESTOP) 감지 시:
     $$\text{BOOST\_EN} \rightarrow \text{LOW (12V 승압 즉시 차단)}, \quad \text{AMP\_PDN} \rightarrow \text{LOW (TAS5805M 하드웨어 Mute)}$$
   - 30분 연속 구동 소프트웨어 강제 타임아웃 및 135°C 도달 시 50% 진폭 디레이팅 루프가 상시 가동됩니다.

---

## 5. E06: 케이블 하네스 및 전기·기구 인터페이스 (ICD Topology)

13.5mm 밀폐 캐비티 내부의 하네스 결선 토폴로지 및 스택업 검증 결과입니다:

```
                  ┌──────────────────────────────────────────────┐
                  │          4.5T 자작합판 상판 (진동판)          │
                  │   [EXC-1]       [EXC-2]      [FPC 안테나]    │
                  │  (120, 60)     (330, 60)      (상판 내측)     │
                  └──────┬─────────────┬──────────────┬──────────┘
                         │             │              │
                   24AWG 실리콘  24AWG 실리콘     IPEX 마이크로동축
                    (25cm 직렬)   (25cm 직렬)    (10~15cm, RTV몰딩)
                         │             │              │
 ┌───────────────────────┼─────────────┼──────────────┼──────────┐
 │ 13.5mm 중간 캐비티    ▼             ▼              ▼          │
 │                 ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
 │                 │  Port J1 │  │  Port J2 │  │ U1 IPEX 포트 │  │
 │                 │(C49423315│  │(C49423315│  │  (ESP32-32UE)│  │
 │                 └──────────┴──┴──────────┴──┴──────────────┘  │
 │                                                               │
 │   USB Type-C 5V IN ──► PPTC F1(3.0A) ──► TVS D1(SMAJ5.0A)    │
 │       ▲                                                       │
 │       │ USB-C 전원 케이블 (외경 ⌀3.5~4.5mm)                   │
 │   ┌───┴───────────────────────────────────────────────────┐   │
 │   │ 측판 단변 관통홀: ⌀7.0mm 방수 실리콘 그로밋           │   │
 │   │ 위치: 단변 레일 X=30.0mm (조립 좌표계 Y≈50.0mm)       │   │
 └───┴───────────────────────────────────────────────────────┴───┘
```

1. **익사이터 하네스 (Harness-EXC-01 / 02)**:
   - 부품: TEAX14C02-8 (또는 HDHX14C02-8) 4개.
   - 결선: J1 채널 2개 직렬, J2 채널 2개 직렬.
   - 선재: 24AWG 내열·내진동 실리콘 연선, 길이 **25cm ± 2cm**.
   - 간극 검증: 익사이터 높이 9.85mm + 테이프 0.26mm = 10.11mm. 캐비티 13.5mm 대비 **+3.39mm 정적 공기 틈새 확보**.
2. **주전원 인입 하네스 (Harness-PWR-01)**:
   - 관통홀 위치: 단변 측판 레일 끝에서 X=30.0mm (Z=6.75mm 중앙).
   - 잔여 살 두께: 외경 ⌀7.0mm 관통홀 기준 상하 잔여 살 두께 3.25mm 확보 (파손 방지 기준 $\ge 3.0\text{ mm}$ 충족).
   - 방수 마감: 식품등급 실리콘 케이블 그로밋 압착.
3. **RF 안테나 하네스 (Harness-RF-01)**:
   - 2.4GHz 3dBi 플렉시블 FPC 안테나 (10~15cm 마이크로 동축 케이블). 상판 내측면에 점착 고정 후 IPEX MHF1 단자에 체결.
   - 진동 탈락 방지를 위해 **RTV 비도전성 전자용 실리콘 본드 필수 도포**.

---

## 6. 기존 도구 및 자산 재사용·통합 계획 (Tool Reuse Architecture)

1. **Three.js 3D Viewer 자산 확장**:
   - `majn_housing/view_3d_rev2_assembly.html`을 E05의 코어로 지정.
   - 현재 누락된 PCB 메쉬, 안테나, 케이블 배선 노드를 추가하여 완전한 디지털 트윈 구축.
2. **CAD/DXF 생성 파이프라인 통합**:
   - `build_rev2_dxf.py` 및 `rev2_params.py`를 형상 생성 SSOT로 유지.
   - `verify_rev2.py`를 Git 커밋 전 자동 게이트로 통합.
3. **Web CAE 및 CalculiX 브릿지 연동**:
   - `bassinet_simulator/c3d10_solver.js`의 쉘/솔리드 수식 및 `fem_wasm_solver.js`의 `.INP` 생성기를 E11의 자산으로 정식 편입.
   - Phase 3에서 데스크톱 CalculiX CLI(`ccx`)와 연동하는 파이썬 브릿지 파이프라인 구축.
4. **EasyEDA Pro MCP 브릿지 및 PlatformIO 자동화**:
   - EasyEDA WebSocket 브릿지(포트 49620) 및 `tools/verify_mfg_package.py`를 통해 거버/BOM/CPL 1:1:1 무결성 검증.
   - PlatformIO 4대 환경 빌드 및 `tools/test_command_parser.py` 92개 회귀 테스트 통과를 PR 병합 필수 조건으로 고정.

---

## 7. 제안 디렉터리 구조 및 Phase 1 실행 계획

### 7.1 권장 디렉터리 구조 (Target Directory Structure)

```text
/Users/youngseok/Desktop/majn/
├── docs/engineering/
│   ├── ENGINEERING_MASTER_PLAN.md             # 마스터 플랜
│   ├── ENGINEERING_DOMAIN_REGISTER.md         # 18개 도메인 레지스터
│   ├── ENGINEERING_DATA_SCHEMA.md             # 데이터 스키마
│   ├── ENGINEERING_ROADMAP.md                 # 로드맵
│   ├── WP00_WP01_INTEGRATED_AUDIT_REPORT.md   # 본 종합 기술 보고서 (SSOT)
│   └── baseline/
│       ├── asset_inventory.csv                # 18개 도메인 전수 자산 레지스터
│       ├── discrepancy_register.csv           # 12대 불일치 추적 레지스터
│       └── interface_registry.csv             # 기구·전장·케이블 인터페이스 레지스터
│
├── core/                                      # [Phase 1: 도메인 거버넌스]
│   ├── requirements/
│   │   └── requirements_register.csv          # E01 요구사항 (28개 ID)
│   ├── configuration/
│   │   ├── part_registry.csv                  # E03 부품 대장
│   │   └── master_bom.csv                     # E03 E-BOM / M-BOM 분리표
│   ├── interfaces/
│   │   └── interface_registry.csv             # IF-MEC-ELEC-001 등 ICD
│   └── changes/
│       └── eco_register.csv                   # ECO 설계변경 이력
│
├── cad/                                       # [E04, E05: 기구 및 형상]
│   ├── source/                                # rev2_params.py, DXF 원본
│   └── viewers/                               # view_3d_rev2_assembly.html
│
├── electrical/                                # [E06, E07: 전장 및 하네스]
│   ├── pcb/                                   # Rev_C_mfg 제조 패키지
│   └── harness/                               # CABLE-EXC-001 등 결선도
│
├── firmware/                                  # [E08: 임베디드 제어]
│   ├── src/                                   # main.cpp, tas5805m 등
│   └── release/                               # v0.1.0-mvp 바이너리
│
├── cae/                                       # [E11: 물리 해석 및 시뮬레이션]
│   ├── solvers/                               # c3d10_solver.js, fem_wasm
│   └── reports/                               # 모달 해석 및 Huber 보고서
│
└── verification/                              # [E09, E12, E13: 시험 및 품질 게이트]
    ├── automated_gates/                       # verify_rev2, verify_hardware 등
    └── protocols/                             # VIBRATION_TEST_PROTOCOL.md
```

---

## 8. 사람의 엔지니어링 판단 및 승인 요청 사항 (D-1 ~ D-9)

안전 및 하드웨어 제조 비용이 수반되는 아래 9가지 의사결정 사항에 대해 담당 엔지니어(사람)의 공식 검토와 승인을 요청합니다:

| 번호 | 결정 항목 | 선택지 / 의사결정 경로 | 영향 도메인 | 권장안 (AI 조사 제안) |
|:---:|---|---|---|---|
| **D-1** | PCB Rev-C `U1` 쇼트 해결 경로 선택 | **경로 2-A**: 검증된 기존 동박 유지 + CPL 정규화<br>**경로 2-B**: EasyEDA에서 배선 4종 재라우팅 | E07 | **경로 2-A 우선 검토** (물리 납땜 핀이 100% 동일하므로 기판 재제작 리스크 최소화) |
| **D-2** | PCB Rev-C 4층 보드 제조 발주 승인 | 발주 진행 vs #0005 실측 완료 시까지 HOLD | E07, E17 | **HOLD 유지** (#0005 실측 데이터셋 완성 및 D-1 승인 후 발주) |
| **D-3** | 3.3V LDO 최종 부품 승인 | AP2112K (600mA) vs TLV75733 (1.0A) | E07, E12 | **TLV75733PDBVR (1A)** 승인 (Wi-Fi 19dBm 송신 피크 시 전압 강하 방지) |
| **D-4** | 하우징 Rev 2 도면 공식 SSOT 채택 | 10볼트 체결 Master DXF 승인 | E04, E10 | **`majung_bassinet_4.5T_rev2_master.dxf` 승인** |
| **D-5** | 하판 내 PCB 장착홀 추가 (ECO) | 하판에 M3 스탠드오프홀 4개 타공 vs 3D 브래킷 사용 | E04, E06 | **하판 스탠드오프홀 4개소 타공 반영 승인** (조립 편의성 및 신뢰성) |
| **D-6** | 제품 라인업 분리 승인 | 450×250 단일화 vs 가정용(450) & 조리원용(720) 병행 | E01, E04 | **2대 제품군 분리 관리 승인** (`CFG-HOME-450`, `CFG-HOSPITAL-720`) |
| **D-7** | 익사이터 양산 부품 및 결선 승인 | 8Ω TEAX14C02 직렬(16Ω) vs 12Ω 고저항 샘플 유지 | E06, E07 | **8Ω TEAX14C02 직렬(16Ω) 승인** (단, TAS5805M 출력 전력 상승에 따른 발열 감시 필수) |
| **D-8** | 외장 안테나 KC 인증 승계 질의 | 등록 안테나 형식(이득 $\le 2.33\text{dBi}$) 적용 확인 | E16 | 공인 시험기관(KTL/DT&C 등) 공식 기술 질의 진행 |
| **D-9** | 매트리스 상부 가속도 판정 기준선 | P1(중앙) RMS $0.05 \sim 0.25\text{ m/s}^2$ 기준선 승인 | E01, E13 | `VIBRATION_TEST_PROTOCOL.md` 기준선 공식 승인 |

---

## 9. Gate 0 (G0) 기준선 완료 체크리스트 및 결론

- [x] 저장소 전체 18개 도메인 자산의 위치, 포맷, 상태가 누락 없이 목록화되었는가? (WP-00 완료)
- [x] 선행 보고서의 12대 오류(그로밋 위치, CAE 맹점, 임피던스 모순 등)가 정밀 교정되었는가? (완료)
- [x] 기구 치수 및 형상 불일치가 식별되고 SSOT가 정의되었는가? (Rev 2 Master 확정)
- [x] 실물 보드(#0005)와 차기 회로(Rev-C) 간 차이점이 완전히 분석되었는가? (3자 대조 완료)
- [x] 전기·기구 하네스 인터페이스 및 캐비티 간섭이 검증되었는가? (+3.39mm 공기 유격 확보)
- [x] AI가 임의로 코드를 수정하거나 형상을 덮어쓰지 않았는가? (100% 비파괴 조사 원칙 준수)
- [ ] D-1 ~ D-9에 대한 사람 엔지니어의 공식 승인이 완료되었는가? (승인 대기)
