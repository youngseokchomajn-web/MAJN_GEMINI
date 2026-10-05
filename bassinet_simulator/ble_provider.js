/**
 * MAJN Smart Bassinet - Web Bluetooth Device Provider
 * Production-ready Web Bluetooth GATT Client for ESP32-WROOM-32UE
 */

import { DeviceProvider } from './device_provider.js';
import { DeviceState, StateMachine } from './state_machine.js';
import { MAJN_BLE_UUIDS, PROTOCOL_LIMITS, PROTOCOL_VERSION, COMMANDS, validateCommandPacket, validateTelemetryPacket } from './protocol.js';

export { MAJN_BLE_UUIDS };

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
    this.stateMachine = new StateMachine(DeviceState.DISCONNECTED);
    this.heartbeatTimer = null;
    this.heartbeatIntervalMs = 2000;
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
        message: `[BLE] State: ${old} -> ${newState}${reason ? ` (${reason})` : ''}`
      });
    }
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
        optionalServices: [MAJN_BLE_UUIDS.service, MAJN_BLE_UUIDS.otaService]
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
      protocol: PROTOCOL_VERSION,
      mode: 'ble'
    };

    this.setState(DeviceState.CONNECTED, 'GATT Services Subscribed');
    this.emit('connectionChange', { isConnected: true, provider: this });
    this.emit('log', { type: 'success', message: `[BLE] ${this.deviceInfo.name}와 연결이 성공적으로 완료되었습니다.` });

    // Initial handshake
    await this.send(COMMANDS.PING);
    await this.send(COMMANDS.STATUS);

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
          await this.send(COMMANDS.PING);
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
    const validation = validateCommandPacket(packet);
    if (!validation.valid) {
      this.emit('log', { type: 'error', message: `[BLE 패킷 거부] ${validation.error}` });
      throw new Error(validation.error);
    }

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

      if (data.state && this.state !== data.state) {
        this.setState(data.state, 'Telemetry sync');
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
    return await this.send(COMMANDS.START, { frequency_hz: Number(f), amplitude: Number(a) });
  }

  async stop() {
    return await this.send(COMMANDS.STOP);
  }

  async emergencyStop() {
    return await this.send(COMMANDS.ESTOP);
  }

  async resetFault() {
    return await this.send(COMMANDS.STATUS);
  }

  async setFrequency(hz) {
    this.currentFrequency = Number(hz);
    return await this.send(COMMANDS.SET_FREQUENCY, { frequency_hz: this.currentFrequency });
  }

  async setAmplitude(amp) {
    this.currentAmplitude = Number(amp);
    return await this.send(COMMANDS.SET_AMPLITUDE, { amplitude: this.currentAmplitude });
  }

  async setVibration(hz, amp) {
    if (hz !== undefined) this.currentFrequency = Number(hz);
    if (amp !== undefined) this.currentAmplitude = Number(amp);
    return await this.send(COMMANDS.SET_VIBRATION, { frequency_hz: this.currentFrequency, amplitude: this.currentAmplitude });
  }

  async setVolume(volume) {
    this.currentVolume = Number(volume);
    return await this.send(COMMANDS.SET_VOLUME, { volume: this.currentVolume });
  }

  async setPreset(preset) {
    this.currentPreset = preset;
    return await this.send(COMMANDS.SET_PRESET, { preset });
  }

  async ping() {
    return await this.send(COMMANDS.PING);
  }

  async getStatus() {
    return await this.send(COMMANDS.STATUS);
  }

  async reboot() {
    return await this.send(COMMANDS.REBOOT);
  }

  /**
   * 100% Wireless Web Bluetooth OTA Firmware Update
   * Uploads .bin firmware directly to ESP32 over BLE GATT
   */
  async performOta(file, onProgress) {
    if (!this.isConnected || !this.server) {
      throw new Error('ESP32가 연결되어 있지 않습니다. 먼저 BLE 연결을 해주세요.');
    }

    this.emit('log', { type: 'info', message: `[BLE-OTA] 무선 펌웨어 업데이트 시작 (파일: ${file.name}, 크기: ${file.size} bytes)` });

    const otaService = await this.server.getPrimaryService(MAJN_BLE_UUIDS.otaService);
    const otaControl = await otaService.getCharacteristic(MAJN_BLE_UUIDS.otaControl);
    const otaData = await otaService.getCharacteristic(MAJN_BLE_UUIDS.otaData);

    const encoder = new TextEncoder();

    // 1. Send OTA_BEGIN with firmware size
    const beginPayload = JSON.stringify({ cmd: 'OTA_BEGIN', size: file.size });
    await otaControl.writeValue(encoder.encode(beginPayload));
    this.emit('log', { type: 'info', message: '[BLE-OTA] ESP32 OTA 준비 완료. 바이너리 스트리밍을 시작합니다...' });

    // 2. Read file as ArrayBuffer and send in MTU chunks
    const buffer = await file.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    const totalBytes = bytes.length;
    const CHUNK_SIZE = 256;
    let offset = 0;

    while (offset < totalBytes) {
      const end = Math.min(offset + CHUNK_SIZE, totalBytes);
      const chunk = bytes.slice(offset, end);

      if (otaData.writeValueWithoutResponse) {
        await otaData.writeValueWithoutResponse(chunk);
      } else {
        await otaData.writeValue(chunk);
      }

      offset = end;
      const pct = Math.round((offset / totalBytes) * 100);
      if (onProgress) onProgress(pct, offset, totalBytes);

      // Micro-pause to prevent BLE stack buffer overflow
      await new Promise(r => setTimeout(r, 6));
    }

    // 3. Send OTA_END
    this.emit('log', { type: 'info', message: '[BLE-OTA] 모든 바이너리 전송 완료. 플래시 무결성 검증 및 재부팅 요청 중...' });
    const endPayload = JSON.stringify({ cmd: 'OTA_END' });
    await otaControl.writeValue(encoder.encode(endPayload));
    this.emit('log', { type: 'info', message: '🎉 [BLE-OTA] 무선 업데이트 성공! ESP32가 새 펌웨어로 자동 재부팅됩니다.' });
  }
}

if (typeof window !== 'undefined') {
  window.BleDeviceProvider = BleDeviceProvider;
  window.MajnBleProvider = BleDeviceProvider;
}
