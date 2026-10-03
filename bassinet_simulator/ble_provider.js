// MAJN Web Bluetooth provider
// Mac Chrome / HTTPS or localhost only.

const MAJN_BLE = {
  service: '7b4d0001-7a6a-4d41-9a4d-4d414a4a4e01',
  command: '7b4d0002-7a6a-4d41-9a4d-4d414a4a4e01',
  telemetry: '7b4d0003-7a6a-4d41-9a4d-4d414a4a4e01',
  event: '7b4d0004-7a6a-4d41-9a4d-4d414a4a4e01'
};

class MajnBleProvider {
  constructor() {
    this.device = null;
    this.command = null;
    this.telemetry = null;
    this.event = null;
    this.connected = false;
    this.sequence = 1;
    this.decoder = new TextDecoder();
  }

  log(type, message) {
    if (typeof logMessage === 'function') logMessage(type, message);
  }

  async connect() {
    if (!navigator.bluetooth) {
      throw new Error('이 브라우저는 Web Bluetooth를 지원하지 않습니다. Mac Chrome을 사용하세요.');
    }

    this.device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [MAJN_BLE.service] }],
      optionalServices: [MAJN_BLE.service]
    });

    this.device.addEventListener('gattserverdisconnected', () => {
      this.connected = false;
      this.updateConnectionUI(false);
      this.log('warn', '[BLE] ESP32 연결이 끊겼습니다. 안전정지 상태를 확인하세요.');
    });

    const server = await this.device.gatt.connect();
    const service = await server.getPrimaryService(MAJN_BLE.service);

    this.command = await service.getCharacteristic(MAJN_BLE.command);
    this.telemetry = await service.getCharacteristic(MAJN_BLE.telemetry);
    this.event = await service.getCharacteristic(MAJN_BLE.event);

    await this.telemetry.startNotifications();
    await this.event.startNotifications();
    this.telemetry.addEventListener('characteristicvaluechanged', e => this.handleTelemetry(e));
    this.event.addEventListener('characteristicvaluechanged', e => this.handleEvent(e));

    this.connected = true;
    this.updateConnectionUI(true);
    this.log('success', '[BLE] MAJN-Bassinet 연결 완료.');

    await this.send('PING');
    await this.send('STATUS');
  }

  async disconnect() {
    if (this.device?.gatt?.connected) this.device.gatt.disconnect();
    this.connected = false;
    this.updateConnectionUI(false);
  }

  async send(cmd, payload = {}) {
    if (!this.connected || !this.command) {
      throw new Error('ESP32 BLE가 연결되지 않았습니다.');
    }
    const packet = { id: this.sequence++, cmd, ...payload };
    const data = new TextEncoder().encode(JSON.stringify(packet));
    await this.command.writeValue(data);
    return packet.id;
  }

  handleTelemetry(event) {
    try {
      const data = JSON.parse(this.decoder.decode(event.target.value));
      if (data.type !== 'telemetry') return;
      this.updateConnectionUI(true, data);
      this.updateTelemetryUI(data);
      window.dispatchEvent(new CustomEvent('majn-telemetry', { detail: data }));
    } catch (e) {
      this.log('error', '[BLE] telemetry JSON parse 실패');
    }
  }

  handleEvent(event) {
    try {
      const data = JSON.parse(this.decoder.decode(event.target.value));
      if (data.type === 'ack') {
        this.log(data.status === 'rejected' || data.status === 'fault' ? 'error' : 'info',
          `[BLE ACK] #${data.id} ${data.cmd}: ${data.status}`);
      }
      window.dispatchEvent(new CustomEvent('majn-event', { detail: data }));
    } catch (e) {
      this.log('error', '[BLE] event JSON parse 실패');
    }
  }

  updateConnectionUI(connected, telemetry = null) {
    const title = document.querySelector('.status-title');
    const indicator = document.querySelector('.status-indicator');
    if (title) title.textContent = connected ? 'ESP32 BLE Connected' : 'ESP32 BLE Disconnected';
    if (indicator) indicator.classList.toggle('online', connected);

    const badge = document.querySelector('.mode-badge');
    if (badge) badge.innerHTML = connected
      ? '<i class="fa-solid fa-bluetooth-b"></i> ESP32 BLE 실물 연결'
      : '<i class="fa-solid fa-flask"></i> SIMULATION';

    const btn = document.getElementById('btn-ble-connect');
    if (btn) btn.textContent = connected ? 'BLE 해제' : 'ESP32 BLE 연결';
    if (telemetry) {
      const state = telemetry.state || 'UNKNOWN';
      document.getElementById('wifi-rssi').textContent = 'BLE';
      document.getElementById('pvdd-val').textContent = telemetry.pvdd_v == null ? 'N/A' : telemetry.pvdd_v.toFixed(2) + 'V';
      document.getElementById('vdd3v3-val').textContent = telemetry.vdd_3v3_v == null ? 'N/A' : telemetry.vdd_3v3_v.toFixed(2) + 'V';
      document.getElementById('pvdd-voltage').textContent = telemetry.pvdd_v == null ? 'N/A' : telemetry.pvdd_v.toFixed(2) + ' V';
      document.getElementById('vdd-voltage').textContent = telemetry.vdd_3v3_v == null ? 'N/A' : telemetry.vdd_3v3_v.toFixed(2) + ' V';
      document.getElementById('amp-temp').textContent = telemetry.amp_temp_c == null ? 'N/A' : telemetry.amp_temp_c.toFixed(1) + ' °C';
      document.getElementById('sound-mode-txt').textContent = state;
    }
  }

  updateTelemetryUI(data) {
    if (!window.imuChart || typeof imuChart === 'undefined') return;
    chartDataX.shift(); chartDataX.push(data.accel_g.x);
    chartDataY.shift(); chartDataY.push(data.accel_g.y);
    chartDataZ.shift(); chartDataZ.push(data.accel_g.z);
    imuChart.update('none');
  }
}

