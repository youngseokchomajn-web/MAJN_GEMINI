# MAJUNG E001-A~E001-E 1차 문헌 추출 문서 감사 — 2026-10-12

**목적:** 기존 원문 추출 문서가 동일한 필드와 출처 추적성을 갖추고 있는지 점검한다. 본 문서는 논문 전체를 새로 재분석했다는 선언이 아니며, 실제 결과를 변경하지 않는다.

## 1. 감사 기준

각 source extraction에는 최소한 다음 항목이 있어야 한다.

1. Full citation, DOI/PMID/PMCID 또는 공식 문서 URL
2. Source type 및 Evidence type
3. Evidence quality와 directness를 서로 분리
4. Population, inclusion/exclusion, sample enrolled/analyzed
5. Intervention, comparator, actual physical exposure
6. Pre-specified primary endpoint와 secondary/exploratory endpoint
7. Primary result, effect estimate, uncertainty, p-value/CI가 제공될 때의 값
8. Adverse events 및 안전성 관찰: 없음/미보고/해당 없음 구분
9. Limitations, risk of bias, null/negative result
10. MAJUNG에 대한 직접 적용 가능성과 적용 불가 주장
11. 핵심 숫자·해석마다 DOI/URL 및 가능한 경우 page/table/figure/section 위치
12. Extracted fact, author interpretation, MAJUNG inference를 구분

## 2. 기존 문서 감사 결과

| 문서 | 강점 | 추가 보완 필요 |
|---|---|---|
| E001-A Smith 2015 | 인구집단, ON/OFF crossover, 물리 출력, 결과 범주, 통계 구조, MAJUNG 직접성 한계가 구체적 | 주요 결과의 표/그림/페이지 추적을 각 수치에 붙이기. adverse event 보고를 '미보고'와 '없음'으로 구분. 실제 분석집단과 누락 데이터 설명 재확인 |
| E001-B Bloch-Salisbury 2009 | 물리 출력, 공간 균일성, 소리, 하중/침구 시험, 각성 임계 검토 등 공학 방법이 상세 | 주요 측정값·방법에 원문 figure/table/page를 붙이기. 안전성·이상사건의 정확한 보고 상태를 구분. sample flow 및 제한사항을 표준 필드로 추가 |
| E001-C Zuzarte 2017 | 대상·출력·ON/OFF·환경/돌봄 로그·생리/행동 측정이 상세 | 표본 흐름, 사전 지정 결과 여부, 결과 수치의 표/그림 위치, 안전성/이상사건 보고, 교란 및 연구 설계 한계를 동일 필드로 보강 |
| E001-D Prapela FDA | 공식 9페이지 De Novo Summary를 printed-page 기준으로 대조; intended use, bench testing, clinical evidence, risks, special controls, benefit-risk locator audit 추가 | 상세 bench 수치 일부는 redacted 상태. safety support와 effectiveness evidence를 분리하고, 일반 영아 Claim으로 확대하지 않음 |
| E001-E Bloch-Salisbury 2023 | Table 2/3, Figure 1/2, eTable 3/4 및 publisher HTML locator를 숫자별로 분리한 보조 감사 문서 추가 | 저널 인쇄 페이지 단위 locator와 다중성/통계 분석계획의 전체 감사는 별도 확인이 남음. shutdown 관찰은 인과적 rebound로 해석하지 않음 |

## 3. 이번 감사에서 이미 확인한 공통 해석 규칙

- E001-A~C는 주로 미숙아/특정 임상 집단의 생리 반응 연구다. 일반 영아의 진정·수면 효능 연구가 아니다.
- E001-B의 표면 출력 측정·공간 균일성·하중/침구·소리 평가는 MAJUNG의 공학 시험 방법을 설계하는 데 유용하지만, 그 수치를 영아에게 안전한 기준값으로 가져올 수 없다.
- E001-C의 시간 동기화와 간호/보호자 개입 기록은 향후 데이터 구조의 참고가 되지만, 관찰된 생리 변화만으로 일반 영아 진정 효과를 주장할 수 없다.
- E001-D의 규제상 적응증은 prenatal opioid exposure가 있고 NOWS가 있는 만삭 신생아의 제한된 임상 사용이다. 일반 소비자 제품의 수면·진정 Claim과 동일하지 않다.
- E001-E에서 전체 무작위 배정의 약물치료 비율 차이는 유의하지 않았다. 노출 시간과 결과의 연관성 및 3주 이내 치료 완료 하위집단은 별도로 해석해야 한다.
- adverse event가 보고되지 않았다는 표현은 실제 원문에서 수집·보고 여부를 확인한 뒤에만 사용한다. 미기재는 '안전'이나 '이상사건 없음'과 다르다.

## 4. 표준 추출 필드 제안

각 문서의 앞부분에 다음 metadata table을 넣는다.

| Field | Value |
|---|---|
| Source ID | E001-A ... E001-E |
| Full citation | Complete bibliographic citation |
| Primary source URL | DOI or official full text |
| Population | Exact population and sample analyzed |
| Intervention | Device/stimulus and comparator |
| Evidence type | Engineering / physiological / behavior / sleep / clinical efficacy / regulatory |
| Evidence quality | Design and reporting appraisal |
| Directness to MAJUNG | High / moderate / low with rationale |
| Primary endpoint | As prespecified in source |
| Primary result | Exact result with table/figure/section locator |
| Adverse events | Reported / none reported / not reported / not applicable |
| Limitations | Design, sample, bias, generalizability |
| MAJUNG implication | Method/design use only or direct evidence status |
| Extraction status | Verified / partial / needs source locator |

Quality와 directness는 다른 축이다. 예를 들어 잘 설계된 RCT라도 다른 임상 집단과 다른 endpoint를 다루면 MAJUNG 일반 영아 진정 Claim에 대한 직접성은 낮다.

## 5. 실행 순서

1. E001-E: 전체 무작위 결과, 노출시간 분석, responder subgroup, discontinuation observation의 source locator를 보강한다.
2. E001-D: FDA 페이지별 risk/special controls/indication 위치를 보존하면서 effectiveness와 safety support를 분리한다.
3. E001-A/B/C: 주요 결과 수치 및 실제 출력 측정에 source locator를 추가한다.
4. 모든 문서에 adverse event status를 표준화한다.
5. 최종적으로 master evidence matrix에서 extraction status와 unresolved locator를 표시한다.

## 6. 완료 기준

- 주요 숫자와 해석을 원문 표/그림/섹션까지 추적할 수 있다.
- primary endpoint와 secondary/subgroup/exposure analysis가 혼합되지 않는다.
- adverse event가 '없음', '미보고', '미확인' 중 무엇인지 명시된다.
- evidence type, quality, directness가 분리돼 있다.
- MAJUNG에 직접 적용할 수 없는 근거가 직접 효능 근거로 잘못 표현되지 않는다.

현재 상태: E001-A/B/C의 주요 수치별 Results subsection, Table/Figure 및 제한적 안전성 보고 상태를 보조 감사 문서에 정리했다. E001-D는 FDA De Novo Summary printed-page locator, E001-E는 핵심 수치별 Table/Figure/eTable 및 publisher HTML locator를 별도 기록했다. 남은 일은 A/B/C의 저널 인쇄 페이지 기준 대조, E001-E의 저널 인쇄 페이지 기준 대조, 그리고 전체 문서의 표준 필드·미해결 항목 통합이다.
