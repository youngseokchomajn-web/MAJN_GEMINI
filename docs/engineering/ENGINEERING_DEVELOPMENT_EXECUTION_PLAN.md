# MAJN 엔지니어링 통합 시스템 상세 개발 실행계획

- 문서 ID: MAJN-ENG-PLAN-001
- 상태: Draft for controlled execution
- 기준: `docs/engineering-system-plan` + `docs/engineering-system-wp00-wp01-baseline`
- 적용 범위: 제품 요구사항부터 CAD/CAE, 전장/케이블, 펌웨어, 검증, 안전, 규제, 제조 및 수명주기까지
- 원칙: 이 문서는 실행 순서와 통제 방법을 정의한다. 미해결 설계값을 승인하거나 기존 파일을 자동 변경하지 않는다.

## 1. 목표와 완료 정의

MAJN의 설계·제작·시험 정보를 하나의 추적 가능한 체계로 연결한다. 특정 시제품을 재현하려면 어떤 기구 형상, PCB, 케이블 하네스, 펌웨어, 파라미터, 부속품 및 시험 절차가 사용됐는지 확인할 수 있어야 한다. 설계 변경이 발생하면 영향을 받는 도면, 3D 모델, 하네스, PCB, 펌웨어, CAE, 시험, 위험 및 제조 문서를 빠짐없이 식별할 수 있어야 한다.

완료는 문서 수나 자동화 수가 아니라 다음 조건으로 판정한다.

1. 각 제품/시제품 구성이 식별 가능한 구성 매니페스트를 가진다.
2. 요구사항-설계-인터페이스-위험-시험-증거 간 양방향 추적이 된다.
3. 기구/전장/케이블/PCB/펌웨어/CAE의 기준 리비전과 호환성이 기록된다.
4. 설계 변경 영향평가와 승인 이력이 남는다.
5. CI는 결정론적인 형식·참조·기존 검증기 실행을 자동화하되, 안전/성능 판단을 자동 승인하지 않는다.
6. 실제 시험 데이터는 원본, 계측 조건, 처리 코드, 결과, 검토자를 함께 보존한다.

## 2. 기준 자료와 신뢰 경계

우선 참조 자료:
- `ENGINEERING_MASTER_PLAN.md`
- `ENGINEERING_DOMAIN_REGISTER.md`
- `ENGINEERING_DATA_SCHEMA.md`
- `ENGINEERING_ROADMAP.md`
- `WP00_WP01_INTEGRATED_AUDIT_REPORT.md`
- `baseline/asset_inventory.csv`
- `baseline/discrepancy_register.csv`
- `baseline/interface_registry.csv`

감사 보고서는 조사 결과이지 설계 동결 문서가 아니다. 감사 보고서 또는 CSV에 `VERIFIED`, `RESOLVED`, `VERY HIGH`라고 적혀 있다는 사실만으로 실제 설계·시험 승인 상태로 승격하지 않는다. 원본 소스, 실물 식별정보, 측정 원시데이터, 조건, 리비전, 독립 검토가 연결된 경우에만 해당 사실을 확인한다.

### 2.1 발견된 추가 기준선 충돌

