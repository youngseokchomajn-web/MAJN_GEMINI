/**
 * MAJN Smart Bassinet - Diagnostics & Telemetry Monitor
 * Tracks command latency, ACK statistics, telemetry rate, and fault logs
 */

export class DiagnosticsMonitor {
  constructor() {
    this.commandsSent = 0;
    this.acksReceived = 0;
    this.rejectedCount = 0;
    this.telemetryPackets = 0;
    this.lastTelemetryTimestamp = 0;
    this.telemetryIntervals = [];
    this.eventLogs = [];
    this.pendingAcks = new Map(); // id -> { cmd, sentTime }
  }

  recordCommand(id, cmd, payload = {}) {
    this.commandsSent++;
    this.pendingAcks.set(id, { cmd, sentTime: Date.now(), payload });
  }

  recordAck(ack) {
    this.acksReceived++;
    let latencyMs = 0;
    if (this.pendingAcks.has(ack.id)) {
      latencyMs = Date.now() - this.pendingAcks.get(ack.id).sentTime;
      this.pendingAcks.delete(ack.id);
    }
    if (ack.status === 'rejected' || ack.status === 'fault') {
      this.rejectedCount++;
    }
    return latencyMs;
  }

  recordTelemetry(data) {
    this.telemetryPackets++;
    const now = Date.now();
    if (this.lastTelemetryTimestamp > 0) {
      const dt = now - this.lastTelemetryTimestamp;
      this.telemetryIntervals.push(dt);
      if (this.telemetryIntervals.length > 20) this.telemetryIntervals.shift();
    }
    this.lastTelemetryTimestamp = now;
  }

  getCalculatedRateHz() {
    if (this.telemetryIntervals.length === 0) return 0;
    const avgDt = this.telemetryIntervals.reduce((a, b) => a + b, 0) / this.telemetryIntervals.length;
    return avgDt > 0 ? (1000 / avgDt).toFixed(1) : 0;
  }

  isTelemetryStale(timeoutMs = 3000) {
    if (this.lastTelemetryTimestamp === 0) return false;
    return (Date.now() - this.lastTelemetryTimestamp) > timeoutMs;
  }

  reset() {
    this.commandsSent = 0;
    this.acksReceived = 0;
    this.rejectedCount = 0;
    this.telemetryPackets = 0;
    this.lastTelemetryTimestamp = 0;
    this.telemetryIntervals = [];
    this.pendingAcks.clear();
  }
}

if (typeof window !== 'undefined') {
  window.MAJN_DIAGNOSTICS = { DiagnosticsMonitor };
}
