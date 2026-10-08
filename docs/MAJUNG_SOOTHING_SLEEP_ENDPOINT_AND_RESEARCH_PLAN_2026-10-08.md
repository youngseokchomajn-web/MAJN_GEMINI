# MAJUNG Infant Soothing / Sleep Endpoint Framework & Research Plan

작성일: 2026-10-08

## 1. 이번 단계의 목적

현재까지의 진동 연구는 주로 다음을 보여준다.

- 저강도 mattress-surface vibrotactile stimulation을 실제 물리량으로 정의하고 측정할 수 있다.
- 일부 신생아/미숙아 집단에서 호흡·심박·움직임 등 단기 생리반응을 관찰할 수 있다.
- 그러나 이것만으로 일반적인 건강한 만삭아의 '진정(soothing)' 또는 '수면 개선'을 주장할 수는 없다.

따라서 MAJUNG의 다음 연구 단계는 '진동이 좋다'를 전제로 하지 않고,

Source → Endpoint → Measurement → Study design → Gap → Decision

순서로 설계한다.

핵심 질문은 다음과 같다.

> MAJUNG의 특정 물리적 자극이 영아의 fussing/crying, behavioral state, sleep organization 또는 physiological state에 재현 가능한 변화를 만드는가?

## 2. 새롭게 확인된 근거

### E002-A — SNOO preterm randomized study, NCT05711927

ClinicalTrials.gov에 등록된 무작위 연구는 미숙아에서 SNOO와 전통적 bassinet을 비교했다. SNOO 조건은 rocking + white noise + swaddling을 포함하며, powered-off 조건은 움직임과 소리가 없는 비교조건이다. 3시간 sleep assessment에서 sleep stage와 vital signs를 측정하고 EEG/NIRS도 계획했다.

2025년 결과가 등록되어 있으며, 실제 분석은 20명(SNOO 11, control 9)이다. SNOO군은 quiet sleep 비율이 높고 active sleep 비율이 낮았으나 전체 sleep time, awake, crying에는 유의한 차이가 없었다.

중요한 해석:
- sleep architecture를 객관적 endpoint로 사용할 수 있는 직접적인 선례다.
- 그러나 SNOO는 rocking + sound + swaddling의 복합중재다.
- 따라서 vibration-only efficacy 근거로 사용할 수 없다.
- MAJUNG에서는 'quiet sleep proportion'을 후보 endpoint로 유지하되, 단독 efficacy claim으로 연결하지 않는다.

### E002-B — SNOO / five-S scoping review

2023년 scoping review는 SNOO와 five-S soothing literature를 검토했다. 검토된 SNOO 관련 연구 수 자체가 적었고, 정상 영아에서 수면 및 crying 감소 가능성을 제시했지만 추가 연구가 필요하다고 결론냈다.

특히 SNOO 관련 결과는:
- sleep duration
- longest sleep period
- night waking
- fussiness
- heart rate
- heart rate variability
등을 사용했다.

중요한 해석:
- 후보 endpoint를 넓히는 데는 유용하다.
- 그러나 SNOO의 rocking, white noise, swaddling이 동시에 작용하므로 MAJUNG vibration-only 근거로는 낮은 directness다.

### E002-C — 2026 responsive bassinet longitudinal feasibility study

2026년 Sensors 논문은 SNOO의 timestamped activity logs를 이용해 26,187명의 영아에서 대규모 sleep/soothing metric을 추출하는 방법을 제시했다.

사용한 metric:
- Total Night Sleep
- Longest Sleep Stretch
- Sleep Efficiency
- Number of Fussing Episodes
- Resolved Fussing Episodes
- Unresolved Fussing Episodes
- Proportion of Resolved Episodes
- Intervention Delay

특히 중요한 점은 '기기 상태 변화'를 단순한 sleep measurement로 취급하지 않고, fussing → bassinet response → resolution 또는 caregiver intervention의 시간적 관계를 분석했다는 것이다.

단, 이 연구는 descriptive feasibility study이며 특정 치료효과를 검증한 RCT가 아니다. 또한 제조사 관련 연구자가 포함되어 있고, device-derived proxy를 사용한다.

MAJUNG에 대한 직접적 가치:
- endpoint 구조와 timestamp schema에 매우 높은 가치
- efficacy evidence로는 낮은 directness
- 향후 MAJUNG 연구의 event-log 설계에 높은 가치

## 3. Endpoint hierarchy

MAJUNG에서는 endpoint를 다음 4층으로 나눈다.

### Layer 1 — Primary behavioral endpoint

가장 먼저 확인할 후보:

1. Crying/fussing duration
2. Fussing episode count
3. Time-to-settling
4. Proportion of episodes resolved without caregiver intervention

