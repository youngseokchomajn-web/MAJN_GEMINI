# MAJN 검증·계측·안전·릴리즈 관리계획

- 문서 ID: MAJN-ENG-VVR-001
- 상태: Draft for review
- 목적: 설계 검증, 물리 계측, 안전 위험, 연구 증거, 제조 릴리즈를 혼동하지 않고 추적한다.

## 1. 검증 계층

| 계층 | 질문 | 대표 방법 | 이 계층이 증명하지 않는 것 |
|---|---|---|---|
| V0 자료/설계 검사 | 파일/도면/회로가 정의와 일치하는가? | schema, DRC, geometry, ERC, review | 실제 물리 동작 |
| V1 구성품 시험 | 부품/PCB/익사이터가 동작하는가? | continuity, power rail, driver, load test | 매트리스 상부 성능 |
| V2 시스템 벤치 시험 | 조립체에서 의도한 신호/진동이 발생하는가? | electrical + accelerometer + thermal + noise | 영아 안전/진정 효능 |
| V3 사용 환경 검증 | 지정 하중/매트리스/환경에서 성능이 재현되는가? | repeatability, load variation, endurance | 임상적 유효성 |
| V4 연구/임상 | 사전 정의한 사람 대상 endpoint가 유효한가? | IRB/ethics-approved study | 다른 제품 구성/인구집단에 대한 일반화 |
| V5 적합성/규제 | 적용 법규/규격에 부합하는가? | qualified lab/technical file | 별도 intended use/variant에 대한 자동 승계 |

## 2. 요구사항 추적

각 REQ는 다음을 포함한다.
- requirement_id, source, rationale, owner, priority, product_variant
- requirement_text, measurable_acceptance_criteria, units
- verification_method: INSPECTION / ANALYSIS / DEMONSTRATION / TEST
- linked design artifacts, interfaces, risks
- test protocol ID, test report ID, evidence IDs
- status: DRAFT / REVIEW / APPROVED / VERIFIED / FAILED / BLOCKED / SUPERSEDED

안전/규제 요구사항은 수락 기준이 비어 있으면 APPROVED 상태로 승격하지 않는다. 효능 가설과 제품 기능 요구사항을 혼합하지 않는다.

## 3. 시험 기록 필수 항목

- test_id / protocol_revision / test_article_configuration_id
- hardware serial / PCB ID / PCB revision / module / antenna / actuator
- firmware commit / build environment / binary SHA-256 / runtime parameters
- mechanical assembly / mattress / contact surface / load / fixture
- instrument manufacturer/model/serial/calibration due date
- sensor type / sensitivity / range / axis / mounting / orientation
- sampling rate / filter / window / analysis code revision
- environment / temperature / humidity / power source / cable
- operator / date / location / deviations
- raw data hash / processed data hash / plot/report
- acceptance criteria source / reviewer / approval / limitations

원시 계측 파일은 수정하지 않는다. 필터링/보정/단위변환 결과는 별도 파생물로 저장하고 처리 코드를 보존한다.

## 4. MAJN 우선 검증 시퀀스

### T1 — PCB identity & electrical baseline
1. 시제품과 PCB serial/marking 촬영
2. PCB 층수/board outline/connector/major IC 확인
3. supply rails idle/start/steady/peak measurement
4. current profile at defined actuator load
5. fault shutdown and recovery
6. thermal monitoring under bounded test duration

**주의:** 기존 #0005의 성공 측정 기록은 해당 측정일의 특정 구성과 조건에만 적용한다. 동일 구성이 재현되지 않으면 기준선으로 승격하지 않는다.

### T2 — Actuator load qualification
- exact actuator MPN/nominal impedance/DCR/tolerance
- number of units and series/parallel wiring
- amplifier output waveform/frequency/amplitude/duty
- supply current, device temperature, actuator temperature
- mounting adhesive/thickness/contact condition
- repeated start/stop and extended operation
- failure/open/short/disconnected load behavior

8Ω 양산 후보는 별도 시험계획과 승인된 limit가 생기기 전까지 qualified part가 아니다.

### T3 — Mechanical clearance and assembly
- nominal stack-up and tolerance stack
- unloaded/loaded dimensions
- deflection at documented load points
- cable and connector clearance
- fastener length/thread engagement/tool access
- vibration-induced contact/buzzing/abrasion
- repeated assembly/disassembly and service access

15kg 등 하중 값은 시험 입력 후보로 취급하며 intended use와 구조 설계 근거로 검토 후 승인한다.

### T4 — Mattress/top-surface vibration
- P1~P5 positions and coordinate datum
- triaxial accelerometer type/range/calibration
- mounting method and sensor mass effect
- load/mattress/contact configuration
- sampling/filter/window/steady-state definition
- time waveform, RMS, peak, spectrum, frequency response
- repeated runs and uncertainty
- actuator command vs measured output comparison

P1의 0.05~0.25m/s² 범위는 출처와 안전/효능 근거가 확보되기 전까지 임시 시험 탐색 범위로만 취급한다. 합격 기준 또는 영아 안전 기준으로 사용하지 않는다.

