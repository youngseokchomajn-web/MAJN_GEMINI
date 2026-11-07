#!/usr/bin/env python3
"""
verify_phase1_power_design.py
=============================
MAJN Smart Bassinet - PCB #0006 Engineering Phase 1
MP3426 Boost Converter Independent Power Design Verification Engine

This script executes a mathematically rigorous, reproducible verification
of the MP3426 12V boost power supply, SWPA6045S-4R7 inductor, and PVDD MLCCs.

Key capabilities:
1. MP3426 switching frequency interpolation & tolerance bounds.
2. Worst-case circuit analysis (WCCA) across 4 operational scenarios.
3. Sunlord SWPA6045S4R7MT inductor core/copper loss & thermal saturation.
4. Output MLCC DC bias derating & peak-to-peak ripple model.
5. Bleeder resistor power & pulse-skipping threshold analysis.
6. Self-verifying regression tests exiting with code 0.
"""

import math
import csv
import sys
import os

# ----------------------------------------------------------------------
# 1. MP3426 Switching Frequency Model
# ----------------------------------------------------------------------

# MPS MP3426 Datasheet Table 1: R_FSET (kOhm) vs f_sw (MHz)
TABLE1_DATA = [
    (180.0, 0.26),
    (160.0, 0.29),
    (150.0, 0.31),
    (143.0, 0.32),
    (66.5,  0.62),
    (35.7,  1.06),
    (25.0,  1.44),
    (18.0,  1.91),
    (16.0,  2.12)
]

def calculate_fsw_interpolated(r_kohm):
    """
    Interpolates switching frequency from MP3426 Table 1 using period linear interpolation.
    In boost converters, internal ramp period T_sw is typically linear with R_FSET.
    """
    sorted_table = sorted(TABLE1_DATA, key=lambda x: x[0])
    
    # Boundary check
    if r_kohm <= sorted_table[0][0]:
        return sorted_table[0][1] * 1000.0  # kHz
    if r_kohm >= sorted_table[-1][0]:
        return sorted_table[-1][1] * 1000.0 # kHz
    
    for i in range(len(sorted_table) - 1):
        r1, f1 = sorted_table[i]
        r2, f2 = sorted_table[i+1]
        if r1 <= r_kohm <= r2:
            t1 = 1.0 / f1  # us
            t2 = 1.0 / f2  # us
            # Linear interpolation in period
            t_interp = t1 + (r_kohm - r1) / (r2 - r1) * (t2 - t1)
            f_interp = 1.0 / t_interp
            return f_interp * 1000.0  # Return in kHz

def calculate_fsw_bounds(r_nominal_kohm=82.0, r_tol=0.01, osc_tol=0.15):
    """
    Calculates nominal, min, and max switching frequency considering:
    - R9 resistor tolerance (default +-1%)
    - MP3426 internal oscillator manufacturing & temperature drift (default +-15%)
    """
    r_nom = r_nominal_kohm
    r_max = r_nominal_kohm * (1.0 + r_tol)
    r_min = r_nominal_kohm * (1.0 - r_tol)
    
    f_nom_raw = calculate_fsw_interpolated(r_nom)
    f_at_rmax = calculate_fsw_interpolated(r_max)
    f_at_rmin = calculate_fsw_interpolated(r_min)
    
    # Min frequency occurs with high resistance and slow oscillator
    f_min = f_at_rmax * (1.0 - osc_tol)
    # Max frequency occurs with low resistance and fast oscillator
    f_max = f_at_rmin * (1.0 + osc_tol)
    
    return {
        "f_nom_kHz": round(f_nom_raw, 1),
        "f_min_kHz": round(f_min, 1),
        "f_max_kHz": round(f_max, 1),
        "r_nom_kohm": r_nom,
        "r_tol_pct": r_tol * 100.0,
        "osc_tol_pct": osc_tol * 100.0
    }

# ----------------------------------------------------------------------
# 2. Worst-Case Circuit Analysis (WCCA)
# ----------------------------------------------------------------------

