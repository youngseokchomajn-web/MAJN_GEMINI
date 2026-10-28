#ifndef MAJN_WIFI_MANAGER_H
#define MAJN_WIFI_MANAGER_H

#include <Arduino.h>
#include "imu_manager.h"

namespace MajnWiFi {

bool initWiFiServer(const char* ssid = "MAJN-Bassinet", const char* password = nullptr);
void handleClient();
void updateTelemetry(const AccelData& accel);

} // namespace MajnWiFi

#endif // MAJN_WIFI_MANAGER_H
