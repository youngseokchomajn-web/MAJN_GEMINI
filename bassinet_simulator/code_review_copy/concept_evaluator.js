/**
 * MAJN Smart Bassinet - Multi-Criteria Housing Concept Evaluator
 * Compares 4 Architectural Concepts:
 *   A. Pure Wood Joinery (Finger Joint + Wood Glue)
 *   B. Wood + EVA Foam Sandwich (3M VHB Tape)
 *   C. Wood + Metal L-Brackets & Bolts
 *   D. Hybrid (EVA Foam + L-Brackets + Wood)
 * Across 5 Trade-off Indices: Vibration Deflection, Machining Difficulty, Assembly Time, Durability, Cost.
 */

class ConceptEvaluator {
  constructor() {
    this.concepts = {
      pure_wood: {
        id: 'pure_wood',
        name: 'Concept A: 순수 나무 짜맞춤 (Finger Joint & Wood Glue)',
        costUSD: 41.2,
        machiningDiff: 4.8, // 1 (Easy) ~ 5 (Hard)
        assemblyTimeMin: 45, // Assembly labor
        durabilityScore: 3.6, // 1 ~ 5
        maxDeflectionMm: 0.22,
        maxStressMPa: 1.15,
        safetyFactor: 41.7,
        pros: '부자재 비용 최소화, 고급 목재 일체감',
        cons: 'CNC 정밀 가공 시간 길음, 본드 접착 대기 24시간'
      },
      eva_sandwich: {
        id: 'eva_sandwich',
        name: 'Concept B: 목재 + EVA 폼 완충 샌드위치 (3M VHB)',
        costUSD: 45.4,
        machiningDiff: 2.1,
        assemblyTimeMin: 18,
        durabilityScore: 4.1,
        maxDeflectionMm: 0.18,
        maxStressMPa: 0.88,
        safetyFactor: 54.5,
        pros: '진동 차음/댐핑 우수, CNC 가공 용이',
        cons: '장기 사용 시 EVA 폼 경화 변형 가능성'
      },
      l_bracket: {
        id: 'l_bracket',
        name: 'Concept C: 목재 + 금속 L-브래킷 체결 (Bolts & Standoffs)',
        costUSD: 46.8,
        machiningDiff: 1.5,
        assemblyTimeMin: 12,
        durabilityScore: 4.8,
        maxDeflectionMm: 0.15,
        maxStressMPa: 0.72,
        safetyFactor: 66.7,
        pros: '가장 빠르고 쉬운 조립, 유지보수/분해 최고',
        cons: '금속 브래킷 및 볼트 자재비 추가'
      },
      hybrid: {
        id: 'hybrid',
        name: 'Concept D: 하이브리드 (EVA 폼 + L-브래킷 + 목재)',
        costUSD: 48.4,
        machiningDiff: 2.2,
        assemblyTimeMin: 15,
        durabilityScore: 5.0,
        maxDeflectionMm: 0.14,
        maxStressMPa: 0.70,
        safetyFactor: 68.5,
        pros: '최고의 내구성, 진동 차음, 우수한 안전율',
        cons: '상대적으로 높은 원가 비용 ($48.4)'
      }
    };
  }

  // Calculate Weighted Pareto Score
  // Weights: wCost, wMachining, wAssembly, wDurability, wVibration (sum to 1.0)
  recommendBestConcept(wCost = 0.25, wMachining = 0.20, wAssembly = 0.20, wDurability = 0.20, wVibration = 0.15) {
    let bestKey = null;
    let highestScore = -Infinity;
    const scores = {};

    Object.keys(this.concepts).forEach(key => {
      const c = this.concepts[key];

      // Normalized sub-scores (0 ~ 100, higher is better)
      const scoreCost = Math.max(0, 100 - (c.costUSD - 40) * 8.0);
      const scoreMachining = Math.max(0, 100 - (c.machiningDiff - 1.0) * 22.0);
      const scoreAssembly = Math.max(0, 100 - (c.assemblyTimeMin - 10) * 2.5);
      const scoreDurability = c.durabilityScore * 20.0;
      const scoreVibration = Math.max(0, 100 - c.maxDeflectionMm * 300.0);

      const totalScore = (
        scoreCost * wCost +
        scoreMachining * wMachining +
        scoreAssembly * wAssembly +
        scoreDurability * wDurability +
        scoreVibration * wVibration
      );

      scores[key] = Math.round(totalScore * 10) / 10;

      if (totalScore > highestScore) {
        highestScore = totalScore;
        bestKey = key;
      }
    });

    return {
      recommendedConcept: this.concepts[bestKey],
      scores: scores
    };
  }
}

if (typeof window !== 'undefined') {
  window.ConceptEvaluator = ConceptEvaluator;
}
