#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <WebServer.h>           // 웹 대시보드 및 무선 웹 업데이트용
#include <Update.h>              // 웹 브라우저 펌웨어 업데이트용
#include <WiFiManager.h>         // 동적 와이파이 간편 설정 매니저 라이브러리
#include "driver/dac_oneshot.h"   // v3.x DAC 드라이버 (초기화 전용)
#include "soc/rtc_io_reg.h"      // DAC 레지스터 직접 접근 (ISR-safe)
#include "esp_attr.h"            // DRAM_ATTR 매크로용
#include <math.h>

// ─── [설정값] 프라펠라 SVS 임상 스펙 ──────────────────────
const int SAMPLE_RATE   = 4000;   // 초당 4000 샘플 (오디오급 해상도)
const int DURATION_SEC  = 10;     // 신경계 적응 방지를 위한 10초 롱 루프
const int TOTAL_SAMPLES = SAMPLE_RATE * DURATION_SEC; // 40,000 샘플
// ───────────────────────────────────────────────────

// ─── [하드웨어 핀 맵 (흰색 LED 내장 버튼)] ──────────────
const int PIN_BUTTON = 4;  // 스위치 2번 다리 -> P4 (내부 풀업, Active Low)
const int PIN_LED    = 5;  // LED +다리 -> 저항 -> P5 (Active High)
// ───────────────────────────────────────────────────

// ─── [진폭 스케일 및 모드 상수] ─────────────────────
const uint16_t SCALE_OFF  = 0;    // 정지: 0%
const uint16_t SCALE_LOW  = 102;  // 약: 40% (102/256)
const uint16_t SCALE_MID  = 179;  // 중: 70% (179/256)
const uint16_t SCALE_HIGH = 256;  // 강: 100%

enum SvsMode {
  MODE_OFF = 0,
  MODE_LOW,
  MODE_MID,
  MODE_HIGH,
  MODE_COUNT
};

// ─── 전역 및 Volatile 변수 ─────────────────────────
uint8_t DRAM_ATTR svsTable[TOTAL_SAMPLES]; // ISR 접근 속도 극대화를 위해 DRAM 강제 지정
volatile int idx = 0;            // ISR ↔ loop() 공유 인덱스
hw_timer_t *timer = NULL;
volatile bool otaInProgress = false;

// 페이드 및 모드 관리 변수
SvsMode currentMode = MODE_OFF;
uint16_t targetScale = SCALE_OFF;
uint16_t currentScale = SCALE_OFF;
volatile uint16_t ampScale = SCALE_OFF;  // ISR 안전 전이용 스케일 변수

// [자극 타이머] 15분 자동 종료 타이머 변수
unsigned long modeStartTime = 0;
const unsigned long SESSION_DURATION_MS = 15 * 60 * 1000; // 15분 (900,000ms)

// v3.x DAC 핸들 (초기화 전용)
dac_oneshot_handle_t dac_chan1;
dac_oneshot_handle_t dac_chan2;

// 웹 서버 객체 선언 (Port 80)
WebServer server(80);

// 전역 와이파이 매니저 객체 선언
WiFiManager wm;

// 함수 선언
void onTimer();
void setupWiFi();
void setupOTA();
void setupWebServer();
void triggerWifiReset();

// ─── SVS 파형 합성 헬퍼 (2-pass 정규화용) ─────────
static float computeSVS(float t) {
  float sig = 0.0f;
  sig += 1.00f * sinf(2.0f * PI * 30.0f * t);
  sig += 0.35f * sinf(2.0f * PI * 14.2f * t + 0.5f);
  sig += 0.25f * sinf(2.0f * PI * 22.7f * t + 1.2f);
  sig += 0.40f * sinf(2.0f * PI *  7.4f * t + 2.8f);
  sig += 0.20f * sinf(2.0f * PI * 33.1f * t + 4.1f);
  return sig;
}

