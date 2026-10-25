# 빌드·시험 이력

이 표는 빌드와 실제 하드웨어 시험을 별도 상태로 추적한다. 사용자 보고는 독립적으로 재실행·측정한 결과와 구분한다.

| 날짜 | 시험 ID | 커밋 | 보드/리비전 | 빌드·시험 | 결과 | 증거/비고 |
|---|---|---|---|---|---|---|
| 2026-10-25 | FW-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | esp32_full_hw 빌드 | 사용자 보고: 성공 | 빌드 로그 원문과 바이너리 SHA-256은 이 기록에서 확인되지 않음 |
| 2026-10-25 | FW-002 | [81bb9e5](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746) | PCB #0005 | esp32_full_hw 빌드 | **컴파일 성공 (검증 완료)** | 로그: `logs/firmware/2026-10-25_esp32_full_hw_build.log`<br/>바이너리 SHA-256: `3e5eb2d0...cd`<br/>크기: Flash 1,805,827B / .bin 1,806,224B |
| 2026-10-25 | FW-003 | 본 커밋 반영 | PCB #0005 | P0 fail-safe 3대 결함 수정 및 재컴파일 | **컴파일 성공 (검증 완료)** | 로그: `logs/firmware/2026-10-25_esp32_full_hw_p0_fixes_build.log`<br/>바이너리 SHA-256: `18d646f1...57`<br/>크기: Flash 1,806,319B / .bin 1,806,720B |
| 2026-10-25 | AMP-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | 앰프 fault / I²C timeout 차단 시험 | 미실시 또는 결과 미확보 | 실제 fault injection 및 차단 시간 로그 필요 |
| 2026-10-25 | AMP-002 | [81bb9e5](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746) | PCB #0005 | I2C 25ms 타임아웃 & RESET_FAULT | 코드 구현 완료 / 실물 미실시 | 보드 전원 인가 후 실물 인터록 검증 대기 |
| 2026-10-25 | PWR-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | 더미 부하 전력·온도 실측 | 미확보 | 차동 Vrms, 저항값, 온도, 측정 위치 필요 |
| 2026-10-25 | VIB-001 | 미기록 | PCB #0005 관련 이전 보고, 시험 리비전 재확인 필요 | 익사이터 및 패드 상면 진동 계측 | 데이터 미확보 | BLE START 이후 익사이터 무반응을 보고한 이력은 있으나 현재 상태와 원인은 미확정 |

| 2026-10-25 | FW-002 | [81bb9e5](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746) | PCB #0005 대상, 실제 시험 리비전 미기록 | Wire timeout 25 ms / RESET_FAULT 코드 반영 | 원격 소스 변경 확인; 빌드 로그 원문 미확보 | 로그북에는 빌드 SUCCESS와 메모리 수치가 기록되어 있으나, 실행 기록상 빌드 대기/바이너리 복사 후 push 재시도 로그가 있어 동일 커밋·바이너리의 빌드 산출물 연결은 추가 확인 필요 |
| 2026-10-25 | SAFE-002 | [81bb9e5](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746) | PCB #0005 대상, 실측 미확인 | RESET_FAULT / Safety Lock 복구 시험 | 하드웨어 시험 결과 미확보 | I²C 정상·fault 해소·fault 잔류·통신 실패 조건별 ACK와 출력 차단 상태를 기록해야 함 |

> **바이너리 일치성 주의:** 로그북의 PlatformIO Flash 수치(1,805,827 bytes)와 대화에 보고된 다른 빌드 수치(1,805,443 bytes), 바이너리 파일 크기(1,806,224 bytes)는 서로 다른 산출물일 수 있다. 빌드 원문 로그와 해당 바이너리 SHA-256이 연결되기 전에는 같은 빌드의 수치로 합치지 않는다.

## 각 시험에서 반드시 추가할 필드
- 시작 시각 / 종료 시각 / 시험자
- Git commit SHA / 바이너리 SHA-256 / 빌드 명령과 도구 버전
- PCB 보드 번호 / PCB 리비전 / 주요 부품 리비전
- 전원 공급 장치, 전압, 전류 제한, 배선, 연결 부하
- 시험 목적 / 기대 결과 / 합격 기준
- 실제 관측 결과 / 실패 코드 / 차단까지의 시간
- 원시 로그 경로와 파일 SHA-256
- 계측기 모델·범위·정확도, 센서 부착 위치·방향·샘플링 조건
- 판정(통과/실패/중단/미실시)과 근거
- 후속 조치와 담당자

