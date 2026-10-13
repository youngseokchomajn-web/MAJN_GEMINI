# MAJUNG 근거 추출 마스터 테이블 (Evidence Extraction Master Table)
작성일: 2026-10-13  
상태: 1차 원문 추출 통합본 — locator/상태 정합성 검토 중 (버전 1.1)  
목적: E001-A~F 1차 문헌의 핵심 수치, 원문 위치(Locator), 해석 경계 및 사실/해석 구분을 단일 마스터 테이블로 영구 보존.

---

## 1. 표준 스키마 정의 (22개 필드)

1. `source_id`: E001-A ~ E001-F
2. `full_citation`: 정식 서지정보
3. `doi_url`: DOI 및 공식 링크
4. `source_type`: 논문 / FDA 요약 / 임상시험 등록부
5. `evidence_type`: 공학 / 생리 / 행동 / 임상유효성 / 안전성 / 규제
6. `evidence_quality`: 비뚤림 위험, 무작위배정, 눈가림, 분석 완전성
7. `directness_to_MAJUNG`: 목표집단·자극방식·평가변수의 직접성 (High / Moderate / Low)
8. `population`: 포함/제외 기준, 재태연령, 임상 상태
9. `n_enrolled_randomized_analyzed`: 등록/무작위배정/최종분석 표본수 분리
10. `intervention_comparator`: 중재 조건 vs 대조군 조건
11. `exposure_parameters`: 주파수, 변위(RMS/최대), 파형, 주기
12. `primary_endpoint`: 원문 사전 지정 1차 평가변수
13. `secondary_exploratory_endpoints`: 2차 및 탐색적 평가변수
14. `result_effect_estimate_uncertainty`: 수치, 분모, 단위, 신뢰구간(CI), p-value
15. `adverse_event_status`: reported / none reported / not reported / not assessed / unclear
16: `limitations_risk_of_bias`: 설계 결함, 조기종료, 비눈가림 등
17. `printed_page_locator`: 저널 인쇄본/PDF 인쇄 페이지 기준 위치
18. `section_table_figure_locator`: 본문 절, 표/그림 번호 및 행/열
19. `fact_from_source`: 원문에 명시된 객관적 사실
20. `author_interpretation`: 원문 저자의 고찰 및 해석
21. `majung_inference_and_boundary`: MAJUNG 적용 시 외삽 금지 경계
22. `verification_status`: Verified / Partial / Unresolved

---

## 2. 문헌별 정밀 추출 마스터 데이터

### 2.1 E001-A: Smith et al. 2015 (Pediatrics)

* **source_id**: E001-A
* **full_citation**: Smith VC, et al. Stochastic Resonance Effects on Apnea, Bradycardia, and Oxygenation: A Randomized Controlled Trial. *Pediatrics*. 2015;136(6):e1561–e1568.
* **doi_url**: DOI 10.1542/peds.2015-1334 / PMCID PMC4657600
* **source_type**: Peer-reviewed randomized crossover clinical trial
* **evidence_type**: Preterm respiratory & cardiac physiology
* **evidence_quality**: Crossover RCT, n=36, 교차 블록 설계 우수하나 미숙아 병원 내 생리 측정에 국한.
* **directness_to_MAJUNG**: Low (대상: 미숙아, 평가: 무호흡/산소포화도; 건강아 진정·수면 아님).
* **population**: 미숙아 36명 (출생체중 <1500g 또는 재태연령 <32주, 연구 당시 주수 32–38주, 무호흡/서맥/산소탈포화 사건 이력 보유).
* **n_enrolled_randomized_analyzed**: 36명 등록 / 36명 무작위 교차 배정 / 36명 분석 완료 (Figure 2, p.e1564).
* **intervention_comparator**: 매트리스 내장 확률 공명(SR) 진동 ON vs OFF 교대 (각 30분 블록, 총 수 시간 관찰).
* **exposure_parameters**: 30–60 Hz 대역 확률 진동, 매트리스 표면 변위 10–20 μm.
* **primary_endpoint**: 산소탈포화(Desaturation), 무호흡(Apnea), 서맥(Bradycardia) 사건 수 및 특성.
* **secondary_exploratory_endpoints**: 사건 지속시간(Duration), 중증도 강도(Intensity: 곡선하면적/최저점).
* **result_effect_estimate_uncertainty**:
  - 산소탈포화 사건 수: 709건 중 315 ON vs 394 OFF; 18% 감소 (95% CI 5%–29%, P=.01).
  - 산소탈포화 지속시간: 35% 감소 (95% CI 33%–37%, P<.0001).
  - 산소탈포화 강도: 21% 감소 (95% CI 20%–22%, P<.0001).
  - 무호흡 사건 수: 39건 중 13 ON vs 26 OFF; 50% 감소 보고 (Table 2).
  - 서맥 사건 수: 73건 중 38 ON vs 35 OFF; 사건 수 유의차 없음 (강도는 18% 감소, 95% CI 15%–22%, P<.0001).
