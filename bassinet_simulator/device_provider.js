/**
 * MAJN Smart Bassinet - Common Device Provider Architecture
 * 
 * Defines the unified DeviceProvider interface implemented by:
 * - SimulationDeviceProvider (pure software simulation for UI & scenario testing)
 * - BleDeviceProvider (real hardware Web Bluetooth communication for ESP32)
 */

export const DeviceState = Object.freeze({
  DISCONNECTED: 'DISCONNECTED',
  CONNECTING: 'CONNECTING',
  CONNECTED: 'CONNECTED',
  READY: 'READY',
  RUNNING: 'RUNNING',
  FAULT: 'FAULT',
  SAFETY_LOCK: 'SAFETY_LOCK'
});

export class EventEmitter {
  constructor() {
    this._listeners = new Map();
  }

  on(event, handler) {
    if (!this._listeners.has(event)) {
      this._listeners.set(event, new Set());
    }
    this._listeners.get(event).add(handler);
    return () => this.off(event, handler);
  }

  off(event, handler) {
    if (this._listeners.has(event)) {
      this._listeners.get(event).delete(handler);
    }
  }

  emit(event, ...args) {
    if (this._listeners.has(event)) {
      for (const handler of this._listeners.get(event)) {
        try {
          handler(...args);
        } catch (err) {
          console.error(`[EventEmitter] Error in listener for ${event}:`, err);
        }
      }
    }
  }
}

/**
 * Base abstract DeviceProvider class
 */
export class DeviceProvider extends EventEmitter {
  constructor(modeName) {
    super();
    this.mode = modeName; // 'simulation' | 'ble'
    this.state = DeviceState.DISCONNECTED;
    this.isConnected = false;
    this.deviceInfo = {
      name: 'Unknown',
      firmware: 'N/A',
      protocol: 1,
      mode: modeName
    };
    this.currentFrequency = 45.0;
    this.currentAmplitude = 0.2; // 0.0 ~ 0.5 (Scale)
    this.currentVolume = 45;      // 0 ~ 100
    this.currentPreset = 'pink';
  }

  setState(newState, reason = '') {
    if (this.state !== newState) {
      const oldState = this.state;
      this.state = newState;
      this.emit('stateChange', { state: newState, oldState, reason });
      this.emit('log', {
        type: (newState === DeviceState.FAULT || newState === DeviceState.SAFETY_LOCK) ? 'error' : 'info',
        message: `[${this.mode.toUpperCase()}] State changed: ${oldState} -> ${newState}${reason ? ' (' + reason + ')' : ''}`
      });
    }
  }

  async connect() { throw new Error('connect() not implemented'); }
  async disconnect() { throw new Error('disconnect() not implemented'); }
  async start(options = {}) { throw new Error('start() not implemented'); }
  async stop() { throw new Error('stop() not implemented'); }
  async emergencyStop() { throw new Error('emergencyStop() not implemented'); }
  async resetFault() { throw new Error('resetFault() not implemented'); }
  async setFrequency(hz) { throw new Error('setFrequency() not implemented'); }
  async setAmplitude(amp) { throw new Error('setAmplitude() not implemented'); }
  async setVibration(hz, amp) { throw new Error('setVibration() not implemented'); }
  async setVolume(volume) { throw new Error('setVolume() not implemented'); }
  async setPreset(preset) { throw new Error('setPreset() not implemented'); }
  async ping() { throw new Error('ping() not implemented'); }
  async getStatus() { throw new Error('getStatus() not implemented'); }
}

/**
 * SimulationDeviceProvider
 * Fully standalone software emulation of the ESP32 closed-loop controller
 */
export class SimulationDeviceProvider extends DeviceProvider {
  constructor() {
    super('simulation');
    this.deviceInfo = {
      name: 'MAJN-Virtual-Simulator',
      firmware: '0.2.0-sim',
      protocol: 1,
      mode: 'simulation'
    };
    this.simTimer = null;
    this.uptimeMs = 0;
    this.babyState = 'sleep';
    this.autoSoothing = true;
    this.currentRampedAmp = 0.0;
    this.phase = 0;
  }

