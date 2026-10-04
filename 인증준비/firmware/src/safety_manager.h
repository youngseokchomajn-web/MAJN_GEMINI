#pragma once

#include <Arduino.h>
#include "ble_protocol.h"

namespace MajnSafety {
void initSafety();
bool isSafetyLockTriggered();
void requestEmergencyStop();
void requestSafeStop();
bool resetSafetyLock();
void safetyLockISR();
MajnBle::SystemState getSystemState(bool systemActive);
}
