# MAJN 시제품 PCB #0005 펌웨어 볼륨 검증 및 50% 하드캡 감사 보고서

- **문서 버전**: v1.1 (Post-Audit Implementation)
- **작성 일시**: 2026-10-25 00:50 KST
- **대상**: MAJN 스마트 배시넷 실물 시제품 (PCB #0005)
- **목적**: 하드웨어 리뷰어의 코드 재대조 피드백(볼륨 레지스터 쓰기 실패 무시, 공통 진폭 제한 미강제, 주소 정합성, 볼륨 매핑)에 대한 코드 레벨 조치 및 실물 시험 계획 수립.

---

## 1. 코드 대조 지적 사항 및 조치 완료 내역

| 점검 항목 | 리뷰어 지적 사항 | 수정 전 상태 | **조치 완료 상태 (Commit 반영)** |
|:---|:---|:---|:---|
| **① 볼륨 I²C 쓰기 오류** | `setVolume()`이 3개 레지스터 쓰기 반환값을 무시함. | `writeRegister` 반환값 무시 후 무조건 `return true` | `ok1 && ok2 && ok3` 검사 후 **3개 중 하나라도 실패 시 즉시 `false` 반환 및 에러 로깅**. |
| **② 초기화 볼륨 쓰기** | `begin()`에서 볼륨 레지스터 쓰기 결과를 무시함. | `writeRegister(0x4C, 0x30)` 등 반환값 무시 | 3개 레지스터 중 하나라도 NACK 시 **`begin()` 즉시 `return false`로 앰프 차단**. |
| **③ 최대 진폭 50% 강제** | `setTarget()`이 `0.0f ~ 1.0f`로 풀려 있어 모든 경로에서 50% 제한이 보장 안 됨. | `constrain(amplitudeScale, 0.0f, 1.0f)` | **공통 코어 함수(`setTarget`)에서 `constrain(amplitudeScale, 0.0f, 0.5f)`로 하드캡 강제**. 어떤 경로로도 50% 초과 불가. |
| **④ BLE START 폴백 진폭** | `START` 명령 시 amplitude 미지정 시 0.6(60%)으로 진입 위험. | `doc["amplitude"] \| 0.6f` | **기본 폴백 값을 `0.4f` (40%, 안전 규격 이내)로 하향 조정**. |
| **⑤ BLE SET_VOLUME 명령** | `SET_VOLUME` 명령 수신 시 I2C 성공 여부 미검증. | `v > 100` 검사 후 성공 여부 무관 `applied` | `MajnAmplifier::setVolume()` 반환값 검사 후 성공 시 `applied`, 실패 시 `failed` 응답. |
| **⑥ 0x2C 주소 정합성** | 보고서의 0x2C 주소와 PCB 주소 설정 저항의 일치 여부 확인. | 이전 문서에 0x2D로 혼용 기록됨 | **TI TAS5805M Datasheet Table 7-1 재검증**: R12 = 4.7kΩ 풀업 시 기본 주소는 **`0x2C` (0101100b)**가 100% 맞음. 실물 프로빙도 `0x2C` 응답 확정. |

---

## 2. 볼륨 수치 매핑(Digital Attenuation Mapping)의 정확한 정의

- **TAS5805M Master Volume (`0x4C`) 스펙**:
  - `0x00`: $+24\text{ dB}$ (최대 하드웨어 증폭)
  - `0x30`: $0\text{ dB}$ (Unity Gain, 기준 최대 허용 볼륨)
  - `0x31` ~ `0xFE`: $-0.5\text{ dB} \sim -103\text{ dB}$ (0.5dB 감쇄 스텝)
  - `0xFF`: Complete Mute (출력 차단)
- **펌웨어 구현 매핑 수식**:
  - $0\%$: `0xFF` (완전 음소거)
  - $1\% \sim 100\%$: $\text{Reg} = 0x30 + \left\lfloor \frac{(100 - \text{Percent}) \times 206}{100} \right\rfloor$
  - 안전 클램핑: $\text{Reg} < 0x30$일 경우 강제로 $0x30$($0\text{ dB}$)으로 고정하여 **영아 청각 손상 및 앰프 과열(+dB)을 100% 원천 차단**.

> [!CAUTION] **이론적 감쇄치와 실물 계측값 분리 주의**
> 데이터시트 기준 이론 감쇄치(예: Reg 0xC2 = -73 dB, Reg 0x6D = -30.5 dB)는 디지털 레지스터의 산술적 코드 감쇄량일 뿐입니다. 실제 익사이터 코일 임피던스, 배시넷 프레임 공진, 매트리스 폼의 기계적 감쇄로 인해 **패드 상면 진동 가속도(G-force)는 비선형적**으로 나타납니다. 따라서 이 수치는 시험 전 이론 참고치일 뿐이며, 물리적 실측 전에는 제품 사양이나 시험 결과로 취급하지 않습니다.

---

## 3. Commit `37831af` 소스 코드 정밀 검증 결과

- **원격 저장소 동기화**: `git log` 확인 결과 `37831af`가 `origin/main`에 완전 반영됨.
- **PlatformIO 빌드 검증**: `esp32_full_hw` 타깃 0-error, 0-warning 컴파일 성공 (Flash: 1,804,863B / 54.0%, RAM: 69,264B / 21.1%).
- **진폭 50% 하드캡 우회 경로 전수 조사**:
  - `git grep -n "gTargetAmplitude\|gCurrentAmplitude\|setTarget"` 전수 조사 완료.
  - 모든 명령 수신 계층(BLE `START`, `SET_PRESET`, `SET_FREQ`, `SET_AMP`)이 `MajnVibration::setTarget()`을 경유.
  - `setTarget()` 내에서 `gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);`로 강제 고정.
  - 램프 루프(`RAMP_STEP_20MS`) 역시 `gCurrentAmplitude`가 `gTargetAmplitude`를 초과할 수 없도록 이중 방어.
  - 결론: **어떠한 입력 경로로도 진폭 50%를 초과할 수 없음이 코드 레벨에서 증명됨**.

---

## 4. 실물 시험 절차 (Safe Bring-up Procedure)

1. [x] **볼륨 레지스터 3개 쓰기 실패 감지 구현** (완료)
2. [x] **공통 제어 함수(`setTarget`)에서 최대 진폭 50% 하드캡 강제** (완료)
3. [x] **초기화 시 필수 레지스터 쓰기 실패 감지 및 차단** (완료)
4. [ ] **실제 보드 4단계 볼륨 시험 및 패드 상면 진동 측정 (실물 시험 준비)**:
   - **Step 1 (연결 확인)**: 보드에 USB-C 전원 인가 후 BLE 연결(`MAJN-Bassinet`) 및 펌웨어 버전 확인.
   - **Step 2 (0% 볼륨 음소거 시험)**: `SET_VOLUME(0)` 송신 $\rightarrow$ 레지스터 `0xFF` 진입, 차동 전압 0.0V 및 완전 무음/무진동 검증.
   - **Step 3 (단계별 안전 증강 시험)**: 30% $\rightarrow$ 70% $\rightarrow$ 100% 순차 입력, 각 단계별 레지스터 응답 및 익사이터 발열/이상 진동 여부 관측.
   - **Step 4 (물리적 진동 가속도 계측)**:
     - J1/J2 차동 신호에 일반 오실로스코프 접지 클립 직접 연결 금지 (BTL 쇼트 방지).
     - 매트리스 패드 상면에 가속도 센서를 거치하여 볼륨/진폭별 실제 G-value를 실측하고 기록.
