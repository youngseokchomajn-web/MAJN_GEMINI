/**
 * MAJN Smart Bassinet - Pure Software Simulation Provider
 * Simulates physical dynamics, closed-loop PID response, and baby state interactions
 */

import { DeviceProvider } from './device_provider.js';
import { DeviceState, StateMachine } from './state_machine.js';
import { PROTOCOL_LIMITS, PROTOCOL_VERSION, COMMANDS, validateCommandPacket } from './protocol.js';

export class SimulationDeviceProvider extends DeviceProvider {
  constructor() {
    super('simulation');
    this.deviceInfo = {
      name: 'MAJN-Virtual-Simulator',
      firmware: '0.2.0-sim',
      protocol: PROTOCOL_VERSION,
      mode: 'simulation'
    };
    this.stateMachine = new StateMachine(DeviceState.DISCONNECTED);
    this.simTimer = null;
    this.uptimeMs = 0;
    this.babyState = 'sleep';
    this.autoSoothing = true;
    this.currentRampedAmp = 0.0;
    this.phase = 0;
  }

  get state() {
    return this.stateMachine.state;
  }

  setState(newState, reason = '') {
    const old = this.stateMachine.state;
    if (this.stateMachine.transition(newState, reason)) {
      this.emit('stateChange', { state: newState, oldState: old, reason });
      this.emit('log', {
        type: (newState === DeviceState.FAULT || newState === DeviceState.SAFETY_LOCK) ? 'error' : 'info',
        message: `[SIM] State: ${old} -> ${newState}${reason ? ` (${reason})` : ''}`
      });
    }
  }

  async connect() {
    this.setState(DeviceState.CONNECTING, 'Initializing virtual simulator');
    await new Promise(r => setTimeout(r, 150));

    this.isConnected = true;
    this.uptimeMs = 0;
    this.setState(DeviceState.READY, 'Virtual ESP32 Ready');
    this.emit('connectionChange', { isConnected: true, provider: this });
    this.startLoop();
    this.emit('log', { type: 'success', message: '[SIM] 가상 배시넷 컨트롤러가 준비되었습니다.' });
    return true;
  }

  async disconnect() {
    this.stopLoop();
    this.isConnected = false;
    this.setState(DeviceState.DISCONNECTED, 'User requested disconnect');
    this.emit('connectionChange', { isConnected: false, provider: this });
    this.emit('log', { type: 'info', message: '[SIM] 시뮬레이션 연결이 해제되었습니다.' });
    return true;
  }

