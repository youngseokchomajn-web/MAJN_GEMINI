# MAJUNG Gemini 일괄 조사·검증 실행 패키지
작성일: 2026-10-13
상태: 실행 지시서 / WP-0 진행 중
대상 저장소: https://github.com/youngseokchomajn-web/MAJN_GEMINI

> 목적: 반복적인 채팅 조사 대신 Gemini Deep Research 한 번의 작업에서 기존 자료를 인계받아 원문 검증, 누락 보완, 연구설계 및 기관 협업 패키지까지 구조적으로 수행한다. 이 문서는 조사 완료를 선언하지 않는다.

## 1. 프로젝트의 최우선 원칙

MAJUNG(마중 스마트 배시넷)의 최우선 목표는 진동 하드웨어 구현 자체가 아니라 **제품 판매 전에 진동 모듈의 효과와 안전성을 뒷받침할 증거를 확보하고, 직접 증거가 부족하면 대학·병원 연구진과 함께 검증할 수 있는 준비를 끝내는 것**이다.

- 하드웨어 설계는 변경 가능한 개발 기준선이다. 기존 PCB나 부품 구성을 최종안으로 가정하지 않는다.
- 센서·펌웨어·PCB 개선은 증거 구축에 필요한 경우에만 다룬다. LSM6DSOX 등 특정 센서가 연구의 중심이 되면 안 된다.
- 일반 건강 영아의 진정, 울음 감소, settling, 수면 개선을 입증했다고 주장하지 않는다. 대상군·자극 방식·비교군·결과지표가 다른 연구를 MAJUNG 직접 근거로 취급하지 않는다.
- 임상 효능, 물리 출력 특성, 안전성, 규제 적합성, 마케팅 Claim은 별도의 검증 게이트다. 어느 한 영역의 통과가 다른 영역을 자동으로 입증하지 않는다.
- 결과가 유의하지 않거나 부정적이면 그대로 보존한다. 연구자의 해석, 원문에서 확인되는 사실, MAJUNG에 대한 추론을 분리한다.
- 영아 대상 연구는 대학/병원 연구팀 및 기관의 윤리심의(IRB 등), 법·규제 검토와 안전계획 없이 실행하도록 제안하지 않는다. 적절한 돌봄을 지연·대체하는 설계를 제안하지 않는다.
- 출처 위치·수치·분모를 확인하지 못하면 추정해서 채우지 말고 `미확인`, `미보고`, `미평가`, `불명확`으로 남긴다.
- 문헌 검토가 끝났다고 말하려면 완료 기준을 모두 충족해야 한다. 지금 WP-0는 진행 중이다.

## 2. 기준 저장소 및 기존 문서

**GitHub repo:** https://github.com/youngseokchomajn-web/MAJN_GEMINI
**연구 문서 색인:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_INDEX.md
**전체 종합·결정 기록:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_PROJECT_SYNTHESIS_AND_DECISION_REGISTER_2026-10-13.md
**표준 추출 상태표:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001_STANDARDIZED_EXTRACTION_STATUS_MATRIX_2026-10-13.md
**Claim–Evidence–Gap–Experiment 매트릭스:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_CLAIM_EVIDENCE_GAP_EXPERIMENT_MATRIX_2026-10-12.md
**연구·실험 마스터 플랜:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_RESEARCH_AND_EXPERIMENT_MASTER_PLAN_2026-10-12.md
**Endpoint·측정·이벤트 기록 계획:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_ENDPOINT_MEASUREMENT_AND_EVENT_LOGGING_PLAN_2026-10-12.md
**임상·측정 연구자 질문지:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_CLINICAL_RESEARCHER_REVIEW_QUESTION_SET_2026-10-13.md
**연구 검토 세션 로그:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_RESEARCH_REVIEW_SESSION_LOG_2026-10-12.md
**WP-0 진행 이슈:** https://github.com/youngseokchomajn-web/MAJN_GEMINI/issues/3

### 현재 E001 근거 세트
- E001-A Smith et al. 2015, 미숙아의 생리 지표와 stochastic resonance stimulation.
- E001-B Bloch-Salisbury et al. 2009, 미숙아의 호흡 생리 지표.
- E001-C Zuzarte et al. 2017, 산전 opioid 노출 신생아의 SVS 연구.
- E001-D FDA Prapela De Novo 요약, NOWS 적응증·규제 맥락.
- E001-E Bloch-Salisbury et al. 2023, 산전 opioid 노출 신생아 RCT.
- E001-F Singh et al. 2025 online / 2026 issue, NOWS 위험 신생아 다기관 SVS RCT.

현재 확인된 locator 진척: E001-A Table 2 p.e1566, adverse-event 문구 p.e1565; E001-B Table 2 p.1021 및 Figure 6 p.1024; E001-C Table 2 PDF p.9/15. E001-E/F의 표별 printed-page 위치, 보충자료와 수치별 독립 대조는 미완료다. 독립 검토도 아직 실시되지 않았다.

