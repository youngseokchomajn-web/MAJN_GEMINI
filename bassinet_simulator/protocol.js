/**
 * MAJN BLE Protocol v1 Specification & Validation Module
 * Single Source of Truth for Web Bluetooth & Simulation Communications
 */

export const PROTOCOL_VERSION = 1;

export const MAJN_BLE_UUIDS = Object.freeze({
  service: '7b4d0001-7a6a-4d41-9a4d-4d414a4a4e01',
  command: '7b4d0002-7a6a-4d41-9a4d-4d414a4a4e01',
  telemetry: '7b4d0003-7a6a-4d41-9a4d-4d414a4a4e01',
  event: '7b4d0004-7a6a-4d41-9a4d-4d414a4a4e01'
});

export const PROTOCOL_LIMITS = Object.freeze({
  FREQUENCY_MIN_HZ: 30.0,
  FREQUENCY_MAX_HZ: 65.0,
  FREQUENCY_DEFAULT_HZ: 45.0,
  AMPLITUDE_MIN_SCALE: 0.0,
  AMPLITUDE_MAX_SCALE: 0.5,
  AMPLITUDE_DEFAULT_SCALE: 0.2,
  VOLUME_MIN: 0,
  VOLUME_MAX: 100,
  VOLUME_DEFAULT: 45,
  HEARTBEAT_TIMEOUT_MS: 5000,
  TELEMETRY_PERIOD_MS: 200,
  VALID_PRESETS: Object.freeze(['pink', 'heartbeat', 'lullaby', 'off'])
});

export const COMMANDS = Object.freeze({
  PING: 'PING',
  STATUS: 'STATUS',
  START: 'START',
  STOP: 'STOP',
  ESTOP: 'ESTOP',
  SET_VIBRATION: 'SET_VIBRATION',
  SET_FREQUENCY: 'SET_FREQUENCY',
  SET_AMPLITUDE: 'SET_AMPLITUDE',
  SET_VOLUME: 'SET_VOLUME',
  SET_PRESET: 'SET_PRESET',
  REBOOT: 'REBOOT'
});

export const ACK_STATUS = Object.freeze({
  RECEIVED: 'received',
  VALIDATED: 'validated',
  APPLIED: 'applied',
  REJECTED: 'rejected',
  FAULT: 'fault'
});

/**
 * Validates a command packet according to Protocol v1 rules
 */
