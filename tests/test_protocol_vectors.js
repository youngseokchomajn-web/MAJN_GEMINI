/**
 * MAJN Protocol & State Machine Automated Test Suite
 * Validates protocol vectors, state transitions, validation boundaries, and diagnostics
 */

import { PROTOCOL_VERSION, PROTOCOL_LIMITS, COMMANDS, ACK_STATUS, validateCommandPacket, validateTelemetryPacket } from '../bassinet_simulator/protocol.js';
import { DeviceState, StateMachine } from '../bassinet_simulator/state_machine.js';
import { DiagnosticsMonitor } from '../bassinet_simulator/diagnostics.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    print(`  [PASS] ${message}`);
  } else {
    failed++;
    print(`  [FAIL] ${message}`);
  }
}

print('=== 1. PROTOCOL VECTOR TESTS ===');

// PING / STATUS / STOP / ESTOP
assert(validateCommandPacket({ id: 1, cmd: COMMANDS.PING }).valid, 'Valid PING packet');
assert(validateCommandPacket({ id: 2, cmd: COMMANDS.STATUS }).valid, 'Valid STATUS packet');
assert(validateCommandPacket({ id: 3, cmd: COMMANDS.STOP }).valid, 'Valid STOP packet');
assert(validateCommandPacket({ id: 4, cmd: COMMANDS.ESTOP }).valid, 'Valid ESTOP packet');

// START validation
assert(validateCommandPacket({ id: 5, cmd: COMMANDS.START, frequency_hz: 45, amplitude: 0.2 }).valid, 'Valid START packet with params');
assert(!validateCommandPacket({ id: 6, cmd: COMMANDS.START, frequency_hz: 20 }).valid, 'START with frequency < 30Hz rejected');
assert(!validateCommandPacket({ id: 7, cmd: COMMANDS.START, frequency_hz: 70 }).valid, 'START with frequency > 65Hz rejected');
assert(!validateCommandPacket({ id: 8, cmd: COMMANDS.START, amplitude: 0.6 }).valid, 'START with amplitude > 0.5 rejected');
assert(!validateCommandPacket({ id: 9, cmd: COMMANDS.START, amplitude: -0.1 }).valid, 'START with amplitude < 0.0 rejected');

// SET_FREQUENCY
assert(validateCommandPacket({ id: 10, cmd: COMMANDS.SET_FREQUENCY, frequency_hz: 30 }).valid, 'SET_FREQUENCY at 30Hz lower bound');
assert(validateCommandPacket({ id: 11, cmd: COMMANDS.SET_FREQUENCY, frequency_hz: 65 }).valid, 'SET_FREQUENCY at 65Hz upper bound');
assert(!validateCommandPacket({ id: 12, cmd: COMMANDS.SET_FREQUENCY, frequency_hz: 29.9 }).valid, 'SET_FREQUENCY below 30Hz rejected');
assert(!validateCommandPacket({ id: 13, cmd: COMMANDS.SET_FREQUENCY, frequency_hz: 65.1 }).valid, 'SET_FREQUENCY above 65Hz rejected');

// SET_AMPLITUDE
assert(validateCommandPacket({ id: 14, cmd: COMMANDS.SET_AMPLITUDE, amplitude: 0.0 }).valid, 'SET_AMPLITUDE at 0.0 lower bound');
assert(validateCommandPacket({ id: 15, cmd: COMMANDS.SET_AMPLITUDE, amplitude: 0.5 }).valid, 'SET_AMPLITUDE at 0.5 upper bound');
assert(!validateCommandPacket({ id: 16, cmd: COMMANDS.SET_AMPLITUDE, amplitude: 0.51 }).valid, 'SET_AMPLITUDE above 0.5 rejected');

// SET_VOLUME
assert(validateCommandPacket({ id: 17, cmd: COMMANDS.SET_VOLUME, volume: 0 }).valid, 'SET_VOLUME at 0');
assert(validateCommandPacket({ id: 18, cmd: COMMANDS.SET_VOLUME, volume: 100 }).valid, 'SET_VOLUME at 100');
assert(!validateCommandPacket({ id: 19, cmd: COMMANDS.SET_VOLUME, volume: 101 }).valid, 'SET_VOLUME > 100 rejected');
assert(!validateCommandPacket({ id: 20, cmd: COMMANDS.SET_VOLUME, volume: -1 }).valid, 'SET_VOLUME < 0 rejected');