## 3. 이미 확보된 핵심 결론(반드시 유지)

1. **E001-E Bloch-Salisbury 2023:** 산전 opioid 노출 신생아 RCT에서 전체 morphine treatment 비율 35.6% vs 30.9%, P=.60으로 유의한 차이가 없었다. Exposure-duration association, 약물치료를 받은 하위집단, 특정 responder subgroup은 전체 무작위 비교와 별도로 설명한다. 6/58 장치 중단 후 약물치료 기준 충족 관찰만으로 rebound 또는 인과관계를 단정하지 않는다.
2. **E001-F Singh 2025/2026:** 다기관 open-label RCT, 62명( SVS 40, 표준 매트리스 22), 계획 표본 120명 전에 모집 부족으로 조기 종료. 5일 이내 약물치료 4/40 (10.0%) vs 4/22 (18.2%); adjusted OR 0.54 (95% CI 0.10–2.85), P=.46. 울음 subset n=46에서 fussy/pain cry 시간 8.0% vs 7.2%, P=.82, cry strength 87.2% vs 86.5%, P=.55. 통계적으로 유의한 차이를 보이지 않았고 신뢰구간이 넓다. 부모/간호사 주관적 수용성 응답은 객관적 효능과 분리한다.
3. **SNOO 연구:** 작은 미숙아 표본, rocking+white noise+swaddling 복합중재이므로 진동 단독 효과로 해석하지 않는다. 전체 수면시간 또는 울음 개선이 확립됐다고 쓰지 않는다.
4. **Contours Vibes:** 소규모 선택 표본, 순서 고정(기준선→진동 OFF→ON), 주로 보호자 보고, 짧은 기간. MAJUNG의 직접 효능 증거가 아니다.
5. **Huhtala et al. 2000:** 산통 영아에서 vibrator와 massage를 비교했으나 무처치 대조군이 없어 자연 경과를 분리하기 어렵다.
6. **Emori et al. 1995:** 1 Hz, 큰 진폭의 수평 cradle vibration에서 울음이 멈추는 관찰이 있었지만 졸림/수면 중 강한 각성도 보고됐다. MAJUNG에 대한 안전 한계나 동등 효과로 전용하지 않는다.
7. **Catal et al. 2024:** heel lance 전 국소 진동은 시술 통증 endpoint에 관한 연구다. 일반적인 진정·수면 개선 증거가 아니다.
8. **Poets et al. 2024:** 전동 rocking RCT에서 수면 지표 유의차가 없었다. rocking과 vibration은 서로 다른 자극이다.
9. **Prapela FDA De Novo:** 특정 NOWS 관련 적응증 및 해당 기기에 관한 규제 자료다. MAJUNG의 허가, 일반 영아 Claim, 모든 사용 환경에서의 안전성을 대신하지 않는다.
10. **Smith 2015 / Bloch-Salisbury 2009 / Zuzarte 2017:** 주로 미숙아 또는 산전 opioid 노출 신생아의 생리/움직임 결과다. 건강한 일반 영아의 울음·settling·수면 효능과 혼합하지 않는다.

## 4. Gemini가 수행할 전체 작업 범위

이 작업은 단순 문헌 요약이 아니다. 아래 work package를 한 작업 안에서 순서대로 수행하고, 각 단계 산출물을 저장소에 반영할 준비를 한다.

### WP-0 — 문헌 인벤토리 및 원문 수치 검증
- 기존 E001-A~F를 기준으로 중복 여부를 확인하고, 관련 직접·간접 근거를 추가 탐색한다.
- 우선순위: 논문 원문/보충자료, ClinicalTrials.gov 원등록·결과, FDA 공식 자료, 학회/저널 공식 보고, 체계적 문헌고찰, 그 외 2차 자료 순.
- 모든 핵심 수치에 DOI/URL, PDF printed page, section, table/figure/eTable, 정확한 행/열 또는 본문 문구를 기록한다.
- HTML locator와 PDF 인쇄 페이지를 별개 필드로 유지한다.
- 등록된 primary outcome와 최종 논문 보고 outcome, protocol deviation, early termination, missingness, analysis set를 비교한다.
- adverse-event 상태는 `reported` / `authors reported none` / `not reported` / `not assessed` / `unclear` 중 하나로 코딩한다.
- 독립 검토자가 없는 경우 `독립 검토 미실시`로 남긴다. Gemini가 자신을 독립 검토자로 표시하지 않는다.

