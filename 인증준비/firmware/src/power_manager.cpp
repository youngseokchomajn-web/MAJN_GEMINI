#include "power_manager.h"

namespace {
bool gBoostActive = false;
}

namespace MajnPower {

void initPower() {
    pinMode(PIN_BOOST_EN, OUTPUT);
    digitalWrite(PIN_BOOST_EN, LOW);
    gBoostActive = false;
    Serial.println("[Power] Power manager initialized. BOOST_EN is LOW.");
}

void enableBoost() {
#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("[Power] BLE-only test mode: BOOST_EN held LOW for safety.");
    gBoostActive = false;
#else
    digitalWrite(PIN_BOOST_EN, HIGH);
    gBoostActive = true;
    delay(10); // Settle time for PVDD 12V rail
    Serial.println("[Power] MP3426 12V Boost Regulator enabled.");
#endif
}

void disableBoost() {
    digitalWrite(PIN_BOOST_EN, LOW);
    gBoostActive = false;
    Serial.println("[Power] MP3426 12V Boost Regulator disabled.");
}

bool isBoostEnabled() {
    return gBoostActive;
}

}
