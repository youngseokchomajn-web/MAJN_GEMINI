#!/usr/bin/env python3
"""
MAJN Smart Bassinet - Standalone AI FEA & SVS Dynamic Optimizer CLI Script
Designed for AI Coding Agents (Claude, Gemini, ChatGPT) and CI/CD pipelines.
Runs multi-objective structural FEA & 5-Tone SVS vibration optimization.
"""

import sys
import json
import math

def run_ai_optimization_cli(weight_kg=15.0, target_svs_um=11.2):
    materials = {
        'birch_3mm': {'name': '자작합판 3mm', 'E_x': 9.15e9, 'E_y': 4.20e9, 'nu': 0.33, 't': 0.003, 'density': 680, 'yield': 48e6},
        'birch_4mm': {'name': '자작합판 4mm', 'E_x': 9.15e9, 'E_y': 4.20e9, 'nu': 0.33, 't': 0.004, 'density': 680, 'yield': 48e6},
        'birch_5mm': {'name': '자작합판 5mm', 'E_x': 10.5e9, 'E_y': 4.50e9, 'nu': 0.33, 't': 0.005, 'density': 690, 'yield': 52e6},
        'birch_6mm': {'name': '자작합판 6mm', 'E_x': 10.5e9, 'E_y': 4.50e9, 'nu': 0.33, 't': 0.006, 'density': 690, 'yield': 52e6},
        'abs_3mm':   {'name': 'ABS 플라스틱 3mm', 'E_x': 2.30e9, 'E_y': 2.30e9, 'nu': 0.38, 't': 0.003, 'density': 1050, 'yield': 45e6},
        'pc_4mm':    {'name': '폴리카보네이트 4mm', 'E_x': 3.10e9, 'E_y': 3.10e9, 'nu': 0.37, 't': 0.004, 'density': 1190, 'yield': 65e6}
    }
    
    candidate_widths = [450, 500, 600, 650, 720]
    candidate_heights = [16.5, 18.0, 20.0, 25.0]
    candidate_forces = [1.5, 2.5, 3.5, 5.0]
    
    best_score = -999999.0
    best_result = None
    
    P_N = weight_kg * 9.81
    
    for mat_key, mat in materials.items():
        t_m = mat['t']
        for w_mm in candidate_widths:
            l_mm = round(w_mm * 0.56)
            w_m = w_mm / 1000.0
            l_m = l_mm / 1000.0
            
            for h_mm in candidate_heights:
                if h_mm < (t_m*2000.0 + 10.0): continue
                
                D_base = math.sqrt(((mat['E_x'] * (t_m**3)) / (12.0 * (1.0 - mat['nu']**2))) * ((mat['E_y'] * (t_m**3)) / (12.0 * (1.0 - mat['nu']**2))))
                K_box = 1.0 + (5.5 * (h_mm / 45.0))
                D_box = D_base * K_box
                
                w_static_mm = (P_N * (w_m**3) / (48.0 * D_box)) * 1000.0
                sigma_max_MPa = (6.0 * (P_N * w_m / 8.0)) / (l_m * (t_m**2) * K_box) / 1e6
                sf = mat['yield'] / (sigma_max_MPa * 1e6 + 1e-3)
                
                for f_N in candidate_forces:
                    dyn_amp_um = (f_N * 5.0e-4 / D_box) * 1e6
                    
                    vol = (2 * w_m * l_m * t_m) + (2 * w_m * (h_mm/1000) * t_m) + (2 * l_m * (h_mm/1000) * t_m)
                    weight_g = vol * mat['density'] * 1000.0 + 140.0
                    
                    score = 100.0
                    score -= max(0, w_static_mm - 6.0) * 15.0
                    score -= abs(dyn_amp_um - target_svs_um) * 10.0
                    score -= max(0, weight_g - 1400.0) * 0.05
                    if sf < 3.0: score -= 50.0
                    
                    if score > best_score:
                        best_score = score
                        best_result = {
                            'matKey': mat_key,
                            'matName': mat['name'],
                            'width_mm': w_mm,
                            'length_mm': l_mm,
                            'height_mm': h_mm,
                            'thickness_mm': t_m * 1000.0,
                            'drive_force_N': f_N,
                            'w_static_mm': round(w_static_mm, 2),
                            'sigma_max_MPa': round(sigma_max_MPa, 2),
                            'safety_factor': round(sf, 1),
                            'dyn_amp_um': round(dyn_amp_um, 1),
                            'weight_g': round(weight_g, 0),
                            'score': round(score, 1)
                        }

    return best_result

if __name__ == '__main__':
    res = run_ai_optimization_cli()
    print(json.dumps(res, indent=2, ensure_ascii=False))