### WP-1 — Claim–Evidence–Gap–Experiment 연결
제품이 주장할 가능성이 있는 Claim을 과장 없이 나눈다. 예시:
- 물리 Claim: 특정 조건에서 어떤 주파수·가속도·변위의 진동을 출력한다.
- 효능 Claim: settling time, 울음/보챔 시간 또는 수면 지표에 차이가 있다.
- 안전 Claim: 특정 연령·사용 환경·출력 범위에서 사전에 정의한 위험을 평가했다.
- 사용성/수용성 Claim: 보호자나 임상진이 사용하기 쉽다고 보고했다.
- 규제/마케팅 Claim: 별도 법규 검토가 필요한 문구.
각 Claim마다 현재 근거, 근거의 직접성, 반대/무효 결과, 빈틈, 필요한 시험, 통과 기준, 보류 기준을 연결한다.

### WP-2 — 영아 진정·울음·수면에 대한 근거 지도
- 건강한 만삭 영아, 미숙아, 산전 opioid 노출/NOWS, 시술 통증, 동물/가축, 비영아 성인 연구를 별도 population으로 분리한다.
- 진동, rocking, swaddling, white noise, massage, skin-to-skin 등 복합중재를 분리한다.
- 울음 감소, settling, sleep onset, total sleep time, sleep architecture, physiologic stability, procedural pain을 서로 다른 endpoint로 취급한다.
- 동물/가축 연구는 사람 영아 효능의 직접 근거가 아니라 기전/시험 아이디어 수준으로만 표시한다.
- systematic review와 negative/null findings도 포함한다. 성공 사례만 고르지 않는다.

### WP-3 — MAJUNG 물리 출력 및 공학 안전 시험계획
- 실제 장치 출력의 waveform, frequency, acceleration/displacement, RMS/peak, start/stop transient, spatial variation, load/bedding/contact surface effect, sound, temperature, actuator fixation, cord/entrapment 및 구조적 위험을 구분한다.
- 측정 기구/센서의 bandwidth, sampling rate, calibration, mounting, noise floor, uncertainty와 재현성을 함께 기록한다.
- 센서가 측정한 값과 임상 결과를 혼동하지 않는다. 가속도계만으로 영아의 진정이나 수면을 증명하지 않는다.
- 시험 전 제품 요구사항·대상 연령·사용 시나리오·접촉면·출력 한계를 미결정 항목으로 명시한다.
- 수치형 안전 한계를 문헌에서 그대로 가져오지 않는다. 표준·규제·임상전문가 검토 없이 허용 한계를 만들어내지 않는다.
- 시험 순서: 요구사항/위험분석 → bench characterization → 반복성/고장모드 → 연구팀/규제 검토 → 승인된 연구만 수행.

### WP-4 — 임상/연구기관 협업 패키지
- 적합한 한국 대학·병원·연구실 후보를 실제 공식 프로필/논문/기관 페이지로 검증한다.
- 후보마다 이름, 소속, 관련 연구, 해당 근거와 URL, 왜 적합한지, 어떤 질문을 자문할지, 접촉 우선순위를 기록한다.
- 소아청소년과/신생아 임상, 생체신호·수면 측정, 기계/제어공학/진동 계측, 의료기기·규제 전문가의 역할을 구분한다.
- 근거가 없는 개인 이메일·직함·협업 의향을 만들어내지 않는다.
- 첫 접촉 메일, 1-page concept note, 연구자 미팅 질문, 자료 제공 범위와 이해상충/데이터 관리 체크리스트를 작성한다.
- 연구팀이 검토할 질문: population, comparator, primary endpoint, clinically meaningful difference, sample size/power, measurement validity, blinding, safety monitoring, stopping rules, IRB, registration, data management, adverse-event reporting.

### WP-5 — 연구 프로토콜 초안과 통계 설계
- 후보 primary question: 통상적인 적절한 돌봄을 유지한 상태에서 MAJUNG 진동 추가가 사전 정의된 settling time 또는 울음/보챔 시간에 영향을 주는가?
- 후보 primary endpoint: 사전에 정의한 settling 기준까지의 시간. 임상·측정 연구자와 함께 정의를 확정하기 전에는 확정된 endpoint로 쓰지 않는다.
- secondary endpoints: crying/fussing duration, episode count, resolved/unresolved rate, blinded video behavior coding. Sleep onset/awakenings/total sleep time은 측정 타당성 검증 후 탐색 지표로 고려한다.
- 무작위화, 적절한 comparator, 가능한 평가자 눈가림, 사전 등록, sample-size rationale, missing-data handling, multiplicity, stopping rules, adverse-event capture를 제안한다.
- 실제 영아 연구는 IRB/기관·규제 검토 및 안전계획 후에만 실행 가능하다고 명시한다.
- 통계적 유의성뿐 아니라 effect size, CI, 임상적 의미, 불확실성을 기록한다. 사후 subgroup을 confirmatory 결과로 포장하지 않는다.

