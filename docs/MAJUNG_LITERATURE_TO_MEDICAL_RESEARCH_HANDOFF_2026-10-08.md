# MAJUNG 문헌 → 의료연구자 전달용 연구 프레임 v1.0 — 2026-10-08

## 1. 목적
현재 문헌 검토를 바탕으로, 의료연구자에게 MAJUNG 연구를 설명할 때 필요한 질문과 최소 연구구조를 정리한다.
이 문서는 MAJUNG의 효능을 주장하는 문서가 아니다. 현재 근거의 한계를 유지하면서 어떤 질문을 실제 임상연구로 검증해야 하는지를 정의한다.

## 2. 문헌에서 얻은 가장 중요한 연구 설계 원칙
### 원칙 A — '잠을 잘 자는가' 하나로 끝내지 않는다
현재 문헌에서는 sleep duration, quiet sleep, active sleep, crying, movement, physiological response가 서로 다른 결과를 보인다. 따라서 primary endpoint를 '수면 개선'이라는 단일 지표로 잡지 않는다.

### 원칙 B — 초기 상태를 반드시 기록한다
- crying/fussing
- awake/content
- drowsy
- quiet sleep
- active sleep
특히 자극이 초기 상태에 따라 서로 다른 방향의 반응을 보일 가능성이 있으므로, 상태는 핵심 effect modifier 후보로 취급한다.

### 원칙 C — caregiver intervention을 분리한다
feeding, diaper change, holding, rocking, pacifier, repositioning, swaddling 등은 모두 timestamp를 남긴다. 울음이 줄었다는 사실만으로 MAJUNG 효과라고 판정하지 않는다.

### 원칙 D — commanded vibration과 실제 전달 vibration을 분리한다
임상 데이터에서 device ON만 기록하지 않는다. 최종적으로 command → measured mattress-surface vibration → infant behavioral state → physiological response가 같은 시간축으로 연결되어야 한다.

### 원칙 E — vibration-only 효과와 복합중재를 분리한다
SNOO 등의 자료는 endpoint와 연구방법의 참고자료로 사용하되, MAJUNG vibration-only efficacy의 직접 근거로 사용하지 않는다.

## 3. 의료연구자와 검토할 핵심 RQ
### RQ-M01 — 단기 settling
MAJUNG의 사전 정의된 자극이 crying/fussing 상태의 건강한 만삭 영아에서 caregiver intervention 없이 settling까지 걸리는 시간 또는 fussing episode resolution probability를 변화시키는가?

### RQ-M02 — behavioral state
MAJUNG 자극이 quiet sleep, active sleep, drowsy, awake 상태의 분포 또는 상태 전이를 변화시키는가?

### RQ-M03 — physiological response
행동 변화가 관찰될 경우 HR, HRV, RR, SpO2, movement 등의 생리 지표에도 일관된 변화가 동반되는가?

### RQ-M04 — state × stimulation interaction
초기 crying/fussing, awake, drowsy, sleep 상태에 따라 동일 자극의 효과 방향 또는 크기가 달라지는가?

### RQ-M05 — exposure-response
실제 mattress-surface stimulation의 물리량과 행동/생리 반응 사이에 관계가 존재하는가?

### RQ-M06 — safety
자극 중 clinically meaningful abnormal physiological response, excessive acoustic exposure, mechanical/thermal exposure 또는 기타 adverse event가 증가하지 않는가?

## 4. 가장 합리적인 초기 연구 구조
### Phase 0 — engineering characterization
인체시험 전에 prototype의 실제 자극을 정의한다. 최소 기록: frequency spectrum, acceleration/displacement, spatial distribution, load/bedding dependence, acoustic output, temperature, ON/OFF timing, hardware/firmware version.

### Phase 1 — short-term human feasibility
목적은 '잠을 재우는지'를 입증하는 것이 아니라 반복 측정 가능한 단기 반응이 존재하는지 확인하는 것이다.
권장 구조: baseline → predefined stimulation → washout/off → repeated condition.
실제 자극 강도·노출시간·대상 연령·중단기준은 의료연구자와 IRB 검토를 거쳐 결정한다.

### Phase 2 — controlled efficacy study
Phase 1에서 재현 가능한 signal이 확인될 경우에만 진행한다.
가능한 비교: MAJUNG stimulation ON / sham-off / standard bassinet-care. 최종 비교군은 연구 질문과 IRB/의료적 현실성을 기준으로 결정한다.

