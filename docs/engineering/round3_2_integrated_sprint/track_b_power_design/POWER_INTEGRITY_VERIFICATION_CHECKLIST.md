# Power Integrity & Electrical Test Verification Checklist
## Test Point Protocol, Pass/Fail Thresholds, and Oscilloscope Probing Rules

- **Document Identifier**: `MAJN-R3.2-TRK-B-CHECKLIST-001`
- **Revision**: v1.0
- **Track**: Track B — Power & Circuit Design
- **Date**: 2026-11-06

---

## 1. Safety Directives for Power Integrity Probing

```
========================================================================================
[CRITICAL SAFETY WARNING: BTL OUTPUT PROBING RESTRICTION]
NEVER connect a standard passive single-ended oscilloscope ground clip to any TAS5805M
BTL output pin (OUT_A+, OUT_A-, OUT_B+, OUT_B-)!
Standard oscilloscope probe grounds are tied to mains earth. Connecting the probe ground
to a BTL terminal shorts the high-side or low-side switching FET to earth ground,
resulting in the instantaneous destruction of the TAS5805M silicon.
MANDATORY PROTOCOL: Use high-voltage active differential probes, or two matched 10:1
probes utilizing the oscilloscope Math function (Channel 1 - Channel 2) with probe
ground clips connected strictly to the designated system ground point (TP_GND).
========================================================================================
```

---

## 2. Power Integrity & Circuit Verification Checklist

### TP-01: PVDD 12V Boost Startup & Inrush Behavior
- **Target Net**: `PVDD_12V_BOOST` (at output of MP3426 / $R_{\text{BLEED}}$)
- **Reference Ground**: `TP_GND` (PCB Star Ground)
- **Probe Type**: 10:1 Passive Voltage Probe (500MHz bandwidth, coaxial ground spring)
- **Test Condition**: Cold start, USB-C 5.0V input connected via 1-meter cable.
- **Pass / Fail Acceptance Thresholds**:
  * Steady-State Voltage: $12.17\text{V} \pm 3.0\%$ ($11.80\text{V} \sim 12.53\text{V}$)
  * Power-On Overshoot: $V_{\text{pk}} \le 13.20\text{V}$ (Absolute maximum margin $\ge 16.8\text{V}$ relative to TAS5805M 30V limit)
  * Soft-Start Rise Time: $2.0\text{ms} \le t_{\text{rise}} \le 10.0\text{ms}$ (monotonic rise without plateau or dips)

---

### TP-02: VBUS Input Dynamic Sag & Current Limit
- **Target Net**: `VBUS_5V` (at input of USB-C connector and TVS D1)
- **Reference Ground**: `TP_GND`
- **Measurement Tool**: Oscilloscope Channel 1 (AC coupled ripple / DC sag) + In-line Current Shunt Probe
- **Test Condition**: Transition from Standby to 45Hz infant soothing vibration (scale 0.50) with 2x serial TEAX14C02-8 loads.
- **Pass / Fail Acceptance Thresholds**:
  * Minimum Transient Voltage: $V_{\text{min}} \ge 4.50\text{V}$ under full dynamic load
  * Steady-State Operating Current: $I_{\text{avg}} \le 1.80\text{A}$ ($P \le 9.0\text{W}$)
  * Peak Dynamic Current: $I_{\text{peak}} \le 2.00\text{A}$ ($P_{\text{peak}} \le 10.0\text{W}$)
  * Brownout Margin: Voltage above AP2112K dropout threshold ($3.3\text{V} + 0.25\text{V} = 3.55\text{V}$) must be $\ge 950\text{mV}$.

---

### TP-03: BTL Audio Differential Output & Back-EMF Clamping
- **Target Net**: `AMP_OUT_A+` vs `AMP_OUT_A-`, and `AMP_OUT_B+` vs `AMP_OUT_B-`
- **Probe Type**: High-speed active differential probe ($\ge 200\text{MHz}$)
- **Test Condition**: 45Hz vibration driven at max amplitude, followed by an immediate emergency mute / shutdown (`PDN = LOW`).
- **Pass / Fail Acceptance Thresholds**:
  * Differential Voltage Swing: $V_{\text{diff,pk}} \le 11.5\text{V}$
  * Back-EMF Single-Ended Clamp Voltage: Each pin must remain bounded within:
    $$-0.50\text{V} \le V_{\text{pin}} \le V_{\text{PVDD}} + 0.50\text{V}$$
    (Verified by Schottky diodes D4~D7 conducting clamping current)
  * THD+N (1kHz audio test tone): $\le 0.15\%$ at 1W into $16\Omega$.

---