### WP-6 — 의사결정 및 제품 Claim 게이트
- Gate 0: intended use, 대상 연령, 사용자, 사용 환경, 출력·작동 조건 정의.
- Gate 1: 물리 출력 특성화 및 공학적 위험 검토.
- Gate 2: 임상·측정·규제 연구자와 population/endpoint/comparator/safety/ethics 합의.
- Gate 3: 기관 승인 후 feasibility study.
- Gate 4: 적절한 대조군을 갖춘 효능·안전 연구.
- Gate 5: 반복성/장기 사용 근거가 필요한 Claim은 별도 장기 검증.
각 gate에 통과 기준, 실패/보류 조건, 책임자 역할, 다음 행동을 기록한다. 근거 부족은 `보류`가 정당한 결정일 수 있다.

## 5. 필수로 다시 열어볼 주요 1차 출처

- Singh et al., “Efficacy of stochastic vibro-tactile stimulation for newborns at risk of neonatal opioid withdrawal syndrome,” Pediatric Research 2026;99(1):276–282, online 2025-05-23. DOI: https://doi.org/10.1038/s41390-025-04162-2
  - Publisher: https://www.nature.com/articles/s41390-025-04162-2
  - PubMed: https://pubmed.ncbi.nlm.nih.gov/40410582/
  - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC13134440/
  - Trial: https://clinicaltrials.gov/study/NCT04834297
- Bloch-Salisbury et al. 2023 JAMA Pediatrics RCT. DOI: https://doi.org/10.1001/jamapediatrics.2023.1077
  - https://jamanetwork.com/journals/jamapediatrics/fullarticle/2804943
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC10186209/
- Smith et al. 2015 Pediatrics. DOI: https://doi.org/10.1542/peds.2015-1334
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC4657600/
- Bloch-Salisbury et al. 2009: https://pmc.ncbi.nlm.nih.gov/articles/PMC2763836/
- Zuzarte et al. 2017 PLOS ONE. DOI: https://doi.org/10.1371/journal.pone.0175981
  - https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175981
- FDA Prapela De Novo summary: https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240031.pdf
- SNOO registry: https://clinicaltrials.gov/study/NCT05711927
- Contours Vibes: https://pmc.ncbi.nlm.nih.gov/articles/PMC8889968/
- Huhtala et al. 2000 Pediatrics: https://pubmed.ncbi.nlm.nih.gov/10835097/
- Emori et al. 1995: https://www.jstage.jst.go.jp/article/jje1965/31/6/31_6_369/_article/-char/en
- Catal et al. 2024: https://pubmed.ncbi.nlm.nih.gov/39394025/
- Poets et al. 2024: https://pubmed.ncbi.nlm.nih.gov/38760904/
- Korean skin-to-skin protocol (design/operations reference only): https://pmc.ncbi.nlm.nih.gov/articles/PMC12519669/
- Infant sleep intervention/actigraphy review: https://onlinelibrary.wiley.com/doi/10.1111/ijn.13196

위 목록은 출발점이지 폐쇄된 목록이 아니다. 각 출처에서 참고문헌과 관련 trial registry를 추적하고, 새로운 출처는 중복·직접성·품질을 평가한 뒤 추가한다.

## 6. 모든 문헌에 적용할 표준 데이터 스키마

각 논문/보고서마다 다음 필드를 채운다.

`source_id | full_citation | DOI/URL | source_type | evidence_type | evidence_quality | directness_to_MAJUNG | population | inclusion/exclusion | enrolled/randomized/analyzed n | intervention | comparator | exposure details | registry/protocol match | primary endpoint | secondary/exploratory endpoints | effect estimate | CI | p-value | denominator/analysis set | adverse-event code | limitations/bias | exact source locator | fact vs author interpretation vs MAJUNG inference | unresolved questions | reviewer/status/date`

- Evidence type, evidence quality, directness는 하나의 종합점수로 합치지 않는다.
- 분자/분모와 분석집단을 분리한다. 단위·시간창·RMS/peak·absolute/relative difference를 생략하지 않는다.
- 결과가 논문 본문, 표, 보충자료, trial registry에서 다르면 각각 기록하고 차이를 설명한다.
- 그림의 막대 길이로 수치를 추정하지 않는다. 보충자료를 못 봤다면 못 봤다고 적는다.
- 저자 결론을 그대로 복사하지 말고 원자료 수치와 일치하는지 확인한다.

## 7. 저장소에 반영할 산출물과 파일 경로

기존 파일을 중복 생성하지 말고 먼저 색인과 폴더를 확인한 뒤 적합한 파일을 업데이트한다. 새 파일은 아래 경로/이름을 기준으로 한다.