## 바이너리 해시 생성 예시
macOS/Linux에서 로컬 바이너리의 SHA-256을 기록하려면:

~~~bash
shasum -a 256 majn_latest_firmware.bin
~~~

빌드 로그를 파일로 보존하는 예:

~~~bash
pio run -e esp32_full_hw 2>&1 | tee logs/firmware/$(date +%F)_esp32_full_hw_build.log
~~~

위 명령은 예시다. 실제 프로젝트에서 PlatformIO 환경 이름과 실행 위치를 확인한 뒤 사용한다.


## 기록 정합성 보완 — 2026-10-25

- [문서 및 원시 빌드 로그 반영 커밋 `5ee3a00`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/5ee3a00ee4699d4a46bd71163e654c8b67579400)은 이 파일, 공용 인계 로그, README 및 `logs/firmware/2026-10-25_esp32_full_hw_build.log`를 반영한다.
- [펌웨어 소스 및 마스터 로그북 커밋 `81bb9e5`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746)는 `ble_manager.cpp` (RESET_FAULT), `tas5805m.cpp` (Wire 타임아웃 25ms), `MAJN_PCB_0005_MASTER_TROUBLESHOOTING_AND_SYSTEM_CHARACTERISTICS_LOGBOOK.md`를 반영한 펌웨어 소스 커밋이다.
- 보고된 빌드 바이너리와 배포용 바이너리의 SHA-256은 `3e5eb2d0d1032e83c784018d81a4a79c16257a0d330e032aacf87dfdcd23e9cd`이다.
- **Flash 사용량 vs .bin 크기 차이의 기술적 원인 실증**:
  - `xtensa-esp32-elf-size -A`로 `firmware.elf`의 플래시 로드 섹션을 전수 확인한 결과: `.flash.text`(1,403,008B) + `.flash.rodata`(254,888B) + `.flash.appdesc`(256B) + `.dram0.data`(26,984B) + `.iram0.text`(119,919B) + `.iram0.vectors`(1,028B) + `.rtc.force_slow`(32B) + `.rtc_fast_reserved`(16B) + `.rtc_slow_reserved`(24B) = **1,806,155 bytes**.
  - `esptool.py`가 플래시 이미지 생성 시 ESP32 이미지 헤더(24B) 및 세그먼트 헤더(각 8B)와 섹터 정렬 패딩을 추가하여 최종 `.bin` 크기가 **1,806,224 bytes**가 됨. PlatformIO 콘솔에 표시되는 1,805,827 bytes는 PlatformIO의 내부 집계 기준(일부 IRAM/RTC 영역 제외 등)에 따른 수치 차이임이 실증 분석됨.
- 위 커밋은 기록·증거 파일 반영이며, 실물 보드 플래시, BLE, 앰프 출력, 차단시간, 전력·온도 또는 패드 상면 진동의 실측 통과를 의미하지 않는다.


## 정적 코드 검토 메모 — REVIEW-001 (2026-10-25)

공용 인계 로그의 [SHARED-2026-10-25-005](AGENT_SHARED_LOG.md)에 기록한 정적 검토 결과를 반영한다.

- START 경로에서 앰프 초기화 반환값을 무시할 수 있음: 실패 후에도 RUNNING ACK가 나갈 가능성.
- supervisor 감시가 `systemActive && isAmplifierReady()` 조건에 묶여 있어 앰프 미준비 상태의 오류 감시가 빠질 가능성.
- RESET_FAULT 경로에서 `enterStandbyState()` 반환값을 확인하지 않고 safety lock을 해제할 가능성.
- 25ms I²C timeout + 약 100ms supervisor 주기만으로 전체 차단시간 상한을 보장할 수 없음. fault injection 및 핀/레일 계측 필요.
- 시험 절차에 적힌 전압·전류·온도·가속도·하중 기준은 회로 사양과 위험 분석으로 검증되기 전까지 **임시 시험 제안값**이며, 제품 합격 기준이나 영아 안전 한계가 아니다.

**판정:** 빌드 성공과 별개로, 위 코드 경로 검토와 필요한 수정·재빌드가 끝나기 전에는 fail-safe 로직을 실물 시험 통과 또는 안전 보장으로 간주하지 않는다. 현재 하드웨어 실측 상태는 미검증이다.

## P0 제어 결함 조치 완료 메모 — FIX-001 (2026-10-25)