### T5 — Wireless and OTA
- antenna identity and final installed routing
- distance/orientation/channel/environment
- RSSI plus packet loss/throughput/reconnect
- phone compatibility matrix
- OTA interruption/power loss/rollback/recovery
- firmware-board-module compatibility

### T6 — Durability and environmental
- cable flex/strain/vibration fatigue
- connector retention
- repeated start/stop
- power cycling and brownout
- thermal soak under bounded safe test conditions
- cleaning/liquid exposure only to defined intended-use claim and test method
- post-test inspection and functional regression

## 5. CAE 검증/상관성

CAE 보고서는 아래를 반드시 포함한다.
- solver/version/build
- geometry source hash and simplification notes
- element type, mesh size, convergence
- material source, directionality, thickness, joints/adhesive
- boundary conditions, constraints, contacts
- load magnitude/location/time/frequency
- damping assumptions
- units and coordinate frame
- numerical checks and benchmark
- correlation data and error metric
- validated domain and limitations

CAE 코드/뷰어가 존재하는 것은 solver verification이나 model validation을 의미하지 않는다. 실측과 조건이 맞지 않는 결과는 correlation evidence로 사용하지 않는다.

## 6. 안전·위험 통제

위험 로그는 hazard, hazardous situation, harm, initiating event, severity rationale, probability rationale, risk control, verification evidence, residual risk, approver를 기록한다.

최소 고려 범위:
- 전기충격/단락/과전류/과열/화재
- 배터리/USB 전원 불안정과 역전압
- BTL 출력/배선 오류/부하 단락
- 진동 과도/예기치 않은 재시작/제어 오류
- 케이블 끼임/걸림/마찰/단선
- 구조 파손/체결 풀림/부품 이탈
- 매트리스/접촉면 변형과 국부 압력
- 액체/세척/습기 노출
- RF/EMC 간섭과 무선 연결 상실
- OTA 업데이트 중단 및 안전 상태 복구
- 보호자 오사용/설정 오류/비상 중단 실패

AI 생성 FMEA는 초안이며, hazard severity/acceptability와 residual risk는 담당 전문가 및 책임자가 검토한다.

## 7. 연구 및 임상 증거 경계

- 벤치 계측은 기계적/전기적 출력에 관한 근거다.
- 관찰 기록은 통제된 연구의 효과 추정과 동일하지 않다.
- 타 제품 연구/논문/FDA 지정 또는 승인 이력은 MAJN의 성능·안전·규제 지위를 증명하지 않는다.
- 영아 대상 연구는 적절한 연구기관/IRB/윤리 및 법적 요건 검토 후 진행한다.
- 광고/투자자료의 모든 성능 주장은 claim-evidence register와 연결한다.

## 8. CI/자동화 검증 전략

### GitHub-hosted CI에 적합
- Markdown/link/CSV/JSON schema validation
- duplicate IDs and broken references
- metadata completeness
- status transition checks
- Python unit tests for lightweight validators
- existing deterministic test scripts where dependencies are available
- firmware build only if pinned toolchain and reproducible environment exist

### 전용 local/self-hosted runner가 적합할 수 있음
- EasyEDA export/GUI-dependent EDA operations
- FreeCAD native GUI/large CAD conversion
- CalculiX/large CAE
- hardware-in-loop and serial/BLE/Wi-Fi tests
- calibrated instrument acquisition

CI는 도구가 없어서 검사하지 못한 항목을 PASS로 처리하지 않는다. NOT_RUN / NOT_AVAILABLE / BLOCKED 상태를 별도로 남긴다. GitHub Actions는 least-privilege token permission, action version pinning, untrusted PR의 read-only 실행, concurrency 충돌 방지를 적용한다.

## 9. Release gate

릴리즈 후보는 다음을 포함해야 한다.
1. configuration manifest
2. approved requirements baseline
3. CAD/drawing/BOM/PCB/harness revisions
4. firmware source commit and binary hash
5. test reports and raw-data hashes
6. CAE inputs/results and limitations if used
7. risk register and residual-risk approval
8. manufacturing/inspection instructions
9. regulatory applicability and evidence
10. ECO history and superseded baseline links

미해결 P0 또는 미승인 critical risk가 있으면 릴리즈하지 않는다. 문서 검증 PASS와 제품 적합성 PASS를 혼동하지 않는다.

## 10. 변경 후 재검증 규칙

| 변경 | 최소 영향 검토 |
|---|---|
| 하우징/홀/두께/재료 | CAD, drawing, tolerance, assembly, CAE, vibration, safety |
| PCB/부품/전원 | BOM, power, thermal, EMC, firmware compatibility, safety |
| 익사이터/배선 | load, amplifier, harness, thermal, vibration, acoustic |
| 안테나/케이블/배치 | RF performance, EMC, regulatory, enclosure integration |
| 펌웨어/파라미터 | state machine, fault handling, OTA, HIL, test regression |
| 매트리스/하중/사용환경 | vibration, structural, usability, intended-use and claims |
| intended use/product variant | requirements, risk, research, regulatory, labeling, all affected tests |

