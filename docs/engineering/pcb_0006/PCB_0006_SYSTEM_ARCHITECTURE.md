# [아키텍처 명세서] MAJN PCB #0006 — 전체 시스템 아키텍처 및 도메인 분리 명세서
(MAJN PCB #0006 System Architecture & Domain Separation Specification)

- **문서 식별자**: `PCB_0006_SYSTEM_ARCHITECTURE`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **적용 대상**: 차기 제어 보드 PCB #0006

---

## 1. 전체 시스템 블록 다이어그램

```mermaid
flowchart TD
    subgraph POWER_INPUT["[전원 입력부]"]
        USBC["USB-C 16-Pin Receptacle<br/>(CC1/CC2: 5.1kΩ Rd)"]
        TVS_IN["SMAJ5.0A TVS Protection"]
        SHUNT_VBUS["R_SHUNT1 (50mΩ)"]
    end

    subgraph POWER_CONVERSION["[전원 변환부]"]
        LDO["3.3V LDO (AP2112K-3.3)<br/>C_in: 1µF, C_out: 22µF"]
        BOOST["MP3426 12V Boost Converter<br/>L1: 4.7µH (Isat>=7A)<br/>D3: SS34 Schottky"]
        R_ISO["R_ISO1 (2512 0Ω Isolation Jumper)"]
        R_BLD["R_BLEED (1.5kΩ 1206 Bleeder)"]
        SHUNT_PVDD["R_SHUNT2 (20mΩ)"]
    end

    subgraph MCU_AND_COMM["[MCU 및 제어부]"]
        ESP32["ESP32-WROOM-32UE-N8<br/>(Core 0: BLE 5.0, Core 1: DSP/Control)"]
        ANT["2.4GHz FPC External Antenna<br/>(u.FL Receptacle)"]
        UART["UART 6-Pin Debug Header"]
    end

    subgraph SENSORS["[센서부]"]
        IMU["LSM6DSOX 6-Axis Motion Sensor<br/>(Safety INT1 -> ESP32 GPIO34)"]
    end

    subgraph AUDIO_SUBSYSTEM["[오디오 구동부]"]
        AMP["TAS5805M Class-D Amplifier<br/>(I2C: 0x2C, PDN: Free GPIO)"]
        FILT["Output Beads (FB1-4) & Filter (C24-27)"]
        PROT["BTL Back-EMF Surge Clamping Array"]
    end

    subgraph ACTUATORS["[구동 액추에이터]"]
        J1_J2["2.0mm Locking Connectors (J1, J2)"]
        EXC["4x TEAX14C02-8 Exciters<br/>(2S2P Wiring -> 16Ω Combined)"]
    end

    USBC --> TVS_IN --> SHUNT_VBUS
    SHUNT_VBUS -->|VBUS 5.0V| LDO
    SHUNT_VBUS -->|VBUS 5.0V| BOOST
    LDO -->|VCC_3V3 (Digital)| ESP32
    LDO -->|VCC_3V3 (Filtered)| IMU
    LDO -->|DVDD 3.3V| AMP

    BOOST -->|BOOST_12V (Pre-Jumper)| R_ISO
    R_ISO -->|PVDD_12V (Amp Power)| SHUNT_PVDD --> R_BLD --> AMP

    ESP32 <-->|SPI Bus: SCLK(18), MOSI(23), MISO(19), CS(5)| IMU
    ESP32 -->|I2S Audio: BCK(26), LRCK(25), DOUT(22)| AMP
    ESP32 <-->|I2C Bus: SDA(21), SCL(27)| AMP
    ESP32 -->|AMP_PDN: Free GPIO (Default LOW)| AMP
    ESP32 -->|BOOST_EN: GPIO4 (Default LOW)| BOOST
    ESP32 <-->|UART0| UART
    ESP32 <-->|RF 2.4GHz| ANT

    AMP --> FILT --> PROT --> J1_J2 --> EXC
```

---

## 2. 전원 도메인 분리 및 분배 계통도

| 전원 레일 명칭 | 공칭 전압 | 정격 전류 | 공급원 | 수용 서브시스템 | 디커플링 및 필터링 사양 |
|:---|:---:|:---:|:---|:---|:---|
| **VBUS_5V** | 5.0 V | 최대 2.0 A | USB-C 5V 어댑터 | LDO 입력, 부스트 입력 | SMAJ5.0A TVS, 10µF 16V X5R (C1) |
| **PVDD_12V** | 12.12 V | 피크 1.5 A | MP3426 승압 회로 | TAS5805M 전력단 | 2x 22µF 35V X7R 1210 (C6, C7), 1.5kΩ 블리더 |
| **VCC_3V3** | 3.3 V | 피크 0.6 A | AP2112K-3.3 LDO | ESP32, TAS5805M DVDD | 22µF 10V X7R (출력 벌크) + 100nF 분기 캡 |
| **VCC_3V3_ANA**| 3.3 V | 최대 20 mA | 3V3 레일 (비드 분리) | LSM6DSOX 센서 코어 | 페라이트 비드 + 100nF C16 + 100nF C11 |
| **GND** | 0 V | - | 4층 Inner 1 Plane | 전체 공통 접지 기준면 | 단일 저임피던스 플레인 (Star Point 분기) |

---

## 3. 신호 도메인 및 버스 계통도

1. **디지털 제어 버스 (I2C)**:
   - 라인: `I2C_SDA (GPIO21)`, `I2C_SCL (GPIO27)`.
   - 풀업: 4.7kΩ 1% to 3.3V (R11, R8).
   - 통신 대상: TAS5805M (주소 `0x2C`).
   - 방어 메커니즘: 25ms Wire 하드 타임아웃 및 하드웨어 리셋 스위치 연계.
2. **디지털 오디오 버스 (I2S)**:
   - 라인: `I2S_BCLK (GPIO26)`, `I2S_LRCLK (GPIO25)`, `I2S_DOUT (GPIO22)`.
   - 사양: 48kHz 샘플링 레이트, 32-bit BTL 정현파 PCM 오디오 스트림.
   - 시퀀싱: 앰프 PDN 활성화 전 반드시 선행 클록 송출 필수.
3. **고속 모션 센서 버스 (SPI)**:
   - 라인: `SPI_SCLK (GPIO18)`, `SPI_MOSI (GPIO23)`, `SPI_MISO (GPIO19)`, `SPI_CS (GPIO5)`.
   - 전용 대상: LSM6DSOX (독립 버스, 타 제어선 공유 금지).
   - 긴급 차단 인터럽트: `PIN_SAFETY_INT1 (GPIO34, Input-only)` $\rightarrow$ 1.5g 이상 시 0.1ms 내 하드웨어 차단.
4. **하드웨어 제어 라인 (Active Control)**:
   - `BOOST_EN`: GPIO4 (10kΩ 풀다운, 디폴트 OFF).
   - `AMP_PDN`: 미할당 Free GPIO (10kΩ 풀다운, 디폴트 MUTE).
