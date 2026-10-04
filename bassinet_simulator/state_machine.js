/**
 * MAJN Smart Bassinet - State Machine & Policy Engine
 * Formalized State Transitions and Control Permissions
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

const ALLOWED_TRANSITIONS = new Map([
  [DeviceState.DISCONNECTED, new Set([DeviceState.CONNECTING, DeviceState.READY, DeviceState.CONNECTED])],
  [DeviceState.CONNECTING, new Set([DeviceState.CONNECTED, DeviceState.READY, DeviceState.DISCONNECTED, DeviceState.FAULT])],
  [DeviceState.CONNECTED, new Set([DeviceState.READY, DeviceState.DISCONNECTED, DeviceState.FAULT, DeviceState.SAFETY_LOCK])],
  [DeviceState.READY, new Set([DeviceState.RUNNING, DeviceState.FAULT, DeviceState.SAFETY_LOCK, DeviceState.DISCONNECTED])],
  [DeviceState.RUNNING, new Set([DeviceState.READY, DeviceState.FAULT, DeviceState.SAFETY_LOCK, DeviceState.DISCONNECTED])],
  [DeviceState.FAULT, new Set([DeviceState.READY, DeviceState.DISCONNECTED])],
  [DeviceState.SAFETY_LOCK, new Set([DeviceState.READY, DeviceState.DISCONNECTED])]
]);

export class StateMachine {
  constructor(initialState = DeviceState.DISCONNECTED) {
    this.currentState = initialState;
    this.history = [{ state: initialState, timestamp: Date.now(), reason: 'Initial state' }];
  }

  canTransitionTo(nextState) {
    const allowed = ALLOWED_TRANSITIONS.get(this.currentState);
    return allowed ? allowed.has(nextState) : false;
  }

  transition(nextState, reason = '') {
    if (this.currentState === nextState) return true;

    // Safety rule: ESTOP / FAULT / SAFETY_LOCK can be forced from any active state
    const isEmergency = (nextState === DeviceState.FAULT || nextState === DeviceState.SAFETY_LOCK);
    if (!this.canTransitionTo(nextState) && !isEmergency) {
      if (typeof console !== 'undefined' && console.warn) {
        console.warn(`[StateMachine] Illegal transition: ${this.currentState} -> ${nextState}`);
      }
      return false;
    }

    const prev = this.currentState;
    this.currentState = nextState;
    this.history.push({ state: nextState, previous: prev, timestamp: Date.now(), reason });
    if (this.history.length > 50) this.history.shift();
    return true;
  }

  get state() {
    return this.currentState;
  }

  canStart() {
    return this.currentState === DeviceState.READY;
  }

  canStop() {
    return this.currentState === DeviceState.RUNNING;
  }

  canEmergencyStop() {
    return true; // Always allowed
  }

  canReset() {
    return this.currentState === DeviceState.FAULT || this.currentState === DeviceState.SAFETY_LOCK;
  }

  canModifyParameters() {
    return this.currentState === DeviceState.READY || this.currentState === DeviceState.RUNNING;
  }
}

if (typeof window !== 'undefined') {
  window.MAJN_STATE = {
    DeviceState,
    StateMachine
  };
}
