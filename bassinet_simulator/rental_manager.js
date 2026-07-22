/**
 * MAJN Smart Bassinet - Rental Refurbishment & Vibration Efficiency Simulator Engine
 * Calculates Rental Turnaround Time, Sleeve Replacement Cost, Quick-swap A/S time,
 * Vibration Transfer Efficiency (%), and Total Lightweight Housing Mass (kg).
 */

class RentalRefurbishmentManager {
  constructor(femEngine) {
    this.femEngine = femEngine;
    this.rentalSpecs = {
      sleeveCostUSD: 2.5,
      sleeveSwapTimeSec: 10,
      cartridgeSwapTimeMin: 1.5,
      totalRefurbishTimeMin: 3.5,
      vibrationEfficiencyPct: 88.5,
      housingWeightKg: 1.75,
      reusabilityCycleCount: 50 // 50 rental cycles
    };
  }

  // Calculate Turnaround Cost & Time for Rental Return
  calculateRefurbishment(needsSleeveChange = true, needsCartridgeSwap = false) {
    let costUSD = 0.0;
    let laborMin = 0.0;

    if (needsSleeveChange) {
      costUSD += this.rentalSpecs.sleeveCostUSD;
      laborMin += this.rentalSpecs.sleeveSwapTimeSec / 60.0;
    }

    if (needsCartridgeSwap) {
      costUSD += 5.0; // Replacement cartridge
      laborMin += this.rentalSpecs.cartridgeSwapTimeMin;
    }

    return {
      refurbishCostUSD: Math.round(costUSD * 100) / 100,
      turnaroundTimeMin: Math.round(laborMin * 10) / 10,
      vibrationEfficiencyPct: this.rentalSpecs.vibrationEfficiencyPct,
      housingWeightKg: this.rentalSpecs.housingWeightKg
    };
  }
}

if (typeof window !== 'undefined') {
  window.RentalRefurbishmentManager = RentalRefurbishmentManager;
}
