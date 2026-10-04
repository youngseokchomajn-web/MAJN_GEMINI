/**
 * MAJN Smart Bassinet - Base Device Provider & EventEmitter
 */

import { DeviceState } from './state_machine.js';
import { PROTOCOL_VERSION } from './protocol.js';

export { DeviceState };

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
    this.isConnected = false;
    this.deviceInfo = {
      name: 'Unknown',
      firmware: 'N/A',
      protocol: PROTOCOL_VERSION,
      mode: modeName
    };
    this.currentFrequency = 45.0;
    this.currentAmplitude = 0.2; // 0.0 ~ 0.5 (Scale)
    this.currentVolume = 45;      // 0 ~ 100
    this.currentPreset = 'pink';
  }

  get state() {
    return DeviceState.DISCONNECTED;
  }

  setState(newState, reason = '') {
    // Overridden by subclasses with stateMachine
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

if (typeof window !== 'undefined') {
  window.DeviceState = DeviceState;
  window.EventEmitter = EventEmitter;
  window.DeviceProvider = DeviceProvider;
}
