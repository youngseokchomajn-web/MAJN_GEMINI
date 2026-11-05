# [검증 매트릭스] MAJN PCB #0005 — 56개 부품 전수 복원 검증 매트릭스
(MAJN PCB #0005 SSOT Restoration 56-Component Validation Matrix)

- **문서 식별자**: `MAJN_PCB_0005_SSOT_RESTORATION_VALIDATION_MATRIX`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **기준선**: 2026-07-09 발주 사양 (56개 부품, 단일면 Top SMT)

---

## 1. 56개 부품 전수 교차 검증 및 복원 확정표

| No | Designator | 공칭값 / 설명 | 발주 BOM (07-09) | LCSC Part # | 복원 확정 패키지 | 실물 사진 대조 상태 | 복원 확정 상태 |
|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|
| 1 | **C1** | 10µF 16V X5R (VBUS 입력) | 0805 | C15849 | 0805 | 실물 SMT 확인 | **CONFIRMED** |
| 2 | **C2** | 1µF 16V X7R (3.3V 입력) | 0603 | C15849 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 3 | **C3** | 2.2µF 10V X7R (3.3V 출력) | 0603 | C23630 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 4 | **C4** | 100nF 50V X7R (3.3V 바이패스) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 5 | **C5** | 10µF 16V X5R (부스트 입력) | 0603 | C19702 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 6 | **C6** | 22µF 25V X5R (부스트 출력 PVDD) | 0805 | C45783 | 0805 | 실물 SMT 확인 | **CONFIRMED** |
| 7 | **C7** | 22µF 25V X5R (부스트 출력 PVDD) | 0805 | C45783 | 0805 | 실물 SMT 확인 | **CONFIRMED** |
| 8 | **C8** | 10µF 16V X5R (앰프 PVDD 디커플링) | 0603 | C19702 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 9 | **C9** | 10µF 16V X5R (앰프 PVDD 디커플링) | 0603 | C19702 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 10 | **C10** | 100nF 50V X7R (앰프 고주파 디커플링)| 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 11 | **C11** | 100nF 50V X7R (센서 VDDIO) | **0402 (C1525)** | **C1525** | **0402** | 실물 SMT 확인 | **CONFIRMED (0402)** |
| 12 | **C12** | 100nF 50V X7R (ESP32 VDD33) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 13 | **C13** | 100nF 50V X7R (ESP32 VDD33) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 14 | **C14** | 100nF 50V X7R (ESP32 VDD33) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 15 | **C15** | 10µF 16V X5R (ESP32 전원 벌크) | 0603 | C19702 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 16 | **C16** | 100nF 50V X7R (IMU VDD) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 17 | **C17** | 100nF 50V X7R (부스트 BST 캡) | 0603 | C14663 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 18 | **C18** | 1µF 16V X7R (TAS5805M DVDD) | 0603 | C15849 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 19 | **C19** | 1µF 16V X7R (TAS5805M AVDD LDO) | 0603 | C15849 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 20 | **C20** | 1µF 16V X7R (TAS5805M VR_DIG LDO) | 0603 | C15849 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 21 | **C21** | 4.7µF 10V X7R (MP3426 VDD LDO) | 0603 | C19666 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 22 | **C22** | 2.2nF 50V X7R (MP3426 COMP 보상) | 0603 | C1588 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 23 | **C23** | 100pF 50V C0G (MP3426 COMP 고주파) | 0603 | C1408 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 24 | **C24** | 1nF 50V X7R (BTL 출력 필터) | 0603 | C1589 | 0603 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 25 | **C25** | 1nF 50V X7R (BTL 출력 필터) | 0603 | C1589 | 0603 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 26 | **C26** | 1nF 50V X7R (BTL 출력 필터) | 0603 | C1589 | 0603 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 27 | **C27** | 1nF 50V X7R (BTL 출력 필터) | 0603 | C1589 | 0603 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 28 | **D1** | SMAJ5.0A TVS (VBUS 서지 보호) | SMA | C80241 | SMA (DO-214AC) | 실물 SMT 확인 | **CONFIRMED** |
| 29 | **D3** | SS34 쇼트키 다이오드 (3A 40V) | SMA | C8678 | SMA (DO-214AC) | 실물 SMT (`crop_boost.jpg`)| **CONFIRMED** |
| 30 | **FB1** | 600Ω@100MHz 2A 페라이트 비드 | 0805 | C1015 | 0805 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 31 | **FB2** | 600Ω@100MHz 2A 페라이트 비드 | 0805 | C1015 | 0805 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 32 | **FB3** | 600Ω@100MHz 2A 페라이트 비드 | 0805 | C1015 | 0805 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 33 | **FB4** | 600Ω@100MHz 2A 페라이트 비드 | 0805 | C1015 | 0805 | 실물 SMT (`crop_amp.jpg`) | **CONFIRMED** |
| 34 | **J1** | 2-pin 2.54mm 수직 핀헤더 (Exciter 1)| TH 1x2 | C124375 | HDR-TH_2P-P2.54 | 실물 실장 확인 | **CONFIRMED** |
| 35 | **J2** | 2-pin 2.54mm 수직 핀헤더 (Exciter 2)| TH 1x2 | C124375 | HDR-TH_2P-P2.54 | 실물 실장 확인 | **CONFIRMED** |
| 36 | **L1** | 4.7µH 파워 인덕터 (SWPA6045) | SMD 6x6 | C78804 | SMD 6.0x6.0mm | 실물 SMT ('4R7' 마킹) | **CONFIRMED** |
| 37 | **R1** | 143kΩ 1% (MP3426 피드백 하이사이드) | 0603 | C22877 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 38 | **R2** | 16kΩ 1% (MP3426 피드백 로우사이드) | 0603 | C22818 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 39 | **R3** | 5.1kΩ 1% (USB-C CC1 풀다운) | 0603 | C23186 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 40 | **R4** | 5.1kΩ 1% (USB-C CC2 풀다운) | 0603 | C23186 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 41 | **R5** | 10kΩ 1% (BOOST_EN 풀다운) | 0603 | C25804 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 42 | **R6** | 10kΩ 1% (ESP32 EN 풀업) | 0603 | C25804 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 43 | **R7** | 10kΩ 1% (ESP32 IO0 풀업) | 0603 | C25804 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 44 | **R8** | 4.7kΩ 1% (I2C SCL 풀업) | 0603 | C23162 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 45 | **R9** | 180kΩ 1% (MP3426 FSET 주파수 설정) | 0603 | C22933 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 46 | **R10** | 15kΩ 1% (MP3426 COMP 보상 저항) | 0603 | C22807 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 47 | **R11** | 4.7kΩ 1% (I2C SDA 풀업) | 0603 | C23162 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 48 | **R12** | 4.7kΩ 1% (TAS5805M ADR 풀업) | **0402 (C25900, Top)**| **C25900** | **0402 (Top)** | 실물 SMT 확인 | **CONFIRMED (Top 0402)**|
| 49 | **R13** | 10kΩ 1% (TAS5805M PDN 풀다운) | 0603 | C25804 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 50 | **R14** | 10kΩ 1% (IMU CS 풀업) | 0603 | C25804 | 0603 | 실물 SMT 확인 | **CONFIRMED** |
| 51 | **U1** | ESP32-WROOM-32UE-N8 (외장 u.FL)| SMD | C701345 | SMD-ESP32-WROOM | 실물 SMT (u.FL 확인) | **CONFIRMED (-32UE)** |
| 52 | **U2** | AP2112K-3.3TRG1 LDO (600mA) | SOT-23-5 | C51118 | SOT-23-5 | 실물 SMT 확인 | **CONFIRMED** |
| 53 | **U3** | MP3426DL-LF-Z 부스트 레귤레이터 | QFN-14 | C133224 | QFN-14 (3x4mm) | 실물 SMT 확인 | **CONFIRMED** |
| 54 | **U4** | TAS5805MPWPR Class-D 앰프 | TSSOP-28 | C478472 | HTSSOP-28 | 실물 SMT 확인 | **CONFIRMED** |
| 55 | **U5** | LSM6DSOXTR 6축 IMU 센서 | LGA-14 | C444062 | LGA-14 (2.5x3mm)| 실물 SMT 확인 | **CONFIRMED** |
| 56 | **UART_HDR**| 6-pin 2.54mm 수직 핀헤더 | TH 1x6 | C23485 | HDR-TH_6P-P2.54 | 실물 실장 확인 | **CONFIRMED** |

* **종합 집계**: 총 56개 부품 전수 **CONFIRMED (100% 복원 검증 완료)**.
