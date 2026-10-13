# MAJUNG E001-A~F 1차 근거 표준 필드·상태 매트릭스
작성일: 2026-10-13

**목적:** E001-A~E001-F 원문 추출을 동일한 필드로 관리하고, 출처 위치가 확인된 항목과 미확인 항목을 구분한다. 이 문서는 원문 전체의 재분석이나 모든 locator의 완료를 선언하지 않는다.

## 1. 공통 추출 스키마

각 source row는 아래 필드를 유지한다. 값이 원문에 없거나 아직 확인되지 않았다면 빈칸을 추정으로 채우지 말고 상태를 기록한다.

| Field | 정의 / 입력 규칙 |
|---|---|
| source_id | E001-A~E001-F |
| full_citation | 저자, 제목, 저널/기관, 연도, 권·호·페이지 또는 문서번호 |
| doi_url | DOI와 원문/공식 URL |
| source_type | peer-reviewed paper / FDA regulatory summary / registry / report |
| evidence_type | engineering output / physiology / behavior / sleep / clinical efficacy / safety / regulatory |
| evidence_quality | 설계, 편향, 표본, 측정 타당성, 보고 완전성에 따른 별도 평가 |
| directness_to_MAJUNG | target population, physical stimulus, endpoint, use environment 각각에 대한 직접성 |
| population | 모집·포함 기준, 임상 맥락, 연령/재태연령 |
| n_enrolled_randomized_analyzed | 분리해서 기록; 흐름도/등록 결과로 확인 |
| intervention_comparator | 활성 중재, 비교 조건, 병행 치료/복합 중재 |
| exposure | 실제 장치, frequency, displacement/acceleration, waveform, dose, duration; 서로 다른 metric을 혼합하지 않음 |
| primary_endpoint | 사전 지정 1차 endpoint를 원문 그대로 기록; 등록/논문 간 차이가 있으면 둘 다 기록 |
| secondary_exploratory_endpoints | 2차, 탐색, 하위집단, 노출량 연관 분석을 분리 |
| result_effect_estimate_uncertainty | 분자/분모, 단위, effect estimate, CI, p-value; 없는 값은 만들지 않음 |
| adverse_event_status | reported / none reported by authors / not reported / not assessed / unclear; 단순 미기재를 '없음'으로 코딩하지 않음 |
| limitations_risk_of_bias | 설계, 선택·측정·보고 편향, 결측, 일반화 한계 |
| source_locator | 핵심 수치별 printed page + section + table/figure/eTable; web HTML line은 보조 locator로 분리 |
| fact_vs_author_interpretation_vs_MAJUNG_inference | 세 층위를 분리해 기술 |
| unresolved_items | 미대조 locator, 불명확한 분모/분석집단, 자료 미수집 등 |
| extraction_status | Draft / partial locator verified / numerical locator verified / independently checked |
| reviewer_date | 검토자 및 날짜; 독립 검토가 없으면 “독립 검토 미실시” |

## 2. 문헌별 현재 상태

| Source | Population / study type | Intervention and comparator | Primary or principal endpoint | Main result to preserve | Safety-reporting code | Locator status | Remaining work |
|---|---|---|---|---|---|---|---|
| E001-A Smith 2015 | 미숙아 36명, 무작위 crossover; apnea/bradycardia/desaturation 이력이 있는 입원 영아 | mattress stochastic resonance stimulation ON vs OFF, alternating 30-min blocks | oxygen desaturation, bradycardia, apnea events | desaturation event count/duration/intensity와 apnea가 감소했지만 bradycardia event count는 개선되지 않았고 intensity 변화가 보고됨. 대상군·생리 endpoint를 유지 | 원문 adverse-event 문구를 재대조해 bounded report로 기록; “일반 영아 안전”으로 외삽 금지 | 핵심 수치별 subsection/Table 2/figures locator 초안 있음; 인쇄 페이지 미정규화 | 각 수치의 printed page/표 행, 분석 분모, 안전성 문구 최종 대조 |
| E001-B Bloch-Salisbury 2009 | 미숙아 10명, 반복 ON/OFF 생리 측정 | 30–60 Hz stochastic mechanosensory mattress; ON vs OFF | IBI variance/prolonged IBI 및 oxygen desaturation time | 호흡 간격 변동과 긴 IBI, 산소탈포화 시간이 감소했으나 건강 영아 진정·수면 효능 endpoint가 아님 | 추출된 문구에서 표준화된 adverse-event 보고가 명확하지 않음; “미확인/불명확” 유지 | 주요 수치의 subsection/Table 2/Figure locator 초안 있음; 인쇄 페이지 미정규화 | adverse event/reporting completeness 확인, printed page, sample flow 및 missing data |
| E001-C Zuzarte 2017 | 산전 opioid 노출 만삭 신생아 26명, 약물치료 중 단일기관 within-subject 연구 | SVS ON/OFF 30-min blocks; 병행 약물치료 지속 | movement activity와 생리 측정 | 움직임 활동 감소 및 일부 호흡/심박 지표 변화; 일반 건강 영아의 진정/수면 결과로 치환 금지 | FDA summary는 해당 자료가 safety support에 기여했다고 설명; 원문 보고 범위로 제한 | 주요 수치별 Table 1/2/Figure 3 및 subsection locator 초안 있음; 인쇄 페이지 미정규화 | 표/행 단위 숫자·단위·분모, adverse-event 문구, co-treatment/confounding 확인 |
| E001-D Prapela FDA De Novo | FDA 규제 요약; NOWS 적응증의 특정 의료기기 | Prapela SVS Hospital Bassinet Pad; 제품별 bench/clinical evidence | 해당 적응증의 임상 성능과 기기 안전성/규제 기준 | 2023 RCT의 전체 무작위 결과와 subgroup 결과를 구분; 2017 자료는 FDA 평가상 effectiveness 입증 endpoint로는 부적절하지만 safety support에 기여 | 제출된 임상 자료 범위에서 adverse events 미관찰 보고; 장기/모든 영아 위험 없음의 증거 아님 | 9-page PDF printed-page locator audit 기록됨 | redacted bench 수치는 미해결로 명시; FDA summary의 모든 주요 표/문장 locator 2차 확인 |
| E001-E Bloch-Salisbury 2023 | 산전 opioid 노출 신생아, randomized clinical trial; 208 enrolled/randomized, 181 analyzed | SVS mattress + treatment as usual vs treatment as usual | morphine treatment administration, cumulative morphine dose, length of stay (논문 Methods/Abstract 기준) | 전체 약물치료 비율 35.6% vs 30.9%, P=.60; exposure-duration association, treated cohort, responder subgroup 별도 분석 | 6/58 shutdown observation을 rebound/causality로 단정하지 않음; adverse event status는 원문 정의대로 제한 | Table 2/3, Figure 1/2, eTable 3/4 + publisher HTML locator 기록됨; 인쇄 페이지 미정규화 | journal PDF page/table locator, multiplicity/statistical analysis plan, adverse event terminology, subgroup status final check |