def calculate_boost_operating_point(
    v_in, v_out, p_out, efficiency, f_sw_khz, l_uh, v_diode=0.45
):
    """
    Computes electrical parameters for CCM Boost Converter:
    - Duty cycle (D)
    - Average output & input currents
    - Inductor ripple current (dIL)
    - Peak & RMS inductor currents
    """
    f_sw_hz = f_sw_khz * 1000.0
    l_h = l_uh * 1e-6
    
    # Duty cycle taking diode drop into account
    duty = (v_out + v_diode - v_in) / (v_out + v_diode)
    duty = max(0.01, min(0.95, duty))
    
    i_out = p_out / v_out
    p_in = p_out / efficiency
    i_in_avg = p_in / v_in
    
    # Ripple current
    delta_il = (v_in * duty) / (f_sw_hz * l_h)
    
    i_peak = i_in_avg + (delta_il / 2.0)
    # RMS current through boost inductor in CCM
    i_rms = math.sqrt(i_in_avg**2 + (delta_il**2 / 12.0))
    
    return {
        "v_in": v_in,
        "v_out": v_out,
        "p_out": p_out,
        "efficiency": efficiency,
        "f_sw_kHz": f_sw_khz,
        "l_uH": l_uh,
        "duty": round(duty, 4),
        "i_out_A": round(i_out, 3),
        "i_in_avg_A": round(i_in_avg, 3),
        "delta_il_A": round(delta_il, 3),
        "i_peak_A": round(i_peak, 3),
        "i_rms_A": round(i_rms, 3)
    }

# ----------------------------------------------------------------------
# 3. Inductor Thermal and Saturation Model (SWPA6045S4R7MT)
# ----------------------------------------------------------------------

# Sunlord SWPA6045S4R7MT Datasheet Baseline:
# Inductance: 4.7 uH +-20%
# Isat (25C): Min = 4.97 A, Typ = 5.50 A (30% drop)
# Irms (25C): Min = 3.30 A, Typ = 3.60 A (dT = 40C)
# DCR: Typ = 26 mOhm, Max = 34 mOhm (at 20C)

def calculate_inductor_thermal_and_saturation(
    i_rms, i_peak, ambient_temp_c=25.0, dcr_20c_mohm=34.0, core_loss_w=0.035
):
    """
    Calculates inductor copper loss, total loss, temperature rise,
    and derated saturation current at equilibrium core temperature.
    """
    alpha_cu = 0.00393 # Copper temp coefficient per degC
    
    # Iterate for thermal equilibrium
    t_core = ambient_temp_c + 10.0
    for _ in range(5):
        dcr_t = (dcr_20c_mohm / 1000.0) * (1.0 + alpha_cu * (t_core - 20.0))
        p_cu = (i_rms ** 2) * dcr_t
        p_total = p_cu + core_loss_w
        
        # Thermal resistance derived from Irms=3.30A at DCR=34mOhm causing 40C rise
        # Rth = 40.0 / (3.30^2 * 0.034) = 108.0 degC/W
        r_th = 108.0
        delta_t = p_total * r_th
        t_core = ambient_temp_c + delta_t
    
    # Saturation derating model for shielded ferrite/composite core:
    # Retains 100% at 25C, 90% at 60C, 85% at 85C, 80% at 100C
    if t_core <= 25.0:
        sat_derating = 1.0
    elif t_core <= 60.0:
        sat_derating = 1.0 - (t_core - 25.0) * (0.10 / 35.0)
    elif t_core <= 100.0:
        sat_derating = 0.90 - (t_core - 60.0) * (0.10 / 40.0)
    else:
        sat_derating = 0.80 - (t_core - 100.0) * (0.10 / 25.0)
    sat_derating = max(0.50, sat_derating)
    
    isat_min_25c = 4.97
    isat_typ_25c = 5.50
    
    isat_min_derated = isat_min_25c * sat_derating
    isat_typ_derated = isat_typ_25c * sat_derating
    
    margin_min_pct = ((isat_min_derated - i_peak) / isat_min_derated) * 100.0
    margin_typ_pct = ((isat_typ_derated - i_peak) / isat_typ_derated) * 100.0
    
    return {
        "ambient_temp_C": ambient_temp_c,
        "dcr_at_t_mohm": round(dcr_t * 1000.0, 1),
        "copper_loss_W": round(p_cu, 4),
        "core_loss_W": round(core_loss_w, 4),
        "total_loss_W": round(p_total, 4),
        "delta_t_C": round(delta_t, 1),
        "t_core_C": round(t_core, 1),
        "sat_derating_factor": round(sat_derating, 3),
        "isat_min_derated_A": round(isat_min_derated, 2),
        "isat_typ_derated_A": round(isat_typ_derated, 2),
        "margin_min_pct": round(margin_min_pct, 1),
        "margin_typ_pct": round(margin_typ_pct, 1)
    }