1. `docs/MAJUNG_GEMINI_BATCH_RESEARCH_EXECUTION_PACKAGE_2026-10-13.md` — 이 실행 패키지.
2. `docs/MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md` — source inventory, DOI/URL, source type, population, directness, status.
3. `docs/MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md` — 논문별 수치·분모·locator·AE 코딩 통합표.
4. `docs/MAJUNG_CLAIM_EVIDENCE_GAP_EXPERIMENT_MATRIX_2026-10-12.md` — 새 문헌과 gap/시험을 반영해 기존 문서를 업데이트.
5. `docs/MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md` — 출력 특성화·공학 안전 시험.
6. `docs/MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md` — 연구 질문·endpoint·설계·통계·윤리.
7. `docs/MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md` — 검증된 기관/연구자 후보.
8. `docs/MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md` — 1-page concept note, 첫 메일, 미팅 질문.
9. `docs/MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md` — Gate 0–5, go/no-go, Claim 제한.
10. `docs/MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md` — 수행한 검색, 쿼리, 열어본 원문, 미확인 사항, 후속작업.
11. 기존 `docs/MAJUNG_INDEX.md`, synthesis/decision register, status matrix, session log, Issue #3에 링크와 진행 상태를 업데이트한다.

중복 문서가 이미 존재하면 새 파일을 만들지 말고 기존 파일을 업데이트하거나 실행 패키지에서 기존 문서로 연결한다. 대량 원문 PDF는 저작권·저장소 용량을 고려해 임의로 커밋하지 않는다. URL/DOI, 적법한 보관 위치, 필요한 경우 사용자가 제공한 PDF의 page locator를 기록한다. 민감한 개인 데이터나 영아 식별 정보는 저장소에 올리지 않는다.

## 8. GitHub 반영 규칙

1. 조사 전에 repo의 default branch, 현재 HEAD, `docs/MAJUNG_INDEX.md`, 기존 파일 목록, Issue #3을 확인한다.
2. 먼저 기존 문서와 중복 여부를 검사한다. 기존 판단을 조용히 덮어쓰지 말고 변경 이유를 decision log에 남긴다.
3. 파일명은 영문 대문자/날짜/주제 규칙을 유지한다. 문서 본문은 자연스러운 한국어, 핵심 과학 용어는 필요 시 영문 병기.
4. 핵심 숫자는 원문 locator가 있을 때만 확정값으로 표시한다. 미확인은 별도 목록으로 관리한다.
5. 수정 파일마다 커밋 메시지를 구체적으로 작성한다. 가능하면 작업 패키지 단위로 논리적 커밋을 만든다.
6. 직접 GitHub write 권한과 저장소 연결이 있으면 실제 파일을 반영하고 commit SHA/URL을 검증한다. 권한이 없으면 “푸시 완료”라고 말하지 말고 각 파일의 완전한 Markdown 본문을 경로별로 제공해 사용자가 커밋할 수 있게 한다.
7. 쓰기 전에 최신 파일을 다시 읽어 SHA/충돌을 확인한다. 동일 파일에 대한 동시 업데이트를 하지 않는다.
8. 완료 후 index의 링크, markdown table 렌더링, source locator, issue comment, commit history를 확인한다. 생성 시도와 성공 검증을 구분한다.
9. 최종 요약은 `완료 / 부분 완료 / 미완료 / 근거 부족`로 나누고 다음 단계와 막힌 이유를 기록한다.

## 9. Gemini의 조사 행동 강령

- 계획 단계에서 멈추지 말고 조사·추출·대조·문서화까지 진행한다. 사용자에게 중간 승인이나 추가 질문을 반복하지 않는다. 필요한 정보가 없으면 가정을 명시하고 `미결정`으로 처리한다.
- 먼저 기존 repo 문서를 읽고 이미 끝난 일을 처음부터 반복하지 않는다.
- 검색 결과 요약만으로 결론을 내리지 않는다. 핵심 결과는 원문 PDF/HTML, 보충자료, registry를 확인한다.
- 각 주장에 직접 근거를 붙인다. DOI, 공식 URL, page/section/table/figure locator를 명시한다.
- 출처가 서로 충돌하면 합치지 말고 충돌표를 만든다.
- 논문에 없는 표본 수, 안전 한계, 통계량, 규제 판단, 연락처를 생성하지 않는다.
- 저널 논문, FDA 규제 요약, trial registry, 보도자료, 저자 주장, MAJUNG에 대한 자체 추론을 구분한다.
- 연구가 NOWS 또는 미숙아에 한정되면 일반 영아로 외삽하지 않는다.
- 연구 수가 많다는 이유로 효능이 입증됐다고 말하지 않는다. 서로 다른 기기·자극·대상·endpoint를 메타분석처럼 합산하지 않는다.
- null/negative results, 조기 종료, 낮은 표본, 비눈가림, 결측, 사후 분석을 본문과 요약 모두에서 유지한다.
- 인간 대상 연구를 즉시 수행하라고 지시하지 않는다. 기관 연구자, IRB, 법·규제, 위험관리 검토가 선행돼야 한다.
- 검색을 무한히 확장하지 않는다. 우선순위와 종료 기준을 지키고, 남은 불확실성을 명시한다.

