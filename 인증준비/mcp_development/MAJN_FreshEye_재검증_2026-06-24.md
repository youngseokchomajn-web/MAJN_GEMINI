# 마중 PCB — Fresh-eye 전수점검 + 재검증 (2026-06-24)

회로도(넷리스트 43)·BOM(53)을 4개 기능블록 병렬 독립검토 → **권위 데이터시트로 재검증**.
**핵심 교훈: AI 병렬검토도 틀린 데이터시트를 보면 false positive를 낸다. 라이브 검증부품 심볼 + 공식 데이터시트 교차확인이 필수.**

## 재검증 결과

| 발견 | 1차 주장 | 권위 재검증 | 판정 |
|---|---|---|---|
| U5 IMU VDD/GND 스왑 | pin8=GND(치명) | **ST 공식DS: pin8=VDD, 9=INT2, 10=OCS_Aux, 11=SDO_Aux** | ❌ **false positive** (구형 LSM6 핀아웃 오인). pin8→VCC 정상 |
| U3 MP3426 핀 역순 | 8~14 역순 | **alldatasheet 실표: 8~10=PGND,12=SS,13=FB,14=FSET** | ❌ **false positive**. 라이브 심볼 일치 |
| **U4 ADR=GND** | 저항 필요 | **TI Table7-5: ADR은 DVDD 풀업저항(4.7k/15k/47k/120k)만, GND직결 미문서=주소미정.** 프로젝트 pinmap도 동일 지적 | ✅ **진짜(CRITICAL)** |

## 확정 수정 — U4 ADR (실행됨: SSOT)
- **현상**: U4/3(ADR/FAULT)이 GND 직결 → I2C 주소 미정 → FW(0x2C 기대) ACK 실패 위험 = 앰프 초기화 불가.
- **수정(design_flow v1.9)**: **R12=4.7k(C23162) 추가**, U4/3을 GND에서 분리, **AMP_ADR 넷**(U4/3↔R12/1) 신설, R12/2→VCC_3V3(DVDD). → 7-bit 0x2C / 8-bit write 0x58.
- **PCB 반영 잔여**: 브릿지로 부품추가 불가 → UI ECO 필요(R12 배치 + U4/3↔R12, R12↔VCC_3V3 배선, U4/3의 기존 GND배선 제거).

## 나머지 발견 — 정직한 재평가 (대부분 경미/과장)
- **GPIO15(AMP_PDN)·GPIO5(SPI_CS) 스트래핑 pull** (진짜·경미): 강건성 위해 10k pull 권장. 내부 pull로 대개 동작하므로 필수 아님. PDN은 pull-down(앰프 fail-safe), CS는 pull-up.
- **PVDD 벌크** (과장): C6/C7(22µF×2=44µF)이 PVDD레일에 이미 있음. 로컬 디커플링만 점검.
- **부트스트랩 C12~15 100nF vs TI 0.22µF** (중간): 데이터시트 값 재확인 권장.
- **D1 SMAJ5.0A** (경미): 5.0V standoff가 5V레일엔 빠듯 → SMAJ5.5/6.0 고려.
- **USB-C 5A** (조건부): 덤프 5V/5A 어댑터면 OK / USB-PD 협상이면 ≤3A. 소스방식 확정 필요.
- **CC선 ESD·출력 68Ω 스너버** (선택): KC ESD/EMC 마진.

## ✅ 검증 완료(정상): 부스트 토폴로지·D3방향·전압정격·I2S매핑(6/7/8)·SPI 4선·IMU 전원(pin8=VDD)·CC 5.1k(sink)·EN RC·플래시핀/GPIO12 미사용·출력필터 순서·MP3426 핀 등 다수.
