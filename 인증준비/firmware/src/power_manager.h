#pragma once

#include <Arduino.h>

namespace MajnPower {
#define PIN_BOOST_EN 4

void initPower();
void enableBoost();
void disableBoost();
bool isBoostEnabled();
}
