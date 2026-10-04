#pragma once

#include <Arduino.h>

namespace MajnOta {

void initOta();
void tickOta();
bool isUpdating();
int getProgress();

}
