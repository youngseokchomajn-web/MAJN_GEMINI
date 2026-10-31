# 마중 배시넷(MAJN Bassinet) 하드웨어/펌웨어 종합 엔지니어링 의사결정 로그 (Comprehensive Decision Log)

> **문서 상태**: 공식 승인 (SSOT)  
> **최신 개정일**: 2026년 10월 31일  
> **적용 대상**: PCB Rev-C (Rel 5), ESP32 펌웨어, 목공 케이스(4.5T), 하네스 및 센서 연동  
> **검증 스크립트**: `/Users/youngseok/Desktop/majn/tools/verify_hardware_review.py` (21/21 100% PASS, v2.4 Deep Electrical & Mechanical Clearance)

---

## 1. 개요 및 설계 철학
본 문서는 마중 배시넷의 프로토타입(#0005 보드) 제작 및 실기 테스트 과정에서 도출된 결함 분석, 하드웨어 회로 수정, 부품 교체, 무선 통신 최적화, 전원 관리 및 와이어 하네스 공정에 이르는 **모든 대소 엔지니어링 의사결정과 사소한 세부 주의사항까지 누락 없이 영구 기록(SSOT)**하기 위해 작성되었습니다.

---

## 2. 세부 의사결정 로그 (Chronological & Category Decision Log)

### [결정 01] 부스트 컨버터(MP3426) D3 및 L1 원본 설계 오류 규명 및 정상화
- **발견된 문제**:
  - 원본 `.epro2` 역공학 분석 결과, D3 위치에 3.9kΩ 저항(`0603WAF3901T5E`), L1 위치에 5.6kΩ 저항(`0603WAF5601T5E`)이 배치되어 있었음.
  - 이로 인해 승압(Boost) 스위칭 루프가 형성되지 않고 12V PVDD 공급이 불가한 치명적 결함 존재.
- **의사결정**:
  - D3: 40V 3A 쇼트키 다이오드(`SS34`, SMC 패키지, LCSC: `C14999`)로 정상화.
  - L1: 4.7µH 3.5A 차폐형 파워 인덕터(`CD54-4R7M`, LCSC: `C408333`)로 정상화.
  - 스위칭 노드 고주파 링잉 감쇄를 위해 RC 스너버(`C_SNUB` 1nF 50V X7R + `R_SNUB` 2.2Ω) 직렬 배치.

### [결정 02] ESP32 물리 패드(Physical Pad) vs 공식 GPIO 1:1 정밀 매핑 정정
- **발견된 문제**:
  - 이전 설계 회로도에서 ESP32 모듈의 핀 번호(Pin 1~38)와 내부 마이크로컨트롤러의 GPIO 번호가 혼용되어, 잘못된 핀 결선 위험 발생.
- **의사결정 및 확정 매핑**:
  - **Pad 4 (SENSOR_VP)**: 공식 `GPIO36` (ADC1_CH0, 입력 전용) $\rightarrow$ 외장 BCG 포트 차동 P(`NET_BCG_MCU_P`) 매핑.
  - **Pad 5 (SENSOR_VN)**: 공식 `GPIO39` (ADC1_CH3, 입력 전용) $\rightarrow$ 외장 BCG 포트 차동 N(`NET_BCG_MCU_N`) 매핑.
  - **Pad 6 (VDET_1)**: 공식 `GPIO34` (입력 전용) $\rightarrow$ LSM6DSOX IMU 인터럽트(`SENSOR_INT1`) 매핑.
  - **Pad 7 (VDET_2)**: 공식 `GPIO35` (입력 전용) $\rightarrow$ INMP441 디지털 마이크 DIN(`NET_MIC_MCU_DIN`) 매핑.
  - **Pad 10 (DAC_1)**: 공식 `GPIO25` $\rightarrow$ TAS5805M 및 마이크 I2S Word Select(`I2S_LRCLK`) 공통 매핑.
  - **Pad 11 (DAC_2)**: 공식 `GPIO26` $\rightarrow$ TAS5805M 및 마이크 I2S Bit Clock(`I2S_BCLK`) 공통 매핑.
  - **Pad 12 (IO27)**: 공식 `GPIO27` $\rightarrow$ TAS5805M 앰프 제어 I2C SCL(`AMP_I2C_SCL`) 매핑.
  - **Pad 14 (MTDI / GPIO12)**: **부팅 스트래핑 핀(VDD_SDIO 전압 결정)**이므로, 외부 회로 연결 시 부팅 불능 위험이 있어 **완전 미연결(NC) 격리**.
  - **Pad 27 (IO16)**: 공식 `GPIO16` $\rightarrow$ 레이더 UART2 RX(`NET_RADAR_MCU_RX`) 매핑.
  - **Pad 28 (IO17)**: 공식 `GPIO17` $\rightarrow$ 레이더 UART2 TX(`NET_RADAR_MCU_TX`) 매핑.
  - **Pad 33 (IO21)**: 공식 `GPIO21` $\rightarrow$ TAS5805M 앰프 제어 I2C SDA(`AMP_I2C_SDA`) 매핑.

### [결정 03] USB Type-C 포트 표준 풀다운(Rd) 및 B5 패드 결선 정정
- **발견된 문제**:
  - 원본 회로에서 CC 라인에 14kΩ 비표준 저항이 장착되어 있었고, CC2 패드가 B8(SBU2)로 오결선되어 C-to-C PD 충전기 연결 시 5V 인식이 완전히 실패하는 결함 존재.
- **의사결정**:
  - USB Type-C 스펙 준수를 위해 CC1(`A5`) 및 CC2(`B5`)에 각각 정밀 5.1kΩ (1%) 풀다운 저항(`R3`, `R4`, LCSC: `C23186`) 실장.
  - B8(SBU2) 패드는 미연결(NC)로 분리 완료. 일반 C-to-C 및 C-to-A 보조배터리 전원 정상 공급 확보.

### [결정 04] INMP441 디지털 I2S 마이크 인터페이스 7-Pin 확장
- **발견된 문제**:
  - 기존 6-Pin 환경에서는 환경 센서(SDA, SCL)와 마이크 공유 시 I2S의 필수 3대 신호(BCLK, WS, DIN) 중 BCLK가 외부 커넥터로 전달되지 못하는 치명적 누락 존재.
- **의사결정**:
  - `J_ENV_MIC` 커넥터를 JST-SH 7-Pin(`SM07B-SRSS-TB`, LCSC: `C160407`)으로 전면 확장.
  - 핀맵: 1: 3.3V, 2: GND, 3: SDA, 4: SCL, 5: `I2S_BCLK`, 6: `I2S_WS`, 7: `MIC_DIN`.
  - DIN 라인에는 0Ω 격리 저항(`R_L8`)을 배치하여 신호 간섭 차단.

### [결정 05] 탄성파/심탄도(BCG) 초고임피던스 PVDF 센서 AFE 모듈 분리
- **발견된 문제**:
  - PVDF 압전 필름은 기가옴($G\Omega$) 단위의 초고출력 임피던스를 가지므로, ESP32의 내장 ADC(메가옴 미만 입력 임피던스)에 직결할 경우 극심한 로딩 효과와 전하 누설로 인해 심박/호흡 미세 신호가 완전히 소실됨.
- **의사결정**:
  - 메인 PCB의 `J_BCG` 포트를 "외장 차지앰프(Charge Amp) / 초고입력임피던스 JFET 버퍼 AFE 모듈용 인터페이스"로 명확히 재정의.
  - 0Ω 링크(`R_L1`, `R_L2`)를 통해 외장 AFE에서 증폭/필터링된 아날로그 전압(0~3.3V 저임피던스 신호)을 수신하도록 구조화.

### [결정 06] Wi-Fi 신호 감쇄 해결: ESP32-WROOM-32UE (외장 IPEX 안테나) 전환
- **발견된 문제**:
  - 자작합판 하우징 내부 밀폐 및 주변 금속/배선으로 인해 내장 PCB 패턴 안테나의 전파 방사 효율 저하 및 Wi-Fi/BLE 통신 거리 단축 현상 발생.
- **의사결정**:
  - 메인 MCU 모듈을 `ESP32-WROOM-32E-N8`(내장 안테나)에서 **`ESP32-WROOM-32UE-N8`**(IPEX 커넥터 장착형, LCSC: `C701343`)로 전격 교체.
  - **하드웨어 호환성**: 외형 핀 배열, 랜드 패턴(Footprint) 100% 동일하여 PCB 기판 재설계 비용 0원.
  - **펌웨어 호환성**: 내부 RF 실리콘 및 레지스터 100% 동일하여 펌웨어 소스 코드 수정 0줄.
  - **안테나 부품**: 2.4GHz 3dBi 플렉시블 FPC 안테나(케이블 길이 10~15cm, IPEX MHF1 단자) 채택. 목공 케이스 상판 내부 최적 위치에 점착 고정.
  - **공정 주의사항**: 배시넷 진동에 의해 IPEX 마이크로 동축 커넥터가 이탈되는 것을 원천 방지하기 위해 **RTV 비도전성 전자용 실리콘 본드 마감** 공정 필수 반영.

### [결정 07] 일반 보조배터리 자동 꺼짐(Auto-Shutoff) 방지 대책
- **발견된 문제**:
  - 일반 보조배터리는 연결된 기기의 소비 전류가 약 50~70mA 이하로 떨어지면 완충 상태로 오인하여 15~30초 내에 5V 출력을 자동으로 차단(Sleep)함.
  - ESP32 단독 대기 상태(15~30mA) 시 배터리가 스스로 꺼지는 현상 발생.
- **의사결정**:
  - **펌웨어 솔루션 (하드웨어 수정 불필요)**: ESP32 Wi-Fi Tx Power를 19.5dBm 상시 모드로 유지하고 100ms 간격 비콘/하트비트를 활성화하여 상시 대기 전류를 75~85mA 수준으로 유지.
  - **백업 옵션**: 초저전력 슬립이 필요한 경우, GPIO 제어 트랜지스터로 10초마다 100mA 펄스를 100ms 동안 인가하는 활성화 더미 로드 회로 추가 검토.

### [결정 08] 센서 포트 확장 및 동시 사용 시 신호 간섭 방지 (I2C 하드웨어 풀업 실장)
- **발견된 문제**:
  - 미래 확장을 위한 포트(BCG, Radar, Env/Mic)에 외장 케이블(20~30cm)을 연결할 경우, 케이블의 기생 커패시턴스로 인해 ESP32 내부 약한 풀업(약 45kΩ)만으로는 I2C 신호의 상승 시간(Rise Time)이 지연되어 통신 에러 발생 위험.
- **의사결정**:
  - `AMP_I2C_SCL` 및 `AMP_I2C_SDA` 버스 라인에 3.3V 기준 **4.7kΩ 하드웨어 정밀 풀업 저항(`R_PU1`, `R_PU2`, 0603, LCSC: `C23179`) 2개 실장 추가**.
  - 각 포트별 전원 분리: Radar는 5V(고소비전력), BCG 및 Env/Mic는 SGM2036 3.3V LDO 저잡음 레일 공급으로 전원 노이즈 상호 간섭 차단.
  - 신호선 완전 격리를 위한 0Ω 점퍼 저항(`R_L1` ~ `R_L8`) 8개소 유지.

### [결정 09] 햅틱 익사이터(HDHX14C02-8) 실물 구조 및 하네스 제작 공정 확정
- **실물 사양 분석 (사진 확인)**:
  - 모델: `HDHX14C02-8` (14mm 보이스코일, 8Ω 임피던스).
  - 단자 구조: 별도 커넥터 없이 상하단에 각각 납땜용 솔더 패드(`+` 표시 및 은색 패드) 노출.
  - 메커니즘: 중앙 보이스코일 유닛 주변으로 지그재그(Wavy) 판스프링 서스펜션 암 일체형 구조.
- **의사결정**:
  - **납땜 및 절연 공정**: 익사이터 단자에 24AWG 다심 실리콘 연선(내열 내진동)을 직접 납땜 후, 납땜 부위를 열수축 튜브(Heat Shrink Tube) 및 실리콘으로 완전 절연 몰딩 처리.
  - **하네스 케이블 길이**: 메인 기판 장착 위치로부터 진동판 중앙 4개소까지의 거리를 고려하여 **길이 25cm ± 2cm** 규격 하네스 제작.
  - **기판 결합 커넥터**: 기판의 J1/J2 단자대에 원터치 체결 가능한 JST 2P 압착 커넥터 적용.
  - **조립 고정**: 진동판(상판 내측)에는 3M VHB(4910 또는 5952) 고접착 탄성 폼 테이프로 압착 고정하여 진동 전달률 극대화 및 나사 풀림 소음 방지.

### [결정 10] 스마트배시넷 목공 하우징(케이스) 최신본 기준 사양 확정
- **소재 및 가공처**: 홍대 해광레이저, **4.5T 자작나무 합판(Birch Plywood)** 레이저 커팅.
- **조립 완품 외경**: **450.0 × 250.0 × 22.5 mm** (4코너 R20 라운딩 마감).
- **스택업 구조**:
  - 상판(4.5T): 나사홀 없는 매끈한 상부면, 내측면에 익사이터 4구 레이저 마킹 INFO 레이어 적용.
  - 중간 캐비티(13.5mm): 4.5T 측판 3장 적층, TEAX14C02/HDHX14C02 수용 후 약 3.4mm 공기 틈새 확보, ⌀5.5mm 배선 통과홀 구비.
  - 코너 블록: 20×20mm 부채꼴 R20 조각 3장 적층(기둥 4개 형성).
  - 하판(4.5T): M3 접시머리 카운터싱크 나사홀 6개소.
- **최신 도면 SSOT**: `/Users/youngseok/Desktop/majn/majn_housing/majung_bassinet_order_4.5T_haptic.dxf`

### [결정 11] 현 시제품 보드(PCB #0005) 하드웨어 제약 및 펌웨어 배포 원칙 (절대 준수)
- **물리 버튼 전무**: PCB #0005 보드에는 BOOT, EN 버튼이 일체 없음.
- **시리얼 플래시 불가**: CP2102 헤더에 DTR/RTS 리셋 회로가 없으므로 유선 `esptool` 다운로드 불가.
- **배포 방식**: 오직 **무선 OTA (BLE GATT OTA 또는 Wi-Fi HTTP `/update`)**로만 펌웨어 업로드 실행.

### [결정 12] MP3426 12V 승압 피드백 분배 저항 스왑 (R1 ↔ R2 정상화)
- **발견된 문제**:
  - 기존 설계에서 PVDD_12V ↔ BOOST_FB에 연결된 R1이 16kΩ, BOOST_FB ↔ GND에 연결된 R2가 150kΩ으로 역전 실장되어 승압 출력 전압이 $V_{OUT} = 1.2\text{V} \times (1 + 16/150) = 1.33\text{V}$로 심각하게 저하되는 결함 존재.
- **의사결정**:
  - `R1`(High-Side)을 **150kΩ (`0603WAF1503T5E`, LCSC: `C22807`)**, `R2`(Low-Side)를 **16kΩ (`0603WAF1602T5E`, LCSC: `C22818`)**으로 전격 교체.
  - 출력 전압: $V_{OUT} = 1.20\text{V} \times (1 + 150\text{k}\Omega / 16\text{k}\Omega) = \mathbf{12.45\text{V}}$로 정상화 완료 (TAS5805M 정격 12V 완벽 충족).

### [결정 13] PVDD_12V 라인 디커플링 MLCC 내압 25V 상향 (C8, C9 교체)
- **발견된 문제**:
  - 기존 C8, C9에 배치된 `CL10A106KP8NNNC`(`C19702`)는 10V 정격('P' 코드) 부품으로, 12V 전원 라인 인가 시 유전체 파괴(Dielectric Breakdown) 및 발열/쇼트 위험 상존.
- **의사결정**:
  - C8, C9을 **25V 정격 10µF 0805 X5R MLCC (`CL21A106KAYNNNE`, LCSC: `C96919`)**로 즉시 교체하여 2배 이상의 절연 내압 안전 마진 확보.

### [결정 14] U3(MP3426) & U4(TAS5805M) 보조 핀 결선 완료 및 1-Pin Dead Net 전면 제거
- **발견된 문제**:
  - Netlist 상에 U3.7(VDD), U3.14(FSET), U3.1(COMP), U4.13(AVDD), U4.4(VR_DIG) 5개 핀이 단독 1-pin 상태로 방치되어 칩 기동 불능 위험 존재.
- **의사결정 및 완비 회로**:
  - **U3.7 (`BOOST_VDD`)**: 1µF 16V 바이패스 커패시터(`C_BVDD`, LCSC: `C15849`)를 GND에 결선.
  - **U3.14 (`BOOST_FSET`)**: 600kHz 스위칭 주파수 설정용 100kΩ 저항(`R_FSET`, LCSC: `C25804`)을 GND에 결선.
  - **U3.1 (`BOOST_COMP`)**: 피드백 루프 안정성 보상을 위해 10kΩ 저항(`R_COMP`, LCSC: `C25803`)과 2.2nF 50V 커패시터(`C_COMP`, LCSC: `C14668`) 직렬 네트워크(`NET_COMP_MID`)를 GND에 결선.
  - **U4.13 (`AVDD`)**: 1µF 아날로그 디커플링 커패시터(`C_AVDD`, LCSC: `C15849`)를 GND에 결선.
  - **U4.4 (`VR_DIG`)**: 1µF 디지털 코어 디커플링 커패시터(`C_VRDIG`, LCSC: `C15849`)를 GND에 결선.
  - 결과: 설계 전체에서 **1-Pin Dead Net 개수 = 0건 완비**. (U4 Pin 3/Pin 9 결선 상세는 [결정 21] 참조).

### [결정 15] 3.3V LDO 용량 1A급 상향 (U2: SGM2036 300mA → TLV75733 1A 교체)
- **발견된 문제**:
  - 기존 실장된 SGM2036-3.3(300mA, UTDFN-4L)은 ESP32의 Wi-Fi 19.5dBm 송신 시 발생하는 순간 피크 전류(350~490mA)를 감당하지 못해 브라운아웃(Brownout) 전압 강하 및 MCU 리셋을 초래할 치명적 위험 존재.
- **의사결정**:
  - TI 사의 저잡음 고신뢰 1A LDO인 **`TLV75733PDBVR` (SOT-23-5, LCSC: `C444158`)**로 전격 교체.
  - 핀맵: 1(IN, VBUS_5V), 2(GND), 3(EN, VBUS_5V), 4(NC), 5(OUT, VCC_3V3). 상시 통신 및 송신 피크 시에도 안정적인 3.3V 정전압 공급 보장.

### [결정 16] ESP32 Power-On Reset(POR) RC 시상수 100배 확대 (R5=10kΩ, C17=1µF)
- **발견된 문제**:
  - 물리 리셋 버튼이 일체 없는 배시넷 보드 특성 상, 기존 R5(1kΩ), C17(100nF)의 매우 짧은 시상수($\tau = 0.1\text{ms}$)로 인해 전원 투입 시 LDO 슬루율 지연에 따른 부팅 실패 및 래치업 위험 존재.
- **의사결정**:
  - `R5`를 10kΩ(`0603WAF1002T5E`, LCSC: `C25803`), `C17`을 1µF(`CL10A105KB8NNNC`, LCSC: `C15849`)로 교체하여 시상수를 $\tau = 10\text{k}\Omega \times 1\mu\text{F} = \mathbf{10.0\text{ms}}$로 100배 확대. Espressif 공식 권고(>1ms)를 완벽 충족하여 무버튼 완전 자동 Power-On Reset 신뢰성 확보.

### [결정 17] 레거시 유령 부품(TYPE_C, D2, SOP16) 전면 제거 및 USB 입력 커패시터(C1, C2) 정상화
- **발견된 문제**:
  - 초기 프로토타입 잔재인 DIP-20 MCU 패드(`D2`), 미결선 USB-UART(`SOP16` CH340C), 중복 리셉터클(`TYPE_C`)이 BOM과 Netlist에 남아 있었으며, C1(10µF)과 C2(100nF)가 고립된 `NET_VBUS`에 연결되어 보드 메인 5V 전원 레일에 실질적으로 기여하지 못함.
- **의사결정**:
  - 레거시 유령 부품 3종(`D2`, `SOP16`, `TYPE_C`)을 BOM과 Netlist에서 완전 영구 제적.
  - `C1`(10µF)과 `C2`(100nF)를 실제 전원 버스인 `VBUS_5V`에 직결하여 5V 입력단 서지 억제 및 벌크 디커플링 정상화.

### [결정 18] I2S 클럭 댐핑(R_BCLK) 및 스피커 BTL 출력 EMI 필터링(C_SPK1~4) 추가
- **발견된 문제**:
  - 고속 오디오 비트클럭(I2S_BCLK) 분기 배선 시 발생하는 임피던스 불일치 및 링잉 노이즈 위험.
  - TAS5805M Class-D 앰프의 고주파 스위칭 PWM 노이즈가 스피커 케이블(하네스)을 안테나 삼아 방사되어 전자파 인증(KC/FCC Class B)에 불합격할 위험.
- **의사결정**:
  - ESP32 Pad 11(DAC_2) 출력단에 **33Ω 직렬 댐핑 저항(`R_BCLK`, 0603, LCSC: `C23138`)**을 삽입하여 `NET_I2S_BCLK_MCU` $\rightarrow$ `I2S_BCLK` 구동.
  - 스피커 커넥터 출력 4개 라인(`NET_SPK_A+`, `NET_SPK_A-`, `NET_SPK_B+`, `NET_SPK_B-`)에 각각 **1nF 50V 고주파 바이패스 커패시터(`C_SPK1` ~ `C_SPK4`, 0603 X7R, LCSC: `C14666`)**를 GND로 결선하여 전자파 노이즈 감쇄 대책 완비.

### [결정 19] UART_HDR 6핀 헤더 동기화로 RXD/TXD 데드넷 해소
- **발견된 문제**:
  - BOM 상에 `UART_HDR`이 2핀(`B-2100S02P-A110`)으로 오기되어 있어, 실물 보드의 6핀 커넥터 규격과 불일치하고 U1.34(`ESP_RXD`), U1.35(`ESP_TXD`)가 Netlist에서 1-pin 상태로 고립됨.
- **의사결정**:
  - `UART_HDR`을 실물 표준 규격인 2.54mm 6핀 헤더(`B-2100S06P-A110`, LCSC: `C124380`)로 정정.
  - 핀맵: 1(3.3V), 2(EN), 3(IO0), 4(TXD0), 5(RXD0), 6(GND) 완비로 1-pin 데드넷 원천 박멸.

### [결정 20] BOM.csv RFC 4180 표준 콤마 이스케이프 및 verify_hardware_review.py v2.3 심층 검증 강화
- **발견된 문제**:
  - `BOM.csv`의 마지막 열('Category / Circuit Role')에 포함된 괄호 내 콤마(예: `R1`, `R5`, `R_L1~8`, `R_PU1~2`)가 따옴표로 감싸지지 않아, 표준 CSV 파서(Python csv.reader, Excel, LCSC/JLCPCB 발주기) 파싱 시 11번째 열로 쪼개지는 구문 오류 존재.
  - 기존 `verify_hardware_review.py`가 단순 `csv.DictReader`를 사용하여 열 개수 불일치를 걸러내지 못하고 은폐하였으며, 보조 핀의 GND 리턴 및 루프 보상(R_COMP-C_COMP) 직렬 네트워크를 피상적으로만(`len >= 2`) 검증함.
- **의사결정**:
  - `BOM.csv`의 모든 콤마 포함 필드를 큰따옴표(`"..."`)로 감싸 RFC 4180 표준을 100% 준수하도록 정제.
  - `verify_hardware_review.py`를 v2.3으로 개정하여 BOM 열 개수 전수 검사, MP3426 루프 보상 RC 직렬 네트워크(`U3.1` $\rightarrow$ `R_COMP` $\rightarrow$ `NET_COMP_MID` $\rightarrow$ `C_COMP` $\rightarrow$ `GND`), 보조 핀 디커플링 MLCC의 GND 리턴 및 용량/저항값 검증, ESP32 EN RC 시상수 결선 무결성 검증을 전면 통합.

### [결정 21] TAS5805M(U4) SDOUT(Pin 9) NC 격리 및 ADR(Pin 3) 풀다운 저항(R_ADR) 정합화
- **발견된 문제**:
  - 초기 수정본에서 U4 Pin 9(`SDOUT`)가 `GND`에 직결되어 있었음. `SDOUT`은 I2S CMOS 직렬 오디오 데이터 출력 핀이므로 접지 단락 시 내부 드라이버 과전류 소손 치명적 결함 유발 (`pinmap_master.md` 기준 미연결 NC 필수).
  - U4 Pin 3(`ADR/FAULT#`)이 `GND`에 0Ω 직결되어 있었음. Pin 3은 부팅 시 I2C 주소 래치 후 동작 중 Fault 알림 오픈드레인/출력으로 전환되므로 단락 전류 위험 존재. 또한 펌웨어 주소(`0x2C`)와의 7-bit/8-bit 표기 혼선 존재.
- **의사결정**:
  - `U4.9`를 `NET "GND"`에서 완전히 제거하여 **안전한 미연결(NC, Floating)** 상태로 격리.
  - `U4.3`은 10kΩ 풀다운 저항 **`R_ADR` (`0603WAF1002T5E`, LCSC: `C25803`)**을 거쳐 GND에 연결하도록 신규 네트 `AMP_ADR` 신설.
  - I2C 주소를 펌웨어(`Majn_Vibe_Controller.ino`)의 `0x2C`와 일치하도록 **7-bit `0x2C` (8-bit `0x58`)**로 공식 정렬.

### [결정 22] 부팅 시퀀스 안전 스트래핑 저항 3종(R_BEN, R_PDN, R_CS) 하드웨어 결선
- **발견된 문제**:
  - ESP32 부팅 직후 GPIO 핀들이 High-Z 상태일 때, ① `BOOST_EN` 플로팅에 의한 12V 급격한 기동 및 돌입전류 셧다운, ② `AMP_PDN` 팝 노이즈 및 GPIO15 부트스트랩 위반 위험, ③ `SPI_CS` 핀 노이즈로 `LSM6DSOX` IMU의 I2C 모드 오진입 위험 상존 (`MAJN_펌웨어요구사항_HW-FW계약_2026-07-03.md` 필수 안전 사양).
- **의사결정**:
  - **`R_BEN` (100kΩ, LCSC: `C25804`, 0603)**: `BOOST_EN` ↔ `GND` 풀다운 결선. ESP32 기동 전 12V 승압 레귤레이터 기본 OFF 강제 보장.
  - **`R_PDN` (10kΩ, LCSC: `C25803`, 0603)**: `VCC_3V3` ↔ `AMP_PDN` 풀업 결선. GPIO15 부팅 스트래핑 사양(High)을 충족하고 앰프 초기 팝 노이즈 억제.
  - **`R_CS` (10kΩ, LCSC: `C25803`, 0603)**: `VCC_3V3` ↔ `SPI_CS` 풀업 결선. IMU CS 라인을 High로 고정하여 SPI 통신 모드 고정 보장.

### [결정 23] D1 5V TVS 다이오드 복구, C_BULK 저배형 MLCC 추가 및 13.5mm 목공 캐비티 간섭 해소
- **발견된 문제**:
  - 목공 하우징(4.5T 자작합판) 내부 캐비티 높이는 **13.5mm**인데, `D1`에 높이 12.0mm의 스루홀 전해커패시터(`插件 D6.3xL12mm`, Jianghai `C106568`)가 등록되어 PCB(1.6mm) 및 리드 납땜부 포함 시 약 15.1mm로 케이스 조립 불가 간섭 발생.
  - 또한 `D1`은 원래 KC/FCC 전자파 및 서지 보호를 위한 5V TVS 다이오드 위치였음.
- **의사결정**:
  - `D1`을 원래 목적인 SMD 5V 단방향 TVS 다이오드 **`SMAJ5.0A` (MDD, LCSC: `C15929`, Footprint: `SMA(DO-214AC)`, 높이 2.2mm)**로 원상 복구 (`D1.1`=`VBUS_5V`, `D1.2`=`GND`).
  - 5V 레일 벌크 디커플링 용량 보강을 위해 초저배형 SMD MLCC **`C_BULK` (22µF 25V, YAGEO `CC0805MKX5R8BB226`, LCSC: `C784585`, Footprint: `0805`, 높이 1.25mm)**를 추가 결선 (`C_BULK.1`=`VBUS_5V`, `C_BULK.2`=`GND`).
  - 13.5mm 캐비티 내에 최대 2.2mm 이내로 모든 부품을 완전 수용하여 기구 간섭 100% 해소.

### [결정 24] J1/J2 2핀 스피커 커넥터 품번 정정 및 F1 PPTC 3.0A 상향 (45°C 열 디레이팅 대응)
- **발견된 문제**:
  - `J1`, `J2` 2핀 스피커 단자가 BOM 상에 10핀 헤더(`B-2100S10P-A110`, LCSC `C124372`)로 잘못 등재되어 SMT 발주 오작업 위험 존재.
  - `F1` 폴리퓨즈가 1.5A 정격(`SMD1206P150TF`)으로 되어 있어, 12V 앰프 대음량 + ESP32 Wi-Fi 풀 파워(19.5dBm) + 60GHz 레이더 동시 구동 시의 5V 피크 전류(2.0~2.4A) 및 밀폐 케이스 내부 온도(45°C) 조건에서 트립 한계가 약 1.1A로 디레이팅되어 전원 차단 오작동 위험 상존.
- **의사결정**:
  - `J1`, `J2`를 실물 정격인 **2.54mm 2핀 헤더 (`B-2100S02P-A110`, LCSC: `C124375`, Footprint: `2.54mm 2P Pin Header`)**로 즉시 정정.
  - `F1`을 45°C 열 디레이팅을 견디는 **3.0A 홀딩 정격 SMD PPTC (`SMD1206P300TF`, LCSC: `C269155`, 1206)**로 전격 상향.

### [결정 26] Rev-C 실제 제조 패키지(Rev_C_mfg) 정상화 및 4층 56부품 실증 기준 동결 (옵션 A 확정)
- **발견된 사실 및 배경**:
  - 로컬 EasyEDA Pro 프로젝트 DB(`/Users/youngseok/Documents/EasyEDA-Pro/projects/260627.eprj2`, `260627_backup`) 및 실물 제조 아카이브([`인증준비/pcb/260708/`](file:///Users/youngseok/Desktop/majn/인증준비/pcb/260708/)) 전수 조사 결과, #0005 실물 보드에 실증된 **진짜 4층 56부품 거버(`Gerber_InnerLayer1.G1`, `Gerber_InnerLayer2.G2` 포함 21개 파일)** 및 CPL/BOM이 존재함을 확인.
  - 기존 텍스트 파일에서 임의의 이름(`R_ADR`, `R_BEN`, `C_AVDD` 등)으로 중복 가산되었던 보강 부품들은 이미 `rev-B` 4층 보드에 `R1~R14`, `C1~C27` 표준 연번으로 100% 라우팅 완료 상태였음.
- **의사결정 (옵션 A 확정)**:
  1. **독립 제조 디렉터리 구축**: [`/Users/youngseok/Desktop/majn/인증준비/pcb/Rev_C_mfg/`](file:///Users/youngseok/Desktop/majn/인증준비/pcb/Rev_C_mfg/)를 신설하여 4층 제조 패키지(`Gerber_MAJN_Rev_C.zip`, `BOM_MAJN_Rev_C.csv`, `CPL_MAJN_Rev_C.csv`, `MAJN_Rev_C.epro2`)를 독립 구축.
  2. **오발주 방지 격리**: 루트의 레거시 37부품 2층 거버를 [`DEPRECATED_37part_2layer_Gerber_Output.zip`](file:///Users/youngseok/Desktop/majn/DEPRECATED_37part_2layer_Gerber_Output.zip)으로 격리 조치.
  3. **회로 파라미터 동결**:
     - 12V 승압: `R1`=143kΩ(`C22877`), `R2`=16kΩ(`C22818`) $\rightarrow$ $V_{OUT} = \mathbf{12.17V}$
     - 칩 품번: `U3`=MP3426DL(`C133224`), `U2`=AP2112K-3.3(`C51118`, 600mA), `D1`=SMAJ5.0A(`C83329`)
     - I2C 주소 및 시퀀싱: `R12`=4.7kΩ(7-bit `0x2C`), `R11`=100kΩ PD, `R13`/`R14`=10kΩ PU
     - 오디오 EMI: `FB1~4` (220Ω 3A `C154119`) + `C24~27` (2.2nF 50V `C16033`)
  4. **기구 간섭(13.5mm) 해소 및 LCSC 실물 발주 품번 정합**:
     - `J1`, `J2`, `UART_HDR`을 **직각(Right-Angle 90°) 저배형 커넥터**(`B-2100S02P-A120`, `B-2100S06P-A120`)로 변경하여 케이블 측면 인출 구조 확립.
     - **JLCPCB Part # 실품번 동기화**: `BOM_MAJN_Rev_C.csv` 내에서 수직 핀헤더 품번(`C124375`, `C124380`)을 완벽히 퇴출하고, 실제 90° 직각 핀헤더인 **`C124376` (`J1,J2`)** 및 **`C124381` (`UART_HDR`)**로 1:1 매칭 완료.
     - 수직 스택업 계산: 스페이서(3.0mm) + PCB(1.76mm) + 최고부품(5.0mm) = 9.76mm $\le$ 캐비티 최소 유효고 13.0mm (**+3.24mm 안전 여유고 확보**).
  5. **100% 단면(Top) SMT 달성 및 실증 베이스라인 확정**:
     - `2026-07-09` 개선판을 제조 베이스라인으로 동결. 구버전(`2026-07-08`)의 바닥면 `R12` (0603 `C23162`)를 상면 `0402` (`C25900`)로 전환하여 **56개 전 부품 100% Top 단면 실장**을 달성, 양면 실장 비용 절감 및 바닥면 돌출 완전 배제.
  6. **RF 간섭 근본 해결**:
     - `U1`을 외장 u.FL 안테나 모듈인 **`ESP32-WROOM-32UE-N8` (`C701345`)**로 확정.
  7. **진성 자동 검증기 통과 (Gerber FPT ↔ CPL 좌표 교차 검증)**:
     - 신규 [`tools/verify_mfg_package.py`](file:///Users/youngseok/Desktop/majn/tools/verify_mfg_package.py) 검증 스크립트를 통해 `FlyingProbeTesting.json`과 `CPL_MAJN_Rev_C.csv` 간 56개 전 부품의 실제 물리 좌표를 $\mu\text{m}$ 단위로 전수 비교:
       - $\max(\Delta X) = 0.0004\text{mm}$, $\max(\Delta Y) = 0.0004\text{mm}$ ($\le 0.01\text{mm}$ 허용치 대비 25배 정밀)
       - CPL 및 FPT 상 100% Top 레이어 단면 실장 확인
       - **5/5 GATES 100% PASS** 확인.

---

## 3. 부품 수 및 설계 정합성 최종 현황 (BOM & Netlist Parity)
- **총 부품 수**: **70개** (기존 65개 + R_ADR, R_BEN, R_PDN, R_CS, C_BULK)
- **총 액티브 네트 수**: **59개** (기존 58개 + AMP_ADR)
- **1-Pin 데드 네트 수**: **0개 (Zero Dead Nets)**
- **정합성 검증 결과**:
  ```bash
  $ python3 /Users/youngseok/Desktop/majn/tools/verify_hardware_review.py
  VERIFICATION SUMMARY: 21 / 21 LOGICAL RULES PASSED (100.0%)
  ```

---

## 4. 설계 아티팩트별 실제 반영 상태 및 SSOT 구분 (정밀 감사 결과)

> [!WARNING] 중요: EasyEDA Pro 에디터 물리 배치 동기화 필요
> 자동 검증 스크립트(`verify_hardware_review.py`)의 21/21 PASS는 `BOM.csv`와 `Netlist.net`의 전기적·논리적 정합성 검증 결과입니다. `Rev_C.epro2` 바이너리 내부의 실제 회로도 심볼/배선 및 PCB 패턴은 EasyEDA Pro 에디터를 통해 실체화해야 합니다.

1. **BOM.csv & Netlist.net (100% 신뢰 가능한 SSOT)**:
   - 70개 부품 및 59개 넷이 완벽히 명세되어 있으며, 12V 승압 저항비(12.45V), 25V MLCC 내압, 1A LDO, 10ms POR 지연, 오디오 EMI/댐핑, 제로 데드넷, U4.9 NC 격리, U4.3 R_ADR 풀다운(7-bit 0x2C), 부팅 스트래핑 저항(R_BEN/R_PDN/R_CS), 5V TVS(SMAJ5.0A) 및 13.5mm 캐비티 기구 간섭 배제, 2핀 스피커 헤더(J1/J2), 3.0A PPTC(F1) 사양이 100% 확정됨.
2. **Rev_C.epro2 (에디터 실체화 대기 상태)**:
   - 내부 메타데이터 및 프로젝트 타이틀/설명은 Rel 5로 업데이트 준비 중이며, 실제 그래픽 엔티티(신규 저항 4종, C_BULK, TVS 심볼 및 트랙 등)는 EasyEDA Pro GUI/브릿지를 통해 실장 배치가 동기화되어야 함.
   - 현 상태의 `.epro2`로 직접 거버를 출력하여 발주해서는 안 되며, 에디터에서 부품 배치 완료 후 최종 거버를 생성해야 함.
3. **ESP32-WROOM-32UE-N8 풋프린트 검토 사항**:
   - 모듈 외형 치수가 18.0 × 19.2 mm로 기존 32E(18.0 × 25.5 mm)보다 길이가 6.3mm 짧음.
   - 하단 핀 패드 배열은 호환되나, 상단 안테나 영역 및 외곽 실크스크린/동박 패턴이 상이하므로 에디터 상에서 32UE 전용 풋프린트로의 실장 검증 권장.
