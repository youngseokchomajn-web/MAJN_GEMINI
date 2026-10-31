# 마중(MAJN) 스마트 배시넷 Rev-C 종합 개발 및 양산·인증 마스터 플랜

* **문서 버전:** Rev-C.Master.1.0
* **작성 일자:** 2026-10-31
* **책임 엔지니어:** MAJN Hardware & Software Integration Team
* **기준 브랜치:** `feature/phone-wifi-control`

---

## 1. 프로젝트 배경 및 현재 진행 상태 (Current Baseline)

### 1.1 하드웨어 베이스라인 (PCB #0005 실측 완료)
* **전원 무결성**: USB 5.02V 입력 $\rightarrow$ SGM2036-3.3 LDO (3.20V) $\rightarrow$ MP3426 승압 (12.00V PVDD) 레귤레이션 실측 검증 완료.
* **디지털 오디오 및 액추에이터**: TI TAS5805M Class-D 앰프(I2C 주소 `0x2C`) 정상 `PLAY(0x03)` 상태 진입, 24.8Ω 직렬 익사이터 부하(30~65Hz)를 통한 매트리스 물리 진동 확인.
* **하드웨어 물리적 제약**:
  * 보드에 물리적 버튼(BOOT, EN) 부재.
  * CP2102 헤더는 TX, RX, GND만 연결(DTR/RTS 자동 부트로더 리셋 회로 없음).
  * **유선 시리얼 다운로드 불가, 무선 OTA(BLE / Wi-Fi) 전용 플래시 구조**.

### 1.2 소프트웨어 제어 방식 전환 완료
* PC USB 유선 제어에서 **휴대폰 직접 제어(Wi-Fi SoftAP + Web-UI)**로 전환 완료.
* SSID: `MAJN-Bassinet` (Ch 6, 19.5dBm, 캡티브 포털 DNS 자동 팝업).
* 5초 Heartbeat 감시 안전 Watchdog 및 Web-OTA(`/update`) 탑재.
* BLE 무손실 Paced OTA 스크립트(`tools/run_ble_ota.py`)를 통해 1,088KB 펌웨어 무선 플래시 성공 확인.

### 1.3 단일 진실 원천(SSOT) 복구 및 결함 해결 완료
* 원본 `.epro2` 역공학 분석을 통해 **부스트 다이오드 `D3`(3.9kΩ 저항 오매핑)와 인덕터 `L1`(5.6kΩ 저항 오매핑)의 원본 설계 결함 공식 규명**.
* `PCB_Rev_C` 프로젝트 독립 바이너리(`Rev_C.epro2`) 실체화(고유 SHA-256 생성, 54개 부품 / 58개 넷).
* 자동 검증 스크립트(`tools/verify_hardware_review.py`) 구동 결과 **7대 전 항목 100% PASS** 달성 (GitHub 커밋 `61f45c0` 푸시 완료).
* 크롬 기반 EasyEDA Pro 에디터 실시간 자율 제어 통제권 확보.

---

## 2. PCB Rev-C 핵심 아키텍처 및 설계 사양

```
                     ┌────────────────────────────────────────────────────────┐
                     │                 USB Type-C (5V Power)                  │
                     └──────────────────────────┬─────────────────────────────┘
                                                │
                                    [F1: PPTC Fuse 1.5A] (전원보호)
                                                │
                                                ▼
     ┌──────────────────────────────────── VBUS (5V) ───────────────────────────────────┐
     │                                          │                                       │
     ▼                                          ▼                                       ▼
┌──────────────┐                       ┌─────────────────┐                     ┌────────────────┐
│  SGM2036-3.3 │                       │  MP3426 Boost   │                     │ J_RADAR (4P)   │
│  (3.3V LDO)  │                       │  (12V PVDD)     │                     │ 60GHz mmWave   │
└──────┬───────┘                       └────────┬────────┘                     └────────────────┘
       │                                        │ [RC Snubber: 2.2Ω + 1nF]
       ├───────────────────┐                    ▼
       ▼                   ▼           ┌─────────────────┐
┌──────────────┐    ┌──────────────┐   │    TAS5805M     │
│ ESP32-WROOM  │    │ J_BCG (4P)   │   │  (Class-D Amp)  │
│ -32E (MCU)   │    │ PVDF Sensor  │   └────────┬────────┘
└──────┬───────┘    └──────────────┘            │ [FB1~FB4: Ferrite Beads]
       │                                        ▼
       ├───────────────────────────────► ┌─────────────────┐
       ▼                                 │ J1/J2 Exciters  │
┌──────────────┐                         │ (Dual Channels) │
│ J_ENV_MIC    │                         └─────────────────┘
│ (6P: I2C/I2S)│
└──────────────┘
```

