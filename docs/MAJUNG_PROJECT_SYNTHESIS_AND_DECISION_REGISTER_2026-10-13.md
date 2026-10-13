# MAJUNG 프로젝트 전체 구조 분석·통합 요약·결정 기록
작성일: 2026-10-13
상태: 전체 작업의 구조적 통합 문서. 임상 효능·안전성·공학 검증 완료 선언이 아님.

## 0. 이 문서의 역할

이 문서는 2026-10-13까지 저장소에 축적된 MAJUNG 진동 모듈의 문헌 검토, 제품 Claim, 연구 설계, endpoint, 공학 시험, 연구자 협업, 추출 추적성 작업을 한 구조로 묶는다. 세부 문서의 원본을 대체하지 않고, 무엇이 결정됐고 무엇이 아직 미확인인지 보여주는 상위 진입점이다.

핵심 원칙은 **MAJUNG을 판매 가능한 제품으로 만들기 위해 효과와 안전에 관한 근거를 구축하는 것**이다. 진동이 작동하는 것, 문헌에 유사한 장치가 있는 것, 임상 결과가 관찰된 것은 서로 다른 수준의 증거다.

## Gemini 일괄 조사 실행 완료 산출물 (2026-10-13)

- **통합 구조 재분석 및 불일치 감사:** [MAJUNG_INTEGRATED_STRUCTURAL_REANALYSIS_2026-10-13.md](MAJUNG_INTEGRATED_STRUCTURAL_REANALYSIS_2026-10-13.md). 핵심 지적: WP-0 상태 충돌, 직접 근거 표현 과장 가능성, 잠정 임상/안전 수치의 확정 기준화, 연구자 접촉 패키지의 실측 완료 표현.

- **FTO·리콜·DSP·규제 심층 보고서 비판적 검토**: [MAJUNG_DEEP_DIVE_FTO_RECALL_SIGNAL_REGULATORY_CRITICAL_REVIEW_2026-10-13.md](MAJUNG_DEEP_DIVE_FTO_RECALL_SIGNAL_REGULATORY_CRITICAL_REVIEW_2026-10-13.md). 원 보고서는 보존하고, 특허 회피·안전 수치·DSP 성능·웰니스/IRB 분류를 검증 전 확정 결론으로 사용하지 않도록 상태를 분리함.

- **특허(FTO)·리콜 감사·신호 필터링·웰니스 규제 심층 분석**: [MAJUNG_DEEP_DIVE_FTO_RECALL_SIGNAL_REGULATORY_2026-10-13.md](MAJUNG_DEEP_DIVE_FTO_RECALL_SIGNAL_REGULATORY_2026-10-13.md)
- **연구 실행 및 감사 로그**: [MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md](MAJUNG_GEMINI_RESEARCH_RUN_LOG_2026-10-13.md)
- **근거 추출 마스터 테이블**: [MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md](MAJUNG_EVIDENCE_EXTRACTION_MASTER_TABLE_2026-10-13.md)
- **연구 및 규제 출처 등록부**: [MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md](MAJUNG_RESEARCH_SOURCE_REGISTER_2026-10-13.md)
- **공학 출력·위험 벤치 시험 계획**: [MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md](MAJUNG_ENGINEERING_OUTPUT_AND_BENCH_TEST_PLAN_2026-10-13.md)
- **건강 영아 임상 프로토콜 시놉시스**: [MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md](MAJUNG_CLINICAL_RESEARCH_PROTOCOL_SYNOPSIS_2026-10-13.md)
- **국내 연구자 검증 숏리스트**: [MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md](MAJUNG_KOREA_RESEARCH_COLLABORATOR_SHORTLIST_2026-10-13.md)
- **연구자 접촉 패키지 (Concept Note·질문지)**: [MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md](MAJUNG_RESEARCHER_OUTREACH_PACKAGE_2026-10-13.md)
- **의사결정 게이트 & 클레임 규칙**: [MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md](MAJUNG_DECISION_GATES_AND_CLAIM_RULES_2026-10-13.md)

## Gemini 일괄 진행 인계 패키지 기준선

