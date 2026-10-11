# MAJN Smart Bassinet 실물 PCB(#0005) 오디오/진동 계통 종합 진단 보고서 및 엔지니어 인수인계 가이드

- **작성 일시**: 2026-10-11
- **대상 하드웨어**: MAJN Smart Bassinet PCB Rev 1.0 (실물 보드 일련번호 `#0005`)
- **핵심 칩셋**:
  - MCU: ESP32-WROOM-32UE (8MB Flash, dual-core Tensilica Xtensa LX6)
  - Audio Amp: TI TAS5805M (Class-D Stereo BTL, I2S Digital Input, I2C Control)
  - Boost Converter: MPS MP3426 (12V 승압 레귤레이터, GPIO4 제어)
  - IMU Sensor: ST LSM6DSOX (6-axis Accel/Gyro, SPI)
  - USB-to-UART: Silicon Labs CP2102
  - Transducer: Tectonic TEAX14C02-8 (8Ω 초슬림 익사이터, `J1`/`J2` 단자 결선)
- **Git 원격 저장소**: `https://github.com/youngseokchomajn-web/MAJN_GEMINI` (`origin/main`)

---

## 1. 하드웨어 전원 및 신호 아키텍처 개요

### 1.1 전원 계통 (Power Delivery Network)
> **중요 (주의 사항)**: 보드에는 별도의 외부 12V 전원 입력 잭이 없습니다!
- **USB-C 단자 (5.0V 입력)** ➔ 전원 스위치 통과 ➔ `VBUS_5V` 형성
- `VBUS_5V` ➔ **MPS MP3426 Boost Converter** 입력
- **ESP32 GPIO4 (`BOOST_EN`)**:
  - `LOW`: 승압 꺼짐 (쇼트키 다이오드 `D3`를 통해 약 4.6V~5.0V만 TAS5805M PVDD로 통과)
  - `HIGH`: 12.12V 승압 활성화 ➔ TAS5805M `PVDD` 레일로 12V 공급
- `VCC_3V3`: AMS1117-3.3 LDO 레귤레이터를 통해 ESP32, TAS5805M DVDD, IMU에 3.3V 공급

### 1.2 오디오/진동 신호 계통 (ESP32 ➔ TAS5805M ➔ J1/J2)
| 기능 | 핀 번호 / 네트 | 방향 | 사양 및 설명 |
|---|---|---|---|
| **BOOST_EN** | GPIO4 | ESP32 ➔ MP3426 | 12V 승압 인에이블 (Active HIGH) |
| **AMP_PDN** | GPIO15 | ESP32 ➔ TAS5805M | 앰프 파워다운 해제 (Active HIGH) |
| **I2C SDA** | GPIO21 | 양방향 | TAS5805M 제어 버스 (4.7kΩ 풀업) |
| **I2C SCL** | GPIO27 | ESP32 ➔ TAS5805M | TAS5805M 클럭 버스 (4.7kΩ 풀업) |
| **I2S BCLK** | GPIO26 | ESP32 ➔ TAS5805M | 오디오 비트 클럭 (48kHz × 32 = 1.536 MHz) |
| **I2S LRCLK (WS)**| GPIO25 | ESP32 ➔ TAS5805M | 워드 셀렉트 클럭 (48.0 kHz) |
| **I2S DOUT** | GPIO22 | ESP32 ➔ TAS5805M | 시리얼 오디오 데이터 (16-bit PCM Sine) |
| **OUT_L / OUT_R**| `J1`, `J2` | TAS5805M ➔ 익사이터| BTL(Bridge-Tied Load) 방식 45Hz 수면 진동 출력 |

---

## 2. 앰프(TAS5805M) 트러블슈팅 및 4대 핵심 결함 규명 내역

