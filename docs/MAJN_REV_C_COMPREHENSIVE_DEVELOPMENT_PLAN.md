# 마중(MAJN) 스마트 배시넷 Rev-C 종합 개발 및 양산·인증 마스터 플랜 (v2.0)

* **문서 버전:** Rev-C.Master.2.0 (Engineering Verified)
* **작성 일자:** 2026-10-31
* **기준 브랜치:** `feature/phone-wifi-control`
* **검증 도구:** `tools/verify_hardware_review.py` (10/10 Logic Rules Passed)

---

## 1. 프로젝트 기준선 및 SSOT 팩트 분리 (Ground Truth)

### 1.1 하드웨어 물리적 상태 및 검증 완료 팩트 (PCB #0005)
* **전원 무결성**: USB 5.02V 입력 $\rightarrow$ SGM2036-3.3 LDO (3.20V) $\rightarrow$ MP3426 승압 (12.00V PVDD) 레귤레이션 실측 확인.
* **디지털 오디오 및 액추에이터**: TI TAS5805M Class-D 앰프(I2C 주소 `0x2C`) 정상 `PLAY(0x03)` 상태 진입, 24.8Ω 직렬 익사이터 부하 구동 시 물리 진동 확인.
* **하드웨어 제약사항**:
  * 보드에 물리적 버튼(BOOT, EN) 일체 없음.
  * CP2102 헤더는 TX, RX, GND만 연결(DTR/RTS 리셋 회로 부재).
  * **유선 시리얼 플래시 불가, 무선 OTA(BLE / Wi-Fi) 전용 플래시 구조**.
* **D3/L1 부품 상태의 명확한 분리**:
  * **EasyEDA Pro 설계 파일(`Original.epro2`)**: D3 자리에 3.9kΩ 저항, L1 자리에 5.6kΩ 저항 심볼이 매핑되어 있던 **설계 파일 데이터 결함** 공식 확인.
  * **PCB #0005 실물 보드**: 12.00V 승압이 정상 발진하여 작동했으므로, 실물 제작 시 수작업 쇼트키 다이오드/파워 인덕터로 대체 실장되었을 가능성이 높으며 실물 부품은 육안 점검 대상임.
  * **모듈 모델명**: EasyEDA 라이브러리 등록명은 `ESP32-WROOM-32E-N8`(내장 안테나)이며 실물 모듈(32E vs 32UE)은 차기 육안 확인으로 최종 대조.

### 1.2 소프트웨어 제어 방식 전환 완료
* PC USB 유선 제어에서 **휴대폰 직접 제어(Wi-Fi SoftAP `MAJN-Bassinet` + Web-UI)**로 전환 완료.
* 5초 Heartbeat 감시 안전 Watchdog 및 Web-OTA(`/update`) 탑재.
* BLE 무손실 Paced OTA 스크립트(`tools/run_ble_ota.py`)를 통해 1,088KB 펌웨어 무선 플래시 성공 확인.

---

## 2. ESP32 공식 핀맵 및 Rev-C 모듈 패드 전수 매핑

공식 Espressif `ESP32-WROOM-32E / 32UE` 데이터시트를 기준으로 모듈 물리 패드 번호와 실제 GPIO 번호를 1:1 전수 검증하여 넷리스트를 재구성했습니다:

| 모듈 물리 패드 | 공식 GPIO 명칭 | 전기적 특성 | 기존 PCB #0005 넷 | Rev-C 개선/신규 결선 넷 | 정합성 검토 및 조치 사항 |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **Pad 1** | GND | Ground | GND | GND | 접지 기준면 |
| **Pad 2** | 3V3 | Power | VCC_3V3 | VCC_3V3 | 3.3V 전원 레일 |
| **Pad 3** | EN | Input (Pull-up) | ESP_EN | ESP_EN | R5=1kΩ, C17=100nF 지연 회로 |
| **Pad 4** | **GPIO36 (SENSOR_VP)** | **Input Only (ADC1_CH0)** | **NC** | **`NET_BCG_MCU_P` $\rightarrow$ `R_L1` $\rightarrow$ `J_BCG.3`** | **[정상화] Wi-Fi 무간섭 ADC1 전용 채널 할당** |
| **Pad 5** | **GPIO39 (SENSOR_VN)** | **Input Only (ADC1_CH3)** | **NC** | **`NET_BCG_MCU_N` $\rightarrow$ `R_L2` $\rightarrow$ `J_BCG.4`** | **[정상화] Wi-Fi 무간섭 ADC1 전용 채널 할당** |
| **Pad 6** | GPIO34 (VDET_1) | Input Only (ADC1_CH6) | SENSOR_INT1 | SENSOR_INT1 | LSM6DSOX INT1 인터럽트 |
| **Pad 7** | **GPIO35 (VDET_2)** | **Input Only (ADC1_CH7)** | **NC** | **`NET_MIC_MCU_DIN` $\rightarrow$ `R_L8` $\rightarrow$ `J_ENV_MIC.7`** | **[정상화] INMP441 디지털 오디오 데이터 입력 수신** |
| **Pad 8** | GPIO32 (32K_XN) | RTC, ADC1_CH4 | NC | NC | 예비 핀 (안전 격리) |
| **Pad 9** | GPIO33 (32K_XP) | RTC, ADC1_CH5 | NC | NC | 예비 핀 (안전 격리) |
| **Pad 10** | **GPIO25 (DAC_1)** | **Output, I2S_WS** | **I2S_LRCLK** | **`I2S_LRCLK` (공통) $\rightarrow$ `R_L7` $\rightarrow$ `J_ENV_MIC.6`** | **[정상화] TAS5805M 및 INMP441 I2S_WS 공통 클럭** |
| **Pad 11** | **GPIO26 (DAC_2)** | **Output, I2S_BCLK** | **I2S_BCLK** | **`I2S_BCLK` (공통) $\rightarrow$ `J_ENV_MIC.5`** | **[신규 추가] INMP441 필수 I2S_BCLK 비트 클럭 연결** |
| **Pad 12** | **GPIO27 (IO27)** | **I/O, I2C_SCL** | **AMP_I2C_SCL** | **`AMP_I2C_SCL` (공통) $\rightarrow$ `R_L6` $\rightarrow$ `J_ENV_MIC.4`** | **[정정] 문서상 GPIO19 오기재를 실제 패드 12(GPIO27)로 일치화** |
| **Pad 13** | GPIO14 (MTMS) | JTAG | NC | NC | 예비 핀 |
| **Pad 14** | **GPIO12 (MTDI)** | **Boot Strapping Pin!** | **NC** | **NC (완전 격리)** | **[보호] 부팅 전압(Flash Voltage) 변동 위험 원천 차단** |
| **Pad 23** | GPIO15 (MTDO) | Output | AMP_PDN | AMP_PDN | TAS5805M 파워다운 제어 |
| **Pad 25** | GPIO0 (IO0) | Boot Strapping | ESP_IO0 | ESP_IO0 | 부트스트랩 풀업 저항 R6(1kΩ) |
| **Pad 26** | GPIO4 (IO4) | Output | BOOST_EN | BOOST_EN | MP3426 승압 컨버터 Enable |
| **Pad 27** | **GPIO16 (RX2)** | **UART2 RX** | **NC** | **`NET_RADAR_MCU_RX` $\rightarrow$ `R_L3` $\rightarrow$ `J_RADAR.3`** | **mmWave 레이더 독립 하드웨어 수신** |
| **Pad 28** | **GPIO17 (TX2)** | **UART2 TX** | **NC** | **`NET_RADAR_MCU_TX` $\rightarrow$ `R_L4` $\rightarrow$ `J_RADAR.4`** | **mmWave 레이더 독립 하드웨어 송신** |
| **Pad 29** | GPIO5 (IO5) | Output | SPI_CS | SPI_CS | LSM6DSOX SPI Chip Select |
| **Pad 30** | GPIO18 (IO18) | Output | SPI_SCLK | SPI_SCLK | LSM6DSOX SPI Clock |
| **Pad 31** | **GPIO19 (IO19)** | **Input** | **SPI_MISO** | **SPI_MISO** | **LSM6DSOX SPI Data Input** |
| **Pad 33** | **GPIO21 (IO21)** | **I/O, I2C_SDA** | **AMP_I2C_SDA** | **`AMP_I2C_SDA` (공통) $\rightarrow$ `R_L5` $\rightarrow$ `J_ENV_MIC.3`** | **TAS5805M(0x2C) 및 SHT40(0x44) I2C 데이터 라인** |
| **Pad 34** | GPIO3 (U0RXD) | UART0 RX | ESP_RXD | ESP_RXD | USB-UART 통신 |
| **Pad 35** | GPIO1 (U0TXD) | UART0 TX | ESP_TXD | ESP_TXD | USB-UART 통신 |
| **Pad 36** | GPIO22 (IO22) | Output | I2S_DIN | I2S_DIN | TAS5805M 오디오 데이터 출력 (MCU DOUT) |
| **Pad 37** | GPIO23 (IO23) | Output | SPI_MOSI | SPI_MOSI | LSM6DSOX SPI Data Output |