- 최신 실행 브리프 및 한 번에 붙여넣을 프롬프트: [MAJUNG_GEMINI_ONE_SHOT_HANDOFF_2026-10-13.md](MAJUNG_GEMINI_ONE_SHOT_HANDOFF_2026-10-13.md)
- 실행 패키지 및 복사·붙여넣기용 전체 프롬프트: [MAJUNG_GEMINI_BATCH_RESEARCH_EXECUTION_PACKAGE_2026-10-13.md](MAJUNG_GEMINI_BATCH_RESEARCH_EXECUTION_PACKAGE_2026-10-13.md)

## 1. 한눈에 보는 판정

### 현재 확인된 것
- 영아 대상 진동·운동 자극 연구는 존재하지만, 대상군·물리적 자극·임상 상황·측정 결과가 서로 다르다.
- 일부 연구에서 특정 행동 또는 생리 지표 변화가 관찰됐고, 일부 연구에서는 총 수면·울음·주요 임상 결과의 개선이 확인되지 않았다.
- 기존 문헌은 MAJUNG의 시험 질문, 물리 출력 측정, 행동 코딩, 안전성 관찰 항목을 설계하는 데 참고할 수 있다.
- 근거 추적 기준, Claim–Evidence–Gap–Experiment 매트릭스, endpoint 후보, 연구자 검토 질문, 문헌별 locator 감사 문서가 마련돼 있다.
- 현재 회로·PCB·액추에이터는 변경 가능한 개발안이며, 설계 동결은 검증 결과 이후에 결정한다.

### 아직 확인되지 않은 것
- MAJUNG 접촉면에서 실제 전달되는 진동의 파형·주파수·변위·가속도·위치별 편차·반복성.
- 하중·침구·설치 조건에 따른 출력 변화, 소음·온도·예상 가능한 고장 조건의 위험.
- MAJUNG이 일반 건강 영아의 settling, crying/fussing 또는 sleep을 개선하는지 여부.
- 특정 설정의 영아 안전성, 반복·장기 사용 안전성, 적절한 제품 분류·인증·광고 표현.
- 임상 연구자 또는 기관과의 공식 협업 및 사람 대상 연구 승인.

### 현재 핵심 결론
**MAJUNG의 일반 영아 진정·울음 감소·수면 개선 Claim은 아직 미입증이다.** 현재 작업은 그 Claim을 사실로 가정하는 것이 아니라, 무엇을 어떤 조건에서 측정하고 어떤 증거가 있어야 판단할 수 있는지 준비하는 단계다.

## 2. 전체 프로젝트 구조

프로젝트는 아래의 증거 사슬을 따라야 한다.

1. **제품 의도와 Claim 정의:** 누구에게 어떤 사용 환경에서 어떤 결과를 주장하려는가?
2. **현재 문헌과 직접성 평가:** 대상군, 자극, comparator, endpoint가 MAJUNG과 얼마나 가까운가?
3. **증거 공백 명시:** 현재 자료가 답하지 못하는 질문은 무엇인가?
4. **물리적 자극 특성화:** 장치 명령이 아니라 접촉면에서 실제 전달된 자극을 측정한다.
5. **공학적 위험 평가:** 정상 작동뿐 아니라 설치, 하중, 침구, 소음, 온도, 단일고장 및 예측 가능한 오사용을 검토한다.
6. **측정 타당성:** settling, crying/fussing, sleep, total sleep을 각각 신뢰성 있게 정의하고 측정한다.
7. **임상·통계 검토:** 대상군, comparator, endpoint, 분석계획, 표본 수 산정 전제를 전문가가 검토한다.
8. **기관·윤리·규제 경로 확인:** 실제 사람 대상 연구 전에 필요한 책임·검토·승인을 확인한다.
9. **feasibility → 효능·안전성 평가:** 적절한 승인과 절차 아래 수행하고 null/negative 결과도 보존한다.
10. **Claim 판정:** 실제 결과가 뒷받침하는 범위 안에서만 제품 표현을 정한다.

앞 단계의 성공은 뒤 단계의 성공을 보장하지 않는다. 출력 재현성은 임상 효능이 아니며, 단기 안전성 관찰은 반복·장기 안전성을 뜻하지 않는다.

## 3. 증거를 읽는 공통 기준

각 문헌은 서로 다른 네 가지 질문으로 분리 평가한다.

