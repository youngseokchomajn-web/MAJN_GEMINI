# MAJN 예상 이슈·충돌·리스크 관리대장

- 문서 ID: MAJN-ENG-RISK-001
- 상태: Open working register
- 원칙: 이 문서는 설계 승인 기록이 아니다. 모든 리스크는 증거, 소유자, 조치, 잔여 위험을 가진다.

## 1. 상태 및 우선순위 규칙

상태:
- `FACT_CONFIRMED`: 지정된 원본/실물/시험 증거로 사실 확인
- `DISCREPANCY_IDENTIFIED`: 자료 간 충돌 확인, 원인 미해결
- `ENGINEERING_ACTION_OPEN`: 설계/문서/프로세스 조치 필요
- `VERIFICATION_PENDING`: 시험 또는 독립 검토 대기
- `HUMAN_APPROVAL_PENDING`: 책임자 승인 대기
- `BLOCKED`: 선행 정보/장비/외부 판단 부족
- `CLOSED`: 조치와 검증 및 승인 완료
- `SUPERSEDED`: 새 리비전으로 대체, 이력 보존

우선순위:
- P0: 잘못된 설계/제조/안전 판단 또는 기준선 오염 가능성이 있어 관련 릴리즈 차단
- P1: 설계 통합/시험/인증 일정에 큰 영향
- P2: 운영 효율/문서 품질/후속 제품에 영향
- P3: 개선 항목

각 리스크는 발생 가능성·영향·검출 가능성을 별도 기록한다. 근거가 없으면 숫자 RPN을 임의로 부여하지 않는다.

## 2. 초기 충돌 및 리스크