## 10. WP-0 완료 조건과 작업 종료 기준

WP-0는 아래 모두를 충족해야만 완료다.
- E001-A~F 및 새로 추가한 핵심 문헌의 주요 수치에 추적 가능한 원문 locator가 있다.
- enrolled/randomized/analyzed 및 하위 분석 분모가 구분됐다.
- 등록된 primary outcome, 논문 보고 outcome, exploratory/subgroup 분석이 분리됐다.
- AE 보고 상태가 표준 코드로 기록됐다.
- Evidence type, quality, directness가 분리됐다.
- null/negative 결과와 미수집 데이터가 보존됐다.
- 보충자료와 PDF printed-page 확인 상태가 명확하다.
- 독립 검토가 수행됐는지 명시돼 있다.
- 모든 남은 항목이 미결정 목록으로 기록됐다.

WP-0를 완료하지 못해도 WP-1 이후의 초안 작성은 진행할 수 있다. 다만 미검증 수치에 의존하는 결론을 확정하지 말고, 각 산출물에 선행 불확실성을 표시한다.

---

# Gemini Deep Research에 한 번에 붙여넣을 실행 프롬프트

아래 프롬프트 전체를 Gemini Deep Research에 그대로 붙여넣어 실행한다.

---

너는 MAJUNG(마중 스마트 배시넷) 프로젝트의 연구 총괄 보조자다. 이 작업은 문헌 요약이 아니라 **기존 근거를 원문 수준에서 검증하고, 효과·안전성 근거의 빈틈을 정리한 뒤, 시험·임상 연구·기관 협업·제품 Claim 판단까지 이어지는 실행 가능한 연구 패키지를 만드는 일**이다. 가능한 범위에서 한 번의 Deep Research 작업 안에서 모든 work package를 순서대로 수행하고, 불필요한 확인 질문을 하지 마라.

## 필수 시작 지점
- Repository: https://github.com/youngseokchomajn-web/MAJN_GEMINI
- Index: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_INDEX.md
- Synthesis: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_PROJECT_SYNTHESIS_AND_DECISION_REGISTER_2026-10-13.md
- Extraction matrix: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001_STANDARDIZED_EXTRACTION_STATUS_MATRIX_2026-10-13.md
- Claim/evidence matrix: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_CLAIM_EVIDENCE_GAP_EXPERIMENT_MATRIX_2026-10-12.md
- Master plan: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_RESEARCH_AND_EXPERIMENT_MASTER_PLAN_2026-10-12.md
- Endpoint plan: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_ENDPOINT_MEASUREMENT_AND_EVENT_LOGGING_PLAN_2026-10-12.md
- Researcher question set: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_CLINICAL_RESEARCHER_REVIEW_QUESTION_SET_2026-10-13.md
- Ongoing work issue: https://github.com/youngseokchomajn-web/MAJN_GEMINI/issues/3

먼저 위 문서와 링크된 extraction/locator audit 문서를 읽고, 현재 파일 목록과 최신 커밋을 확인하라. 기존 문서를 무시하고 별도의 새 조사로 시작하지 마라. 기존 문서에 없는 새 자료만 추가하고, 변경은 이유와 함께 기록하라.

## 절대 원칙
1. 최우선 목표는 진동 모듈의 판매 가능한 효과·안전 근거 구축과 연구기관 협업 준비다. 하드웨어 구현은 그 목적을 지원하는 수단일 뿐이다.
2. 일반 건강 영아의 calming, crying reduction, settling, sleep improvement를 입증했다고 선결론 내리지 마라.
3. 임상 효능, 물리 출력, 안전성, 규제 적합성, 마케팅 Claim을 각각 다른 검증 게이트로 다뤄라.
4. 건강한 만삭 영아, 미숙아, NOWS/산전 opioid 노출 신생아, 시술 통증, 동물·가축 연구를 분리하라.
5. vibration, rocking, swaddling, white noise, massage, skin-to-skin 복합중재를 구분하라.
6. null/negative findings, 넓은 CI, 조기 종료, 작은 표본, 비눈가림, 결측, post-hoc subgroup을 숨기지 마라.
7. source fact, author interpretation, MAJUNG inference를 분리하라.
8. 핵심 수치마다 DOI/URL + PDF printed page + section + table/figure/eTable + row/column을 기록하라. HTML locator는 보조 필드로 둔다. 모르면 미확인으로 남겨라.
9. enrolled/randomized/analyzed n과 각 subgroup의 분모를 분리하고, 단위·시간창·RMS/peak·absolute/relative effect를 정확히 유지하라.
10. adverse event를 reported / authors reported none / not reported / not assessed / unclear로 구분한다. 미기재를 “안전했다”로 해석하지 마라.
11. 원문/보충자료/ClinicalTrials.gov/FDA 공식 자료를 우선한다. 논문과 registry가 다르면 차이를 표로 남겨라.
12. 임상 영아 연구는 기관·임상 연구진, IRB/윤리심의, 규제 검토, 사전 안전계획 없이 실행하도록 제안하지 마라.
13. Gemini가 GitHub write 권한이 없는 경우 절대 push 완료라고 주장하지 마라. 그 경우 파일 경로별 완전한 Markdown 본문과 수동 반영 절차를 출력하라.
14. 추가 질문 없이 최대한 진행하되, 결정되지 않은 제품 요구사항이나 부족한 자료는 명시적으로 미결정으로 남겨라.

