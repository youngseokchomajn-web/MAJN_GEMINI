#ifndef MAJN_WIFI_MANAGER_H
#define MAJN_WIFI_MANAGER_H

#include <Arduino.h>
#include "imu_manager.h"

namespace MajnWiFi {

bool initWiFiServer(const char* ssid = "MAJN-Bassinet", const char* password = "majn-secure-2026", const char* authToken = nullptr);
void handleClient();
void updateTelemetry(const AccelData& accel);
bool isOtaInProgress();

} // namespace MajnWiFi

#endif // MAJN_WIFI_MANAGER_H