// ─── ISR: 정확히 250us(4kHz) 마다 실행 ────────────
// ⚠️ DAC 레지스터 직접 쓰기 매크로의 버그를 완벽히 수정했습니다!
void IRAM_ATTR onTimer() {
  if (otaInProgress) return;

  int localIdx = idx;
  int raw = (int)svsTable[localIdx] - 127;
  int scaled = (raw * (int)ampScale) >> 8;
  uint8_t val = (uint8_t)(127 + scaled);

  // ⭐ 버그 수정: 매크로의 마지막 인자를 레지스터명이 아닌 비트 시프트 상수(PDAC1_DAC_S / PDAC2_DAC_S)로 복구하여 WDT 무한 재부팅 루프를 해결합니다!
  SET_PERI_REG_BITS(RTC_IO_PAD_DAC1_REG, RTC_IO_PDAC1_DAC_V, val, RTC_IO_PDAC1_DAC_S);
  SET_PERI_REG_BITS(RTC_IO_PAD_DAC2_REG, RTC_IO_PDAC2_DAC_V, val, RTC_IO_PDAC2_DAC_S);

  localIdx++;
  if (localIdx >= TOTAL_SAMPLES) localIdx = 0;
  idx = localIdx;
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n--- MAJN Controller Starting ---");

  // 1. 하드웨어 핀 설정 (스위치 및 LED)
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  
  // ESP32 하드웨어 PWM 설정 (주파수 5000Hz, 8비트 해상도)
  ledcAttachChannel(PIN_LED, 5000, 8, 0); 
  
  // [하드웨어 진단] 부팅 시 LED가 물리적으로 정상 작동하는지 3회 깜빡여 확인합니다.
  for (int i = 0; i < 3; i++) {
    ledcWrite(PIN_LED, 255);
    delay(200);
    ledcWrite(PIN_LED, 0);
    delay(200);
  }

  // 2. ESP32 v3.x DAC 채널 초기화 (GPIO 25, 26)
  dac_oneshot_config_t chan1_cfg = { .chan_id = DAC_CHAN_0 };
  dac_oneshot_new_channel(&chan1_cfg, &dac_chan1);

  dac_oneshot_config_t chan2_cfg = { .chan_id = DAC_CHAN_1 };
  dac_oneshot_new_channel(&chan2_cfg, &dac_chan2);

  // 3. DAC 초기화 부팅 팝 노이즈 방지 (Soft-Start)
  for (int v = 0; v <= 127; v++) {
    SET_PERI_REG_BITS(RTC_IO_PAD_DAC1_REG, RTC_IO_PDAC1_DAC_V, v, RTC_IO_PDAC1_DAC_S);
    SET_PERI_REG_BITS(RTC_IO_PAD_DAC2_REG, RTC_IO_PDAC2_DAC_V, v, RTC_IO_PDAC2_DAC_S);
    delay(1);
  }

  // 4. 10초 분량의 SVS 파형 합성
  float maxAbs = 0.0f;
  for (int i = 0; i < TOTAL_SAMPLES; i++) {
    float t = (float)i / (float)SAMPLE_RATE;
    float sig = computeSVS(t);
    float absVal = fabsf(sig);
    if (absVal > maxAbs) maxAbs = absVal;
  }

  float scale = (maxAbs > 0.0f) ? (127.0f / maxAbs) : 1.0f;
  for (int i = 0; i < TOTAL_SAMPLES; i++) {
    float t = (float)i / (float)SAMPLE_RATE;
    float sig = computeSVS(t);
    int val = (int)(127.5f + sig * scale);
    svsTable[i] = (uint8_t)constrain(val, 0, 255);
  }

  // 5. 비차단(Non-blocking) 방식의 초고속 부팅 와이파이 초기화
  setupWiFi();
  
  // [속도 성능 튜닝] 아이폰 핫스팟 접속 렉을 예방하기 위해 Wi-Fi Modem Sleep을 완전히 끕니다!
  WiFi.setSleep(false); 
  Serial.println("WiFi Full-Power Active (Modem Sleep Disabled for latency).");

  // 6. 타이머 기동
  timer = timerBegin(1000000);
  timerAttachInterrupt(timer, &onTimer);
  timerAlarm(timer, 250, true, 0);

  Serial.println("System fully ready and running SVS instantly! (Zero-delay Boot)");
}

