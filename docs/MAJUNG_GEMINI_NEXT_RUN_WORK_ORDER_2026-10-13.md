# MAJUNG Gemini 다음 실행 작업지시서 — WP-0 문헌 locator 정합성 마감

작성일: 2026-10-13  
버전: 1.0  
상태: **다음 Gemini 실행용 작업지시서 — WP-0는 아직 Partial**  
저장소: https://github.com/youngseokchomajn-web/MAJN_GEMINI

## 0. Gemini에 줄 작업 범위

이번 실행은 프로젝트 전체를 처음부터 다시 조사하는 작업이 아니다. 이미 작성된 자료를 기준으로 **핵심 1차 문헌 E001-C, E001-E, E001-F의 남은 원문 대조를 완료 가능한 범위까지 수행하고, 파일 간 상태를 일치시키는 것**이 목표다.

완료를 선언하는 것보다 불확실성을 정확히 기록하는 것이 우선이다. 자료에 접근하지 못하거나 최종 PDF/보충자료를 확인하지 못하면 추측으로 채우지 말고 `Partial` 또는 `Unresolved`로 남긴다.

## 1. 프로젝트 원칙 — 반드시 유지

1. 최우선 목표는 진동 하드웨어를 구현하는 것 자체가 아니라, MAJUNG을 판매하기 전에 진동 모듈의 효과·안전성 주장을 뒷받침할 근거를 만드는 것이다.
2. 일반 건강 영아의 진정·울음 감소·settling·수면 개선 효과는 현재 MAJUNG에서 입증되지 않았다.
3. 미숙아, 산전 opioid 노출/NOWS 신생아, 건강 만삭 영아, 시술 통증 대상군의 결과를 서로 대체하지 않는다.
4. 진동 매트리스의 stochastic stimulation, 국소 진동, 흔들기/rocking, 백색소음·속싸개 등 복합중재를 같은 자극으로 취급하지 않는다.
5. 임상 효능, 물리 출력, 공학적 위험, 장기 안전성, 규제 적합성은 각각 다른 증거 영역이다.
6. 부정적·무효 결과, 신뢰구간, 하위집단 분석, 누락 데이터, 이상사례 보고의 한계를 삭제하거나 축약해 긍정적 결론으로 바꾸지 않는다.
7. 연구 계획서·설계안·시험 프로토콜은 시험 결과가 아니다. MAJUNG 자체의 bench test가 실행됐다는 원자료가 없으면 완료로 쓰지 않는다.
8. 영아 대상 연구는 임상 책임자, 기관의 윤리·규제 검토 및 필요한 승인 전 실행을 권하지 않는다.

## 2. 반드시 먼저 읽을 파일

- Index: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_INDEX.md
- 전체 종합·결정 기록: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_PROJECT_SYNTHESIS_AND_DECISION_REGISTER_2026-10-13.md
- 통합 구조 재분석: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_INTEGRATED_STRUCTURAL_REANALYSIS_2026-10-13.md
- 표준 추출 상태표: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001_STANDARDIZED_EXTRACTION_STATUS_MATRIX_2026-10-13.md
- 근거 추출 마스터 테이블: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md
- 실행 로그: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md
- E001-C Zuzarte 2017: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001C_ZUZARTE_2017_PRIMARY_EXTRACTION_2026-10-08.md
- E001-E Bloch-Salisbury 2023 RCT: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001E_BLOCH_SALISBURY_2023_RCT_PRIMARY_EXTRACTION_2026-10-08.md
- E001-F Singh 2025 online / 2026 issue: https://github.com/youngseokchomajn-web/MAJN_GEMINI/blob/main/docs/MAJUNG_E001F_SINGH_2026_NOWS_RCT_PRIMARY_EXTRACTION_2026-10-13.md

## 3. 실행 순서

### WP-0C — E001-C Zuzarte 2017 수치별 대조

공식 원문:
- Publisher/PLOS ONE: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175981
- PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC5398650/

현재 문서에는 PDF의 주요 위치가 추가됐지만, 모든 수치의 행 단위 전사 및 독립 2차 검토는 끝나지 않았다.

해야 할 일:
- Abstract, Methods, Table 1–3, Figure 1–2, Results, Discussion/Conclusions를 PDF와 대조한다.
- 각 핵심 숫자에 대해 `claim | 정확한 값/단위 | 분자/분모 | 대상 분석집단 | PDF printed page | section/table/figure/row | HTML locator | 해석 한계`를 기록한다.
- ON/OFF 비교가 within-subject임을 유지하고, 30분 블록·예외·동시 morphine/phenobarbital 등 시간 변화와 병행 처치 한계를 표시한다.
- movement activity 감소를 sleep 또는 healthy-infant soothing endpoint로 바꾸지 않는다.
- adverse-effect 문구를 정확히 인용/요약하고, 연구 대상·노출시간·표본 범위에 한정한다.
- 이전 기록과 불일치하는 수치가 있으면 조용히 덮어쓰지 말고 discrepancy log에 기존 값/원문 값/해결 상태를 적는다.