* **adverse_event_status**: authors reported none ("No adverse events, adverse device effects, or unanticipated problems were encountered", p.e1565).
* **limitations_risk_of_bias**: 소규모(n=36), 단기 병원 관찰, 진정/울음/수면 구조 평가 부재, 서맥 빈도 자체는 개선되지 않음.
* **printed_page_locator**: 
  - Participant flow (Figure 2): p.e1564
  - Adverse events 문구: p.e1565 (Results 첫 단락)
  - Table 2 (모든 사건 수치): p.e1566
* **section_table_figure_locator**: Results ("Oxygen Desaturation", "Apnea", "Bradycardia"), Table 2.
* **fact_from_source**: 확률 진동이 미숙아의 산소탈포화 및 무호흡 빈도/강도를 줄였으나 서맥 발생 횟수는 줄이지 못함.
* **author_interpretation**: 감각 피질의 확률 공명 기전이 미숙한 뇌간 호흡 중추 신경망의 리듬 생성을 보조함.
* **majung_inference_and_boundary**: **외삽 절대 금지.** 미숙아의 생리적 사건 억제 효과를 건강한 만삭아의 '잠투정 해소'나 '수면 연장' 근거로 차용할 수 없음.
* **verification_status**: Partial (Figure 2 및 Table 2 주요 locator가 기록됨. 모든 핵심 수치·분모의 재대조와 WP-0 전체 종료 판정은 별도 확인 필요).

---

### 2.2 E001-B: Bloch-Salisbury et al. 2009 (J Appl Physiol)

* **source_id**: E001-B
* **full_citation**: Bloch-Salisbury E, Indic P, Bednarek F, Paydarfar D. Stabilizing immature breathing patterns of preterm infants using stochastic mechanosensory stimulation. *J Appl Physiol*. 2009;107(4):1017–1027.
* **doi_url**: DOI 10.1152/japplphysiol.00058.2009 / PMCID PMC2763836
* **source_type**: Peer-reviewed physiological mechanistic study
* **evidence_type**: Engineering output characterization & preterm breathing physiology
* **evidence_quality**: Mechanistic repeated-measures design, 정밀 물리 출력 계측 및 생체신호 분석 우수, n=10 초소규모.
* **directness_to_MAJUNG**: Low-Moderate (공학적 진동 계측 및 침구 감쇠 측정 방법은 유용; 임상 효능 직접성은 낮음).
* **population**: 미숙아 10명 (출생 재태 26–31주, 시험 시점 31–36주, 인큐베이터 내 안정 상태).
* **n_enrolled_randomized_analyzed**: 10명 등록 / 10명 분석 완료 (Table 1, p.1020).
* **intervention_comparator**: 기계감각 진동 자극 매트리스 ON vs OFF (10분 자극 / 10분 휴식 반복 블록).
* **exposure_parameters**: 30–60 Hz 대역 제한 핑크 노이즈; 표면 변위 0.021 mm RMS (최대 변위 0.090 mm); 변위 균일도 ±2% (선형 변위 센서 LVDT 측정).
* **primary_endpoint**: 호흡 간격(Interbreath interval, IBI) 분산, 호흡 안정성, 산소탈포화 비율.
* **secondary_exploratory_endpoints**: 수면/각성 상태 전이, 뇌파(EEG) 스펙트럼 밀도, 각성(Arousal) 유발 여부.
* **result_effect_estimate_uncertainty**:
  - IBI 분산: ON 0.46 s² vs OFF 0.91 s² (약 50% 감소, P=.003, Figure 2).
  - 연장된 IBI (>5초) 발생률: ON 18.6회/h vs OFF 37.1회/h (Table 2).
  - 산소탈포화 시간 비율: ON 0.68% vs OFF 1.92% (약 65% 감소, P=.04, Table 2).
  - 조용한 수면(Quiet sleep) 비율: OFF 61.1% vs ON 60.1% (유의차 없음, P=NS). 자극 전환 시 각성 유발 없음.
