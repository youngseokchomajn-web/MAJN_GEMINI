# MAJN 기구·전장·케이블·PCB·펌웨어 통합 및 인터페이스 개발계획

- 문서 ID: MAJN-ENG-INT-001
- 상태: Draft — interface facts require source verification
- 핵심 목적: 기구 CAD부터 케이블 하네스, PCB, RF, 펌웨어, 시험까지 물리·전기 인터페이스를 한 구성으로 관리한다.

## 1. 통합 아키텍처

설계의 기준은 단일한 3D 이미지가 아니라 다음의 연결된 데이터다.

1. 제품 구성 CFG와 요구사항 REQ
2. 시스템 아키텍처 SYS와 인터페이스 IF
3. 기구 부품 PART/ASM 및 CAD/drawing revision
4. PCB ID/revision, schematic, BOM, Gerber/CPL
5. Cable/Harness ID, wire list, connector pinout, routing
6. Firmware ID/commit/binary hash/board compatibility
7. CAE/TEST/EVID/RISK 결과

각 연결에는 source revision, configuration, 상태, 증거가 필요하다.

## 2. 인터페이스 분류와 계약 항목

| 인터페이스 | 기계 항목 | 전기/신호 항목 | 필수 검증 |
|---|---|---|---|
| USB-C/전원 인입 | 포트 위치, 그로밋, 케이블 외경, 고정, 당김 방지 | 전압/전류/극성/보호소자/전압강하 | worst-case load, pull/strain, 온도 |
| PCB-하우징 | board outline, mounting holes, standoff, keepout | GND/EMI/접지 경로 및 절연거리 | 좌표 중첩, 공차, 실물 체결 |
| 앰프-익사이터 | 커넥터 위치, 케이블 길이, 진동/마찰 방지 | BTL +/- pin, load, gauge, insulation | polarity/continuity, differential waveform, load/thermal |
| ESP32-RF 안테나 | 안테나 방향, 위치, 접착, coax routing, keepout | connector type, cable loss, gain, RF band | RSSI/throughput/reconnect 및 규제 검토 |
| 센서-구조물 | 측정 위치, 부착 강성, 방향, 케이블 strain relief | interface voltage, bus, sample rate | calibration, axis orientation, noise |
| 펌웨어-앰프 | connector/pin mapping | I2C address, I2S clock/data, PDN, BOOST_EN | init/fault/recovery/HIL |
| 기구-가스켓 | compression, mating surfaces, tolerance | N/A | compression/ingress test if claimed |
| 기구-매트리스 | support/contact geometry, load distribution | vibration transmission | load-dependent top-surface measurement |

## 3. Cable Routing & Electrical Integration 상세

### 3.1 케이블 데이터 모델

각 케이블은 다음 필드를 가져야 한다.
- cable_id / revision / configuration_id
- from_component / from_connector / from_pin
- to_component / to_connector / to_pin
- signal_class: POWER, BTL_AUDIO, DIGITAL, SENSOR, RF, GROUND, OTHER
- conductor_count / wire_gauge / conductor_material
- insulation_material / voltage_rating / temperature_rating
- nominal_length / length_tolerance / measurement_datums
- minimum_bend_radius / service_loop / slack_policy
- connector_mpn / terminal_mpn / housing_mpn / keying
- polarity / shield / drain / twist / pair mapping
- route_waypoints / clips / grommets / strain_relief / protection
- assembly_sequence / label / inspection / continuity_test
- source_drawing / BOM_ref / reviewer / approval

미확인 필드는 TBD로 남긴다. 도체 규격이나 최소 굽힘 반경을 추정으로 채우지 않는다.

### 3.2 하네스 설계 단계

**H0 — 실물 식별**
- PCB/익사이터/안테나/전원 커넥터의 실제 제조사 part number와 mating part를 확인한다.
- 커넥터 핀 번호가 mating face인지 wire-entry face인지 도면에 명시한다.
- #0005와 차기 PCB의 커넥터 위치/방향 차이를 기록한다.

**H1 — 전기적 정의**
- wire list와 pin-to-pin mapping을 작성한다.
- BTL 출력은 차동 쌍으로 정의하고 두 선을 별도 출력으로 표시한다.
- 전원/신호/RF를 구분하고 공통 경로, 교차, 근접 구간을 표시한다.
- 전류·전압강하·발열 계산 입력과 worst-case 조건을 기록한다.

**H2 — 기구 라우팅**
- 실제 CAD 좌표계에 cable centerline 및 waypoint를 정의한다.
- 모서리, 나사 보스, moving parts, 진동판, 가스켓, PCB component keepout, 안테나를 검사한다.
- 케이블이 목재와 접촉할 경우 abrasion protection 및 고정 방법을 정의한다.
- 서비스 루프와 커넥터 탈착 공간을 남긴다.
- 최소 굽힘 반경은 케이블 제조사 데이터 또는 검증된 공급사 자료에서 가져온다.

