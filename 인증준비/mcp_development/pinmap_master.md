# 마스터 핀맵 (검증 기준표) — S1 산출물

본 표는 정정 넷리스트(S2)와 재검증(S7)의 **단일 진실 공급원(SSOT)** 이다.
출처: TI TAS5805M(SLASEH5D, 로컬 PDF 추출), ST LSM6DSOX 표준 LGA‑14 핀아웃, Espressif ESP32‑WROOM‑32E 모듈, 실측 넷리스트(`FlyingProbeTesting.json`) 교차검증.
표기: ✅확정 · ⚠️S4 라이브 심볼 덤프에서 핀번호 최종확인 필요.

---

## U1 — ESP32-WROOM-32E (C701342)  ✅
모듈 패드번호. 실측(U1_30=IO18, U1_31=IO19, U1_37=IO23, U1_6=IO34, U1_2=3V3, U1_1=GND)과 일치 확인.

| 기능(네트) | 패드# | 심볼 핀이름 |
|---|---|---|
| 3.3V (VCC_3V3) | 2 | 3V3 |
| GND | 1, 15, 38, 39(EP) | GND |
| EN (ESP_EN) | 3 | EN |
| BOOST_EN | 26 | IO4 |
| SPI_CS | 29 | IO5 |
| SPI_SCLK | 30 | IO18 |
| SPI_MISO | 31 | IO19 |
| SPI_MOSI | 37 | IO23 |
| SENSOR_INT1 | 6 | IO34 (입력전용) |
| I2S_BCLK | 11 | IO26 |
| I2S_LRCLK | 10 | IO25 |
| I2S_DIN | 36 | IO22 |
| AMP_I2C_SDA | 33 | IO21 |
| AMP_I2C_SCL | 12 | IO27 |
| AMP_PDN | 23 | IO15 (strapping) |
| ESP_IO0 | 25 | IO0 (strapping) |
| ESP_RXD | 34 | RXD0 (IO3) |
| ESP_TXD | 35 | TXD0 (IO1) |

> 스키매틱 흐름은 이름 매칭(GPIO26↔IO26 별칭)하므로 스펙은 GPIO명으로 참조 가능. EP(39)는 반드시 GND.

## U4 — TI TAS5805M, PWP/HTSSOP-28 (C478472)  ✅ (TI 데이터시트 확정)

| 기능(네트) | 패드# | 핀이름 | 비고 |
|---|---|---|---|
| GND (디지털) | 1, 5 | DGND | **현재 미접지→수정** |
| **3.3V (VCC_3V3)** | 2 | DVDD | **현재 미연결→3.3V 연결 필수** + 디커플 |
| I2C 주소설정 | 3 | ADR/FAULT | GND직결 대신 저항 권장(0x2C) |
| (내부 1.5V reg) | 4 | VR_DIG | 외부공급 금지, 디커플 캡만 |
| I2S_LRCLK | 6 | LRCLK | **현재 pin8 오결선** |
| I2S_BCLK | 7 | SCLK | ✓ |
| I2S_DIN | 8 | SDIN | **현재 pin9(SDOUT) 오결선** |
| (미사용/선택) | 9 | SDOUT | 출력, 보통 미연결 |
| AMP_I2C_SDA | 10 | SDA | **현재 pin5 오결선** |
| AMP_I2C_SCL | 11 | SCL | **현재 pin6 오결선** |
| AMP_PDN | 12 | PDN | 활성-Low(High=enable) |
| (내부 5V reg) | 13 | AVDD | 외부공급 금지, 디커플 캡만 |
| GND (아날로그) | 14 | AGND | |
| **PVDD_12V** | **15,16,27,28** | PVDD | **현재 15만 연결·28은 GND단락→4핀 전부 12V** |
| GND (파워) | 19, 24 | PGND | **현재 미접지→수정** |
| AMP_OUT_B+ | 17 | OUT_B+ | ✓ |
| BST_B+ | 18 | BST_B+ | ✓ |
| AMP_OUT_B- | 20 | OUT_B- | ✓ |
| BST_B- | 21 | BST_B- | ✓ |
| BST_A- | 22 | BST_A- | ✓ |
| AMP_OUT_A- | 23 | OUT_A- | ✓ |
| BST_A+ | 25 | BST_A+ | ✓ |
| AMP_OUT_A+ | 26 | OUT_A+ | ✓ |
| **GND** | EP(29) | PowerPAD | **현재 PVDD_12V→GND로 수정(중대)** |

> 추가 필요 부품: DVDD 디커플(0.1µF+1µF), AVDD 디커플(1µF→AGND), VR_DIG 디커플(0.1µF). I2C 풀업 2개.

## U2 — SGM2036-3.3YUDH4 LDO, UTDFN-1x1-4L (C81114)  ✅
정류 및 3.3V 변환 전원용 LDO.

| 기능(네트) | 패드# | 핀이름 | 비고 |
|---|---|---|---|
| OUT (VCC_3V3) | 1 | OUT | 3.3V 전원 출력 |
| GND | 2 | GND | 접지 |
| EN (VBUS_5V) | 3 | EN | LDO 활성화 (5V 인가) |
| IN (VBUS_5V) | 4 | IN | 5V 전원 입력 |
| GND | 5 (EP) | EP | 노출 방열 패드, 접지 |

