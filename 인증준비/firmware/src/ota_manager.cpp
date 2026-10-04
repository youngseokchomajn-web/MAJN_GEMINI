#include "ota_manager.h"
#include <WiFi.h>
#include <ArduinoOTA.h>

namespace {
bool gOtaInitialized = false;
bool gIsUpdating = false;
int gOtaProgress = 0;
}

namespace MajnOta {

void initOta() {
    // Configure SoftAP for standalone emergency OTA if no router
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP("MAJN-Bassinet-OTA", "majn1234");
    Serial.println("[OTA] SoftAP started: SSID=MAJN-Bassinet-OTA, IP=");
    Serial.println(WiFi.softAPIP());

    ArduinoOTA.setHostname("MAJN-Bassinet");
    ArduinoOTA.setPassword("majn1234");

    ArduinoOTA.onStart([]() {
        gIsUpdating = true;
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Serial.println("[OTA] Update started: " + type);
    });

    ArduinoOTA.onEnd([]() {
        gIsUpdating = false;
        Serial.println("\n[OTA] Update completed successfully. Rebooting...");
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        gOtaProgress = (progress / (total / 100));
        Serial.printf("[OTA] Progress: %u%%\r", gOtaProgress);
    });

    ArduinoOTA.onError([](ota_error_t error) {
        gIsUpdating = false;
        Serial.printf("[OTA] Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

    ArduinoOTA.begin();
    gOtaInitialized = true;
    Serial.println("[OTA] ArduinoOTA engine ready.");
}

void tickOta() {
    if (gOtaInitialized) {
        ArduinoOTA.handle();
    }
}

bool isUpdating() {
    return gIsUpdating;
}

int getProgress() {
    return gOtaProgress;
}

}
