/* ═════════════════════════════════════════════════════════════════
   MAJN Smart Bassinet v2 Simulator & Interactive Controller Logic
   (Using Exact Original Baby Assets: baby_crying_v3.png & baby_sleeping_v3.png)
   ═════════════════════════════════════════════════════════════════ */

let currentMode = 0; // 0: OFF, 1: LOW, 2: MID, 3: HIGH
let isAutoDetect = true;
let timerSeconds = 0;
let timerInterval = null;

// Bio Wave Canvas Vars
let canvas, ctx;
let wavePhase = 0;

document.addEventListener('DOMContentLoaded', () => {
    initBioCanvas();
    initSimEvents();
    updateUI();
});

/* -----------------------------------------------------------------
   1. Real-time IR-UWB Radar Bio-Wave Canvas Visualizer
   ----------------------------------------------------------------- */
function initBioCanvas() {
    canvas = document.getElementById('bioCanvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth - 32;
        canvas.height = 65;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    requestAnimationFrame(renderWave);
}

function renderWave() {
    if (!ctx || !canvas) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;

    ctx.beginPath();
    ctx.lineWidth = 2.5;

    const grad = ctx.createLinearGradient(0, 0, width, 0);
    if (currentMode === 0) {
        grad.addColorStop(0, '#94A3B8');
        grad.addColorStop(1, '#CBD5E1');
    } else if (currentMode === 3) {
        grad.addColorStop(0, '#FF7675');
        grad.addColorStop(1, '#6C5CE7');
    } else {
        grad.addColorStop(0, '#6C5CE7');
        grad.addColorStop(1, '#00CEC9');
    }
    ctx.strokeStyle = grad;

    const freq = currentMode === 0 ? 0.03 : currentMode * 0.05 + 0.03;
    const amp = currentMode === 0 ? 5 : currentMode * 10 + 6;
    const speed = currentMode === 0 ? 0.02 : 0.04 + currentMode * 0.025;

    wavePhase += speed;

    for (let x = 0; x < width; x++) {
        const y = centerY + Math.sin(x * freq + wavePhase) * amp + (Math.random() - 0.5) * (currentMode * 1.2);
        if (x === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }

    ctx.stroke();

    requestAnimationFrame(renderWave);
}

/* -----------------------------------------------------------------
   2. Simulator Controller State Handlers
   ----------------------------------------------------------------- */
function initSimEvents() {
    const autoToggle = document.getElementById('autoDetectToggle');
    if (autoToggle) {
        autoToggle.checked = isAutoDetect;
        autoToggle.addEventListener('change', (e) => {
            isAutoDetect = e.target.checked;
            const statusToast = document.getElementById('toastMsg');
            if (statusToast) {
                statusToast.innerText = isAutoDetect ? "울음 감지 자동 모드 ON 🎙️" : "수동 제어 모드 🕹️";
                statusToast.style.opacity = '1';
                setTimeout(() => statusToast.style.opacity = '0', 2500);
            }
        });
    }
}

function setSimMode(mode) {
    currentMode = mode;

    const btns = document.querySelectorAll('.mode-btn');
    btns.forEach((btn, idx) => {
        if (idx === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (currentMode > 0) {
        timerSeconds = currentMode * 600; // 10m, 20m, 30m
        startTimer();
    } else {
        stopTimer();
    }

    updateUI();
}

function updateUI() {
    const statusText = document.getElementById('simStatusText');
    const ledIndicator = document.getElementById('simLed');
    const ledStatusText = document.getElementById('simLedText');
    const babyImg = document.getElementById('babyImg');
    const babyWrapper = document.getElementById('babyWrapper');
    const rippleContainer = document.getElementById('vibrationRipples');
    const bpmVal = document.getElementById('bpmVal');

    if (currentMode === 0) {
        if (statusText) {
            statusText.innerText = "앗, 아기가 깨서 칭얼거리네요! (진동을 켜주세요)";
            statusText.style.color = "#E74C3C";
        }
        if (ledIndicator) {
            ledIndicator.style.background = "#E74C3C";
            ledIndicator.style.boxShadow = "none";
        }
        if (ledStatusText) ledStatusText.innerText = "정지 (OFF)";
        if (babyImg) {
            babyImg.src = "images/baby_crying_v3.png";
        }
        if (babyWrapper) {
            babyWrapper.classList.add('crying');
        }
        if (rippleContainer) {
            rippleContainer.classList.remove('v-active');
        }
        if (bpmVal) bpmVal.innerText = "118 BPM (상승)";
    } else {
        if (statusText) {
            statusText.innerText = "아기가 안정을 느끼며 편안하게 쌔근쌔근 잠듭니다 💤";
            statusText.style.color = "#00B894";
        }
        if (ledIndicator) {
            ledIndicator.style.background = "#2ECC71";
            ledIndicator.style.boxShadow = "0 0 10px #2ECC71";
        }
        const modeLabels = ["정지 (OFF)", "약한 자극 (LOW)", "중간 자극 (MID)", "강한 자극 (HIGH)"];
        if (ledStatusText) ledStatusText.innerText = modeLabels[currentMode];

        if (babyWrapper) {
            babyWrapper.classList.remove('crying');
        }
        if (rippleContainer) {
            rippleContainer.classList.add('v-active');
        }

        // Smooth transition to exact original sleeping baby asset
        setTimeout(() => {
            if (currentMode > 0 && babyImg) {
                babyImg.src = "images/baby_sleeping_v3.png";
            }
        }, 300);

        if (bpmVal) {
            const targetBpm = 85 - (currentMode * 3);
            bpmVal.innerText = `${targetBpm} BPM (안정)`;
        }
    }
}

/* -----------------------------------------------------------------
   3. Timer Controller Logic
   ----------------------------------------------------------------- */
function startTimer() {
    stopTimer();
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        if (timerSeconds > 0) {
            timerSeconds--;
            updateTimerDisplay();
        } else {
            setSimMode(0);
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerSeconds = 0;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const timerDisplay = document.getElementById('timerVal');
    if (!timerDisplay) return;
    const mins = Math.floor(timerSeconds / 60);
    const secs = timerSeconds % 60;
    timerDisplay.innerText = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/* -----------------------------------------------------------------
   4. Inquiry Modal Popup Logic
   ----------------------------------------------------------------- */
function openInquiryModal(type) {
    const modal = document.getElementById('inquiryModal');
    const modalTitle = document.getElementById('modalTitle');
    if (!modal) return;

    if (type === 'B2B') {
        if (modalTitle) modalTitle.innerText = "산후조리원 / B2B 무료 시범 도입 문의";
    } else {
        if (modalTitle) modalTitle.innerText = "마중 스마트 배시넷 사전 예약 신청";
    }

    modal.classList.add('active');
}

function closeInquiryModal() {
    const modal = document.getElementById('inquiryModal');
    if (modal) modal.classList.remove('active');
}

function handleInquirySubmit(event) {
    event.preventDefault();
    closeInquiryModal();
    const wadizModal = document.getElementById('wadizSuccessModal');
    if (wadizModal) {
        wadizModal.classList.add('active');
    } else {
        alert("감사합니다! 성공적으로 접수되었습니다. 담당자가 빠르게 연락드리겠습니다.");
    }
}

function closeWadizModal() {
    const wadizModal = document.getElementById('wadizSuccessModal');
    if (wadizModal) wadizModal.classList.remove('active');
}