---

## U5 — ST LSM6DSOX, LGA-14 (C481766)  ✅(LCSC 표준 LGA-14 라이브러리 교차검증)
표준 ST LGA‑14 핀아웃. 실측 U5_1=SDO, U5_4=INT1, U5_6/7=GND, U5_13=SPC, U5_14=SDI 일치.

| 기능(네트) | 패드# | 핀이름 | 비고 |
|---|---|---|---|
| SPI_MISO | 1 | SDO/SA0 | ✓ |
| (보조 I2C) | 2 | SDX | 미사용시 데이터시트대로 종단 |
| (보조 I2C) | 3 | SCX | 미사용시 종단 |
| SENSOR_INT1 | 4 | INT1 | ✓ |
| **VCC_3V3** | 5 | VDDIO | IO 전원 (3.3V 연결) |
| GND | 6 | GND | 접지 |
| GND | 7 | GND | 접지 |
| **VCC_3V3** | 8 | VDD | 주전원 (3.3V 연결 - **오동규 설계 오류 수정**) |
| (미사용) | 9 | INT2 | 인터럽트2 (미사용 - **기존 VCC_3V3 오연결 수정**) |
| (선택) INT2 | 10 | OSC_AUX | 보조 오실레이터 |
| 예약 | 11 | SDO_AUX | 보조 SPI 데이터 |
| **SPI_CS** | 12 | CS | SPI 칩 셀렉트 (SPI_CS 연결) |
| SPI_SCLK | 13 | SCL/SPC | SPC 클록 |
| SPI_MOSI | 14 | SDA/SDI | SDI 데이터 |

## U3 — MPS MP3426 부스트, QFN-14+EP (C162810)  ⚠️ 핀번호 S4 확정
C162810=MP3426(6A/35V 부스트) 확인. **현재 보드엔 2패드뿐** → 올바른 14핀 심볼로 교체 후 아래 토폴로지로 결선. 핀 **이름**으로 스펙 작성, 정확한 패드번호는 S4 라이브 심볼 덤프로 확정.

| 기능(네트) | 핀이름 | 연결 |
|---|---|---|
| 입력 5V (VBUS_5V) | VIN | + 입력캡 C5, 인덕터 L1 입력측 |
| 스위치노드 (BOOST_SW) | SW | 인덕터 L1, 쇼트키 D3 애노드 |
| 피드백 (BOOST_FB) | FB | R1/R2 분압 노드 |
| 인에이블 (BOOST_EN) | EN | ESP32 IO4 |
| 보상 | COMP | **R-C 보상망 추가 필요(현재 없음)** |
| 소프트스타트 | SS | **SS 캡 추가 검토** |
| 주파수설정 | FREQ | 저항/종단(데이터시트) |
| 접지 | GND, PGND, EP | GND |

> ⚠️ **S4에서 확정**: ① MP3426 실제 패드번호/핀이름, ② FB 기준전압 Vref(현 R1=150k/R2=16k가 12V 산출하는지; Vref 1.2V 가정 시 ≈12.45V), ③ COMP/SS/FREQ 필요 부품.

## 커넥터/헤더
- **UART_HDR (C124380, 1×6):** 1=3V3, 2=EN, 3=IO0, 4=TXD, 5=RXD, 6=GND. ✅(실측 일치)
- **J1/J2 (C124372, 1×2):** 1=+, 2=−. ✅(실측 AMP_OUT 일치, 기능핀만)
- **USB_C (C165948, Type-C 16P):** 기능=VBUS·GND·CC1·CC2·(D±). ⚠️ **패드 라벨 S4 확정 필요** — 이 16핀 풋프린트는 표준 24핀 A1~B12 라벨을 쓰지 않음(실측에서 VBUS=병합패드 `B4A9`, GND=`A1B12`, CC2=`B8`로 나타남). 따라서 CC1/CC2/VBUS의 정확한 패드명은 라이브 심볼 덤프로 확정. (**확정 사항: USB_CC1에 CC1 패드가 빠져 있어 추가 필요**)

---

## S1 결론 — 정정의 핵심(요약)
1. **U4 전원계 전면 복구**: DVDD(2)→3V3, DGND(1,5)·PGND(19,24)→GND, PVDD(15,16,27,28) 4핀 전부→12V, **EP→GND**(현재 12V), +디커플/I2C풀업.
2. **U4 디지털 정렬**: SDA→10, SCL→11, LRCLK→6, SDIN→8 (BCLK=7 유지), PDN→12.
3. **U5 정렬**: VDD(9)·VDDIO(5)→3V3, CS(12)→SPI_CS, GND(8) 추가.
4. **U3 14핀 복구** + COMP/SS 보상망(S4 확정).
5. **ESP32 전 신호 결선**(이름 기준) + EP→GND, **USB_CC1 추가**.

➡️ 다음: **S2 — `mcp_design_flow.json` 정정**. (S1 종료, 확인 후 진행)