ChatGPT 세션의 정적 검토(REVIEW-001)에서 지적된 3대 P0 제어 결함을 소스 코드에서 전면 수정하고 컴파일 검증을 완료함:
1. **START 경로 검증 강화:** `ble_manager.cpp`에서 `initAmplifier()`, `enterPlayState()`, `getDiagnostics()` 3중 반환값을 모두 검증. 하나라도 실패하면 `systemActive` 활성화를 거부하고 `failed` 응답 회신.
2. **Supervisor 감시 독립화:** `main.cpp`에서 `isAmplifierReady()`를 필수 전제로 두지 않고, `systemActive == true`인데 `!isAmplifierReady()`인 이상 상태 감지 시 즉각 비상 정지(ESTOP) 트리거.
3. **RESET_FAULT 복구 검증 강화:** `ble_manager.cpp`에서 `enterStandbyState()` 반환값을 확인하고, 대기 상태 진입 후 앰프 진단이 완전히 정상(clean)인지 재확인한 뒤에만 `resetSafetyLock()` 허용.
- **빌드 아티팩트:** `logs/firmware/2026-10-25_esp32_full_hw_p0_fixes_build.log` (Flash 1,806,319B / .bin 1,806,720B, SHA-256 `18d646f1...57`).
- **실물 시험 상태:** 코드 수정 및 플랫폼 컴파일 완료 / 실물 보드 플래시 및 결함 주입 실측 대기.


## 후속 정적 재검토 — REVIEW-002 (2026-10-25)
공용 인계 로그의 SHARED-2026-10-25-007에 맞춘 추가 검토 항목이다. **소스 정적 검토이며, 수정·빌드·실물 시험 완료 기록이 아니다.**

- P0 후보: PDN LOW 후 `gAmpReady` 상태 불일치로 RESET_FAULT 복구가 막힐 수 있음.
- P0 후보: BLE 콜백과 주기적 감독 태스크가 앰프 I²C를 직렬화 없이 접근할 가능성.
- P0 후보: `setTarget()`의 현재 진폭 즉시 변경으로 소프트 램프가 우회됨.
- P0 후보: OTA 중 START 등 출력 명령이 허용될 수 있음.
- P0 후보: I²S 준비 상태 및 태스크 생성 성공 여부가 READY/START의 전제조건이 아님.
- P1 후보: OTA 중복 BEGIN, 전송 길이 불일치, 연결 해제·중단 복구, 이미지 무결성/권한 검증.
- P1 후보: ISR에서 일반 하드웨어 제어/로그 실행, IMU 설정·읽기 결과 무시, STOP의 무조건 READY ACK, REBOOT의 선행 안전 정지 부재.
- P1 후보: 공유 상태 데이터 경쟁, I²S 부분 초기화 정리, START 입력 검증 차이, SET_PRESET의 실제 파형 미반영 가능성, 진단 레지스터 범위 부족.
- 부팅 시 BOOST 활성화 및 앰프 초기화 순서가 fail-safe 기본 상태와 일치하는지 재검토 필요.
- SHARED-006의 “0 Warning” 주장과 이전 검토의 ADC/I²S deprecation 경고 기록이 충돌하므로 원시 빌드 로그를 기준으로 정정한다.
- OTA `Update.end(true)`의 실제 의미는 사용 중인 ESP32 Arduino core 버전 문서/소스로 확인하고, 별도로 예상 크기와 수신 크기 일치를 강제한다.

### 미실시 검증
실물 보드 플래시, 전원 레일/차단시간 계측, I²C/IMU/I²S 고장 주입, OTA 중단·잘못된 이미지, 패드 상면 가속도 측정은 여전히 미검증이다. 이 기록은 펌웨어 수정 완료나 안전성 입증을 뜻하지 않는다.


## 추가 제어흐름 점검 — REVIEW-003 (2026-10-25)
공용 로그 SHARED-2026-10-25-008과 연결한다. 정적 검토 후보이며 수정/빌드/실물 검증 완료가 아니다.

