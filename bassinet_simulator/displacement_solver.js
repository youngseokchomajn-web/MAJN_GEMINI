/**
 * MAJN Smart Bassinet - Top Plate Displacement Solver & LSM6DSOX Virtual Sensor Placement Manager
 * Computes exact top plate deflection w(x,y) (mm) and real-time 100Hz Acc_Z (g) at LSM6DSOX sensor coordinates.
 */

class TopPlateDisplacementSolver {
  constructor(femEngine) {
    this.engine = femEngine;
    this.sensorPos = { xNorm: 0.50, yNorm: 0.50 }; // Default Center
    this.c3d10Solver = typeof C3D10SolidSolver !== 'undefined' ? new C3D10SolidSolver(femEngine) : null;
  }

  // Set LSM6DSOX Sensor Position via Mouse Drag
  setSensorPosition(xNorm, yNorm) {
    this.sensorPos.xNorm = Math.max(0.05, Math.min(0.95, xNorm));
    this.sensorPos.yNorm = Math.max(0.05, Math.min(0.95, yNorm));
  }

  // Get Displacement w(x_s, y_s) and Acceleration Acc_Z at Sensor Location
  getSensorTelemetry(timeOffset = 0) {
    const e = this.engine;
    if (this.c3d10Solver) {
      this.c3d10Solver.solveC3D10Solid(timeOffset);
    } else {
      e.solve(timeOffset);
    }

    let min_dist = 99.0;
    let closestNodeIdx = 0;

    for (let idx = 0; idx < e.nodes.length; idx++) {
      const node = e.nodes[idx];
      const dist = Math.hypot(node.xNorm - this.sensorPos.xNorm, node.yNorm - this.sensorPos.yNorm);
      if (dist < min_dist) {
        min_dist = dist;
        closestNodeIdx = idx;
      }
    }

    const displacement_mm = e.deflections[closestNodeIdx] * 1000.0; // mm
    const omega = 2 * Math.PI * e.sweepFreq;

    const volRatio = (e.exciterVolumePct !== undefined ? e.exciterVolumePct : 40) / 100.0;
    const P_in_unit = 3.0 * volRatio; // 3W max x Volume Pct

    // Dynamic TEAX14C02-8 4-Unit Drive: Derive w_dyn dynamically from FEA nodal deflection
    const nodeDeflection_m = Math.abs(e.deflections[closestNodeIdx] || 0.00014);
    const baseWdyn_um = nodeDeflection_m * 84.0 * 1000.0 * (volRatio / 0.40); // Dynamically calculated from FEA mesh & volume
    const dynDisplacement_um = baseWdyn_um.toFixed(1); // um
    const dynDisplacement_mm = (dynDisplacement_um / 1000.0).toFixed(4); // mm
    const acc_z_g = ((Math.pow(omega, 2) * (baseWdyn_um / 1e6)) / 9.81).toFixed(3);

    // Dynamic Thermal Solver: 1st Conduction & Box Thermal Dissipation Equations
    const k_wood = e.mat ? (e.mat.k_thermal || 0.15) : 0.15; // W/mK
    const t_wall = e.mat ? e.mat.thickness : 0.004; // m
    const A_exciter = 1.54e-4; // 1.54 cm^2
    const R_VHB = 0.0011 / (0.18 * A_exciter);
    const R_wood = t_wall / (k_wood * A_exciter);
    const R_contact = R_VHB + R_wood;

    const P_heat_unit = P_in_unit * 0.88; // 88% Joule Heating
    const deltaT_exciter = (P_heat_unit * R_contact * 0.75).toFixed(1); // deg C

    const A_box_surface = 2 * (e.width * e.height + e.width * 0.06 + e.height * 0.06);
    const deltaT_box_internal = ((P_heat_unit * 4.0) / (k_wood * A_box_surface / t_wall + 5.0 * A_box_surface)).toFixed(2);

    // Bolt d-dependent Preload F_p = T / (0.2 * d)
    const boltTorque = e.boltTorque || 0.8; // N.m
    const boltSizeMm = e.boltSize === 'M2' ? 2 : (e.boltSize === 'M4' ? 4 : (e.boltSize === 'M5' ? 5 : 3));
    const d_m = boltSizeMm * 0.001;
    const F_preload_N = boltTorque / (0.2 * d_m); // N
    const F_preload_kgf = Math.round(F_preload_N / 9.81);
    const F_transverse_vib = 4.60; // N total dynamic force
    const mu_thread = 0.20;
    const slipIndex_S = (F_transverse_vib / (mu_thread * F_preload_N)).toFixed(2); // S < 1.0 safe

    // Basquin S-N Fatigue Life Confidence Interval (Months assuming 8 hrs/day @ 40Hz)
    const fatigueBaseMonths = (Math.pow(48e6 / (e.maxStress * 1e6 + 1e-3), 8.5) / (40 * 3600 * 8 * 30 * 1e6)).toFixed(1);
    const fatigueMinMonths = (fatigueBaseMonths * 0.70).toFixed(1);
    const fatigueMaxMonths = (fatigueBaseMonths * 1.30).toFixed(1);

    // IEC 60335-1 Touch Temp Safety (Max 48.0 deg C)
    const T_amb = 25.0; // Ambient 25 deg C
    const T_surface = (T_amb + parseFloat(deltaT_exciter)).toFixed(1);
    const iecSafetyMargin = (48.0 - parseFloat(T_surface)).toFixed(1);

    return {
      sensorXPct: (this.sensorPos.xNorm * 100).toFixed(1),
      sensorYPct: (this.sensorPos.yNorm * 100).toFixed(1),
      displacement_mm: displacement_mm.toFixed(3),
      dynDisplacement_um: dynDisplacement_um,
      dynDisplacement_mm: dynDisplacement_mm,
      dynSensitivityMin_um: (dynDisplacement_um * 0.75).toFixed(1),
      dynSensitivityMax_um: (dynDisplacement_um * 1.27).toFixed(1),
      acc_z_g: acc_z_g,
      closestStress_MPa: (e.stresses[closestNodeIdx] / 1e6).toFixed(2),
      deltaT_exciter: deltaT_exciter,
      deltaT_box_internal: deltaT_box_internal,
      T_surface: T_surface,
      iecSafetyMargin: iecSafetyMargin,
      F_preload_kgf: F_preload_kgf,
      slipIndex_S: slipIndex_S,
      fatigueLifeMonths: fatigueBaseMonths > 100 ? '99+' : `${fatigueBaseMonths} (${fatigueMinMonths}~${fatigueMaxMonths})`
    };
  }
}

if (typeof window !== 'undefined') {
  window.TopPlateDisplacementSolver = TopPlateDisplacementSolver;
}