| ID | 충돌 | 실행 처리 |
|---|---|---|
| BASE-01 | 감사 보고서 상 PCB #0005가 4층으로 서술되나 자산 대장에는 Original.epro2가 2층으로 표기됨 | 실물 보드 사진/거버/원본 EasyEDA 프로젝트/보드 실크/제조기록을 대조해 보드 ID와 층수를 분리 확인 |
| BASE-02 | 감사 보고서의 직렬 저항 21.6Ω과 #0005 성공 기록의 24.8Ω이 다름 | 측정 파일, 시료 ID, 채널/배선 구성, 리드 보정, 온도, 측정일을 대조. 둘 다 원본 그대로 보존 |
| BASE-03 | 인터페이스 레지스터는 RF 3dBi를 VERIFIED로 표기하지만 D-8은 2.33dBi 이하 등록 조건 확인을 요청 | 안테나 제조사/모델/이득/케이블/커넥터/모듈 인증 조건과 시험기관 회신 전까지 RF 인터페이스 상태를 UNRESOLVED |
| BASE-04 | PCB 마운팅 홀 누락으로 기록됐지만 PCB 프로젝트에 68.58×54.86mm 홀 패턴이 있다고 기재 | PCB 홀 패턴과 하판 가공홀은 서로 다른 객체. 좌표계 변환, 보드 외곽, 부품 높이, 스탠드오프, 나사/공구 접근성을 함께 검토 |
| BASE-05 | 450×250 가정용과 720×390 조리원용/IP67 제품군이 함께 기록됨 | 두 번째 제품군의 제품 요구사항, IP 시험 근거, 제조도면, 시장/사용환경이 확인될 때까지 별도 후보 구성으로 격리 |
| BASE-06 | 보고서의 8Ω 양산 익사이터와 #0005의 12Ω 샘플 실측 조건이 다름 | #0005의 성공은 해당 실물 구성에서만 유효. 8Ω 적용 성능/발열/전류는 별도 시험 필요 |
| BASE-07 | 13.5mm 캐비티에서 10.11mm 익사이터 적층값을 빼 3.39mm 여유로 판단 | 공칭 계산과 공차·하중·접착층·케이블·진동 중 동적 간섭 검증을 구분 |
| BASE-08 | 18개 도메인 성숙도 백분율의 평가 척도가 정의되지 않음 | 근거 없는 백분율을 공식 KPI로 사용 금지. 산출물/검증/승인 기준 기반 상태로 전환 |

## 3. 개발 원칙과 작업 통제

- 기존 원본은 제자리에서 유지한다. 이동/이름변경/삭제는 별도 ECO 및 백업/해시 확인 후 수행한다.
- 파생파일(DXF, STEP, GLB, mesh, PDF, plot)은 원본과 다른 artifact ID 및 source reference를 가진다.
- 단위는 SI를 기본으로 하며, 도면 단위와 좌표계/원점/축 방향을 메타데이터로 명시한다.
- 모든 기하/전기/펌웨어/시험값에는 출처와 적용 구성 및 상태를 부여한다.
- 확인되지 않은 값은 빈칸 또는 TBD로 유지한다. 근사값을 사실처럼 채우지 않는다.
- 모든 자동화는 dry-run/preview를 먼저 제공하고, 승인된 경우에만 변경을 수행한다.
- 설계 승인자와 변경 작성자/검증자는 가능하면 분리한다.
- AI는 분석·초안·변환·테스트 실행을 지원하지만 안전성, 임상 효능, 규제 적합성 및 제조 릴리즈를 승인하지 않는다.

## 4. 단계별 개발 로드맵

기간은 달력 약속이 아니라 1~2인 개발팀 기준의 계획 범위다. 선행 게이트와 실제 자료 상태에 따라 재산정한다.

| 단계 | 예상 작업량 | 목표 | 진입 조건 | 종료 조건 |
|---|---:|---|---|---|
| P0 기준선 정정 | 3~5 작업일 | 감사 대장 신뢰성 회복 | WP-00/01 조사자료 확보 | P0 충돌 ID별 증거/담당/상태 확정 |
| P1 Engineering Core | 5~8 작업일 | ID/레지스터/매니페스트/ECO 구조 | P0의 미확정값 격리 | 스키마 검증 및 샘플 구성 재현 |
| P2 CAD·전장 통합 | 8~15 작업일 | CAD-Viewer-PCB-Harness 연결 | 기구/PCB 좌표 기준 확인 | 3D 간섭 검토, 하네스 도면/ICD 초안 |
| P3 전자·펌웨어·CAE | 8~15 작업일 | HW/FW 구성 고정, CAE 재현성 | 시제품/보드 ID 및 도구 환경 식별 | 빌드/시험/해석 입력 구성 매니페스트 |
| P4 검증·안전·연구 | 10~20 작업일 + 외부기관 대기 | 계측, 위험, 증거 체계 | 시험 장비/절차/안전 통제 | 반복 시험 데이터와 잔여 위험 검토 |
| P5 제조·규제 준비 | 10~20 작업일 + 외부기관 대기 | 제조/품질/규제 문서화 | 설계 후보 및 검증 증거 | 파일럿 빌드와 규제 갭 검토 완료 |

작업량은 문서·자동화 개발의 추정치다. 부품 조달, 외부 시험기관 일정, 임상/IRB, 인증시험 기간은 포함하지 않으며 별도 일정으로 관리한다.

## 5. 세부 Work Package

### P0 — 기준선 정정

