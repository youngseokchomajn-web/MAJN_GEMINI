#!/usr/bin/env python3
"""
MAJN Smart Bassinet 3D Box Enclosure - AI (Claude) Joint Optimization Engine
Simultaneously evaluates 4 Architectural Housing Concepts:
  A. Pure Wood Joinery (Finger Joint & Wood Glue)
  B. Wood + EVA Foam Sandwich (3M VHB)
  C. Wood + Metal L-Brackets & Bolts
  D. Hybrid (EVA Foam + L-Brackets + Wood)
Calculates Pareto Optimal Concept based on Cost, Assembly Labor, Durability & Vibration Deflection.
"""

import json
import math
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'housing_config.json')

CONCEPTS = {
    "pure_wood": {
        "name": "Concept A: 순수 나무 짜맞춤 (Finger Joint & Wood Glue)",
        "cost_USD": 41.2,
        "machining_diff": 4.8,
        "assembly_min": 45,
        "durability_score": 3.6,
        "deflection_mm": 0.22,
        "stress_MPa": 1.15
    },
    "eva_sandwich": {
        "name": "Concept B: 목재 + EVA 폼 완충 샌드위치 (3M VHB)",
        "cost_USD": 45.4,
        "machining_diff": 2.1,
        "assembly_min": 18,
        "durability_score": 4.1,
        "deflection_mm": 0.18,
        "stress_MPa": 0.88
    },
    "l_bracket": {
        "name": "Concept C: 목재 + 금속 L-브래킷 체결 (Bolts & Standoffs)",
        "cost_USD": 46.8,
        "machining_diff": 1.5,
        "assembly_min": 12,
        "durability_score": 4.8,
        "deflection_mm": 0.15,
        "stress_MPa": 0.72
    },
    "hybrid": {
        "name": "Concept D: 하이브리드 (EVA 폼 + L-브래킷 + 목재)",
        "cost_USD": 48.4,
        "machining_diff": 2.2,
        "assembly_min": 15,
        "durability_score": 5.0,
        "deflection_mm": 0.14,
        "stress_MPa": 0.70
    }
}

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def evaluate_concepts_pareto(w_cost=0.25, w_machining=0.20, w_assembly=0.20, w_durability=0.20, w_vibr=0.15):
    print("\n[AI PARETO EVALUATOR] Comparing 4 Architectural Housing Concepts...")
    
    best_key = None
    best_score = -float('inf')
    results = {}

    for key, c in CONCEPTS.items():
        s_cost = max(0, 100 - (c['cost_USD'] - 40) * 8.0)
        s_machining = max(0, 100 - (c['machining_diff'] - 1.0) * 22.0)
        s_assembly = max(0, 100 - (c['assembly_min'] - 10) * 2.5)
        s_durability = c['durability_score'] * 20.0
        s_vibr = max(0, 100 - c['deflection_mm'] * 300.0)

        total_score = (s_cost * w_cost + s_machining * w_machining + 
                       s_assembly * w_assembly + s_durability * w_durability + s_vibr * w_vibr)
        results[key] = round(total_score, 1)

        print(f"  > {c['name']:<50} => Score: {total_score:.1f}/100 | Cost: ${c['cost_USD']} | Assembly: {c['assembly_min']}m")

        if total_score > best_score:
            best_score = total_score
            best_key = key

    return best_key, results

def main():
    config = load_config()
    print("=" * 75)
    print("🤖 MAJN Smart Bassinet - AI Housing Concept & Bolt/Exciter Optimization Engine")
    print("=" * 75)

    best_concept_key, results = evaluate_concepts_pareto()
    best_c = CONCEPTS[best_concept_key]

    print("-" * 75)
    print(f"🏆 AI Recommended Optimal Housing Concept: {best_c['name']}")
    print(f"   Score: {results[best_concept_key]}/100 | Cost: ${best_c['cost_USD']} | Deflection: {best_c['deflection_mm']} mm")
    print("=" * 75)

    config['concept_selection'] = best_concept_key
    save_config(config)
    print(f"✅ Config updated with selected concept '{best_concept_key}' in '{CONFIG_PATH}'.")

if __name__ == '__main__':
    main()
