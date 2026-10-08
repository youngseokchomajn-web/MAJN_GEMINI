# MAJUNG E-M001~E-M003 Engineering Test Protocol

작성일: 2026-10-08
상태: Prototype engineering validation protocol v1.0

## 1. 목적

E-M001~E-M003의 목적은 "모터가 작동한다"를 확인하는 것이 아니라, 향후 human research에서 사용할 MAJUNG stimulation envelope을 물리적으로 정의하고 재현성을 확인하는 것이다.

선행 neonatal vibrotactile 연구는 실제 mattress surface에서 진동을 측정했고, 30–60 Hz 대역의 displacement, spatial uniformity, acoustic output, load/bedding effect를 함께 확인했다. 한 연구에서는 mattress 신호를 200 Hz로 기록했다.

## 2. 시험 단계

### E-M001 — Basic output verification

질문:
현재 prototype이 mattress contact surface에서 측정 가능한 반복 진동을 만드는가?

최소 측정:
- accelerometer
- sampling rate ≥ 1 kHz 권장
- device command timestamp
- vibration waveform
- frequency spectrum
- RMS acceleration
- peak acceleration
- temperature
- acoustic level

판정:
- command ON/OFF에 따라 측정 신호가 명확히 구분되어야 한다.
- 동일 조건 반복에서 waveform/spectrum이 재현되어야 한다.
- 센서가 mattress가 아닌 frame/body vibration을 측정하고 있지 않은지 확인한다.

E-M001에서 인간을 사용하지 않는다.

## 3. E-M002 — Engineering characterization

### 3.1 측정 장비

우선순위:
1. MEMS accelerometer 또는 calibrated accelerometer
2. DAQ / high-speed ADC
3. contact microphone 또는 measurement microphone
4. 온도 센서
5. prototype controller logging
6. 기준 질량(load)
7. mattress/bedding assembly

가능하면 accelerometer의 sensitivity와 calibration certificate를 확보한다.

### 3.2 Sampling

진동:
- 권장 ≥1 kHz
- 가능하면 2 kHz 이상

선행 연구에서는 mattress vibration을 200 Hz로 기록했지만, MAJUNG의 실제 spectrum 및 고조파/과도응답까지 확인하려면 더 높은 sampling rate가 유리하다.

audio:
- ≥20 kHz 권장

temperature:
- 1 Hz 또는 그 이하로 충분

모든 채널은 공통 timestamp를 사용한다.

## 4. 센서 위치

최소 5개 위치:
- P1: actuator 중심 상부
- P2: 중심에서 longitudinal +25%
- P3: 중심에서 longitudinal -25%
- P4: lateral +25%
- P5: lateral -25%

가능하면 mattress 전체를 grid로 나눠 추가 측정한다.

핵심은 중앙에서 진동이 잘 나온다는 확인이 아니라 infant contact region 전체에서 얼마나 균일한지를 보는 것이다.

2009 연구에서도 mattress surface displacement를 직접 측정하고 ±2% 수준의 near-uniformity를 확인했다. 이는 MAJUNG의 목표값을 그대로 복사해야 한다는 뜻이 아니며, spatial uniformity를 정량화해야 한다는 선례로 사용한다.

## 5. Load 조건

최소 4조건:
- L0: 무부하
- L1: mattress + bedding only
- L2: mattress + representative infant-equivalent load
- L3: worst-case distributed load

L2/L3는 실제 human study에서 예상되는 체중 범위를 대표하도록 별도 정의한다.

선행 연구에서는 1–1.5 kg saline-filled bag과 bedding을 이용해 infant/bedding effect를 시험했다. MAJUNG에서는 이 값을 그대로 사용하지 않고 mattress geometry와 예상 사용 체중에 맞춰 load matrix를 별도로 만든다.

## 6. Bedding 조건

최소:
- B0 = mattress only
- B1 = normal bedding configuration
- B2 = thickest intended bedding
- B3 = intended-use worst case

목적:
bedding이 vibration transmission과 acoustic output을 변화시키는지 확인한다.

## 7. E-M002 측정 항목

