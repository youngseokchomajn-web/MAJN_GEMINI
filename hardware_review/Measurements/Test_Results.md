# MAJN PCB #0005 Physical Bring-up & Measurement Ground Truth

* **Test Date:** 2026-10-24
* **Hardware:** MAJN Smart Bassinet Prototype Board PCB #0005
* **Power Source:** 5V 2A Power Bank (Measured 5.02V)

## Summary of Results
1. **Power Rails**:
   - VBUS (5.02V) -> VCC_3V3 (3.20V) -> PVDD_12V (12.00V) all verified within specification.
2. **I2C & Digital Audio**:
   - TAS5805M detected at 7-bit address 0x2C. State transition to 0x03 (PLAY) verified clean.
   - I2S Clocks: BCLK 1.536 MHz, LRCLK 48.0 kHz stable.
3. **Physical Exciter Output**:
   - 2 exciters in series (24.8 ohm) driven at 50Hz, 0.5 amplitude.
   - Physical mattress pad vibration energy clearly confirmed.
