# 마중(Majn) 스마트 배시넷 향후 추진 계획 (Action Plan)

본 계획은 `진동논문` 폴더에 수집된 17편의 SOTA급 연구 논문, 안전 기준 가이드라인, 선행 특허(Cradlewise 등) 분석 결과를 바탕으로 수립되었습니다. 마중 배시넷의 핵심인 **비약물적 수면 유도(Beat Frequency Vibration) 기술의 상용화 및 안전성 입증**에 초점을 맞춥니다.

---

## Phase 1: 하드웨어 & 펌웨어 프로토타이핑 (Hardware & Firmware)
논문에서 검증된 30~65Hz 대역의 진동을 정밀하게 구현하기 위한 하드웨어 설계 단계입니다.

*   **VCA 기반 진동 제어**: Dayton Audio TT25-16(VCA)와 ESP32를 결합하여, 수면 진입 시간을 단축하는 30~65Hz의 맥동 주파수 진동(Beat Frequency Vibration) 회로를 구현합니다. (Reference: *The Effect of Beat Frequency Vibration...*)
*   **초정밀 폐루프(Closed-loop) 제어**: ADXL355 가속도 센서를 부착하여 영아의 미세 움직임과 매트리스의 진동 변위를 실시간으로 피드백 받아 진동의 세기를 자동 조절하는 PID 제어 펌웨어를 개발합니다.
*   **소음 기준(AAP) 차음 설계**: 진동 발생 시 구조물에서 발생하는 소음이 미국소아과학회(AAP) 권고 기준인 **50dBA**를 초과하지 않도록 흡음재 및 방진 댐퍼 구조를 설계합니다. (Reference: *Infant Sleep Machines and Hazardous Sound Pressure Levels*)

## Phase 2: Edge Actigraphy & Simple Audio Sensing (On-Device AI)
기존의 무거운 비전 AI(카메라)를 완전히 배제하고, 원가 절감 및 프라이버시 보호를 극대화하는 **임베디드 단독 구동(On-Device) 선제 감지 시스템**을 구축합니다.

*   **ADXL355 기반 Actigraphy (뒤척임 감지)**: 모터가 정지된 Sleep Mode 상태에서, 매트리스 하단에 장착된 초정밀 가속도 센서가 영아의 뒤척임(Thrashing)으로 인한 미세 변위를 측정합니다. 특정 임계치를 넘으면 '각성 징후'로 판단하여 카메라 없이도 선제적(Preemptive) 수면 유도 진동을 가동합니다.
*   **단순 오디오 트리거 연동**: 복잡한 딥러닝 울음 분석 대신, 단순 사운드 센서 모듈(데시벨 및 주파수 필터 기반)을 추가하여 아기가 완전히 깨서 울음소리를 낼 때 더 강한 진동 모드로 전환하는 로직을 결합합니다.
*   **독립형 State Machine 구축**: 외부 PC나 통신 연결 없이도 `수면(센서 감시) -> 뒤척임(약한 진동) -> 울음 터짐(강한 진동) -> 안정(진동 종료)` 사이클이 ESP32 내부에서 자체적으로 돌아가도록 펌웨어를 고도화합니다.

## Phase 3: 임상 및 안전성 검증 (Clinical & Safety)
의료 기기에 준하는 안전성 입증 및 B2B 판매를 위한 근거 마련 단계입니다.

*   **진동 안전성 입증 (반증 논리 방어)**: 기존 SNOO(스누) 침대의 '흔들림(Rocking)' 방식이 아닌 '수평면 미세 진동(Planar Vibration)' 방식을 사용함을 강조합니다. *Smith et al. (2015)* 논문을 근거로 미숙아에게도 안전한 진동임을 입증하는 자체 계측 보고서를 작성합니다.
*   **산후조리원 파일럿 테스트(IRB)**: 프로토타입 완성 후, 협력 산후조리원에서 영아의 수면 진입 시간(Sleep Latency) 단축 및 심박변이도(HRV) 안정화 효과를 측정하는 임상 프로토콜을 기획합니다.
*   **규제 기관 사전 평가**: KC 및 CE 완구 안전기준(부속서 6)에 따른 제품 유해성 및 기계적 안전성 사전 평가를 실시합니다.

## Phase 4: 특허 방어 및 사업화 (Patent & Business)
선행 기업과의 법적 마찰을 피하고 투자 유치를 가속화합니다.

*   **FTO(Freedom to Operate) 전략 완료**: Cradlewise의 특허(WO2021263199A2)를 분석한 결과, 경쟁사는 기계식 바운싱 방식에 의존하므로 우리의 VCA 기반 미세 진동 방식은 회피 설계가 완벽히 가능합니다. 이를 바탕으로 자체 방어 특허를 출원합니다.
*   **사업계획서(Pitch Deck) 고도화**: 현재 작성된 사업계획서 초안(`temp_biz_plan.txt`)에 본 리서치에서 확보한 SOTA 논문 데이터와 안전성 근거를 '경쟁 우위(Competitive Advantage)' 섹션으로 시각화하여 삽입합니다.

---
**Next Immediate Step:** 
Phase 2의 Actigraphy 로직이 `Majn_Vibe_Controller.ino` 펌웨어에 성공적으로 통합되었습니다. 다음 단계로 이 기술적 우위(프라이버시 보장, 저비용, 고정밀)를 사업계획서(`temp_biz_plan.txt`)에 반영하는 작업을 진행합니다.
