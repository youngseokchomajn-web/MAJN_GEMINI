#include "amplifier_manager.h"
#include "tas5805m.h"

namespace {
TAS5805M gAmp;
bool gAmpReady = false;
bool gAmpStandby = true;
uint8_t gCurrentVolume = 72;
}

namespace MajnAmplifier {

bool initAmplifier() {
    pinMode(PIN_AMP_PDN, OUTPUT);
    digitalWrite(PIN_AMP_PDN, LOW);
    gAmpReady = false;
    gAmpStandby = true;

#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("[Amplifier] BLE-only test mode: TAS5805M held in shutdown (PDN LOW).");
    return true;
#else
    digitalWrite(PIN_AMP_PDN, HIGH);
    delay(5);

    if (!gAmp.begin(PIN_I2C_SDA, PIN_I2C_SCL)) {
        Serial.println("[WARN] TAS5805M I2C initialization not responding.");
        digitalWrite(PIN_AMP_PDN, LOW);
        gAmpReady = false;
        return false;
    }

    gAmpReady = true;
    enterPlayState();
    Serial.println("[Amplifier] TAS5805M Initialized and in Play State.");
    return true;
#endif
}

void enterPlayState() {
#if !defined(MAJN_BLE_ONLY_TEST)
    if (gAmpReady && gAmpStandby) {
        gAmp.enterPlayState();
        gAmpStandby = false;
    }
#endif
}

void enterStandbyState() {
#if !defined(MAJN_BLE_ONLY_TEST)
    if (gAmpReady && !gAmpStandby) {
        gAmp.enterStandbyState();
        gAmpStandby = true;
    }
#endif
}

void shutdownAmplifier() {
    digitalWrite(PIN_AMP_PDN, LOW);
    gAmpStandby = true;
    Serial.println("[Amplifier] TAS5805M PDN asserted LOW (Hardware Mute/Shutdown).");
}

void setVolume(uint8_t volumePercent) {
    gCurrentVolume = constrain(volumePercent, (uint8_t)0, (uint8_t)100);
#if !defined(MAJN_BLE_ONLY_TEST)
    if (gAmpReady) {
        // Map 0~100% to volume register if needed
    }
#endif
}

bool isAmplifierReady() {
    return gAmpReady;
}

}
