/**
 * MAJN Smart Bassinet - GUI Application Controller
 * Fully decoupled architecture using the common DeviceProvider interface.
 */

import { SimulationDeviceProvider } from './simulation_provider.js';
import { BleDeviceProvider } from './ble_provider.js';
import { DiagnosticsMonitor } from './diagnostics.js';
import { COMMANDS, PROTOCOL_LIMITS } from './protocol.js';
import { DeviceState } from './state_machine.js';

// Device Providers & Diagnostics
let simProvider = null;
let bleProvider = null;
let activeProvider = null;
const diagnostics = new DiagnosticsMonitor();

// UI & Simulation State
let autoSoothing = true;
let currentBabyState = 'sleep';
let imuChart = null;
let chartDataX = [];
let chartDataY = [];
let chartDataZ = [];
const MAX_CHART_POINTS = 30;

// Web Audio Synthesizer for Audio Preview
let audioCtx = null;
let noiseNode = null;
let audioFilterNode = null;
let audioGainNode = null;

document.addEventListener('DOMContentLoaded', async () => {
  initProviders();
  initIMUChart();
  initEventListeners();
  
  // Default to simulation provider on startup
  await selectProvider('simulation');
  logMessage('system', '[SYSTEM] MAJN Smart Bassinet Controller Ready.');
});

function initProviders() {
  const SimClass = window.SimulationDeviceProvider || SimulationDeviceProvider;
  const BleClass = window.BleDeviceProvider || BleDeviceProvider;

  simProvider = new SimClass();
  bleProvider = new BleClass();
}

/**
 * Switch active device provider (Simulation vs Real BLE)
 */
async function selectProvider(mode) {
  if (activeProvider) {
    detachProviderEvents(activeProvider);
    try {
      await activeProvider.disconnect();
    } catch (err) {
      console.warn('Disconnect error while switching provider:', err);
    }
  }

  const btnSim = document.getElementById('btn-mode-sim');
  const btnBle = document.getElementById('btn-mode-ble');

  if (mode === 'simulation') {
    activeProvider = simProvider;
    btnSim?.classList.add('active');
    btnBle?.classList.remove('active');
    document.getElementById('device-mode-val').textContent = '가상 시뮬레이션';
    document.getElementById('device-mode-val').className = 'highlight';
  } else {
    activeProvider = bleProvider;
    btnBle?.classList.add('active');
    btnSim?.classList.remove('active');
    document.getElementById('device-mode-val').textContent = 'ESP32 BLE 실물';
    document.getElementById('device-mode-val').className = 'highlight';
  }

  attachProviderEvents(activeProvider);

  try {
    await activeProvider.connect();
    updateDeviceInfoUI(activeProvider.deviceInfo);
  } catch (err) {
    logMessage('error', `[${mode.toUpperCase()}] 연결 실패: ${err.message}`);
    if (mode === 'ble') {
      alert(`[블루투스 연결 안내]\n${err.message}`);
      setTimeout(() => selectProvider('simulation'), 500);
    }
  }
}

function attachProviderEvents(provider) {
  provider._unsubState = provider.on('stateChange', onStateChange);
  provider._unsubTelemetry = provider.on('telemetry', onTelemetry);
  provider._unsubConn = provider.on('connectionChange', onConnectionChange);
  provider._unsubLog = provider.on('log', (e) => logMessage(e.type, e.message));
  provider._unsubAck = provider.on('ack', onAck);
}

function detachProviderEvents(provider) {
  if (provider._unsubState) provider._unsubState();
  if (provider._unsubTelemetry) provider._unsubTelemetry();
  if (provider._unsubConn) provider._unsubConn();
  if (provider._unsubLog) provider._unsubLog();
  if (provider._unsubAck) provider._unsubAck();
}

function onConnectionChange({ isConnected, provider }) {
  const statusTitle = document.getElementById('global-status-title');
  const indicator = document.getElementById('global-status-indicator');

  if (!isConnected) {
    if (statusTitle) statusTitle.textContent = `${provider.mode.toUpperCase()} Disconnected`;
    if (indicator) {
      indicator.className = 'status-indicator';
    }
    updateControlsState('DISCONNECTED');
  }
}