**H3 — 3D/도면 산출**
- harness assembly 3D representation
- cable routing drawing
- wire list / connector pinout table
- harness BOM
- clip/grommet/strain-relief part list
- assembly and inspection instructions

**H4 — 실물 검증**
- continuity, short-to-adjacent, polarity, connector retention
- assembly fit and tool access
- static pull/strain relief
- vibration-induced rubbing/noise/fatigue screening
- temperature/voltage-drop under representative load
- RF performance comparison before/after final routing

시험 조건과 합격 기준은 장비/부품 사양/위험분석 근거를 바탕으로 사람이 승인한다.

## 4. 3D CAD와 Viewer 연결

- CAD native file 또는 승인된 parameter source가 설계 기준이다.
- DXF는 제조 2D 산출물, STEP은 솔리드 교환/CAE 입력, GLB는 시각화 파생물로 구분한다.
- 변환 시 unit, origin, axis, handedness, scale, rotation, material, source revision을 기록한다.
- Viewer node에는 `part_id`, `assembly_id`, `source_revision`, `configuration_id`를 연결한다.
- known-point test: CAD에서 알고 있는 기준점 3개 이상이 viewer에서 허용오차 내 일치하는지 자동 검사한다.
- viewer의 색상/애니메이션/투명도는 제조/치수 정확성 증거가 아니다.

## 5. PCB 장착 인터페이스 검토

PCB 마운팅 홀 추가를 즉시 실행하지 않는다. 다음 순서로 검토한다.

1. EasyEDA source의 실제 board outline과 hole center 좌표 추출
2. 실물 PCB 측정 또는 제조 Gerber/Drill로 교차 확인
3. PCB 좌표계를 housing datum에 등록
4. 하판 DXF 좌표계와 transform matrix 확인
5. 스탠드오프/나사/와셔/인서트의 실제 치수 및 높이 확인
6. 부품 하부 keepout, 납땜면, solder mask, 절연 간격 확인
7. 하판 두께/목재 결 방향/가공 공차/모서리 거리 확인
8. 커넥터 삽입/케이블 굽힘/드라이버 접근 확인
9. 3D interference + tolerance stack + physical fit-up
10. ECO, 도면 revision, 승인 후에만 가공

## 6. RF 안테나 통합

- 안테나 모델/제조사/part number/최대 이득/주파수 대역/편파/케이블 길이/커넥터를 식별한다.
- 3dBi와 2.33dBi 이하라는 상충값을 정리하기 전 RF interface를 VERIFIED로 표시하지 않는다.
- 모듈 인증 범위가 안테나 교체/케이블/배치/출력 설정을 포함하는지 시험기관에 질의한다.
- ESP32-WROOM-32UE-N8 같은 외장 안테나 구성은 connector seating, coax damage, antenna orientation, enclosure proximity를 확인한다.
- 실물 RSSI 측정은 위치/거리/방향/채널/송신출력/장비/환경을 함께 기록한다. RSSI 하나만으로 인증/안정성을 판정하지 않는다.

## 7. 전원·BTL·열 통합

- USB-C source, cable, protection, boost, amplifier, actuator load를 하나의 power tree로 관리한다.
- peak/continuous current, inrush, undervoltage, converter efficiency, cable drop, thermal rise를 구분한다.
- BTL output은 differential measurement 방식과 적합한 장비로 측정한다. 일반 접지형 계측기 접지를 출력에 직접 연결하지 않는다.
- 12Ω 샘플의 성공 기록은 8Ω 양산품으로 일반화하지 않는다.
- 실제 부하/파형/진폭/주파수/듀티/환경/케이스 온도를 기록한다.

## 8. 통합 충돌 체크리스트

- [ ] DXF/STEP/GLB 단위 및 좌표계 일치
- [ ] PCB outline/holes/component keepout 정합
- [ ] connector mating 방향과 tool access
- [ ] cable route/길이/굽힘/서비스 루프
- [ ] 진동 중 케이블 마찰/버징/피로
- [ ] BTL polarity와 차동쌍
- [ ] 전원 peak current와 voltage drop
- [ ] RF antenna keepout/route/gain/compliance
- [ ] thermal path와 주변 소재
- [ ] assembly order 및 service access
- [ ] sensor placement/calibration
- [ ] configuration ID와 firmware compatibility

## 9. 통합 릴리즈 패키지

통합 설계 후보마다 아래를 묶는다.
- approved CAD/drawing/STEP/GLB derivatives
- PCB source + BOM + CPL + Gerber + drill + verification report
- cable drawing + wire list + harness BOM
- ICD and interface status
- firmware source commit + binary hash + compatibility manifest
- CAE model/input/solver settings/result
- assembly review + fit-up report
- risk review + verification plan
- ECO approvals and unresolved items

하나라도 미승인 critical interface가 있으면 manufacturing release를 차단한다.
