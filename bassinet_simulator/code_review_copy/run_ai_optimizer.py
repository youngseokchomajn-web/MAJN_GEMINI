#!/usr/bin/env python3
"""
MAJN Smart Bassinet - Standalone AI FEA & SVS Dynamic Optimizer CLI Script
Designed for AI Coding Agents (Claude, Gemini, ChatGPT) and CI/CD pipelines.
Runs multi-objective structural FEA & 5-Tone SVS vibration optimization.

v2 (calibrated): material orthotropy & Kbox model now match the web solver
(c3d10_solver.js: Ex = 1.15*E, Ey = 0.70*E / fem_engine.js: Kbox = 1 + 5.5*(H/45)),
and the 24-month design constraints are enforced as hard constraints:
  - box height <= 18.0 mm (ultra-slim: 4mm top + 10mm exciter + 4mm bottom)
  - pad width >= 600 mm (24-month ergonomic fit, 600x340 target)
  - safety factor > 5.0x (vs. material yield strength)
  - SVS peak amplitude within 10.0 ~ 12.5 um clinical band at 40Hz 5-Tone
"""

import sys
import json
import math

# Design constraints (NUCU_PAD_ULTRA_SLIM_ENGINEERING_REPORT.md §1)
MAX_HEIGHT_MM = 18.0
MIN_WIDTH_MM = 600
SVS_BAND_UM = (10.0, 12.5)
MIN_SAFETY_FACTOR = 5.0

def run_ai_optimization_cli(weight_kg=15.0, target_svs_um=11.2):
    # Base isotropic E values identical to fem_engine.js materials DB;
    # orthotropic split (Ex=1.15E, Ey=0.70E) identical to c3d10_solver.js.
    materials = {
        'birch_3mm': {'name': '자작합판 3mm', 'E': 9.15e9, 'nu': 0.33, 't': 0.003, 'density': 680, 'yield': 48e6},
        'birch_4mm': {'name': '자작합판 4mm', 'E': 9.15e9, 'nu': 0.33, 't': 0.004, 'density': 680, 'yield': 48e6},
        'birch_5mm': {'name': '자작합판 5mm', 'E': 10.5e9, 'nu': 0.33, 't': 0.005, 'density': 690, 'yield': 52e6},
        'birch_6mm': {'name': '자작합판 6mm', 'E': 10.5e9, 'nu': 0.33, 't': 0.006, 'density': 690, 'yield': 52e6},
        'abs_3mm':   {'name': 'ABS 플라스틱 3mm', 'E': 2.30e9, 'nu': 0.38, 't': 0.003, 'density': 1050, 'yield': 45e6},
        'pc_4mm':    {'name': '폴리카보네이트 4mm', 'E': 3.10e9, 'nu': 0.37, 't': 0.004, 'density': 1190, 'yield': 65e6}
    }

    candidate_widths = [450, 500, 600, 650, 720]
    candidate_heights = [16.5, 18.0, 20.0, 25.0]
    candidate_forces = [1.5, 1.8, 2.0, 2.2, 2.5, 3.5, 5.0]

    # SVS amplitude calibration to the web telemetry (displacement_solver.getSensorTelemetry @ S1 center):
    #   dynamicAmpFactor = 1/sqrt((1-0.8^2)^2 + (2*zeta*0.8)^2), zeta(VHB)=0.05  -> 2.712
    #   sum of 4-exciter Gaussian influence exp(-d^2*14) at pad center           -> 0.678
    #   bolt proximity factor 1-exp(-d^2*25) at center                           -> 0.988
    AMP_CAL = 2.712 * 0.678 * 0.988  # ~1.816

    best_score = -999999.0
    best_result = None
    rejected = {'height': 0, 'width': 0, 'sf': 0, 'svs_band': 0, 'clearance': 0}

    P_N = weight_kg * 9.81

    for mat_key, mat in materials.items():
        t_m = mat['t']
        Ex = mat['E'] * 1.15
        Ey = mat['E'] * 0.70
        nu_xy = mat['nu']
        nu_yx = (Ey / Ex) * nu_xy

        for w_mm in candidate_widths:
            l_mm = round(w_mm * 0.56)
            w_m = w_mm / 1000.0
            l_m = l_mm / 1000.0

            if w_mm < MIN_WIDTH_MM:
                rejected['width'] += 1
                continue

            for h_mm in candidate_heights:
                if h_mm < (t_m * 2000.0 + 10.0):
                    rejected['clearance'] += 1
                    continue
                if h_mm > MAX_HEIGHT_MM:
                    rejected['height'] += 1
                    continue

                denom = 12.0 * (1.0 - nu_xy * nu_yx)
                D_base = math.sqrt(((Ex * t_m**3) / denom) * ((Ey * t_m**3) / denom))
                K_box = 1.0 + (5.5 * (h_mm / 45.0))
                D_box = D_base * K_box

                w_static_mm = (P_N * (w_m**3) / (48.0 * D_box)) * 1000.0
                sigma_max_MPa = (6.0 * (P_N * w_m / 8.0)) / (l_m * (t_m**2) * K_box) / 1e6
                sf = mat['yield'] / (sigma_max_MPa * 1e6 + 1e-3)

                if sf < MIN_SAFETY_FACTOR:
                    rejected['sf'] += 1
                    continue

                for f_N in candidate_forces:
                    dyn_amp_um = (f_N * 5.0e-4 / D_box) * AMP_CAL * 1e6

                    if not (SVS_BAND_UM[0] <= dyn_amp_um <= SVS_BAND_UM[1]):
                        rejected['svs_band'] += 1
                        continue

                    vol = (2 * w_m * l_m * t_m) + (2 * w_m * (h_mm / 1000) * t_m) + (2 * l_m * (h_mm / 1000) * t_m)
                    weight_g = vol * mat['density'] * 1000.0 + 140.0

                    score = 100.0
                    score -= max(0, w_static_mm - 6.0) * 15.0
                    score -= abs(dyn_amp_um - target_svs_um) * 10.0
                    score -= max(0, weight_g - 1400.0) * 0.05

                    if score > best_score:
                        best_score = score
                        best_result = {
                            'matKey': mat_key,
                            'matName': mat['name'],
                            'width_mm': w_mm,
                            'length_mm': l_mm,
                            'height_mm': h_mm,
                            'thickness_mm': t_m * 1000.0,
                            'K_box': round(K_box, 2),
                            'drive_force_N': f_N,
                            'w_static_mm': round(w_static_mm, 2),
                            'sigma_max_MPa': round(sigma_max_MPa, 2),
                            'safety_factor': round(sf, 1),
                            'dyn_amp_um': round(dyn_amp_um, 1),
                            'weight_g': round(weight_g, 0),
                            'score': round(score, 1)
                        }

    return {
        'constraints': {
            'max_height_mm': MAX_HEIGHT_MM,
            'min_width_mm': MIN_WIDTH_MM,
            'svs_band_um': list(SVS_BAND_UM),
            'min_safety_factor': MIN_SAFETY_FACTOR,
            'payload_kg': weight_kg,
            'target_svs_um': target_svs_um
        },
        'rejected_candidates': rejected,
        'optimum': best_result
    }

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    res = run_ai_optimization_cli()
    print(json.dumps(res, indent=2, ensure_ascii=False))
