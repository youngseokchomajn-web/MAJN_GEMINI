#pragma once

#include <Arduino.h>
#include "lsm6dsox.h"

namespace MajnImu {
#define PIN_SPI_CS_XL   5
#define PIN_SPI_MOSI    23
#define PIN_SPI_MISO    19
#define PIN_SPI_SCLK    18
#define PIN_SAFETY_INT1 34

bool initImu();
bool readAcceleration(AccelData &data);
bool isImuReady();
}