## 반드시 수행할 work packages

### A. 기존 자료 감사 및 WP-0 완료
- E001-A Smith 2015, E001-B Bloch-Salisbury 2009, E001-C Zuzarte 2017, E001-D Prapela FDA De Novo, E001-E Bloch-Salisbury 2023, E001-F Singh 2025/2026를 다시 확인한다.
- E001-A: Table 2 p.e1566, adverse-event 문구 p.e1565로 기록된 locator를 원문과 재대조한다.
- E001-B: Table 2 p.1021, Figure 6 p.1024 locator를 재대조한다.
- E001-C: PLOS Table 2 PDF p.9/15 및 article-number convention을 확인한다.
- E001-E/F: 정확한 journal printed page, 표·그림·보충자료, 각 주요 수치와 AE 문구를 원문 PDF 기준으로 대조한다.
- E001-F: Singh et al. DOI 10.1038/s41390-025-04162-2, https://pmc.ncbi.nlm.nih.gov/articles/PMC13134440/, trial NCT04834297. Planned n=120이었으나 n=62에서 조기 종료된 사실, primary comparison의 비유의성, cry subset n=46의 null results를 정확히 유지한다.
- 원문을 열지 못한 수치는 verified로 표기하지 않는다. WP-0 종료 조건이 미충족이면 open으로 남긴다.

### B. 새 문헌 검색 및 evidence map
다음 영역을 검색하되 서로 다른 직접성을 구분한다:
- healthy term infant calming/crying/settling/sleep에 대한 직접 연구
- vibration/crib mattress/bassinet vibration의 임상·공학·안전 근거
- preterm infant physiologic stabilization
- NOWS/neonatal opioid withdrawal syndrome
- procedural pain/local vibration
- rocking/automated bassinet/white noise/swaddling 등 복합 중재
- infant sleep measurement, actigraphy/video coding, sleep-state validation
- 안전 표준, 제품 분류, 의료기기/소비재 규제와 광고 Claim의 공식 자료
- 관련 systematic reviews, registered/ongoing/terminated trials, negative studies
각 연구를 population, stimulus, comparator, endpoint, design, result, quality, directness, limitations, locator로 정리한다.

### C. Claim–Evidence–Gap–Experiment 매트릭스
각 잠재 Claim에 대해 다음을 채운다:
- claim wording (강도별: 현재 말할 수 있음 / 조건부 / 아직 말할 수 없음)
- supporting evidence and counterevidence
- evidence type / quality / directness (분리)
- evidence gap
- required bench or clinical test
- measurable endpoint
- pass/fail/hold criterion, 근거와 함께
- responsible expert/organization needed
- regulatory/marketing caution
어떤 Claim이든 근거가 약하면 “보류”를 권고할 수 있어야 한다.

### D. 물리 출력·공학 안전 시험 계획
MAJUNG의 실제 actuator와 mounting/bed surface/load 조건을 고려해 출력 파형, frequency, acceleration/displacement, RMS/peak, startup/shutdown transient, spatial uniformity, load dependence, sound, heat, fixation, cord/entrapment, electrical/mechanical failure modes를 다룬다.
측정기의 bandwidth, sample rate, calibration, mounting, noise floor, uncertainty, repeatability를 명시한다. 임의의 infant-safe threshold를 만들지 않는다. 현재 장치의 미결정 사양을 목록화한다.

### E. 연구 설계 및 프로토콜 synopsis
후보 질문은 “통상적인 적절한 돌봄을 유지한 상태에서 MAJUNG 진동 추가가 사전 정의한 settling time 또는 crying/fussing duration을 변화시키는가?”다. 최종 population과 endpoint는 연구자 검토 전까지 미확정으로 둔다.
- primary endpoint 후보와 객관적 operational definition
- secondary/exploratory outcomes
- comparator, randomization, blinding feasibility
- clinically meaningful effect size와 sample-size/power 접근
- missing data, multiplicity, analysis set
- safety monitoring, AE definitions, stopping rules
- protocol registration, IRB, consent, data privacy
- sensor/video/actigraphy validity와 진동에 의한 measurement artifact
- feasibility study와 confirmatory RCT의 구분
실제 연구를 승인 없이 시행하라는 문구를 쓰지 않는다.

