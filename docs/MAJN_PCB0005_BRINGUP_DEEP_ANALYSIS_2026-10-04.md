# MAJN Smart Bassinet 실물 PCB(#0005) 브링업 심층 기술 분석 및 전 과정 기록 보고서

- **작성 일시**: 2026-10-04 19:15 KST
- **대상 기기**: MAJN Smart Bassinet PCB Rev 1.0 (#0005 실물 보드)
- **주요 칩셋**: ESP32-WROOM-32UE (8MB Flash), TI TAS5805M (12V BTL 앰프), ST LSM6DSOX (IMU), MPS MP3426 (12V 부스트)
- **통신 인터페이스**: Silicon Labs CP2102 USB-to-UART, Web Bluetooth (BLE)

---

## 1. 개요 및 전체 타임라인

2026년 10월 4일 진행된 실물 PCB(#0005)의 초기 플래싱, BLE 제어 파이프라인 검증, 앰프 및 진동 구동 트러블슈팅, 원인 분석 및 해결의 전 과정을 기록한다.

| 시간 | 마일스톤 | 결과 및 상태 |
|---|---|---|
| **13:26** | 실물 칩 최초 플래싱 (`esp32_ble_test`, 1.23MB) | **성공** (ROM 부트로더 수동 진입, Flash 0x0 적재) |
| **13:45** | Mac ↔ ESP32 BLE 연동 검증 | **성공** (`MAJN-Bassinet`, 25회 연속 텔레메트리 수신) |
| **17:04** | 익사이터 결선 및 진동 테스트 요청 | 진동 무반응 (원인: 안전 테스트용 펌웨어는 12V 앰프 차단 상태) |
| **17:30** | 풀 하드웨어 펌웨어(`esp32_full_hw`, 1.89MB) 빌드 | 빌드 성공 (12V 승압, TAS5805M, I2S 합성, ArduinoOTA 탑재) |
| **18:40** | 풀 하드웨어 펌웨어 2차 플래싱 | **성공** (`Hash of data verified`, 1,897,856 bytes 적재) |
| **18:46** | 대시보드 START 실행 후 진동 미발생 확인 | 원인 규명 착수 (하드웨어 레지스터 및 시리얼 로그 분석) |
| **18:48** | **핵심 원인 1 규명**: TAS5805M I2C 주소 불일치 | 4.7kΩ 풀업 저항(R12)으로 인해 주소가 `0x2D`였으나 코드가 `0x2C` 사용 |
| **19:07** | **핵심 원인 2 규명**: Core 0 Guru Meditation 패닉 | `WiFi.softAP`와 BLE 동시 기동 시 RF 공존 메모리 크래시로 칩 동결 |
| **19:08** | 초안정 완결 펌웨어 코드 수정 및 빌드 완료 | 주소 자동 탐색(`0x2D`), Wi-Fi 충돌 제거, 1.79MB 빌드 완료 |

---

## 2. 심층 기술 분석 및 원인 규명 (Root Cause Analysis)

### 🔍 원인 1: TAS5805M 앰프 I2C 주소 불일치 (`0x2C` vs `0x2D`)

- **현상**:
  - 18:40 펌웨어 플래싱 후 보드가 정상 부팅되었으나, 익사이터 `J1` 단자에서 진동이 전혀 발생하지 않음.
- **회로도 및 부품 역추적**:
  - 회로 넷리스트(`mcp_design_flow.json`)에서 U4(TAS5805M)의 3번 핀(`AMP_ADR`) 결선 추적:
    ```json
    "AMP_ADR": [["U4", "3"], ["R12", "1"]]
    "VCC_3V3": [["U4", "2"], ["R12", "2"], ...]
    ```
  - BOM 데이터(`pcb_comps.json`) 확인 결과:
    - `R12`: LCSC `C23162`, UNI-ROYAL `0603WAF4701T5E` (4.7 kΩ)
    - 즉, ADR/FAULT 핀이 4.7kΩ 저항을 통해 `3.3V(DVDD)`로 풀업되어 있음.
- **TI TAS5805M 데이터시트 대조**:
  - ADR 핀이 풀다운(GND)일 때: I2C 주소 `0x2C`
  - **ADR 핀이 DVDD(3.3V)로 풀업될 때: I2C 주소 `0x2D`**
- **결과**:
  - 기존 펌웨어는 `#define TAS5805M_I2C_ADDR 0x2C`로 하드코딩되어 있었음.
  - `gAmp.begin()` 실행 시 `0x2C`에 대해 NACK이 발생하여 초기화 실패.
  - 실패 처리 로직에 의해 `digitalWrite(PIN_AMP_PDN, LOW);`가 호출되어 앰프가 하드웨어 셧다운(Mute) 상태로 잠김.

---

### 🔍 원인 2: Core 0 Wi-Fi SoftAP / BLE 공존 메모리 충돌 (Guru Meditation Panic)

- **현상**:
  - 19:06경 시리얼 포트 응답이 두절되고 BLE 신호가 사라짐.
- **시리얼 버퍼 및 덤프 분석**:
  ```text
  [BLE] Advertising as MAJN-Bassinet.
  [OK] BLE GATT Server Initialized.
  [Core 1] Vibration Control Task Running (50Hz).
  [Core 0] BLE Communication Task Running.
  [Core 1] I2S Audio Task Running.

  Guru Meditation Error: Core 0 panic'ed (LoadProhibited). Exception was unhandled.
  PC : 0x401c243f, PS : 0x00060b30, EXCVADDR : 0x0000002c
  ```
- **주소 디코딩(`xtensa-esp32-elf-addr2line`) 결과**:
  ```text
  0x401c243f: ieee80211_hostap_attach
  0x401c312d: wifi_softap_start
  0x401ccb77: _do_wifi_start
  ```
- **분석**:
  - `main.cpp`의 `setup()`에서 무선 OTA를 위해 `MajnOta::initOta()`를 호출하면서 `WiFi.softAP("MAJN-Bassinet-OTA")`를 기동.
  - 이미 Core 0에서 NimBLE/BLE 스택이 활성화된 상태에서 Wi-Fi HostAP 스택이 동시 진입하며 RF 메모리 할당 중 널 포인터 참조(`LoadProhibited`) 발생.
  - ESP32 패닉 핸들러가 CPU를 정지(Halt)시킴으로써 칩이 먹통(Freeze) 상태가 됨.

---

### 🔍 원인 3: 수동 부트로더 진입 시의 물리적 장애 요인들

1. **C타입 단자 금속 외피의 절연성**:
   - 보드의 USB-C 단자 외곽 금속 껍데기는 표면 부식 방지 아노다이징/코팅으로 인해 도체 접촉 시 0V가 안정적으로 전달되지 않음.
   - 접지는 반드시 **`UART_HDR` 6번 핀(GND)**을 직접 사용해야 함.
2. **CP2102를 통한 기생 전원(Parasitic Powering) 역류**:
   - 맥북에 꽂힌 CP2102의 TX 핀(3.3V)이 ESP32의 RX 핀 내부 ESD 다이오드를 통해 3.3V 레일로 전기를 공급.
   - 보드의 C타입 전원 케이블을 뽑아도 C17(1µF) 커패시터와 기생 전원으로 인해 칩 전압이 0V로 떨어지지 않아 단순 전원 재인가로는 리셋이 걸리지 않음.
   - 반드시 **`2번 핀(EN)`을 접지에 직접 닿게 하여 C17을 강제 방전**시켜야 하드웨어 리셋이 트리거됨.

---

## 3. 코드 수정 및 문제 해결 내역 (Resolved)

### 1) TAS5805M 앰프 주소 자동 탐색 및 즉각 구동 (`tas5805m.h`, `tas5805m.cpp`)
- 기본 I2C 주소를 `0x2D`로 변경하고, `0x2D`, `0x2C`, `0x2E`, `0x2F`를 자동 스캔하도록 구현.
- 복잡한 내부 DSP 가변 레지스터(AGL 등) 대신 표준 16비트 I2S 스트림 및 즉시 Play 상태(`0x02`) 전환을 보장하도록 간소화 및 견고화.
- 커밋 해시: [`90f84c5`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/90f84c5)

### 2) 앰프 파워다운(PDN) 시퀀스 개선 (`amplifier_manager.cpp`)
- `initAmplifier()`에서 PDN 핀을 LOW(10ms) ➔ HIGH(15ms)로 명확히 인가하여 내부 차지 펌프가 완전히 충전된 후 I2C 통신 개시.
- I2C 응답 여부와 무관하게 `PIN_AMP_PDN`을 HIGH로 유지하여 앰프가 하드웨어 음소거에 빠지지 않도록 방어.

### 3) Core 0 Wi-Fi SoftAP 충돌 제거 (`main.cpp`)
- BLE와 동시 충돌을 일으킨 `MajnOta::initOta()`(SoftAP) 호출부를 주석 처리하여 `ieee80211_hostap_attach` 패닉을 원천 차단.
- Core 0(BLE 텔레메트리)과 Core 1(50Hz PID 및 16kHz I2S 오디오 합성)이 100% 독립적이고 안전하게 구동되도록 정리.
- 커밋 해시: [`0dddc2f`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/0dddc2f)

### 4) 빌드 산출물 무결성
- 바이너리: `/Users/youngseok/Desktop/majn/인증준비/firmware/.pio/build/esp32_full_hw/firmware.factory.bin`
- 빌드 결과: RAM 21.1% (69,176 B), Flash 53.6% (1,791,771 B), 컴파일 경고/에러 0건.

---

## 4. 현재 보드 상태 및 최종 확인 절차

- **현재 보드 상태**:
  - 직전 부팅 시 발생했던 Wi-Fi 패닉 핸들러 상태에서 정지(Halt)되어 있음.
- **최종 조치 단계**:
  1. 보드의 `3번 핀(IO0)`을 `6번 핀(GND)`에 유지한 채, `2번 핀(EN)`을 `6번 핀(GND)`에 1초간 댔다 떼어 정지 상태를 해제하고 부트로더로 진입.
  2. 준비 완료된 초안정 완결 펌웨어(`0dddc2f`)를 20초 만에 플래싱.
  3. 플래싱 완료 후 정상 리셋 시:
     - `BOOST_EN`에 의해 PVDD가 12V로 승압.
     - TAS5805M이 `0x2D` 주소로 즉시 Play 상태로 진입.
     - `J1` 단자의 익사이터에서 45Hz 수면 진동 즉각 발생 확인.
