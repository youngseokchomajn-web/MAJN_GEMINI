# MAJN 시제품 PCB #0005 진동 구동 복구 및 펌웨어 오류 진단 보고서

- **작성일**: 2026-10-22
- **대상**: MAJN 하드웨어 시제품 1호기 (PCB #0005)
- **주요 부품**: ESP32-WROOM-32E (U1), MP3426DL 12V Boost (U3), TI TAS5805M Class-D 앰프 (U4), LSM6DSOX 6축 IMU (U5)
- **부하 액추에이터**: 24.8Ω 익사이터 2개 직렬 연결 (`J2` 단자 채널 B)

---

## 1. 하드웨어 계측 및 물리적 팩트 전수 확인

| 계측 항목 | 위치 및 기준 | 실측값 | 판정 |
|:---|:---|:---:|:---:|
| **3.3V 시스템 전원 (VCC_3V3)** | U2 (AP2112K) 출력 / C14 | **3.20 V** | **정상** (ESP32 및 디지털 로직 구동 양호) |
| **12V 승압 전원 (PVDD)** | D3 다이오드 캐소드 / C15 | **12.00 V** | **정상** (MP3426 승압 컨버터 정상 동작) |
| **앰프 파워다운 핀 (PDN)** | R13 상단 / GPIO15 | **3.20 V** | **정상** (Active-HIGH 인가 확인) |
| **익사이터 부하 저항** | J2 커넥터 2핀 도통 계측 | **24.8 Ω** | **정상** (직렬 배선 정상, 단선 및 합선 없음) |
| **스피커 출력 교류 전압 (AC V)** | J2 커넥터 양단 (`~V 200`) | **0.00 V** | **출력 차단 발생 (Hi-Z 잠김)** |

> **초기 진단 결론**: 12V 승압, 3.3V 전원, PDN 활성화 및 부하 저항은 완벽하게 정상이나, **TAS5805M 앰프가 내부 보호 로직(Fault Latch) 또는 클럭 동기 실패로 인해 스스로 출력을 Hi-Z(High Impedance)로 차단**하고 있는 상태였음.

---

## 2. 4대 핵심 결함 심층 원인 분석 (Root Cause Analysis)

### 결함 ①: TI TAS5805M 내부 Fault Latch 및 레지스터 북/페이지 시퀀스 오류
- **현상**: 부팅 시 MP3426 승압 전원 소프트스타트 및 I2S 클럭 안정화 과정에서 앰프가 일시적인 전원/클럭 글리치를 감지하면, 이를 내부 레지스터(`0x70 CHAN_FAULT`, `0x71 GLOBAL_FAULT1`)에 래치(Latch)하고 영구적인 Hi-Z(출력 차단) 모드로 고정됨.
- **원인 코드**:
  - `REG_FAULT_CLEAR (0x78 = 0x80)`을 호출하지 않아 하드웨어 전원을 껐다 켜도 부팅 시 즉시 차단 상태로 복귀함.
  - TI 데이터시트 규격상 Book 변경(`0x7F`)을 수행하려면 반드시 **Page 0(`0x00=0x00`)으로 먼저 진입**한 뒤 `0x7F`를 써야 하나, 기존 코드는 Page 0 이동 없이 `0x7F`에 Book 번호를 기록하여 레지스터 설정이 적용되지 않음.
- **해결책**:
  - TI 공식 3단계 북/페이지 시퀀스(`0x00=0x00` $\rightarrow$ `0x7F=book` $\rightarrow$ `0x00=page`) 구현.
  - `enterPlayState()` 진입 시 반드시 `writeRegister(0x78, 0x80)` 강제 클리어 후 `0x03` (Play 모드) 진입.

---

### 결함 ②: I2S DMA 버퍼 언더런(Underflow) 및 클럭 소실
- **현상**: ESP32의 I2S 오디오 스트림이 순간적으로 끊기면 TAS5805M이 "Clock Lost"를 감지하여 PWM 스위칭을 즉각 중단하고 차단 모드로 진입.
- **원인 코드**:
  - `AudioOutputTask` 루프 내에 `vTaskDelay(pdMS_TO_TICKS(1))`이 삽입되어 있었음.
  - 48kHz / 256 프레임(5.33ms) 단위로 DMA 블로킹 전송을 수행하는데, 매 전송마다 1ms의 불필요한 태스크 지연이 발생하여 DMA 버퍼가 고갈되고 클럭 글리치가 주기적으로 발생함.
  - 앰프가 대기 상태(`gCurrentAmplitude == 0`)일 때 `renderAudioBlock()`이 DMA 쓰기를 중단하여 I2S BCLK/LRCLK 출력이 완전히 정지됨.
- **해결책**:
  - `AudioOutputTask`의 `vTaskDelay`를 제거하고, `i2s_write(..., portMAX_DELAY)`의 순수 하드웨어 DMA 블로킹 타이밍에 100% 동기화.
  - 진동이 멈춘 상태에서도 0(무음) 데이터를 지속적으로 DMA에 밀어넣어 **BCLK(1.536MHz) 및 LRCLK(48kHz)가 24시간 끊김 없이 영구 유지**되도록 패치.

---

### 결함 ③: 스피커 채널 매핑 및 개별 채널 볼륨 설정 누락
- **현상**: 보드 상면의 익사이터는 물리적으로 `J2` 커넥터(회로상 채널 B / 오른쪽 출력)에 꽂혀 있었으나, 소리가 나지 않음.
- **원인 코드**:
  - 마스터 볼륨(`0x4C`)만 0dB로 설정하고, 개별 채널 볼륨(`0x4D CH1_VOL`, `0x4E CH2_VOL`)을 명시적으로 초기화하지 않음.
- **해결책**:
  - `tas5805m.cpp` 초기화 시 마스터(`0x4C`), Ch1(`0x4D`), Ch2(`0x4E`)를 전수 `0x30` (0dB Unity Gain)으로 명시적 설정.
  - 스테레오 버퍼 생성 시 Ch1(Left/J1)과 Ch2(Right/J2)에 동일한 진폭의 사인파를 듀얼 출력.

---

### 결함 ④: Web BLE OTA 무선 펌웨어 업데이트 83% 패킷 유실 결함
- **현상**: 최신 펌웨어 빌드 후 무선 OTA를 진행했음에도 보드가 이전 펌웨어 상태로 계속 머물러 있었음.
- **원인 분석**:
  - 기존 `ble_ota_flash.py` 스크립트가 `response=False` (Write Without Response) 방식으로 512바이트씩 5ms마다 고속 전송함.
  - macOS CoreBluetooth 스택 및 ESP32 BLE GATT 버퍼 수용한계를 초과하여 전체 1.8MB 패킷 중 **약 83%가 전송 도중 유실**됨.
  - ESP32의 `ota_ble_service.cpp`는 총 1,804,496바이트 중 300,000바이트(17%)만 수신한 상태에서 `OTA_END`를 받았고, `Update.end()`가 `"Update.end failed: incomplete"` 에러를 내며 롤백함.
  - 호스트 스크립트는 이 에러 노티피케이션을 구독하지 않고 단순히 전송 완료로 간주하고 있었음.
- **해결책**:
  - `write_gatt_char(..., response=True)`로 변경하여 **ATT Write Response(ACK) 수신 확인 후 다음 패킷을 전송하는 100% 무손실 신뢰성 파이프라인**으로 전환.
  - 호스트에서 `OTA_CONTROL_UUID` 노티피케이션을 실시간 구독하여 ESP32의 실제 플래시 기록 진행률(`progress`)을 1:1 대조 검증.

---

## 3. 최신 펌웨어 산출물 및 빌드 정보

- **환경**: `esp32_full_hw`
- **MCU**: ESP32-WROOM-32E (8MB Flash, Flash Mode: DIO, 40MHz)
- **파티션 구조**: `partitions_8mb_ota.csv` (app0: 3.2MB, app1: 3.2MB 지원)
- **빌드 산출물**:
  1. `firmware.bin` (크기: 1,804,091 bytes, 위치: `인증준비/firmware/.pio/build/esp32_full_hw/firmware.bin`)
  2. `firmware.factory.bin` (통합 부트로더 + 파티션 테이블 + 앱 이미지)
  3. `~/Desktop/majn_latest_firmware.bin` (배포 및 OTA용 단일 바이너리)

---

## 4. 실시간 텔레메트리 모니터링 연동 사양

최신 펌웨어는 BLE Telemetry (`7b4d0003-...`)를 통해 매 200ms마다 아래의 앰프 진단 정보를 실시간 전송합니다:
```json
{
  "type": "telemetry",
  "protocol": 1,
  "firmware": "0.2.0-ble",
  "uptime_ms": 12345,
  "state": "RUNNING",
  "safety_lock": false,
  "frequency_hz": 45.0,
  "amplitude_scale": 0.4,
  "amp_ready": true,
  "amp_status": "READY(0x2C S:0x03 CF:0x00 GF:0x00)",
  "accel_g": {"x": -0.868, "y": 0.000, "z": 0.500}
}
```
- `amp_ready`: 앰프 I2C 정상 통신 여부 (`true`/`false`)
- `amp_status`: 감지된 I2C 주소(`0x2C`), 동작 상태(`S:0x03` = Play), 채널 오류(`CF`), 글로벌 오류(`GF`)
