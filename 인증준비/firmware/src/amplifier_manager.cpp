#include "amplifier_manager.h"
#include "tas5805m.h"

namespace {
TAS5805M gAmp;
bool gAmpReady = false;
bool gAmpStandby = true;
uint8_t gCurrentVolume = 72;
char gStatusBuf[64] = "Uninitialized";
}

namespace MajnAmplifier {

bool initAmplifier() {
#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("[Amplifier] BLE-only test mode: TAS5805M held in shutdown (PDN LOW).");
    digitalWrite(PIN_AMP_PDN, LOW);
    gAmpReady = false;
    gAmpStandby = true;
    snprintf(gStatusBuf, sizeof(gStatusBuf), "BLE_ONLY_TEST");
    return false;
#else
    pinMode(PIN_AMP_PDN, OUTPUT);

    // Try up to 3 times to initialize TAS5805M with hardware reset
    for (int attempt = 1; attempt <= 3; attempt++) {
        digitalWrite(PIN_AMP_PDN, LOW);
        delay(20);
        digitalWrite(PIN_AMP_PDN, HIGH);
        delay(50); // Power-on settle time (internal charge pump & PLL)

        Serial.printf("[Amplifier] Attempting TAS5805M init (try %d/3)...\n", attempt);
        if (gAmp.begin(PIN_I2C_SDA, PIN_I2C_SCL)) {
            gAmpReady = true;
            gAmpStandby = false;
            uint8_t aState = 0, cFault = 0, gFault = 0;
            gAmp.getDiagnostics(aState, cFault, gFault);
            snprintf(gStatusBuf, sizeof(gStatusBuf), "READY(0x%02X S:0x%02X CF:0x%02X GF:0x%02X)", gAmp.getI2CAddress(), aState, cFault, gFault);
            Serial.printf("[Amplifier] TAS5805M Initialized: %s\n", gStatusBuf);
            return true;
        }
        delay(30);
    }

    gAmpReady = false;
    gAmpStandby = true;
    digitalWrite(PIN_AMP_PDN, LOW); // Hold PDN LOW for safety if all attempts fail
    snprintf(gStatusBuf, sizeof(gStatusBuf), "FAILED(No I2C Ack probed 2C,2D,2E,2F)");
    Serial.println("[Amplifier] ERROR: TAS5805M init failed after 3 attempts! PDN held LOW.");
    return false;
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

bool getDiagnostics(uint8_t &state, uint8_t &chanFault, uint8_t &globalFault1) {
#if !defined(MAJN_BLE_ONLY_TEST)
    if (gAmpReady) {
        return gAmp.getDiagnostics(state, chanFault, globalFault1);
    }
#endif
    return false;
}

const char* getStatusString() {
    return gStatusBuf;
}

}