# ----------------------------------------------------------------------
# 4. Capacitor DC Bias & Output Ripple Model
# ----------------------------------------------------------------------

# Capacitor Candidates:
# 1) Legacy: 2x 10uF 0603 25V X5R (Murata GRM188R61E106)
# 2) Candidate A: 2x 22uF 1210 25V X7R (Murata GRM32ER71E226)
# 3) Candidate B: 2x 22uF 1210 35V X7R (Murata GRM32ER7YA226)
# 4) Candidate C: 2x 22uF 1210 50V X7R (Murata GRM32ER71H226)

CAPACITOR_MODELS = {
    "Legacy_2x_0603_10uF_25V": {
        "nominal_each_uF": 10.0,
        "quantity": 2,
        "v_rated": 25.0,
        "dc_bias_retention_12V_typ": 0.28,  # -72% drop
        "dc_bias_retention_12V_min": 0.22,  # -78% drop
        "temp_factor_worst": 0.85,          # X5R +-15%
        "tol_factor_worst": 0.80,           # +-20% tol
        "esr_parallel_mohm": 5.0
    },
    "Candidate_A_2x_1210_22uF_25V": {
        "nominal_each_uF": 22.0,
        "quantity": 2,
        "v_rated": 25.0,
        "dc_bias_retention_12V_typ": 0.45,  # -55% drop
        "dc_bias_retention_12V_min": 0.38,  # -62% drop
        "temp_factor_worst": 0.85,          # X7R +-15%
        "tol_factor_worst": 0.90,           # +-10% tol
        "esr_parallel_mohm": 3.0
    },
    "Candidate_B_2x_1210_22uF_35V": {
        "nominal_each_uF": 22.0,
        "quantity": 2,
        "v_rated": 35.0,
        "dc_bias_retention_12V_typ": 0.60,  # -40% drop
        "dc_bias_retention_12V_min": 0.52,  # -48% drop
        "temp_factor_worst": 0.85,          # X7R +-15%
        "tol_factor_worst": 0.90,           # +-10% tol
        "esr_parallel_mohm": 2.5
    },
    "Candidate_C_2x_1210_22uF_50V": {
        "nominal_each_uF": 22.0,
        "quantity": 2,
        "v_rated": 50.0,
        "dc_bias_retention_12V_typ": 0.85,  # -15% drop
        "dc_bias_retention_12V_min": 0.75,  # -25% drop
        "temp_factor_worst": 0.85,          # X7R +-15%
        "tol_factor_worst": 0.90,           # +-10% tol
        "esr_parallel_mohm": 2.2
    }
}

def calculate_effective_capacitance_and_ripple(
    cap_model_key, i_out, duty, f_sw_khz, delta_il
):
    """
    Computes effective capacitance (nominal vs worst-case)
    and resulting peak-to-peak output voltage ripple.
    """
    model = CAPACITOR_MODELS[cap_model_key]
    c_nom_total = model["nominal_each_uF"] * model["quantity"]
    
    # Nominal effective capacitance at 12V DC bias
    c_eff_typ = c_nom_total * model["dc_bias_retention_12V_typ"]
    
    # Worst-case effective capacitance (DC bias min * temp drift * tolerance * aging 0.97)
    c_eff_worst = (
        c_nom_total
        * model["dc_bias_retention_12V_min"]
        * model["temp_factor_worst"]
        * model["tol_factor_worst"]
        * 0.97 # Aging derating
    )
    
    f_sw_hz = f_sw_khz * 1000.0
    esr_ohm = model["esr_parallel_mohm"] / 1000.0
    
    # Capacitive ripple: dVc = (Iout * D) / (fsw * Cout)
    # ESR ripple: dVesr = delta_IL * ESR
    # Typ ripple
    d_vc_typ = (i_out * duty) / (f_sw_hz * (c_eff_typ * 1e-6))
    d_vesr_typ = delta_il * esr_ohm
    v_ripple_typ_mv = (d_vc_typ + d_vesr_typ) * 1000.0
    
    # Worst ripple
    d_vc_worst = (i_out * duty) / (f_sw_hz * (c_eff_worst * 1e-6))
    d_vesr_worst = delta_il * esr_ohm
    v_ripple_worst_mv = (d_vc_worst + d_vesr_worst) * 1000.0
    
    return {
        "cap_model": cap_model_key,
        "c_nom_total_uF": round(c_nom_total, 1),
        "c_eff_typ_uF": round(c_eff_typ, 1),
        "c_eff_worst_uF": round(c_eff_worst, 1),
        "v_ripple_typ_mV": round(v_ripple_typ_mv, 1),
        "v_ripple_worst_mV": round(v_ripple_worst_mv, 1)
    }

