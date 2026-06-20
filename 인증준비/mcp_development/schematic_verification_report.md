# EasyEDA Schematic S4 Verification Report
Date: 2026-06-19  
Schematic Page: P1  
Spec Version: 1.2.0 (Majung_Smart_Bassinet_v1.1)  

## Verification Summary
- **총 검증 대상 (스펙 연결 개수)**: 145개
- **정상 결선 완료 (OK)**: 152개
- **미결선/누락 (ERR)**: 0개
- **오결선/네트 불일치 (ERR)**: 0개
- **스펙 외 추가 결선 (WARN)**: 0개

> [!NOTE]
> **SUCCESS**: 모든 스펙상 연결이 회로도 상에 기하학적으로 100% 완벽하게 결선되어 있습니다!

## 세부 오류 및 경고 목록
- 발견된 오류가 없습니다.

## 모든 연결 실측 테이블
| 부품 | 스펙 핀 | 매칭 심볼 핀 | 예상 네트 | 상태 | 비고 |
|---|---|---|---|---|---|
| USB_C | VBUS | A4B9(VBUS) | VBUS_5V | OK | |
| USB_C | VBUS | B4A9(VBUS) | VBUS_5V | OK | |
| D1 | 1 | 1(C) | VBUS_5V | OK | |
| U2 | 1 | 1(OUT) | VBUS_5V | OK | |
| C3 | 1 | 1(1) | VBUS_5V | OK | |
| U3 | 3 | 3(VIN) | VBUS_5V | OK | |
| C5 | 1 | 1(1) | VBUS_5V | OK | |
| L1 | 1 | 1(1) | VBUS_5V | OK | |
| U2 | 5 | 5(EP) | VCC_3V3 | OK | |
| C4 | 1 | 1(1) | VCC_3V3 | OK | |
| U1 | 3V3 | 2(3V3) | VCC_3V3 | OK | |
| C1 | 1 | 1(1) | VCC_3V3 | OK | |
| C2 | 1 | 1(1) | VCC_3V3 | OK | |
| U5 | 5 | 5(VDDIO) | VCC_3V3 | OK | |
| U5 | 9 | 9(INT2) | VCC_3V3 | OK | |
| C10 | 1 | 1(1) | VCC_3V3 | OK | |
| C11 | 1 | 1(1) | VCC_3V3 | OK | |
| UART_HDR | 1 | 1(1) | VCC_3V3 | OK | |
| R5 | 1 | 1(1) | VCC_3V3 | OK | |
| R6 | 1 | 1(1) | VCC_3V3 | OK | |
| U4 | 2 | 2(DVDD) | VCC_3V3 | OK | |
| C18 | 1 | 1(1) | VCC_3V3 | OK | |
| R7 | 2 | 2(2) | VCC_3V3 | OK | |
| R8 | 2 | 2(2) | VCC_3V3 | OK | |
| D3 | 2 | 2(2) | PVDD_12V | OK | |
| C6 | 1 | 1(1) | PVDD_12V | OK | |
| C7 | 1 | 1(1) | PVDD_12V | OK | |
| R1 | 1 | 1(1) | PVDD_12V | OK | |
| U4 | 15 | 15(PVDD) | PVDD_12V | OK | |
| U4 | 16 | 16(PVDD) | PVDD_12V | OK | |
| U4 | 27 | 27(PVDD) | PVDD_12V | OK | |
| U4 | 28 | 28(PVDD) | PVDD_12V | OK | |
| C8 | 1 | 1(1) | PVDD_12V | OK | |
| C9 | 1 | 1(1) | PVDD_12V | OK | |
| U3 | 4 | 4(SW) | BOOST_SW | OK | |
| U3 | 5 | 5(SW) | BOOST_SW | OK | |
| U3 | 6 | 6(SW) | BOOST_SW | OK | |
| L1 | 2 | 2(2) | BOOST_SW | OK | |
| D3 | 1 | 1(1) | BOOST_SW | OK | |
| U3 | 13 | 13(FB) | BOOST_FB | OK | |
| R1 | 2 | 2(2) | BOOST_FB | OK | |
| R2 | 1 | 1(1) | BOOST_FB | OK | |
| U1 | GPIO4 | 26(IO4) | BOOST_EN | OK | |
| U3 | 2 | 2(EN) | BOOST_EN | OK | |
| U1 | GPIO23 | 37(IO23) | SPI_MOSI | OK | |
| U5 | 14 | 14(SDA) | SPI_MOSI | OK | |
| U1 | GPIO19 | 31(IO19) | SPI_MISO | OK | |
| U5 | 1 | 1(SDO/SA0) | SPI_MISO | OK | |
| U1 | GPIO18 | 30(IO18) | SPI_SCLK | OK | |
| U5 | 13 | 13(SCL) | SPI_SCLK | OK | |
| U1 | GPIO5 | 29(IO5) | SPI_CS | OK | |
| U5 | 12 | 12(CS) | SPI_CS | OK | |
| U5 | 4 | 4(INT1) | SENSOR_INT1 | OK | |
| U1 | GPIO34 | 6(IO34) | SENSOR_INT1 | OK | |
| U1 | GPIO26 | 11(IO26) | I2S_BCLK | OK | |
| U4 | 7 | 7(SCLK) | I2S_BCLK | OK | |
| U1 | GPIO25 | 10(IO25) | I2S_LRCLK | OK | |
| U4 | 6 | 6(LRCLK) | I2S_LRCLK | OK | |
| U1 | GPIO22 | 36(IO22) | I2S_DIN | OK | |
| U4 | 8 | 8(SDIN) | I2S_DIN | OK | |
| U1 | GPIO21 | 33(IO21) | AMP_I2C_SDA | OK | |
| U4 | 10 | 10(SDA) | AMP_I2C_SDA | OK | |
| R7 | 1 | 1(1) | AMP_I2C_SDA | OK | |
| U1 | GPIO27 | 12(IO27) | AMP_I2C_SCL | OK | |
| U4 | 11 | 11(SCL) | AMP_I2C_SCL | OK | |
| R8 | 1 | 1(1) | AMP_I2C_SCL | OK | |
| U1 | GPIO15 | 23(IO15) | AMP_PDN | OK | |
| U4 | 12 | 12(PDN#) | AMP_PDN | OK | |
| U4 | 13 | 13(AVDD) | AVDD | OK | |
| C19 | 1 | 1(1) | AVDD | OK | |
| U4 | 4 | 4(VR_DIG) | VR_DIG | OK | |
| C20 | 1 | 1(1) | VR_DIG | OK | |
| U1 | RXD | 34(RXD0) | ESP_RXD | OK | |
| UART_HDR | 5 | 5(5) | ESP_RXD | OK | |
| U1 | TXD | 35(TXD0) | ESP_TXD | OK | |
| UART_HDR | 4 | 4(4) | ESP_TXD | OK | |
| U1 | GPIO0 | 25(IO0) | ESP_IO0 | OK | |
| UART_HDR | 3 | 3(3) | ESP_IO0 | OK | |
| R6 | 2 | 2(2) | ESP_IO0 | OK | |
| U1 | EN | 3(EN) | ESP_EN | OK | |
| UART_HDR | 2 | 2(2) | ESP_EN | OK | |
| R5 | 2 | 2(2) | ESP_EN | OK | |
| C17 | 1 | 1(1) | ESP_EN | OK | |
| USB_C | CC1 | A5(CC1) | USB_CC1 | OK | |
| R3 | 1 | 1(1) | USB_CC1 | OK | |
| USB_C | CC2 | B5(CC2) | USB_CC2 | OK | |
| R4 | 1 | 1(1) | USB_CC2 | OK | |
| U4 | 25 | 25(BST_A+) | BST_A+ | OK | |
| C12 | 2 | 2(2) | BST_A+ | OK | |
| U4 | 22 | 22(BST_A-) | BST_A- | OK | |
| C13 | 2 | 2(2) | BST_A- | OK | |
| U4 | 18 | 18(BST_B+) | BST_B+ | OK | |
| C14 | 2 | 2(2) | BST_B+ | OK | |
| U4 | 21 | 21(BST_B-) | BST_B- | OK | |
| C15 | 2 | 2(2) | BST_B- | OK | |
| U4 | 26 | 26(OUT_A+) | AMP_OUT_A+ | OK | |
| C12 | 1 | 1(1) | AMP_OUT_A+ | OK | |
| J1 | 1 | 1(1) | AMP_OUT_A+ | OK | |
| J1 | 1 | 10(10) | AMP_OUT_A+ | OK | |
| U4 | 23 | 23(OUT_A-) | AMP_OUT_A- | OK | |
| C13 | 1 | 1(1) | AMP_OUT_A- | OK | |
| J1 | 2 | 2(2) | AMP_OUT_A- | OK | |
| U4 | 17 | 17(OUT_B+) | AMP_OUT_B+ | OK | |
| C14 | 1 | 1(1) | AMP_OUT_B+ | OK | |
| J2 | 1 | 1(1) | AMP_OUT_B+ | OK | |
| J2 | 1 | 10(10) | AMP_OUT_B+ | OK | |
| U4 | 20 | 20(OUT_B-) | AMP_OUT_B- | OK | |
| C15 | 1 | 1(1) | AMP_OUT_B- | OK | |
| J2 | 2 | 2(2) | AMP_OUT_B- | OK | |
| USB_C | GND | A1B12(GND) | GND | OK | |
| USB_C | GND | B1A12(GND) | GND | OK | |
| D1 | 2 | 2(A) | GND | OK | |
| U2 | 2 | 2(GND) | GND | OK | |
| C3 | 2 | 2(2) | GND | OK | |
| C4 | 2 | 2(2) | GND | OK | |
| U3 | 8 | 8(PGND) | GND | OK | |
| U3 | 9 | 9(PGND) | GND | OK | |
| U3 | 10 | 10(PGND) | GND | OK | |
| U3 | 11 | 11(AGND) | GND | OK | |
| U3 | 15 | 15(EP) | GND | OK | |
| C5 | 2 | 2(2) | GND | OK | |
| C6 | 2 | 2(2) | GND | OK | |
| C7 | 2 | 2(2) | GND | OK | |
| R2 | 2 | 2(2) | GND | OK | |
| U1 | GND | 39(GND) | GND | OK | |
| U1 | GND | 38(GND) | GND | OK | |
| U1 | GND | 15(GND) | GND | OK | |
| U1 | GND | 1(GND) | GND | OK | |
| C1 | 2 | 2(2) | GND | OK | |
| C2 | 2 | 2(2) | GND | OK | |
| U5 | 6 | 6(GND) | GND | OK | |
| U5 | 7 | 7(GND) | GND | OK | |
| U5 | 8 | 8(VDD) | GND | OK | |
| C10 | 2 | 2(2) | GND | OK | |
| C11 | 2 | 2(2) | GND | OK | |
| U4 | 1 | 1(DGND) | GND | OK | |
| U4 | 3 | 3(ADR/FAULT#) | GND | OK | |
| U4 | 5 | 5(DGND) | GND | OK | |
| U4 | 14 | 14(AGND) | GND | OK | |
| U4 | 19 | 19(PGND) | GND | OK | |
| U4 | 24 | 24(PGND) | GND | OK | |
| U4 | 29 | 29(EP) | GND | OK | |
| C8 | 2 | 2(2) | GND | OK | |
| C9 | 2 | 2(2) | GND | OK | |
| D2 | GND | 2(GND) | GND | OK | |
| UART_HDR | 6 | 6(6) | GND | OK | |
| R3 | 2 | 2(2) | GND | OK | |
| R4 | 2 | 2(2) | GND | OK | |
| C17 | 2 | 2(2) | GND | OK | |
| C18 | 2 | 2(2) | GND | OK | |
| C19 | 2 | 2(2) | GND | OK | |
| C20 | 2 | 2(2) | GND | OK | |