### 2.1 전파인증(EMC) 및 전기안전 방어 대책
1. **USB 전원 과전류/단락 보호 (`F1`)**:
   * 부품: 1.5A 6V 리셋 가능 폴리퓨즈 (PPTC 1206, LCSC: `C112349`).
   * 결선: `NET_VBUS_RAW` $\rightarrow$ `F1` $\rightarrow$ `VBUS_5V` (내부 회로 공급).
2. **MP3426 승압 고주파 링잉 스너버 (`C_SNUB` + `R_SNUB`)**:
   * 목적: 900kHz 스위칭 주파수의 수십 MHz 고조파 복사 방사(RE) 감쇠.
   * 규격: 1nF 50V X7R 0603 (`C14666`) + 2.2Ω 1/10W 0603 (`C22800`).
   * 결선: `BOOST_SW` $\rightarrow$ `C_SNUB` $\rightarrow$ `NET_SNUB_MID` $\rightarrow$ `R_SNUB` $\rightarrow$ `GND` (완전 직렬).
3. **오디오 출력 안테나 방사 억제 (`FB1 ~ FB4`)**:
   * 목적: 1~2m 익사이터 연결 케이블이 고주파 노이즈 방사 안테나로 동작하는 현상 차단.
   * 규격: 100Ω @ 100MHz, 정격 전류 2A, 0805 패키지 (LCSC: `C1015`).
   * 결선: BTL 출력 4개 라인(`AMP_OUT_A+/A-`, `AMP_OUT_B+/B-`)에 직렬 삽입.

### 2.2 3대 센서 확장 포트 및 0Ω 격리 설계
모든 센서 인터페이스는 **0Ω 분리 링크 저항군(`R_L1 ~ R_L7`)**을 경유하도록 설계하여, **1차 KC 전파인증 시 미실장(DNP)하여 노이즈를 원천 차단**하고 양산 시 부품 실장만으로 센서 모델을 출하하는 **단일 기판 2트랙 인증 전략**을 구현합니다.

| 센서 포트 | 커넥터 규격 | 연결 핀맵 | 할당 MCU GPIO | 0Ω 링크 저항 | 용도 및 알고리즘 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`J_BCG`** | JST-SH 1.0mm 4P | 1: 3.3V, 2: GND<br>3: SIG_P, 4: SIG_N | GPIO36 (VP)<br>GPIO39 (VN) | `R_L1` (SIG_P)<br>`R_L2` (SIG_N) | 매트리스 하부 PVDF 필름 심탄도(BCG) 감지 (호흡/심박) |
| **`J_RADAR`** | JST-SH 1.0mm 4P | 1: 5V, 2: GND<br>3: RADAR_TX, 4: RADAR_RX | GPIO16 (RX2)<br>GPIO17 (TX2) | `R_L3` (RADAR_TX)<br>`R_L4` (RADAR_RX) | 60GHz mmWave 생체 레이더 비접촉 아기 재실/뒤척임 감지 |
| **`J_ENV_MIC`** | JST-SH 1.0mm 6P | 1: 3.3V, 2: GND<br>3: SDA, 4: SCL<br>5: WS, 6: DIN | GPIO21 (SDA)<br>GPIO19 (SCL)<br>GPIO25 (WS)<br>GPIO35 (DIN) | `R_L5` (SDA)<br>`R_L6` (SCL)<br>`R_L7` (WS) | SHT40 온습도 센서(I2C) + INMP441 디지털 마이크(I2S) |

---

## 3. PCB 레이아웃 및 거버 아트워크 규칙

1. **4층 기판 스택업 (Standard 4-Layer Stackup)**:
   * **Layer 1 (Top Layer)**: 주요 IC(ESP32, MP3426, TAS5805M) 실장, 고전류 전원 배선, RF 안테나 킵아웃.
   * **Layer 2 (Ground Plane)**: 솔리드 GND 플레인 (노이즈 억제 및 임피던스 기준면).
   * **Layer 3 (Power Plane)**: PVDD 12V 전원 및 5V/3.3V 전원 분할 아일랜드.
   * **Layer 4 (Bottom Layer)**: 신호선(I2C, I2S, UART, ADC) 및 센서 커넥터 인출 배선.
2. **배치 규칙 (Layout Guidelines)**:
   * **센서 커넥터(`J_BCG`, `J_RADAR`, `J_ENV_MIC`)**: 기판 우측 외곽 모서리에 1.0mm 피치로 일렬 배치하여 배선 하네스 간섭 방지.
   * **부스트 스위칭 루프**: MP3426 SW 핀 $\rightarrow$ L1 $\rightarrow$ D3 $\rightarrow$ C6/C7 커패시터 그라운드로 이어지는 고주파 루프 면적을 **20mm² 이하**로 극소화.
   * **ESP32 안테나 영역**: 안테나 하부 및 주변 5mm 이내 전 층 동박(Copper) 완전 배제(Keepout).
   * **동박 재구축(Shift+B)** 및 자동 DRC 전수 검증 통과 필수.

