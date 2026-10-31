# 마중 스마트 배시넷 하드웨어 및 회로 검토 패키지 가이드

본 디렉토리(`hardware_review/`)는 EasyEDA Pro 네이티브 바이너리(`.epro2`)의 분석 한계를 극복하고, AI 에이전트 및 하드웨어 엔지니어가 회로 결선, 넷리스트, BOM, 실측값, 인증 규격을 전수 교차 검증할 수 있도록 표준화된 형태로 구성된 마스터 패키지입니다.

---

## 1. 디렉토리 구조 및 파일 역할

```
hardware_review/
├── README.md                           # 본 가이드 문서 (SSOT 정합성 검증 결과 수록)
│                                       # ➔ 상세 마스터 플랜: docs/MAJN_REV_C_COMPREHENSIVE_DEVELOPMENT_PLAN.md
├── PCB_0005_original/                  # [기준 원본] 실측 검증 완료 골든 베이스라인
│   ├── Original.epro2                 # EasyEDA Pro 원본 프로젝트 아카이브
│   ├── BOM.csv                        # 37개 정본 부품 명세서 (LCSC ID, 패키지, 제조사, 설계결함 주석)
│   ├── Netlist.net                    # 42개 넷 결선 전수 핀맵 정의서
│   ├── Netlist.json                   # 기계 판독용 넷리스트 JSON
│   └── Gerber_Output.zip              # PCB #0005 제조용 거버 파일
│
├── PCB_Rev_C/                          # [개선 사본] 전파인증(EMC) 및 3대 센서 확장 리비전
│   ├── Rev_C.epro2                    # Rev-C 프로젝트 바이너리 (실체화 완료, Distinct SHA)
│   ├── BOM.csv                        # 54개 부품 전수 명세서 (정상화 D3/L1 + 3대 센서 + 0Ω + 스너버 + PPTC)
│   ├── Netlist.net                    # 58개 넷 결선도 (0Ω 양단 분리 및 스너버 직렬 결선 완비)
│   └── Gerber_RevC_Base.zip           # 4층 기판 베이스 거버 아카이브
│
├── Measurements/                       # [실측 전수 데이터] PCB #0005 실기 계측 Ground Truth
│   ├── Voltage.csv                    # 전원 레일 실측 (VBUS 5.02V, VCC 3.20V, PVDD 12.00V)
│   ├── Resistance.csv                 # 익사이터 부하 DCR(21.6Ω)/공칭 임피던스(24Ω), 실장 저항 실측
│   └── Test_Results.md                # 2026-10-24 익사이터 물리 진동 확인 및 SSOT 불일치 분석 보고서
│
└── Datasheets/                         # 주요 핵심 IC 데이터시트 보관소
    └── (TAS5805M, MP3426, ESP32-WROOM-32E, LSM6DSOX)
```

---

## 2. SSOT(단일 진실 원천) 정밀 분석 및 불일치 해결 내역

원본 `.epro2` 내부 소스(`epru`)를 JSON 단위로 전수 역공학 분석한 결과, 기존 문서와 실제 설계 파일 간의 다음과 같은 불일치가 확인되어 바로잡았습니다:

| 부품 | 원본 `.epro2` 실제 기록 | 실제 회로상 기능 | 불일치 원인 및 정정 조치 |
| :--- | :--- | :--- | :--- |
| **D3** | `RN731JTTD3901B25` (3.9kΩ 저항) | MP3426 SW ↔ PVDD 쇼트키 다이오드 | **원본 설계 결함**: 설계자가 다이오드 자리에 3.9kΩ 저항 심볼 배치. 원본 BOM에는 사실대로 기록하고, **Rev-C에서 쇼트키 다이오드 SS34 (40V 3A, LCSC: C14999)로 정상화** |
| **L1** | `WR04X5601FTL` (5.6kΩ 0402 저항) | MP3426 SW ↔ VBUS 파워 인덕터 | **원본 설계 결함**: 설계자가 인덕터 자리에 5.6kΩ 저항 심볼 배치. 원본 BOM에는 사실대로 기록하고, **Rev-C에서 차폐형 파워 인덕터 4.7µH 3.5A (LCSC: C408333)로 정상화** |
| **U2** | `SGM2036D-3.3YUDH4G/TR` (C700416) | 3.3V 300mA LDO 레귤레이터 | 일부 문서에 AP2112K로 오기재되었으나, 원본 프로젝트의 **SGMICRO SGM2036D-3.3(UTDFN-4L)**이 실제 부품임을 확정 및 일치화 |
| **U1** | `ESP32-WROOM-32E-N8` (C701342) | 메인 MCU (내장 안테나) | 일부 문서의 32UE(외장 안테나) 표기를 원본 라이브러리의 **ESP32-WROOM-32E(내장 안테나)**로 단일화 |
| **R7, R8, R11, R12** | 원본 PCB에는 미존재 (R1~R6만 존재) | I2C 버스 풀업 저항 | 이전 측정표의 R11/R12 오기를 정정하고, **PCB #0005는 ESP32 내부 풀업(~45kΩ) 사용 중**임을 실측표에 정확히 반영 |