| ID | 우선순위 | 영역 | 예상 이슈/충돌 | 영향 | 예방/검증 조치 | 종료 증거 | 초기 상태 |
|---|---|---|---|---|---|---|---|
| RSK-001 | P0 | PCB identity | #0005 층수가 감사 본문 4-layer, 자산 대장 2-layer로 불일치 | 잘못된 보드/제조 데이터 연결 | 실물 실크/사진/거버/원본 프로젝트/제조 기록 대조 | board identity record + source hash | DISCREPANCY_IDENTIFIED |
| RSK-002 | P0 | Exciter | 21.6Ω과 24.8Ω 기록 차이, 시료/측정 조건 불명확 | 앰프 전류·출력·발열 판단 오류 | 원시 CSV/시료 ID/채널/직렬 수/리드 보정/측정일 대조 | signed measurement reconciliation | DISCREPANCY_IDENTIFIED |
| RSK-003 | P0 | RF/Regulatory | IF registry 3dBi, D-8 2.33dBi 이하 조건 | KC/RF 적합성 및 인증 범위 오류 | 안테나 모델/최대 이득/케이블/모듈/배치와 시험기관 확인 | 공식 부품 사양 및 시험기관 회신 | BLOCKED |
| RSK-004 | P0 | Mechanical/Electrical | PCB 장착홀 위치와 하판 홀 부재/좌표 정보 불완전 | 목재 재가공, PCB 응력, 쇼트/간섭 | PCB 실제 외곽/홀 좌표/부품 keepout/공구 접근/공차 overlay | 승인된 ECO + drawing + physical fit | HUMAN_APPROVAL_PENDING |
| RSK-005 | P0 | Product configuration | 450×250 가정용과 720×390 조리원용/IP67 후보 혼재 | 요구사항·안전·규제·제조 범위 혼선 | 독립 CFG와 intended-use/규격/근거 분리 | 승인된 product variant charter | DISCREPANCY_IDENTIFIED |
| RSK-006 | P0 | Actuator/Amplifier | 12Ω 샘플 성공 기록을 8Ω 양산품에 일반화 | 출력/전류/열 과부하 | 정확한 부품 데이터시트, 실제 부하, 파형, 전원/온도 시험 | 승인된 load qualification report | VERIFICATION_PENDING |
| RSK-007 | P0 | Safety claims | 0.05~0.25m/s²를 영아 안전/진정 기준으로 오인 | 근거 없는 안전·효능 주장 | 시험용 범위로만 표시, 임상 endpoint와 분리 | 연구 파트너 검토 및 출처 기록 | HUMAN_APPROVAL_PENDING |
| RSK-008 | P1 | Mechanical stack-up | 3.39mm nominal gap이 실제 동적 유격으로 오인 | 접촉/버징/케이블 마찰 | tolerance stack, 하중 변형, adhesive variation, vibration clearance 시험 | stack-up report + physical test | VERIFICATION_PENDING |
| RSK-009 | P1 | Cable routing | 케이블 길이/경로/서비스 루프/최소 굽힘 반경 미정 | 피로 단선, 끼임, 잡음, 조립 불량 | 3D route + harness drawing + vibration/abrasion/strain relief test | released cable assembly drawing | ENGINEERING_ACTION_OPEN |
| RSK-010 | P1 | Antenna integration | 금속/목재/배선/배터리 위치에 따른 RF 성능 변화 | 연결 안정성 저하 | 안테나 keepout/방향/케이블 손실/실물 RSSI·throughput 시험 | RF test report per configuration | VERIFICATION_PENDING |
| RSK-011 | P1 | CAD/Viewer | 좌표계·단위·원점 불일치 또는 stale GLB | 간섭 판단 오판 | known-point transform tests, source revision 표시, export hash | geometry consistency report | ENGINEERING_ACTION_OPEN |
| RSK-012 | P1 | Drawing/DFM | DXF 주석/바운딩박스와 절단 윤곽 혼동 | 잘못된 레이저 가공/네스팅 | cut layer allowlist, text exclusion, units/scale check, vendor preview | approved manufacturing drawing | ENGINEERING_ACTION_OPEN |
| RSK-013 | P1 | Firmware/HW | firmware binary가 다른 PCB/module/partition과 결합 | 부팅 실패/제어 오동작/OTA 복구 실패 | compatibility manifest, hardware-in-loop, rollback tests | validated FW-HW matrix | VERIFICATION_PENDING |
| RSK-014 | P1 | Power/thermal | USB-C 전원/케이블/보조배터리 전류 제한, boost/amp peak load | reset, undervoltage, heating | worst-case current and temperature measurement | power budget + thermal test | VERIFICATION_PENDING |
| RSK-015 | P1 | CAE | 코드 존재를 solver verification/validation으로 오해 | 설계 안전성 오판 | benchmark, mesh convergence, material/BC review, correlation | CAE verification & correlation report | VERIFICATION_PENDING |
| RSK-016 | P1 | Test | 가속도계/마운트/필터/샘플링/교정 정보 부족 | 재현 불가한 진동 결과 | calibrated instrument, sensor mounting protocol, raw data retention | approved test protocol + raw data | BLOCKED |
| RSK-017 | P1 | Manufacturing | E-BOM/M-BOM/대체품/공급자 정보 혼재 | 조립 오류/원가·품질 편차 | separate BOMs, approved vendor list, incoming inspection | pilot build record | ENGINEERING_ACTION_OPEN |
| RSK-018 | P1 | Regulatory | KC/어린이제품/RF/EMC 범위 제품군별 미확정 | 재시험/인증 지연 | classify intended use/age group/power/radio/product form with lab | regulatory applicability memo | BLOCKED |
| RSK-019 | P1 | Data governance | 오래된 보고서가 최신 기준처럼 유통 | 잘못된 설계값 재사용 | status banner, revision metadata, source hash, superseded link | traceability audit | ENGINEERING_ACTION_OPEN |
| RSK-020 | P1 | Automation | GitHub-hosted runner에 CAD/CAE/EDA 도구가 없거나 license/GUI 필요 | CI false fail/불필요한 비용 | lightweight CI + local/self-hosted specialized runner | runner capability matrix | ENGINEERING_ACTION_OPEN |
| RSK-021 | P1 | CI security | PR workflow가 과도한 token 권한/외부 action을 사용 | 저장소/비밀정보 위험 | least privilege permissions, pinned actions, untrusted PR read-only | workflow security review | ENGINEERING_ACTION_OPEN |
| RSK-022 | P2 | Toolchain | FreeCAD/CadQuery/Three.js/EasyEDA 중복 파이프라인 | 변환/수정 책임 혼란 | tool ownership matrix; one authoritative source per artifact | approved toolchain register | ENGINEERING_ACTION_OPEN |
| RSK-023 | P2 | Scope creep | 18개 영역 동시 구축으로 MVP 검증 지연 | 시간/비용 낭비 | dependency-based backlog; only critical vertical slice first | prioritized backlog review | ENGINEERING_ACTION_OPEN |
| RSK-024 | P2 | Team capacity | full-time job과 소규모 팀으로 검토/시험 병목 | 일정 지연 | work-in-progress limit, external review for specialist areas | resource plan | ENGINEERING_ACTION_OPEN |
| RSK-025 | P2 | Evidence | 논문/타사 FDA 자료를 MAJN 효능/인증으로 오해 | 과장 광고/투자자료 리스크 | claim-evidence matrix, evidence type/quality separation | reviewed claim register | ENGINEERING_ACTION_OPEN |
| RSK-026 | P2 | Privacy | 앱/로그/시험 데이터에 개인·영아 정보 포함 | 개인정보 노출 | minimize, de-identify, retention/access policy | data governance checklist | ENGINEERING_ACTION_OPEN |