- **Evidence type:** 실제로 무엇을 측정했는가? 예: 호흡 생리, 움직임, 통증 반응, 수면 상태 분포, 약물치료.
- **Evidence quality:** 그 연구가 해당 질문에 답하는 방법이 얼마나 신뢰할 만한가? 설계, 표본, 눈가림, 비교군, 결측, 측정 및 보고를 본다.
- **Directness to MAJUNG:** 대상군, 물리 자극, endpoint, 사용 환경이 MAJUNG Claim에 얼마나 직접적인가?
- **Claim boundary:** 연구 결과에서 허용되는 결론과 허용되지 않는 외삽은 무엇인가?

좋은 설계의 연구라도 다른 환자군이나 다른 endpoint를 다루면 MAJUNG 일반 영아 진정 Claim에 대한 직접성은 낮을 수 있다. “유의하지 않음”, “측정하지 않음”, “보고하지 않음”, “위해 없음”은 서로 다른 상태다.

## 4. 문헌 근거의 통합 판독

### 4.1 행동·울음 관련 연구
- **Emori et al. (1995):** 54명의 건강 영아에게 수평 요람 전신 운동을 적용했을 때 울음 중단이 관찰됐지만, 졸림/수면 상태 영아의 각성도 보고됐다. 큰 변위의 요람 운동이므로 MAJUNG 소형 진동과 같은 자극으로 간주하지 않는다. 특정 설정을 안전 기준으로 가져오지 않는다.
- **Huhtala et al. (2000):** 산통 영아에서 마사지와 crib vibrator를 비교했고 양쪽에서 울음 감소가 관찰됐다. 무중재 대조군이 없어 자연 경과와 진동 고유 효과를 분리하기 어렵다.
- **Contours Vibes (2022):** 소규모 표본, 고정된 매트리스 조건 순서, 보호자 보고 중심이다. 일부 개선 신호는 연구 가설을 만드는 데 참고할 수 있지만 진동 단독 효과나 장기 안전성을 확정하지 않는다.
- **Catal et al. (2024):** 만삭 신생아의 발뒤꿈치 채혈 전 국소 진동과 급성 통증·울음 결과를 다룬다. 처치 통증에 관한 근거이지, 배시넷에서의 일반 진정이나 수면 개선 근거가 아니다.

### 4.2 미숙아·산전 opioid 노출 신생아 연구
- **Bloch-Salisbury et al. (2009) 및 Smith et al. (2015):** stochastic mechanosensory stimulation과 관련된 미숙아 호흡 생리 연구다. IBI, apnea, desaturation 등 생리 지표는 settling·울음·수면 효능과 별도다.
- **Zuzarte et al. (2017):** 산전 opioid 노출 신생아의 움직임 및 생리 지표를 다룬다. 움직임 감소를 주관적 진정이나 건강 영아의 수면 개선으로 바꾸어 해석하지 않는다.
- **Prapela FDA De Novo 및 Bloch-Salisbury et al. (2023):** 특정 의료 적응증과 임상 집단의 규제·임상 자료다. 2023년 RCT의 전체 분석군 약물치료 비율은 TAU 35.6%, SVS 30.9%, P=.60으로 유의한 차이가 없었다. 노출 시간과 결과의 연관성 및 responder subgroup은 전체 무작위 비교와 분리해 해석한다. 6/58 shutdown 관찰만으로 rebound나 인과적 위해를 단정하지 않는다.
- **SNOO NCT05711927 / 2024 보고:** 미숙아 20명 규모이며 rocking + swaddling + white noise 복합중재다. quiet/active sleep 분포 결과를 총 수면시간이나 울음 감소와 혼동하지 않는다. 총 수면시간 비율과 awake/crying의 유의한 차이는 보고되지 않았고, 계획된 두 번째 시점의 일부 생리 자료는 수집되지 않았다. SNOO 결과를 진동 단독 효능으로 귀속하지 않는다.
- **Poets et al. (2024):** 전동 rocking 연구에서 수면 지표의 유의한 개선이 확인되지 않았다. rocking과 vibration은 다른 물리 중재이지만, null result를 근거표에서 제거하지 않는다.