이 중 초기 human study에서는 **time-to-settling** 또는 **fussing episode resolution**을 가장 중요한 단기 endpoint 후보로 둔다.

이유:
- 자극 ON/OFF 직후의 변화와 직접 연결할 수 있다.
- caregiver intervention의 영향을 timestamp로 분리할 수 있다.
- 장시간 sleep study보다 작은 연구에서도 측정 가능하다.

### Layer 2 — Sleep organization

후보:
- quiet sleep proportion
- active sleep proportion
- total sleep time
- longest uninterrupted sleep stretch
- sleep efficiency
- sleep onset latency
- number of awakenings

단, infant sleep은 연령과 발달단계에 따라 크게 달라지므로 단순 total sleep time만으로 효과를 판단하지 않는다.

특히 preterm 연구에서는 quiet sleep / active sleep 분포가 중요한 endpoint로 사용됐다.

### Layer 3 — Physiological response

후보:
- heart rate
- heart rate variability
- respiratory rate
- SpO2
- movement activity

이는 '진정'의 직접 endpoint라기보다 보조적인 physiological response endpoint로 분류한다.

특히 HR/HRV는 baseline과 자극 직후의 변화를 비교하는 데 유용하지만, 임상적 의미를 과장하지 않는다.

### Layer 4 — Engineering / environmental covariates

반드시 함께 기록:
- actual mattress-surface vibration
- frequency spectrum
- displacement/acceleration
- sensor position
- load
- acoustic level
- ambient sound
- device state
- stimulation intensity
- firmware/hardware version

이 Layer 4가 없으면 human outcome이 나와도 어떤 physical exposure에서 나온 결과인지 재현하기 어렵다.

## 4. Endpoint를 하나로 고르지 않는 이유

'아기가 안정됐다'는 하나의 측정값으로 정의하지 않는다.

다음과 같이 계층화한다.

Primary:
- settling / fussing resolution

Secondary:
- crying/fussing duration
- behavioral state
- sleep organization

Exploratory:
- HR
- HRV
- RR
- SpO2
- movement

Safety:
- adverse events
- abnormal physiological responses
- excessive acoustic/mechanical exposure

이 구조라야 '진동 → 진정 → 수면'을 한 번에 주장하는 오류를 피할 수 있다.

## 5. 가장 중요한 연구설계 결정

### Phase H0 — 비인체 engineering

목표:
MAJUNG이 실제로 어떤 자극을 전달하는지 확정.

측정:
- mattress surface acceleration
- displacement estimate
- frequency spectrum
- spatial uniformity
- load dependence
- bedding dependence
- acoustic output
- thermal behavior
- time stability

결과:
MAJUNG stimulation envelope vX.Y.Z를 고정한다.

### Phase H1 — 짧은 human within-subject response study

목표:
'자극이 들어가는 순간' 영아의 행동이 달라지는지 확인.

권장 구조:
- baseline
- predefined stimulation ON
- stimulation OFF
- 필요시 반복 crossover

각 epoch에 대해:
- timestamp
- device command
- measured vibration
- sound
- crying/fussing
- behavioral state
- HR/RR/SpO2
- caregiver intervention

을 같은 timeline에 저장한다.

이 단계에서는 장기간 수면 개선을 주장하지 않는다.

### Phase H2 — controlled clinical study

H1에서 명확한 단기 endpoint signal이 발견된 경우에만 진행한다.

가능한 비교:
- MAJUNG stimulation
- sham/off
- standard bassinet

가능하면 assessor blinding 또는 video-based blinded scoring을 고려한다.

Primary endpoint는 사전에 하나로 고정한다.

### Phase H3 — longitudinal sleep study

H2에서 short-term soothing effect가 재현될 경우:
- total sleep
- longest sleep stretch
- sleep efficiency
- night waking
- fussing episodes
- caregiver intervention
등을 장기간 관찰한다.

이 단계에서야 'sleep improvement'를 별도의 연구질문으로 다룬다.

## 6. 데이터 구조

모든 연구에서 최소한 다음 event schema를 사용한다.

| timestamp | device_state | commanded_level | measured_vibration | acoustic_level | behavioral_state | crying/fussing | HR | RR | SpO2 | caregiver_event | version |
|---|---|---|---|---|---|---|---|---|---|---|---|

핵심은 **commanded_level과 measured_vibration을 분리하는 것**이다.

예:
command = level 2
≠
actual mattress displacement = X μm

human outcome은 반드시 actual measured exposure와 연결할 수 있어야 한다.

## 7. Caregiver intervention을 반드시 별도 event로 기록

fussing이 감소했다고 해서 vibration 때문이라고 볼 수 없다.

다음 intervention을 timestamp로 기록한다.