void loop() {
  ArduinoOTA.handle();

  // 비차단식 와이파이 루프 처리
  wm.process();

  // 와이파이가 연결 완료되면 대시보드 기동
  static bool portalStopped = false;
  if (WiFi.status() == WL_CONNECTED && !portalStopped) {
    portalStopped = true;
    // ⚠️ 버그 수정: 부팅 즉시 자동 접속에 성공한 경우(포털이 켜진 적 없음) stopConfigPortal()을 호출하면
    // NULL 포인터 참조로 커널 패닉(LoadProhibited)이 발생하는 문제를 방지하기 위해 호출을 생략합니다.
    // wm.stopConfigPortal(); 
    setupWebServer();      
    setupOTA();            
    
    // [mDNS 기동] IP 주소 대신 http://majn.local 주소로 간편하게 브라우저 접속을 지원합니다.
    if (MDNS.begin("majn")) {
      MDNS.addService("http", "tcp", 80);
      Serial.println("mDNS responder started. You can access via http://majn.local");
    }
    
    Serial.println("\n[Network Setup] Wi-Fi Connection Established! Web Dashboard Server Active.");
  }

  // 웹 브라우저 클라이언트 요청 처리 (대시보드가 켜졌을 때만 작동)
  if (portalStopped) {
    server.handleClient();
  }

  // [진단 튜닝] 하트비트 주기를 2초로 줄이고, 물리 버튼의 핀 상태(HIGH/LOW)를 실시간 출력합니다.
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 2000) {
    lastPrint = millis();
    Serial.printf("[SVS] Mode=%d Scale=%d wifi=%s IP=%s PIN_BTN=%d\n",
      currentMode, ampScale,
      WiFi.status() == WL_CONNECTED ? "OK" : "OFFLINE",
      WiFi.localIP().toString().c_str(),
      digitalRead(PIN_BUTTON));
  }

  // 스위치 감지 및 디바운스
  static bool lastRawButtonState = HIGH;
  static bool debouncedButtonState = HIGH;
  static unsigned long lastDebounceTime = 0;
  const unsigned long DEBOUNCE_DELAY = 30;

  bool rawState = digitalRead(PIN_BUTTON);
  if (rawState != lastRawButtonState) {
    lastDebounceTime = millis();
  }
  lastRawButtonState = rawState;

  static unsigned long buttonPressTime = 0;
  static bool longPressTriggered = false;
  static bool resetTriggered = false;

  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    if (rawState != debouncedButtonState) {
      debouncedButtonState = rawState;

      if (debouncedButtonState == LOW) {
        buttonPressTime = millis();
        longPressTriggered = false;
        resetTriggered = false;
      } else {
        if (!longPressTriggered && !resetTriggered) {
          unsigned long duration = millis() - buttonPressTime;
          if (duration >= 50 && duration < 1200) {
            currentMode = (SvsMode)((currentMode + 1) % MODE_COUNT);
            Serial.printf("[Switch] Short Press -> Mode Changed: %d\n", currentMode);

            switch (currentMode) {
              case MODE_OFF:  targetScale = SCALE_OFF;  break;
              case MODE_LOW:  targetScale = SCALE_LOW;  break;
              case MODE_MID:  targetScale = SCALE_MID;  break;
              case MODE_HIGH: targetScale = SCALE_HIGH; break;
            }
            
            if (currentMode != MODE_OFF) {
              modeStartTime = millis();
            }
          }
        }
      }
    }
  }

  // 1.2초 누름: 즉시 정지 처리
  if (debouncedButtonState == LOW && !longPressTriggered && !resetTriggered) {
    unsigned long pressDur = millis() - buttonPressTime;
    if (pressDur >= 1200 && pressDur < 5000) {
      longPressTriggered = true;
      currentMode = MODE_OFF;
      targetScale = SCALE_OFF;
      Serial.println("[Switch] Long Press (1.2s) -> Mode RESET: OFF");

      for (int k = 0; k < 3; k++) {
        ledcWrite(PIN_LED, 255); delay(60);
        ledcWrite(PIN_LED, 0);   delay(60);
      }
    }
  }

  // 5초 강제 누름: 와이파이 초기화 및 임시 설정창 열기
  if (debouncedButtonState == LOW && !resetTriggered) {
    if (millis() - buttonPressTime >= 5000) {
      resetTriggered = true;
      triggerWifiReset();
    }
  }
  // [타이머 체크] 15분 경과 시 자동 정지 처리
  if (currentMode != MODE_OFF) {
    if (millis() - modeStartTime >= SESSION_DURATION_MS) {
      currentMode = MODE_OFF;
      targetScale = SCALE_OFF;
      Serial.println("[Timer] 15-minute session completed! Automatically shutting down SVS.");
      
      // 사용자 인지를 위해 LED 3회 빠르게 반짝임 피드백 출력
      for (int k = 0; k < 3; k++) {
        ledcWrite(PIN_LED, 255); delay(60);
        ledcWrite(PIN_LED, 0);   delay(60);
      }
    }
  }

  // 진폭 페이드 제어
  static unsigned long lastFadeTick = 0;
  if (millis() - lastFadeTick >= 10) {
    lastFadeTick = millis();
    if (currentScale < targetScale) {
      currentScale += 2;
      if (currentScale > targetScale) currentScale = targetScale;
    } else if (currentScale > targetScale) {
      currentScale -= 2;
      if (currentScale < targetScale) currentScale = targetScale;
    }
    ampScale = currentScale;
  }

  // LED 정밀 PWM 조명 연동
  static unsigned long lastLedUpdate = 0;
  if (millis() - lastLedUpdate >= 20) {
    lastLedUpdate = millis();
    
    if (resetTriggered) return; 

    switch (currentMode) {
      case MODE_OFF:
        ledcWrite(PIN_LED, 0);
        break;

      case MODE_LOW: {
        float cycle = (float)(millis() % 2000) / 2000.0f;
        int brightness = (int)(5.0f + 115.0f * (0.5f - 0.5f * cosf(2.0f * PI * cycle)));
        ledcWrite(PIN_LED, brightness);
        break;
      }

      case MODE_MID:
        ledcWrite(PIN_LED, 70);
        break;

      case MODE_HIGH:
        ledcWrite(PIN_LED, 255);
        break;

      default:
        break;
    }
  }

  delay(1);
}

