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
    
    // Acc_Z (g) = -omega^2 * displacement / 9.81
    const dynDisplacement_m = (displacement_mm / 1000.0) * 0.4;
    const acc_z_g = Math.abs((Math.pow(omega, 2) * dynDisplacement_m) / 9.81);

    return {
      sensorXPct: (this.sensorPos.xNorm * 100).toFixed(1),
      sensorYPct: (this.sensorPos.yNorm * 100).toFixed(1),
      displacement_mm: displacement_mm.toFixed(3),
      acc_z_g: acc_z_g.toFixed(2),
      closestStress_MPa: (e.stresses[closestNodeIdx] / 1e6).toFixed(2)
    };
  }
}

if (typeof window !== 'undefined') {
  window.TopPlateDisplacementSolver = TopPlateDisplacementSolver;
}