* **adverse_event_status**: not clearly reported in extracted source (이상사건 전용 표나 표준화된 보고 문단 부재; "자극이 수면 상태를 교란하거나 각성을 유발하지 않았다"는 점만 명시).
* **limitations_risk_of_bias**: n=10 극소 표본, 통계적 검정력 한계, 장기 안전성 미평가.
* **printed_page_locator**:
  - Table 1 (환아 특성): p.1020
  - Table 2 (호흡, 심장, 수면상태 수치): p.1021
  - Methods "Vibrotactile Stimulation" (공학 계측): p.1018–1019
  - Figure 6 (요약 그래프): p.1024
* **section_table_figure_locator**: Methods, Results ("Variance of IBIs", "Sleep state"), Table 2, Figure 6.
* **fact_from_source**: 0.021 mm RMS(30-60 Hz) 진동이 미숙아의 호흡 불규칙성을 반감시켰으며, 수면 단편화나 각성을 일으키지 않고 수면 상태 비율을 유지함.
* **author_interpretation**: 감각 진동 자극이 호흡신경망에 동조 신호로 작용하여 안정화를 유도함.
* **majung_inference_and_boundary**: **공학적 참고 한정.** 매트리스 폼의 진동 감쇠 및 침구(시트/담요) 적층 시 진폭 보정 방법론은 벤치 테스트 설계에 유효하나, 수치 자체를 일반 영아의 안전 한계값으로 전용할 수 없음.
* **verification_status**: Partial (주요 표·그림 페이지 locator가 기록됨. 물리 출력 subsection 및 이상사건 보고 범위 확인이 남아 있음).

---

### 2.3 E001-C: Zuzarte et al. 2017 (PLOS ONE)

* **source_id**: E001-C
* **full_citation**: Zuzarte I, Indic P, Barton B, Paydarfar D, Bednarek F, Bloch-Salisbury E. Vibrotactile stimulation: A non-pharmacological intervention for opioid-exposed newborns. *PLOS ONE*. 2017;12(4):e0175981.
* **doi_url**: DOI 10.1371/journal.pone.0175981 / PMCID PMC5398650
* **source_type**: Peer-reviewed clinical within-subject intervention study
* **evidence_type**: Clinical behavior (motor movement) & physiology in NOWS
* **evidence_quality**: Prospective within-subject crossover (n=26), 정밀 움직임 센서 및 비디오 동기화 분석, 단일 기관, 약물치료 병행 상태.
* **directness_to_MAJUNG**: Moderate (영아의 신체 움직임/과민반응 감소를 객관적 모션 센서로 검증한 점은 유사하나 대상군이 NOWS 환아임).
* **population**: 산전 오피오이드에 노출되어 금단증상(NOWS)으로 모르핀 약물치료를 받고 있는 만삭 신생아 26명 (재태연령 ≥37주, 출생체중 >2500g).
* **n_enrolled_randomized_analyzed**: 26명 등록 / 26명 분석 (Table 1, PDF p.6/15).
* **intervention_comparator**: 확률 진동 매트리스(SVS) ON vs OFF (30분 블록 교대, 6–8시간 연속 세션).
* **exposure_parameters**: 30–60 Hz 대역; 10–12 μm RMS 변위.
* **primary_endpoint**: 신체 움직임 활동(Movement activity, % of epoch) 및 30초 초과 지속 움직임 에피소드.
* **secondary_exploratory_endpoints**: 호흡수, 심박수, 산소포화도(SaO₂), 피부 체온(Skin temperature).
* **result_effect_estimate_uncertainty**:
  - 절대 움직임 활동: OFF 40% (95% CI 36%–45%) vs ON 26% (95% CI 23%–30%); 상대 감소율 35% (P<.001, Table 2).
  - 30초 초과 긴 움직임 횟수: OFF 13회 vs ON 9회 (P=.003, Table 2). 26명 중 23명에서 움직임 감소 관찰 (Figure 3).
  - 호흡수: OFF 74회/분 vs ON 68회/분 (P=.023); 빈호흡(Tachypneic) 호흡수 감소 (P=.024).
  - 심박수: OFF 137회/분 vs ON 134회/분 (P=.016).
  - 산소포화도: 평균 99% 유지 (P=.544, 유의차 없음).
  - 체온: 평균 36.8°C 유지 (P=.581, 유의차 없음).
