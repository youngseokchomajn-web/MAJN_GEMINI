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