- **Singh et al. (online 2025; issue 2026):** 산전 opioid 노출 신생아 62명을 대상으로 한 다기관 비눈가림 RCT. 약물치료 시작은 SVS 4/40 (10.0%) vs 표준 4/22 (18.2%), 조정 OR 0.54 (95% CI 0.10–2.85), P=.46으로 유의한 차이가 없었다. 퇴원 준비도는 중앙값 3.9일 vs 4.9일, 조정 rate ratio 0.75 (95% CI 0.53–1.05), P=.09. Cry data subset n=46에서 fussy/pain cry 시간과 cry strength 차이는 유의하지 않았다. 보호자·간호사의 긍정적 수용성 설문은 객관적 진정 효능과 구분한다. 계획 표본 120명 대비 62명 등록 후 조기 종료했고, 일반 건강 영아의 수면/진정 연구가 아니다. [1차 추출 문서](MAJUNG_E001F_SINGH_2026_NOWS_RCT_PRIMARY_EXTRACTION_2026-10-13.md)

**통합 해석:** 문헌은 연구 질문·측정·위험 관찰을 설계하는 데 도움이 되지만, 현재 확보된 자료는 MAJUNG이 일반 건강 영아의 진정·울음·수면을 개선한다고 직접 입증하지 않는다.

## 5. Claim 단계별 상태

| Claim ID | 주장 후보 | 현재 상태 | 판정에 필요한 핵심 증거 |
|---|---|---|---|
| C1 | 정의된 설정에서 접촉면에 재현 가능한 진동을 전달한다 | 미확인 | 실측 파형·주파수·변위/가속도·위치 편차·반복성·불확도 |
| C2 | 하중·침구·설치 조건에 따른 출력 변화가 알려져 있다 | 미확인 | 조건별 반복 측정 및 변동 범위 |
| C3 | 정상 및 예측 가능한 고장 조건에서 위험이 적절히 통제된다 | 미확인 | 위험 분석, bench 시험, 잔여 위험 검토 |
| C4 | 단기 settling에 영향을 준다 | 현재 주장 불가 | 적절한 대상군·조작적 endpoint·비교 설계·임상 자료 |
| C5 | crying/fussing을 줄인다 | 현재 주장 불가 | 사전 정의한 울음/보챔 endpoint와 적절한 대조 비교 |
| C6 | 수면을 개선한다 | 현재 주장 불가 | 타당한 수면 측정, 진동으로 인한 센서 오염 통제, 충분한 대조 자료 |
| C7 | 반복·장시간 사용에 안전하다 | 현재 주장 불가 | 반복/장기 노출과 위험에 맞는 별도 증거 |
| C8 | 특정 연령·집단에 사용할 수 있다 | 미결정 | intended use, 대상군별 증거, 위험·규제 검토 |
| C9 | 광고에서 특정 효능을 표현할 수 있다 | 현재 주장 불가 | 해당 문구를 직접 뒷받침하는 증거와 법규 검토 |

Claim은 기능 구현, 물리 출력, 공학 안전, 단기 효능, 수면, 장기 안전, 마케팅을 한 단계로 묶지 않는다.

## 6. 연구 질문과 측정 구조

### 연구 질문 후보
통상적인 적절한 돌봄을 유지하는 조건에서, MAJUNG 진동을 추가했을 때 사전에 정의한 settling까지의 시간이나 crying/fussing의 관찰 결과에 추가 변화가 있는가?

이 문장은 연구 가설 후보일 뿐, 진동이 효과가 있다는 전제가 아니다. 대상군과 실제 출력·위험 정보가 정리된 뒤 임상 연구자가 질문을 수정하거나 보류할 수 있다.

### Endpoint 계층
- **후보 1차:** 사전 정의한 settling 기준에 처음 도달하기까지의 시간(time-to-settling).
- **후보 2차:** crying/fussing 지속시간, 에피소드 수, 해결/미해결 비율.
- **탐색:** sleep-onset latency, awakening count, total sleep time 등. 타당한 수면 측정과 진동 센서 간섭 검증이 선행돼야 한다.
- **안전성:** 사전 정의한 이상 징후, 중단 사유, 장치·설치 문제, 노출 시간 및 대응 기록.

