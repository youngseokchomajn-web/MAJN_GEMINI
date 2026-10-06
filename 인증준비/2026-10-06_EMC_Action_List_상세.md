# EMC Action List 2026-10-06

## P0
- MP3426 BOOST_SW loop: 총 약 20.4 mm.
- U3 약 (60,30) mm, L1 약 (60,38) mm, D3 약 (66,30) mm.
- U3와 L1 사이가 약 8 mm 떨어져 있어 switching loop 축소를 강하게 권장.
- L1/D3/U3를 가능한 한 조밀하게 배치하고 SW copper 면적을 최소화.
- PCB geometry와 BOM/netlist의 L1/D3 정보가 서로 맞지 않으므로 제조 전 revision 정합성 확인 필수.

## P1
- TAS5805M A+ 약 26.0 mm, A- 약 39.4 mm.
- A채널 출력은 J1 외부 케이블로 연결되므로 경로 대칭화와 layer transition 축소를 권장.
- J1/J2 주변은 향후 common-mode 대책을 추가할 수 있는 공간을 확보.
- PVDD_12V return path와 U4 주변 decoupling/GND via를 상세 확인.

## P2
- B+ 약 14.1 mm, B- 약 16.5 mm로 A채널보다 양호.
- ESP32/IMU와 Boost/Class-D가 물리적으로 분리된 점은 긍정적.
- USB-C와 noisy power/audio 영역도 위치상 분리되어 있음.

## 제작 전 순서
1. 최신 schematic/PCB/BOM/PnP/netlist revision 통일
2. BOOST loop 수정 검토
3. Class-D A채널 경로 수정 검토
4. GND plane/via 확인
5. prototype 제작
6. EMC Pre-test
7. 실패 주파수와 operating mode 확인 후 필요한 계측기만 추가

현재 단계에서는 오실로스코프나 스펙트럼 분석기를 미리 구매할 필요성이 낮다.
