#ifndef MAJN_SYSTEM_CONTROLLER_H
#define MAJN_SYSTEM_CONTROLLER_H

#include <Arduino.h>
#include "imu_manager.h"

namespace MajnSystemCtrl {

// Core lifecycle
void init();

// Command & Telemetry
bool handleJsonCommand(const char* jsonStr, String& responseJson);
void getTelemetryJson(String& outJson, const AccelData& accel);

// State inspection
bool isSystemActive();
const char* getCurrentStateName();

// Direct safety triggers
void triggerSafeStop();
void triggerEmergencyStop();
void resetFault();

// Heartbeat & Connection Supervision
void noteClientActivity();
void checkClientTimeout(uint32_t timeoutMs = 5000);

} // namespace MajnSystemCtrl

#endif // MAJN_SYSTEM_CONTROLLER_H
