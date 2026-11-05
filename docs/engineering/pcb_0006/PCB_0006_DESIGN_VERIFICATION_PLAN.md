# [설계 검증 계획서] MAJN PCB #0006 — 설계 검증 계획 및 평가 매트릭스 (DVP)
(MAJN PCB #0006 Design Verification Plan & Evaluation Matrix)

- **문서 식별자**: `PCB_0006_DESIGN_VERIFICATION_PLAN`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **적용 대상**: PCB #0006 하드웨어 설계 검증

---

## 1. 개요 및 DVP 운영 원칙

본 설계 검증 계획서(DVP: Design Verification Plan)는 PCB #0006이 상용화 및 안전 인증에 필요한 모든 **전기적, 기능적, 환경적, 기구적 신뢰성 요구조건을 완벽히 만족하는지 검증하기 위한 총괄 시험 계획**이다.

---

## 2. 4대 시험 범주 및 DVP 매트릭스

| 시험 카테고리 | 시험 ID | 시험 항목 | 시험 조건 및 규격 | 판정 기준 (Acceptance Criteria) | 샘플 수 |
|:---|:---:|:---|:---|:---|:---:|
| **1. 전기적 시험<br>(Electrical)** | **DVP-EL-01** | 입력 전압 변동 및 VBUS 드롭 | $V_{\text{in}} = 4.5\text{V} \sim 5.25\text{V}$, 최대 부하 | 3.3V 레일 $\ge 3.20\text{V}$, Brownout 리셋 전무 | 3 EA |
| | **DVP-EL-02** | MP3426 승압 효율 및 리플 | $V_{\text{in}} = 5.0\text{V}, V_{\text{out}} = 12.0\text{V}$, $10\text{W}$ 부하 | 효율 $\ge 85\%$, 출력 리플 $\le 50\text{mV}_{\text{p-p}}$ | 3 EA |
| | **DVP-EL-03** | PVDD 오버슈트 및 팝 노이즈 | 기동 시 및 Shutdown 시 과도 파형 | PVDD 오버슈트 $\le 13.5\text{V}$, BTL 팝 서지 $\le 0.5\text{V}$ | 3 EA |
| | **DVP-EL-04** | 인덕터 L1 포화전류 마진 | $60^\circ\text{C}$ 챔버 환경, 피크 부하 구동 | 인덕턴스 저하 $\le 20\%$, 비정상 발진 전무 | 3 EA |
| **2. 기능 시험<br>(Functional)** | **DVP-FN-01** | BLE 통신 거리 및 패킷 수신율 | 개활지 10m 및 하우징 내부 밀폐 조건 | 패킷 손실률 $\le 0.1\%$, RSSI $\ge -75\text{dBm}$ | 3 EA |
| | **DVP-FN-02** | 4-익사이터 진동 균일성 | 4개 진동자 상면 가속도 동시 계측 | 4개 지점 가속도 편차 $\le \pm 10\%$ 이내 | 2 Set |
| | **DVP-FN-03** | 100ms 액티브 세이프티 가드 | I2C 통신 중단 및 Fault 발생 시 | $100\text{ms}$ 이내 하드웨어 MUTE 및 승압 차단 | 3 EA |
| | **DVP-FN-04** | 1.5g 비상 충격 즉시 정지 | 수직 충격 인가 (낙하/외력 충격) | $0.1\text{ms}$ 이내 안전 락(Safety Lock) 진입 | 3 EA |
| **3. 환경/신뢰성<br>(Reliability)** | **DVP-REL-01** | 30분 연속 운전 열 포화 시험 | 주변 온도 $25^\circ\text{C}$, 최대 정현파 연속 구동 | 부품 표면 온도 $\le 70^\circ\text{C}$, 하우징 외벽 $\le 40^\circ\text{C}$ | 3 EA |
| | **DVP-REL-02** | 전원 온/오프 급단속 (Power Cycling) | 5V 입력 1초 On / 1초 Off, 1,000회 반복 | 부품 파손 및 기동 실패 0건, 데이터 손상 없음 | 3 EA |
| | **DVP-REL-03** | 유도성 급정지 역기전력 내구 | 최대 진동 중 비상 정지 500회 연속 인가 | TAS5805M FET 손상 및 특성 열화 0건 | 3 EA |
| **4. 안전 규제<br>(Regulatory)** | **DVP-REG-01** | KC 전자파 적합성 (EMC 사전평가)| KN 301 489 복합기기 EMC 규격 | 방사 전자파(RE) 및 전도 전자파(CE) 마진 $\ge 6\text{dB}$ | 2 EA |
| | **DVP-REG-02** | 영유아 접촉면 온도 안전성 | 어린이제품안전특별법 기준 | 사용 중 유아 접촉 가능 표면 온도 $\le 43^\circ\text{C}$ | 2 Set |
| | **DVP-REG-03** | 진동 가속도 상한선 안전 검증 | 가속도 센서 매트리스 상면 계측 | 최대 가속도 피크 $\le 0.15\text{G}$ (안전 마진 준수) | 2 Set |