### 측정 원칙
- 장치 명령/상태, 접촉면 실측 출력, 행동 상태, 보호자 개입/통상 돌봄, 안전성 이벤트, 분석 endpoint를 각각 기록한다.
- 울음 중단은 수면과 동일하지 않다. quiet sleep 비율은 total sleep time과 동일하지 않다.
- 진동에 의해 움직인 액티그래피/움직임 센서 신호를 실제 수면으로 잘못 분류하지 않도록 검증한다.
- 수유, 기저귀, 통증, 질병, 불편 등 필요한 돌봄을 연구 때문에 지연하거나 진동으로 대체하지 않는다.
- 표본 수, 안전성 임계값, settling 유지시간, 최종 comparator는 임의로 정하지 않고 전문가 검토를 거친다.

## 7. 공학 시험과 설계 변경의 위치

현재 회로·PCB·펌웨어·액추에이터 설정은 개발 기준선이지 최종 동결 설계가 아니다. 제품 요구사항과 위험·검증 기준을 먼저 정하고, 측정 결과에 따라 설계를 수정한 뒤 재시험한다.

### 공학 시험 후보
1. **E-M001 — 실제 출력 존재/ON-OFF 구분:** 장치 명령과 접촉면의 실제 진동을 구분해 확인한다.
2. **E-M002 — 출력 특성화:** 주파수, 변위, 가속도, 파형, RMS/peak, 위치별 편차, 반복성, 불확도를 기록한다.
3. **E-M003 — 조건·환경 평가:** 하중, 매트리스/침구, 설치, 장시간 작동, 소음, 표면 온도와 예상 가능한 고장 조건을 검토한다.
4. **위험 분석 후 설계 수정 및 재검증:** 변경 사유, 하드웨어·펌웨어 버전, 영향 분석, 재시험 범위를 기록한다.

측정 장비는 실제 시험 질문과 요구 불확도에 따라 선택한다. 장비를 먼저 구매하거나 내부 센서 수치만으로 접촉면 출력을 입증했다고 가정하지 않는다. 벤치 시험 결과는 임상 효능이나 영아 대상 안전성의 대체 증거가 아니다.

### 별도 하드웨어 디버깅 트랙
이전 개발 기록에는 PCB #0005에서 BLE 연결과 START→RUNNING 상태 전환은 되지만 익사이터가 반응하지 않는 문제가 있다. 이는 명령 상태와 실제 구동을 분리해서 진단해야 하는 별도 구현 이슈다. 최신 EasyEDA Pro Schematic1/PCB1, BOM, 필요 시 netlist/DRC와 정확한 액추에이터 정보를 기준으로 점검한다. 확인 전 핀 이름·전압·원인을 추정하지 않는다. 전원이 들어간 노출 회로의 위험한 프로빙을 지시하지 않는다.

이 하드웨어 문제가 해결돼도 효능·안전 근거가 자동으로 생기지 않으며, 반대로 연구 계획은 시제품 작동 여부와 무관하게 문서 수준에서 준비할 수 있다.

## 8. 임상 연구자 협업 준비 상태

연구자에게 단순히 “진동이 아기에게 효과가 있는지 연구해 달라”고 요청하는 대신 아래 자료를 전달할 수 있도록 준비한다.

1. 현재 Claim과 직접 근거·반대 근거·미해결 질문
2. E001-A~F 표준 추출 상태표와 원문 추적 링크
3. 후보 연구 질문과 endpoint 정의가 필요한 항목
4. comparator, 시간 경과, 초기 행동 상태, 보호자 개입 및 결측 처리 질문
5. 실제 출력과 위험 자료가 추가로 필요한 목록
6. 안전성 감시·중단 절차 및 필요한 기관/IRB/규제 검토 질문
7. 연구자 검토 의견·수정 이력·협업 상태 기록표

연구자 후보의 이름이나 이전 논문만으로 협업을 확정하지 않는다. 현재 공식 협업이나 연구 승인 상태는 미확정이다. 실제 사람 대상 연구는 적절한 임상 책임자, 기관별 윤리·안전 검토와 필요한 승인 절차 후에만 진행한다.

## 9. 지금까지 문서화된 산출물

