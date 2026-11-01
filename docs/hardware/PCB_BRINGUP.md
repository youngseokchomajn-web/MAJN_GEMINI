# MAJN PCB #0005 실물 하드웨어 Bring-up 가이드 (PCB BRINGUP)

> **대상 하드웨어**: MAJN 스마트 배시넷 PCB #0005 프로토타입  
> **비교 기준**: Rev_C_mfg 4층 제조 패키지  
> **최신 펌웨어 기준**: `c63e60a` (v0.1.0-mvp)  
> **문서 상태**: 실행 및 기록 대기  

---

## 0. 하드웨어 물리 제약 사항 (필수 숙지)

1. **[물리 버튼 전무]**: PCB #0005 보드에는 BOOT, EN 버튼이 일체 없습니다. 버튼을 누르는 가이드는 불가능합니다.
2. **[시리얼 플래시 불가]**: CP2102 헤더는 TX, RX, GND 3가닥만 결선되어 있어 DTR/RTS 자동 부트로더 리셋 회로가 없습니다. 유선(`esptool`) 다운로드는 불가능하며, **오직 무선 OTA(BLE OTA 또는 Wi-Fi HTTP /update)로만 플래시가 가능**합니다.
3. **[외장 안테나(u.FL) 특성]**: ESP32-WROOM-32UE는 외장 IPEX u.FL 안테나형 모듈(C701345)입니다. 외장 안테나 미체결 시 누설 전파(-84 dBm 수준)만 발생하므로, 무선 통신 시험 시 스마트폰을 10cm 이내로 근접시켜야 합니다.

---

## 1. PCB #0005 vs Rev_C_mfg 핵심 대조표

| 항목 | PCB #0005 실물 | Rev_C_mfg 양산형 | 조치 및 유의사항 |
|---|---|---|---|
| **MCU 모듈** | ESP32-WROOM-32UE-N8 (외장 u.FL) | ESP32-WROOM-32UE-N8 | 안테나 케이블 체결 필수 |
| **3.3V LDO** | AP2112K-3.3TRG1 (600mA) | TLV75733PDBVR (1.0A) | #0005는 Wi-Fi 출력 15dBm 표준 유지 필수 |
| **오디오 앰프** | TAS5805MPWPR (TSSOP-28) | TAS5805MPWPR | I2C 7비트 주소 `0x2C` (ADR 풀다운) |
| **12V 승압기** | MP3426DL (12.17V 피드백) | MP3426DL (12.45V 피드백) | R1=143k/150k, R2=16k 차이 |
| **스피커 커넥터** | 2.54mm 수직 헤더 | C49423315 라이트앵글 2P | 케이스 13.5mm 간섭 방지 확인 |
| **UART 헤더** | 2.54mm 수직 6P (TX/RX/GND만 연결) | C124367 라이트앵글 6P | 디버그 시리얼 모니터링 전용 |

---

## 2. 단계별 Bring-up 절차 (Step-by-Step)

### Step 1. 비전원(Unpowered) DMM 쇼트 검사
전원을 투입하기 전 반드시 디지털 멀티미터(저항/도통 모드)로 주요 레일의 접지 단락 여부를 검사합니다.
- [ ] **USB 5V VBUS $\leftrightarrow$ GND**: 저항값 > 100kΩ 확인 (단락 0Ω 시 전원 투입 금지)
- [ ] **3.3V Rail $\leftrightarrow$ GND**: 저항값 > 1kΩ 확인
- [ ] **12V PVDD $\leftrightarrow$ GND**: 저항값 > 50kΩ 확인
- [ ] **PPTC Fuse F1 (3.0A)**: 양단 도통 저항 < 0.1Ω 확인

### Step 2. 최초 전원 인가 (Current Limited Power-on)
1. 직류 전원공급기(Power Supply)를 5.0V, 전류 제한 500mA로 설정합니다.
2. USB-C 포트 또는 VBUS 테스트 포인트에 전원을 연결합니다.
3. 무부하 대기 전류 확인:
   - 정상 범위: **45mA ~ 75mA** (ESP32 부팅 직후 Wi-Fi AP 대기 상태)
   - 이상 징후: 전류가 300mA 이상 급증하거나 전압 강하 발생 시 즉시 전원 차단!

### Step 3. 주요 전원 레일 전압 실측
| 계측 포인트 | 목표 전압 | 허용 범위 | 실측치 (V) | 판정 |
|---|:---:|:---:|:---:|:---:|
| **VBUS_5V (C1/C2)** | 5.00V | 4.75V ~ 5.25V | ________ V | [ ] |
| **VCC_3V3 (U2 VOUT)** | 3.30V | 3.23V ~ 3.37V | ________ V | [ ] |
| **PVDD_12V (C8/C9)** | 12.17V | 11.80V ~ 12.50V | ________ V | [ ] |
| **ESP_EN (U1.3)** | 3.30V | 3.10V ~ 3.30V | ________ V | [ ] |
| **AMP_PDN (U4.12)** | 3.30V | 3.10V ~ 3.30V | ________ V | [ ] |
*(※ 주의: U4 Pin 2는 DVDD 3.3V 전원 핀이며, AMP_PDN은 Pin 12입니다. 프로빙 시 쇼트에 각별히 유의하십시오.)*

### Step 4. 디버그 UART 시리얼 로그 확인
CP2102 시리얼 헤더의 TX, RX, GND를 PC에 연결하고 115,200 bps로 부팅 로그를 모니터링합니다.

```bash
# 시리얼 모니터링 실행 (macOS)
python3 /Users/youngseok/Desktop/majn/tools/serial_monitor.py
# 또는
screen /dev/cu.usbserial-* 115200
```

**정상 부팅 시 확인해야 할 핵심 로그**:
1. `rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)`
2. `[TAS5805M] Init success. Device ID: 0x2C, State: STANDBY (Hi-Z)`
3. `[WIFI] SoftAP started. SSID: MAJN-BASSINET-XXXX, Ch: 6`
4. `[BLE] Advertising started. Adv interval: 7.5ms ~ 22.5ms`
5. `[SYSTEM] Boot complete. System State: READY`

### Step 5. TAS5805M I2C 통신 및 무음 팝노이즈 검증
- 오실로스코프 프로브를 스피커 출력단(`NET_SPK_A+`, `NET_SPK_A-`)에 물리고 전원 On/Off를 3회 반복합니다.
- **판정 기준**: 전원 투입 순간 과도 전압 스파이크(DC Pop)가 50mV 미만일 것 (STANDBY Hi-Z 정상 안착).

---

## 3. 이상 현상 발생 시 조치 매뉴얼 (Troubleshooting)

| 증상 | 원인 추정 | 긴급 조치 사항 |
|---|---|---|
| **부팅 직후 전류 300mA 이상 급증** | 12V Boost 인덕터 단락 또는 TAS5805M 솔더링 브릿지 | 즉시 전원 OFF. U3, U4 핀 솔더링 현미경 검사. |
| **3.3V 전압이 1.5V 이하로 처짐** | ESP32 내부 단락 또는 LDO U2 과열 보호 | USB 전류 제한 확인 및 U2 발열 상태 점검. |
| **I2C 에러: TAS5805M 통신 실패** | ADR 핀 전압 이상(0x2C 주소 불일치) 또는 PDN 로우 고정 | R12(4.7k 풀업) 및 R_PDN(10k 풀업) 전압 3.3V 확인. |
| **스마트폰 Wi-Fi 신호 안 뜸** | 외장 u.FL 안테나 케이블 미체결 | 스마트폰을 ESP32 모듈 5cm 이내로 밀착하여 재검색. |
