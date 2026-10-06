# MAJN EMC 실제 PCB 레이아웃 1차 판정 — 2026-10-06

기준: PCB1 revB 2026-07-09 Gerber 및 레포에 저장된 PCB geometry/position 데이터.

## 결론

기존의 회로도/BOM 기반 1차 판정보다 실제 PCB를 확인한 결과, EMC에서 우선 수정 검토해야 할 항목이 명확해졌다.

### HIGH

1. **MP3426 BOOST_SW 경로**
   - BOOST_SW 배선 총 약 20.4 mm
   - U3 주변에서 L1 방향으로 약 7 mm 구간
   - L1 이후 D3 방향으로 약 8.9 mm 구간
   - 전체가 Top layer(L1) 중심으로 구성
   - 스위칭 노드가 예상보다 길다.
   - 우선적인 레이아웃 개선 후보.

2. **TAS5805M Class-D A채널 출력**
   - AMP_OUT_A+ 약 26.0 mm
   - AMP_OUT_A- 약 39.4 mm
   - 두 출력의 경로와 layer transition이 상당히 다르다.
   - 특히 A-는 긴 Bottom/내층 경로를 포함한다.
   - 외부 J1 케이블과 연결되므로 방사/공통모드 노이즈 관점에서 HIGH 우선순위.

3. **외부 액추에이터 케이블**
   - J1/J2가 PCB 우측 가장자리에 위치.
   - Class-D 출력이 외부 케이블로 바로 나가는 구조.
   - 실제 케이블 길이와 배선 방식에 따라 방사/공통모드가 크게 달라질 수 있음.
   - 공식 EMC Pre-test에서 반드시 worst-case 조건으로 확인.

### MEDIUM-HIGH

4. **AMP_OUT_B 채널**
   - B+ 약 14.1 mm
   - B- 약 16.5 mm
   - A채널보다 경로 균형은 양호.
   - 다만 외부 케이블로 나가므로 여전히 주요 EMC source.

5. **PVDD_12V 배선**
   - TAS5805M 주변과 Boost 영역을 연결.
   - 총 약 55.8 mm의 분기 배선.
   - 일부 inner layer 사용.
   - Class-D 전류와 Boost switching noise가 함께 존재하므로 return path 확인 필요.

6. **USB-C VBUS_5V**
   - USB-C에서 Boost 입력까지 비교적 긴 경로가 존재.
   - VBUS 전체 net에는 약 31.8 mm의 긴 Top-layer 구간이 확인됨.
   - USB 외부 케이블을 통한 conducted/common-mode path 가능성 확인 필요.

### LOW-MEDIUM

7. **ESP32 RF 영역**
   - ESP32는 보드 하단 중앙에 위치하고 Boost/AMP는 우측에 위치.
   - 물리적으로 noisy power/audio block과 분리된 구조는 긍정적.
   - 다만 실제 ESP32 antenna keep-out 및 GND 조건은 Gerber 상세 확인이 필요.

8. **LSM6DSOX**
   - 좌측 상단에 배치되어 Boost/Class-D와 물리적으로 분리.
   - EMI source라기보다 noise에 영향을 받는 sensitive block으로 판단.

## 긍정적인 점

- 4-layer PCB.
- GND pour가 4개 copper layer에 존재.
- Boost/Class-D가 보드 우측에 집중되어 MCU/IMU와 어느 정도 분리되어 있음.
- Class-D B채널 출력은 두 선의 길이 차이가 비교적 작음.
- USB-C는 보드 좌측, noisy power/audio 영역은 우측이라 기능 블록 분리가 되어 있음.

## 가장 먼저 수정 검토할 것

### Priority 1 — BOOST_SW

목표:
- U3 SW → L1 → D3 주변의 switching current loop 최소화.
- SW copper/trace 면적 최소화.
- SW 노드가 다른 신호 및 GND return과 불필요하게 병렬로 길게 가지 않도록 확인.
- 가능하면 L1/D3/U3를 더 조밀하게 묶는 방향 검토.

### Priority 2 — AMP_OUT_A

목표:
- A+ / A-의 경로 차이를 줄임.
- 불필요한 layer transition 최소화.
- 두 출력의 return/coupling 환경을 최대한 대칭화.
- J1까지의 경로를 짧고 예측 가능하게 유지.

### Priority 3 — 외부 케이블

목표:
- J1/J2 connector에서 나가는 출력의 common-mode 경로 관리.
- 실제 케이블 길이를 포함한 Pre-test 조건 정의.
- 필요 시 connector 근처 ferrite/common-mode 대책을 적용할 수 있도록 footprint/공간 확보.

## 중요한 판단

현재 결과는 **EMC 인증 실패를 의미하지 않는다.**

다만 회로도만 보고 HIGH로 판단했던 항목 중 실제 PCB에서도 위험도가 높은 것이 확인되었고, 특히:

- BOOST_SW
- Class-D A채널 출력
- 외부 액추에이터 케이블

은 시제품 제작 전에 다시 손볼 가치가 충분하다.

## 다음 단계

1. BOOST_SW 주변 실제 component/pad/trace loop를 상세 검토
2. TAS5805M → J1/J2 출력 경로 상세 검토
3. GND plane 및 via stitching 확인
4. ESP32 antenna keep-out 확인
5. USB-C 주변 보호/return 경로 확인
6. 수정 필요 항목만 EMC Action List로 확정
7. 그 후 PCB 수정 여부 결정
8. 시제품 → EMC Pre-test

## 데이터 기준

- PCB1 revB 2026-07-09 Gerber
- pcb31_positions.json
- geo_dump.json
- probe_pcb5_assess_out.json
- 기존 EMC 1차 위험도 판정 문서