---

## 3. PCB #0005 vs PCB Rev-C 엔지니어링 변경 내역

| 구분 | 기존 PCB #0005 (검증 기준선) | 신규 PCB Rev-C (인증 & 센서 확장) | 변경 목적 및 기술적 근거 |
| :--- | :--- | :--- | :--- |
| **승압 다이오드/인덕터** | 저항 소자 오매핑 (D3: 3.9kΩ, L1: 5.6kΩ) | **정규 소자 적용 (D3: SS34 쇼트키, L1: 4.7µH 파워 인덕터)** | 원본 설계 결함 완전 해소 및 승압 회로 정격 안정화 |
| **전원 보호** | USB-C VBUS 직결 | **1.5A 리셋터블 PPTC 퓨즈 (`F1`)** 직렬 추가 | 과전류 및 VBUS 쇼트 발생 시 자동 차단 (전기안전) |
| **스위칭 노이즈 억제** | MP3426 SW 핀 단순 인덕터 결선 | **RC 스너버 직렬 구성 (`2.2Ω + 1nF`)** | MP3426 SW 노드의 수십 MHz 대역 고주파 링잉 전압 감쇠 및 복사 방사(RE) 저감 대책 |
| **오디오 출력 필터** | TAS5805M BTL 출력 직결 | **페라이트 비드 (`FB1~FB4`, 100Ω@100MHz 2A)** | 익사이터 연결 케이블을 통한 고주파 노이즈 방사 억제 |
| **생체 BCG 센서** | 미지원 | **`J_BCG` (JST-SH 4P)**: 3.3V, GND, GPIO36, 39 | Wi-Fi/BT 동작 중에도 안정적인 ADC1 채널 기반 침대 매트리스 하부 PVDF 호흡/심박 감지 포트 |
| **생체 mmWave 레이더** | 미지원 | **`J_RADAR` (JST-SH 4P)**: 5V, GND, GPIO16, 17 | USB 시리얼 디버그와 독립된 하드웨어 UART2 통신 포트 |
| **환경/울음 마이크** | 미지원 | **`J_ENV_MIC` (JST-SH 6P)**: 3.3V, GND, I2C, I2S WS/DIN | SHT40 온습도 센서(I2C) 및 INMP441 디지털 마이크(I2S) 통합 포트 |
| **시험 및 노이즈 격리** | - | **0Ω 분리 링크 저항군 (`R_L1 ~ R_L7`)** | 양단 넷을 완전 분리하여 센서 모듈별 회로 격리 시험 및 노이즈 유입 경로 추적 용이성 확보 |

---

## 4. 정합성 및 DRC 검증 결과 (100% PASS)

`tools/verify_hardware_review.py` 자동 검증 스크립트를 통해 아래 7개 핵심 항목을 전수 검증하였습니다:

```
[TEST 1] epro2 SHA-256 Differentiation Check: PASS (Original과 Rev-C 바이너리 고유 해시 분리)
[TEST 2] PCB #0005 Original Component Parity: PASS (37개 부품 BOM-Netlist 1:1 일치)
[TEST 3] PCB Rev-C Component Parity: PASS (54개 부품 BOM-Netlist 1:1 일치)
[TEST 4] 0-Ohm Links Electrical Isolation: PASS (R_L1~R_L7 양단 넷 완전 분리 확인)
[TEST 5] MP3426 SW RC Snubber Serialization: PASS (BOOST_SW -> C_SNUB -> NET_SNUB_MID -> R_SNUB -> GND 직렬 확인)
[TEST 6] PPTC Fuse F1 USB Protection: PASS (NET_VBUS_RAW -> F1 -> VBUS_5V 보호 경로 확인)
[TEST 7] Global Short-Circuit Prevention: PASS (전원 레일 간 및 GND 단락 0건)
======================================================================
VERIFICATION SUMMARY: 7 / 7 TESTS PASSED (100.0%)
======================================================================
```
