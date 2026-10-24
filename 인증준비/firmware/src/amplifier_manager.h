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
bool setVolume(uint8_t volumePercent);
bool isAmplifierReady();
bool getDiagnostics(uint8_t &state, uint8_t &chanFault, uint8_t &globalFault1);
const char* getStatusString();
}
