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
| E001-A Smith 2015 | 미숙아 36명, 무작위 crossover; apnea/bradycardia/desaturation 이력이 있는 입원 영아 | mattress stochastic resonance stimulation ON vs OFF, alternating 30-min blocks | oxygen desaturation, bradycardia, apnea events | desaturation event count/duration/intensity와 apnea가 감소했지만 bradycardia event count는 개선되지 않았고 intensity 변화가 보고됨. 대상군·생리 endpoint를 유지 | 원문 adverse-event 문구를 재대조해 bounded report로 기록; “일반 영아 안전”으로 외삽 금지 | Results/Table 2 핵심 locator 확인; Table 2 p.e1566, adverse-event 문구 p.e1565; 일부 수치별 독립 대조 미완료 | 각 수치의 printed page/표 행, 분석 분모, 안전성 문구 최종 대조 |
| E001-B Bloch-Salisbury 2009 | 미숙아 10명, 반복 ON/OFF 생리 측정 | 30–60 Hz stochastic mechanosensory mattress; ON vs OFF | IBI variance/prolonged IBI 및 oxygen desaturation time | 호흡 간격 변동과 긴 IBI, 산소탈포화 시간이 감소했으나 건강 영아 진정·수면 효능 endpoint가 아님 | 추출된 문구에서 표준화된 adverse-event 보고가 명확하지 않음; “미확인/불명확” 유지 | Table 2 p.1021, Figure 6 p.1024 확인; 물리 출력 subsection 페이지와 전체 adverse-event 보고 확인 미완료 | adverse event/reporting completeness 확인, printed page, sample flow 및 missing data |
| E001-C Zuzarte 2017 | 산전 opioid 노출 만삭 신생아 26명, 약물치료 중 단일기관 within-subject 연구 | SVS ON/OFF 30-min blocks; 병행 약물치료 지속 | movement activity와 생리 측정 | 움직임 활동 35% 상대 감소 (14%p 절대 감소, P<.001); 지속 움직임(>5s, ≥30s) 감소; 심박/호흡 안정; SaO2/체온 유지. 일반 영아 진정/수면 효능 아님 | 저자는 본 세션에서 adverse effects 미발생 보고, 추가 연구 필요 명시. 간호사/부모의 "안정/수면" 보고는 anecdotal(일화적)임. 일반 영아 안전 외삽 금지 | Publisher PDF(x/15) 대조 완료: Abstract p.1, Table 1 pp.3–4, Methods p.4, Fig 1 p.5, Fig 2 p.6, Table 2 pp.7–9, Fig 3 p.8, Table 3 p.10, AE discussion p.11 | 수치별 대조 완료. 외부 독립 2차 검토(Independent second-review) 미실시; 동시 morphine/phenobarbital 병행 한계 |
| E001-D Prapela FDA De Novo | FDA 규제 요약; NOWS 적응증의 특정 의료기기 | Prapela SVS Hospital Bassinet Pad; 제품별 bench/clinical evidence | 해당 적응증의 임상 성능과 기기 안전성/규제 기준 | 2023 RCT의 전체 무작위 결과와 subgroup 결과를 구분; 2017 자료는 FDA 평가상 effectiveness 입증 endpoint로는 부적절하지만 safety support에 기여 | 제출된 임상 자료 범위에서 adverse events 미관찰 보고; 장기/모든 영아 위험 없음의 증거 아님 | 9-page PDF printed-page locator audit 기록됨 | redacted bench 수치는 미해결로 명시; FDA summary의 모든 주요 표/문장 locator 2차 확인 |
| E001-E Bloch-Salisbury 2023 | 산전 opioid 노출 신생아, randomized clinical trial; 208 enrolled/randomized, 181 analyzed | SVS mattress + treatment as usual vs treatment as usual | morphine treatment administration, cumulative morphine dose, length of stay (논문 Methods/Abstract 기준) | 전체 약물치료 비율 35.6% vs 30.9%, P=.60 (비유의); exposure-duration aOR 0.88 (95% CI 0.81–0.93); 반응군(≤21일) 3.18일 단축; 비반응군(>21일) 유의차 없음 | 6/58 shutdown observation (10.3% 약물기준 재도달) 문서화. 체계적 AE 표 부재, 직접 기기 위해 미보고 | 저널 인쇄 페이지 pp.665–674 완전 정규화 완료 (Fig 1 p.668, Table 1 p.667, Table 2 p.669, Table 3 p.670, Fig 2 p.671, Discussion pp.671–673). Supplement 2(eTable 3, 4) 대조 완료 | 수치 및 인쇄 페이지 대조 완료. 외부 독립 2차 검토(Independent second-review) 미실시 |
| E001-F Singh 2025/2026 | 산전 opioid 노출, ≥35주 신생아 62명; 다기관 비눈가림 RCT, 조기 종료 | SVS mattress 40명 vs 표준 매트리스 22명; 30–60 Hz, 10–12 μm RMS | 생후 5일 이내 NOWS 약물치료 시작 | 4/40 (10.0%) vs 4/22 (18.2%); adjusted OR 0.54 (95% CI 0.10–2.85), P=.46 (비유의). Cry subset n=46에서 fussy/pain cry(P=.82) 및 cry strength(P=.55) 차이 없음 | 저자는 "No adverse events were noted in either study groups" 명시; 단기 병원 관찰 및 n=62 범위에 한정 | 저널 페이지 범위 pp.276–282 및 PMC 풀텍스트 대조 완료 (Fig 1 p.278, Table 2 p.279, Table 3 p.280, Table 4 pp.280–281). Supplement(NIHMS2106170: Table S1, Fig S1) 식별 | 표본 부족/조기 종료(계획 120 vs 실제 62), cry subset 분모(46명), 인쇄 PDF 최종 레스터 검토 및 외부 독립 2차 검토 미실시 |

