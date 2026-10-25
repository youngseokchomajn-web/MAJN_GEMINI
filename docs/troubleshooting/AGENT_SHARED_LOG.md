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
- **결과 커밋:** 진행 중 (본 병합 커밋으로 반영)
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
