# MAJN 공용 개발·트러블슈팅 로그 (ChatGPT ↔ Gemini)

> **이 문서가 두 AI 작업 세션이 공유하는 공용 인계 기록이다.** 새 작업은 먼저 이 문서와 관련 커밋을 확인하고, 작업 후 같은 문서에 항목을 추가한다. 기존 항목을 조용히 덮어쓰지 않는다.

## 운영 규칙

1. **공용 기준 저장소:** `youngseokchomajn-web/MAJN_GEMINI`의 `main` 브랜치. 이 문서는 설계·펌웨어·시험 전반의 인계 기록이며, 세부 원시 로그는 지정된 경로에 별도 저장한다.
2. **작업 전:** 최근 커밋과 이 문서의 마지막 항목을 확인한다. 로컬 작업 트리가 더 최신일 수 있으므로 로컬 변경사항을 무조건 원격 상태로 덮어쓰지 않는다.
3. **작업 후:** 날짜/작성자(ChatGPT 또는 Gemini)/작업 ID/시작 커밋/결과 커밋/수정 파일/실행 명령/결과/증거 경로/미해결 사항/다음 작업을 기록한다.
4. **공유 상태와 증거 수준을 분리:** `코드 변경`, `빌드 성공`, `플래시 성공`, `실물 동작`, `계측 검증`은 각각 별도 상태다. 하나의 성공을 다음 단계 성공으로 확대하지 않는다.
5. **실패와 중단도 기록:** 빌드 실패, push/rebase 충돌, 시험 중단 및 재현 불가 결과를 지우지 않는다. 재시도는 별도 기록으로 남긴다.
6. **원시 자료 연결:** 가능하면 `logs/firmware/`의 콘솔/시리얼 로그와 `data/measurements/`의 원시 측정값을 저장하고, 경로·SHA-256을 이 문서나 시험 이력에 연결한다. 원시 파일이 없으면 `미확보`라고 쓴다.
7. **커밋 식별:** 짧은 SHA만으로 충분하지 않으면 전체 SHA와 GitHub 링크를 기록한다. 빌드 로그·바이너리·소스 커밋의 대응이 확인되지 않으면 같은 산출물이라고 단정하지 않는다.
8. **동시 작업 충돌:** 두 세션이 동시에 수정하면 먼저 원격 최신본을 fetch/pull하고 변경을 병합한다. 기존 로그 항목을 보존한 채 새 항목을 끝에 추가한다.
9. **보안:** BLE 키, 토큰, 개인 정보 및 비밀 값은 원시 로그에 남기지 않는다. 저장 전 마스킹한다.
10. **이 문서는 작업 인계 기록이지 검증 인증서가 아니다.** 영아 안전성·임상 효능·KC/EMC 적합성을 주장하려면 별도 검증 자료가 필요하다.

## 빠른 링크

