#include "safety_manager.h"
#include "vibration_controller.h"

extern volatile bool systemActive;
extern volatile unsigned long activeStateStartTime;
extern void hardwareEmergencyShutdown();

namespace {
volatile bool gSafetyLock = false;
volatile bool gIsrShockPending = false;
}

namespace MajnSafety {

void initSafety() {
    gSafetyLock = false;
    gIsrShockPending = false;
}

bool isSafetyLockTriggered() {
    if (gIsrShockPending) {
        gIsrShockPending = false;
        hardwareEmergencyShutdown();
        MajnVibration::setTarget(MajnVibration::getTargetFrequency(), 0.0f);
        Serial.println("[Safety] Hardware Shock Interrupt (>1.5g) triggered Emergency Stop!");
    }
    return gSafetyLock;
}

void IRAM_ATTR safetyLockISR() {
    // Only engage shock lock when vibration is actively running, and NEVER call Serial/non-IRAM functions inside ISR!
    if (systemActive) {
        gSafetyLock = true;
        systemActive = false;
        activeStateStartTime = 0;
        gIsrShockPending = true;
    }
}

void requestEmergencyStop() {
    activeStateStartTime = 0;
    gSafetyLock = true;
    systemActive = false;
    hardwareEmergencyShutdown();
    MajnVibration::setTarget(MajnVibration::getTargetFrequency(), 0.0f);
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