| 항목 | 기록 |
|---|---|
| commanded state | ON/OFF |
| commanded level | controller value |
| actual acceleration | RMS / peak |
| frequency | dominant + spectrum |
| displacement estimate | 가능하면 RMS/peak |
| position | P1~P5/grid |
| load | L0~L3 |
| bedding | B0~B3 |
| acoustic level | dBA + spectrum 가능시 |
| temperature | mattress/actuator vicinity |
| duration | start/end |
| hardware revision | exact ID |
| firmware | exact version |

## 8. Displacement와 acceleration을 혼동하지 않는다

accelerometer로 직접 측정한 값은 acceleration이다.

displacement를 보고하려면 frequency-domain 관계를 이용해 별도로 계산하거나 displacement sensor를 사용해야 한다.

단일 sinusoid에 가까운 경우:
a(t) = -(2πf)^2 x(t)

따라서:
x_RMS = a_RMS / (2πf)^2

를 사용할 수 있지만, MAJUNG signal이 broadband/stochastic이면 전체 spectrum에서 frequency별 변환을 수행하는 것이 더 적절하다.

보고서에는:
- measured acceleration
- calculated displacement
- calculation method

를 구분한다.

## 9. Spatial uniformity 계산

각 위치 Pi에 대해 RMS magnitude를 계산한다.

예:
U_i = RMS_i / RMS_center

그리고:
- max/min ratio
- coefficient of variation
- center-to-edge difference

를 기록한다.

판정 기준은 초기에는 임의로 ±2% 이내로 고정하지 않는다.

2009 연구의 ±2%는 그 연구 장비의 engineering result이지 MAJUNG의 universal safety/efficacy threshold가 아니다.

MAJUNG의 acceptance criterion은 E-M002 pilot data를 확보한 뒤:
- intended-use region
- sensor uncertainty
- manufacturing variation
- load condition

을 고려하여 별도로 freeze한다.

## 10. Acoustic test

센서 위치:
- infant head position에 해당하는 위치
- mattress surface 위 bedding 상부

측정:
- dBA
- frequency spectrum 가능시
- ON/OFF difference
- load/bedding condition

선행 연구에서도 sound meter를 infant cranium 인접 위치에 두고 dB(A)를 측정했다.

중요:
motor vibration이 진동만 전달하는지 확인하지 않고, 소리라는 별도의 sensory exposure가 함께 발생하는지 확인한다.

## 11. Time stability

각 조건에서 최소:
- 10 s startup
- 60 s stable operation
- 10 s shutdown

가능하면 10 min continuous run까지 확장한다.

계산:
- startup transient
- steady-state RMS
- frequency drift
- amplitude drift
- thermal drift

human study에서는 transient와 steady-state를 구분할 수 있도록 한다.

## 12. E-M003 — Surrogate / worst-case validation

### Mechanical worst cases
- lowest expected load
- highest expected load
- off-center load
- edge load
- mattress compression
- bedding variation

### Electrical/control worst cases
- minimum output
- nominal output
- maximum intended output
- startup
- repeated ON/OFF
- long-duration operation

### Environmental
- room temperature range
- bedding configuration
- acoustic background

## 13. Test repeatability

각 핵심 조건은 최소 3회 반복한다.

반복 측정에서:
- RMS
- dominant frequency
- bandwidth
- spatial ratio
- acoustic level

의 mean / SD / CV를 기록한다.

3회 반복은 최종 제조공정 validation의 충분한 표본이 아니라 prototype characterization용 최소 반복이다.

## 14. Synchronization

모든 장비는 하나의 experiment ID와 timestamp를 공유한다.

최소 event:
- T0 = recording start
- T1 = command ON
- T2 = measured vibration onset
- T3 = stable vibration
- T4 = command OFF
- T5 = measured vibration decay/end

human research로 넘어갈 경우:
- T6 = crying/fussing onset
- T7 = settling
- T8 = caregiver intervention

까지 같은 timeline에 연결한다.

2017 neonatal study는 mattress output, physiological/environmental signals, video 및 caregiver interventions를 synchronized timestamp로 기록했다. MAJUNG에서도 이 구조를 기본 데이터 모델로 채택한다.

