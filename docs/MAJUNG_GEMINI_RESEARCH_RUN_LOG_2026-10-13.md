# MAJUNG Gemini 일괄 연구 실행 및 감사 로그 (Research Run Log)
작성일: 2026-10-13  
상태: 작업 산출물 및 후속 정합성 정정 기록 (버전 1.1)  
기준 브리프: `docs/MAJUNG_GEMINI_ONE_SHOT_HANDOFF_2026-10-13.md`

---

## 1. 실행 개요

* **실행 일시**: 2026-10-13 13:00 KST
* **당시 실행 목표**: 원문 추적성(WP-0) 감사, 증거 공백 매핑, 공학 벤치 계획, 임상 시놉시스, 연구자 패키지 및 제품 주장 게이트를 일괄 정리하는 것이었다. 이후 정합성 검토에서 WP-0 완료 판정과 일부 계획 수치·완료 표현이 과도했음이 확인되어 아래 정정 상태를 우선한다.
* **작업 브랜치**: `main` (최신 커밋 동기화 완료 후 실행)

---

## 2. 순위별 과업 수행 결과 요약

### [1순위] WP-0 핵심 문헌 (E001-A~F) 원문 locator 검토 — 완료 판정 보류
* **E001-A (Smith 2015)**: Figure 2, Table 2 및 p.e1565 adverse-event 문구의 주요 locator가 기록돼 있다. 모든 수치·분모의 최종 재대조가 남아 있어 전체 완료로 보지 않는다.
* **E001-B (Bloch-Salisbury 2009)**: 주요 표·그림 locator가 기록돼 있다. 물리 출력 subsection 및 이상사건 보고 범위 확인이 남아 있어 전체 완료로 보지 않는다.
* **E001-C (Zuzarte 2017)**: 일부 PDF 페이지 locator가 기록돼 있다. 모든 수치·분모 및 표·그림 locator 재대조가 남아 있다.
* **E001-D (Prapela FDA)**: 공식 9페이지 문서와 일부 규제 locator가 검토됐으나, 주요 문장·표의 2차 확인 및 redacted bench 수치 한계 기록이 남아 있다.
* **E001-E (Bloch-Salisbury 2023)**: 주요 HTML locator와 분석 위계는 기록돼 있으나, 인쇄 페이지 정규화·보충자료·하위집단 및 이상사건 맥락 확인이 남아 있다.
* **E001-F (Singh 2026/2025)**: PMC full-text에서 Methods/Results, Figure 1, Tables 2–4 anchor와 저널 페이지 범위 276–282를 확인했다. 개별 표의 인쇄 페이지 매핑은 최종 PDF 대조 전 잠정이며, 보충자료 내용 확인도 남아 있다.

### [2순위] 연구 및 규제 출처 등록부 생성
* 파일: `docs/MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md`
* 건강 만삭아 선행 연구(E002), 복합/비교 중재(E003: SNOO 등), 측정 타당도(E004: 가속도 간섭), 규제 기준(FDA 21 CFR 880.5151, ASTM F2194, KC 유아안전) 체계적 등록.

### [3순위] 근거 추출 마스터 테이블 생성
* 파일: `docs/MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md`
* 22개 표준 스키마 필드 전수 적용, source fact vs author interpretation vs MAJUNG inference 3단계 층위 완벽 분리.

### [4순위] 공학 출력 및 위험 벤치 시험 계획 수립
* 파일: `docs/MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md`
* 30–60 Hz 변위(10–25 μm RMS) 9점 측정, 0/3/6 kg 하중 및 침구 감쇠율 맵핑, <45 dBA 음향 소음, 표면 발열 <2°C 상승 한계, 전기/기계 페일세이프 규정.

### [5순위] 건강 영아 임상 연구 프로토콜 시놉시스 작성
* 파일: `docs/MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md`
* 생후 2주~16주 건강 만삭아 대상 MAJUNG-CALM Trial. 1차 평가변수(취침 진정 시간, 울음 비율) 조작적 정의, 비디오 독립 코딩 Gold Standard 설정, 액티그래피 간섭 필터링, IRB/DSMB 규정.

### [6순위] 국내 연구진 공식 검증 숏리스트 및 아웃리치 패키지 구축
* 파일: `docs/MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md`
* 파일: `docs/MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md`
* 조재소(분당서울대), 이병섭/김수현(서울아산), KRISS 진동음향센터 공식 팩트체크 완료. 과장 없는 1-page Concept Note, 한국어 이메일 초안, 30분 미팅 구조화 아젠다, IP/COI 거버넌스 완성.

### [7순위] 의사결정 게이트 (Gate 0–5) 및 클레임 규칙 확립
* 파일: `docs/MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md`
* 공학(Gate 0) -> 인증(Gate 1) -> 자문/IRB(Gate 2) -> 파일럿(Gate 3) -> 확증임상(Gate 4) -> 상용화(Gate 5). 의료기기 오인 금지 및 허용/금지 문구 매트릭스, 2주 로드맵 수립.

---

## 3. WP-0 종료 게이트 점검표 — 정정 상태

| 점검 항목 | 현재 판정 | 미해결 사항 |
|---|---|---|
| 주요 수치 추적성 | 부분 확인 | E001-C/E/F 등 일부 표·그림의 개별 locator 및 분모 재대조 필요 |
| 표본 분모 구분 | 부분 확인 | source별 enrolled/randomized/analyzed 및 하위분석 분모 최종 대조 필요 |
| 분석 위계 구분 | 주요 구분 기록 | 원문 locator와 분모 재확인, 하위집단 결과의 탐색적 성격 유지 |
| 이상사건 코딩 | 부분 확인 | E001-B/E/F 등 보고 범위와 원문 맥락 재확인 |
| Evidence type/quality/directness | 별도 필드 존재 | 값의 일관성 및 근거 추적성 검토 계속 |
| 음성 결과 보존 | 주요 음성 결과 기록 | 원문 locator와 수치 재대조 필요 |
| 독립 검토 기록 | 외부 독립 검토 미실시 | 독립 임상 연구자 검토는 향후 단계로 남음 |

**정정된 WP-0 상태: Partial — 종료 판정 보류.** 이전 버전의 “Internal Verification Complete” 및 “전수 대조 완료” 표현은 현재 확인된 미해결 locator와 일치하지 않아 철회한다. 일부 표·그림의 위치가 확인됐다는 사실은 모든 문헌의 추출·수치·이상사건 검토가 끝났다는 의미가 아니다.

## 4. 신규 및 갱신 파일 목록

1. `docs/MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md` [신규]
2. `docs/MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md` [신규]
3. `docs/MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md` [신규]
4. `docs/MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md` [신규]
5. `docs/MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md` [신규]
6. `docs/MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md` [신규]
7. `docs/MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md` [신규]
8. `docs/MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md` [신규]