// SET_PRESET
assert(validateCommandPacket({ id: 21, cmd: COMMANDS.SET_PRESET, preset: 'pink' }).valid, 'SET_PRESET pink');
assert(validateCommandPacket({ id: 22, cmd: COMMANDS.SET_PRESET, preset: 'heartbeat' }).valid, 'SET_PRESET heartbeat');
assert(validateCommandPacket({ id: 23, cmd: COMMANDS.SET_PRESET, preset: 'lullaby' }).valid, 'SET_PRESET lullaby');
assert(validateCommandPacket({ id: 24, cmd: COMMANDS.SET_PRESET, preset: 'off' }).valid, 'SET_PRESET off');
assert(!validateCommandPacket({ id: 25, cmd: COMMANDS.SET_PRESET, preset: 'rock_music' }).valid, 'SET_PRESET unknown preset rejected');

// Unknown command
assert(!validateCommandPacket({ id: 26, cmd: 'INVALID_CMD' }).valid, 'Unknown command rejected');

print('=== 2. STATE MACHINE TESTS ===');
const sm = new StateMachine(DeviceState.DISCONNECTED);

assert(sm.state === DeviceState.DISCONNECTED, 'Initial state DISCONNECTED');
assert(!sm.canStart(), 'Cannot start while DISCONNECTED');

assert(sm.transition(DeviceState.CONNECTING), 'Transition to CONNECTING');
assert(sm.transition(DeviceState.READY), 'Transition to READY');
assert(sm.canStart(), 'Can start while READY');
assert(!sm.canStop(), 'Cannot stop while READY (already stopped)');

assert(sm.transition(DeviceState.RUNNING), 'Transition to RUNNING');
assert(!sm.canStart(), 'Cannot start while RUNNING');
assert(sm.canStop(), 'Can stop while RUNNING');

assert(sm.transition(DeviceState.READY), 'Transition STOP -> READY');
assert(sm.transition(DeviceState.RUNNING), 'Transition START -> RUNNING');

// Emergency Stop
assert(sm.transition(DeviceState.SAFETY_LOCK, 'ESTOP'), 'Transition RUNNING -> SAFETY_LOCK');
assert(!sm.canStart(), 'Cannot start during SAFETY_LOCK');
assert(!sm.canStop(), 'Cannot normal stop during SAFETY_LOCK');
assert(sm.canReset(), 'Can reset during SAFETY_LOCK');

// Illegal transition while locked
assert(!sm.transition(DeviceState.RUNNING), 'Illegal transition SAFETY_LOCK -> RUNNING blocked');

// Reset to ready
assert(sm.transition(DeviceState.READY, 'Reset'), 'Transition SAFETY_LOCK -> READY allowed on reset');
assert(sm.canStart(), 'Can start again after reset');

print('=== 3. TELEMETRY & DIAGNOSTICS TESTS ===');
const diag = new DiagnosticsMonitor();
diag.recordCommand(1, COMMANDS.PING);
diag.recordAck({ type: 'ack', id: 1, cmd: COMMANDS.PING, status: 'applied', state: 'READY' });
assert(diag.commandsSent === 1, 'Diagnostics tracked command');
assert(diag.acksReceived === 1, 'Diagnostics tracked ACK');

const validTelem = {
  type: 'telemetry',
  protocol: 1,
  firmware: '0.2.0-ble',
  uptime_ms: 12345,
  state: 'READY',
  safety_lock: false,
  frequency_hz: 45.0,
  amplitude_scale: 0.2,
  accel_g: { x: 0.01, y: -0.02, z: 1.00 },
  pvdd_v: null,
  vdd_3v3_v: null,
  amp_temp_c: null
};

assert(validateTelemetryPacket(validTelem), 'Valid telemetry packet with null unmeasured fields');
diag.recordTelemetry(validTelem);
assert(diag.telemetryPackets === 1, 'Telemetry packet tracked');

print(`\n========================================`);
print(`TEST SUMMARY: ${passed} PASSED, ${failed} FAILED`);
print(`========================================`);

if (failed > 0) {
  throw new Error(`Test suite failed with ${failed} failures`);
}
