# MAJN ESP32 ↔ GUI BLE Protocol v1

## 1. 목표

Mac Chrome 기반 MAJN GUI가 ESP32-WROOM-32UE와 BLE GATT로 연결되어 실제 상태/IMU를 읽고 안전하게 제어한다.

초기 구현은 JSON 텍스트를 사용한다. 통신량이 증가하면 v2에서 binary telemetry를 검토한다.

## 2. GATT

- Service UUID: `7b4d0001-7a6a-4d41-9a4d-4d414a4a4e01`
- Command Write Characteristic: `7b4d0002-7a6a-4d41-9a4d-4d414a4a4e01`
- Telemetry Notify Characteristic: `7b4d0003-7a6a-4d41-9a4d-4d414a4a4e01`
- Event Notify Characteristic: `7b4d0004-7a6a-4d41-9a4d-4d414a4a4e01`

## 3. Command

GUI → ESP32:

```json
{"id":12,"cmd":"PING"}
{"id":13,"cmd":"STATUS"}
{"id":14,"cmd":"START","frequency_hz":45,"amplitude":0.2}
{"id":15,"cmd":"STOP"}
{"id":16,"cmd":"ESTOP"}
{"id":17,"cmd":"SET_VIBRATION","frequency_hz":45,"amplitude":0.5}
{"id":18,"cmd":"SET_FREQUENCY","frequency_hz":50}
{"id":19,"cmd":"SET_AMPLITUDE","amplitude":0.3}
{"id":20,"cmd":"SET_VOLUME","volume":72}
{"id":21,"cmd":"SET_PRESET","preset":"pink"}
```

### ACK

ESP32 → GUI:

```json
{"type":"ack","id":17,"cmd":"SET_VIBRATION","status":"applied","state":"READY"}
```

가능한 status:

- `received`
- `validated`
- `applied`
- `rejected`
- `fault`

## 4. Telemetry

Notify 5 Hz:

```json
{
  "type":"telemetry",
  "uptime_ms":123456,
  "state":"READY",
  "safety_lock":false,
  "frequency_hz":45.0,
  "amplitude_scale":0.50,
  "accel_g":{"x":0.01,"y":-0.02,"z":1.00},
  "pvdd_v":null,
  "vdd_3v3_v":null,
  "amp_temp_c":null
}
```

`null`은 현재 하드웨어/펌웨어에서 해당 값을 실제 측정하지 않는다는 뜻이다. GUI에서 임의값을 표시하지 않는다.

## 5. State machine

```
BOOT
  ↓
SELF_TEST
  ↓
READY
  ├─ START → RUNNING
  ├─ STOP  → READY
  └─ ESTOP → FAULT

RUNNING
  ├─ STOP → READY
  ├─ ESTOP → FAULT
  ├─ BLE timeout → SAFE_STOP → READY
  ├─ sensor/amp fault → FAULT
  └─ runtime limit → SAFE_STOP → READY

FAULT
  └─ local recovery/reset only
```

BLE 명령은 로컬 안전 규칙보다 우선하지 않는다.

## 6. Safety rules

1. 부팅 직후 AMP_PDN=LOW, BOOST_EN=LOW.
2. BOOST_EN을 켠 뒤 PVDD 안정 대기 후 AMP_PDN을 HIGH로 전환한다.
3. START 전에 센서/앰프 초기화가 성공해야 한다.
4. ESTOP은 즉시 PDN LOW + BOOST LOW.
5. BLE 연결이 끊기거나 heartbeat가 timeout되면 실행 중 진동을 안전 정지한다.
6. 총 출력 상한은 FW에서 강제한다.
7. GUI가 보낸 frequency/amplitude/volume은 FW 범위검증 후 적용한다.

## 7. Versioning

- protocol: `1`
- firmware는 telemetry의 `protocol`과 `firmware` 필드를 제공한다.
- GUI는 연결 직후 PING/STATUS로 호환성을 확인한다.

## 8. Current hardware telemetry matrix

| 항목 | 실제 source | 현재 상태 |
|---|---|---|
| Acc X/Y/Z | LSM6DSOX SPI | 실제 측정 |
| PVDD | ADC/전압센서 미정 | 미측정 |
| VDD 3.3V | ADC/전압센서 미정 | 미측정 |
| TAS5805M temperature | 별도 센서/레지스터 구현 필요 | 미측정 |
| TAS5805M fault | I2C status register 구현 필요 | 미구현 |
| BOOST_EN | GPIO4 | 실제 상태 추적 |
| AMP_PDN | GPIO15 | 실제 상태 추적 |
| frequency | FW target | 실제 명령값 |
| amplitude | FW scale | 실제 명령값 |

GUI는 '미측정' 값을 simulation 값으로 섞지 않는다.