// ─── Web Server Handlers ─────────────────────────

const char HTML_DASHBOARD[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAJN Controller Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0c10;
            --card-bg: #1f2833;
            --accent-color: #66fcf1;
            --text-color: #ffffff;
            --text-muted: #c5c6c7;
            --shadow: 0 10px 30px rgba(0,0,0,0.5);
            --neon-green: #39ff14;
            --neon-yellow: #fff01f;
            --neon-red: #ff3131;
            --neon-blue: #00f0ff;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 480px;
            background: linear-gradient(145deg, #151b23, #0f141a);
            border-radius: 24px;
            padding: 30px 24px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255,255,255,0.05);
            margin-top: 20px;
        }
        h1 {
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 24px;
            background: linear-gradient(90deg, #66fcf1, #45a29e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
        }
        .status-card {
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.03);
        }
        .status-title {
            font-size: 14px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        }
        .status-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-color);
        }
        .led-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .led-off { background-color: #555; }
        .led-low { background-color: var(--neon-green); box-shadow: 0 0 15px var(--neon-green); }
        .led-mid { background-color: var(--neon-yellow); box-shadow: 0 0 15px var(--neon-yellow); }
        .led-high { background-color: var(--neon-red); box-shadow: 0 0 15px var(--neon-red); }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 28px;
        }
        .info-item {
            background: rgba(255,255,255,0.01);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            font-size: 13px;
            border: 1px solid rgba(255,255,255,0.02);
        }
        .info-label { color: var(--text-muted); margin-bottom: 4px; font-size: 11px; }
        .info-val { font-weight: 600; color: #fff; }

        .btn-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }
        .btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-color);
            padding: 16px;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn:active { transform: scale(0.98); }
        .btn-off.active { border-color: var(--neon-red); color: var(--neon-red); }
        .btn-low.active { border-color: var(--neon-green); color: var(--neon-green); }
        .btn-mid.active { border-color: var(--neon-yellow); color: var(--neon-yellow); }
        .btn-high.active { border-color: var(--neon-blue); color: var(--neon-blue); }
        
        .reset-btn {
            background: rgba(255, 49, 49, 0.05);
            border: 1px dashed rgba(255, 49, 49, 0.3);
            color: #ff5555;
            margin-top: 24px;
            padding: 12px;
            font-size: 13px;
            font-weight: 600;
            width: 100%;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .reset-btn:hover {
            background: rgba(255, 49, 49, 0.15);
            border-color: #ff3333;
        }
        .update-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MAJN CONTROLLER</h1>
        <div class="status-card">
            <div class="status-title">실시간 기기 상태</div>
            <div style="display: flex; align-items: center; justify-content: center; margin-top: 5px;">
                <span id="led" class="led-indicator led-off"></span>
                <span id="status">연결 확인 중...</span>
            </div>
            <div id="timer-container" style="margin-top: 15px; font-size: 15px; color: var(--accent-color); font-weight: 600; display: none; background: rgba(102,252,241,0.05); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(102,252,241,0.15); letter-spacing: 0.5px;">
                남은 자극 시간: <span id="timer-val">15:00</span>
            </div>
        </div>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">실시간 출력 스케일</div>
                <div id="scale">-</div>
            </div>
            <div class="info-item">
                <div class="info-label">Wi-Fi 신호 감도</div>
                <div id="wifi">-</div>
            </div>
        </div>
        <div class="btn-grid">
            <button class="btn btn-off" onclick="setMode(0)">자극 정지 (OFF)</button>
            <button class="btn btn-low" onclick="setMode(1)">약한 자극 (LOW)</button>
            <button class="btn btn-mid" onclick="setMode(2)">중간 자극 (MID)</button>
            <button class="btn btn-high" onclick="setMode(3)">강한 자극 (HIGH)</button>
        </div>
        
        <button class="reset-btn" onclick="confirmWifiReset()">Wi-Fi 무선연결 기록 초기화</button>
        <a href="/update" class="update-link">웹 브라우저 펌웨어 업데이트 (Web OTA)</a>
    </div>
    <script>
        const modes = ["정지 (OFF)", "약한 자극 (LOW)", "중간 자극 (MID)", "강한 자극 (HIGH)"];
        const ledClasses = ["led-off", "led-low", "led-mid", "led-high"];
        const btnClasses = [".btn-off", ".btn-low", ".btn-mid", ".btn-high"];

        function updateUI(data) {
            document.getElementById("status").innerText = modes[data.mode];
            document.getElementById("scale").innerText = Math.round(data.scale / 256 * 100) + "%";
            document.getElementById("wifi").innerText = data.wifi + " dBm";
            const led = document.getElementById("led");
            led.className = "led-indicator " + ledClasses[data.mode];
            document.querySelectorAll(".btn").forEach(btn => btn.classList.remove("active"));
            const activeBtn = document.querySelector(btnClasses[data.mode]);
            if (activeBtn) activeBtn.classList.add("active");

            // 타이머 업데이트
            const timerContainer = document.getElementById("timer-container");
            if (data.mode !== 0 && data.remaining > 0) {
                timerContainer.style.display = "block";
                const mins = Math.floor(data.remaining / 60);
                const secs = data.remaining % 60;
                document.getElementById("timer-val").innerText = mins + ":" + (secs < 10 ? "0" : "") + secs;
            } else {
                timerContainer.style.display = "none";
            }
        }

        function loadStatus() {
            fetch('/status').then(res => res.json()).then(data => updateUI(data));
        }

        function setMode(modeNum) {
            fetch('/control?mode=' + modeNum).then(res => res.json()).then(data => updateUI(data));
        }
        
        function confirmWifiReset() {
            if(confirm("정말로 기기의 와이파이 기록을 지우시겠습니까?\n확인을 누르면 기기가 재부팅되며 새로운 와이파이 연결 화면이 열립니다.")) {
                fetch('/wifireset').then(() => {
                    alert("와이파이가 초기화되었습니다. 기기가 재부팅됩니다.");
                    window.location.reload();
                });
            }
        }
        
        setInterval(loadStatus, 1000);
        window.onload = loadStatus;
    </script>
</body>
</html>
)rawhtml";

