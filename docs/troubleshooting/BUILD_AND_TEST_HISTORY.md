# 빌드·시험 이력

이 표는 빌드와 실제 하드웨어 시험을 별도 상태로 추적한다. 사용자 보고는 독립적으로 재실행·측정한 결과와 구분한다.

| 날짜 | 시험 ID | 커밋 | 보드/리비전 | 빌드·시험 | 결과 | 증거/비고 |
|---|---|---|---|---|---|---|
| 2026-10-25 | FW-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | esp32_full_hw 빌드 | 사용자 보고: 성공 | 빌드 로그 원문과 바이너리 SHA-256은 이 기록에서 확인되지 않음 |
| 2026-10-25 | AMP-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | 앰프 fault / I²C timeout 차단 시험 | 미실시 또는 결과 미확보 | 실제 fault injection 및 차단 시간 로그 필요 |
| 2026-10-25 | PWR-001 | [6ddf383](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/6ddf38305b7d828c41f6921ac38f06b26e14ef7b) | 미기록 | 더미 부하 전력·온도 실측 | 미확보 | 차동 Vrms, 저항값, 온도, 측정 위치 필요 |
| 2026-10-25 | VIB-001 | 미기록 | PCB #0005 관련 이전 보고, 시험 리비전 재확인 필요 | 익사이터 및 패드 상면 진동 계측 | 데이터 미확보 | BLE START 이후 익사이터 무반응을 보고한 이력은 있으나 현재 상태와 원인은 미확정 |

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
