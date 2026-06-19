# MP3426(U3) 부스트 보상망 — 데이터시트 확정 설계 ✅

**출처:** MP3426 데이터시트 Rev.1.11 (MPS 공식, 브라우저로 취득·pdf.js 추출).
**상태:** 값 전부 데이터시트로 **확정**. 남은 작업 = 부품 5개 캐싱 + 스펙 반영 + S4 재실행.
**부하:** TT25 미세진동(경부하) → 안정성 여유 큼. 그래도 제작 전 벤치 검증 권장.

---

## 데이터시트 확정값 (5V→12V, COUT≥22µF)
MP3426 Table 2(Recommended Component Values) 중 **우리 설계와 동일 행**:
`VIN=5, VOUT=12, COUT=22µF → R_COMP=25kΩ, C_COMP=4.9nF, fSW=600kHz, L=6.8µH`

| 항목 | 핀 | 확정값 | 근거 |
|---|---|---|---|
| **FB 분압** | FB(13) | R1=150k / R2=16k → **12.71V** | Vref=**1.225V**, Vout=1.225×(1+R1/R2). 12V 정확히는 R2≈16.9k(→12.10V) |
| **FSET 주파수** | FSET(14) | **R_FSET=84.5kΩ → 540kHz** | EC 특성화값(450/540/630kHz @84.5k). Table 2는 600kHz 기준 |
| **COMP 보상** | COMP(1) | **R_COMP=24.9k + C_COMP=4.7nF 직렬 → AGND** | Table 2(25k/4.9nF). "Connect R+C in series to AGND" |
| (옵션)COMP 2캡 | COMP(1)→GND | 미사용(필요시 100pF) | "second comp cap" 옵션 |
| **VDD 바이패스** | VDD(7) | **1µF → GND** | "LDO Output for internal power supply" |
| **SS 소프트스타트** | SS(12) | **미연결(NC)** | "Leave disconnected if not used"(내부 기본) |
| **EN 풀다운** | EN(2) | **100k → GND**(권장 추가) | "Do not leave EN floating". 부팅 시 boost OFF 페일세이프 |

**인덕터:** 데이터시트 권장 6.8µH, 현재 L1=4.7µH. 경부하라 4.7µH도 동작(리플 ↑ 약간). 정합성 위해 6.8µH 교체 고려 가능.
**출력캡:** 현재 2×22µF=44µF(≥22µF 권장 충족 ✓).

## 추가할 부품 (5개) — 캐싱 필요
| 지정 | 값 | 연결 | LCSC(확인필요) |
|---|---|---|---|
| C21 | 1µF 0603 | VDD(7)→GND | C15849(1µF/25V) |
| C22 | 4.7nF 0603 | COMP경유→GND | (4.7nF 50V) |
| R9 | 84.5k 0603 1% | FSET(14)→GND | (84.5k) |
| R10 | 24.9k 0603 1% | COMP(1)→C22 | (24.9k) |
| R11 | 100k 0603 | EN(2)→GND | (100k, 또는 캐시된 150k C22817) |

> ⚠️ 새 LCSC ID는 run_draw_schematic 전 EasyEDA 라이브러리에 캐싱돼야 배치됨.

## 넷 추가 (스펙 반영)
- `BOOST_VDD`: U3.7, C21.1 / C21.2→GND
- `BOOST_FSET`: U3.14, R9.1 / R9.2→GND
- `BOOST_COMP`: U3.1, R10.1 / R10.2↔C22.1(`COMP_RC`) / C22.2→GND
- `BOOST_EN`: + R11.1 / R11.2→GND (기존 U1.GPIO4, U3.2 유지)
- SS(U3.12): 미연결

## 남은 절차
1. 위 부품 LCSC ID 확정 + EasyEDA 캐싱.
2. `mcp_design_flow.json`에 부품 5개 + 네트 반영.
3. `python run_draw_schematic.py` 재실행 → 회로도 갱신 → ERC.
4. S5(PCB)·S7(검증)로 진행.
5. **제작 전 벤치: 부스트 출력전압·기동·load step 안정성 측정**(데이터시트 절차: R_COMP를 점진적으로 올려 오버슈트 최소화).