const char HTML_UPDATE[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAJN Web OTA Update</title>
    <style>
        body { background-color: #0b0c10; color: #ffffff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #151b23; border-radius: 20px; padding: 40px 30px; width: 100%; max-width: 400px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }
        h2 { color: #66fcf1; }
        .btn { background: #66fcf1; color: #0b0c10; border: none; padding: 14px; width: 100%; border-radius: 12px; font-weight: 700; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>무선 업데이트 (Web OTA)</h2>
        <form method='POST' action='/update' enctype='multipart/form-data'>
            <input type='file' name='update' accept='.bin' style="margin-bottom: 20px;">
            <input type='submit' class="btn" value='펌웨어 업데이트 시작'>
        </form>
    </div>
</body>
</html>
)rawhtml";

void handleRoot() {
  server.send_P(200, "text/html", HTML_DASHBOARD);
}

void handleStatus() {
  unsigned long remainingSecs = 0;
  if (currentMode != MODE_OFF) {
    unsigned long elapsed = millis() - modeStartTime;
    if (elapsed < SESSION_DURATION_MS) {
      remainingSecs = (SESSION_DURATION_MS - elapsed) / 1000;
    }
  }

  String json = "{";
  json += "\"mode\":" + String(currentMode) + ",";
  json += "\"scale\":" + String(ampScale) + ",";
  json += "\"wifi\":" + String(WiFi.RSSI()) + ",";
  json += "\"remaining\":" + String(remainingSecs);
  json += "}";
  server.send(200, "application/json", json);
}

void handleControl() {
  if (server.hasArg("mode")) {
    int modeNum = server.arg("mode").toInt();
    if (modeNum >= 0 && modeNum < MODE_COUNT) {
      currentMode = (SvsMode)modeNum;
      switch (currentMode) {
        case MODE_OFF:  targetScale = SCALE_OFF;  break;
        case MODE_LOW:  targetScale = SCALE_LOW;  break;
        case MODE_MID:  targetScale = SCALE_MID;  break;
        case MODE_HIGH: targetScale = SCALE_HIGH; break;
      }
      if (currentMode != MODE_OFF) {
        modeStartTime = millis();
      }
    }
  }
  handleStatus();
}

void handleUpdateGet() {
  server.send_P(200, "text/html", HTML_UPDATE);
}

void handleUpdatePost() {
  server.sendHeader("Connection", "close");
  server.send(200, "text/plain", (Update.hasError()) ? "FAIL" : "SUCCESS - REBOOTING...");
  delay(1000);
  ESP.restart();
}

void handleUpdateUpload() {
  HTTPUpload& upload = server.upload();
  if (upload.status == UPLOAD_FILE_START) {
    otaInProgress = true;
    if (timer != NULL) {
      timerDetachInterrupt(timer);
    }
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
      Update.printError(Serial);
    }
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
      Update.printError(Serial);
    }
  } else if (upload.status == UPLOAD_FILE_END) {
    if (Update.end(true)) {
      Serial.printf("Update Success\nRebooting...\n");
    } else {
      Update.printError(Serial);
      otaInProgress = false;
      if (timer != NULL) {
        timerAttachInterrupt(timer, &onTimer);
        timerAlarm(timer, 250, true, 0);
      }
    }
  }
}

void handleWifiResetRequest() {
  server.send(200, "text/plain", "OK");
  delay(500);
  triggerWifiReset();
}

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/status", handleStatus);
  server.on("/control", handleControl);
  server.on("/update", HTTP_GET, handleUpdateGet);
  server.on("/update", HTTP_POST, handleUpdatePost, handleUpdateUpload);
  server.on("/wifireset", handleWifiResetRequest); 
  server.begin();
}