  async start(options = {}) {
    if (!this.stateMachine.canStart()) {
      const err = `Cannot start from state: ${this.state}`;
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.START, status: 'rejected', state: this.state });
      throw new Error(err);
    }

    if (options.frequency_hz !== undefined) this.currentFrequency = options.frequency_hz;
    if (options.amplitude !== undefined) this.currentAmplitude = options.amplitude;

    this.setState(DeviceState.RUNNING, 'Start vibration');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.START, status: 'applied', state: this.state });
    this.emit('log', {
      type: 'success',
      message: `[SIM] 진동 구동 시작: ${this.currentFrequency}Hz, scale ${(this.currentAmplitude).toFixed(2)}`
    });
    return true;
  }

  async stop() {
    if (this.state === DeviceState.SAFETY_LOCK || this.state === DeviceState.FAULT) {
      return;
    }
    this.setState(DeviceState.READY, 'Stop vibration');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.STOP, status: 'applied', state: this.state });
    this.emit('log', { type: 'info', message: '[SIM] 진동 구동 정지 (대기 상태 복귀)' });
    return true;
  }

  async emergencyStop() {
    this.currentRampedAmp = 0.0;
    this.setState(DeviceState.SAFETY_LOCK, '비상 정지(ESTOP) 발동');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.ESTOP, status: 'applied', state: this.state });
    this.emit('log', {
      type: 'error',
      message: '[SIM ESTOP] 비상 정지 발동! 하드웨어 부스트(12V) 및 앰프 전원 즉시 차단됨.'
    });
    return true;
  }

  async resetFault() {
    if (this.stateMachine.canReset()) {
      this.setState(DeviceState.READY, 'Manual fault reset');
      this.emit('log', { type: 'info', message: '[SIM] 안전 잠금 상태가 정상 해제되었습니다.' });
      return true;
    }
    return false;
  }

  async setFrequency(hz) {
    const val = validateCommandPacket({ id: 1, cmd: COMMANDS.SET_FREQUENCY, frequency_hz: Number(hz) });
    if (!val.valid) {
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_FREQUENCY, status: 'rejected', state: this.state });
      throw new Error(val.error);
    }
    this.currentFrequency = Number(hz);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_FREQUENCY, status: 'applied', state: this.state });
    return true;
  }

  async setAmplitude(amp) {
    const val = validateCommandPacket({ id: 1, cmd: COMMANDS.SET_AMPLITUDE, amplitude: Number(amp) });
    if (!val.valid) {
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_AMPLITUDE, status: 'rejected', state: this.state });
      throw new Error(val.error);
    }
    this.currentAmplitude = Number(amp);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_AMPLITUDE, status: 'applied', state: this.state });
    return true;
  }

  async setVibration(hz, amp) {
    const val = validateCommandPacket({ id: 1, cmd: COMMANDS.SET_VIBRATION, frequency_hz: Number(hz), amplitude: Number(amp) });
    if (!val.valid) {
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_VIBRATION, status: 'rejected', state: this.state });
      throw new Error(val.error);
    }
    this.currentFrequency = Number(hz);
    this.currentAmplitude = Number(amp);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_VIBRATION, status: 'applied', state: this.state });
    return true;
  }

  async setVolume(volume) {
    const val = validateCommandPacket({ id: 1, cmd: COMMANDS.SET_VOLUME, volume: Number(volume) });
    if (!val.valid) {
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_VOLUME, status: 'rejected', state: this.state });
      throw new Error(val.error);
    }
    this.currentVolume = Number(volume);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_VOLUME, status: 'applied', state: this.state });
    return true;
  }

  async setPreset(preset) {
    const val = validateCommandPacket({ id: 1, cmd: COMMANDS.SET_PRESET, preset });
    if (!val.valid) {
      this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_PRESET, status: 'rejected', state: this.state });
      throw new Error(val.error);
    }
    this.currentPreset = preset;
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.SET_PRESET, status: 'applied', state: this.state });
    this.emit('log', { type: 'info', message: `[SIM] 사운드 프리셋 변경: ${preset.toUpperCase()}` });
    return true;
  }

  async ping() {
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.PING, status: 'applied', state: this.state });
    return 'PONG';
  }

  async getStatus() {
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: COMMANDS.STATUS, status: 'applied', state: this.state });
    return this.state;
  }

  setBabyState(babyState, autoSoothing) {
    this.babyState = babyState;
    this.autoSoothing = autoSoothing;
  }

  startLoop() {
    this.stopLoop();
    this.simTimer = setInterval(() => {
      this.tick();
    }, PROTOCOL_LIMITS.TELEMETRY_PERIOD_MS); // 200ms (5 Hz)
  }

  stopLoop() {
    if (this.simTimer) {
      clearInterval(this.simTimer);
      this.simTimer = null;
    }
  }

  tick() {
    this.uptimeMs += PROTOCOL_LIMITS.TELEMETRY_PERIOD_MS;
    const isRunning = (this.state === DeviceState.RUNNING);
    const isLocked = (this.state === DeviceState.SAFETY_LOCK || this.state === DeviceState.FAULT);

    // Soft start / stop ramping
    const targetAmp = (isRunning && !isLocked) ? this.currentAmplitude : 0.0;
    const rampRate = 0.04;
    if (this.currentRampedAmp < targetAmp) {
      this.currentRampedAmp = Math.min(targetAmp, this.currentRampedAmp + rampRate);
    } else if (this.currentRampedAmp > targetAmp) {
      this.currentRampedAmp = Math.max(targetAmp, this.currentRampedAmp - rampRate);
    }

    // Dynamic wave phase & noise
    this.phase += (this.currentFrequency * 2 * Math.PI) * 0.2;
    let noiseLevel = 0.02;
    if (this.babyState === 'light_sleep') noiseLevel = 0.06;
    if (this.babyState === 'fussing') noiseLevel = 0.15;
    if (this.babyState === 'crying') noiseLevel = 0.35;

    const vibFactor = this.currentRampedAmp;
    const ax = (Math.sin(this.phase) * vibFactor * 0.8) + ((Math.random() - 0.5) * noiseLevel);
    const ay = (Math.cos(this.phase) * vibFactor * 0.6) + ((Math.random() - 0.5) * noiseLevel);
    const az = 1.0 + (Math.sin(this.phase * 0.5) * vibFactor * 0.4) + ((Math.random() - 0.5) * noiseLevel * 0.5);

    // Power & thermal telemetry (clearly marked simulated)
    const pvdd = isLocked ? 5.0 : (12.10 + (Math.random() - 0.5) * 0.05);
    const vdd33 = 3.31 + (Math.random() - 0.5) * 0.01;
    const temp = 39.0 + (this.currentRampedAmp * 8.0) + ((Math.random() - 0.5) * 0.2);

    const telemetry = {
      type: 'telemetry',
      protocol: this.deviceInfo.protocol,
      firmware: this.deviceInfo.firmware,
      uptime_ms: this.uptimeMs,
      state: this.state,
      safety_lock: isLocked,
      frequency_hz: this.currentFrequency,
      amplitude_scale: Number(this.currentRampedAmp.toFixed(3)),
      accel_g: {
        x: Number(ax.toFixed(3)),
        y: Number(ay.toFixed(3)),
        z: Number(az.toFixed(3))
      },
      pvdd_v: Number(pvdd.toFixed(2)),
      vdd_3v3_v: Number(vdd33.toFixed(2)),
      amp_temp_c: Number(temp.toFixed(1)),
      volume: this.currentVolume,
      preset: this.currentPreset,
      simulated: true
    };

    this.emit('telemetry', telemetry);
  }
}

if (typeof window !== 'undefined') {
  window.SimulationDeviceProvider = SimulationDeviceProvider;
}