- feeding
- diaper change
- holding
- rocking by caregiver
- pacifier
- medication
- repositioning
- removal from bassinet
- environmental disturbance

따라서 분석 단위는:

stimulation
→ infant response
→ caregiver intervention
→ outcome

으로 한다.

## 8. Null result 처리

다음 결과도 모두 정식 evidence다.

- crying 감소 없음
- settling time 차이 없음
- sleep time 차이 없음
- quiet sleep 차이 없음
- HR/HRV 변화 없음
- stimulation intensity와 response의 관계 없음

특히 H1에서 효과가 없으면 H2로 자동 진입하지 않는다.

## 9. MAJUNG 연구의 decision gates

### Gate G0 — Physical reproducibility

통과 조건:
- 실제 contact-surface vibration 측정 가능
- 반복 측정 재현성 확보
- load/bedding 영향 확인
- acoustic output 확인

불통과 → human study 중단.

### Gate G1 — Short-term response feasibility

통과 조건:
- predefined endpoint를 객관적으로 측정 가능
- timestamp synchronization 가능
- caregiver intervention 분리 가능
- adverse signal 없음

효과가 없더라도 측정 시스템이 유효하면 'no demonstrated short-term effect'로 기록한다.

### Gate G2 — Controlled efficacy

통과 조건:
- sham/off 대비 일관된 primary endpoint 차이
- predefined analysis에 부합
- physical exposure와 outcome의 연결 가능

통과 전에는 'sleep improvement' claim을 만들지 않는다.

### Gate G3 — Longitudinal benefit

통과 조건:
- 반복 연구에서 sleep/soothing benefit 재현
- 안전성 자료 확보
- age-dependent effect 검토
- caregiver/environment confounding 검토

## 10. 의학 연구자에게 장비를 제공하는 경로

현재 단계에서 가장 현실적인 협업 모델:

### Model A — 장비 + engineering characterization package

의료기관에 MAJUNG prototype만 전달하지 않는다.

함께 제공:
- hardware revision
- mattress revision
- stimulation protocol
- physical output measurement report
- acoustic report
- safety limits
- data dictionary
- event logging specification
- known failure cases

### Model B — 공동 연구

MAJUNG 측:
- device
- engineering measurement
- software/logging
- protocol support

의료연구자:
- IRB
- inclusion/exclusion
- clinical endpoints
- infant assessment
- adverse event monitoring
- statistical analysis

이 구조가 가장 적합하다.

## 11. 현재 evidence의 최종 판단

현재까지의 문헌을 종합하면:

### 높은 확신

- infant mattress vibrotactile stimulation은 물리적으로 정의·측정할 수 있다.
- 실제 contact-surface vibration, load, spatial uniformity, acoustic output을 함께 관리하는 것이 중요하다.
- infant response를 timestamp 기반으로 device exposure와 연결할 수 있다.
- sleep state, fussing, caregiver intervention을 객관적/반객관적 endpoint로 설계할 수 있다.

### 중간 확신

- 일부 preterm 또는 특수 임상집단에서 vibrotactile stimulation이 생리적 반응과 연관될 가능성이 있다.
- SNOO의 multimodal sensory intervention은 일부 연구에서 quiet sleep 증가 또는 fussing resolution 등의 신호를 보인다.

### 아직 입증되지 않음

- MAJUNG의 특정 vibration이 일반 건강한 영아의 soothing을 개선한다.
- MAJUNG vibration 단독으로 sleep duration 또는 sleep quality를 개선한다.
- 특정 frequency/amplitude가 일반 영아에게 최적이라는 결론.

## 12. 다음 실행 순서

1. 기존 E001 primary evidence matrix에 2017 Zuzarte와 2023 Bloch-Salisbury RCT를 정식 편입한다.
2. SNOO NCT05711927 결과를 별도 multimodal evidence로 등록한다.
3. endpoint taxonomy와 event schema를 MAJUNG 연구계획 문서의 표준으로 고정한다.
4. prototype engineering test E-M001~E-M003의 측정 항목을 이 endpoint 구조와 연결한다.
5. 의료연구자에게 제시할 1~2 page collaboration brief를 만든다.
6. 그 후에야 실제 기관/연구자 후보를 찾고 공동연구 문의를 진행한다.

## 13. Evidence integrity rule

SNOO 또는 Prapela 결과를 MAJUNG의 efficacy evidence로 직접 전환하지 않는다.

모든 결과는 다음 형태로 기록한다.

Population
→ Intervention
→ Comparator
→ Physical exposure
→ Endpoint
→ Result
→ Quality
→ Directness
→ Limitation
→ MAJUNG implication

특히 multimodal intervention은 vibration-only evidence와 별도 분류한다.