**WP-00A: 자산 대장 정합성**
- 파일 경로 존재 여부, Git commit, hash, 원본/파생 구분, 소유 도구, 리비전, 제품군, 시제품 ID를 검증한다.
- 누락/이동/중복 경로를 기록하되 자동 삭제하지 않는다.
- 파일 크기만으로 동일성을 판단하지 않고 SHA-256과 소스 이력을 사용한다.

**WP-00B: 시제품 구성 재구성**
- PCB #0005 실물, PCB 원본 프로젝트, 차기 Rev-C 제조 프로젝트, 70-part concept를 서로 다른 보드 식별자로 분리한다.
- 각 보드의 층수, 보드 외형, 장착홀, 커넥터, BOM, 제조 산출물, 펌웨어 호환성을 확인한다.
- 시제품 번호와 PCB 리비전, 모듈/안테나/익사이터 부품 번호를 별도 필드로 기록한다.

**WP-01A: 치수·좌표 감사**
- DXF 단위, INSUNITS, 블록/레이어, 치수 엔티티, 절단 윤곽, 주석 텍스트를 분리한다.
- 좌표계 정의(원점, X/Y/Z, 상판/하판 기준면, 조립 datum)를 문서화한다.
- 뷰어의 0.00mm 표시는 특정 파라미터와 모델 간 비교 결과인지, 전체 설계 정확도인지 범위를 명시한다.

**WP-01B: 전기·케이블·RF 감사**
- 커넥터 part number, pin numbering 방향, 케이블 길이 기준점, 배선 방식, 부하 구성, 극성, 정격을 검증한다.
- BTL 출력은 차동 출력으로 취급하고 각 출력 단자를 GND로 가정하지 않는다.
- RF 안테나 이득/케이블 손실/배치/모듈 인증 조건을 독립 확인한다.

**산출물:** 정정된 discrepancy register, source-of-truth matrix, prototype configuration manifest, evidence links.
**Gate P0:** Critical 충돌은 해소하거나 BLOCKED 상태와 필수 증거/책임자를 지정해야 한다. 충돌이 남아도 문서 체계 개발은 진행할 수 있지만, 해당 값을 사용하는 제조/설계 릴리즈는 금지한다.

### P1 — Engineering Core

**WP-02: 식별자·메타데이터**
- REQ, SYS, IF, PART, ASM, CABLE, PCB, FW, DRW, CAE, RISK, TEST, EVID, CFG, ECO ID 규칙을 적용한다.
- ID는 영구 식별자, revision은 변경 이력으로 분리한다.
- 메타데이터 필드: artifact_id, type, title, revision, status, product_variant, configuration_id, source_refs, units, coordinate_frame, owner, created_by, reviewer, approval, verification_state, hash, toolchain_version.

**WP-03: 레지스터 및 링크**
- 요구사항, 파트, E-BOM, M-BOM, 인터페이스, 케이블, 위험, 시험, 증거, 구성, ECO 레지스터를 생성한다.
- 기존 28개 요구사항 ID는 원본 ID를 보존해 import한다. 중복/모호한 요구사항은 새 ID를 발급하지 않고 mapping/duplicate 후보로 표시한다.
- 각 Critical/Safety 요구사항은 검증 방법과 수락 기준 또는 미해결 근거를 가져야 한다.

**WP-04: 구성 매니페스트**
- 시제품별로 mechanical assembly revision, PCB ID/revision, BOM, cable harness revision, ESP32 module/antenna, firmware commit/build environment/binary hash, configuration parameters, accessories, test record를 묶는다.
- 하나의 최신 파일 링크가 아니라 시험 시점의 불변 구성을 기록한다.
- 변경 전후 호환성은 명시적으로 평가한다.

**WP-05: ECO**
- 변경 요청 → 영향평가 → 설계 검토 → 검증 계획 → 승인 → 구현 → 검증 → 릴리즈 → 구버전 superseded 순서를 정의한다.
- 영향평가는 E01~E18 각각에 AFFECTED / REVIEWED_NO_CHANGE / NOT_APPLICABLE / UNRESOLVED 중 하나를 기록한다.
- 미해결 영향이 있으면 ECO를 닫지 않는다.

**산출물:** 스키마, CSV/JSON 레지스터, validator, 샘플 CFG manifest, ECO 템플릿.
**Gate P1:** 레지스터 참조 무결성, 필수 메타데이터, 유효 상태 전이, 구성 재현 테스트 통과.

