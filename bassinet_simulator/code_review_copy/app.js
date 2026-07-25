// MAJN Smart Bassinet Simulator Logic Engine

let currentState = 'sleep'; // 'sleep', 'light_sleep', 'fussing', 'crying'
let autoSoothing = true;
let bounceLevel = 2;
let soundPreset = 'pink';
let volume = 45;

let imuChart = null;
let chartDataX = [];
let chartDataY = [];
let chartDataZ = [];
let maxPoints = 30;

// Web Audio Synth for White Noise & Heartbeat Simulation
let audioCtx = null;
let noiseNode = null;
let gainNode = null;

document.addEventListener('DOMContentLoaded', () => {
  initIMUChart();
  initEventListeners();
  startSimulationLoop();
  logMessage('system', '[SYSTEM] MAJN Bassinet Closed-loop Controller Ready.');
});

// Chart.js IMU Initialization
function initIMUChart() {
  const ctx = document.getElementById('imuChart').getContext('2d');
  
  for (let i = 0; i < maxPoints; i++) {
    chartDataX.push(0);
    chartDataY.push(0);
    chartDataZ.push(1); // 1g Gravity
  }

  imuChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array.from({length: maxPoints}, (_, i) => `${i}s`),
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
          min: -2.5,
          max: 2.5,
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
  // Auto Soothing Toggle
  document.getElementById('auto-soothing-toggle').addEventListener('change', (e) => {
    autoSoothing = e.target.checked;
    logMessage('info', `[AI] Auto Soothing Engine switched to: ${autoSoothing ? 'ENABLED' : 'MANUAL'}`);
  });

  // Bounce Slider
  const bounceSlider = document.getElementById('bounce-slider');
  bounceSlider.addEventListener('input', (e) => {
    bounceLevel = parseInt(e.target.value);
    updateBounceUI();
    logMessage('info', `[ACTUATOR] Manual Bouncing set to Level ${bounceLevel}`);
  });

  // Volume Slider
  const volumeSlider = document.getElementById('volume-slider');
  volumeSlider.addEventListener('input', (e) => {
    volume = parseInt(e.target.value);
    document.getElementById('volume-txt').innerText = `${volume} dB`;
    if (gainNode) {
      gainNode.gain.setValueAtTime(volume / 100 * 0.2, audioCtx.currentTime);
    }
  });

  // Emergency Stop
  document.getElementById('btn-emergency-stop').addEventListener('click', () => {
    bounceLevel = 0;
    soundPreset = 'off';
    document.getElementById('bounce-slider').value = 0;
    updateBounceUI();
    updateSoundUI();
    stopAudio();
    logMessage('error', '[EMERGENCY] Emergency Stop Triggered! All Actuators Shutdown.');
  });
}

// State Trigger Simulation
function triggerBabyState(state) {
  currentState = state;
  const pill = document.getElementById('baby-state-pill');
  const zzz = document.getElementById('sleep-zzz');
  const cry = document.getElementById('cry-waves');

  if (state === 'sleep') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot sleeping"></span> 수면 중 (Deep Sleep)';
    zzz.style.display = 'block';
    cry.style.display = 'none';
    logMessage('success', '[IMU_AI] Baby is in Deep Sleep. Calming actuators down.');
    
    if (autoSoothing) {
      bounceLevel = 1;
      soundPreset = 'pink';
      volume = 35;
    }
  } else if (state === 'light_sleep') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot" style="background:#f59e0b"></span> 얕은 수면 (REM Sleep)';
    zzz.style.display = 'block';
    cry.style.display = 'none';
    logMessage('info', '[IMU_AI] Micro-movements detected. Adjusting gentle rhythm.');
    
    if (autoSoothing) {
      bounceLevel = 2;
      soundPreset = 'heartbeat';
      volume = 45;
    }
  } else if (state === 'fussing') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot" style="background:#a855f7"></span> 칭얼거림 (Fussing)';
    zzz.style.display = 'none';
    cry.style.display = 'block';
    logMessage('warn', '[AI_SOOTHING] Fussing pattern recognized! Accelerating bouncing motion & sound.');
    
    if (autoSoothing) {
      bounceLevel = 3;
      soundPreset = 'pink';
      volume = 55;
    }
  } else if (state === 'crying') {
    pill.className = 'status-pill';
    pill.innerHTML = '<span class="dot crying"></span> 심한 울음 (Crying)';
    zzz.style.display = 'none';
    cry.style.display = 'block';
    logMessage('error', '[ALERT] High-amplitude Crying detected! Max soothing power engaged.');
    
    if (autoSoothing) {
      bounceLevel = 4;
      soundPreset = 'pink';
      volume = 70;
    }
  }

  // Update UI Elements
  document.getElementById('bounce-slider').value = bounceLevel;
  document.getElementById('volume-slider').value = volume;
  document.getElementById('volume-txt').innerText = `${volume} dB`;
  updateBounceUI();
  updateSoundUI();
  playAudioPreset(soundPreset);
}

