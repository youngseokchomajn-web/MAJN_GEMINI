#include "wifi_manager.h"

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Update.h>
#include "system_controller.h"
#include "mobile_web_ui.h"

namespace MajnWiFi {

static const byte DNS_PORT = 53;
static DNSServer dnsServer;
static WebServer server(80);
static AccelData sLatestAccel = {0, 0, 0, 0.0f, 0.0f, 1.0f};

static void handleRoot() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
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
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", jsonOut);
}

static void handlePing() {
    MajnSystemCtrl::noteClientActivity();
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", "{\"status\":\"ok\"}");
}

static void handleCommand() {
    MajnSystemCtrl::noteClientActivity();
    if (!server.hasArg("plain")) {
        server.send(400, "application/json", "{\"error\":\"Missing body\"}");
        return;
    }

    String body = server.arg("plain");
    String responseJson;
    bool success = MajnSystemCtrl::handleJsonCommand(body.c_str(), responseJson);

    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(success ? 200 : 400, "application/json", responseJson);
}

bool initWiFiServer(const char* ssid, const char* password) {
    // 1. Reset Wi-Fi peripheral to clean state
    WiFi.disconnect(true);
    delay(50);
    WiFi.mode(WIFI_AP);

    // 2. Set Max Transmission RF Power (19.5 dBm) for maximum mobile antenna range
    WiFi.setTxPower(WIFI_POWER_19_5dBm);

    // 3. Configure IP (192.168.4.1)
    IPAddress local_ip(192, 168, 4, 1);
    IPAddress gateway(192, 168, 4, 1);
    IPAddress subnet(255, 255, 255, 0);
    WiFi.softAPConfig(local_ip, gateway, subnet);

    // 4. Start SoftAP on Channel 6 (Global standard compatibility, min interference)
    bool apStarted = false;
    if (password && strlen(password) >= 8) {
        apStarted = WiFi.softAP(ssid, password, 6, 0, 4);
    } else {
        apStarted = WiFi.softAP(ssid, nullptr, 6, 0, 4);
    }

    if (!apStarted) {
        Serial.println("[WiFi] Failed to start SoftAP.");
        return false;
    }

    Serial.println("[WiFi] SoftAP Started Successfully!");
    Serial.printf("[WiFi] SSID: %s (Channel 6, 19.5dBm)\n", ssid);
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

    // 9. Web-based Wireless Firmware Update Route (/update)
    server.on("/update", HTTP_POST, []() {
        server.sendHeader("Connection", "close");
        server.send(200, "text/plain", (Update.hasError()) ? "UPDATE FAILED" : "UPDATE SUCCESS! Rebooting...");
        delay(500);
        ESP.restart();
    }, []() {
        HTTPUpload& upload = server.upload();
        if (upload.status == UPLOAD_FILE_START) {
            Serial.printf("[Web-OTA] Starting update: %s\n", upload.filename.c_str());
            MajnSystemCtrl::triggerSafeStop();
            if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
                Update.printError(Serial);
            }
        } else if (upload.status == UPLOAD_FILE_WRITE) {
            if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
                Update.printError(Serial);
            }
        } else if (upload.status == UPLOAD_FILE_END) {
            if (Update.end(true)) {
                Serial.printf("[Web-OTA] Successfully updated %u bytes\n", upload.totalSize);
            } else {
                Update.printError(Serial);
            }
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
