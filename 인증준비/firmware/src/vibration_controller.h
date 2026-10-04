#pragma once

#include <Arduino.h>

namespace MajnVibration {
#define PIN_I2S_BCLK 26
#define PIN_I2S_LRCLK 25
#define PIN_I2S_DOUT 22

void initVibrationController();
void setTarget(float frequencyHz, float amplitudeScale);
float getTargetFrequency();
float getCurrentAmplitude();
float getTargetAmplitude();
void tickControlLoop(float dt);
void renderAudioBlock();
}
