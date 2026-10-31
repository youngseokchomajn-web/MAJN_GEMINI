#include "wifi_manager.h"

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Update.h>
#include <esp_wifi.h>
#include <esp_heap_caps.h>
#include "system_controller.h"
#include "mobile_web_ui.h"

namespace MajnWiFi {

static const byte DNS_PORT = 53;
static DNSServer dnsServer;
static WebServer server(80);
static AccelData sLatestAccel = {0, 0, 0, 0.0f, 0.0f, 1.0f};
static bool sOtaInProgress = false;
static String sAuthToken = "majn-device-token-2026";

bool isOtaInProgress() {
    return sOtaInProgress;
}

static bool isRequestAuthorized() {
    if (sAuthToken.isEmpty()) return true;
    if (server.hasHeader("X-Auth-Token") && server.header("X-Auth-Token") == sAuthToken) {
        return true;
    }
    if (server.hasArg("token") && server.arg("token") == sAuthToken) {
        return true;
    }
    if (server.hasHeader("Cookie")) {
        String cookie = server.header("Cookie");
        if (cookie.indexOf(String("majn_token=") + sAuthToken) != -1) {
            return true;
        }
    }
    return false;
}

static void handleRoot() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
    server.sendHeader("Set-Cookie", String("majn_token=") + sAuthToken + "; Path=/; HttpOnly; SameSite=Strict");
    server.send(200, "text/html", MOBILE_INDEX_HTML);
}

static void handleCaptiveRedirect() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
}

static void handleStatus() {
    MajnSystemCtrl::noteClientActivity();
    String jsonOut;
    MajnSystemCtrl::getTelemetryJson(jsonOut, sLatestAccel);

    uint32_t freeHeap = ESP.getFreeHeap();
    uint32_t minFreeHeap = esp_get_minimum_free_heap_size();
    uint32_t largestBlock = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);

    if (jsonOut.endsWith("}")) {
        jsonOut.remove(jsonOut.length() - 1);
        jsonOut += String(",\"free_heap\":") + freeHeap +
                   String(",\"min_free_heap\":") + minFreeHeap +
                   String(",\"largest_free_block\":") + largestBlock + "}";
    }

    server.sendHeader("Access-Control-Allow-Origin", "http://192.168.4.1");
    server.send(200, "application/json", jsonOut);
}

static void handlePing() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Access-Control-Allow-Origin", "http://192.168.4.1");
    server.send(200, "application/json", "{\"status\":\"ok\"}");
}

static void handleCommand() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Access-Control-Allow-Origin", "http://192.168.4.1");

    if (!isRequestAuthorized()) {
        server.send(401, "application/json", "{\"error\":\"Unauthorized: Missing or invalid authentication token\"}");
        return;
    }

    if (sOtaInProgress) {
        server.send(423, "application/json", "{\"error\":\"Locked: Firmware update in progress. Vibration inhibited.\"}");
        return;
    }

    if (!server.hasArg("plain")) {
        server.send(400, "application/json", "{\"error\":\"Missing body\"}");
        return;
    }

    String body = server.arg("plain");
    String responseJson;
    bool success = MajnSystemCtrl::handleJsonCommand(body.c_str(), responseJson);

    server.send(success ? 200 : 400, "application/json", responseJson);
}