## 3. 반드시 연결할 기존 감사 항목

기존 DISC-001~012는 삭제하지 않는다. 상태를 다시 평가하고, 조치와 증거를 붙인다. 특히 DISC-008은 실제 설계 변경이 아직 수행되지 않았으므로 `RESOLVED`로 처리하지 않는다. `OPEN` 또는 더 구체적인 상태를 유지한다.

기존 interface registry의 `VERIFIED`는 원본 시험 증거와 configuration ID가 연결되는지 확인한다. 연결되지 않으면 `VERIFICATION_PENDING` 또는 `UNRESOLVED`로 낮춘다. 단순히 인터페이스 설명이 존재하는 것과 실제 검증은 다르다.

## 4. 변경 영향평가 체크리스트

모든 ECO/PR에서 아래를 검토한다.

- [ ] Intended use / user / environment / product variant
- [ ] Requirements / acceptance criteria
- [ ] System architecture / ICD
- [ ] CAD / dimensions / tolerances / materials
- [ ] Drawing / DXF / STEP / GLB derivatives
- [ ] PCB / schematic / BOM / Gerber / CPL
- [ ] Power / thermal / EMC / RF
- [ ] Cable routing / connector / pinout / strain relief
- [ ] Firmware / protocol / OTA / fault behavior
- [ ] CAE model / mesh / loads / boundary conditions
- [ ] Assembly / service / cleaning / packaging
- [ ] Hazard / FMEA / residual risk
- [ ] Verification protocol / equipment / raw data
- [ ] Research/clinical claim / IRB / usability
- [ ] Regulatory applicability / certification
- [ ] Manufacturing process / supplier / inspection
- [ ] Lifecycle / repair / field feedback

각 항목은 AFFECTED, REVIEWED_NO_CHANGE, NOT_APPLICABLE, UNRESOLVED로 기록한다. UNRESOLVED가 하나라도 남으면 ECO 종료를 금지한다.

## 5. 리스크 검토 주기

- 매 PR: 변경과 직접 관련된 리스크 검토
- 매 Gate: P0/P1 전체 재평가
- 새 시제품 조립/시험 전: 구성, 위험통제, 시험 절차 확인
- 부품 대체/안테나/전원/펌웨어 변경 시: 안전·규제·EMC 영향 재평가
- 제품 intended use 변경 시: 요구사항부터 규제·연구까지 전체 재검토