function onStateChange({ state, oldState, reason }) {
  const statusTitle = document.getElementById('global-status-title');
  const indicator = document.getElementById('global-status-indicator');
  const badge = document.getElementById('global-mode-badge');
  const badgeText = document.getElementById('mode-badge-text');
  const stateVal = document.getElementById('device-state-val');

  if (stateVal) stateVal.textContent = state;

  // Indicator & Badge Styling
  if (indicator) {
    indicator.className = 'status-indicator';
    if (state === 'READY') indicator.classList.add('online', 'ready');
    else if (state === 'RUNNING') indicator.classList.add('online', 'running');
    else if (state === 'FAULT' || state === 'SAFETY_LOCK') indicator.classList.add('fault');
  }

  if (badge) {
    badge.className = 'mode-badge';
    if (state === 'RUNNING') {
      badge.classList.add('running');
      if (badgeText) badgeText.textContent = '진동 폐루프 구동 중 (RUNNING)';
    } else if (state === 'SAFETY_LOCK' || state === 'FAULT') {
      badge.classList.add('fault');
      if (badgeText) badgeText.textContent = '비상 안전 잠금 (SAFETY LOCK)';
    } else {
      badge.classList.add('ready');
      if (badgeText) badgeText.textContent = '안전 대기 상태 (READY)';
    }
  }

  if (statusTitle) {
    const modePrefix = activeProvider.mode === 'simulation' ? 'Simulation' : 'ESP32 BLE';
    statusTitle.textContent = `${modePrefix} ${state}`;
  }

  updateControlsState(state);
}

function updateControlsState(state) {
  const btnStart = document.getElementById('btn-device-start');
  const btnStop = document.getElementById('btn-device-stop');
  const btnReset = document.getElementById('btn-reset-lock');
  const btnEstop = document.getElementById('btn-emergency-stop');

  if (state === 'RUNNING') {
    if (btnStart) btnStart.disabled = true;
    if (btnStop) btnStop.disabled = false;
    if (btnReset) btnReset.style.display = 'none';
  } else if (state === 'READY') {
    if (btnStart) btnStart.disabled = false;
    if (btnStop) btnStop.disabled = true;
    if (btnReset) btnReset.style.display = 'none';
  } else if (state === 'SAFETY_LOCK' || state === 'FAULT') {
    if (btnStart) btnStart.disabled = true;
    if (btnStop) btnStop.disabled = true;
    if (btnReset) btnReset.style.display = 'inline-flex';
  } else {
    // DISCONNECTED or CONNECTING
    if (btnStart) btnStart.disabled = true;
    if (btnStop) btnStop.disabled = true;
    if (btnReset) btnReset.style.display = 'none';
  }
}

function updateDeviceInfoUI(info) {
  const verElem = document.getElementById('device-version-val');
  if (verElem) {
    verElem.textContent = `${info.firmware} / v${info.protocol}`;
  }
}

function onAck(ack) {
  // ACK telemetry updates if any
}