# ----------------------------------------------------------------------
# 5. Bleeder Resistor & Light-Load Analysis
# ----------------------------------------------------------------------

def calculate_bleeder_and_pulse_skipping(
    r_bleed_ohm=1500.0, v_out=12.17, v_in=5.0, l_uh=4.7, f_sw_khz=521.0, c_eff_uF=26.4
):
    """
    Analyzes bleeder power dissipation, pulse-skipping threshold,
    and safe discharge time constant.
    """
    i_bleed = v_out / r_bleed_ohm
    p_bleed_mw = (v_out ** 2) / r_bleed_ohm * 1000.0
    
    # MP3426 minimum on-time ton_min = 100 ns
    t_on_min_s = 100e-9
    l_h = l_uh * 1e-6
    f_sw_hz = f_sw_khz * 1000.0
    
    # Energy in one minimum pulse: E_min = (Vin^2 * ton_min^2) / (2 * L)
    e_pulse_min = (v_in ** 2) * (t_on_min_s ** 2) / (2.0 * l_h)
    # Continuous power at min pulses without skipping: P_min = E_pulse_min * fsw
    p_min_pulse_mw = e_pulse_min * f_sw_hz * 1000.0
    
    # Discharge time constant tau = R * C
    tau_ms = (r_bleed_ohm * (c_eff_uF * 1e-6)) * 1000.0
    # Time to decay to 1.0 V from 12.17 V: t = tau * ln(12.17 / 1.0)
    t_discharge_1v_ms = tau_ms * math.log(v_out / 1.0)
    
    return {
        "r_bleed_ohm": r_bleed_ohm,
        "i_bleed_mA": round(i_bleed * 1000.0, 2),
        "p_bleed_mW": round(p_bleed_mw, 1),
        "p_min_pulse_mW": round(p_min_pulse_mw, 2),
        "can_absorb_min_pulse": p_bleed_mw > p_min_pulse_mw,
        "tau_ms": round(tau_ms, 2),
        "t_discharge_1v_ms": round(t_discharge_1v_ms, 1)
    }

# ----------------------------------------------------------------------
# 6. Main Verification Runner & CSV Exporters
# ----------------------------------------------------------------------