### F. 한국 연구기관·연구자 shortlist
공식 기관 페이지와 최근 관련 논문으로 후보를 검증한다. 소아/신생아 임상, 수면·행동 측정, 생체신호, 기계·제어·진동 계측, 의료기기 규제 전문가를 구분한다. 후보별 소속, 근거 URL, 연구 적합성, 제안 질문, 연락 우선순위를 표로 만든다. 개인 이메일/직함/협업 의사를 추정하지 않는다. 기존에 언급된 조재소, 이병섭, 김수현은 동명이인·소속·연구 분야를 공식 출처로 확인한 뒤에만 후보에 넣는다.

### G. 협업·실행 패키지
- 1-page concept note
- 연구자 첫 접촉 이메일(과장 없는 한국어)
- 30분 미팅 질문 목록
- 제공 가능한 장치/데이터/측정 정보 목록
- 이해상충, IP, 데이터 소유·공유, 연구비/장치 제공 조건 체크리스트
- Go/No-Go decision gates 0–5
- 다음 2주간 우선순위와 각 작업의 산출물·완료 기준

## 필수 시작 문헌/링크
- Singh et al. 2025/2026: https://doi.org/10.1038/s41390-025-04162-2 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC13134440/ ; https://clinicaltrials.gov/study/NCT04834297
- Bloch-Salisbury et al. 2023: https://doi.org/10.1001/jamapediatrics.2023.1077 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10186209/
- Smith et al. 2015: https://doi.org/10.1542/peds.2015-1334 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4657600/
- Bloch-Salisbury et al. 2009: https://pmc.ncbi.nlm.nih.gov/articles/PMC2763836/
- Zuzarte et al. 2017: https://doi.org/10.1371/journal.pone.0175981 ; https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175981
- FDA Prapela De Novo: https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240031.pdf
- SNOO registry: https://clinicaltrials.gov/study/NCT05711927
- Contours Vibes: https://pmc.ncbi.nlm.nih.gov/articles/PMC8889968/
- Huhtala et al. 2000: https://pubmed.ncbi.nlm.nih.gov/10835097/
- Emori et al. 1995: https://www.jstage.jst.go.jp/article/jje1965/31/6/31_6_369/_article/-char/en
- Catal et al. 2024: https://pubmed.ncbi.nlm.nih.gov/39394025/
- Poets et al. 2024: https://pubmed.ncbi.nlm.nih.gov/38760904/
- Korean skin-to-skin protocol (design reference only): https://pmc.ncbi.nlm.nih.gov/articles/PMC12519669/
- Actigraphy review: https://onlinelibrary.wiley.com/doi/10.1111/ijn.13196

## 저장소 산출물
기존 문서가 있으면 중복 생성하지 말고 업데이트한다. 최소 산출물:
1. source register
2. E001-A~F + 신규 논문 standardized extraction master table
3. claim/evidence/gap/experiment matrix
4. engineering output and bench test plan
5. clinical research protocol synopsis
6. verified Korea researcher shortlist
7. researcher outreach package
8. decision gates/claim rules
9. Gemini research run log
10. index, synthesis/decision register, status matrix, session log, Issue #3 update

제안 경로는 `docs/MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md`, `docs/MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md`, `docs/MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md`, `docs/MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md`, `docs/MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md`, `docs/MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md`, `docs/MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md`, `docs/MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md`.

각 파일은 독립적으로 읽을 수 있어야 하고, 상호 링크와 source locator를 포함해야 한다. 최종적으로 index를 업데이트하고, Issue #3에 변경 사항·미해결 항목·다음 행동을 기록한다. 실제 GitHub 반영이 불가능하면 push했다고 말하지 말고 파일별 완전한 본문과 경로를 출력한다.

## 최종 보고 형식
1. Executive summary: 무엇이 확실하고 무엇이 아직 불확실한가.
2. Current evidence table: claim / strongest evidence / null or counterevidence / directness / confidence / unresolved.
3. Source locator audit status: verified / partial / unverified.
4. Claim–Evidence–Gap–Experiment matrix.
5. Engineering bench plan.
6. Clinical research synopsis and ethics/regulatory gates.
7. Verified Korea collaborator shortlist.
8. Researcher outreach package.
9. GitHub changes: exact paths, commit SHAs/URLs if truly committed, otherwise ready-to-paste Markdown.
10. Remaining risks, unknowns, and next 2-week actions.
11. WP-0 status and explicit criteria not yet met.

작업을 계획만 제시하고 끝내지 마라. 가능한 범위에서 원문 확인, 표 작성, 파일 문서화까지 수행하라. 근거가 부족한 부분은 그 자체를 결과로 기록하라.