function onTelemetry(data) {
  // 1. Chart update
  if (data.accel_g && imuChart) {
    chartDataX.shift(); chartDataX.push(data.accel_g.x);
    chartDataY.shift(); chartDataY.push(data.accel_g.y);
    chartDataZ.shift(); chartDataZ.push(data.accel_g.z);
    imuChart.update('none');
  }

  // 2. Power & Thermal (Handling nulls according to HW telemetry matrix)
  const pvddElem = document.getElementById('pvdd-voltage');
  const pvddSidebar = document.getElementById('pvdd-val');
  if (data.pvdd_v == null) {
    if (pvddElem) { pvddElem.textContent = 'N/A (미측정)'; pvddElem.className = 'value unmeasured'; }
    if (pvddSidebar) { pvddSidebar.textContent = 'N/A'; pvddSidebar.className = 'unmeasured'; }
  } else {
    if (pvddElem) { pvddElem.textContent = `${data.pvdd_v.toFixed(2)} V`; pvddElem.className = 'value'; }
    if (pvddSidebar) { pvddSidebar.textContent = `${data.pvdd_v.toFixed(2)}V`; pvddSidebar.className = 'highlight'; }
  }

  const vddElem = document.getElementById('vdd-voltage');
  const vddSidebar = document.getElementById('vdd3v3-val');
  if (data.vdd_3v3_v == null) {
    if (vddElem) { vddElem.textContent = 'N/A (미측정)'; vddElem.className = 'value unmeasured'; }
    if (vddSidebar) { vddSidebar.textContent = 'N/A'; vddSidebar.className = 'unmeasured'; }
  } else {
    if (vddElem) { vddElem.textContent = `${data.vdd_3v3_v.toFixed(2)} V`; vddElem.className = 'value'; }
    if (vddSidebar) { vddSidebar.textContent = `${data.vdd_3v3_v.toFixed(2)}V`; vddSidebar.className = ''; }
  }

  const tempElem = document.getElementById('amp-temp');
  const tempSidebar = document.getElementById('amp-temp-sidebar');
  if (data.amp_temp_c == null) {
    if (tempElem) { tempElem.textContent = 'N/A (미측정)'; tempElem.className = 'value unmeasured'; }
    if (tempSidebar) { tempSidebar.textContent = 'N/A'; }
  } else {
    if (tempElem) { tempElem.textContent = `${data.amp_temp_c.toFixed(1)} °C`; tempElem.className = 'value'; }
    if (tempSidebar) { tempSidebar.textContent = `${data.amp_temp_c.toFixed(1)} °C`; }
  }

  // 3. Cradle wobble animation
  const cradle = document.getElementById('bassinet-cradle');
  if (cradle) {
    if (data.state === 'RUNNING' && data.amplitude_scale > 0) {
      const periodSec = Math.max(0.2, (1.8 / Math.max(0.1, data.amplitude_scale * 10)));
      cradle.style.animation = `rocking ${periodSec.toFixed(2)}s infinite ease-in-out`;
    } else {
      cradle.style.animation = 'none';
    }
  }
}

// Chart.js IMU Initialization
function initIMUChart() {
  const canvas = document.getElementById('imuChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  for (let i = 0; i < MAX_CHART_POINTS; i++) {
    chartDataX.push(0);
    chartDataY.push(0);
    chartDataZ.push(1); // 1g gravity default
  }

  imuChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array.from({ length: MAX_CHART_POINTS }, (_, i) => `${i}s`),
      datasets: [
        {
          label: 'Acc X (g)',
          data: chartDataX,
          borderColor: '#38bdf8',
          borderWidth: 1.5,
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: 'Acc Y (g)',
          data: chartDataY,
          borderColor: '#ec4899',
          borderWidth: 1.5,
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: 'Acc Z (g)',
          data: chartDataZ,
          borderColor: '#10b981',
          borderWidth: 1.5,
          tension: 0.3,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: { display: false },
        y: {
          min: -2.0,
          max: 2.0,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8', font: { size: 10 } }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#f8fafc', font: { size: 11 } }
        }
      }
    }
  });
}