* **adverse_event_status**: authors reported none (FDA De Novo DEN240031 p.7 검토서 상 이상사건 미보고 확인).
* **limitations_risk_of_bias**: 모르핀 병용 상태의 금단 환아에 국한, 비눈가림 세션, 영아의 '수면'이나 '울음 지속시간'을 직접 분리하여 primary로 검증하지 않음.
* **printed_page_locator**:
  - Article identifier: e0175981 (15 pages)
  - Table 1 (환아 특성): PDF p.6/15
  - Table 2 (움직임 및 생리 지표): PDF p.9/15
  - Figure 3 (개별 움직임 감소 그래프): PDF p.8/15
* **section_table_figure_locator**: Results ("Condition and movement periods", "Physiological measurements"), Table 2, Figure 3.
* **fact_from_source**: SVS 진동 시 NOWS 환아의 과도한 신체 움직임이 35% 감소하고 심박/호흡이 안정되었으며 체온 저하나 탈포화는 없었음.
* **author_interpretation**: 체성감각 진동 자극이 중추신경계 자율신경계 과흥분을 진정시켜 금단 증상을 완화함.
* **majung_inference_and_boundary**: **움직임 감소 ≠ 건강 영아 수면 성공.** 과민 환아의 모터 움직임 감소가 일반 영아의 보챔 완화나 야간 수면 질 개선을 자동으로 보장하지 않음. FDA 또한 본 연구의 엔드포인트가 '유효성 확증'에는 불충분하며 '안전성 보조 근거'로만 인정함(DEN240031 p.7).
* **verification_status**: Partial (일부 PDF 페이지 locator가 기록됨. 모든 수치·분모와 표·그림 locator의 재대조가 남아 있음).

---

### 2.4 E001-D: Prapela FDA De Novo Summary (DEN240031)