### 프로젝트 중심 문서
- [1순위 사고·행동철칙](MAJUNG_1ST_PRINCIPLE_EVIDENCE_AND_MEDICAL_COLLABORATION_2026-10-08.md)
- [연구·실험 마스터 플랜](MAJUNG_RESEARCH_AND_EXPERIMENT_MASTER_PLAN_2026-10-12.md)
- [Claim–Evidence–Gap–Experiment 매트릭스](MAJUNG_CLAIM_EVIDENCE_GAP_EXPERIMENT_MATRIX_2026-10-12.md)
- [제품 요구사항 초안](MAJUNG_PRODUCT_REQUIREMENTS_DRAFT_2026-10-12.md)
- [Endpoint·측정법·이벤트 기록 설계](MAJUNG_ENDPOINT_MEASUREMENT_AND_EVENT_LOGGING_PLAN_2026-10-12.md)
- [임상 연구 Protocol Synopsis 초안](MAJUNG_CLINICAL_PROTOCOL_SYNOPSIS_DRAFT_2026-10-12.md)
- [임상·측정 연구자 검토 질문](MAJUNG_CLINICAL_RESEARCHER_REVIEW_QUESTION_SET_2026-10-13.md)

### 문헌 감사·추적성
- [1차 문헌 원문 재확인·근거 해석 업데이트](MAJUNG_PRIMARY_SOURCE_AUDIT_AND_EVIDENCE_UPDATES_2026-10-12.md)
- [E001-A~E 1차 추출 문서 감사](MAJUNG_E001_PRIMARY_EXTRACTION_AUDIT_2026-10-12.md)
- [E001-A/B/C 수치별 locator 감사](MAJUNG_E001ABC_NUMERICAL_LOCATOR_AUDIT_2026-10-12.md)
- [E001-D FDA locator 감사](MAJUNG_E001D_FDA_LOCATOR_AUDIT_2026-10-12.md)
- [E001-E 수치별 locator 감사](MAJUNG_E001E_NUMERICAL_LOCATOR_AUDIT_2026-10-12.md)
- [E001-A~F 표준 추출 필드·상태 매트릭스](MAJUNG_E001_STANDARDIZED_EXTRACTION_STATUS_MATRIX_2026-10-13.md)
- [Singh et al. 2025/2026 다기관 SVS RCT 추출](MAJUNG_E001F_SINGH_2026_NOWS_RCT_PRIMARY_EXTRACTION_2026-10-13.md)
- [SNOO 공식 등록 결과–2024 보고서 대조](MAJUNG_SNOO_NCT05711927_REGISTRY_REPORT_RECONCILIATION_2026-10-12.md)

### 공학 시험·측정 준비
- [E-M001/E-M003 시험 프로토콜](MAJUNG_E-M001_E-M003_ENGINEERING_TEST_PROTOCOL_2026-10-08.md)
- [최소 비용 측정 구성](MAJUNG_E-M001_MINIMUM_COST_MEASUREMENT_SETUP_2026-10-08.md)
- [물리 출력 측정 준비도 감사](MAJUNG_PHYSICAL_OUTPUT_MEASUREMENT_READINESS_AUDIT_2026-10-08.md)
- [E-M001 실행·연구 전달 패키지](MAJUNG_E-M001_BENCH_EXECUTION_AND_RESEARCH_HANDOFF_PACK_2026-10-09.md)

문서가 존재한다는 것은 그 주제의 계획·검토 자료가 있다는 뜻이지, 해당 실험이나 검증이 수행됐다는 뜻이 아니다.

## 10. 남은 일과 우선순위

### P0 — 문헌 추적성과 통합 근거표
- E001-A/B/C/E/F의 핵심 수치를 저널 인쇄 페이지·섹션·표/그림 행까지 대조한다.
- E001-D의 주요 FDA 문장·표·미공개/비교 불가 자료를 확인 상태와 함께 보존한다.
- adverse-event status를 reported / none reported / not reported / not assessed / unclear로 정확히 코딩한다.
- enrolled/randomized/analyzed, 분모, endpoint, subgroup/exposure association, missing/not collected를 분리한다.
- 독립 검토 여부를 기록한다. 완료되지 않은 locator를 완료로 표시하지 않는다.

### P1 — 연구자에게 전달할 최소 패키지
- 프로젝트 요약, claim matrix, 근거표, protocol synopsis, endpoint 계획, 연구자 질문을 하나의 전달 패키지로 묶는다.
- 어떤 수치와 주장이 미확인인지 첫 페이지에서 보이게 한다.
- 전문가 피드백과 협업 상태를 추측 없이 기록한다.

