#pragma once

#include <Arduino.h>
#include "ble_protocol.h"

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
