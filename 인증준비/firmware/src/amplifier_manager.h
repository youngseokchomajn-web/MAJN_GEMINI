#pragma once

#include <Arduino.h>

namespace MajnAmplifier {
#define PIN_AMP_PDN 15
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 27

bool initAmplifier();
void enterPlayState();
void enterStandbyState();
void shutdownAmplifier();
void setVolume(uint8_t volumePercent);
bool isAmplifierReady();
}