| E001-F Singh 2025/2026 | 산전 opioid 노출, ≥35주 신생아 62명; 다기관 비눈가림 RCT, 조기 종료 | SVS mattress 40명 vs 표준 매트리스 22명; 30–60 Hz, 10–12 μm RMS | 생후 5일 이내 NOWS 약물치료 시작 | 4/40 (10.0%) vs 4/22 (18.2%); adjusted OR 0.54 (95% CI 0.10–2.85), P=.46. Cry data subset n=46에서 fussy/pain cry 시간 및 cry strength 차이 유의하지 않음 | 저자는 양 군에서 adverse events 미관찰 보고; 단기 병원 관찰·표본 범위로 제한 | Methods/Results, Table 2–4, Fig. 1 위치 확인; 저널 페이지 276–282, 각 표의 정확한 인쇄 페이지 미확인 | 표본 부족·조기 종료, cry subset 분모, 보충자료, adverse-event 맥락, PDF 인쇄 페이지, 독립 검토 확인 |\n\n## 3. Evidence type / quality / directness 분리 예시

이 필드들은 서로 다른 질문에 답하므로 합쳐서 한 점수로 만들지 않는다.

- **Evidence type:** 실제로 무엇을 측정했는가? 예: 미숙아의 호흡 생리, 움직임 활동, NOWS 약물치료, 수면 상태 분포.
- **Evidence quality:** 해당 연구의 질문에 대한 결과가 얼마나 신뢰 가능한가? 예: crossover 구조의 적절성, 표본 규모, 평가 눈가림, 결측, 분석 사전 지정 여부.
- **Directness:** 그 결과가 MAJUNG의 목표 Claim에 얼마나 직접적인가? 예: 대상군, 자극 방식, endpoint, 가정용 환경의 차이.
- 높은 연구 품질이어도 MAJUNG의 일반 영아 진정 Claim에 대한 직접성은 낮을 수 있다. 규제상 허가/De Novo 판단 역시 MAJUNG 제품의 허가나 일반 Claim을 대신하지 않는다.

## 4. Locator 표준

각 핵심 수치는 아래 형식으로 기록한다.

`source_id | claim_id | exact value + unit | population/analysis set | printed page | section | table/figure row | DOI/URL | verification status`

- HTML line number는 재접근에 유용한 보조 정보지만 printed journal page와 동일시하지 않는다.
- PDF 인쇄 페이지를 확인하지 못했으면 “미확인”으로 둔다.
- figure의 시각적 막대 길이로 정확한 숫자를 추정하지 않는다.
- 분모, analysis set, 시간 단위, RMS/peak/max, absolute/relative difference를 생략하지 않는다.
- 수치가 원문 본문·표·부록 사이에서 다르면 각 위치와 정의를 모두 기록하고, 임의로 하나로 통합하지 않는다.

## 5. WP-0 종료 게이트

WP-0는 다음 항목이 충족된 뒤에만 완료로 표시한다.

1. 모든 핵심 결과 수치가 원문 페이지·섹션·표/그림까지 추적 가능하다.
2. enrolled/randomized/analyzed 및 각 분석의 분모가 구분돼 있다.
3. primary endpoint, secondary endpoint, exploratory/subgroup/exposure association이 구분돼 있다.
4. adverse event가 reported / none reported / not reported / not assessed / unclear 중 정확히 코딩돼 있다.
5. Evidence type, quality, directness가 별도 필드로 존재한다.
6. null/negative findings와 미수집 결과가 유지된다.
7. 독립 검토 여부가 기록돼 있다.

**현재 판정: WP-0 진행 중.** 이 문서는 통일 스키마와 현재 상태를 고정한다. E001-A~F 핵심 숫자의 printed-page locator 대조 및 독립 검토가 끝나지 않았으므로 완료로 처리하지 않는다.

## 6. 제품 주장에 대한 현재 제한

E001-A~E001-E는 대부분 미숙아 또는 산전 opioid 노출 신생아의 생리·임상 맥락을 다룬다. 이 자료는 물리 출력 시험 방법과 향후 연구 설계에는 유용하지만, MAJUNG이 일반 건강 영아의 울음·settling·수면을 개선한다는 직접 증거로 분류할 수 없다.