### P2 — CAD·3D·Cable Routing & Electrical Integration

**WP-06: CAD 원본·파생 파이프라인**
- 현행 `rev2_params.py`와 DXF 생성기를 변경 없이 분석한다.
- 승인된 파라미터만 DXF 생성기에 전달하고, 출력 전후 critical dimension 비교를 수행한다.
- FreeCAD 네이티브 모델/STEP 도입은 편집성·조립·CAE 전달에서 실제 이득이 확인된 뒤 적용한다.
- GLB는 viewer용 파생물로만 관리한다.

**WP-07: 통합 3D Viewer**
- 기존 Three.js 뷰어를 확장한다. 신규 뷰어 중복 개발 금지.
- 모델 노드 ↔ PART/ASM ID ↔ BOM ↔ source revision 매핑을 구현한다.
- PCB, 커넥터, 안테나, 케이블, 그로밋, 클립, 스트레인 릴리프를 단계별 추가한다.
- CAD 좌표계와 viewer 좌표계 간 변환을 자동 검증한다.
- exploded view, layer visibility, section view, collision highlight, configuration switch, cable route overlay를 우선순위 순으로 추가한다.

**WP-08: Cable Routing & Harness Definition**
- 케이블 양 끝점, 커넥터/핀, 신호/전원 분류, 도체 수/게이지, 절연재/온도 등급, 길이 및 공차, 최소 굽힘 반경, 서비스 루프, 고정점, 보호재, 라벨, 조립 순서를 정의한다.
- 진동판/목재 모서리/나사 보스/가스켓/PCB/안테나/이동부와의 간섭 및 마찰 가능성을 검사한다.
- 전원선과 저레벨 신호/RF 경로는 EMC/노이즈 검토 후 분리 원칙을 결정한다.
- 케이블 길이 25cm ±2cm 등의 기존 값은 실제 양 끝 기준점과 조립 상태가 확인되기 전까지 후보 사양으로 둔다.
- 하네스 도면, wire list, connector pinout, harness BOM, routing drawing, continuity/polarity test를 산출한다.

**WP-09: 전기-기구 ICD**
- PCB mounting hole, board edge, component keep-out, connector mating direction, cable exit, antenna clearance, thermal path, access envelope를 하나의 좌표 기준으로 정의한다.
- 기구 홀 추가 전 PCB 실제 보드/거버/기구 datum을 중첩하고 공차 누적을 확인한다.
- 3D 간섭 통과만으로 제조 가능 판정하지 않고 나사 체결 공구 접근과 조립 순서를 확인한다.

**WP-10: 도면·DFM·조립성**
- 도면의 재료, 두께, 공차, 표면처리, 홀/슬롯, 절단 윤곽, 기준면, 검사 특성을 정의한다.
- 조립 작업 순서, 작업자 손/공구 접근, 케이블 끼임, 유지보수/분해/세척, 부품 교환을 검토한다.
- 조립 SOP와 검사 체크시트를 파일럿 조립에서 검증한다.

**Gate P2:** 도면-CAD-BOM 일치, PCB/하네스 배치, 간섭 보고서, cable drawing, ICD, physical assembly review가 완료되어야 한다. PCB/목재 가공 변경은 별도 승인 전까지 HOLD.

### P3 — PCB·Firmware·CAE

**WP-11: PCB 설계/제조 패키지**
- EasyEDA 원본, schematic, PCB, BOM, CPL, Gerber, drill, fabrication notes의 revision 일치를 검증한다.
- ERC/DRC와 제조 패키지 검증기는 기존 도구를 재사용한다.
- U1 쇼트, L1/D3, BOOST_SW loop, C5-U3 VIN/GND loop 등 기존 이슈는 각각 issue ID로 추적한다.
- BOM 대체품은 footprint, pinout, electrical ratings, thermal, availability, certification impact를 검토한다.
- #0005에서 성공한 전기 동작은 Rev-C 제조본 승인 근거로 자동 전이하지 않는다.