### WP-0E — E001-E Bloch-Salisbury 2023 RCT PDF·보충자료 대조

공식 원문:
- JAMA Pediatrics: https://jamanetwork.com/journals/jamapediatrics/fullarticle/2804943
- PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC10186209/
- DOI: https://doi.org/10.1001/jamapediatrics.2023.1077

해야 할 일:
- 최종 출판 PDF의 실제 인쇄 페이지를 확인해 Abstract, Figure 1, Tables 2–3, Figure 2 및 관련 eTables/eFigures의 위치를 정규화한다.
- 등록 208, 무작위 배정 104/104, 분석 87/94/총 181의 분모 차이를 각 결과와 연결한다.
- 전체 무작위군 morphine treatment 비교(31/87=35.6% 대 29/94=30.9%, P=.60)를 눈에 띄게 유지한다.
- exposure-duration association, morphine 투여 하위집단, 3주 내 치료 완료 responder subgroup을 전체 무작위군의 primary result와 분리한다.
- 보충자료를 실제 열어보고 파일명, 표/그림 번호, 해당 결과, PDF page를 기록한다. 파일을 열 수 없으면 미확인으로 남긴다.
- adverse-event/AE 표현, 6/58 shutdown 관찰 및 rebound 관련 문구는 원문 정의·분모·시간 맥락을 재확인한다. 인과관계를 과장하지 않는다.
- primary/secondary/exploratory/subgroup와 multiplicity 관련 문구를 논문 원문대로 분리한다.

### WP-0F — E001-F Singh 2025/2026 RCT PDF·보충자료 대조

공식 원문:
- Nature/Pediatric Research: https://www.nature.com/articles/s41390-025-04162-2
- PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC13134440/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/40410582/
- Trial registry: https://clinicaltrials.gov/study/NCT04834297

현재 남은 사항:
- 최종 출판 PDF의 개별 표·그림 인쇄 페이지는 기존 문서에서 잠정 매핑으로만 기록돼 있다.
- `NIHMS2106170-supplement-Supplementary_Files.pdf`의 실제 내용은 아직 검토되지 않았다.

해야 할 일:
- 최종 출판 PDF를 열어 Figure 1, Tables 2–4, primary outcome, discharge readiness, cry results, acceptability 및 adverse-event 문구의 정확한 printed page를 확인한다.
- 보충자료 PDF를 열어 Supplemental Table S1/Figure S1의 실제 내용, 분모, 누락 데이터, 분석집단, page를 기록한다.
- 62명 전체, 무작위 배정군(SVS 40/control 22), cry subset(n=46; SVS 32/control 14)을 결과별로 분리한다.
- 조기 종료와 계획 표본수 120 대 실제 62명을 표시한다.
- primary endpoint의 4/40 대 4/22, adjusted OR 0.54 (95% CI 0.10–2.85), P=.46 결과를 유의한 효능 입증으로 표현하지 않는다.
- 주관적 caregiver/nurse acceptability와 객관적 cry/clinical outcome을 분리한다.
- “adverse events not observed”를 이 연구의 표본·단기 병원 관찰에 한정한다.

## 4. 공통 추출 스키마

각 claim별로 아래 필드를 유지한다.

`source_id | claim_id | exact_value | unit | numerator | denominator | analysis_population | endpoint_role | printed_page | section | table_figure_row | HTML_anchor | DOI_URL | author_interpretation | MAJUNG_inference_boundary | verification_status | reviewer_note`

규칙:
- `printed page`와 HTML anchor/브라우저 줄 번호를 혼용하지 않는다.
- PDF 인쇄 페이지를 실제로 보지 못했다면 숫자를 추정하지 않는다.
- denominator가 해당 결과에 적용되지 않으면 `N/A`; 원문에 없으면 `not reported`; 아직 확인 못 했으면 `unverified`로 구분한다.
- adverse-event 상태는 `reported / none reported / not reported / not assessed / unclear` 중 원문에 맞는 값으로 코딩한다.
- 논문 저자의 해석과 Gemini의 MAJUNG 적용 추론은 별도 필드다.
- 각 논문의 출처를 다른 논문·FDA 요약으로 대신하지 않는다. FDA 요약은 보조 출처로 별도 표시한다.
- 외부 독립 검토를 실제로 받지 않았다면 `independently checked`로 표시하지 않는다.