  async connect() {
    this.setState(DeviceState.CONNECTING, 'Initializing virtual simulator');
    await new Promise(r => setTimeout(r, 200));

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
    if (this.state === DeviceState.FAULT || this.state === DeviceState.SAFETY_LOCK) {
      throw new Error('안전 잠금(SAFETY_LOCK) 상태입니다. 먼저 비상 정지 해제/리셋을 수행하세요.');
    }
    if (options.frequency_hz !== undefined) this.currentFrequency = options.frequency_hz;
    if (options.amplitude !== undefined) this.currentAmplitude = options.amplitude;

    this.setState(DeviceState.RUNNING, 'Start vibration');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'START', status: 'applied', state: this.state });
    this.emit('log', {
      type: 'success',
      message: `[SIM] 진동 구동 시작: ${this.currentFrequency}Hz, scale ${(this.currentAmplitude).toFixed(2)}`
    });
    return true;
  }

  async stop() {
    if (this.state === DeviceState.FAULT || this.state === DeviceState.SAFETY_LOCK) {
      return; // ESTOP state remains
    }
    this.setState(DeviceState.READY, 'Stop vibration');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'STOP', status: 'applied', state: this.state });
    this.emit('log', { type: 'info', message: '[SIM] 진동 구동 정지 (대기 상태 복귀)' });
    return true;
  }

  async emergencyStop() {
    this.currentRampedAmp = 0.0;
    this.setState(DeviceState.SAFETY_LOCK, '비상 정지(ESTOP) 트리거');
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'ESTOP', status: 'applied', state: this.state });
    this.emit('log', {
      type: 'error',
      message: '[SIM ESTOP] 비상 정지 발동! 하드웨어 부스트(12V) 및 앰프 전원 즉시 차단됨.'
    });
    return true;
  }

  async resetFault() {
    if (this.state === DeviceState.FAULT || this.state === DeviceState.SAFETY_LOCK) {
      this.setState(DeviceState.READY, 'Manual fault reset');
      this.emit('log', { type: 'info', message: '[SIM] 안전 잠금 상태가 정상 해제되었습니다.' });
      return true;
    }
    return false;
  }

  async setFrequency(hz) {
    if (hz < 30 || hz > 65) throw new Error('Frequency must be between 30Hz and 65Hz');
    this.currentFrequency = Number(hz);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'SET_FREQUENCY', status: 'applied', state: this.state });
    return true;
  }

  async setAmplitude(amp) {
    if (amp < 0 || amp > 0.5) throw new Error('Amplitude scale must be between 0.0 and 0.5');
    this.currentAmplitude = Number(amp);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'SET_AMPLITUDE', status: 'applied', state: this.state });
    return true;
  }

  async setVibration(hz, amp) {
    if (hz !== undefined) await this.setFrequency(hz);
    if (amp !== undefined) await this.setAmplitude(amp);
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'SET_VIBRATION', status: 'applied', state: this.state });
    return true;
  }

  async setVolume(volume) {
    this.currentVolume = Math.min(100, Math.max(0, Number(volume)));
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'SET_VOLUME', status: 'applied', state: this.state });
    return true;
  }

  async setPreset(preset) {
    this.currentPreset = preset;
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'SET_PRESET', status: 'applied', state: this.state });
    this.emit('log', { type: 'info', message: `[SIM] 사운드 프리셋 변경: ${preset.toUpperCase()}` });
    return true;
  }

  async ping() {
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'PING', status: 'applied', state: this.state });
    return 'PONG';
  }

  async getStatus() {
    this.emit('ack', { type: 'ack', id: Date.now(), cmd: 'STATUS', status: 'applied', state: this.state });
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
    }, 100); // 10 Hz
  }

  stopLoop() {
    if (this.simTimer) {
      clearInterval(this.simTimer);
      this.simTimer = null;
    }
  }

  tick() {
    this.uptimeMs += 100;
    const isRunning = (this.state === DeviceState.RUNNING);
    const isLocked = (this.state === DeviceState.SAFETY_LOCK || this.state === DeviceState.FAULT);

    // Soft start / stop ramping
    const targetAmp = (isRunning && !isLocked) ? this.currentAmplitude : 0.0;
    const rampRate = 0.02;
    if (this.currentRampedAmp < targetAmp) {
      this.currentRampedAmp = Math.min(targetAmp, this.currentRampedAmp + rampRate);
    } else if (this.currentRampedAmp > targetAmp) {
      this.currentRampedAmp = Math.max(targetAmp, this.currentRampedAmp - rampRate);
    }

    // Vibration wave calculation
    this.phase += (this.currentFrequency * 2 * Math.PI) * 0.1;
    let noiseLevel = 0.02;
    if (this.babyState === 'light_sleep') noiseLevel = 0.06;
    if (this.babyState === 'fussing') noiseLevel = 0.15;
    if (this.babyState === 'crying') noiseLevel = 0.35;

    const vibFactor = this.currentRampedAmp;
    const ax = (Math.sin(this.phase) * vibFactor * 0.8) + ((Math.random() - 0.5) * noiseLevel);
    const ay = (Math.cos(this.phase) * vibFactor * 0.6) + ((Math.random() - 0.5) * noiseLevel);
    const az = 1.0 + (Math.sin(this.phase * 0.5) * vibFactor * 0.4) + ((Math.random() - 0.5) * noiseLevel * 0.5);

    // Simulation power & temp (clearly simulated)
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

/**
 * BleDeviceProvider
 * Real ESP32 BLE GATT client via Web Bluetooth
 */
export const MAJN_BLE_UUIDS = Object.freeze({
  service: '7b4d0001-7a6a-4d41-9a4d-4d414a4a4e01',
  command: '7b4d0002-7a6a-4d41-9a4d-4d414a4a4e01',
  telemetry: '7b4d0003-7a6a-4d41-9a4d-4d414a4a4e01',
  event: '7b4d0004-7a6a-4d41-9a4d-4d414a4a4e01'
});

export class BleDeviceProvider extends DeviceProvider {
  constructor() {
    super('ble');
    this.device = null;
    this.server = null;
    this.commandChar = null;
    this.telemetryChar = null;
    this.eventChar = null;
    this.sequence = 1;
    this.decoder = new TextDecoder();
    this.heartbeatTimer = null;
    this.heartbeatIntervalMs = 2000;
  }

  async connect() {
    if (!navigator.bluetooth) {
      const msg = '이 브라우저는 Web Bluetooth를 지원하지 않습니다. Mac Chrome 환경(localhost 또는 HTTPS)에서 실행하세요.';
      this.emit('log', { type: 'error', message: msg });
      throw new Error(msg);
    }

    this.setState(DeviceState.CONNECTING, 'Requesting Bluetooth device');
    this.emit('log', { type: 'info', message: '[BLE] ESP32 블루투스 장치 검색 창을 엽니다...' });

    try {
      this.device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [MAJN_BLE_UUIDS.service] }],
        optionalServices: [MAJN_BLE_UUIDS.service]
      });
    } catch (err) {
      this.setState(DeviceState.DISCONNECTED, 'Device selection cancelled');
      throw new Error('블루투스 장치 선택이 취소되었습니다: ' + err.message);
    }

    this.device.addEventListener('gattserverdisconnected', () => {
      this.handleGattDisconnected();
    });

    this.emit('log', { type: 'info', message: `[BLE] ${this.device.name || 'MAJN 장치'}에 GATT 연결 중...` });
    this.server = await this.device.gatt.connect();

    this.emit('log', { type: 'info', message: '[BLE] MAJN 제어 서비스 탐색 중...' });
    const service = await this.server.getPrimaryService(MAJN_BLE_UUIDS.service);

    this.commandChar = await service.getCharacteristic(MAJN_BLE_UUIDS.command);
    this.telemetryChar = await service.getCharacteristic(MAJN_BLE_UUIDS.telemetry);
    this.eventChar = await service.getCharacteristic(MAJN_BLE_UUIDS.event);

    await this.telemetryChar.startNotifications();
    await this.eventChar.startNotifications();

    this.telemetryChar.addEventListener('characteristicvaluechanged', (e) => this.onTelemetryReceived(e));
    this.eventChar.addEventListener('characteristicvaluechanged', (e) => this.onEventReceived(e));

    this.isConnected = true;
    this.deviceInfo = {
      name: this.device.name || 'MAJN-Bassinet',
      firmware: '0.2.0-ble',
      protocol: 1,
      mode: 'ble'
    };

    this.setState(DeviceState.CONNECTED, 'GATT Services Subscribed');
    this.emit('connectionChange', { isConnected: true, provider: this });
    this.emit('log', { type: 'success', message: `[BLE] ${this.deviceInfo.name}와 연결이 성공적으로 완료되었습니다.` });

    // Initial handshakes
    await this.send('PING');
    await this.send('STATUS');

    this.startHeartbeat();
    return true;
  }

  async disconnect() {
    this.stopHeartbeat();
    if (this.device?.gatt?.connected) {
      this.device.gatt.disconnect();
    }
    this.handleGattDisconnected();
    return true;
  }

  handleGattDisconnected() {
    this.stopHeartbeat();
    this.isConnected = false;
    this.setState(DeviceState.DISCONNECTED, 'ESP32 BLE 연결 끊김');
    this.emit('connectionChange', { isConnected: false, provider: this });
    this.emit('log', {
      type: 'warn',
      message: '[BLE] ESP32와의 연결이 끊어졌습니다. 안전 규칙에 따라 장치는 자동 정지됩니다.'
    });
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(async () => {
      if (this.isConnected && this.commandChar) {
        try {
          await this.send('PING');
        } catch (err) {
          console.warn('[BLE] Heartbeat ping failed:', err);
        }
      }
    }, this.heartbeatIntervalMs);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  async send(cmd, payload = {}) {
    if (!this.isConnected || !this.commandChar) {
      throw new Error('ESP32 BLE 장치가 연결되어 있지 않습니다.');
    }
    const packet = { id: this.sequence++, cmd, ...payload };
    const jsonStr = JSON.stringify(packet);
    const data = new TextEncoder().encode(jsonStr);

    try {
      if (typeof this.commandChar.writeValueWithoutResponse === 'function') {
        await this.commandChar.writeValueWithoutResponse(data);
      } else {
        await this.commandChar.writeValue(data);
      }
    } catch (err) {
      this.emit('log', { type: 'error', message: `[BLE 전송 오류] ${cmd}: ${err.message}` });
      throw err;
    }
    return packet.id;
  }

  onTelemetryReceived(event) {
    try {
      const raw = this.decoder.decode(event.target.value);
      const data = JSON.parse(raw);
      if (data.type !== 'telemetry') return;

      if (data.protocol && this.deviceInfo.protocol !== data.protocol) {
        this.deviceInfo.protocol = data.protocol;
      }
      if (data.firmware && this.deviceInfo.firmware !== data.firmware) {
        this.deviceInfo.firmware = data.firmware;
      }

      // Sync state if returned from device
      if (data.state && this.state !== data.state) {
        this.setState(data.state, 'Telemetry status sync');
      }

      this.emit('telemetry', data);
    } catch (err) {
      this.emit('log', { type: 'error', message: '[BLE] Telemetry 수신 파싱 실패: ' + err.message });
    }
  }

  onEventReceived(event) {
    try {
      const raw = this.decoder.decode(event.target.value);
      const data = JSON.parse(raw);
      if (data.type === 'ack') {
        const isErr = (data.status === 'rejected' || data.status === 'fault');
        this.emit('log', {
          type: isErr ? 'error' : 'info',
          message: `[BLE ACK #${data.id}] ${data.cmd}: ${data.status}${data.state ? ` (State: ${data.state})` : ''}`
        });
        if (data.state && this.state !== data.state) {
          this.setState(data.state, `ACK ${data.cmd}`);
        }
        this.emit('ack', data);
      } else {
        this.emit('event', data);
      }
    } catch (err) {
      this.emit('log', { type: 'error', message: '[BLE] Event 수신 파싱 실패: ' + err.message });
    }
  }

  async start(options = {}) {
    const f = options.frequency_hz ?? this.currentFrequency;
    const a = options.amplitude ?? this.currentAmplitude;
    this.currentFrequency = f;
    this.currentAmplitude = a;
    return await this.send('START', { frequency_hz: Number(f), amplitude: Number(a) });
  }

  async stop() {
    return await this.send('STOP');
  }

  async emergencyStop() {
    return await this.send('ESTOP');
  }

  async resetFault() {
    return await this.send('STATUS');
  }

  async setFrequency(hz) {
    this.currentFrequency = Number(hz);
    return await this.send('SET_VIBRATION', { frequency_hz: this.currentFrequency, amplitude: this.currentAmplitude });
  }

  async setAmplitude(amp) {
    this.currentAmplitude = Number(amp);
    return await this.send('SET_VIBRATION', { frequency_hz: this.currentFrequency, amplitude: this.currentAmplitude });
  }

  async setVibration(hz, amp) {
    if (hz !== undefined) this.currentFrequency = Number(hz);
    if (amp !== undefined) this.currentAmplitude = Number(amp);
    return await this.send('SET_VIBRATION', { frequency_hz: this.currentFrequency, amplitude: this.currentAmplitude });
  }

  async setVolume(volume) {
    this.currentVolume = Number(volume);
    return await this.send('SET_VOLUME', { volume: this.currentVolume });
  }

  async setPreset(preset) {
    this.currentPreset = preset;
    return await this.send('SET_PRESET', { preset });
  }

  async ping() {
    return await this.send('PING');
  }

  async getStatus() {
    return await this.send('STATUS');
  }
}

if (typeof window !== 'undefined') {
  window.DeviceState = DeviceState;
  window.EventEmitter = EventEmitter;
  window.DeviceProvider = DeviceProvider;
  window.SimulationDeviceProvider = SimulationDeviceProvider;
  window.BleDeviceProvider = BleDeviceProvider;
  window.MAJN_BLE_UUIDS = MAJN_BLE_UUIDS;
}