function setSoundPreset(preset) {
  soundPreset = preset;
  updateSoundUI();
  playAudioPreset(preset);
  logMessage('info', `[TAS5805M] Audio DSP Preset Switched to: ${preset.toUpperCase()}`);
}

function updateBounceUI() {
  const txts = ['Off', 'Level 1 (Gentle Breeze)', 'Level 2 (Soft Rocking)', 'Level 3 (Medium Calm)', 'Level 4 (Strong Soothe)', 'Level 5 (Emergency Calm)'];
  document.getElementById('bounce-level-txt').innerText = txts[bounceLevel] || 'Off';
  
  const cradle = document.getElementById('bassinet-cradle');
  cradle.style.animation = bounceLevel > 0 ? `rocking ${1.8 / bounceLevel}s infinite ease-in-out` : 'none';
}

function updateSoundUI() {
  const names = { pink: '바이오리듬 핑크 노이즈', heartbeat: '엄마 심장소리 (Low Pass Filter)', lullaby: '바이오 자장가 (Acoustic)', off: '음소거 (Off)' };
  document.getElementById('sound-mode-txt').innerText = names[soundPreset] || '음소거';

  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  const btnMap = { pink: 0, heartbeat: 1, lullaby: 2, off: 3 };
  if (btnMap[soundPreset] !== undefined) {
    document.querySelectorAll('.preset-btn')[btnMap[soundPreset]].classList.add('active');
  }
}

// Real-time Simulation Loop (10 Hz Update)
function startSimulationLoop() {
  setInterval(() => {
    // Generate IMU Signal Noise based on State & Bounce Level
    let noiseAmp = 0.05;
    if (currentState === 'light_sleep') noiseAmp = 0.15;
    if (currentState === 'fussing') noiseAmp = 0.4;
    if (currentState === 'crying') noiseAmp = 1.2;

    let bounceFreq = bounceLevel * 0.8;
    let time = Date.now() / 1000;

    let accX = Math.sin(time * bounceFreq) * (bounceLevel * 0.15) + (Math.random() - 0.5) * noiseAmp;
    let accY = Math.cos(time * bounceFreq) * (bounceLevel * 0.12) + (Math.random() - 0.5) * noiseAmp;
    let accZ = 1.0 + (Math.random() - 0.5) * noiseAmp * 0.5;

    // Update Chart
    chartDataX.shift(); chartDataX.push(accX);
    chartDataY.shift(); chartDataY.push(accY);
    chartDataZ.shift(); chartDataZ.push(accZ);
    imuChart.update();

    // Randomize Voltage telemetry slightly
    document.getElementById('pvdd-voltage').innerText = (12.12 + (Math.random() - 0.5) * 0.04).toFixed(2) + ' V';
    document.getElementById('pvdd-val').innerText = (12.12 + (Math.random() - 0.5) * 0.04).toFixed(2) + 'V';
    document.getElementById('vdd-voltage').innerText = (3.31 + (Math.random() - 0.5) * 0.01).toFixed(2) + ' V';
    document.getElementById('amp-temp').innerText = (41.5 + (bounceLevel * 0.6) + (Math.random() - 0.5) * 0.2).toFixed(1) + ' °C';

  }, 100);
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
      womb: { type: 'lowpass', freq: 250, gain: 4.0 },
      pink: { type: 'bandpass', freq: 450, gain: 1.5 },
      white: { type: 'highpass', freq: 800, gain: 0.8 },
      heartbeat: { type: 'lowpass', freq: 120, gain: 6.0 }
    };

    const cfg = presetMap[presetKey] || presetMap.womb;

    // Reuse filter and gain nodes dynamically if already created
    if (audioFilterNode && audioGainNode) {
      audioFilterNode.type = cfg.type;
      audioFilterNode.frequency.setTargetAtTime(cfg.freq, audioCtx.currentTime, 0.05);
      audioGainNode.gain.setTargetAtTime(cfg.gain, audioCtx.currentTime, 0.05);
      console.log(`🎵 Sound Preset Updated dynamically: ${presetKey} (${cfg.freq}Hz)`);
      return;
    }

    // Create Web Audio Noise Generator Chain once
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
    audioGainNode.gain.value = cfg.gain;

    whiteNoise.connect(audioFilterNode);
    audioFilterNode.connect(audioGainNode);
    audioGainNode.connect(audioCtx.destination);

    whiteNoise.start();
    noiseNode = whiteNoise;
    console.log(`🎵 Sound Generator Started with Preset: ${presetKey}`);

  } catch (e) {
    console.log('Audio init skipped or auto-play restricted:', e);
  }
  if (noiseNode) {
    try {
      noiseNode.stop();
      noiseNode.disconnect();
    } catch (e) {}
    noiseNode = null;
  }
}

function logMessage(type, msg) {
  const term = document.getElementById('log-terminal');
  const line = document.createElement('div');
  line.className = `log-line ${type}`;
  const timestamp = new Date().toLocaleTimeString();
  line.innerText = `[${timestamp}] ${msg}`;
  term.appendChild(line);
  term.scrollTop = term.scrollHeight;
}

function clearLogs() {
  document.getElementById('log-terminal').innerHTML = '';
}