## 15. Human study용 endpoint와 연결

Engineering phase에서 아래 데이터를 확보해야 이후 human study에서 exposure variable을 만들 수 있다.

### Exposure
E = {frequency spectrum, acceleration, displacement estimate, position, load, duration}

### Behavioral outcome
- fuss/cry onset
- fuss/cry duration
- time-to-settling
- resolution without caregiver intervention
- behavioral state

### Sleep outcome
- sleep onset
- quiet sleep
- active sleep
- awake
- awakening
- longest sleep stretch

Infant sleep 연구에서는 infrared videosomnography를 이용해 sleep, drowsy, awake content, awake crying/fussing 등의 상태를 시간 단위로 코딩할 수 있었고, blinded trained coders의 reliability도 평가했다.

또 다른 방법론 연구에서는 video와 audio를 time-lock하여 crying과 다른 vocalization을 구별하는 것이 중요하다고 제안한다. 따라서 MAJUNG에서는 audio-only crying detection을 primary behavioral endpoint로 사용하지 않는다.

## 16. E-M001~E-M003의 통과 기준

### Gate E0 — Detectability
PASS:
- vibration ON/OFF가 measurement에서 명확히 구분됨.
FAIL:
- signal이 noise와 구분되지 않음.

### Gate E1 — Repeatability
PASS:
- 핵심 조건 반복 시 spectrum/RMS가 사전에 정한 tolerance 안에서 재현됨.
FAIL:
- 반복마다 output이 크게 변함.

### Gate E2 — Load characterization
PASS:
- load에 따른 변화량이 정량화됨.
FAIL:
- 실제 사용 체중 범위에서 output을 예측할 수 없음.

### Gate E3 — Spatial characterization
PASS:
- intended infant contact region의 spatial variation을 정량화함.
FAIL:
- 특정 위치에서만 자극이 집중됨.

### Gate E4 — Acoustic characterization
PASS:
- vibration과 acoustic output을 별도로 측정하고 exposure를 설명할 수 있음.
FAIL:
- vibration ON에서 발생하는 acoustic exposure를 설명할 수 없음.

### Gate E5 — Configuration freeze
PASS:
- hardware / mattress / firmware / stimulation parameters가 revision ID로 고정됨.
FAIL:
- human study 중 device configuration이 계속 변함.

## 17. E-M001~E-M003 이후의 다음 단계

### E-M004
MAJUNG Stimulation Envelope v1.0을 생성한다.

내용:
- frequency range
- acceleration range
- displacement estimate
- spatial distribution
- load dependence
- acoustic output
- startup/steady-state behavior
- allowable operating range
- measurement uncertainty

### H1
그 이후에야 human observational / within-subject study protocol을 작성한다.

H1의 기본 구조:
baseline → ON → OFF → ON/OFF 반복

실제 infant study의 cycle duration과 stopping rules는 의료연구자/IRB 검토 후 확정한다.

## 18. 중요한 제한

이 문서는 의료기기 안전기준이나 임상시험 승인 문서가 아니다.

특히 선행 연구의 30–60 Hz 또는 특정 displacement를 MAJUNG의 안전한 목표값으로 그대로 복사하지 않는다.

2009 연구의 stimulus intensity도 해당 연구에서 behavioral arousal threshold 이하로 선택된 값이며, 보편적인 infant safety threshold가 아니다.

MAJUNG의 human-use stimulation envelope은:
1. prototype measurement
2. engineering characterization
3. safety/risk assessment
4. medical researcher review
5. IRB/윤리 검토

순서로 별도 확정한다.

## 19. 최종 decision

현재 MAJUNG의 다음 행동은 인체 실험이 아니라 E-M001 → E-M002 → E-M003 실행 준비다.

특히 첫 번째로 확보해야 하는 것은:

"MAJUNG mattress의 실제 infant contact surface에서, 실제 load를 걸었을 때, 어떤 주파수와 진폭의 진동이 얼마나 균일하게 전달되는가?"

이다.

이 값이 확보되면 이후 human research에서 commanded vibration이 아니라 measured physical exposure를 독립변수로 사용할 수 있다.