## 5. 저장소 반영할 파일

최소한 아래를 동기화한다.
1. E001-C/E001-E/E001-F 각각의 primary extraction 문서
2. `MAJUNG_E001_STANDARDIZED_EXTRACTION_STATUS_MATRIX_2026-10-13.md`
3. `MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md`
4. `MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md`
5. `MAJUNG_PROJECT_SYNTHESIS_AND_DECISION_REGISTER_2026-10-13.md`
6. `MAJUNG_INDEX.md) — 링크 또는 현재 상태 요약이 실제로 바뀌는 경우에만 수정

같은 정보를 복제한 새 보고서를 대량 생성하지 않는다. 기존 문서를 갱신하고, 별도 파일은 discrepancy log나 명확한 새 근거가 필요할 때만 만든다.

## 6. GitHub 업데이트 및 품질 확인

- 작업 전에 현재 branch와 최신 파일을 확인한다. 저장소의 현재 기본 브랜치에 직접 반영할 권한/환경이 없으면 수정했다고 주장하지 않는다.
- 각 파일 변경 후 GitHub에서 다시 읽어 변경 사항이 실제로 저장됐는지 확인한다.
- 변경한 파일, 변경 요약, 실제 commit SHA와 URL을 실행 로그에 기록한다.
- 원문을 직접 확인한 사실과 기존 문서에서 인용한 사실을 구분한다.
- source PDF/보충자료 접근 실패, paywall, 누락된 파일은 그대로 보고하고 추측하지 않는다.
- 상태표, 마스터 테이블, 실행 로그, 종합 문서의 WP-0 상태를 모두 일치시킨다.
- 모든 완료 기준이 충족되지 않으면 WP-0는 `Partial — closure deferred`로 유지한다.

## 7. 이번 실행의 종료 기준

아래 항목별로 `Done / Partial / Blocked / Not started`를 보고한다.
- [ ] E001-C 핵심 수치·분모·표/행·페이지 대조
- [ ] E001-E PDF 인쇄 페이지·분모·보충자료·AE 문맥 대조
- [ ] E001-F PDF 인쇄 페이지·cry subset·보충자료·AE 문맥 대조
- [ ] source-level discrepancies 기록
- [ ] 상태표와 마스터 테이블 정합화
- [ ] 실행 로그와 종합 기록 갱신
- [ ] 실제 GitHub commit SHA 검증
- [ ] 외부 독립 검토 여부를 사실대로 표시

**중요:** Gemini 자체가 재확인했다는 이유만으로 외부 독립 검토 완료로 표시하지 않는다. WP-0 locator 작업의 완료와 임상적 유효성/안전성 입증을 혼동하지 않는다.

## 8. Gemini에 한 번에 붙여넣을 프롬프트

아래를 그대로 실행 지시로 사용한다.

> 너는 MAJUNG 문헌 추적성(WP-0) 담당 연구 보조자다. 먼저 `docs/MAJUNG_GEMINI_NEXT_RUN_WORK_ORDER_2026-10-13.md` 전체와 연결된 기존 문서를 읽어라. 이번 작업은 프로젝트 전체를 처음부터 재조사하는 것이 아니라 E001-C, E001-E, E001-F의 원문 PDF·보충자료 locator 및 수치/분모를 확인하고 문서 간 상태를 정합화하는 것이다.
>
> 공식 원문 링크를 직접 열고, 최종 PDF와 보충자료를 실제로 확인한 항목만 verified로 기록하라. PDF 페이지를 열지 못했으면 인쇄 페이지를 추정하지 말고 unverified로 남겨라. 각 수치의 단위, 분자/분모, 분석집단, primary/secondary/exploratory/subgroup 여부, adverse-event 보고 맥락을 확인하라. 논문 저자의 해석과 MAJUNG에 대한 추론을 분리하라. 건강 영아의 진정·울음·수면 효과로 외삽하지 말라.
>
> 우선 기존 extraction 문서를 수정하고, 그다음 standardized matrix, master table, run log, synthesis를 같은 상태로 갱신하라. 중복 문서를 만들지 말라. 원문 접근 불가, 숫자 불일치, 보충자료 미확인 등 장애물은 discrepancy log에 남겨라. MAJUNG 자체 bench test를 실행한 것처럼 쓰지 말라. 임상 연구 승인이나 외부 독립 검토가 없으면 완료로 쓰지 말라.
>
> 마지막에 변경 파일별 경로·핵심 변경·실제 commit SHA/URL, 확인한 원문 링크, 미해결 항목, WP-0 종료 여부를 보고하라. 모든 종료 기준을 충족하지 못하면 WP-0를 Partial — closure deferred로 유지하라.