## 3. Evidence type / quality / directness 분리 예시

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

## 5. WP-0 진행 상황 — 내부 대조 갱신 보고, 종료 판정 보류

2026-10-13 최신 원문 PMC 풀텍스트 및 저널 인쇄 페이지 메타데이터를 바탕으로 E001-C, E001-E, E001-F의 핵심 수치, 분모, 보충자료를 정밀 재대조했다.

- E001-A: Table 2 p.e1566 및 adverse-event 문구 p.e1565 인쇄본 대조 기록 보유. 수치별 독립 검토 미실시.
- E001-B: Table 2 p.1021, Figure 6 p.1024, Methods 계측 pp.1018–1019 기록 보유.
- E001-C: Publisher PDF (x/15) 기준 Table 1(pp.3–4), Table 2(pp.7–9), Table 3(p.10), AE discussion(p.11) 정밀 대조 완료. Condition duration (28.7 vs 28.8 min), Caregiver disruption (58.1 vs 54.5 s), Sigma skewness (1.7 vs 1.5) 행 단위 수치 확인 완료.
- E001-D: FDA 9페이지 PDF 인쇄본 전수 검토 완료. Redacted 벤치 수치 한계 유지.
- E001-E: JAMA Pediatr 2023 인쇄본 pp.665–674 전수 정규화 완료. Table 2 1차 결과(35.6% vs 30.9%, P=.60), Table 3 노출시간(aOR 0.88), Figure 2/eTable 3 반응군(n=32), eTable 4 비반응군(n=28), 셧다운(6/58, 10.3%) 분모 분리 완료. Supplement 2 확인 완료.
- E001-F: Pediatr Res 2026 저널 pp.276–282 및 PMC13134440 대조 완료. ITT(n=62), 1차 결과(4/40 vs 4/22, P=.46), Cry subset(n=46, P=.82), Table 4 설문(60%/80%), AE 문구 확인 완료. 보충자료(NIHMS2106170: Table S1, Fig S1) 식별 완료.
- 외부 독립 임상 연구자 검토(Independent Second-Review): 미실시 상태 유지 (Gate 2 배정).

### WP-0 종료 게이트

WP-0는 아래 항목을 문헌별로 확인하고 미해결 항목을 명시한 뒤 종료할 수 있다.

1. 핵심 수치가 원문 인쇄 페이지·섹션·표/그림 행까지 추적 가능하다. (내부 대조 진척)
2. enrolled/randomized/analyzed와 각 분석 분모가 구분돼 있다. (확인 완료)
3. 1차·2차·탐색·하위집단·노출량 연관 분석이 구분돼 있다. (확인 완료)
4. 이상사건 상태가 reported / none reported / not reported / not assessed / unclear 중 근거에 맞게 코딩돼 있다. (확인 완료)
5. Evidence type, evidence quality, directness가 분리돼 있다. (확인 완료)
6. null/negative findings와 미수집 결과가 보존돼 있다. (확인 완료)
7. 독립 검토 실시 여부와 미해결 항목이 명시돼 있다. (외부 독립 검토 미실시)

**현재 판정: Partial — closure deferred (종료 판정 보류).** E001-C, E, F의 원문 수치와 분모 대조가 대폭 보강되었으나, 외부 독립 임상 연구자 검토(Independent second-review)가 미실시 상태이므로 WP-0를 닫지 않고 보류 상태로 유지한다.

## 6. 제품 주장에 대한 현재 제한

E001-A~E001-F는 대부분 미숙아 또는 산전 opioid 노출 신생아의 생리·임상 맥락을 다룬다. 이 자료는 물리 출력 시험 방법과 향후 연구 설계에는 유용하지만, MAJUNG이 일반 건강 영아의 울음·settling·수면을 개선한다는 직접 증거로 분류할 수 없다.