---

## 3. 세부 회로 인터페이스 엔지니어링 사양

### 3.1 INMP441 & SHT40 복합 인터페이스 (`J_ENV_MIC` 7-Pin)
디지털 I2S 마이크의 동작을 위해서는 5대 신호(VDD, GND, SCK/BCLK, WS, SD/DIN)가 반드시 필요하므로, 기존 6-Pin에서 **JST-SH 1.0mm 7-Pin(`SM07B-SRSS-TB`)**으로 확장 완료했습니다:

```
[ESP32 MCU]
   Pad 11 (GPIO26) ──── I2S_BCLK (공통) ──────────────────────────────► J_ENV_MIC Pin 5 (BCLK)
   Pad 10 (GPIO25) ──── I2S_LRCLK ─────── [R_L7: 0Ω] ─────────────────► J_ENV_MIC Pin 6 (WS)
   Pad  7 (GPIO35) ◄─── NET_MIC_MCU_DIN ─ [R_L8: 0Ω] ◄── NET_MIC_CONN ── J_ENV_MIC Pin 7 (DIN)
   Pad 33 (GPIO21) ──── AMP_I2C_SDA ───── [R_L5: 0Ω] ─────────────────► J_ENV_MIC Pin 3 (SDA)
   Pad 12 (GPIO27) ──── AMP_I2C_SCL ───── [R_L6: 0Ω] ─────────────────► J_ENV_MIC Pin 4 (SCL)
```
* **동기화 원리**: ESP32 I2S Master가 출력하는 BCLK(1.536MHz) 및 WS(48kHz) 클럭을 TAS5805M 앰프와 INMP441 마이크가 함께 공유 수신하여 지터 없이 완벽 동기화.
* **노이즈 격리**: 인증 시험 시 `R_L5 ~ R_L8` 4개 저항을 미실장(DNP)하여 센서 인출 라인을 완벽 차단.

### 3.2 BCG 생체 신호 수신 및 아날로그 프런트엔드(AFE) 분석
* **센서 특성 한계 인지**: PVDF 압전 필름 센서는 전하 발생형(Charge generator) 초고임피던스 소자이므로, **ESP32 내장 ADC에 직결 시 신호가 즉시 감쇠/방전되어 호흡/심박(0.1~10Hz 대역, 수십 µV~수 mV) 추출이 불가능함**.
* **Rev-C 포트 규정**: `J_BCG` (JST-SH 4P: 3.3V, GND, VP, VN) 포트는 **"외부 전하 증폭 AFE 모듈"을 연결하기 위한 아날로그 인터페이스 포트**로 명확히 정의함.
* **필수 AFE 구성 요건 (외부 모듈 사양)**:
  1. 초고입력 임피던스(>100MΩ) JFET/CMOS OP-Amp(예: TI TLV6001 / OPA320) 기반 전하 증폭기(Charge Amplifier).
  2. 0.1Hz ~ 15Hz 대역 능동 대역통과 필터(BPF).
  3. ESP32 ADC 입력 범위(0~3.3V)에 맞춘 1.65V DC 가상 접지 바이어스.
  4. 정전기(ESD) 및 과전압 보호용 클램핑 쇼트키 다이오드(BAT54S).