* **source_id**: E001-D
* **full_citation**: FDA CDRH. De Novo Classification Request for Prapela SVS Hospital Bassinet Pad (Model P01). Decision Summary DEN240031. 2024.
* **doi_url**: https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240031.pdf
* **source_type**: Official FDA regulatory classification & decision document (9 pages)
* **evidence_type**: Regulatory, non-clinical bench safety, and clinical evidence audit
* **evidence_quality**: FDA 공식 규제 검토서로 법적·기술적 신뢰도 최고 수준. 단, 벤치 시험 수치 일부 비공개(Redacted).
* **directness_to_MAJUNG**: Moderate-Low (의료기기 인허가 요건 및 위험 분석 벤치마킹에는 직접적이나, MAJUNG은 현재 일반 공산품/전자기기 포지셔닝임).
* **population**: 재태연령 ≥37주, 산전 오피오이드 노출 및 NOWS 진단을 받은 입원 신생아.
* **n_enrolled_randomized_analyzed**: 제출 임상자료: Zuzarte 2017 (n=26) + Bloch-Salisbury 2023 RCT (n=181 analyzed) 종합.
* **intervention_comparator**: Prapela SVS Hospital Bassinet Pad (Class II 의료기기, 코드 QVY, 21 CFR 880.5151).
* **exposure_parameters**: 매트리스 내장 액추에이터, DRMS(진동 실효값) 기반 제어, 3시간 ON/OFF 자동 운전 사이클.
* **primary_endpoint**: NOWS 증상 완화 보조 요법으로서의 임상적 유효성 및 기기 안전성.
* **secondary_exploratory_endpoints**: 음향 소음(Sound level), 전기안전(IEC 60601-1), 전자파(IEC 60601-1-2), 생체적합성(ISO 10993), 소프트웨어 V&V.
* **result_effect_estimate_uncertainty**:
  - FDA 규제 승인 (Class II De Novo granted).
  - 유효성 판단: 2023 RCT에서 전체 모르핀 치료율 차이는 비유의했으나, 반응군(21일 이내 완료)에서 치료 기간 및 누적 용량의 임상적 유의성을 인정.
  - 2017 연구: 적응증에 대한 유효성 입증 엔드포인트로는 불충분하나 안전성(체온 유지, 산소포화도 유지, 이상사건 없음) 뒷받침으로 인정 (p.7).
* **adverse_event_status**: bounded report (제출된 모든 임상 데이터에서 기기 관련 이상사건 미관찰 보고).
* **limitations_risk_of_bias**: 병원 내 전문 의료진 감독 하의 처방 전용(Prescription use only) 기기로 제한됨. 가정 내 사용 안전성 미포함.
* **printed_page_locator**:
  - Regulatory Information & Indication: Printed p.1
  - Device Description: Printed p.2
  - Bench Testing (소음, 진동 균일도 등): Printed pp.4–6
  - Clinical Information (2017 vs 2023 구분): Printed p.7
  - Risks to Health: Printed p.8
  - Special Controls & Benefit-Risk Conclusion: Printed pp.8–9
* **section_table_figure_locator**: 각 절 제목 (Indications for Use, Performance Testing – Bench, Summary of Clinical Information, Risks to Health).
* **fact_from_source**: FDA는 SVS 패드를 NOWS 신생아의 '보조 요법' 의료기기로 승인함. 특별 통제 기준으로 음향 소음 한계 및 진동 출력 검증을 의무화함.
* **author_interpretation**: 기기의 위험(수면 방해/청각 영향, 끼임, 조직 반응 등)은 특별 통제 기준(Special Controls)을 통해 합리적으로 완화 가능함.
* **majung_inference_and_boundary**: **의료기기 승인을 일반 제품 효능으로 위장 불가.** MAJUNG이 FDA De Novo 허가를 획득한 것이 아니며, 일반 영아 배시넷에 대해 "FDA 승인 기술" 등의 과장 광고를 적용할 경우 의료기기법 및 표시광고법 위반에 해당함.
* **verification_status**: Partial (문서 페이지 범위 및 일부 규제 근거를 검토했으나, redacted bench 수치의 한계와 핵심 문장·표의 2차 확인이 남아 있음).

---

### 2.5 E001-E: Bloch-Salisbury et al. 2023 (JAMA Pediatrics)

