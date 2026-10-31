# 마중 스마트 배시넷 하드웨어 및 회로 검토 패키지 가이드

본 디렉토리(`hardware_review/`)는 EasyEDA Pro 네이티브 바이너리(`.epro2`)의 분석 한계를 극복하고, AI 에이전트 및 하드웨어 엔지니어가 회로 결선, 넷리스트, BOM, 실측값, 인증 규격을 전수 교차 검증할 수 있도록 표준화된 형태로 구성된 마스터 패키지입니다.

* **상세 종합 마스터 플랜:** [`docs/MAJN_REV_C_COMPREHENSIVE_DEVELOPMENT_PLAN.md`](file:///Users/youngseok/Desktop/majn/docs/MAJN_REV_C_COMPREHENSIVE_DEVELOPMENT_PLAN.md)

---

## 1. 디렉토리 구조 및 파일 역할

```
hardware_review/
├── README.md                           # 본 가이드 문서 (SSOT 및 논리 검증 결과 수록)
├── PCB_0005_original/                  # [기준 원본] 실측 검증 완료 골든 베이스라인
│   ├── Original.epro2                 # EasyEDA Pro 원본 프로젝트 아카이브
│   ├── BOM.csv                        # 37개 정본 부품 명세서 (LCSC ID, 패키지, 제조사, 설계결함 주석)
│   ├── Netlist.net                    # 42개 넷 결선 전수 핀맵 정의서
│   ├── Netlist.json                   # 기계 판독용 넷리스트 JSON
│   └── Gerber_Output.zip              # PCB #0005 제조용 거버 파일
│
├── PCB_Rev_C/                          # [개선 사본] 전파인증(EMC) 및 3대 센서 확장 리비전
│   ├── Rev_C.epro2                    # Rev-C 프로젝트 바이너리 (실체화 완료, 고유 SHA)
│   ├── BOM.csv                        # 55개 부품 명세서 (정상화 D3/L1 + 센서 포트 + 0Ω 8종 + 스너버 + PPTC)
│   ├── Netlist.net                    # 60개 넷 결선도 (Espressif 공식 패드 및 USB-C B5 정합성 반영)
│   └── Gerber_RevC_Base.zip           # 4층 기판 베이스 거버 아카이브
│
├── Measurements/                       # [실측 전수 데이터] PCB #0005 실기 계측 Ground Truth
│   ├── Voltage.csv                    # 전원 레일 실측 (VBUS 5.02V, VCC 3.20V, PVDD 12.00V)
│   ├── Resistance.csv                 # 익사이터 부하 DCR(21.6Ω)/공칭 임피던스(24Ω), 실장 저항 실측
│   └── Test_Results.md                # 2026-10-24 익사이터 물리 진동 확인 및 SSOT 분석 보고서
│
└── Datasheets/                         # 주요 핵심 IC 데이터시트 보관소
    └── (TAS5805M, MP3426, ESP32-WROOM-32E, LSM6DSOX)
```

---

## 2. 2차 기술 검토 반영 및 정합성 교정 내역

| 항목 | 기존 문제점 / 불일치 | 2차 기술 검토 정정 조치 | 하드웨어적 근거 및 효과 |
| :--- | :--- | :--- | :--- |
| **BCG 핀맵** | GPIO36/39 주장 vs 실제 넷리스트는 Pad 8, 9 (GPIO32/33) | **Pad 4(GPIO36, SENSOR_VP) 및 Pad 5(GPIO39, SENSOR_VN)로 결선 수정** | Wi-Fi/BT 작동 시에도 충돌 없는 ADC1 채널 정규 할당 |
| **I2C SCL** | 문서상 GPIO19 기재 | **Pad 12(GPIO27, IO27)로 문서 및 넷리스트 일치화** | GPIO19는 SPI_MISO에 연결되어 있으므로 실제 패드 12번(GPIO27)으로 통일 |
| **마이크 신호** | INMP441 BCLK 신호 누락 및 DIN 격리 부재 | **`J_ENV_MIC`를 7-Pin으로 확장(BCLK 추가) 및 DIN 격리 저항(`R_L8`) 추가** | I2S 3대 신호(BCLK Pad 11, WS Pad 10, DIN Pad 7) 완전 수용 및 노이즈 격리 |
| **부팅 핀 보호** | GPIO12(Pad 14) 외장 연결 위험 | **GPIO12(Pad 14) 완전 NC(미연결) 처리** | 부팅 스트래핑 핀으로 인한 Flash VDD 전압 오작동 위험 원천 차단 |
| **USB-C 회로** | 비표준 14kΩ 저항 및 CC2 패드 B8 오매핑 | **표준 5.1kΩ Rd 저항(`R3`, `R4`) 적용 및 CC2 패드를 B5로 정정** | USB Type-C 표준 Sink 규격 준수 (B8은 SBU2이므로 CC2 B5로 정상화) |
| **BCG AFE** | PVDF 센서의 MCU 직결 불가 특성 미반영 | **`J_BCG`를 '외부 AFE 전하 증폭 모듈용 인터페이스'로 재정의** | 초고임피던스 전하 방전 방지 및 아날로그 증폭 회로 사양 수립 |
| **스너버/비드** | 확정값으로 기술되었던 표현 | **시제품 실측 및 온도/파형 비교를 거쳐 확정할 '설계 가설/튜닝 옵션'으로 명시** | 벤치 테스트를 통한 최적 부품값 선정 절차 확립 |

---

## 3. 정합성 및 논리 DRC 검증 결과 (10 / 10 PASS)

`tools/verify_hardware_review.py` 자동 검증 스크립트를 통해 아래 10개 핵심 논리 규칙을 전수 검증하였습니다:

```
[TEST 1] epro2 Binary SHA-256 Differentiation: PASS (Original과 Rev-C 바이너리 분리)
[TEST 2] PCB #0005 Original Component Parity: PASS (37개 부품 1:1 일치)
[TEST 3] PCB Rev-C Component Parity: PASS (55개 부품 1:1 일치)
[TEST 4] ESP32-WROOM-32E Official Pad Map: PASS (Pad 4=GPIO36, Pad 5=GPIO39, Pad 7=GPIO35, Pad 10=GPIO25, Pad 11=GPIO26, Pad 12=GPIO27, Pad 14=NC(Safe))
[TEST 5] USB Type-C Standard Compliance: PASS (CC1/CC2 5.1kΩ Rd 정상화, B5 패드 정정 완료)
[TEST 6] INMP441 Microphone Completeness: PASS (BCLK, WS, DIN 3대 I2S 신호 완비)
[TEST 7] 0-Ohm Links Electrical Isolation: PASS (R_L1~R_L8 8개 저항 양단 넷 완전 분리)
[TEST 8] MP3426 SW RC Snubber Serialization: PASS (BOOST_SW -> C_SNUB -> R_SNUB -> GND 직렬 확인)
[TEST 9] PPTC Fuse F1 USB Protection: PASS (NET_VBUS_RAW -> F1 -> VBUS_5V 보호 경로 확인)
[TEST 10] Global Power Rail Short-Circuit Check: PASS (전원 레일 간 및 GND 단락 0건)
==============================================================================
VERIFICATION SUMMARY: 10 / 10 LOGICAL RULES PASSED (100.0%)
==============================================================================
```
*(주의: 본 검증은 논리 넷리스트 및 BOM 정합성 검사이며, 기하학적 PCB 레이아웃 DRC는 EasyEDA Pro 내장 DRC로 교차 수행됩니다.)*