**WP-12: Firmware & configuration**
- PlatformIO build env, board/module variant, partition table, SDK/library versions, compile flags, firmware commit, binary SHA-256을 manifest에 연결한다.
- unit/protocol tests, build, OTA rollback/recovery, watchdog/fault handling, brownout, reconnect, long-run, RF coexistence를 단계화한다.
- OTA는 전원 안정성/중단 복구/버전 호환성 시험을 별도로 둔다.
- 무선 업데이트가 실패해도 안전한 상태로 복구되는지 검증한다.

**WP-13: CAE pipeline**
- 기존 웹 기반 solver와 INP 생성기를 먼저 테스트 사례로 평가한다. CalculiX CLI 연동은 검증된 입력/출력 계약이 정해진 뒤 진행한다.
- 재료 방향성, 적층/접착, 접촉, 체결, 경계조건, 하중, mesh convergence, solver version을 모두 기록한다.
- 해석 유형은 정적/모달/조화응답/FRF 중 질문과 검증 데이터가 있는 것부터 선택한다.
- 수치 결과의 단위, mesh sensitivity, energy balance, benchmark case를 검사한다.
- 계측과 matched configuration으로 상관성을 확인하기 전에는 해석 결과를 제품 성능 주장에 사용하지 않는다.

**Gate P3:** 재현 가능한 PCB 제조 데이터/펌웨어 빌드/CAE 입력 세트가 존재하고, 선택된 시험 사례가 재실행 가능해야 한다.

### P4 — 시험·안전·연구

**WP-14: Verification & Measurement**
- 요구사항별 verification method(inspection, analysis, demonstration, test)를 지정한다.
- 계측 장비 모델/serial/calibration, 센서 방향/부착, sample rate, filter, window, load, mattress/contact surface, 환경, operator, test article configuration을 기록한다.
- 전기적 익사이터 동작, 구조 전달, 매트리스 상부 진동, 소음/온도, 장기 내구, 사용 결과를 별도 시험으로 구분한다.
- 원시 데이터는 수정하지 않고, 처리 스크립트와 파생 데이터 버전을 분리한다.
- RMS/peak/crest factor, frequency spectrum, uncertainty, repeatability를 시험 목적에 맞게 정의한다.

**WP-15: Safety & Reliability**
- 사용 시나리오와 오사용/고장 시나리오 기반 hazard analysis/FMEA를 수행한다.
- 전원/배터리/USB, 열, Class-D 출력, 케이블 단선/단락, 커넥터 분리, 과진동, 고정 풀림, 구조 파손, 끼임, 세척/액체, RF/EMC, OTA 오류를 포함한다.
- 위험 통제는 요구사항/설계/시험과 연결하고 residual risk는 사람의 승인을 받는다.
- 성인 기준이나 타 제품 인증을 영아용 제품 안전 근거로 직접 전용하지 않는다.

**WP-16: Research & Usability**
- 진정/수면/행동 결과 주장은 벤치 진동과 분리한다.
- 연구 질문, endpoint, inclusion/exclusion, study design, adverse event, data privacy, ethics/IRB, 연구기관 역할을 전문가와 정의한다.
- 승인 전 영아 대상 연구/사용시험을 진행하지 않는다.
- UI/보호자 사용성, 경고, 오사용 방지, 설정 범위, 중단/비상 동작을 별도 평가한다.

**Gate P4:** 시험 증거와 잔여 위험이 정리되고, 임상·안전 주장이 근거 범위를 초과하지 않아야 한다.

### P5 — 제조·규제·수명주기

**WP-17: Manufacturing & Quality**
- E-BOM/M-BOM 분리, 승인 공급자/대체품, 입고검사, 공정 흐름, CTQ, 작업표준, 검사 기록, 부적합/NCR, CAPA, serial traceability를 만든다.
- 파일럿 빌드에서 실제 공정 능력과 재작업/조립 이슈를 기록한다.
- 제조 릴리즈 패키지의 revision과 구성 manifest를 고정한다.

**WP-18: Regulatory & Lifecycle**
- 제품 분류와 적용 규격/인증 경로는 공인 시험기관 및 자격 있는 전문가와 확인한다.
- KC/EMC/RF/어린이제품 관련 의무는 모델/안테나/전원/사용 환경에 따라 확인한다. 시험기관 질의 전에는 적합/면제/승계 가능성을 단정하지 않는다.
- 라벨, 설명서, 포장, 운송, 반품, 세척, 부품교체, 폐기, 불만/사고 대응 프로세스를 정의한다.

