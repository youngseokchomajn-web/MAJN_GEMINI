# MAJUNG Phase 1 Medical Research Brief

## 1. Purpose

이 문서는 MAJUNG의 효능을 주장하기 위한 자료가 아니라, 의료연구자와 함께 검토할 수 있는 초기 연구 질문과 측정 구조를 정리한 연구 brief다.

현재 문헌은 특정 임상군에서 기계적/진동 자극이 행동·생리 반응을 바꿀 가능성을 보여주지만, 건강한 만삭 영아에서 MAJUNG의 특정 자극이 수면 또는 진정을 개선한다고 결론내릴 수준은 아니다.

따라서 Phase 1의 목적은 **효과를 증명하는 것보다 실제 자극과 영아의 단기 반응을 신뢰성 있게 측정할 수 있는지 확인하는 것**으로 둔다.

## 2. Research question

### Primary candidate
사전에 정의된 MAJUNG 물리 자극이 건강한 만삭 영아의 특정 초기 행동상태에서 caregiver intervention 없이 발생하는 settling 또는 fussing/crying episode resolution의 시간 또는 확률을 변화시키는가?

### Secondary
- 행동상태 전이: crying/fussing → drowsy → sleep 등
- quiet sleep / active sleep 비율
- HR / HRV / RR / SpO2 / movement 변화
- 초기 상태에 따른 효과 차이
- 실제 mattress-surface vibration과 행동 반응의 exposure-response 관계
- caregiver/environmental intervention 통제 후 결과 유지 여부
- 이상반응 및 비정상 생리반응 여부

## 3. Why this endpoint structure

영아 sleep-state scoring은 관찰자 간 차이가 발생할 수 있으므로 명확한 scoring rule과 training이 필요하다. CHIME 연구에서는 scoring 기준을 수정하고 재훈련한 뒤 sleep-state inter-rater kappa가 0.68까지 개선됐다. [REF: CHIME reliability]

행동 기반 sleep annotation은 PSG와 비교해 wake/active sleep/quiet sleep을 구분할 수 있는 가능성이 보고됐지만, 더 큰 표본과 다양한 집단에서 추가 검증이 필요하다. [REF: behavioral annotation]

따라서 MAJUNG은 '진정도'라는 단일 점수를 만들지 않고, 시간축의 행동상태와 사건(event)을 직접 기록한다.

## 4. Proposed observation structure

각 관찰 세션은 다음 공통 timeline을 가진다.

baseline → stimulation ON → response → stimulation OFF → recovery

동시에 다음 데이터를 timestamp로 기록한다.

device command | measured mattress vibration | acoustic/environmental data | infant behavioral state | physiology | caregiver intervention

영상은 가능한 경우 infant와 caregiver를 동시에 확인할 수 있도록 설계한다. Videosomnography 연구에서도 infant state와 parental intervention을 시간축으로 함께 코딩한 선행 방법이 있다.

## 5. Behavioral coding

최소 상태 분류 후보:
- Quiet sleep
- Active sleep
- Drowsy / transition
- Awake / calm
- Fussing
- Crying
- Indeterminate / not scorable

추가 event:
- crying/fussing onset
- settling onset
- sleep onset
- awakening
- caregiver intervention onset/end

초기 연구에서는 자동 분류를 primary 판정에 사용하지 않는다. 자동 videosomnography는 sleep timing에는 유용하지만 wake 판정의 한계가 보고되어 있다.

## 6. Caregiver intervention control

다음 항목은 별도 event로 기록한다.
- holding
- rocking/manual movement
- feeding
- pacifier
- diaper change
- swaddling/unswaddling
- touch/patting
- verbal soothing
- environmental sound/light change

이 기록이 있어야 vibration ON 뒤에 울음이 줄었다고 해도 그것이 MAJUNG 때문인지 caregiver intervention 때문인지 구분할 수 있다.

## 7. Physical stimulus requirement

임상 관찰 전에 다음을 먼저 확정한다.
- commanded stimulation
- actual mattress-surface vibration
- frequency/spectrum
- RMS/peak amplitude 또는 displacement estimate
- load dependence
- spatial variation
- acoustic output
- time stability

문헌에서 사용된 30–60 Hz 또는 특정 displacement 값을 MAJUNG의 안전 기준이나 목표값으로 복사하지 않는다.

## 8. Phase 1 design concept

권장 기본 구조는 within-subject repeated exposure이며, 정확한 ON/OFF 시간과 총 노출량은 의료연구자와 IRB 검토 후 결정한다.

가능한 기본 구조:
baseline → ON → OFF → ON/OFF repeat

초기 상태를 반드시 기록하고, intervention 순서는 가능한 경우 counterbalance한다.

### Phase 1 success criteria
1. 자극이 실제 mattress surface에서 반복적으로 측정됨
2. 영상/행동 coding이 안정적으로 수행됨
3. caregiver intervention을 stimulation과 시간축에서 분리할 수 있음
4. 동일 조건 반복에서 반응 방향이 재현되는지 평가 가능함
5. clinically meaningful adverse event 여부를 평가할 수 있음

효과가 관찰되지 않는 것도 유효한 결과로 기록한다.

## 9. What Phase 1 must NOT conclude

Phase 1 결과만으로 다음을 주장하지 않는다.
- MAJUNG이 아기를 재운다
- MAJUNG이 수면시간을 증가시킨다
- 특정 진동 주파수가 안전하다
- 특정 진동 amplitude가 최적이다
- SNOO와 동등한 효과가 있다
- 장기적인 수면 또는 발달 효과가 있다

## 10. Medical researcher decisions required

다음 항목은 개발자가 임의로 결정하지 않고 의료연구자/IRB와 확정한다.
- population and age window
- inclusion/exclusion criteria
- baseline state requirement
- session duration
- ON/OFF sequence
- primary endpoint
- behavioral-state coding standard
- physiological monitoring requirements
- stopping criteria
- adverse-event definition
- sample size / power
- randomization or counterbalancing
- sham/off comparator feasibility
- consent/privacy/data retention

## 11. One-paragraph handoff

진동이 아기를 재운다고 가정하고 시험하려는 것이 아니라, 기존 연구에서 관찰된 영아의 기계적 자극 반응이 MAJUNG의 실제 물리 자극에서도 재현되는지, 그리고 그 반응이 초기 행동상태와 caregiver intervention에 따라 어떻게 달라지는지를 먼저 검증하고 싶습니다. 이를 위해 실제 mattress-surface vibration을 독립적으로 측정하고, infant behavioral state와 caregiver intervention을 timestamp로 동기화해 단기 settling/fussing resolution과 생리적 변화를 관찰하는 초기 feasibility 연구부터 설계하고자 합니다.

## 12. Current status

- Literature review: frozen
- Evidence matrix: established
- Engineering measurement protocol: established
- Medical research questions: established
- Endpoint hierarchy: established
- Phase 1 medical research brief: this document

Next gate: **prototype physical-output characterization → medical researcher review → protocol refinement → IRB/ethics review**.

이 문서는 임상시험 계획서나 의료기기 안전성 평가 문서가 아니다.