export function validateCommandPacket(packet) {
  if (!packet || typeof packet !== 'object') {
    return { valid: false, error: 'Packet must be an object' };
  }
  if (typeof packet.id !== 'number' || !Number.isInteger(packet.id)) {
    return { valid: false, error: 'Packet id must be an integer' };
  }
  if (!packet.cmd || typeof packet.cmd !== 'string') {
    return { valid: false, error: 'Packet cmd must be a string' };
  }

  const { cmd } = packet;

  switch (cmd) {
    case COMMANDS.PING:
    case COMMANDS.STATUS:
    case COMMANDS.STOP:
    case COMMANDS.ESTOP:
      return { valid: true };

    case COMMANDS.START:
      if (packet.frequency_hz !== undefined) {
        if (typeof packet.frequency_hz !== 'number' || 
            packet.frequency_hz < PROTOCOL_LIMITS.FREQUENCY_MIN_HZ || 
            packet.frequency_hz > PROTOCOL_LIMITS.FREQUENCY_MAX_HZ) {
          return { valid: false, error: `START frequency_hz must be ${PROTOCOL_LIMITS.FREQUENCY_MIN_HZ}~${PROTOCOL_LIMITS.FREQUENCY_MAX_HZ}` };
        }
      }
      if (packet.amplitude !== undefined) {
        if (typeof packet.amplitude !== 'number' || 
            packet.amplitude < PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE || 
            packet.amplitude > PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE) {
          return { valid: false, error: `START amplitude must be ${PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE}~${PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE}` };
        }
      }
      return { valid: true };

    case COMMANDS.SET_VIBRATION:
      if (packet.frequency_hz === undefined || typeof packet.frequency_hz !== 'number' ||
          packet.frequency_hz < PROTOCOL_LIMITS.FREQUENCY_MIN_HZ || 
          packet.frequency_hz > PROTOCOL_LIMITS.FREQUENCY_MAX_HZ) {
        return { valid: false, error: `SET_VIBRATION frequency_hz must be ${PROTOCOL_LIMITS.FREQUENCY_MIN_HZ}~${PROTOCOL_LIMITS.FREQUENCY_MAX_HZ}` };
      }
      if (packet.amplitude === undefined || typeof packet.amplitude !== 'number' ||
          packet.amplitude < PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE || 
          packet.amplitude > PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE) {
        return { valid: false, error: `SET_VIBRATION amplitude must be ${PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE}~${PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE}` };
      }
      return { valid: true };

    case COMMANDS.SET_FREQUENCY:
      if (typeof packet.frequency_hz !== 'number' || 
          packet.frequency_hz < PROTOCOL_LIMITS.FREQUENCY_MIN_HZ || 
          packet.frequency_hz > PROTOCOL_LIMITS.FREQUENCY_MAX_HZ) {
        return { valid: false, error: `SET_FREQUENCY frequency_hz must be ${PROTOCOL_LIMITS.FREQUENCY_MIN_HZ}~${PROTOCOL_LIMITS.FREQUENCY_MAX_HZ}` };
      }
      return { valid: true };

    case COMMANDS.SET_AMPLITUDE:
      if (typeof packet.amplitude !== 'number' || 
          packet.amplitude < PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE || 
          packet.amplitude > PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE) {
        return { valid: false, error: `SET_AMPLITUDE amplitude must be ${PROTOCOL_LIMITS.AMPLITUDE_MIN_SCALE}~${PROTOCOL_LIMITS.AMPLITUDE_MAX_SCALE}` };
      }
      return { valid: true };

    case COMMANDS.SET_VOLUME:
      if (typeof packet.volume !== 'number' || 
          packet.volume < PROTOCOL_LIMITS.VOLUME_MIN || 
          packet.volume > PROTOCOL_LIMITS.VOLUME_MAX) {
        return { valid: false, error: `SET_VOLUME volume must be ${PROTOCOL_LIMITS.VOLUME_MIN}~${PROTOCOL_LIMITS.VOLUME_MAX}` };
      }
      return { valid: true };

    case COMMANDS.SET_PRESET:
      if (typeof packet.preset !== 'string' || !PROTOCOL_LIMITS.VALID_PRESETS.includes(packet.preset.toLowerCase())) {
        return { valid: false, error: `SET_PRESET preset must be one of: ${PROTOCOL_LIMITS.VALID_PRESETS.join(', ')}` };
      }
      return { valid: true };

    default:
      return { valid: false, error: `Unknown command: ${cmd}` };
  }
}

/**
 * Validates incoming telemetry packet
 */
export function validateTelemetryPacket(data) {
  if (!data || typeof data !== 'object') return false;
  if (data.type !== 'telemetry') return false;
  if (typeof data.uptime_ms !== 'number') return false;
  if (typeof data.state !== 'string') return false;
  if (typeof data.safety_lock !== 'boolean') return false;
  if (!data.accel_g || typeof data.accel_g !== 'object') return false;
  if (typeof data.accel_g.x !== 'number' || typeof data.accel_g.y !== 'number' || typeof data.accel_g.z !== 'number') return false;
  return true;
}

if (typeof window !== 'undefined') {
  window.MAJN_PROTOCOL = {
    PROTOCOL_VERSION,
    MAJN_BLE_UUIDS,
    PROTOCOL_LIMITS,
    COMMANDS,
    ACK_STATUS,
    validateCommandPacket,
    validateTelemetryPacket
  };
}
