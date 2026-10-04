#include "safety_manager.h"
#include "vibration_controller.h"

extern volatile bool systemActive;
extern void hardwareEmergencyShutdown();

namespace {
volatile bool gSafetyLock = false;
}

namespace MajnSafety {

void initSafety() {
    gSafetyLock = false;
}

bool isSafetyLockTriggered() {
    return gSafetyLock;
}

void IRAM_ATTR safetyLockISR() {
    gSafetyLock = true;
    systemActive = false;
    hardwareEmergencyShutdown();
}

void requestEmergencyStop() {
    safetyLockISR();
    MajnVibration::setTarget(MajnVibration::getTargetFrequency(), 0.0f);
    Serial.println("[Safety] Emergency Stop (ESTOP) engaged!");
}

void requestSafeStop() {
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
    return MajnBle::SystemState::READY;
}

}