### TP-04: MP3426 SW Switching Node Ringing & Slew Rate
- **Target Net**: `BOOST_SW` (Pin 13/14 of MP3426 / Anode of SS34 diode)
- **Reference Ground**: Local PGND via ultra-short spring tip ($\le 5\text{mm}$)
- **Probe Type**: 10:1 Passive Probe ($\ge 500\text{MHz}$), coaxial connection
- **Test Condition**: Heavy load ($P_{\text{audio}} = 3.5\text{W}$), continuous conduction mode (CCM).
- **Pass / Fail Acceptance Thresholds**:
  * Peak Voltage: $V_{\text{SW,pk}} \le 18.0\text{V}$ (MP3426 switch breakdown is 22.0V; required design margin $\ge 4.0\text{V}$)
  * Switching Frequency: $1.20\text{MHz} \le f_{\text{sw}} \le 1.30\text{MHz}$ (verified with R9 = 82kΩ)
  * Snubber Effect: High-frequency ringing damped to $<10\%$ within 3 cycles.

---

### TP-05: Inductor Dynamic Current Waveform & Saturation Verification
- **Target Net**: `L1` series current
- **Measurement Tool**: High-frequency clip-on current probe (Tektronix TCP0030A or current shunt insertion at $R_{\text{ISO1}}$)
- **Test Condition**: Worst-case low input $V_{\text{in}} = 4.50\text{V}$, maximum vibration burst.
- **Pass / Fail Acceptance Thresholds**:
  * Inductor Current Peak: $I_{L,\text{pk}} \le 2.65\text{A}$ (nominal) / $\le 3.10\text{A}$ (transient burst)
  * Inductor Saturation Headroom: $I_{\text{sat}} - I_{L,\text{pk}} \ge 0.50\text{A}$ ($I_{\text{sat}} = 3.60\text{A}$ for SWPA6045S-4R7; $\ge 1.9\text{A}$ if upgraded to SWPA8040S-4R7 with $I_{\text{sat}} = 5.0\text{A}$)
  * Linearity: Inductor current slope must remain linear ($\Delta I / \Delta t = \text{const}$); zero downward concave curvature during switch-on time.

---

### TP-06: 3.3V LDO Rail Stability Under Wi-Fi TX Burst
- **Target Net**: `VCC_3V3` (Output of AP2112K-3.3, decoupling at ESP32 Pin 2)
- **Reference Ground**: Local digital GND
- **Probe Type**: 1:1 or 10:1 AC-coupled probe with 50Ω termination
- **Test Condition**: Continuous BLE advertising + Wi-Fi 802.11b TX burst mode ($P_{\text{out}} = +20\text{dBm}$).
- **Pass / Fail Acceptance Thresholds**:
  * DC Regulation: $3.20\text{V} \le V_{\text{CC3V3}} \le 3.40\text{V}$
  * Peak-to-Peak Transient Ripple: $\Delta V_{\text{pk-pk}} \le 100\text{mV}$
  * Absolute Minimum Valley Voltage: $V_{\text{min}} \ge 3.10\text{V}$ (ESP32 brownout threshold is $2.80\text{V}$; margin $\ge 300\text{mV}$).

---

### TP-07: USB Type-C CC Configuration & Hot-Plug Inrush
- **Target Net**: `USB_CC1`, `USB_CC2`
- **Reference Ground**: `TP_GND`
- **Test Condition**: Connecting to 5V/3A USB-C native power supply and C-to-C cable.
- **Pass / Fail Acceptance Thresholds**:
  * Pull-down Resistance: $5.1\text{k}\Omega \pm 1\%$ verified by unpowered DMM measurement
  * Advertised Voltage: $0.20\text{V} \le V_{\text{CC}} \le 0.80\text{V}$ (confirming standard 500mA / 1.5A / 3.0A negotiation)
  * Hot-Plug Inrush Voltage Spike on VBUS: $V_{\text{VBUS,pk}} \le 5.75\text{V}$ (clamped by SMAJ5.0A TVS).

---

### TP-08: Thermal Equilibrium Saturation (30-Minute Soak Test)
- **Target Components**: U3 (MP3426), U4 (TAS5805M), U2 (AP2112K), L1, Bassinet Enclosure
- **Measurement Tool**: Calibrated FLIR thermal imaging camera + calibrated K-type thermocouples
- **Test Condition**: Fully enclosed housing, ambient temperature $T_{\text{amb}} = 25^\circ\text{C}$ and $40^\circ\text{C}$ chamber, 30 minutes continuous 45Hz vibration at rated infant soothing amplitude.
- **Pass / Fail Acceptance Thresholds**:
  * MP3426 IC Case Temperature: $T_{\text{case}} \le 85^\circ\text{C}$ ($T_j \le 105^\circ\text{C}$, limit $125^\circ\text{C}$)
  * TAS5805M IC Case Temperature: $T_{\text{case}} \le 75^\circ\text{C}$ ($T_j \le 95^\circ\text{C}$, limit $125^\circ\text{C}$)
  * AP2112K LDO Case Temperature: $T_{\text{case}} \le 70^\circ\text{C}$ ($T_j \le 90^\circ\text{C}$, limit $125^\circ\text{C}$)
  * Inductor L1 Surface Temperature: $T_{\text{case}} \le 75^\circ\text{C}$
  * Bassinet Plastic Housing Exterior (Touch Area): $T_{\text{touch}} \le 40.0^\circ\text{C}$ (Strict compliance with IEC 62368-1 infant product limit).