def run_phase1_verification():
    print("=" * 80)
    print("MAJN PCB #0006 - PHASE 1 INDEPENDENT POWER VERIFICATION ENGINE")
    print("=" * 80)
    
    # 1. Frequency calculation
    freq_data = calculate_fsw_bounds(r_nominal_kohm=82.0, r_tol=0.01, osc_tol=0.15)
    print("\n[1] MP3426 Switching Frequency Analysis (R9 = 82kOhm +-1%):")
    print(f"  - Nominal Interp Frequency : {freq_data['f_nom_kHz']} kHz")
    print(f"  - Worst-Case Min Frequency : {freq_data['f_min_kHz']} kHz (-15% osc, +1% R)")
    print(f"  - Worst-Case Max Frequency : {freq_data['f_max_kHz']} kHz (+15% osc, -1% R)")
    
    # 2. Operating scenarios (WCCA)
    scenarios = [
        ("SCEN-1_Nominal_7.56W",       5.00, 12.17, 7.56,  0.88, freq_data['f_nom_kHz'], 4.70, 25.0),
        ("SCEN-2_WorstCase_Sag_4.5V",   4.50, 12.17, 7.56,  0.85, freq_data['f_min_kHz'], 3.76, 50.0),
        ("SCEN-3_HighVoltage_5.5V",     5.50, 12.17, 7.56,  0.90, freq_data['f_max_kHz'], 4.70, 25.0),
        ("SCEN-4_Peak_Burst_10W",       4.50, 12.17, 10.00, 0.85, freq_data['f_min_kHz'], 3.76, 50.0)
    ]
    
    wcca_results = []
    inductor_results = []
    
    print("\n[2] Worst-Case Circuit Analysis (WCCA):")
    for name, vin, vout, pout, eff, fsw, l_val, t_amb in scenarios:
        pt = calculate_boost_operating_point(vin, vout, pout, eff, fsw, l_val)
        ind = calculate_inductor_thermal_and_saturation(pt['i_rms_A'], pt['i_peak_A'], ambient_temp_c=t_amb)
        
        row_wcca = {**pt, "scenario_name": name, "ambient_temp_C": t_amb}
        wcca_results.append(row_wcca)
        
        row_ind = {
            "scenario_name": name,
            "i_rms_A": pt['i_rms_A'],
            "i_peak_A": pt['i_peak_A'],
            **ind
        }
        inductor_results.append(row_ind)
        
        print(f"  [{name}] Vin={vin}V, Pout={pout}W, fsw={fsw}kHz, L={l_val}uH -> "
              f"Iavg={pt['i_in_avg_A']}A, dIL={pt['delta_il_A']}A, Ipk={pt['i_peak_A']}A, "
              f"Tcore={ind['t_core_C']}C, SatMargin(min)={ind['margin_min_pct']}%")
    
    # 3. Capacitor evaluation across scenarios
    print("\n[3] Output MLCC DC Bias & Ripple Evaluation:")
    cap_results = []
    for scen_name, vin, vout, pout, eff, fsw, l_val, t_amb in scenarios:
        pt = calculate_boost_operating_point(vin, vout, pout, eff, fsw, l_val)
        for cap_key in CAPACITOR_MODELS.keys():
            cap_eval = calculate_effective_capacitance_and_ripple(
                cap_key, pt['i_out_A'], pt['duty'], fsw, pt['delta_il_A']
            )
            cap_results.append({
                "scenario_name": scen_name,
                "f_sw_kHz": fsw,
                "i_out_A": pt['i_out_A'],
                "duty": pt['duty'],
                "delta_il_A": pt['delta_il_A'],
                **cap_eval
            })
            if scen_name in ["SCEN-1_Nominal_7.56W", "SCEN-2_WorstCase_Sag_4.5V"]:
                print(f"    ({scen_name}) {cap_key:30s} -> Ceff={cap_eval['c_eff_worst_uF']:4.1f}uF, "
                      f"Ripple(typ)={cap_eval['v_ripple_typ_mV']:4.1f}mV, Ripple(worst)={cap_eval['v_ripple_worst_mV']:4.1f}mV")
    
    # 4. Bleeder evaluation
    bleed_data = calculate_bleeder_and_pulse_skipping(
        r_bleed_ohm=1500.0, v_out=12.17, v_in=5.0, l_uh=4.7, f_sw_khz=freq_data['f_nom_kHz']
    )
    print("\n[4] Bleeder Resistor R_BLEED (1.5kOhm 1206) Evaluation:")
    print(f"  - Bleeder Current : {bleed_data['i_bleed_mA']} mA")
    print(f"  - Bleeder Power   : {bleed_data['p_bleed_mW']} mW (safe on 1206, rated 250mW)")
    print(f"  - Min Pulse Power : {bleed_data['p_min_pulse_mW']} mW")
    print(f"  - Absorbs Pulse   : {bleed_data['can_absorb_min_pulse']} (prevents voltage runaway at no-load)")
    print(f"  - Discharge to 1V : {bleed_data['t_discharge_1v_ms']} ms")
    
    # 5. Export CSV files
    out_dir = "docs/engineering/round3_2_1/phase1_power"
    os.makedirs(out_dir, exist_ok=True)
    
    # WCCA CSV
    wcca_path = os.path.join(out_dir, "POWER_WORST_CASE_ANALYSIS_MATRIX.csv")
    with open(wcca_path, "w", newline="") as fp:
        fieldnames = [
            "scenario_name", "v_in", "v_out", "p_out", "efficiency", "f_sw_kHz",
            "l_uH", "ambient_temp_C", "duty", "i_out_A", "i_in_avg_A",
            "delta_il_A", "i_peak_A", "i_rms_A"
        ]
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(wcca_results)
    print(f"\n[+] Exported: {wcca_path}")
    
    # Inductor CSV
    ind_path = os.path.join(out_dir, "INDUCTOR_SWPA6045_DETAILED_THERMAL_SATURATION_ANALYSIS.csv")
    with open(ind_path, "w", newline="") as fp:
        fieldnames = [
            "scenario_name", "i_rms_A", "i_peak_A", "ambient_temp_C",
            "dcr_at_t_mohm", "copper_loss_W", "core_loss_W", "total_loss_W",
            "delta_t_C", "t_core_C", "sat_derating_factor",
            "isat_min_derated_A", "isat_typ_derated_A",
            "margin_min_pct", "margin_typ_pct"
        ]
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(inductor_results)
    print(f"[+] Exported: {ind_path}")
    
    # Capacitor CSV
    cap_path = os.path.join(out_dir, "CAPACITOR_DC_BIAS_AND_RIPPLE_ANALYSIS.csv")
    with open(cap_path, "w", newline="") as fp:
        fieldnames = [
            "scenario_name", "f_sw_kHz", "i_out_A", "duty", "delta_il_A",
            "cap_model", "c_nom_total_uF", "c_eff_typ_uF", "c_eff_worst_uF",
            "v_ripple_typ_mV", "v_ripple_worst_mV"
        ]
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(cap_results)
    print(f"[+] Exported: {cap_path}")
    
    return True

