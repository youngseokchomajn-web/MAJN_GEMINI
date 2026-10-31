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
      letter-spacing: 0.5px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 9999px;
      background: #334155;
      color: var(--text-muted);
      transition: all 0.3s;
    }
    .badge.connected {
      background: #14532d;
      color: #86efac;
    }
    .badge.disconnected {
      background: #7f1d1d;
      color: #fca5a5;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card-title {
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
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
      display: inline-block;
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
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .stat-label {
      font-size: 11px;
      color: var(--text-muted);
    }
    .stat-value {
      font-size: 20px;
      font-weight: 700;
      color: var(--text);
    }
    .control-row {
      display: flex;
      flex-direction: column;
      gap: 8px;
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
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
    }
    /* 시간 선택 칩 */
    .chip-group {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-top: 4px;
    }
    .chip {
      background: #0f172a;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 10px 0;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 700;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .chip.active {
      background: var(--primary);
      color: #0f172a;
      border-color: var(--primary);
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.4);
    }
    /* 버튼 스타일 */
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
      padding: 12px;
      font-size: 14px;
    }
    .btn-ota {
      background: #334155;
      color: #38bdf8;
      border: 1px solid #475569;
      font-size: 14px;
      padding: 12px;
      text-decoration: none;
      border-radius: 10px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      font-weight: 600;
    }
    .btn-ota:active {
      background: #475569;
    }
    .info-table {
      width: 100%;
      font-size: 12px;
      color: var(--text-muted);
      border-collapse: collapse;
    }
    .info-table td {
      padding: 4px 0;
    }
    .info-table td:last-child {
      text-align: right;
      color: #cbd5e1;
      font-weight: 600;
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

    <!-- 기기 작동 상태 카드 -->
    <div class="card">
      <div class="card-title">기기 작동 상태</div>
      <div class="status-display">
        <div>
          <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">시스템 모드</div>
          <div id="sys-state" class="state-pill">WAIT</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">앰프 진단</div>
          <div id="amp-state" style="font-size: 14px; font-weight: 700; color: #38bdf8;">대기 중</div>
        </div>
      </div>
      <div class="grid-2">
        <div class="stat-box">
          <div class="stat-label">목표 주파수</div>
          <div class="stat-value"><span id="val-freq">45.0</span> <span style="font-size:14px;font-weight:400;">Hz</span></div>
        </div>
        <div class="stat-box">
          <div class="stat-label">진폭 세기</div>
          <div class="stat-value"><span id="val-amp">0.30</span> <span style="font-size:12px;color:var(--text-muted);font-weight:400;">/ 0.50</span></div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-label">잔여 작동 시간</div>
        <div class="stat-value" id="val-timer" style="color: #38bdf8;">15:00</div>
      </div>
    </div>

    <!-- 작동 시간 설정 카드 -->
    <div class="card">
      <div class="card-title">작동 시간 설정 (타이머)</div>
      <div class="chip-group">
        <div class="chip" onclick="setDuration(5)">5분</div>
        <div class="chip" onclick="setDuration(10)">10분</div>
        <div class="chip active" id="chip-15" onclick="setDuration(15)">15분</div>
        <div class="chip" onclick="setDuration(30)">30분</div>
      </div>
    </div>

    <!-- 진동 파라미터 제어 카드 -->
    <div class="card">
      <div class="card-title">진동 파라미터 조절</div>
      <div class="control-row">
        <div class="control-header">
          <span>진동 주파수 (30 ~ 65 Hz)</span>
          <span id="slider-freq-val" style="color: var(--primary);">45 Hz</span>
        </div>
        <input type="range" id="slider-freq" class="slider" min="30" max="65" step="1" value="45">
      </div>
      <div class="control-row">
        <div class="control-header">
          <span>진폭 세기 (0.05 ~ 0.50)</span>
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

    <!-- 비상 정지 및 고장 복구 -->
    <button id="btn-estop" class="btn btn-estop" onclick="sendCommand('ESTOP')">
      ⚠ 비상정지 (ESTOP)
    </button>
    <button id="btn-reset" class="btn btn-reset" onclick="sendCommand('RESET_FAULT')" style="display:none;">
      안전 잠금 해제 (FAULT RESET)
    </button>

    <!-- 시스템 정보 및 무선 OTA 카드 -->
    <div class="card">
      <div class="card-title">시스템 정보 및 업데이트</div>
      <table class="info-table">
        <tr><td>기기 식별</td><td>MAJN Smart Bassinet (#0005)</td></tr>
        <tr><td>펌웨어 버전</td><td id="fw-ver">v1.2-wireless</td></tr>
        <tr><td>여유 힙 메모리</td><td id="free-heap">-</td></tr>
      </table>
      <a id="ota-link" href="/update" class="btn-ota">
        🚀 보안 무선 펌웨어 업데이트 (/update)
      </a>
      <div class="notice">
        • 브라우저 접속이 끊기거나 5초 이상 응답이 없으면 안전을 위해 자동 정지됩니다.<br>
        • 설정된 타이머 시간이 만료되면 출력이 자동으로 안전 정지(Soft Stop)됩니다.
      </div>
    </div>
  </div>

  <script>
    let reqId = 100;
    let selectedDurationMin = 15;
    let authToken = '';
    const sliderFreq = document.getElementById('slider-freq');
    const sliderAmp = document.getElementById('slider-amp');
    const labelFreq = document.getElementById('slider-freq-val');
    const labelAmp = document.getElementById('slider-amp-val');
    const badge = document.getElementById('conn-badge');
    const sysState = document.getElementById('sys-state');
    const ampState = document.getElementById('amp-state');
    const valFreq = document.getElementById('val-freq');
    const valAmp = document.getElementById('val-amp');
    const valTimer = document.getElementById('val-timer');
    const btnReset = document.getElementById('btn-reset');
    const fwVer = document.getElementById('fw-ver');
    const freeHeap = document.getElementById('free-heap');
    const otaLink = document.getElementById('ota-link');

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

    function setDuration(minutes) {
      selectedDurationMin = minutes;
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      const activeChip = Array.from(document.querySelectorAll('.chip')).find(c => c.textContent === (minutes + '분'));
      if (activeChip) activeChip.classList.add('active');
      sendCommand('SET_DURATION', { duration_min: minutes });
    }

    function formatTime(seconds) {
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    }

    async function sendCommand(cmd, extra = {}) {
      const payload = {
        id: ++reqId,
        cmd: cmd,
        frequency_hz: parseFloat(sliderFreq.value),
        amplitude: parseFloat(sliderAmp.value),
        duration_min: selectedDurationMin,
        ...extra
      };

      const headers = { 'Content-Type': 'application/json' };
      if (authToken) {
        headers['X-Auth-Token'] = authToken;
      }

      try {
        const cmdUrl = '/api/command' + (authToken ? ('?token=' + encodeURIComponent(authToken)) : '');
        const res = await fetch(cmdUrl, {
          method: 'POST',
          headers: headers,
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

        if (data.auth_token) {
          authToken = data.auth_token;
          if (otaLink) otaLink.href = '/update?token=' + encodeURIComponent(authToken);
        }

        sysState.textContent = data.state;
        sysState.className = 'state-pill ' + data.state;

        ampState.textContent = data.amp_status || 'OK';
        valFreq.textContent = Number(data.target_freq || 0).toFixed(1);
        valAmp.textContent = Number(data.current_amp || 0).toFixed(2);

        if (data.remaining_sec !== undefined) {
          valTimer.textContent = formatTime(data.remaining_sec);
        }

        if (data.fw_version) {
          fwVer.textContent = data.fw_version + ' (' + (data.build_date || '') + ')';
        }

        if (data.free_heap) {
          freeHeap.textContent = Math.round(data.free_heap / 1024) + ' KB';
        }

        if (data.state === 'FAULT') {
          btnReset.style.display = 'block';
        } else {
          btnReset.style.display = 'none';
        }
      } catch (e) {
        badge.textContent = '연결 끊김';
        badge.className = 'badge disconnected';
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
