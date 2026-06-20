# Schematic Verification Audit Report

This report compares the active schematic in EasyEDA Pro with the spec in `mcp_design_flow.json`.

## 1. Component Placement Audit

| Designator | Spec Name | LCSC ID | Status | Note |
| --- | --- | --- | --- | --- |
| U1 | ESP32-WROOM-32E | C701342 | **OK** |  |
| U2 | SGM2036-3.3YUDH4/TR LDO | C2827670 | **MISSING** | Requires manual search (`Shift+F`) to download LCSC library. |
| U3 | MPS MP3426 Boost Converter | C162810 | **OK** |  |
| U4 | TI TAS5805M Amplifier | C299105 | **MISSING** | Requires manual search (`Shift+F`) to download LCSC library. |
| U5 | ST LSM6DSOX Accelerometer | C444158 | **MISSING** | Requires manual search (`Shift+F`) to download LCSC library. |
| D1 | SMAJ5.0A TVS Diode | C80145 | **MISSING** | Requires manual search (`Shift+F`) to download LCSC library. |
| D2 | USBLC6-2SC6 TVS Diode | C15309 | **MISSING** | Requires manual search (`Shift+F`) to download LCSC library. |
| USB_C | TYPE-C-16P Female | C165948 | **OK** |  |
| UART_HDR | UART 6Pin Header | C124375 | **OK** |  |
| C1 | MCU Bypass 10uF | C19702 | **OK** |  |
| C2 | MCU Bypass 100nF | C14663 | **OK** |  |
| C3 | LDO Input Cap 10uF | C19702 | **OK** |  |
| C4 | LDO Output Cap 10uF | C19702 | **OK** |  |
| C5 | Boost Input Cap 4.7uF | C19666 | **OK** |  |
| C6 | Boost Output Cap 22uF | C784585 | **OK** |  |
| C7 | Boost Output Cap 22uF | C784585 | **OK** |  |
| C8 | Amp PVDD Cap 10uF | C19702 | **OK** |  |
| C9 | Amp PVDD Cap 10uF | C19702 | **OK** |  |
| C10 | Accel VDD Cap 100nF | C14663 | **OK** |  |
| L1 | Boost Inductor 4.7uH | C168239 | **OK** |  |
| D3 | Boost Schottky Diode | C186407 | **OK** |  |
| R1 | Boost FB Resistor 1 (150k) | C22817 | **OK** |  |
| R2 | Boost FB Resistor 2 (16k) | C22810 | **OK** |  |
| R3 | USB CC1 Pulldown 5.1k | C22803 | **OK** |  |
| R4 | USB CC2 Pulldown 5.1k | C22803 | **OK** |  |
| R5 | ESP EN Pullup 10k | C22548 | **OK** |  |
| C17 | ESP EN RC Cap 100nF | C14663 | **OK** |  |
| R6 | ESP IO0 Pullup 10k | C22548 | **OK** |  |
| C11 | Accel VDDIO Cap 100nF | C14663 | **OK** |  |
| C12 | BST A+ Cap 100nF | C14663 | **OK** |  |
| C13 | BST A- Cap 100nF | C14663 | **OK** |  |
| C14 | BST B+ Cap 100nF | C14663 | **OK** |  |
| C15 | BST B- Cap 100nF | C14663 | **OK** |  |
| J1 | Speaker Output A | C124372 | **OK** |  |
| J2 | Speaker Output B | C124372 | **OK** |  |

## 2. Netlist & Connections Audit

Shows which nets are logically connected based on ports/flags placed at pin stubs.

| Net Name | Total Pins in Spec | Connected Pins | Status | Missing Pins/Connections |
| --- | --- | --- | --- | --- |
| VBUS_5V | 7 | 5 | **PARTIAL** | D1.1 (Component Missing), U2.1 (Component Missing) |
| VCC_3V3 | 12 | 9 | **PARTIAL** | U2.5 (Component Missing), U5.5 (Component Missing), U5.12 (Component Missing) |
| PVDD_12V | 8 | 6 | **PARTIAL** | U4.15 (Component Missing), U4.29 (Component Missing) |
| BOOST_SW | 3 | 3 | **COMPLETE** | None |
| BOOST_FB | 3 | 3 | **COMPLETE** | None |
| BOOST_EN | 2 | 2 | **COMPLETE** | None |
| SPI_MOSI | 2 | 1 | **PARTIAL** | U5.14 (Component Missing) |
| SPI_MISO | 2 | 1 | **PARTIAL** | U5.1 (Component Missing) |
| SPI_SCLK | 2 | 1 | **PARTIAL** | U5.13 (Component Missing) |
| SPI_CS | 2 | 1 | **PARTIAL** | U5.5 (Component Missing) |
| SENSOR_INT1 | 2 | 1 | **PARTIAL** | U5.4 (Component Missing) |
| I2S_BCLK | 2 | 1 | **PARTIAL** | U4.7 (Component Missing) |
| I2S_LRCLK | 2 | 1 | **PARTIAL** | U4.8 (Component Missing) |
| I2S_DIN | 2 | 1 | **PARTIAL** | U4.9 (Component Missing) |
| AMP_I2C_SDA | 2 | 1 | **PARTIAL** | U4.5 (Component Missing) |
| AMP_I2C_SCL | 2 | 1 | **PARTIAL** | U4.6 (Component Missing) |
| AMP_PDN | 2 | 1 | **PARTIAL** | U4.12 (Component Missing) |
| ESP_RXD | 2 | 2 | **COMPLETE** | None |
| ESP_TXD | 2 | 2 | **COMPLETE** | None |
| ESP_IO0 | 3 | 3 | **COMPLETE** | None |
| ESP_EN | 4 | 4 | **COMPLETE** | None |
| USB_CC1 | 2 | 2 | **COMPLETE** | None |
| USB_CC2 | 2 | 2 | **COMPLETE** | None |
| BST_A+ | 2 | 1 | **PARTIAL** | U4.25 (Component Missing) |
| BST_A- | 2 | 1 | **PARTIAL** | U4.22 (Component Missing) |
| BST_B+ | 2 | 1 | **PARTIAL** | U4.18 (Component Missing) |
| BST_B- | 2 | 1 | **PARTIAL** | U4.21 (Component Missing) |
| AMP_OUT_A+ | 3 | 2 | **PARTIAL** | U4.26 (Component Missing) |
| AMP_OUT_A- | 3 | 2 | **PARTIAL** | U4.23 (Component Missing) |
| AMP_OUT_B+ | 3 | 2 | **PARTIAL** | U4.17 (Component Missing) |
| AMP_OUT_B- | 3 | 2 | **PARTIAL** | U4.20 (Component Missing) |
| GND | 28 | 20 | **PARTIAL** | D1.2 (Component Missing), U2.2 (Component Missing), U5.6 (Component Missing), U5.7 (Component Missing), U4.14 (Component Missing), U4.28 (Component Missing), D2.GND (Component Missing), U4.3 (Component Missing) |