### Phase 3 — longitudinal sleep study
Phase 2에서 단기 settling/state effect가 재현된 경우에만 검토한다.
주요 질문: sleep onset latency, total sleep time, longest uninterrupted sleep stretch, awakenings, quiet/active sleep distribution, resolved/unresolved fussing episodes.

## 5. 초기 연구의 primary endpoint 후보
가장 방어적인 후보는 caregiver intervention 없이 발생한 fussing/crying episode의 resolution 또는 predefined settling event까지의 time-to-event이다.
이유: MAJUNG의 즉각적인 작용 가설과 직접 연결되고, sleep duration보다 짧은 시간에 관찰 가능하며, intervention/censoring을 명시할 수 있고, 이후 sleep outcome과 별도로 분석할 수 있다.
최종 primary endpoint는 의료연구자가 population과 영상/행동 coding 체계를 검토한 후 확정한다.

## 6. behavioral measurement 원칙
가능하면 단순 audio-only 판단을 primary measure로 사용하지 않는다.
권장: time-locked video, blinded 또는 독립 coder, 사전 정의된 behavioral-state coding, inter-rater reliability 평가, caregiver intervention timestamp.
event sequence는 crying/fussing → drowsy → quiet sleep 또는 crying/fussing → caregiver intervention처럼 보존한다.

## 7. 최소 데이터 구조
한 연구의 모든 데이터는 공통 timeline을 사용한다.
| timestamp | device command | measured vibration | sound/environment | behavioral state | physiology | caregiver intervention |
|---|---|---|---|---|---|---|
분석 단위는 단순 평균값만 두지 않는다.
Event-level: fuss onset, cry onset, stimulation onset, settling, sleep onset, awakening, caregiver intervention.
Episode-level: episode duration, time-to-resolution, intervention-free resolution, repeated episode frequency.
Infant-level: total crying/fussing duration, total sleep duration, quiet/active sleep proportion, longest sleep stretch, physiological summary.

## 8. Bias / confounding control
반드시 기록할 변수: feeding timing, diaper status/change, holding, pacifier, swaddling, recent handling, room sound, room light, time of day, age/postnatal age, gestational age, sex, baseline state, medication/illness if clinical population.
특히 caregiver intervention은 주요 confounder이자 competing event로 취급한다.

## 9. 안전수면과 효능을 분리
AAP의 safe-sleep recommendations는 영아를 등을 대고, 다른 사람 없이, 단단하고 평평한 수면면에서 재우고, 느슨한 침구나 부드러운 물체를 제거하는 것을 기본으로 한다.
따라서 '아기가 더 오래 잔다'는 결과만으로 제품의 안전성을 의미하지 않는다.
효능: settling / behavioral state / sleep continuity.
안전: sleep surface / position / airway-related hazards / mechanical / acoustic / thermal / electrical / entrapment / strangulation.

## 10. 의료연구자에게 처음 전달할 때의 한 문장
"진동이 아기를 재운다고 가정하고 시험하려는 것이 아니라, 기존 연구에서 관찰된 영아의 기계적 자극 반응이 MAJUNG의 실제 물리 자극에서도 재현되는지, 그리고 그 반응이 초기 행동상태에 따라 어떻게 달라지는지를 먼저 검증하고 싶습니다."

## 11. 연구자에게 요청할 전문적 검토사항
1. 대상 population과 exclusion criteria
2. baseline/ON/OFF 또는 crossover 구조의 임상적 타당성
3. primary endpoint 및 behavioral coding definition
4. physiological monitoring의 필요 범위
5. stopping criteria
6. adverse-event definition
7. 영상·생체신호 데이터의 개인정보/보안 처리
8. IRB 제출 가능성
9. 필요한 표본수 산정 방식
10. sham/off comparator의 현실성

## 12. 현재 단계의 Go / No-Go
### GO
문헌상 검증할 가치가 있는 연구질문은 충분히 존재한다.
### NO-GO
현재 문헌만으로 'MAJUNG은 수면을 개선한다', 'MAJUNG vibration은 안전하다', '30–60 Hz가 적정하다', '10–21 µm가 안전/효능 기준이다', 'SNOO와 같은 효과를 낸다'고 주장하거나 시험목표로 확정하지 않는다.

