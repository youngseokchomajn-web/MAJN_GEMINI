#include "safety_manager.h"
#include "vibration_controller.h"

extern volatile bool systemActive;
extern volatile unsigned long activeStateStartTime;
extern void hardwareEmergencyShutdown();

namespace {
volatile bool gSafetyLock = false;
volatile bool gIsrShockPending = false;
volatile bool gVibrationActive = false;
}

namespace MajnSafety {

void initSafety() {
    gSafetyLock = false;
    gIsrShockPending = false;
    gVibrationActive = false;
}

void setVibrationActive(bool active) {
    gVibrationActive = active;
}

bool isVibrationActive() {
    return gVibrationActive;
}

bool isSafetyLockTriggered() {
    return gSafetyLock;
}

void processPendingShock() {
    if (gIsrShockPending) {
        gIsrShockPending = false;
        gVibrationActive = false;
        hardwareEmergencyShutdown();
        MajnVibration::stopImmediately();
        Serial.println("[Safety] Hardware Shock Interrupt (>1.5g) handled on Core 1: Emergency Stop engaged!");
    }
}

void IRAM_ATTR safetyLockISR() {
    // Engage shock lock when vibration is actively running or decaying (STOPPING)
    // NEVER call Serial or non-IRAM functions inside ISR!
    if (systemActive || gVibrationActive) {
        gSafetyLock = true;
        systemActive = false;
        gVibrationActive = false;
        activeStateStartTime = 0;
        gIsrShockPending = true;
    }
}

void requestEmergencyStop() {
    activeStateStartTime = 0;
    gSafetyLock = true;
    systemActive = false;
    gVibrationActive = false;
    hardwareEmergencyShutdown();
    MajnVibration::stopImmediately();
    Serial.println("[Safety] Emergency Stop (ESTOP) engaged!");
}

void requestSafeStop() {
    activeStateStartTime = 0;
    systemActive = false;
    MajnVibration::setTarget(MajnVibration::getTargetFrequency(), 0.0f);
    Serial.println("[Safety] Safe Stop requested.");
}

bool resetSafetyLock() {
    if (gSafetyLock) {
        gSafetyLock = false;
        gIsrShockPending = false;
        Serial.println("[Safety] Safety Lock reset by host command.");
        return true;
    }
    return false;
}

MajnBle::SystemState getSystemState(bool active) {
    if (gSafetyLock) return MajnBle::SystemState::FAULT;
    if (active) return MajnBle::SystemState::RUNNING;
    if (!active && MajnVibration::getCurrentAmplitude() > 0.001f) {
        return MajnBle::SystemState::STOPPING;
    }
    return MajnBle::SystemState::READY;
}

}