- RUNNING 중 START 재호출이 실패할 때 기존 `systemActive`를 정리하지 않을 가능성.
- BLE 연결 해제/heartbeat timeout은 `requestSafeStop()`을 호출하나, 앰프/BOOST의 직접 차단 및 실제 잔류 출력시간은 실측되지 않음.
- OTA 콜백과 일반 제어의 동시 실행/상태 직렬화가 필요함.
- `initAmplifier()`에서 진단 반환값을 무시할 수 있음.
- Spread Spectrum 레지스터 쓰기 결과 및 PLAY 진입 전 FAULT_CLEAR 실패가 정상 흐름으로 이어질 수 있음.
- 볼륨 master/CH1/CH2 순차 쓰기 중 부분 실패 처리 필요.
- 텔레메트리 목표 주파수/소프트웨어 진폭을 물리 실측값으로 오해하지 않도록 정의 필요.
- PID 호출/피드백 적용이 확인되지 않으므로 폐루프 제어라는 주석은 구현과 대조해야 함.
- I²C 통신 복구 후 재초기화·진단·출력 허용 순서를 명시해야 함.

시험 항목: RUNNING 중 START 재호출 고장, BLE 단절, OTA 동시 명령, 부팅 진단 실패, 볼륨 레지스터 부분 실패.


## 추가 제어 루프·OTA 경계 점검 — REVIEW-004 (2026-10-25)
공용 인계 로그 SHARED-2026-10-25-009에 대응한다. 정적 검토 후보이며, 코드 수정·빌드·하드웨어 검증 완료가 아니다.

- 정지 상태에서 `tickControlLoop()`가 20ms마다 `enterStandbyState()`를 반복 호출할 수 있어, READY 상태의 불필요한 I²C 쓰기/버스 점유를 측정한다.
- OTA_BEGIN에서 양수 크기만 검사하고, 누적 수신량이 예상 크기를 넘는지와 최대 이미지/파티션 크기를 쓰기 전에 검사하지 않는 경로가 있다.
- OTA_END/ABORT/쓰기 실패 후 OTA 세션 카운터와 상태 초기화가 일관적인지 확인한다. 진행률 계산의 0 분모 및 100% 초과도 방어한다.
- STOP은 앰프 standby 반환값을 확인하지 않고 READY/applied를 반환한다. ACK는 요청 수락과 실제 하드웨어 정지 결과를 구분해야 한다.
- ISR에서 호출되는 하드웨어 셧다운 경로에 일반 함수/로그가 포함될 수 있다. PDN/BOOST 차단 순서 및 핀 지연은 실측하지 않았다.
- START의 주파수 범위 검증은 개별 SET 명령과 다르다. 공통 입력 검증 및 범위 밖 값의 명시적 거부가 필요하다.
- READY 상태의 설정 명령 허용 정책과 앰프 ready 상태/PDN 상태의 의미를 분리해서 정의한다.

시험 계획: READY 60초 동안 standby I²C 호출 수 측정; OTA 예상 크기보다 짧거나 긴 전송, 파티션 초과, 중복 BEGIN, ABORT 후 재시도; START 범위 초과 입력; STOP/ESTOP/REBOOT 시 PDN·BOOST_EN과 패드 상면 잔류 진동 계측.

이 검토는 소스 정적 점검에 기반한다. 빌드 성공, 실제 보드 검증, 안전성 입증을 의미하지 않는다.


## 빌드 환경·부팅 시퀀스·텔레메트리 점검 — REVIEW-005 (2026-10-25)
공용 로그 SHARED-2026-10-25-010에 대응한다. 정적 검토 후보이며, 수정/빌드/실물 시험 완료가 아니다.

- `platformio.ini` 기본 환경은 `esp32_ble_test`이며 `MAJN_BLE_ONLY_TEST=1`을 정의한다. 릴리스 바이너리는 `esp32_full_hw`를 명시적으로 빌드하고 환경명·파티션·해시를 기록한다.
- 부팅 시 IMU 초기화 성공 여부와 I²S 준비 상태를 확인하기 전에 BOOST가 켜지고 앰프 초기화가 진행된다. 초기화 실패 시 전력단이 안전 기본값에 머무는지 검증한다.
- BLE-only 모드의 가상 IMU 기준값과 실제 센서 측정값이 텔레메트리/UI에서 구분되는지 확인한다.
- `activeStateStartTime`이 START 처리와 제어 태스크 시작 시점 양쪽에서 갱신된다. 초기화/START 경합 시 런타임 제한 타이머 기준이 유지되는지 시험한다.
- OTA 이미지가 현재 보드의 파티션 구성과 빌드 환경에 맞는지 확인한다. OTA 성공 응답만으로 이미지의 실제 부팅 가능성을 단정하지 않는다.

검증 계획: 기본 `pio run`과 `pio run -e esp32_full_hw` 산출물 비교; IMU/I²S/앰프 초기화 실패 주입; 가상 센서 표시 검증; 타이머 경합 시험. 실물 시험은 아직 미실시다.
