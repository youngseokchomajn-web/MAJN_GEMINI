# MAJN PCB #0005 Physical Bring-up & Measurement Ground Truth

* **Test Date:** 2026-10-24
* **Hardware:** MAJN Smart Bassinet Prototype Board PCB #0005
* **Power Source:** 5V 2A Power Bank (Measured 5.02V at USB-C VBUS)

## Summary of Results
1. **Power Rails**:
   - VBUS: 5.02V (Measured at USB-C input)
   - VCC_3V3: 3.20V (Measured at SGM2036 Pin 1 output, within 3.3V ±3% spec)
   - PVDD_12V: 12.00V (MP3426 boost output, FB divider R1=16k / R2=150k + Vref 1.225V nominal)
2. **I2C & Digital Audio**:
   - TAS5805M detected at 7-bit address 0x2C via ESP32 I2C bus (IO21/IO19).
   - Note: PCB #0005 relies on ESP32 internal pull-up (~45kΩ); Rev-C incorporates dedicated 2.2kΩ/4.7kΩ pull-ups for I2C fast mode compliance.
   - State transition to 0x03 (PLAY) verified clean with no bus fault.
   - I2S Clocks: BCLK 1.536 MHz, LRCLK 48.0 kHz verified stable.
3. **Physical Exciter Output**:
   - 2 exciters in series connected to J2.
   - DC Resistance (DCR): Measured 21.6 Ω total (~10.8 Ω per exciter).
   - AC Nominal Impedance: 24.0 Ω (12 Ω x 2 nominal).
   - Driven at 30~65Hz sweep, 0.5 amplitude.
   - Physical bassinet mattress vibration energy verified.
4. **SSOT Discrepancies Identified on PCB #0005**:
   - `D3`: Originally mapped to 3.9kΩ resistor in EasyEDA Pro design files; physical board requires Schottky diode (SS34/MBR140) for boost converter operation.
   - `L1`: Originally mapped to 5.6kΩ resistor in EasyEDA Pro design files; physical board requires power inductor (4.7µH) for boost operation.
   - `U2`: SGMICRO SGM2036D-3.3 (UTDFN-4L, LCSC C700416) confirmed as the actual 3.3V LDO.