function initEventListeners() {
  // Provider Selection Buttons
  document.getElementById('btn-mode-sim')?.addEventListener('click', () => selectProvider('simulation'));
  document.getElementById('btn-mode-ble')?.addEventListener('click', () => selectProvider('ble'));

  // Main Controls
  document.getElementById('btn-device-start')?.addEventListener('click', async () => {
    if (!activeProvider) return;
    try {
      const f = Number(document.getElementById('frequency-slider')?.value || 45);
      const level = Number(document.getElementById('bounce-slider')?.value || 2);
      const amp = level * 0.1;
      await activeProvider.start({ frequency_hz: f, amplitude: amp });
    } catch (err) {
      logMessage('error', err.message);
    }
  });

  document.getElementById('btn-device-stop')?.addEventListener('click', async () => {
    if (!activeProvider) return;
    try {
      await activeProvider.stop();
    } catch (err) {
      logMessage('error', err.message);
    }
  });

  document.getElementById('btn-device-reboot')?.addEventListener('click', async () => {
    if (!activeProvider) return;
    if (confirm('보드를 원격으로 소프트웨어 재기동(REBOOT)하시겠습니까?')) {
      try {
        logMessage('warn', '[SYSTEM] 원격 소프트웨어 재부팅 명령을 보냅니다...');
        if (typeof activeProvider.reboot === 'function') {
          await activeProvider.reboot();
        }
      } catch (err) {
        logMessage('error', `재부팅 실패: ${err.message}`);
      }
    }
  });

  // Web BLE Wireless OTA Handler
  const otaFileInput = document.getElementById('ota-file-input');
  const btnOtaChoose = document.getElementById('btn-ota-choose');
  const btnOtaStart = document.getElementById('btn-ota-start');
  const otaFileInfo = document.getElementById('ota-file-info');
  const otaProgressBar = document.getElementById('ota-progress-bar');
  const otaProgressPct = document.getElementById('ota-progress-pct');
  const otaStatusLabel = document.getElementById('ota-status-label');

  let selectedOtaFile = null;

  btnOtaChoose?.addEventListener('click', () => {
    otaFileInput?.click();
  });

  otaFileInput?.addEventListener('change', (e) => {
    const file = e.target.files?.[0];
    if (file) {
      selectedOtaFile = file;
      if (otaFileInfo) otaFileInfo.textContent = `선택된 파일: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      if (btnOtaStart) btnOtaStart.disabled = false;
      if (otaStatusLabel) otaStatusLabel.textContent = '업로드 준비 완료';
    }
  });

  btnOtaStart?.addEventListener('click', async () => {
    if (!selectedOtaFile) {
      alert('먼저 펌웨어(.bin) 파일을 선택해주세요.');
      return;
    }
    if (activeProvider?.mode !== 'ble' || !activeProvider?.isConnected) {
      alert('ESP32 BLE 실물 장치가 연결되어 있지 않습니다. 상단에서 [ESP32 BLE 실물]을 먼저 연결해주세요.');
      return;
    }

    if (!confirm(`무선 펌웨어 업데이트를 시작하시겠습니까?\n파일: ${selectedOtaFile.name}\n크기: ${(selectedOtaFile.size / 1024).toFixed(1)} KB\n\n업데이트 중에는 전원을 끄지 마세요.`)) {
      return;
    }

    btnOtaStart.disabled = true;
    btnOtaChoose.disabled = true;
    if (otaStatusLabel) otaStatusLabel.textContent = '블루투스 무선 전송 중...';

    try {
      await activeProvider.performOta(selectedOtaFile, (pct, sent, total) => {
        if (otaProgressBar) otaProgressBar.style.width = `${pct}%`;
        if (otaProgressPct) otaProgressPct.textContent = `${pct}% (${(sent / 1024).toFixed(0)}/${(total / 1024).toFixed(0)} KB)`;
      });
      if (otaStatusLabel) otaStatusLabel.textContent = '완료! ESP32 자동 재부팅 중...';
      if (otaProgressBar) otaProgressBar.style.background = '#10b981';
      alert('🎉 무선 펌웨어 업데이트 대성공!\nESP32가 새 펌웨어로 자동 재부팅됩니다.');
    } catch (err) {
      if (otaStatusLabel) otaStatusLabel.textContent = `오류 발생: ${err.message}`;
      if (otaProgressBar) otaProgressBar.style.background = '#ef4444';
      alert(`무선 업데이트 실패: ${err.message}`);
    } finally {
      btnOtaStart.disabled = false;
      btnOtaChoose.disabled = false;
    }
  });

  document.getElementById('btn-emergency-stop')?.addEventListener('click', async () => {
    if (!activeProvider) return;
    try {
      await activeProvider.emergencyStop();
      stopAudio();
    } catch (err) {
      logMessage('error', err.message);
    }
  });

  document.getElementById('btn-reset-lock')?.addEventListener('click', async () => {
    if (!activeProvider) return;
    try {
      await activeProvider.resetFault();
    } catch (err) {
      logMessage('error', err.message);
    }
  });

  // Bounce Slider (Level 0 - 5 => Amplitude scale 0.0 - 0.5)
  const bounceSlider = document.getElementById('bounce-slider');
  bounceSlider?.addEventListener('input', async (e) => {
    const level = parseInt(e.target.value);
    const amp = level * 0.1;
    document.getElementById('bounce-level-txt').textContent = `Level ${level} (Scale ${amp.toFixed(2)})`;
    if (activeProvider) {
      try {
        await activeProvider.setAmplitude(amp);
      } catch (err) {
        logMessage('warn', `Amplitude set warning: ${err.message}`);
      }
    }
  });

  // Frequency Slider (30 - 65 Hz)
  const freqSlider = document.getElementById('frequency-slider');
  freqSlider?.addEventListener('input', async (e) => {
    const hz = parseInt(e.target.value);
    document.getElementById('frequency-txt').textContent = `${hz} Hz`;
    if (activeProvider) {
      try {
        await activeProvider.setFrequency(hz);
      } catch (err) {
        logMessage('warn', `Frequency set warning: ${err.message}`);
      }
    }
  });

  // Volume Slider (0 - 100 %)
  const volSlider = document.getElementById('volume-slider');
  volSlider?.addEventListener('input', async (e) => {
    const vol = parseInt(e.target.value);
    document.getElementById('volume-txt').textContent = `${vol} %`;
    if (audioGainNode && audioCtx) {
      audioGainNode.gain.setValueAtTime((vol / 100) * 1.5, audioCtx.currentTime);
    }
    if (activeProvider) {
      try {
        await activeProvider.setVolume(vol);
      } catch (err) {
        logMessage('warn', `Volume set warning: ${err.message}`);
      }
    }
  });

  // Sound Preset Buttons
  document.querySelectorAll('.preset-btn').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const targetBtn = e.currentTarget;
      const presetKey = targetBtn.dataset.preset;
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      targetBtn.classList.add('active');

      const presetNames = {
        pink: '바이오리듬 핑크 노이즈',
        heartbeat: '엄마 심장소리 (Low Pass)',
        lullaby: '바이오 자장가 (Acoustic)',
        off: '음소거 (Off)'
      };
      document.getElementById('sound-mode-txt').textContent = presetNames[presetKey] || presetKey;

      playAudioPreset(presetKey);

      if (activeProvider) {
        try {
          await activeProvider.setPreset(presetKey);
        } catch (err) {
          logMessage('warn', `Preset set warning: ${err.message}`);
        }
      }
    });
  });

  // Auto-Soothing Switch
  document.getElementById('auto-soothing-toggle')?.addEventListener('change', (e) => {
    autoSoothing = e.target.checked;
    logMessage('info', `[AI] Auto Soothing Engine switched to: ${autoSoothing ? 'ENABLED' : 'MANUAL'}`);
  });

  // Baby State Simulation Buttons
  document.getElementById('btn-trigger-sleep')?.addEventListener('click', () => triggerBabyState('sleep'));
  document.getElementById('btn-trigger-light-sleep')?.addEventListener('click', () => triggerBabyState('light_sleep'));
  document.getElementById('btn-trigger-fussing')?.addEventListener('click', () => triggerBabyState('fussing'));
  document.getElementById('btn-trigger-crying')?.addEventListener('click', () => triggerBabyState('crying'));

  // Log Clear Button
  document.getElementById('btn-clear-log')?.addEventListener('click', clearLogs);
}

/**
 * Handle AI Soothing Trigger
 */
function triggerBabyState(state) {
  currentBabyState = state;
  const pill = document.getElementById('baby-state-pill');
  const zzz = document.getElementById('sleep-zzz');
  const cry = document.getElementById('cry-waves');

  let targetLevel = 2;
  let targetPreset = 'pink';
  let targetVol = 45;

  if (state === 'sleep') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot sleeping"></span> 수면 중 (Deep Sleep)';
    zzz.style.display = 'block';
    cry.style.display = 'none';
    logMessage('success', '[IMU_AI] 아기가 깊은 수면에 들었습니다. 진동을 부드럽게 감속합니다.');
    targetLevel = 1; targetPreset = 'pink'; targetVol = 30;
  } else if (state === 'light_sleep') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot" style="background:#f59e0b"></span> 얕은 수면 (REM Sleep)';
    zzz.style.display = 'block';
    cry.style.display = 'none';
    logMessage('info', '[IMU_AI] 미세 움직임 감지됨. 안정 심장박동 리듬을 공급합니다.');
    targetLevel = 2; targetPreset = 'heartbeat'; targetVol = 45;
  } else if (state === 'fussing') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot" style="background:#a855f7"></span> 칭얼거림 (Fussing)';
    zzz.style.display = 'none';
    cry.style.display = 'block';
    logMessage('warn', '[AI_SOOTHING] 칭얼거림 인식됨. 진동 강도 및 백색 소음을 한 단계 높입니다.');
    targetLevel = 3; targetPreset = 'pink'; targetVol = 60;
  } else if (state === 'crying') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot crying"></span> 심한 울음 (Crying)';
    zzz.style.display = 'none';
    cry.style.display = 'block';
    logMessage('error', '[ALERT] 심한 울음 패턴 감지! 집중 달래기 모드를 즉시 활성화합니다.');
    targetLevel = 4; targetPreset = 'pink'; targetVol = 75;
  }

  if (activeProvider && activeProvider.mode === 'simulation') {
    activeProvider.setBabyState(state, autoSoothing);
  }

  if (autoSoothing) {
    const bounceSlider = document.getElementById('bounce-slider');
    if (bounceSlider) {
      bounceSlider.value = targetLevel;
      document.getElementById('bounce-level-txt').textContent = `Level ${targetLevel} (Scale ${(targetLevel * 0.1).toFixed(2)})`;
    }

    const volSlider = document.getElementById('volume-slider');
    if (volSlider) {
      volSlider.value = targetVol;
      document.getElementById('volume-txt').textContent = `${targetVol} %`;
    }

    // Set preset button active
    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.preset === targetPreset);
    });

    if (activeProvider) {
      activeProvider.setAmplitude(targetLevel * 0.1);
      activeProvider.setVolume(targetVol);
      activeProvider.setPreset(targetPreset);
    }
    playAudioPreset(targetPreset);
  }
}

// Simple Web Audio API Synthesizer for Audio Preview
function playAudioPreset(presetKey) {
  if (presetKey === 'off') {
    stopAudio();
    return;
  }

  try {
    if (!audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) audioCtx = new AudioCtxClass();
    }
    if (!audioCtx) return;

    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    const presetMap = {
      pink: { type: 'bandpass', freq: 450, gain: 1.5 },
      heartbeat: { type: 'lowpass', freq: 120, gain: 4.0 },
      lullaby: { type: 'lowpass', freq: 280, gain: 2.0 }
    };

    const cfg = presetMap[presetKey] || presetMap.pink;

    if (audioFilterNode && audioGainNode) {
      audioFilterNode.type = cfg.type;
      audioFilterNode.frequency.setTargetAtTime(cfg.freq, audioCtx.currentTime, 0.05);
      audioGainNode.gain.setTargetAtTime(cfg.gain, audioCtx.currentTime, 0.05);
      return;
    }

    const bufferSize = audioCtx.sampleRate * 2;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = audioCtx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    audioFilterNode = audioCtx.createBiquadFilter();
    audioFilterNode.type = cfg.type;
    audioFilterNode.frequency.value = cfg.freq;

    audioGainNode = audioCtx.createGain();
    const currentVol = Number(document.getElementById('volume-slider')?.value || 45);
    audioGainNode.gain.value = (currentVol / 100) * cfg.gain;

    whiteNoise.connect(audioFilterNode);
    audioFilterNode.connect(audioGainNode);
    audioGainNode.connect(audioCtx.destination);

    whiteNoise.start();
    noiseNode = whiteNoise;
  } catch (e) {
    console.warn('Audio init skipped or auto-play restricted:', e);
  }
}

function stopAudio() {
  if (noiseNode) {
    try {
      noiseNode.stop();
      noiseNode.disconnect();
    } catch (e) {}
    noiseNode = null;
  }
  audioFilterNode = null;
  audioGainNode = null;
}

function logMessage(type, msg) {
  const term = document.getElementById('log-terminal');
  if (term) {
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    line.innerText = `[${timestamp}] ${msg}`;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
  }
  // Mirror to server log endpoint
  try {
    fetch(`/api/client-log?type=${encodeURIComponent(type)}&msg=${encodeURIComponent(msg)}`).catch(() => {});
  } catch (e) {}
}

function clearLogs() {
  const term = document.getElementById('log-terminal');
  if (term) term.innerHTML = '';
}