window.majnBle = new MajnBleProvider();

document.addEventListener('DOMContentLoaded', () => {
  const connect = document.getElementById('btn-ble-connect');
  const start = document.getElementById('btn-device-start');
  const stop = document.getElementById('btn-device-stop');

  connect?.addEventListener('click', async () => {
    try {
      if (window.majnBle.connected) await window.majnBle.disconnect();
      else await window.majnBle.connect();
    } catch (e) {
      window.majnBle.log('error', '[BLE] ' + e.message);
      window.majnBle.updateConnectionUI(false);
    }
  });

  start?.addEventListener('click', async () => {
    try {
      await window.majnBle.send('START', {
        frequency_hz: Number(document.getElementById('frequency-slider')?.value || 45),
        amplitude: Number(document.getElementById('bounce-slider')?.value || 2) / 10
      });
    } catch (e) { window.majnBle.log('error', '[BLE] ' + e.message); }
  });

  stop?.addEventListener('click', async () => {
    try { await window.majnBle.send('STOP'); }
    catch (e) { window.majnBle.log('error', '[BLE] ' + e.message); }
  });

  document.getElementById('bounce-slider')?.addEventListener('input', async e => {
    if (!window.majnBle.connected) return;
    try {
      await window.majnBle.send('SET_VIBRATION', {
        frequency_hz: Number(document.getElementById('frequency-slider')?.value || 45),
        amplitude: Number(e.target.value) / 10
      });
    } catch (err) { window.majnBle.log('error', '[BLE] ' + err.message); }
  });

  document.getElementById('volume-slider')?.addEventListener('input', async e => {
    if (!window.majnBle.connected) return;
    try { await window.majnBle.send('SET_VOLUME', { volume: Number(e.target.value) }); }
    catch (err) { window.majnBle.log('error', '[BLE] ' + err.message); }
  });
});