## 13. 현재 연구 흐름
문헌 검토 FREEZE → 의료연구 질문 정의 → prototype physical-output definition → engineering characterization → medical researcher review → IRB/ethics feasibility → Phase 1 short-term human feasibility → Phase 2 controlled efficacy → Phase 3 longitudinal sleep

이 순서를 유지한다.

## 14. Endpoint 설계 추가 검토 — 2026-10-08

추가 문헌 검토 결과, 기존의 'time-to-settling' 후보는 유지하되 단독 primary endpoint로 고정하지 않는다.

### 근거

영아 sleep-state 연구에서는 행동상태 분류 자체의 scorer reliability가 중요한 문제이며, 엄격한 scoring guideline과 training을 통해 reliability가 개선된다는 선행근거가 있다. CHIME 연구에서는 trained scorers의 sleep-state inter-rater kappa가 0.68까지 개선됐다. citeturn0search0

또한 infant sleep에서 actigraphy는 PSG와 높은 sleep-detection agreement를 보였지만 wake specificity는 상대적으로 낮았다. 따라서 '잠들었는가'와 '깨어 있는가'를 하나의 센서로 완전히 대체한다고 가정하지 않는다. citeturn0search1

### endpoint hierarchy 수정

**Tier 1 — 가장 직접적인 단기 행동 endpoint**
- time-to-settling
- fussing/crying episode resolution
- caregiver-intervention-free resolution

**Tier 2 — 행동상태 endpoint**
- quiet sleep proportion
- active sleep proportion
- drowsy/awake transitions
- awakening frequency

**Tier 3 — 장기/연속 수면 endpoint**
- sleep onset latency
- total sleep time
- longest sleep stretch
- wake after sleep onset

**Tier 4 — 보조 생리 endpoint**
- HR / HRV
- RR
- SpO2
- movement

### 중요한 수정

'침착/진정'이라는 단일 score를 만들지 않는다.

또한 부모 설문이나 총 수면시간만으로 efficacy를 판정하지 않는다. 실제 연구에서는 객관적 관찰과 caregiver intervention을 함께 기록해야 한다. Videosomnography는 infant sleep-wake 및 parent-child interaction을 시간축으로 관찰하는 선행 방법이 있으며, 자동 videosomnography는 sleep timing에는 유용할 수 있지만 wake와 세부 행동상태 분류에는 한계가 보고됐다. citeturn0search3turn0search4

### Phase 1의 더 보수적인 성공 기준

Phase 1에서는 '수면 개선'을 성공 기준으로 두지 않는다.

1. predefined stimulation이 반복적으로 전달됨
2. behavioral event가 시간축에서 안정적으로 코딩됨
3. caregiver intervention과 stimulation을 구분할 수 있음
4. 동일 조건 반복에서 outcome의 방향성이 일관됨
5. 이상반응 또는 임상적으로 중요한 생리 변화가 없는지 평가 가능함

효과 크기 자체보다 **측정 가능성 + 반복 가능성 + 인과관계 해석 가능성**을 먼저 확인한다.

## 15. 의료연구자에게 전달할 연구 질문의 최종 형태

### Primary question
사전에 정의된 MAJUNG 물리 자극이 특정 초기 행동상태의 건강한 만삭 영아에서 caregiver intervention 없이 발생하는 settling 또는 fussing/crying episode resolution의 시간/확률을 변화시키는가?

### Secondary questions
1. 효과가 있다면 quiet sleep/active sleep 및 상태 전이에 어떤 변화가 나타나는가?
2. 효과는 초기 crying/fussing, awake, drowsy, sleep 상태에 따라 달라지는가?
3. 행동 변화가 HR/HRV/RR/SpO2/movement 변화와 동반되는가?
4. 실제 mattress-surface stimulation 물리량과 반응 사이에 exposure-response 관계가 있는가?
5. caregiver intervention 및 환경요인을 통제한 뒤에도 결과가 유지되는가?
6. 반복 사용에서 clinically meaningful adverse event가 증가하지 않는가?

## 16. 현재 단계의 결론

문헌 검토와 endpoint-methodology 검토를 합쳐도 MAJUNG efficacy claim을 뒷받침하는 단계는 아니다.

대신 의료연구자와 논의할 수 있는 **검증 가능한 연구질문과 측정 구조는 충분히 구체화됐다.**

다음 단계에서는 연구질문을 다시 넓히지 않고, 이 프레임을 기준으로 의료연구자 검토에 필요한 1~2 page research brief를 작성한다.