실물 보드(#0005) 브링업 과정에서 발견되어 최신 펌웨어(`origin/main`)에 전면 반영된 4대 핵심 결함과 해결 내역입니다.

### 📌 결함 1: I2C 슬레이브 주소 불일치 (`0x2C` vs `0x2D`)
- **원인**: 회로도 상 TAS5805M의 3번 핀(`ADR`)이 `R12 (4.7kΩ)` 저항을 통해 `3.3V(DVDD)`로 풀업되어 있음.
- **데이터시트 규격**: ADR 핀이 풀업된 경우 I2C 슬레이브 주소는 `0x2C`가 아닌 **`0x2D`**임.
- **해결 (`tas5805m.cpp`)**: 
  - 기본 주소를 `0x2D`로 변경하고, `0x2D` ➔ `0x2C` 자동 탐색 프로브 루틴 구현.

### 📌 결함 2: I2S 샘플링 레이트 지원 규격 불일치 (`16kHz` vs `48kHz`)
- **원인**: 기존 펌웨어가 16kHz로 I2S 클럭을 공급함. 그러나 TI TAS5805M 칩셋의 내부 PLL 및 자동 클럭 감지기는 32kHz~96kHz만 지원함 (16kHz 미지원).
- **현상**: TAS5805M 내부 `GLOBAL_FAULT1 (0x71)` 레지스터에 `CLOCK_FAULT`가 발생하여 앰프가 출력을 스스로 차단(Hi-Z)함.
- **해결 (`vibration_controller.cpp`)**:
  - `SAMPLE_RATE`를 표준 **`48000Hz (48kHz)`**로 상향 조정.

### 📌 결함 3: PLAY 모드 진입 레지스터 반대 설정 (`0x02` vs `0x03`)
- **원인**: TAS5805M `REG_DEVICE_CTRL_2 (0x03)` 레지스터 정의:
  - `0x00`: Deep Sleep
  - `0x01`: Sleep
  - `0x02`: **Hi-Z (출력 단선 / 고임피던스 대기 모드)**
  - `0x03`: **PLAY (스피커/익사이터 출력 구동 모드)**
- **기존 버그**: 코드가 `enterPlayState()`에서 `0x02`를 기록하여 앰프를 강제 Hi-Z로 차단하고 있었음.
- **해결 (`tas5805m.cpp`)**:
  - `enterPlayState()`에서 명확하게 **`0x03 (PLAY)`** 기록하도록 전면 수정.

### 📌 결함 4: I2S 오디오 포트 비트 심도(Word Length) 미설정
- **원인**: TAS5805M `SAP_CTRL_1 (0x33)` 기본값이 24-bit I2S였으나, ESP32 I2S 드라이버는 16-bit 데이터를 전송하여 데이터 비트 정렬이 어긋남.
- **해결 (`tas5805m.cpp`)**:
  - `writeRegister(0x33, 0x00)`를 추가하여 명시적으로 16-bit I2S 포맷으로 동기화.
  - 마스터 볼륨(`0x4C`)을 `0x00` (0dB Unity Gain)으로 개방하고, 사인파 룩업테이블 연산 진폭 상한을 1.0으로 확대.

---

## 3. 동료 엔지니어를 위한 하드웨어 실측 & 계측 체크리스트

실물 보드에서 진동이 느껴지지 않거나 오디오 출력을 점검할 때, 아래 순서대로 멀티미터(DMM)와 오실로스코프로 측정하십시오.

### 3.1 DMM 전압 측정 (DC Voltage)
| 계측 포인트 | 정상 전압 (대기) | 정상 전압 (동작/START) | 이상 시 의심 부품 / 조치 |
|---|---|---|---|
| **USB-C VBUS** | 5.0V ± 0.2V | 5.0V ± 0.3V | USB 케이블 또는 전원 어댑터 전력 부족 |
| **3.3V 레일 (C17, ESP32 3V3)** | 3.3V ± 0.05V | 3.3V ± 0.05V | AMS1117 LDO 불량 또는 과전류 |
| **GPIO4 (BOOST_EN)** | 0.0V (LOW) | **3.3V (HIGH)** | ESP32 펌웨어 부팅 실패 또는 SafeStop 상태 |
| **D3 다이오드 캐소드 (PVDD)** | ~4.7V | **12.12V ± 0.2V** | MP3426 부스트 컨버터, 인덕터 L1, 피드백 저항 R3/R4 점검 |
| **GPIO15 (AMP_PDN)** | 0.0V | **3.3V (HIGH)** | TAS5805M이 셧다운(Mute) 상태로 잠겨 있음 |
| **TAS5805M 3번 핀 (ADR)** | **3.3V** | **3.3V** | R12(4.7kΩ) 풀업 확인 (0V일 경우 I2C 주소가 0x2C로 변함) |
| **J1, J2 익사이터 단자** | 0.0V DC | 0.0V DC (AC만 흐름)| 직류 저항 측정(전원 OFF 시): 8Ω~23Ω 정상 |

### 3.2 오실로스코프 신호 측정 (Oscilloscope)
보드에 START 명령이 전송되어 동작 중일 때 프로빙하십시오:
1. **GPIO26 (I2S BCLK)**:
   - 파형: 1.536 MHz 3.3V 사각파 (Square wave) 정상 확인.
2. **GPIO25 (I2S LRCLK)**:
   - 파형: 48.0 kHz 3.3V 사각파 정상 확인.
3. **GPIO22 (I2S DOUT)**:
   - 파형: 48kHz 클럭에 동기화된 45Hz 사인파 데이터 버스트 관찰.
4. **J1 단자 (BTL 출력)**:
   - 파형: 45Hz 주파수(주기 약 22.2ms)의 AC 차동 신호가 최대 12Vpp로 스윙해야 함.

---

## 4. Web Bluetooth 기반 100% 무선 OTA 펌웨어 업데이트 절차

물리적 UART 케이블이나 핀 쇼트(IO0/EN 점퍼) 없이, 웹 브라우저에서 최신 펌웨어를 10초 만에 보드로 무선 주입할 수 있습니다.

### 4.1 로컬 웹 시뮬레이터 실행
로컬 HTTP 서버가 8080 포트에서 실행 중입니다:
- 브라우저 주소: `http://localhost:8080/bassinet_simulator/index.html`

### 4.2 펌웨어 바이너리 위치
- **빌드 산출물**: `인증준비/firmware/.pio/build/esp32_full_hw/firmware.bin`
- **배포 복사본**:
  - `bassinet_simulator/majn_latest_firmware.bin`
  - `~/Desktop/majn_latest_firmware.bin`
  - `~/Downloads/majn_latest_firmware.bin`

### 4.3 업데이트 진행 순서
1. Mac Chrome 브라우저에서 `http://localhost:8080/bassinet_simulator/index.html` 접속.
2. 상단 **`[ESP32 BLE 연결]`** 클릭 ➔ 장치 목록에서 `MAJN-Bassinet` 선택 후 페어링.
3. 우측 상단 **"무선 펌웨어 업데이트 (Web BLE OTA)"** 패널로 이동.
4. **`[파일 선택]`** 클릭 ➔ 바탕화면의 `majn_latest_firmware.bin` 선택.
5. **`[무선 플래싱 시작 (OTA)]`** 클릭:
   - 진행률이 0%에서 100%까지 프로그레스 바로 실시간 표시됨.
   - 100% 완료 시 ESP32가 자체 검증 후 새 펌웨어로 자동 소프트 리셋됨.
6. 3초 후 상단 **`[ESP32 BLE 연결]`**을 다시 눌러 재연결.
7. 화면 중앙의 **`[START]`** 클릭 ➔ 상태가 `RUNNING`으로 바뀌며 `J1` 단자 익사이터에서 45Hz 수면 유도 진동 즉시 발생.

---

## 5. 비상 시 수동 시리얼(UART) 플래싱 가이드

무선 OTA가 불가능한 벽돌(Brick) 상태일 경우에만 사용하는 수동 ROM 부트로더 진입 절차입니다.

### 5.1 기생 전원 및 금속 외피 접지 주의점
- **USB-C 단자 외피**: 표면 절연 코팅으로 인해 접지(0V)가 불안정합니다. 접지는 반드시 보드의 **`UART_HDR` 6번 핀(GND)**을 사용하십시오.
- **CP2102 기생 전원**: USB 케이블을 뽑아도 CP2102의 TX 핀을 통해 ESP32 내부로 3.3V 전력이 역류하여 리셋이 걸리지 않을 수 있습니다. 반드시 **`2번 핀(EN)`을 접지(6번 핀)에 접촉시켜 C17 커패시터를 강제 방전**시켜야 합니다.

### 5.2 부트로더 진입 3단계
1. `UART_HDR`의 **3번 핀(IO0)**을 점퍼선으로 **6번 핀(GND)**에 계속 연결해 둡니다.
2. `UART_HDR`의 **2번 핀(EN)**을 **6번 핀(GND)**에 1초간 살짝 댔다가 뗍니다 (하드웨어 리셋 트리거).
3. 터미널에서 아래 명령을 실행하여 플래싱:
   ```bash
   cd /Users/youngseok/Desktop/majn/인증준비/firmware
   ~/.platformio/penv/bin/pio run -e esp32_full_hw -t upload
   ```
4. 플래싱 완료 후 `3번 핀(IO0)`의 접지 점퍼선을 제거하고 보드 전원을 재인가합니다.

---

## 6. 결론 및 인수인계 요약

- **원격 동기화**: 모든 최신 펌웨어 수정 사항과 진단 도구는 GitHub 원격 저장소(`origin/main`)에 푸시되어 있습니다.
- **테스트 결론**: 
  - I2C 주소(`0x2D`), I2S 샘플링 레이트(`48kHz`), Play 모드 레지스터(`0x03`), 16-bit 오디오 포맷 설정(`0x33: 0x00`)이 모두 완료되었습니다.
  - 진동이 약하거나 안 느껴질 경우, 먼저 **멀티미터로 D3 다이오드 캐소드 전압이 12V로 승압되는지** 확인하십시오. 12V가 측정되지 않는다면 `BOOST_EN` 신호 또는 MP3426 부스트 회로를 점검해야 합니다.