---

## 4. 전파인증(KC/FCC) 획득 전략 및 2트랙 로드맵

```
[Phase 1: 기판 제작] ──► [Phase 2: 베이스라인 인증] ──► [Phase 3: 센서형 파생 인증]
 Rev-C 통합 아트워크       기본형 (0Ω 저항 DNP)          센서형 (0Ω 저항 Populate)
 단일 PCB 거버 발주        EMC 적합등록 즉시 취득         기구물/센서 결합 파생 신고
 (비용 1회 투자)          (노이즈 리스크 0%)            (인증비·기간 70% 절감)
```

1. **1차 기본형 인증 (KC 적합등록 - DNP 모드)**:
   * 기판에 `R_L1 ~ R_L7` 0Ω 저항을 미실장(DNP)하여 센서 배선이 안테나로 동작하는 노이즈 경로 원천 차단.
   * 보드 단독(ESP32 Wi-Fi + MP3426 12V 승압 + TAS5805M 익사이터 구동) 상태로 전자파 적합성(KN 32/35) 시험 통과.
2. **2차 센서형 파생 인증 (Populate 모드)**:
   * 기본 모델 인증 완료 후, 0Ω 저항 실장 및 외장 센서 모듈 연결 상태로 파생 모델(기구 변경/부품 추가)로 접수.
   * 회로 기판을 새로 파지 않고 단일 PCB로 인증 완료하여 **개발 기간 2개월 단축 및 인증비 500만 원 이상 절감**.

---

## 5. 단계별 실행 일정 (Action Roadmap)

| 단계 | 목표 작업 | 완료 기준 / 산출물 | 마감 기한 |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Rev-C PCB 아트워크 완성 및 거버 출력** | • EasyEDA 에디터 상 17개 부품 배치<br>• DRC 무결성 통과<br>• `Gerber_RevC_Final.zip` 생성 | **D-Day ~ D+3** |
| **Phase 2** | **PCB 샘플 발주 및 SMT 부품 수급** | • JLCPCB/PCBWay 5장 발주 (4층 기판)<br>• LCSC 부품 BOM(54종) 일괄 발주 | **D+4 ~ D+7** |
| **Phase 3** | **Rev-C 시제품 1차 SMT 및 벤치 실측** | • 전원 레일(5V, 3.3V, 12V) 전압 계측<br>• PPTC 퓨즈 및 스너버 파형 오실로스코프 확인<br>• `Measurements/Rev_C_Measurements.csv` 기록 | **D+8 ~ D+14** |
| **Phase 4** | **3대 센서 펌웨어 드라이버 통합** | • BCG ADC1 신호 획득 및 호흡 필터링<br>• 레이더 UART2 텍스트 프로토콜 파싱<br>• SHT40 온습도 및 INMP441 오디오 I2S 입력 드라이버 탑재 | **D+15 ~ D+21** |
| **Phase 5** | **EMC 사전 측정소 방문 및 챔버 디버깅** | • 30MHz ~ 1GHz 복사 방사(RE) 스캔<br>• 스너버 저항/커패시터 튜닝 (필요시 값 최적화)<br>• 사전 시험 성적서 확보 | **D+22 ~ D+28** |
| **Phase 6** | **KC 공인 시험소 접수 및 본시험 합격** | • 기본 모델 공식 시험 성적서 발급<br>• 전파연구원 적합등록 완료 필증 획득 | **D+29 ~ D+38** |
| **Phase 7** | **양산 금형/하우징 결합 및 파생 모델 출시** | • 마중 배시넷 시제품 조립 완료<br>• 모바일 앱-기기 연동 실증 | **D+39 ~ D+50** |

---

## 6. 품질 및 무결성 검증 기준 (Definition of Done)

* [x] **SSOT 무결성**: EasyEDA 바이너리(`.epro2`), `BOM.csv`, `Netlist.net` 소자 및 핀 결선 100% 일치.
* [x] **자동 검증 통과**: `tools/verify_hardware_review.py` 7대 항목 100% 통과 유지.
* [ ] **거버 DRC 0건**: Clearances $\ge$ 6mil, Via drill $\ge$ 0.3mm, Board outline keepout 준수.
* [ ] **열 해석 및 정격**: MP3426 풀부하 12V 1.5A 구동 시 인덕터/다이오드 온도 $65^\circ\text{C}$ 이하 유지.
* [ ] **소프트웨어 안전성**: Wi-Fi 통신 두절 시 5초 이내 모터 자동 정지 Watchdog 정상 작동.
