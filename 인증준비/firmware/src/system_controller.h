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

// Runtime Duration & Safety Watchdog
void setRunningDurationMinutes(uint16_t minutes);
uint16_t getRunningDurationMinutes();
uint32_t getTargetDurationMs();
uint32_t getRemainingSeconds();

// Heartbeat & Connection Supervision
void noteClientActivity();
uint32_t getLastClientActivity();
void checkClientTimeout(uint32_t timeoutMs = 5000);
void tickSystem();

} // namespace MajnSystemCtrl

#endif // MAJN_SYSTEM_CONTROLLER_H