### 3.3 USB Type-C 전원 입력 표준화
* **CC 풀다운 저항 정상화**: 기존 14kΩ 비표준 저항을 **표준 5.1kΩ ±1% (0603, LCSC: `C23186`) Rd 풀다운 저항(`R3`, `R4`)**으로 교체하여 최신 USB-PD 및 Type-C 고속 충전기에서의 5V 공급 거부 문제를 원천 해결.
* **커넥터 핀 매핑 정정**: 원본 넷리스트상 CC2가 B8(SBU2)로 잘못 라우팅되어 있던 결선을 **`B5`(CC2 패드)**로 정확히 결선.
* **PPTC 퓨즈 보호**: USB VBUS 입력단에 1.5A 6V 리셋 가능 폴리퓨즈(`F1`, LCSC: `C112349`)를 직렬 삽입하여 단락 및 과전류 보호.

### 3.4 RC 스너버 및 페라이트 비드 엔지니어링 가설 성격 명시
* **MP3426 RC 스너버 (`2.2Ω + 1nF`)**:
  * 본 값은 900kHz 스위칭 주파수의 고조파 감쇠를 위한 **설계 가설 목표값(Hypothesis)**임.
  * 확정값이 아니며, Rev-C 시제품 보드 조립 후 오실로스코프로 SW 핀의 링잉 주파수, 스너버 저항 발열($P = C V^2 f$), 효율 변화를 실측 비교한 후 최종 R/C 값을 튜닝하여 확정함.
* **TAS5805M BTL 출력 페라이트 비드 (`FB1 ~ FB4`)**:
  * 1~2m 익사이터 케이블의 안테나 방사 억제를 위한 옵션 패드임.
  * Class-D 출력 고조파 및 익사이터 구동 파형 왜곡 여부를 비드 실장 vs 미실장 상태로 벤치 비교 시험한 후 최종 실장 여부를 결정함.

---

## 4. 검증 스크립트 스코프 및 10대 논리 규칙 결과

`tools/verify_hardware_review.py`는 **전기적 넷리스트 및 BOM의 논리적 무결성을 검증하는 도구**이며, 기하학적 PCB 레이아웃(Clearance, 패턴 폭, 비아, 동박) DRC는 에디터 내장 DRC를 통해 교차 검증해야 합니다.

```
==============================================================================
MAJN HARDWARE REVIEW SUITE - LOGICAL & ELECTRICAL VERIFICATION (v2.0)
==============================================================================
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

---

## 5. 단계별 현실적 개발 일정 (Realistic Action Timeline)

무리한 50일 일정을 지양하고, **기본 진동 구동부의 안전성/효과성 검증을 최우선**으로 하며 센서를 단계별(BCG $\rightarrow$ 레이더 $\rightarrow$ 마이크)로 검증하는 현실적 로드맵을 수립합니다:

```
[Phase 1: 회로 확정 & 아트워크] ──► [Phase 2: 기판 샘플 제작] ──► [Phase 3: 기본 구동 벤치 실측]
 논리 넷리스트 기반 EasyEDA 배치      JLCPCB 4층 기판 5장 발주      전원 레일, 스너버/비드 발열 실측
 물리적 DRC 0건 달성 및 거버 생성    LCSC 55종 부품 수급           익사이터 진동 안전성 우선 검증
 (현재 진행 중 ~ D+5)                (D+6 ~ D+12)                   (D+13 ~ D+20)
                                                                           │
 ┌─────────────────────────────────────────────────────────────────────────┘
 ▼
[Phase 4: 센서 단계별 연동 검증] ─► [Phase 5: EMC 사전 시험 및 튜닝] ─► [Phase 6: KC 적합등록 본시험]
 Step 1: BCG 외부 AFE 아날로그 신호     공인 시험소 챔버 사전 측정        기본형(DNP) 1차 인증 취득
 Step 2: 60GHz 레이더 UART2 파싱       스너버/비드 최적값 확정           센서형 파생 모델 순차 신고
 Step 3: I2S 마이크 음향 수집          (D+31 ~ D+40)                     (D+41 ~ D+60)
 (D+21 ~ D+30)
```