* **source_id**: E001-E
* **full_citation**: Bloch-Salisbury E, Wilson JD, Rodriguez N, et al. Efficacy of a Vibrating Crib Mattress to Reduce Pharmacologic Treatment in Opioid-Exposed Newborns: A Randomized Clinical Trial. *JAMA Pediatr*. 2023;177(7):665–674.
* **doi_url**: DOI 10.1001/jamapediatrics.2023.1077 / PMCID PMC10186209
* **source_type**: Multi-center randomized controlled trial (RCT)
* **evidence_type**: Clinical pharmacotherapy efficacy in NOWS
* **evidence_quality**: 대규모 다기관 RCT (208명 무작위배정), 사전 프로토콜 등록, 그러나 ITT 분석에서 1차 평가변수 통계적 유의성 미달.
* **directness_to_MAJUNG**: Low (NOWS 약물 투여율 및 입원 기간 평가; 영아 진정·수면 평가 아님).
* **population**: 산전 오피오이드 노출 신생아 (재태연령 ≥37주, 출생체중 ≥2200g, 4개 병원 NICU/소아병동 입원).
* **n_enrolled_randomized_analyzed**: 208명 등록 및 무작위 배정 (SVS 104명, TAU 104명) / 181명 최종 프로토콜 분석 완료 (SVS 94명, TAU 87명; 27명은 타원 이송 등으로 중도 탈락) (Figure 1, p.668).
* **intervention_comparator**: SVS 매트리스 + 통상 치료(TAU) vs 통상 치료(TAU) 단독.
* **exposure_parameters**: 30–60 Hz 대역; 10–12 μm RMS 변위; 입원 기간 내 임상 적용.
* **primary_endpoint**: 모르핀 약물치료 시작률(Administration of morphine treatment, AMT), 누적 모르핀 용량(CMD), 입원 기간(LOS).
* **secondary_exploratory_endpoints**: 일일 SVS 가동 시간과 치료율의 노출-반응 연관성, 조기 치료 완료 반응군(≤21일) 하위분석.
* **result_effect_estimate_uncertainty**:
  - **전체 무작위 비교 (1차 결과)**: AMT 투여율 TAU 31/87 (35.6%) vs SVS 29/94 (30.9%); 위험 차이 비유의 (P=.60, Table 2).
  - **노출 시간 연관성 (관찰 분석)**: SVS 가동 시간이 1시간/일 증가할 때마다 약물치료 위험 감소 (aOR 0.88, 95% CI 0.81–0.93, Table 3).
  - **전체 치료군(n=60)**: 누적 모르핀 용량 및 치료 일수 차이 유의하지 않음 (Table 3).
  - **반응군 하위집단 (≤21일 완료, n=32)**: SVS군에서 치료 일수 3.18일 단축, 누적 모르핀 용량 1.76 mg/kg 감소 (95% CI −3.02 to −0.50, Figure 2B, eTable 3).
  - **기기 중단 관찰**: 퇴원 전 SVS 가동 중단(Shutdown)한 58명 중 6명(10.3%)이 24시간 내 약물 치료 기준에 재도달 (Results, p.669).
* **adverse_event_status**: bounded protocol observation (기기 중단 후 6명 증상 재발 관찰 외 기기 직접 부작용 없음).
* **limitations_risk_of_bias**: 무작위 배정 전체 집단에서 1차 결과 음성(Negative/Null), 비눈가림 치료 환경, 조기 완료 하위분석은 사후적(Post-hoc) 성격 내포.
* **printed_page_locator**:
  - Participant Flow (Figure 1): p.668
  - Baseline Characteristics (Table 1): p.667
  - Primary Outcomes (Table 2): p.669
  - Association & Dose Analysis (Table 3): p.670
  - Subgroup Kaplan-Meier (Figure 2): p.671
* **section_table_figure_locator**: Results ("Administration of Morphine", "Infants Treated With Morphine"), Table 2, Table 3, Figure 2, eTable 3/4.
* **fact_from_source**: SVS 배정만으로는 전체 환아의 모르핀 투여율을 유의하게 낮추지 못했으나, 실사용 시간이 길수록 연관 위험이 낮았고 조기 반응군에서 유의한 용량 감소가 관찰됨.
* **author_interpretation**: SVS는 약물 투여 위험을 줄이고 치료 반응을 가속하는 안전한 비약물적 보조 요법이 될 수 있음.
* **majung_inference_and_boundary**: **전체 결과의 음성(Null)을 은폐하고 하위분석만 인용하는 행위 엄금.** MAJUNG 마케팅이나 기술 문서에서 "임상시험을 통해 증명된"이라는 문구를 쓰며 이 논문의 하위분석 수치를 인용하는 것은 심각한 학술적 왜곡임.
* **verification_status**: Partial (주요 분석의 HTML locator는 기록돼 있으나, 인쇄 페이지 정규화·보충자료·하위집단 및 이상사건 맥락 확인이 남아 있음).