void triggerWifiReset() {
  Serial.println("\n[Wi-Fi Reset] Erasing saved Wi-Fi credentials and rebooting...");
  for (int i = 0; i < 5; i++) {
    ledcWrite(PIN_LED, 255); delay(80);
    ledcWrite(PIN_LED, 0);   delay(80);
  }
  wm.resetSettings(); 
  delay(500);
  ESP.restart(); 
}

// WiFiManager 전용 다크 네온 프리미엄 스타일시트 주입
const char WM_CUSTOM_CSS[] PROGMEM = R"rawhtml(
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  body {
    background: #0b0c10 !important;
    color: #ffffff !important;
    font-family: 'Outfit', -apple-system, sans-serif !important;
    padding: 20px !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 100vh !important;
  }
  div, p {
    color: #c5c6c7 !important;
    font-size: 14px !important;
  }
  h1 {
    font-size: 26px !important;
    font-weight: 700 !important;
    margin-bottom: 24px !important;
    background: linear-gradient(90deg, #66fcf1, #45a29e) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    letter-spacing: 1.5px !important;
    text-align: center !important;
  }
  h2 {
    font-size: 18px !important;
    color: #66fcf1 !important;
    margin-bottom: 15px !important;
    text-align: center !important;
  }
  a, button, input[type='submit'], input[type='button'] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #66fcf1 !important;
    padding: 15px !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    display: block !important;
    width: 100% !important;
    text-decoration: none !important;
    margin: 12px 0 !important;
    text-align: center !important;
    box-sizing: border-box !important;
  }
  a:active, button:active, input[type='submit']:active {
    transform: scale(0.98) !important;
    background: rgba(102, 252, 241, 0.1) !important;
  }
  input[type='text'], input[type='password'] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    padding: 15px !important;
    border-radius: 14px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    margin-bottom: 14px !important;
    font-size: 15px !important;
    transition: all 0.2s !important;
  }
  input[type='text']:focus, input[type='password']:focus {
    border-color: #66fcf1 !important;
    outline: none !important;
    box-shadow: 0 0 12px rgba(102, 252, 241, 0.2) !important;
    background: rgba(255, 255, 255, 0.04) !important;
  }
  .msg {
    background: rgba(102, 252, 241, 0.05) !important;
    border: 1px solid rgba(102, 252, 241, 0.15) !important;
    color: #66fcf1 !important;
    padding: 12px !important;
    border-radius: 12px !important;
    margin-bottom: 20px !important;
    text-align: center !important;
  }
  /* WiFi 리스트 링크 고급 커스텀 */
  div.q a {
    background: rgba(255, 255, 255, 0.01) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    color: #ffffff !important;
    text-align: left !important;
    padding: 14px 18px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
  }
  div.q a:hover {
    border-color: #66fcf1 !important;
    background: rgba(102, 252, 241, 0.04) !important;
    color: #66fcf1 !important;
  }