bool initWiFiServer(const char* ssid, const char* password, const char* authToken) {
    if (authToken && strlen(authToken) > 0) {
        sAuthToken = authToken;
    }

    // 1. Reset Wi-Fi peripheral to clean state
    WiFi.disconnect(true);
    delay(50);
    WiFi.mode(WIFI_AP);

    // 2. Configure IP (192.168.4.1)
    IPAddress local_ip(192, 168, 4, 1);
    IPAddress gateway(192, 168, 4, 1);
    IPAddress subnet(255, 255, 255, 0);
    WiFi.softAPConfig(local_ip, gateway, subnet);

    // 3. Start SoftAP on Channel 1 with WPA2-PSK security (never default to Open AP)
    bool apStarted = false;
    if (password && strlen(password) >= 8) {
        apStarted = WiFi.softAP(ssid, password, 1, 0, 4);
    } else {
        apStarted = WiFi.softAP(ssid, "majn-secure-2026", 1, 0, 4);
    }

    if (!apStarted) {
        Serial.println("[WiFi] Failed to start SoftAP.");
        return false;
    }

    // 4. Disable Wi-Fi Modem Sleep (CRITICAL for mobile beacon detection)
    WiFi.setSleep(false);
    esp_wifi_set_ps(WIFI_PS_NONE);

    // 5. Force 20MHz bandwidth (HT20) & standard b/g/n protocols
    esp_wifi_set_bandwidth(WIFI_IF_AP, WIFI_BW_HT20);
    esp_wifi_set_protocol(WIFI_IF_AP, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_11G | WIFI_PROTOCOL_11N);

    // 6. Set Regulatory Country Domain: Korea regulatory domain configuration (KR: Channels 1-13)
    wifi_country_t country = {
        .cc = "KR",
        .schan = 1,
        .nchan = 13,
        .max_tx_power = 60, // ~15 dBm
        .policy = WIFI_COUNTRY_POLICY_MANUAL
    };
    esp_err_t cErr = esp_wifi_set_country(&country);
    if (cErr != ESP_OK) {
        Serial.printf("[WiFi] WARN: Failed to apply regulatory country domain, err=0x%X\n", cErr);
    } else {
        Serial.println("[WiFi] Regulatory country domain applied: KR (Channels 1-13, 15dBm max).");
    }

    // 7. Set Safe Transmission RF Power (15 dBm) AFTER SoftAP is started
    WiFi.setTxPower(WIFI_POWER_15dBm);

    Serial.println("[WiFi] SoftAP Started Successfully!");
    Serial.printf("[WiFi] SSID: %s (Channel 1, HT20, 15.0dBm SafePower, WPA2-PSK)\n", ssid);
    Serial.printf("[WiFi] IP Address: %s\n", WiFi.softAPIP().toString().c_str());

    // 5. Start DNS Server for Captive Portal (Redirects any domain query to 192.168.4.1)
    dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
    dnsServer.start(DNS_PORT, "*", local_ip);
    Serial.println("[WiFi] Captive Portal DNS Server started on port 53.");

    // 6. Start mDNS (http://majn.local)
    if (MDNS.begin("majn")) {
        Serial.println("[WiFi] mDNS Responder active: http://majn.local");
    }

    // 7. Register Standard Web Routes
    server.on("/", HTTP_GET, handleRoot);
    server.on("/api/status", HTTP_GET, handleStatus);
    server.on("/api/ping", HTTP_GET, handlePing);
    server.on("/api/command", HTTP_POST, handleCommand);

    // 8. Register Captive Portal Detection Routes (Apple iOS & Android Auto-Login)
    server.on("/hotspot-detect.html", HTTP_GET, handleRoot);
    server.on("/generate_204", HTTP_GET, handleCaptiveRedirect);
    server.on("/gen_204", HTTP_GET, handleCaptiveRedirect);
    server.on("/connecttest.txt", HTTP_GET, handleCaptiveRedirect);
    server.on("/canonical.html", HTTP_GET, handleRoot);
    server.on("/ncsi.txt", HTTP_GET, handleCaptiveRedirect);

    // 9. Web-based Wireless Firmware Update Route (/update) with Token Security
    server.on("/update", HTTP_GET, []() {
        server.sendHeader("Connection", "close");
        server.send(200, "text/html",
            "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>MAJN Firmware Update</title><style>body{background:#0f172a;color:#fff;font-family:sans-serif;padding:24px;text-align:center;}"
            ".card{background:#1e293b;border-radius:12px;padding:24px;max-width:400px;margin:40px auto;border:1px solid #334155;}"
            "input{margin:12px 0;padding:10px;width:100%;background:#0f172a;color:#fff;border:1px solid #475569;border-radius:6px;box-sizing:border-box;}"
            "button{background:#38bdf8;color:#0f172a;font-weight:bold;padding:12px 24px;border:none;border-radius:8px;font-size:16px;cursor:pointer;width:100%;margin-top:12px;}"
            "</style></head><body><div class='card'><h2>🚀 MAJN 보안 무선 OTA</h2>"
            "<p style='color:#94a3b8;font-size:14px;margin-top:8px;'>ESP32 실행 바이너리(.bin)와 인증 토큰을 입력하세요.</p>"
            "<form method='POST' action='/update' enctype='multipart/form-data'>"
            "<input type='password' name='token' placeholder='보안 인증 토큰' required>"
            "<input type='file' name='update' accept='.bin' required>"
            "<button type='submit'>보안 업데이트 시작</button></form></div></body></html>"
        );
    });

    server.on("/update", HTTP_POST, []() {
        server.sendHeader("Connection", "close");
        sOtaInProgress = false;
        if (!isRequestAuthorized()) {
            server.send(401, "text/plain", "UNAUTHORIZED: Invalid or missing authentication token.");
            return;
        }

        if (Update.hasError()) {
            server.send(500, "text/plain", "UPDATE FAILED: Write error or invalid ESP32 image format.");
            Serial.println("[Web-OTA] Update failed. Reboot suppressed to preserve error diagnostics.");
        } else {
            server.send(200, "text/plain", "UPDATE SUCCESS! Rebooting with verified new firmware...");
            Serial.println("[Web-OTA] Update successful. Rebooting in 1 second...");
            delay(1000);
            ESP.restart();
        }
    }, []() {
        HTTPUpload& upload = server.upload();
        if (upload.status == UPLOAD_FILE_START) {
            if (!isRequestAuthorized()) {
                Serial.println("[Web-OTA] REJECTED: Unauthorized OTA attempt without valid token.");
                return;
            }
            Serial.printf("[Web-OTA] Starting authorized update: %s\n", upload.filename.c_str());
            sOtaInProgress = true;
            MajnSystemCtrl::triggerSafeStop();
            Update.clearError();
            if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
                Update.printError(Serial);
            }
        } else if (upload.status == UPLOAD_FILE_WRITE) {
            if (!isRequestAuthorized()) return;
            // First chunk sanity check: ESP32 binary image magic byte must be 0xE9
            if (upload.totalSize == 0 && upload.currentSize > 0) {
                if (upload.buf[0] != 0xE9) {
                    Serial.printf("[Web-OTA] REJECTED: Header magic byte 0x%02X != 0xE9. Not an ESP32 binary!\n", upload.buf[0]);
                    Update.abort();
                    return;
                }
            }
            if (!Update.hasError()) {
                if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
                    Update.printError(Serial);
                }
            }
        } else if (upload.status == UPLOAD_FILE_END) {
            if (Update.end(true)) {
                Serial.printf("[Web-OTA] Successfully updated %u bytes\n", upload.totalSize);
            } else {
                Update.printError(Serial);
            }
        } else if (upload.status == UPLOAD_FILE_ABORTED) {
            sOtaInProgress = false;
            Update.abort();
            Serial.println("[Web-OTA] Update transfer aborted by client.");
        }
    });

    server.begin();
    Serial.println("[WiFi] HTTP Web Server active on port 80.");
    return true;
}

void handleClient() {
    dnsServer.processNextRequest();
    server.handleClient();
    // Heartbeat safety watchdog: auto safe-stop if no request for 5 seconds while RUNNING
    MajnSystemCtrl::checkClientTimeout(5000);
}

void updateTelemetry(const AccelData& accel) {
    sLatestAccel = accel;
}

} // namespace MajnWiFi
