# MAJN Smart Bassinet Firmware Release Notes - v0.1.0-mvp

> **기준 펌웨어 버전 (Baseline Freeze)**: `c63e60a`  
> **릴리스 일시**: 2026-11-01  
> **기준 브랜치**: `feature/phone-wifi-control`  
> **빌드 환경**: PlatformIO (`esp32_wifi_phone`)  
> **바이너리 파일**: `firmware.bin` (크기: 1,911,536 bytes)  
> **SHA-256 Checksum**: `da97b96e89b2f267c9c4b9d054c0456e1b4bd40eba220bd630815ed60452ce7c`  

---

## 1. 릴리스 개요

본 `v0.1.0-mvp` 릴리스는 마중(MAJN) 스마트 배시넷의 1단계 MVP 실물 Bring-up 및 2R 시연 검증을 위한 **공식 소프트웨어 기준선(Baseline Freeze)**입니다.

단순한 기능 구현을 넘어, 실제 영아용 하드웨어 적용에 필수적인 **OTA 상호 배제(Flash 오염 방지)**, **백그라운드 세션 유지(화면 잠금 시 진동 지속)**, **결함 발생 시 비상 정지 및 FAULT 래칭(하드웨어 보호)**, **부팅 팝노이즈 억제 및 과열 디레이팅(앰프 보호)** 등 4대 핵심 안정성 아키텍처가 완전하게 반영되었습니다.

---

## 2. 핵심 개선 4대 아키텍처

### 1) OTA 상호 배제 (Cross-Transport Mutual Exclusion)
- **적용 모듈**: `ota_ble_service.cpp`, `wifi_manager.cpp`
- **내용**: BLE OTA와 Wi-Fi HTTP Web OTA(`/update`)가 동시에 요청될 경우 상호 원자적 락(`gOtaRunning`)을 통해 후속 요청을 즉시 거부(`HTTP 409 Conflict` 또는 `BLE OTA_BUSY`).
- **효과**: 동시 플래시 기록 시도에 따른 ESP32 플래시 파티션 손상 및 벽돌(Brick) 위험 100% 원천 차단.

### 2) 백그라운드 달래기 세션 안정성 (Background Session Stability)
- **적용 모듈**: `ble_manager.cpp`, `system_controller.cpp`
- **내용**: 스마트폰 화면 잠금, 슬립 모드 진입, 또는 일시적 BLE RSSI 저하로 인한 연결 해제 시에도 설정된 달래기 세션 타이머가 유지되어 진동이 중간에 급격히 꺼지는 문제 해결.
- **안전 정책**: 연결 단절과 무관하게 타이머 만료 시 20ms당 0.005f의 부드러운 감쇄 램프다운(`STOPPING` $\rightarrow$ `READY`) 적용. 사용자의 명시적 `STOP` 및 하드웨어 결함에 의한 `ESTOP`은 상시 최우선 순위로 즉각 실행.

### 3) 하드웨어 안전 감독 및 FAULT 래칭 (Universal Fault Latch & E-STOP)
- **적용 모듈**: `main.cpp`, `system_controller.cpp`
- **내용**: `START` 명령 진입 시 TAS5805M I2C 통신, 전원 레일, 결함 핀 상태를 실시간 전수 진단. 결함 감지 시 즉시 비상 정지(`stopImmediately()`)를 발동하고 시스템을 `FAULT` 상태로 영구 래칭.
- **복구 정책**: 하드웨어 결함이 물리적으로 완전히 해소되기 전에는 `RESET_FAULT` 명령이 거부되며, 재시작 시도 시 결함 은폐(Masking) 없는 안전 인터록 유지.

### 4) 앰프 보호 및 열화 방지 (Pop-noise Suppression & OTW Derating)
- **적용 모듈**: `tas5805m.cpp`, `amplifier_manager.cpp`
- **내용**: TAS5805M `begin()` 구동 시 최종 상태를 `STANDBY(Hi-Z)` 모드로 확정하여 전원 투입 시 진동판 퍽 소리(Pop-noise) 및 돌발 진동을 완전히 제거.
- **과열 보호**: 100ms 주기 Supervisor가 TAS5805M 다이 과열 경고(OTW, 135°C)를 감시하여, 감지 즉시 진동 출력을 50% 강제 디레이팅하고 신규 명령 진폭을 상한선으로 캡(Cap)핑.

---

## 3. 검증 통과 기록 (100% Pass)

| 검증 스위트 | 검증 대상 | 결과 | 비고 |
|---|---|---|---|
| **컴파일 검증** | PlatformIO `esp32_wifi_phone` | **SUCCESS** | 0 Error, 0 Warning |
| **단위/상태머신 테스트** | `tools/test_command_parser.py` | **92 / 92 PASSED** | JSON/경계값/ESTOP/OTA/디레이팅 전건 통과 |
| **전기적 하드웨어 규칙** | `tools/verify_hardware_review.py` | **21 / 21 PASSED** | 넷리스트/BOM/USB-C 5.1k/부스트 12.45V 전건 통과 |
| **제조 패키지 검증** | `tools/verify_mfg_package.py` | **5 / 5 PASSED** | 4층 스택업/FPT-CPL 3-Way 일치/13.5mm 여유 검증 |
| **원격 동기화** | `origin/feature/phone-wifi-control` | **0 Conflicts** | HEAD 커밋 `c63e60a` 일치 |

---

## 4. 하드웨어 환경 및 플래시 주의사항 (절대 준수)

> [!CAUTION] **PCB #0005 물리 제약 사항**
> 1. **[물리 버튼 전무]**: PCB #0005 보드에는 BOOT, EN 버튼이 일체 없습니다. 버튼 누름 가이드를 수행하지 마십시오.
> 2. **[시리얼 플래시 불가]**: CP2102 헤더는 TX, RX, GND만 연결되어 있어 DTR/RTS 리셋 회로가 없습니다. 유선(`esptool`) 다운로드는 불가능하며, **오직 무선 OTA(BLE OTA 또는 Wi-Fi HTTP /update)로만 펌웨어 업데이트가 가능**합니다.

### 무선 OTA 배포 명령 (터미널 절대 경로 실행)
```bash
# 1) Wi-Fi HTTP OTA 업로드 (권장)
python3 /Users/youngseok/Desktop/majn/tools/run_wifi_ota.py

# 2) BLE GATT OTA 업로드 (대체 경로)
python3 /Users/youngseok/Desktop/majn/tools/run_ble_ota.py
```

---

## 5. 바이너리 무결성 검증

```bash
cd /Users/youngseok/Desktop/majn/release/v0.1.0-mvp
shasum -a 256 -c SHA256SUMS
# 출력 결과: firmware.bin: OK
```
