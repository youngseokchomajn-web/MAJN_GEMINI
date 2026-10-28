#ifndef MAJN_MOBILE_WEB_UI_H
#define MAJN_MOBILE_WEB_UI_H

#include <Arduino.h>

const char MOBILE_INDEX_HTML[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>MAJN Bassinet Controller</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --success: #22c55e;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      -webkit-tap-highlight-color: transparent;
    }
    body {
      background-color: var(--bg);
      color: var(--text);
      padding: 16px;
      padding-bottom: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .container {
      width: 100%;
      max-width: 480px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 4px;
    }
    .logo {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: 1px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      font-size: 11px;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 9999px;
      background: #334155;
      color: var(--text-muted);
    }
    .badge.connected {
      background: #14532d;
      color: #86efac;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card-title {
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
    }
    .status-display {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .state-pill {
      font-size: 22px;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: 8px;
      background: #334155;
      color: #cbd5e1;
    }
    .state-pill.RUNNING {
      background: #166534;
      color: #bbf7d0;
      animation: pulse 2s infinite;
    }
    .state-pill.READY {
      background: #1e3a8a;
      color: #bfdbfe;
    }
    .state-pill.FAULT {
      background: #7f1d1d;
      color: #fecaca;
    }
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.75; }
      100% { opacity: 1; }
    }
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .stat-box {
      background: #0f172a;
      border-radius: 10px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .stat-label {
      font-size: 11px;
      color: var(--text-muted);
    }
    .stat-value {
      font-size: 18px;
      font-weight: 700;
      color: var(--text);
    }
    .control-row {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .control-header {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 600;
    }
    .slider {
      -webkit-appearance: none;
      width: 100%;
      height: 8px;
      border-radius: 4px;
      background: #334155;
      outline: none;
    }
    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
    }
    .btn {
      width: 100%;
      padding: 14px;
      border-radius: 12px;
      font-size: 16px;
      font-weight: 700;
      border: none;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn:active {
      transform: scale(0.98);
    }
    .btn-start {
      background: var(--success);
      color: #052e16;
    }
    .btn-stop {
      background: #475569;
      color: #f8fafc;
    }
    .btn-estop {
      background: var(--danger);
      color: #fff;
    }
    .btn-reset {
      background: var(--warning);
      color: #451a03;
      padding: 10px;
      font-size: 14px;
    }
    .notice {
      font-size: 11px;
      color: var(--text-muted);
      line-height: 1.5;
      background: #0f172a;
      border-left: 3px solid var(--primary);
      padding: 8px 12px;
      border-radius: 0 8px 8px 0;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        MAJN Bassinet
      </div>
      <div id="conn-badge" class="badge">연결 대기중</div>
    </header>

    <!-- 상태 요약 카드 -->
    <div class="card">
      <div class="card-title">기기 동작 상태</div>
      <div class="status-display">
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">시스템 모드</div>
          <div id="sys-state" class="state-pill">WAIT</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">앰프 진단</div>
          <div id="amp-state" style="font-size: 14px; font-weight: 700; color: #38bdf8;">초기화 중</div>
        </div>
      </div>
      <div class="grid-2">
        <div class="stat-box">
          <div class="stat-label">목표 주파수</div>
          <div class="stat-value"><span id="val-freq">45.0</span> Hz</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">출력 진폭 스케일</div>
          <div class="stat-value"><span id="val-amp">0.30</span> / 0.50</div>
        </div>
      </div>
    </div>

    <!-- 제어 슬라이더 카드 -->
    <div class="card">
      <div class="card-title">진동 파라미터 설정</div>
      <div class="control-row">
        <div class="control-header">
          <span>진동 주파수 (30 ~ 65 Hz)</span>
          <span id="slider-freq-val" style="color: var(--primary);">45 Hz</span>
        </div>
        <input type="range" id="slider-freq" class="slider" min="30" max="65" step="1" value="45">
      </div>
      <div class="control-row">
        <div class="control-header">
          <span>진폭 세기 (0.00 ~ 0.50)</span>
          <span id="slider-amp-val" style="color: var(--primary);">0.30</span>
        </div>
        <input type="range" id="slider-amp" class="slider" min="0.05" max="0.50" step="0.05" value="0.30">
      </div>
    </div>

    <!-- 메인 제어 버튼 -->
    <div class="grid-2">
      <button id="btn-start" class="btn btn-start" onclick="sendCommand('START')">
        ▶ 진동 시작
      </button>
      <button id="btn-stop" class="btn btn-stop" onclick="sendCommand('STOP')">
        ■ 안전 정지
      </button>
    </div>

    <!-- 비상 정지 및 복구 -->
    <button id="btn-estop" class="btn btn-estop" onclick="sendCommand('ESTOP')">
      ⚠ 비상정지 (ESTOP)
    </button>
    <button id="btn-reset" class="btn btn-reset" onclick="sendCommand('RESET_FAULT')" style="display:none;">
      안전 잠금 해제 (FAULT RESET)
    </button>

    <!-- 센서 및 안전 공지 카드 -->
    <div class="card">
      <div class="card-title">보드 내장 센서 모니터링</div>
      <div class="grid-2">
        <div class="stat-box">
          <div class="stat-label">보드 가속도 X/Y</div>
          <div class="stat-value" style="font-size: 14px;"><span id="imu-xy">0.00 / 0.00</span> g</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">보드 가속도 Z</div>
          <div class="stat-value" style="font-size: 14px;"><span id="imu-z">1.00</span> g</div>
        </div>
      </div>
      <div class="notice">
        <b>안전 안내:</b><br>
        • RUNNING 표시는 펌웨어의 제어 신호 출력 상태를 의미합니다.<br>
        • 가속도 수치는 PCB 보드 내장 센서(IMU) 값이며, 매트리스 상부의 물리적 계측값이 아닙니다.<br>
        • 브라우저 창을 닫거나 Wi-Fi 연결이 끊어지면 안전을 위해 5초 후 자동 정지됩니다.
      </div>
    </div>
  </div>

  <script>
    let reqId = 100;
    const sliderFreq = document.getElementById('slider-freq');
    const sliderAmp = document.getElementById('slider-amp');
    const labelFreq = document.getElementById('slider-freq-val');
    const labelAmp = document.getElementById('slider-amp-val');
    const badge = document.getElementById('conn-badge');
    const sysState = document.getElementById('sys-state');
    const ampState = document.getElementById('amp-state');
    const valFreq = document.getElementById('val-freq');
    const valAmp = document.getElementById('val-amp');
    const imuXY = document.getElementById('imu-xy');
    const imuZ = document.getElementById('imu-z');
    const btnReset = document.getElementById('btn-reset');

    sliderFreq.addEventListener('input', () => {
      labelFreq.textContent = sliderFreq.value + ' Hz';
    });
    sliderFreq.addEventListener('change', () => {
      sendCommand('SET_FREQUENCY', { frequency_hz: parseFloat(sliderFreq.value) });
    });

    sliderAmp.addEventListener('input', () => {
      labelAmp.textContent = parseFloat(sliderAmp.value).toFixed(2);
    });
    sliderAmp.addEventListener('change', () => {
      sendCommand('SET_AMPLITUDE', { amplitude: parseFloat(sliderAmp.value) });
    });

    async function sendCommand(cmd, extra = {}) {
      const payload = {
        id: ++reqId,
        cmd: cmd,
        frequency_hz: parseFloat(sliderFreq.value),
        amplitude: parseFloat(sliderAmp.value),
        ...extra
      };

      try {
        const res = await fetch('/api/command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        console.log('Ack:', data);
        pollStatus();
      } catch (err) {
        console.error('Command failed:', err);
      }
    }

    async function pollStatus() {
      try {
        const res = await fetch('/api/status');
        if (!res.ok) throw new Error('Status poll HTTP ' + res.status);
        const data = await res.json();
        
        badge.textContent = 'Wi-Fi 연결됨';
        badge.className = 'badge connected';

        sysState.textContent = data.state;
        sysState.className = 'state-pill ' + data.state;

        ampState.textContent = data.amp_status || 'OK';
        valFreq.textContent = Number(data.target_freq || 0).toFixed(1);
        valAmp.textContent = Number(data.current_amp || 0).toFixed(2);

        if (data.board_imu) {
          imuXY.textContent = Number(data.board_imu.x).toFixed(2) + ' / ' + Number(data.board_imu.y).toFixed(2);
          imuZ.textContent = Number(data.board_imu.z).toFixed(2);
        }

        if (data.state === 'FAULT') {
          btnReset.style.display = 'block';
        } else {
          btnReset.style.display = 'none';
        }
      } catch (e) {
        badge.textContent = '연결 끊김';
        badge.className = 'badge';
      }
    }

    // 1초 주기로 상태 폴링 및 연결 유지(하트비트)
    setInterval(pollStatus, 1000);
    pollStatus();
  </script>
</body>
</html>
)rawliteral";

#endif // MAJN_MOBILE_WEB_UI_H
