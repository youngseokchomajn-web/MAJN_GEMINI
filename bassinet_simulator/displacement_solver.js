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

    // TEAX14C02-8 4-Unit 1.2W Drive SVS Mode: w_dyn = 11.8 um (0.0118 mm)
    const dynDisplacement_um = (displacement_mm * 84.0).toFixed(1); // um
    const dynDisplacement_mm = (dynDisplacement_um / 1000.0).toFixed(4); // mm
    const acc_z_g = ((Math.pow(omega, 2) * (dynDisplacement_um / 1e6)) / 9.81).toFixed(3);

    // Dynamic Thermal Solver: 1st Conduction & Box Thermal Dissipation Equations
    const k_wood = e.mat ? (e.mat.k_thermal || 0.15) : 0.15; // W/mK
    const t_wall = e.mat ? e.mat.thickness : 0.004; // m
    const A_exciter = 1.54e-4; // 1.54 cm^2
    const R_VHB = 0.0011 / (0.18 * A_exciter);
    const R_wood = t_wall / (k_wood * A_exciter);
    const R_contact = R_VHB + R_wood;

    const volRatio = (e.exciterVolumePct || 40) / 100.0;
    const P_in_unit = 3.0 * volRatio; // 3W max x Volume Pct
    const P_heat_unit = P_in_unit * 0.88; // 88% Joule Heating
    const deltaT_exciter = (P_heat_unit * R_contact * 0.75).toFixed(1); // deg C

    const A_box_surface = 2 * (e.width * e.height + e.width * 0.06 + e.height * 0.06);
    const deltaT_box_internal = ((P_heat_unit * 4.0) / (k_wood * A_box_surface / t_wall + 5.0 * A_box_surface)).toFixed(2);

    return {
      sensorXPct: (this.sensorPos.xNorm * 100).toFixed(1),
      sensorYPct: (this.sensorPos.yNorm * 100).toFixed(1),
      displacement_mm: displacement_mm.toFixed(3),
      dynDisplacement_um: dynDisplacement_um,
      dynDisplacement_mm: dynDisplacement_mm,
      acc_z_g: acc_z_g,
      closestStress_MPa: (e.stresses[closestNodeIdx] / 1e6).toFixed(2),
      deltaT_exciter: deltaT_exciter,
      deltaT_box_internal: deltaT_box_internal
    };
  }
}

if (typeof window !== 'undefined') {
  window.TopPlateDisplacementSolver = TopPlateDisplacementSolver;
}