**Gate P5:** 파일럿 구성 추적, 품질 기록, 규제 갭 평가, 릴리즈 승인 및 사후관리 책임이 정의되어야 한다.

## 6. 우선순위 실행 백로그

### 즉시 착수 — 문서/데이터만으로 가능한 작업
1. BASE-01~08을 discrepancy register에 추가하고 기존 상태를 보존한다.
2. 자산 대장에 prototype_id, board_id, product_variant, source_commit, sha256, source_or_derivative 필드를 추가한다.
3. status dictionary와 evidence schema를 정의한다.
4. 구성 매니페스트 템플릿과 ECO 템플릿을 만든다.
5. 기존 파일을 이동하지 않고 relative path + commit/hash로 연결한다.
6. validator의 첫 버전은 CSV/JSON 스키마, 중복 ID, 끊어진 링크, 잘못된 상태 전이만 검사한다.

### 다음 — 설계/실물 확인이 필요한 작업
1. PCB #0005 층수 및 보드 식별을 확정한다.
2. 21.6Ω/24.8Ω 측정 차이를 원본 데이터로 해결한다.
3. RF 안테나 정확한 모델/이득/인증 조건을 확인한다.
4. PCB 홀과 하판 좌표계를 정합한다.
5. 케이블 양 끝점/경로/서비스 루프/최소 굽힘 반경을 실물 조립으로 확인한다.
6. 가압/하중 상태 캐비티 간섭을 확인한다.
7. 8Ω 익사이터는 전류·출력·온도·장시간 시험 계획이 승인될 때까지 양산 BOM 확정 금지.

### 후속 — 반복 가능한 데이터가 확보된 뒤
1. CAD→STEP/GLB 자동 export 및 viewer ID mapping
2. harness route collision/length report
3. CAE batch runner 및 correlation report
4. test data ingestion 및 plot pipeline
5. 제조 패키지와 configuration release automation

## 7. 개발팀 역할과 승인 책임

| 역할 | 책임 | 승인 범위 |
|---|---|---|
| Product/Systems owner | intended use, 요구사항 우선순위, 제품 구성 | 요구사항/구성 기준 |
| Mechanical owner | CAD, drawing, tolerance, assembly | 기구 설계/도면 |
| Electrical owner | schematic, PCB, power, RF, harness electrical | 회로/PCB/전기 인터페이스 |
| Firmware owner | build, protocol, OTA, fault behavior | 펌웨어 릴리즈 |
| Test/Verification owner | test method, equipment, raw data, reports | 시험 결과의 기술 검토 |
| Safety/Regulatory reviewer | hazard, residual risk, applicable standards | 안전/규제 판단 |
| Research partner | protocol, endpoint, IRB, clinical interpretation | 연구 설계/결과 해석 |
| AI agent | inventory, draft, code assistance, deterministic checks | 승인 권한 없음 |

소규모 팀에서는 한 사람이 여러 역할을 맡을 수 있지만, 자기 작성물의 독립 검토가 불가능한 경우 외부 전문가 검토를 지정한다.

## 8. 변경·릴리즈 통제

- main 및 기준 브랜치에 직접 작업하지 않는다.
- 기능/문서 작업은 별도 브랜치와 PR로 제출한다.
- 모든 PR에는 변경 이유, 영향 도메인, 수정 artifact IDs, 수행 검증, 미해결 위험, 롤백 방법을 포함한다.
- CAD/PCB/FW 산출물은 source commit, tool version, input hash, output hash를 보존한다.
- 기존 검증기 통과는 해당 검증기가 검사하는 범위에 한정해 보고한다.
- release tag는 구성 매니페스트, 승인자, 검사 결과, 바이너리 해시, 제조 문서가 연결될 때만 생성한다.

## 9. 예상 병목과 대응