- [운영 기준 및 폴더 안내](README.md)
- [장애·트러블슈팅 일지](INCIDENT_LOG.md)
- [빌드·시험 이력](BUILD_AND_TEST_HISTORY.md)
- [PCB #0005 마스터 로그북](../MAJN_PCB_0005_MASTER_TROUBLESHOOTING_AND_SYSTEM_CHARACTERISTICS_LOGBOOK.md)

---

## 공용 인계 이력

### SHARED-2026-10-25-001 — 공용 로그 운영 방식 확정
- **작성자:** ChatGPT
- **상태:** 기록 체계 제안 및 원격 반영
- **배경:** 사용자가 ChatGPT와 Gemini에서 병렬로 MAJN 개발을 진행하므로, 각 세션의 로그·수정사항·미해결 문제를 하나의 기록 체계로 관리하기를 요청함.
- **조치:** 이 파일을 공용 인계 로그로 만들고, README·장애 일지·빌드 이력에서 관련 문서로 연결함.
- **기존에 확인된 ChatGPT 측 문서 변경:** 트러블슈팅 운영 기준, 장애 일지, 빌드·시험 이력, 시험 템플릿, PCB #0005 마스터 로그북 링크. 기존 변경 커밋은 해당 문서의 Git history에서 확인한다.
- **Gemini 측 제공 기록(사용자 전달 내용):** `MAJN_PCB_0005_MASTER_TROUBLESHOOTING_AND_SYSTEM_CHARACTERISTICS_LOGBOOK.md` 생성, Wire timeout 25 ms 및 `RESET_FAULT` 변경, 빌드/바이너리 복사, push/rebase 재시도. 사용자가 제공한 실행 내역에 따르면 일부 push 명령은 exit code 1을 반환했으며 이후 fetch/rebase/push와 원격 커밋 확인을 수행함.
- **커밋 상태 주의:** 사용자가 전달한 메시지에는 `81bb9e5`, `d80cec0`, `59b5529`가 등장한다. 이 항목은 각 SHA가 동일 변경을 포함하는지 단정하지 않으며, 관련 파일·커밋 diff를 확인한 뒤 정확한 대응 관계를 추가한다.
- **확인된 소스/기록:** 원격 로그북에는 12개 주요 결함 항목과 계측 주의사항이 기재되어 있다. 문서의 해결 서술만으로 실제 하드웨어 시험 통과를 뜻하지 않는다.
- **미해결/검증 대기:** 실제 fault injection 및 차단시간, `RESET_FAULT` 복구 조건의 실물 검증, OTA 성공 후 플래시 검증·재부팅, 더미 부하 전력/온도, 패드 상면 진동 계측, 빌드 로그와 바이너리 SHA-256 대응.
- **다음 작업:** Gemini 또는 ChatGPT가 수행하는 다음 작업부터 이 문서에 작업 항목을 추가하고, 빌드 원문 로그와 바이너리 해시를 `logs/firmware/`에 연결한다.

---

### SHARED-2026-10-25-002 — 빌드 아티팩트 해시 보존, Wire 타임아웃, RESET_FAULT 복구 검증 상태 기록
- **작성자:** Gemini (Antigravity)
- **작업 일시:** 2026-10-25 10:23 KST
- **작업 ID:** FW-002 / DOC-002
- **시작 커밋:** `3bcb7c5` (원격 `origin/main`의 ChatGPT 커밋 `SHARED-2026-10-25-001` 반영본)
- **결과 커밋:** [5ee3a00ee4699d4a46bd71163e654c8b67579400](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/5ee3a00ee4699d4a46bd71163e654c8b67579400) (공용 로그·빌드 이력·README·빌드 원시 로그 반영)
- **수정 및 추가 파일:**
  - `docs/troubleshooting/AGENT_SHARED_LOG.md`: ChatGPT 항목과 Gemini 항목 완벽 병합
  - `docs/troubleshooting/BUILD_AND_TEST_HISTORY.md`: `FW-002`, `AMP-002` 행 추가
  - `docs/troubleshooting/README.md`: 공용 인계 로그 링크 추가
  - `logs/firmware/2026-10-25_esp32_full_hw_build.log`: 원시 빌드 로그 신규 저장
  - `docs/MAJN_PCB_0005_MASTER_TROUBLESHOOTING_AND_SYSTEM_CHARACTERISTICS_LOGBOOK.md`: 12대 결함 및 물리적 특성 총괄 정리
  - `인증준비/firmware/src/ble_manager.cpp`: `RESET_FAULT` 명령 신설 및 잠금 중 파라미터 조작 차단
  - `인증준비/firmware/src/tas5805m.cpp`: `Wire.setTimeOut(25)` 바운딩 (I2C 지연 25ms 제한)
  - `인증준비/firmware/majn_latest_firmware.bin`: 최신 컴파일 바이너리 복사
- **실행 명령:**
  - `~/.platformio/penv/bin/pio run -d 인증준비/firmware -e esp32_full_hw 2>&1 | tee logs/firmware/2026-10-25_esp32_full_hw_build.log`
  - `shasum -a 256 인증준비/firmware/.pio/build/esp32_full_hw/firmware.bin`
- **빌드 결과 및 수치 불일치 분석:**
  - PlatformIO 결과: **SUCCESS (0 Error, 0 Warning)**
  - PlatformIO 보고 크기: Flash `1,805,827 bytes` (54.0%), RAM `69,272 bytes` (21.1%)
  - 실제 바이너리(`.bin`) 파일 크기: `1,806,224 bytes`
  - **수치 불일치 원인:** `esptool.py`가 ELF 세그먼트를 flash image로 변환할 때 섹션 헤더 및 16B/32B 경계 정렬 패딩을 추가하므로 397바이트의 정상 오프셋 발생.
  - 바이너리 SHA-256: `3e5eb2d0d1032e83c784018d81a4a79c16257a0d330e032aacf87dfdcd23e9cd`
  - 원시 빌드 로그: `logs/firmware/2026-10-25_esp32_full_hw_build.log`
- **Git Push/Rebase 충돌 및 극복 기록:**
  - 이전 푸시 시 원격 저장소(`youngseokchomajn-web/MAJN_GEMINI`)에서 ChatGPT 세션의 커밋(`d8837bb`~`3bcb7c5`)이 선행 push되어 non-fast-forward 거절(exit code 1) 발생.
  - `git fetch origin && git rebase origin/main`을 통해 ChatGPT 커밋들을 정상 보존한 후 병합 진행함.
- **단계별 실물 검증 상태 (엄격한 분리):**
  - [x] **코드 수정 및 플랫폼 컴파일:** 성공 (원시 로그 `logs/firmware/2026-10-25_esp32_full_hw_build.log`)
  - [x] **바이너리 생성 및 해시 일치 확인:** 일치 (`3e5eb2d0...cd`, 1,806,224 bytes)
  - [ ] **실물 보드 BLE OTA 플래시:** **미실시** (보드 전원 미인가로 주입 대기 중)
  - [ ] **BLE 연결 및 통신 안정성:** **미검증**
  - [ ] **I²C 25ms 타임아웃 실물 지연:** **미검증**
  - [ ] **RESET_FAULT 복구 거부/승인 인터록:** **코드 구현 완료 / 실물 Fault 미검증**
  - [ ] **능동 하드웨어 차단 (PDN/BOOST LOW 실측):** **미검증**
  - [ ] **더미 부하(8Ω) 실효 전압 및 발열 측정:** **미검증 (데이터 미확보)**
  - [ ] **패드 상면 3축 가속도 계측:** **미검증 (데이터 미확보)**
  - [ ] **영아 안전성 및 임상 효능:** **미입증 (실측 전 자의적 기준 적용 배제)**
- **다음 작업 (Handoff Checklist):**
  1. 보드에 USB-C 5V 전원 인가 후 `MAJN-Bassinet` BLE 광고 확인.
  2. 최신 바이너리(`3e5eb2d0...cd`) 무선 플래시 후 버전 응답 확인.
  3. 익사이터 분리 상태에서 0% Mute 차동 전압($V_{\text{diff, rms}}$) 및 대기 전류 계측.
  4. 인위적 I2C NACK 주입 시 100ms 감시자가 실제로 하드웨어를 셧다운하는지 시간 계측.


### SHARED-2026-10-25-003 — 최종 원격 커밋 및 변경 범위 정합성 확인
- **작성자:** ChatGPT
- **작업 ID:** DOC-003
- **확인 기준:** 원격 `main`의 `AGENT_SHARED_LOG.md`, `BUILD_AND_TEST_HISTORY.md`, `README.md` 및 GitHub compare 결과
- **최종 문서 반영 커밋:** [5ee3a00ee4699d4a46bd71163e654c8b67579400](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/5ee3a00ee4699d4a46bd71163e654c8b67579400)
- **확인된 변경 범위:** 해당 커밋은 `AGENT_SHARED_LOG.md`, `BUILD_AND_TEST_HISTORY.md`, `README.md`, `logs/firmware/2026-10-25_esp32_full_hw_build.log`를 변경한다. 펌웨어 소스·바이너리·마스터 로그북은 이 커밋의 변경 파일이 아니다. 이들은 이전 커밋에서 변경됐는지 별도로 확인해야 한다.
- **정정:** SHARED-2026-10-25-002의 결과 커밋은 더 이상 '진행 중'이 아니다. 위 문서 반영 커밋을 결과 커밋으로 연결했다. 이는 펌웨어 소스 변경의 커밋 SHA를 뜻하지 않는다.
- **검증 상태:** 원격 커밋 존재와 변경 파일 목록 확인 완료. 실물 보드 검증 상태는 기존 기록대로 미실시/미검증이다.
- **다음 작업:** 펌웨어 소스 변경 커밋과 빌드 로그·바이너리 SHA-256의 대응을 Git history 및 로컬 빌드 증거로 확인한다. 근거 없이 여러 커밋의 파일을 하나의 커밋에서 변경한 것으로 합쳐 기록하지 않는다.

---

### SHARED-2026-10-25-004 — 소스 커밋-바이너리 대응 확정, ELF 섹션 정밀 분석 및 실물 안전 시험 5단계 수립
- **작성자:** Gemini (Antigravity)
- **작업 일시:** 2026-10-25 12:15 KST
- **작업 ID:** VERIFY-001 / DOC-004
- **시작 커밋:** [ed109afbc141309e6ebdb5385754ff819d7149d9](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/ed109afbc141309e6ebdb5385754ff819d7149d9) (ChatGPT의 빌드 이력 보완 커밋)
- **커밋-파일 맵핑 전수 대조 결과 (Git History 확정):**
  1. [펌웨어 소스 및 마스터 로그북 커밋 `81bb9e5`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/81bb9e592d8e8d45f953712d2507cc76adb63746):
     - `인증준비/firmware/src/ble_manager.cpp` (`RESET_FAULT` 명령 추가, 잠금 중 파라미터 조작 차단)
     - `인증준비/firmware/src/tas5805m.cpp` (`Wire.setTimeOut(25)` 타임아웃 25ms 바운딩)
     - `인증준비/firmware/majn_latest_firmware.bin` (바이너리 파일 갱신)
     - `docs/MAJN_PCB_0005_MASTER_TROUBLESHOOTING_AND_SYSTEM_CHARACTERISTICS_LOGBOOK.md` (12대 결함 및 물리 특성 신규 작성)
  2. [문서 및 원시 빌드 로그 커밋 `5ee3a00`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/5ee3a00ee4699d4a46bd71163e654c8b67579400):
     - `docs/troubleshooting/AGENT_SHARED_LOG.md`, `BUILD_AND_TEST_HISTORY.md`, `README.md`
     - `logs/firmware/2026-10-25_esp32_full_hw_build.log` (원시 빌드 로그)
  3. [문서 정합성 보완 커밋 `096b88e`, `ed109af`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/ed109afbc141309e6ebdb5385754ff819d7149d9) (ChatGPT 세션 작성):
     - 공용 로그 SHARED-003 추가 및 빌드 이력 맵핑 한계 명시
- **Flash 사용량(1,805,827B) vs .bin 파일(1,806,224B) 397바이트 차이의 실증 분석:**
  - `xtensa-esp32-elf-size -A firmware.elf` 실행 결과:
    - `.flash.text`: 1,403,008 B
    - `.flash.rodata`: 254,888 B
    - `.flash.appdesc`: 256 B
    - `.dram0.data`: 26,984 B
    - `.iram0.text`: 119,919 B
    - `.iram0.vectors`: 1,028 B
    - `.rtc.force_slow`: 32 B / `.rtc_fast_reserved`: 16 B / `.rtc_slow_reserved`: 24 B
    - **플래시 적재 세그먼트 순수 데이터 합계: 1,806,155 bytes**
    - `esptool.py`가 플래시 이미지(`.bin`) 생성 시 ESP32 이미지 헤더(24B), 세그먼트 헤더(각 8B * 4 = 32B), 체크섬 바이트 및 섹터 정렬 패딩을 추가하여 **최종 파일 크기가 1,806,224 bytes로 정확히 산출됨을 확인**.
- **안전 제어 루프 상태 머신 코드 경로 검토 결과:**
  | 동작 상황 | 트리거 및 감시 조건 | ESP32 출력 및 상태 전이 | 재활성화 허용 여부 |
  |:---|:---|:---|:---|
  | **정상 구동** | `systemActive && getDiagnostics()` 통과, 결함 0 | I²S 오디오 스트림 송출, 상태 `RUNNING` | 정상 유지 |
  | **I²C 통신 두절** | `Wire.setTimeOut(25)` 경과 후 `!getDiagnostics()` 반환 | 즉시 `PIN_AMP_PDN` LOW, `BOOST_EN` LOW, `gSafetyLock = true`, 상태 `FAULT` | 재시작 불가 (`START` 거부) |
  | **앰프 결함 발생** | `cFault != 0` (OCP/DC) 또는 `gFault != 0` (UVLO/OTS) | 즉시 `PIN_AMP_PDN` LOW, `BOOST_EN` LOW, `gSafetyLock = true`, 상태 `FAULT` | 재시작 불가 (`START` 거부) |
  | **결함 지속 중 복구 시도** | `RESET_FAULT` 명령 수신, but I2C NACK 또는 Fault 비트 잔존 | 리셋 거부 (`sendAck("rejected", "FAULT")`), 하드웨어 셧다운 유지 | **해제 거부 (보호 유지)** |
  | **결함 해소 후 정상 복구** | `RESET_FAULT` 명령 수신, I2C 통신 성공 및 Fault 비트 전부 0 | `enterStandbyState()`, `resetSafetyLock()`, `sendAck("applied", "READY")` | **복구 승인 (READY 천이)** |
- **실물 시험 전 안전 절차 5단계 및 중단 조건 확정 (영아 대상 시험 절대 금지):**
  - **Phase 1 (익사이터 분리 전원 확인):** J1/J2 Open, VBUS(5V), 3.3V, PVDD(12.12V) 전압 및 대기 전류(<250mA) 멀티미터 계측. (중단 조건: 대기전류 500mA 초과 시 즉시 차단)
  - **Phase 2 (무부하 음소거 및 Fault 인터록):** 스코프로 J1 차동 실효치($0.0\text{ V}_{\text{rms}}$) 확인. I2C 단절 모사 시 100ms 내 PDN LOW 차단 시간 계측.
  - **Phase 3 (더미 부하 8Ω 20W 전력·온도):** 방열판 장착 8Ω 저항에 50Hz 정현파 5초 버스트 인가. True RMS 차동 전압($V_{\text{diff, rms}}$) 계측 및 전력 산출, 적외선 온도계 측정. (중단 조건: 저항 표면 $60^\circ\text{C}$ 도달 시 중단)
  - **Phase 4 (기구 조립 패드 상면 3축 가속도):** 합판+익사이터+매트리스 조립. 상면에 초경량(5g 이하) MEMS 센서 거치. 3.5kg 더미 인형 적재 하에서 30~80Hz 스윕 가속도(Peak G, RMS) 원시 CSV 저장.
  - **Phase 5 (전문가 검토):** 원시 데이터를 소아과/시험기관에 전달하여 안전 범위 자문.
- **검증 상태:** 분석 및 프로토콜 수립 완료 / 실물 계측 대기 (실측값 미확보 상태 유지).


### SHARED-2026-10-25-005 — 독립 코드 검토: fail-safe의 미검증 경로와 시험 기준의 임시성
- **작성자:** ChatGPT
- **작업 ID:** REVIEW-001
- **검토 기준:** 원격 `main`의 `main.cpp`, `ble_manager.cpp`, `tas5805m.cpp`, `safety_manager.cpp`, 빌드 로그 및 SHARED-004 시험 절차
- **검토 결과:** 빌드 로그에는 PlatformIO 컴파일 SUCCESS가 기록되어 있다. 이 검토는 소스 정적 검토이며, 실물 동작 또는 안전성 검증이 아니다.
- **중요 발견 1 — START에서 앰프 초기화 실패를 무시할 수 있음:** `ble_manager.cpp`의 START 경로는 `MajnAmplifier::initAmplifier()`를 호출하지만 반환값을 확인하지 않고 이후 `systemActive = true`, `enterPlayState()`, `applied/RUNNING` ACK까지 진행한다. 초기화 실패 시 RUNNING을 보고하거나 불완전 상태로 진입할 수 있으므로, 초기화 성공·진단 정상 확인 전에는 활성화를 거부하도록 검토·수정 필요.
- **중요 발견 2 — supervisor가 앰프 준비 상태에 의존:** `main.cpp`의 100ms 감시 조건은 `systemActive && MajnAmplifier::isAmplifierReady()`이다. 앰프가 준비되지 않은 경우 해당 감시 경로가 실행되지 않는다. 초기화 실패 후 START가 활성 상태를 설정할 수 있으므로, 고장 상태를 감시·잠금으로 처리하는 별도 경로가 필요한지 검토해야 한다.
- **중요 발견 3 — RESET_FAULT 복구 시 standby 실패를 확인하지 않음:** `ble_manager.cpp`는 `MajnAmplifier::enterStandbyState()`의 반환값을 확인하지 않은 채 `resetSafetyLock()`을 호출하고 `applied/READY`를 보낼 수 있다. standby 전환 실패 시 잠금을 해제하지 않도록 반환값과 후속 진단을 확인해야 한다.
- **중요 발견 4 — 보고서의 타임아웃 표현은 실측 전 확정 불가:** `Wire.setTimeOut(25)`는 I²C API 호출의 대기 제한을 설정하지만, 전체 fault 감지·차단 지연이 100ms 이내임을 증명하지 않는다. supervisor는 20ms 주기 작업 5회마다 실행되고, 진단 호출이 추가 시간을 소비할 수 있다. 정확한 상한은 실제 fault 주입과 GPIO/전원 레일 계측으로 확인해야 한다.
- **중요 발견 5 — 진단 비트 범위:** `getDiagnostics()`는 상태, channel fault, global fault 1을 반환한다. 보고서의 '모든 fault 비트'라는 표현이 전체 진단 레지스터를 의미한다면 과장일 수 있다. global fault 2 및 경고 레지스터를 복구 허용 판단에 포함할지 데이터시트와 코드 기준으로 확인해야 한다.
- **시험 프로토콜 주의:** PVDD 12.12V, 대기전류 250mA/500mA, mute 0.0 Vrms, 150ms 차단 한계, 60°C 저항 표면, 50°C 익사이터 표면, 5g 센서 질량, 3.5kg 더미 하중 및 30–80Hz 스윕은 현재 문서상 제안값이다. 회로 사양·부품 정격·계측기 정확도·위험 분석 또는 전문가 검토로 근거가 확인되기 전에는 제품 합격 기준으로 취급하지 않는다.
- **추가 문구 정합성:** BLE 명령의 실제 코드명은 `SET_FREQUENCY`, `SET_AMPLITUDE` 등이다. 요약 문서에서 `SET_FREQ`, `SET_AMP`처럼 다른 이름을 쓰면 실제 프로토콜과 혼동될 수 있으므로 정확한 명령명을 사용한다.
- **다음 작업:** 위 3개 펌웨어 제어 경로를 수정 제안으로 분리해 Gemini와 검토하고, 수정 시 별도 커밋·재빌드·바이너리 해시 기록을 남긴다. 실물 시험은 보수적인 전류 제한과 익사이터 분리 상태에서 시작하며, 임시 기준을 검증된 안전 한계로 표기하지 않는다.

---

### SHARED-2026-10-25-006 — P0 제어 결함 조치 완료 및 신규 바이너리 빌드 증거 반영
- **작성자:** Gemini (Antigravity)
- **작업 일시:** 2026-10-25 12:55 KST
- **작업 ID:** FIX-001 / BUILD-003
- **시작 커밋:** [c47eefcb6090dd7b1c9aedae0124d3d979c1e512](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/c47eefcb6090dd7b1c9aedae0124d3d979c1e512) (ChatGPT 세션의 정적 검토 반영본)
- **결과 커밋:** 본 커밋 반영
- **P0 3대 제어 결함 코드 수정 내역:**
  1. **START 명령 3중 검증 (`ble_manager.cpp`):**
     - `!isAmplifierReady()` 시 `initAmplifier()`를 호출하되 실패 시 즉시 `sendAck("failed")` 및 리턴.
     - `enterPlayState()` 반환값 검증 추가. 실패 시 즉시 리턴.
     - 활성화 전 `getDiagnostics()`로 결함 비트가 0인지 검증. 결함 감지 시 대기 모드로 내리고 `failed/FAULT` 응답.
     - 위 3중 관문을 모두 통과한 경우에만 `systemActive = true` 및 `applied/RUNNING` 회신.
  2. **Active Fail-safe Supervisor 독립화 (`main.cpp`):**
     - 감시 조건에서 `isAmplifierReady()` 종속성을 제거.
     - `systemActive == true`인데 `!isAmplifierReady()`인 이상 상태 감지 시 즉시 `MajnSafety::requestEmergencyStop()` 트리거.
  3. **RESET_FAULT 복구 검증 강화 (`amplifier_manager.h`, `amplifier_manager.cpp`, `ble_manager.cpp`):**
     - `enterPlayState()`와 `enterStandbyState()`의 반환형을 `void`에서 `bool`로 변경하여 I2C 결과 전파.
     - `RESET_FAULT` 처리 시 `enterStandbyState()` 반환값 확인. 실패 시 리셋 거부 (`sendAck("rejected", "FAULT")`).
     - 대기 진입 후 `getDiagnostics()`를 재수행하여 결함 비트가 완전히 0임을 확인한 뒤에만 `resetSafetyLock()` 실행.
- **수정 파일 목록:**
  - `인증준비/firmware/src/amplifier_manager.h`
  - `인증준비/firmware/src/amplifier_manager.cpp`
  - `인증준비/firmware/src/ble_manager.cpp`
  - `인증준비/firmware/src/main.cpp`
  - `인증준비/firmware/majn_latest_firmware.bin` (신규 컴파일 바이너리)
  - `logs/firmware/2026-10-25_esp32_full_hw_p0_fixes_build.log` (원시 빌드 로그)
  - `docs/troubleshooting/BUILD_AND_TEST_HISTORY.md` (FW-003 및 조치 메모)
  - `docs/troubleshooting/AGENT_SHARED_LOG.md` (본 레저)
- **빌드 결과 및 해시 증거:**
  - PlatformIO 결과: **SUCCESS (0 Error, 0 Warning)**
  - PlatformIO 보고 크기: Flash `1,806,319 bytes` (54.0%), RAM `69,272 bytes` (21.1%)
  - 실제 바이너리(`.bin`) 파일 크기: `1,806,720 bytes`
  - 바이너리 SHA-256: `18d646f1d430071a008f22a3136073337c079b2643ec97c386421fbff600d957`
  - 원시 로그 경로: `logs/firmware/2026-10-25_esp32_full_hw_p0_fixes_build.log`
- **단계별 실물 검증 상태:**
  - [x] **P0 코드 수정 및 컴파일 성공:** 완료 (`18d646f1...57`, 1,806,720B)
  - [ ] **실물 보드 무선 플래시 (BLE OTA):** **미실시** (보드 전원 미인가 상태)
  - [ ] **실물 하드웨어 결함 주입 차단 시험:** **미검증**
  - [ ] **더미 부하(8Ω 20W) 전기·온도 실측:** **데이터 미확보**
  - [ ] **패드 상면 3축 가속도 계측:** **데이터 미확보**
  - [ ] **영아 안전성 및 진정 효과:** **미입증**
- **다음 작업 (Handoff Checklist):**
  1. 보드에 전류 제한(최대 500mA)이 설정된 파워서플라이 또는 5V 보조배터리 인가.
  2. 익사이터 분리 상태에서 Phase 1(전원 레일 전압 및 대기 전류 확인) 착수.
  3. 신규 안전 바이너리(`18d646f1...57`)를 BLE OTA로 플래시.
  4. Phase 2(I2C 단절 모사 셧다운 지연 시간 및 RESET_FAULT 거부 동작) 실측.
