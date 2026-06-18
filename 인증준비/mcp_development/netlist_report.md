# 마중 스마트배시넷 v1.1 넷리스트(Netlist) 연결 명세서

본 프로젝트의 자동 설계 파이프라인(`run_mcp_design_flow.py`)은 회로도(Schematic) 도면 설계 단계를 거치지 않고, 정의된 설계 명세(`mcp_design_flow.json`)를 기반으로 **PCB 기판 레이아웃에 부품을 다이렉트로 배치하고 배선하는 설계 방식**으로 구축되어 있습니다.

따라서 에디터 내에서 PCB 레이아웃 설계와 Gerber 출력은 완벽하게 완료되었으나, 부모에 해당하는 **Schematic(회로도) 탭은 빈 도화지 상태로 표시되는 것이 설계 구조상 정상**입니다.

회로도 도면 대신 아래의 **넷리스트 연결 명세서**를 참고하시면 모든 부품과 핀 간의 상세 연결 정보를 한눈에 파악하실 수 있습니다.

---

## 1. 전원 공급 및 파워 네트 (Power Nets)

| 넷 이름 (Net Name) | 배선 두께 (Width) | 연결 핀 및 부품 명세 (Pins / Components) | 설명 |
| :--- | :--- | :--- | :--- |
| **`VBUS_5V`** | 1.2 mm | <ul><li>`USB_C` (VBUS)</li><li>`U2` (IN - SGM2036 LDO 입력)</li><li>`D1` (SMAJ5.0A TVS 다이오드 보호단)</li><li>`C3` (LDO 입력 10uF 캡)</li></ul> | USB Type-C 커넥터로부터 유입되는 5V 주전원 라인 |
| **`VCC_3V3`** | 0.25 mm | <ul><li>`U1` (GPIO 3V3 - ESP32)</li><li>`U2` (OUT - LDO 출력 3.3V)</li><li>`U5` (VDD - LSM6DSOX 센서 전원)</li><li>`UART_HDR` (Pin 1 - 디버그 전원)</li><li>`C1`, `C2` (ESP32 바이패스 캡)</li><li>`C4` (LDO 출력 바이패스 캡)</li><li>`C10` (센서 바이패스 캡)</li></ul> | ESP32 및 센서 구동을 위한 정전압 3.3V 전원 버스 |
| **`PVDD_12V`** | 1.0 mm | <ul><li>`U3` (OUT - MP3426 부스트 컨버터 출력)</li><li>`U4` (PVDD - TAS5805M 오디오 앰프 전원)</li><li>`C6`, `C7` (부스트 출력 평활용 캡)</li><li>`C8`, `C9` (앰프 PVDD 바이패스 캡)</li></ul> | 스피커 및 진동 모터 고출력 구동을 위한 12V 승압 전원 |
| **`BOOST_SW`** | 0.25 mm | <ul><li>`U3` (SW - 부스트 레귤레이터 스위칭 노드)</li><li>`L1` (10uH 파워 인덕터)</li><li>`D3` (MBR140 부스트 다이오드)</li></ul> | MP3426 고주파 승압 스위칭용 노드 |
| **`GND`** | (통판 / Via) | <ul><li>`U1` (GND), `U2` (GND), `U3` (GND), `U4` (GND), `U5` (GND)</li><li>`USB_C` (GND), `UART_HDR` (GND)</li><li>모든 바이패스 캐패시터 및 인덕터/보호 소자 접지단</li></ul> | 4층 PCB의 Layer 2(GND Plane) 통판 접지 |

---

## 2. SPI 센서 인터페이스 (SPI Bus - LSM6DSOX)

* **대상 칩**: `U5` (ST LSM6DSOX) ↔ `U1` (ESP32-WROOM)

| 넷 이름 (Net Name) | ESP32 핀 (U1) | 센서 핀 (U5) | 역할 및 설명 |
| :--- | :--- | :--- | :--- |
| **`SPI_MOSI`** | GPIO 23 | SDI (Pin 14) | SPI Master-Out Slave-In 데이터 라인 |
| **`SPI_MISO`** | GPIO 19 | SDO (Pin 1) | SPI Master-In Slave-Out 데이터 라인 |
| **`SPI_SCLK`** | GPIO 18 | SPC (Pin 13) | SPI 직렬 클럭 라인 (Max 10MHz 동작) |
| **`SPI_CS`** | GPIO 5 | CS (Pin 12) | 센서 선택(Chip Select) 제어 라인 |
| **`SENSOR_INT1`** | GPIO 34 | INT1 (Pin 4) | LSM6DSOX 낙하/충격 감지 하드웨어 인터럽트 핀 |

---

## 3. I2S/I2C 오디오 인터페이스 (Audio Bus - TAS5805M)

* **대상 칩**: `U4` (TI TAS5805M) ↔ `U1` (ESP32-WROOM)

| 넷 이름 (Net Name) | ESP32 핀 (U1) | 앰프 핀 (U4) | 역할 및 설명 |
| :--- | :--- | :--- | :--- |
| **`I2S_BCLK`** | GPIO 26 | SCLK (Pin 4) | I2S 비트 클럭 (오디오 데이터 동기화 클럭) |
| **`I2S_LRCLK`** | GPIO 25 | LRCLK (Pin 5) | I2S 프레임/워드 클럭 (좌우 채널 분리 클럭) |
| **`I2S_DIN`** | GPIO 22 | SDIN (Pin 6) | I2S 직렬 디지털 오디오 데이터 입력 라인 |
| **`AMP_I2C_SDA`** | GPIO 21 | SDA (Pin 11) | 앰프 볼륨 및 상태 레지스터 제어 I2C 데이터선 |
| **`AMP_I2C_SCL`** | GPIO 27 | SCL (Pin 12) | 앰프 볼륨 및 상태 레지스터 제어 I2C 클럭선 |

---

## 4. 디버그 및 플래시 업로드 인터페이스 (UART Interface)

* **대상 포트**: `UART_HDR` (디버그 포트 헤더) ↔ `U1` (ESP32-WROOM)

| 넷 이름 (Net Name) | ESP32 핀 (U1) | 디버그 헤더 (UART_HDR) | 역할 및 설명 |
| :--- | :--- | :--- | :--- |
| **`ESP_RXD`** | RXD (Pin 34) | Pin 5 (RXD) | ESP32 수신 (PC 송신 라인 연결) |
| **`ESP_TXD`** | TXD (Pin 35) | Pin 4 (TXD) | ESP32 송신 (PC 수신 라인 연결) |
| **`ESP_IO0`** | GPIO 0 (Pin 25) | Pin 3 (IO0) | 펌웨어 부트로더 진입용 제어 핀 |
| **`ESP_EN`** | EN (Pin 3) | Pin 2 (EN) | ESP32 하드웨어 리셋 핀 |