### P2 — 제품·공학 기준선과 실측 준비
- intended use, 목표 대상, 설치/침구 시나리오 등 제품 요구사항 미결정을 표시한다.
- 현재 하드웨어/펌웨어/기구 버전 및 최신 EasyEDA export를 확인한다.
- 실제 출력 측정의 측정량·센서/기준 장비·측정 위치·불확도·반복 횟수·판정 기준을 시험 질문에 맞춰 결정한다.
- 출력 및 위험 시험 결과에 따라 설계를 변경하고 재검증한다.

### P3 — 임상·규제 단계
- 임상팀이 대상군, comparator, endpoint, 안전성 모니터링과 중단 절차를 검토한다.
- 통계 전문가가 설계와 표본 수 산정 전제를 정한다.
- 기관/IRB 및 필요한 규제 경로를 확인한다.
- 승인된 절차 없이 영아 대상 시험을 진행하지 않는다.
- 결과에 따라 claim을 확정·제한·보류한다.

## 11. 종료 기준

### WP-0 문헌 추적성 완료
- 핵심 수치가 원문 인쇄 페이지·섹션·표/그림까지 추적 가능하다.
- 표본 흐름과 분석 분모가 분리돼 있다.
- 1차·2차·탐색·하위집단·노출량 연관 분석이 구분돼 있다.
- 이상사건 보고 상태와 미수집 자료가 정확히 코딩돼 있다.
- evidence type, quality, directness가 별도 필드다.
- 독립 검토 상태와 미해결 항목이 남아 있다.

### 공학 검증 완료
- 요구사항과 위험이 시험 항목에 연결돼 있다.
- 실제 접촉면 출력과 측정 불확도가 기록돼 있다.
- 정의된 조건과 장치 버전이 재현 가능하다.
- 위험·고장·환경 시험 결과 및 잔여 위험이 검토돼 있다.
- 설계 변경 후 필요한 재시험이 수행돼 있다.

### 임상·Claim 판정 완료
- 적절한 연구 책임자·기관 검토·윤리 승인 절차가 충족돼 있다.
- endpoint와 분석계획이 사전 정의돼 있다.
- 긍정·부정·무효·안전성 결과가 모두 보고돼 있다.
- Claim은 결과가 실제로 지지하는 범위에 제한돼 있다.

**현재 상태:** WP-0 진행 중. 공학 출력 실측·위험 시험은 미완료. 임상 효능·안전성은 미입증. 연구기관 협업·승인은 미확정.

## 12. 핵심 의사결정 기록

1. 최우선 목표는 진동 구현 자체가 아니라 판매 가능한 제품 주장을 뒷받침할 효과·안전 근거를 구축하는 것이다.
2. 연구 계획은 현재 시제품 작동 상태와 분리해 진행한다.
3. 현재 회로·PCB는 변경 가능한 개발안이다. 설계 동결은 요구사항·위험·검증 이후 별도 결정한다.
4. Evidence type, evidence quality, directness를 합산해 하나의 점수로 만들지 않는다.
5. 건강 영아, 미숙아, 산전 opioid 노출 신생아, 시술 통증 대상군의 결과를 서로 바꾸어 적용하지 않는다.
6. rocking, whole-body cradle movement, local vibration, mattress stochastic stimulation, SNOO 복합중재를 동일한 물리 자극으로 취급하지 않는다.
7. safety evidence와 efficacy evidence를 별도로 관리한다.
8. null/negative results, subgroup results, missing data, adverse-event reporting gaps를 보존한다.
9. settling, crying/fussing, sleep state, total sleep을 분리한다.
10. 사람 대상 연구는 적절한 임상 책임자 및 기관의 필요한 검토·승인 뒤에만 진행한다.
11. 연구자 후보는 연락·관심·협업 확정 상태를 구분한다.
12. 문서 작성, 설계 계획, 실제 측정, 임상 검증, 규제 적합성은 각각 다른 완료 상태다.

## 13. 연결 문서와 다음 실행

진입점: [MAJUNG_INDEX.md](MAJUNG_INDEX.md)

다음 실행은 P0 문헌 추적성 마무리다. 이후 통합 근거표를 갱신하고, 연구자 전달 패키지를 구성하며, 실제 출력·위험 시험을 준비한다. 어떤 단계에서도 근거가 없는 효능·안전성 주장을 앞서 확정하지 않는다.
