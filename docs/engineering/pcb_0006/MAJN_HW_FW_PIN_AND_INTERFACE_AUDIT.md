# [핀 인터페이스 감사서] MAJN PCB #0006 — ESP32 전체 GPIO 할당 및 TAS5805M PDN 후보 감사 보고서
(MAJN PCB #0006 ESP32 Full GPIO Allocation & TAS5805M PDN Candidate Audit Report)

- **문서 식별자**: `MAJN_HW_FW_PIN_AND_INTERFACE_AUDIT`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **감사 대상**: ESP32-WROOM-32UE-N8 전체 핀맵, 부트 스트래핑, 펌웨어 소스 및 TAS5805M PDN 배정

---

## 1. 개요 및 감사 목적

선행 보고서에서 TAS5805M Pin 12(PDN) 제어 핀을 기존 GPIO15(MTDO 스트래핑 간섭)에서 **GPIO13으로 배정 완료**하였다고 기술하였으나, 본 감사에서는 ESP32의 38개 전체 핀맵, JTAG 다중화, 부팅 시 핀 상태, 그리고 기존 펌웨어 소스와의 일치성을 전수 조사하여 **GPIO13의 실제 가용성을 공학적으로 검증하고 승인 상태를 '후보(Candidate)'로 정정**한다.

---

## 2. ESP32-WROOM-32UE 전체 38핀 할당 전수 실사표

| Pin | 심볼 명칭 | 현재 배정 기능 | 스트래핑 여부 | 리셋 시 디폴트 상태 | 핀 공유 / 제약 사항 | 가용성 판정 |
|:---:|:---|:---|:---:|:---:|:---|:---:|
| 1 | GND | 접지 (GND) | - | 0V | 공통 접지면 | 필수 |
| 2 | 3V3 | 전원 입력 (3.3V) | - | 3.3V | 3.3V LDO 출력 | 필수 |
| 3 | EN (CHIP_PU) | 하드웨어 리셋 | - | 풀업(10k+1µF) | RC 지연 리셋 | 필수 |
| 4 | SENSOR_VP (GPIO36) | 미사용 (NC) | - | Input Only | ADC1_CH0, 출력 불가 | Input 전용 |
| 5 | SENSOR_VN (GPIO39) | 미사용 (NC) | - | Input Only | ADC1_CH3, 출력 불가 | Input 전용 |
| 6 | GPIO34 | `PIN_SAFETY_INT1` | - | Input Only | LSM6DSOX 1.5g 비상 충격 인터럽트 | **점유 (입력)** |
| 7 | GPIO35 | 미사용 (NC) | - | Input Only | ADC1_CH7, 출력 불가 | Input 전용 |
| 8 | GPIO32 | 미사용 (NC) | - | 풀다운 (Weak) | 32kHz 크리스탈 또는 일반 GPIO | **가용 (Free)** |
| 9 | GPIO33 | 미사용 (NC) | - | 풀다운 (Weak) | 일반 GPIO / ADC1 | **가용 (Free)** |
| 10 | GPIO25 | `PIN_I2S_LRCLK` | - | 풀다운 (Weak) | I2S 오디오 워드 셀렉트 (48kHz) | **점유 (출력)** |
| 11 | GPIO26 | `PIN_I2S_BCLK` | - | 풀다운 (Weak) | I2S 오디오 비트 클록 (1.536MHz) | **점유 (출력)** |
| 12 | GPIO27 | `PIN_I2C_SCL` | - | 풀업(4.7k) | TAS5805M I2C 클록 라인 | **점유 (I2C)** |
| 13 | GPIO14 | 미사용 (NC) | - | 풀업 (Weak) | MTMS (JTAG) 또는 일반 GPIO | **가용 (Free)** |
| 14 | GPIO12 | 미사용 (NC) | **STRAITING** | 풀다운 (Weak) | **MTDI (VDD_SDIO 전압 결정, 위험)** | **사용 회피** |
| 15 | GND | 접지 (GND) | - | 0V | 공통 접지면 | 필수 |
| 16 | **GPIO13** | **[PDN 후보]** | **아님** | **풀다운 (Weak)** | **MTCK (JTAG) 또는 일반 GPIO** | **최우선 후보** |
| 17~22| SD2~CLK | 내부 플래시 (SPI) | - | - | 8MB SPI Flash 점유 (외부 사용 불가)| **사용 금지** |
| 23 | GPIO15 | (구 PDN 배정선) | **STRAPPING** | 풀업 (Weak) | **MTDO (UART0 ROM 로그 제어)** | **격리 대상** |
| 24 | GPIO2 | 미사용 (NC) | **STRAPPING** | 풀다운 (Weak) | 부트 모드 선택 스트래핑 | **사용 회피** |
| 25 | GPIO0 | `BOOT_IO0` | **STRAPPING** | 풀업(10k) | 다운로드 부트 스트래핑 | **점유 (부트)** |
| 26 | GPIO4 | `PIN_BOOST_EN` | - | 풀다운(10k) | MP3426 12V 승압 활성화 제어 | **점유 (출력)** |
| 27 | GPIO16 | 미사용 (NC) | - | 풀다운 (Weak) | PSRAM 미탑재 모델(WROOM-32UE) Free | **가용 (Free)** |
| 28 | GPIO17 | 미사용 (NC) | - | 풀다운 (Weak) | PSRAM 미탑재 모델(WROOM-32UE) Free | **가용 (Free)** |
| 29 | GPIO5 | `PIN_SPI_CS_XL` | - | 풀업(10k) | LSM6DSOX SPI 칩 셀렉트 | **점유 (출력)** |
| 30 | GPIO18 | `PIN_SPI_SCLK` | - | - | **LSM6DSOX SPI 클록 (충돌 확인됨)** | **점유 (SPI)** |
| 31 | GPIO19 | `PIN_SPI_MISO` | - | - | LSM6DSOX SPI 데이터 입력 | **점유 (SPI)** |
| 32 | NC | - | - | - | No Connect | - |
| 33 | GPIO21 | `PIN_I2C_SDA` | - | 풀업(4.7k) | TAS5805M I2C 데이터 라인 | **점유 (I2C)** |
| 34 | RXD0 (GPIO3) | `UART_RX` | - | 풀업 (Weak) | USB-UART 디버그/다운로드 수신 | **점유 (UART)** |
| 35 | TXD0 (GPIO1) | `UART_TX` | - | 풀업 (Weak) | USB-UART 디버그/다운로드 송신 | **점유 (UART)** |
| 36 | GPIO22 | `PIN_I2S_DOUT` | - | 풀다운 (Weak) | I2S 오디오 시리얼 데이터 출력 | **점유 (출력)** |
| 37 | GPIO23 | `PIN_SPI_MOSI` | - | - | LSM6DSOX SPI 데이터 출력 | **점유 (SPI)** |
| 38 | GND | 접지 (GND) | - | 0V | 공통 접지면 | 필수 |

---

## 3. TAS5805M PDN 제어 핀 후보군 비교 분석

| 후보 GPIO | 스트래핑 여부 | 리셋 초기 상태 | JTAG / 주변 다중화 | 펌웨어 영향 | 장단점 및 공학적 판정 |
|:---:|:---:|:---:|:---|:---|:---|
| **GPIO13** | **아님 (Safe)** | **약한 풀다운** | MTCK (JTAG 미사용 시 완전 독립) | `#define PIN_AMP_PDN 13` 수정 필요 | **최우선 후보 (1순위)**<br>리셋 시 디폴트 풀다운으로 외장 10k 풀다운과 조화되어 앰프 기동 퍽 노이즈 원천 차단. |
| **GPIO16** | 아님 (Safe) | 약한 풀다운 | UART2_RXD / 일반 GPIO | `#define PIN_AMP_PDN 16` 수정 필요 | **보조 후보 (2순위)**<br>PSRAM 없는 모듈이므로 완전 자유 핀이나 보드 우측 상단에 위치하여 라우팅 경로가 김. |
| **GPIO32** | 아님 (Safe) | 약한 풀다운 | 32K_XP / ADC1 | `#define PIN_AMP_PDN 32` 수정 필요 | **보조 후보 (3순위)**<br>가용하나 아날로그 라인 근접. |
| **GPIO18** | 아님 | - | **LSM6DSOX SPI_SCLK** | **심각한 충돌 발생** | **절대 불가 (REJECTED)**<br>기존 IMU 센서 SPI 클록 점유 핀. |
| **GPIO15** | **스트래핑 (MTDO)** | **약한 풀업** | **UART0 ROM 디버그 출력 제어** | 기존 펌웨어 설정값 | **배제 권고 (DISCOURAGED)**<br>외장 풀다운과의 전압 분배에 따른 타이밍 위험. |

---

## 4. 감사 결론 및 승인 권고

1. **GPIO13의 기술적 타당성**:
   - ESP32 공식 하드웨어 가이드상 GPIO13은 부트 스트래핑 핀이 아니며, 외부 JTAG 프로브를 사용하지 않는 본 제품 환경에서 TAS5805M PDN 제어용으로 가장 이상적인 핀임이 입증됨.
2. **승인 상태 정정**:
   - 하드웨어 회로도 수정 및 펌웨어 헤더(`amplifier_manager.h`) 동기화가 아직 승인되지 않았으므로, 본 핀 할당은 **"승인 대기 후보(Candidate Pending Gate G3 Approval)"**로 관리하며, Gate G3 통과 시 정식 반영함.