---

### 2.6 E001-F: Singh et al. 2026 / online 2025 (Pediatr Res)

* **source_id**: E001-F
* **full_citation**: Singh R, Trinquart L, Koethe B, Cordova M, Rhein L, Bibi S, Fey J, Anderson A, Davis JM. Efficacy of stochastic vibro-tactile stimulation for newborns at risk of neonatal opioid withdrawal syndrome. *Pediatr Res*. 2026;99(1):276–282. (Online 2025-05-23).
* **doi_url**: DOI 10.1038/s41390-025-04162-2 / PMCID PMC13134440 / ClinicalTrials.gov NCT04834297
* **source_type**: Multi-center open-label randomized trial
* **evidence_type**: Randomized clinical efficacy, infant crying analysis & acceptability
* **evidence_quality**: 중앙 무작위 배정(2:1), 다기관 설계. 단, 조기 종료(목표 120명 중 62명 등록), 비눈가림, 울음 분석 부분 집단 결측 존재.
* **directness_to_MAJUNG**: Low-Moderate (영아 울음 사운드 분석 ChatterBaby를 포함한 점은 MAJUNG에 매우 밀접하나, 집단이 NOWS 위험군이며 결과가 비유의함).
* **population**: 산전 오피오이드에 노출되었으나 등록 당시 금단 증상이 아직 시작되지 않은 신생아 (재태연령 ≥35주, 6개 의료기관).
* **n_enrolled_randomized_analyzed**: 129명 선별 / 80명 적격 / 62명 등록 및 무작위 배정 (SVS 40명, 표준 매트리스 22명) / 62명 분석 (Figure 1, p.278).
* **intervention_comparator**: 지속적 저수준 SVS 매트리스 (40명) vs 표준 유아용 침대 매트리스 (22명) (최대 5일 또는 약물 시작 시점까지).
* **exposure_parameters**: 30–60 Hz 대역; 10–12 μm RMS 변위.
* **primary_endpoint**: 생후 5일 이내 NOWS 약물 치료 시작률.
* **secondary_exploratory_endpoints**: 퇴원 준비 기간(Readiness for discharge), FNASS/ESC 임상 평가 점수, ChatterBaby 음향 분석 기반 울음(보챔/통증 울음 시간 비율, 울음 강도), 보호자/간호사 수용도.
* **result_effect_estimate_uncertainty**:
  - **1차 결과 (약물 치료 시작)**: SVS 4/40 (10.0%) vs 표준 4/22 (18.2%); 조정 OR 0.54 (95% CI 0.10–2.85, P=.46); 조정 위험 차이 −5.7% (95% CI −21.2% to 9.8%). 유의차 없음.
  - **퇴원 준비 기간**: 중간값 SVS 3.9일 vs 표준 4.9일; 조정 위험비 0.75 (95% CI 0.53–1.05, P=.09). 유의차 없음.
  - **울음 분석 (ChatterBaby, n=46 분석)**: 
    - 보챔/통증 울음(Fussy/pain cry) 시간 비율: SVS 중간값 8.0% vs 표준 7.2%; 추정치 0.3 (95% CI −1.5 to 2.3, P=.82). 유의차 없음.
    - 울음 강도(Cry strength): SVS 87.2% vs 표준 86.5%; 추정치 −0.8 (95% CI −3.9 to 2.8, P=.55). 유의차 없음.
  - **수용도 설문 (주관적)**: 간호사의 60%, 부모의 80%가 "매트리스가 아기를 달래고 진정시키는 데 도움이 되었다"고 응답 (Table 4).