| 병목 | 결과 | 대응 |
|---|---|---|
| 여러 제품/보드 세대 혼합 | 잘못된 BOM/치수/시험 결과 재사용 | 제품군·시제품·보드 ID 분리, 호환성 매트릭스 |
| CAD와 Viewer의 좌표계 불일치 | 잘못된 간섭/배치 판정 | datum 정의, known-point transform test |
| 케이블 경로를 3D 모델 없이 문서로만 관리 | 끼임/마찰/EMC/서비스성 문제 누락 | route node + harness drawing + physical mock-up |
| 파일 이동/중복 복사 | 참조 깨짐, SSOT 분열 | 첫 단계에서는 원본 유지, 링크/해시 등록 |
| CI에서 CAD/CAE 도구 미설치 | 거짓 실패 또는 검증 누락 | 경량 validator와 로컬/자체 runner 분리 |
| AI가 상태를 자동 승격 | 미검증 설계가 승인본처럼 유통 | 상태 변경은 evidence + human reviewer 필수 |
| 시험 장비/캘리브레이션 부족 | 결과 재현성 부족 | 장비 확보/외부 시험/측정 불확도 계획 |
| 인증 규격/분류 미확정 | 재설계·시험 재비용 | 초기 시험기관 질의와 regulatory gap analysis |
| 지나친 자동화 범위 | 도구 유지보수 부담 | 가장 빈번하고 오류 비용 높은 검사부터 자동화 |
| 제품 요구사항 변경 | 모든 도메인 재작업 | ECO impact matrix 및 baseline freeze |

## 10. Gate 요약

| Gate | 통과 조건 | 금지되는 조치 |
|---|---|---|
| G0 Baseline integrity | 원본/구성/충돌 추적 가능 | 미확정값 기반 설계 동결 |
| G1 Engineering Core | ID/스키마/manifest/ECO validator 통과 | 기존 원본 대량 이동 |
| G2 Integrated design candidate | CAD/PCB/harness/ICD/assembly review 정합 | 미승인 홀 가공/PCB 발주 |
| G3 Reproducible engineering | FW build/PCB package/CAE input 재현 | CAE를 실측 대체 근거로 사용 |
| G4 Verified candidate | 시험/위험/증거/잔여 위험 검토 | 영아 효능/안전성 과장 주장 |
| G5 Pilot & regulatory readiness | 파일럿 품질/규제 갭/문서 완비 | 인증/적합성 사전 단정 |
| G6 Release & lifecycle | 승인된 구성과 책임자/사후관리 확정 | 미승인 변경 포함 릴리즈 |

## 11. 첫 10개 실행 티켓

| 티켓 | 작업 | 선행조건 | 완료 증거 |
|---|---|---|---|
| ENG-001 | discrepancy register 상태/증거 필드 개편 | 없음 | 스키마 검증된 대장 |
| ENG-002 | PCB #0005/Rev-C/70-part board identity audit | 원본 EasyEDA/실물 | 보드별 구성표 |
| ENG-003 | 21.6Ω vs 24.8Ω measurement reconciliation | 원시 CSV/기록 | 측정 비교 메모 |
| ENG-004 | RF antenna identity/compliance evidence audit | 안테나 실물/부품 정보 | 모델·이득·케이블·승계 질의 |
| ENG-005 | PCB-to-housing datum and hole overlay | PCB CAD + DXF | 좌표 중첩 및 공차 보고서 |
| ENG-006 | harness endpoint/pinout/routing audit | 커넥터/실물 | harness definition draft |
| ENG-007 | prototype configuration manifest schema | ENG-002~006 | 샘플 manifest 검증 |
| ENG-008 | ECO template and impact matrix | ID/domain register | ECO dry-run |
| ENG-009 | registry validator v1 | schema | 자동 테스트 |
| ENG-010 | Three.js node-to-PART ID mapping spike | CAD/viewer baseline | 샘플 모델 매핑 데모 |

## 12. 본 문서의 승인 상태

본 계획은 개발 작업의 순서와 통제 방법을 정하는 문서다. 다음 항목은 별도 사람 승인 전까지 미승인 상태다: Rev 2 최종 기구 SSOT, PCB Rev-C 발주, PCB 하판 홀 추가, LDO 대체품, 익사이터 양산 임피던스, 안테나 인증 조건, 영아 관련 진동 판정 기준, 조리원용 제품군/IP 등급 주장.

관련 문서:
- [Risk and Conflict Register](ENGINEERING_RISK_AND_CONFLICT_REGISTER.md)
- [Integration and Interface Plan](ENGINEERING_INTEGRATION_AND_INTERFACE_PLAN.md)
- [Verification and Release Plan](ENGINEERING_VERIFICATION_AND_RELEASE_PLAN.md)
- [Work Package Backlog](ENGINEERING_WORK_PACKAGE_BACKLOG.md)