</style>
<script>
  document.addEventListener("DOMContentLoaded", function() {
    // 1. 헤더 리브랜딩
    const h1 = document.querySelector("h1");
    if (h1) h1.innerText = "MAJN SETUP";
    
    const h2 = document.querySelector("h2");
    if (h2 && (h2.innerText.includes("MAJN-Device-Setup") || h2.innerText.includes("SSID"))) {
      h2.style.display = "none";
    }

    // 2. 불필요한 번잡 버튼 숨김 및 버튼 명칭 한글 정제
    const elements = document.querySelectorAll("a, button, input[type='submit'], input[type='button']");
    elements.forEach(el => {
      let txt = el.innerText || el.value || "";
      if (txt.includes("Configure WiFi (No Scan)")) {
        el.style.display = "none";
      } else if (txt.includes("Configure WiFi")) {
        if (el.tagName === "INPUT") el.value = "와이파이 검색 및 연결";
        else el.innerText = "와이파이 검색 및 연결";
      } else if (txt.includes("Setup path")) {
        el.style.display = "none";
      } else if (txt.includes("Info")) {
        el.innerText = "기기 정보 확인";
      } else if (txt.includes("Exit")) {
        el.innerText = "설정 종료";
      } else if (txt.includes("Erase")) {
        el.innerText = "저장된 와이파이 기록 삭제";
      } else if (txt.includes("Save")) {
        if (el.tagName === "INPUT") el.value = "저장 및 기기 재부팅";
        else el.innerText = "저장 및 기기 재부팅";
      }
    });

    // 3. 와이파이 목록 내 이모티콘 🔒 자물쇠를 세련된 플랫 배지로 대체
    const qLinks = document.querySelectorAll("div.q a");
    qLinks.forEach(el => {
      if (el.innerHTML.includes("🔒")) {
        el.innerHTML = el.innerHTML.replace("🔒", "<span style='font-size:10px;font-weight:700;color:rgba(102,252,241,0.6);border:1px solid rgba(102,252,241,0.3);padding:2px 6px;border-radius:4px;letter-spacing:0.5px;'>SECURE</span>");
      }
    });
  });
</script>
)rawhtml";

void setupWiFi() {
  wm.setConfigPortalBlocking(false); 
  wm.setConfigPortalTimeout(600); // [타임아웃 10분 연장] 설정 도중 끊김 방지 및 넉넉한 설정 시간 제공
  
  // WiFiManager 설정 페이지를 MAJN 다크 네온 디자인 시스템으로 맞춤 커스텀합니다.
  wm.setCustomHeadElement(WM_CUSTOM_CSS);
  
  Serial.println("Starting Non-blocking Wi-Fi Manager...");
  Serial.printf("[WiFi NVS] Saved SSID: '%s'\n", WiFi.SSID().c_str());
  Serial.printf("[WiFi NVS] Saved Password: '%s'\n", WiFi.psk().c_str());
  
  wm.autoConnect("MAJN-Device-Setup");
}

void setupOTA() {
  ArduinoOTA.setHostname("majn-device");

  ArduinoOTA.onStart([]() {
    otaInProgress = true;
    if (timer != NULL) {
      timerDetachInterrupt(timer);
    }
  });

  ArduinoOTA.onEnd([]() {});
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {});
  ArduinoOTA.onError([](ota_error_t error) {
    otaInProgress = false;
    if (timer != NULL) {
      timerAttachInterrupt(timer, &onTimer);
      timerAlarm(timer, 250, true, 0);
    }
  });

  ArduinoOTA.begin();
}