* **adverse_event_status**: authors reported none ("No adverse events were observed in either group", p.280).
* **limitations_risk_of_bias**: 낮은 모집률로 인한 조기 종료(n=62 vs 계획 120), 불균등 배정(2:1), 비눈가림 평가, 울음 데이터 누락(16명 미수집).
* **printed_page_locator**:
  - 저널 인쇄 페이지: 276–282
  - Participant Flow (Figure 1): p.278
  - Primary & Discharge Outcomes (Table 2): p.279
  - Cry Data (Table 3): p.280
  - Acceptability Survey & AE (Table 4): p.280–281
* **section_table_figure_locator**: Results ("Primary outcome", "Cry data", "Acceptability"), Tables 2–4, Figure 1.
* **fact_from_source**: 지속적 진동 자극이 5일 내 약물치료율, 퇴원 준비 기간, 객관적 울음 시간 및 울음 강도를 통계적으로 유의하게 감소시키지 못함. 그러나 양육자 주관적 만족도는 높았음.
* **author_interpretation**: 환아 모집 부진으로 충분한 검정력을 확보하지 못했으나, 경향성과 수용도는 비약물적 보조 요법으로서의 가능성을 보여줌.
* **majung_inference_and_boundary**: **핵심 경고: 객관적 효능 부재와 주관적 만족도의 괴리.** 객관적 울음 데이터에서 통계적 차이가 전혀 없음(P=.82)에도 불구하고 부모의 80%는 "달래는 데 도움이 되었다"고 응답함. 이는 일반 소비자용 배시넷에서 발생하는 '플라시보 효과' 및 '양육자 기대 편향'을 극명하게 보여줌. MAJUNG 연구는 반드시 주관적 설문이 아닌 객관적 비디오/음향 센서 엔드포인트를 1차로 설정해야 함.
* **verification_status**: Partial (저널 페이지 범위 276–282는 확인됨. 각 표의 정확한 인쇄 페이지, Supplementary Table S1/Figure S1 및 이상사건 맥락은 미완료).

---

## 3. 요약 감사 판정 — 재정합성 수정

| Source ID | 수치 Locator 대조 상태 | AE 코딩 상태 | 건강 영아 진정 직접성 | WP-0 판정 |
|---|---|---|---|---|
| E001-A | Partial — 주요 locator 기록, 전체 수치·분모 재대조 필요 | 보고 문구 locator 기록; 최종 코딩 재확인 | Low | 종료 판정 보류 |
| E001-B | Partial — 주요 표·그림 locator 기록, 출력/AE 맥락 미완료 | not clearly reported; 보고 범위 재확인 | Low-Moderate | 종료 판정 보류 |
| E001-C | Partial — 일부 PDF locator 기록, 수치·분모/표·그림 재대조 필요 | 기존 기록상 authors reported none; 원문 맥락 재확인 | Moderate | 종료 판정 보류 |
| E001-D | Partial — 문서 범위 검토, 핵심 문장·표 2차 확인 필요 | bounded report; 원문 범위 유지 | Moderate-Low | 종료 판정 보류 |
| E001-E | Partial — HTML locator 기록, 인쇄 페이지/보충자료 맥락 미완료 | protocol/shutdown observation의 해석 경계 유지 | Low | 종료 판정 보류 |
| E001-F | Partial — 저널 페이지 범위 확인, 개별 표 페이지/보충자료 미완료 | 저자 보고 문구는 62명·단기 관찰 범위로 한정 | Low-Moderate | 종료 판정 보류 |

> **현재 감사 결론:** E001-A~F의 추출 내용과 일부 locator는 존재하지만, 모든 인쇄 페이지·표/그림·분모·통계·이상사건 맥락이 전수 대조되었다고 선언할 수 없다. E001-E/F의 인쇄 페이지 및 보충자료 확인과 E001-C의 일부 locator 재대조가 남아 있다. 외부 독립 임상 연구자 검토도 아직 수행되지 않았다. 따라서 WP-0는 **Partial / 종료 판정 보류**다. 이 상태는 각 논문의 결과 요약을 무효화하지 않지만, 문헌 감사 전체가 끝났다는 의미도 아니다.
