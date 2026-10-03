/**
 * MAJN Web Bluetooth Provider
 * Backward compatibility wrapper around BleDeviceProvider
 */

import { BleDeviceProvider, MAJN_BLE_UUIDS } from './device_provider.js';

export const MAJN_BLE = MAJN_BLE_UUIDS;
export { BleDeviceProvider as MajnBleProvider };

if (typeof window !== 'undefined') {
  window.MAJN_BLE = MAJN_BLE_UUIDS;
  window.MajnBleProvider = BleDeviceProvider;
  if (!window.majnBle) {
    window.majnBle = new BleDeviceProvider();
  }
}
