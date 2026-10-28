#pragma once

#include <Arduino.h>
#include "ble_protocol.h"

#if !defined(MAJN_WIFI_CONTROL)
bool initBleServer();
void bleLoop();
void bleNotifyTelemetry(
    MajnBle::SystemState state,
    bool safetyLock,
    float frequencyHz,
    float amplitudeScale,
    float ax,
    float ay,
    float az
);
bool bleClientConnected();
void bleRegisterHeartbeat();
#else
inline bool initBleServer() { return true; }
inline void bleLoop() {}
inline void bleNotifyTelemetry(MajnBle::SystemState, bool, float, float, float, float, float) {}
inline bool bleClientConnected() { return false; }
inline void bleRegisterHeartbeat() {}
#endif
