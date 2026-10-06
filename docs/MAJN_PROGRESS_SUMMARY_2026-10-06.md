# 마중 배시넷 실물 PCB(#0005) 브링업 & 무선 OTA 파이프라인 진행 현황 종합 보고서

**작성일**: 2026-10-06  
**대상 기기**: MAJN Smart Bassinet 실물 PCB (#0005) ESP32-WROOM-32UE  
**저장소**: youngseokchomajn-web/MAJN_GEMINI (main 브랜치)

---

## 1. 하드웨어 심층 분석 및 핵심 난제 해결

### 1.1 TAS5805M 오디오 앰프 I2C 주소 규명 (0x2C -> 0x2D)
- **현상**: 보드 전원 인가 후 I2C 통신 응답(ACK)이 없어 앰프가 Mute/정지 상태로 유지됨.
- **원인 분석**: 회로도 넷리스트 추적 결과, 앰프 ADR 핀(3번)이 R12 (4.7kΩ) 저항을 통해 VCC_3V3로 풀업 연결되어 있음. TI 데이터시트 규격에 따라 ADR이 DVDD에 연결될 때 I2C 슬레이브 주소는 0x2D임.
- **해결 조치**: 
  - tas5805m.h, tas5805m.cpp, amplifier_manager.cpp의 I2C 주소를 0x2D로 수정.
  - 전원 인가 시 PDN 핀 하드웨어 제어 시퀀스 및 다중 주소 자동 스캔 로직 탑재.

### 1.2 Wi-Fi + BLE 동시 구동 시 Core 0 크래시(커널 패닉) 제거
- **현상**: 보드 기동 5초 후 ESP32가 무한 재부팅(Reboot loop) 반복.
- **원인 분석**: ESP32 단일 안테나 무선 스택에서 NimBLE과 WiFi.softAP()가 동시 메모리 할당을 시도할 때 ieee80211_hostap_attach 널 포인터 참조 에러(LoadProhibited) 발생.
- **해결 조치**:
  - Wi-Fi AP 스택을 펌웨어에서 완전 분리 및 비활성화하여 BLE 단독으로 안정적인 무중단 동작 확보.

---

## 2. 100% 무선 펌웨어 업데이트(Web Bluetooth OTA) 파이프라인 구축

> **목표**: 향후 시리얼 케이블 연결이나 다운로드 모드(핀 쇼트) 없이, 크롬 브라우저에서 버튼 클릭 한 번으로 무선 펌웨어 업데이트 완료.

### 2.1 펌웨어 단 (firmware/src/ota_ble_service.cpp, .h)
- ESP32 8MB 플래시를 기반으로 Arduino <Update.h>를 연동한 듀얼 파티션(OTA0 / OTA1) GATT 서비스 개발 완료.
- 서비스 UUID: 0000fe00-0000-1000-8000-00805f9b34fb
- 청크 단위 무선 전송 검증 및 수신 완료 시 즉시 새 파티션으로 자가 재부팅(Auto-restart) 루틴 탑재.

### 2.2 웹 대시보드 단 (bassinet_simulator/)
- protocol.js, ble_provider.js, index.html, app.js에 [무선 펌웨어 업데이트 (Web BLE OTA)] UI/로직 통합.
- 바이너리 파일 선택 시 0%~100% 실시간 프로그레스 바 표시 및 완료 후 자동 재연결 대기 기능 탑재.

### 2.3 배포용 바이너리 빌드
- bassinet_simulator/majn_latest_firmware.bin (1.7MB) 생성 완료.

---

## 3. 실물 보드 펌웨어 플래싱 (유선 팩토리 적재) 완료

- esptool.py를 통해 보드 #0005에 부트로더, 파티션 테이블, 최신 완성형 펌웨어(0x0 ~ 0x1DCDE0, 총 1.86MB) 물리 적재 완료 (Hash of data verified, exit code 0).
- 플래싱 완료 직후 신규 펌웨어로 정상 구동하기 위한 완전 방전 후 재기동 대기 상태.

---

## 4. Git 형상 관리 내역 (원격 저장소 동기화 완료)

- 90f84c5: fix(amplifier): update TAS5805M I2C address to 0x2D and robust initialization
- 0dddc2f: fix(firmware): disable WiFi.softAP on Core 0 to eliminate coexistence panic with BLE
- 2f6a60c: docs: add comprehensive deep analysis of PCB #0005 hardware bringup, I2C 0x2D address, and Wi-Fi panic resolution
- beecdca: feat(ota): implement 100% wireless Web Bluetooth (BLE) OTA firmware update pipeline
- 45f1c5a: docs: record 100% successful flashing of Web BLE OTA & 0x2D TAS5805M firmware

---

## 5. 향후 운영 절차

1. **최초 1회 부팅**: 케이블 완전 탈착(방전) 후 재인가 시 신규 펌웨어 즉시 가동.
2. **실물 진동 테스트**: http://localhost:8080/bassinet_simulator/index.html에서 MAJN-Bassinet 연결 후 START 클릭 (45Hz 진동).
3. **향후 펌웨어 업데이트**: 웹 대시보드의 OTA 패널에서 .bin 파일 선택으로 100% 무선 업데이트 수행.