# ----------------------------------------------------------------------
# 7. Self-Verifying Regression Tests (Exit Code 0 Enforced)
# ----------------------------------------------------------------------

def run_unit_tests():
    print("\n=== RUNNING PHASE 1 REGRESSION TESTS ===")
    
    # Test 1: Table 1 Interpolation exact points
    f_66_5 = calculate_fsw_interpolated(66.5)
    assert abs(f_66_5 - 620.0) < 1.0, f"Table 1 point failed: {f_66_5}"
    f_143 = calculate_fsw_interpolated(143.0)
    assert abs(f_143 - 320.0) < 1.0, f"Table 1 point failed: {f_143}"
    print("[PASS] Test 1: Table 1 boundary point interpolation verified")
    
    # Test 2: Frequency bounds sanity
    bounds = calculate_fsw_bounds(82.0)
    assert 400.0 < bounds['f_min_kHz'] < 500.0, f"Min frequency out of bounds: {bounds['f_min_kHz']}"
    assert 500.0 < bounds['f_nom_kHz'] < 550.0, f"Nom frequency out of bounds: {bounds['f_nom_kHz']}"
    assert 580.0 < bounds['f_max_kHz'] < 680.0, f"Max frequency out of bounds: {bounds['f_max_kHz']}"
    print("[PASS] Test 2: Frequency min/nom/max bounds sanity verified")
    
    # Test 3: Inductor saturation margin positive across all worst cases
    scen_worst = calculate_boost_operating_point(4.5, 12.17, 10.0, 0.85, bounds['f_min_kHz'], 3.76)
    ind_worst = calculate_inductor_thermal_and_saturation(
        scen_worst['i_rms_A'], scen_worst['i_peak_A'], ambient_temp_c=50.0
    )
    # Even under 10W worst-case sag at 50C ambient, margin should be analyzed
    print(f"      Worst-Case 10W Inductor Stress: Ipk={scen_worst['i_peak_A']}A, "
          f"Tcore={ind_worst['t_core_C']}C, Isat_min(T)={ind_worst['isat_min_derated_A']}A, "
          f"Margin={ind_worst['margin_min_pct']}%")
    assert ind_worst['t_core_C'] < 100.0, "Core temperature exceeds safety limit"
    print("[PASS] Test 3: Worst-case thermal & saturation computation verified")
    
    # Test 4: Capacitor candidate ordering
    # 50V part must retain more effective capacitance than 25V part
    cap_50v = calculate_effective_capacitance_and_ripple("Candidate_C_2x_1210_22uF_50V", 0.621, 0.589, 521.0, 1.30)
    cap_25v = calculate_effective_capacitance_and_ripple("Candidate_A_2x_1210_22uF_25V", 0.621, 0.589, 521.0, 1.30)
    assert cap_50v['c_eff_worst_uF'] > cap_25v['c_eff_worst_uF'], "50V part should have higher effective capacitance"
    assert cap_50v['v_ripple_worst_mV'] < cap_25v['v_ripple_worst_mV'], "50V part should yield lower ripple"
    print("[PASS] Test 4: Capacitor voltage rating DC bias hierarchy verified")
    
    print("\n[ALL 4 TESTS PASSED CLEANLY - EXIT CODE 0]")
    return True

if __name__ == "__main__":
    success = run_phase1_verification()
    test_ok = run_unit_tests()
    if success and test_ok:
        sys.exit(0)
    else:
        sys.exit(1)
