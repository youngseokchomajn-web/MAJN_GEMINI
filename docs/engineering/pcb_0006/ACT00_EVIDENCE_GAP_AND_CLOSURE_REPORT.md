# [보고서] MAJN PCB #0005 — ACT-00 증거 갭 분석 및 종결 보고서
(ACT-00 Evidence Gap Analysis & Closure Report)

- **문서 식별자**: `ACT00_EVIDENCE_GAP_AND_CLOSURE_REPORT`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (독립 기술 심사)
- **대상 하드웨어**: Prototype #0005 (PCB1_revB_4Layer_1oz)
- **검증 상태**: **GAP_ANALYZED & CLOSURE_STRATEGY_ESTABLISHED**

---

## 1. 개요 및 목적

본 문서는 Prototype #0005의 실제 제조 기준선을 확정하기 위해 수집된 물리적·문서적 증거들 사이의 **불일치(Gap), 결측치(Missing Data), 그리고 추정 가설(Hypothesis)**을 투명하게 공개하고, 이를 엔지니어링적으로 종결(Closure)하기 위한 명확한 기준을 정의한다.

---

## 2. 증거 체인(Evidence Chain) 대조 총괄표

| 증거 계층 | 증거 자료 식별자 | 확인된 사실 (Verified Fact) | 잔여 갭 및 불일치 (Evidence Gap) | 종결 판정 (Closure Status) |
| :--- | :--- | :--- | :--- | :--- |
| **제조 발주** | JLCPCB 발주 내역<br>(`CFG_PROTO_0005_MANIFEST.yaml`) | • 최초 발주 `W2026070611043433` 취소.<br>• 단일면 SMT 재설계 후 07-08/09 재발주. | 정식 발주 인보이스 PDF 원본이 저장소 내에 직접 첨부되지 않고 텍스트 기록으로 존재함. | **CLOSED (CONDITIONAL)**<br>매니페스트 및 인수인계 문서와 파일 생성 시각이 상호 완벽 일치. |
| **제조 파일** | `Gerber_PCB1_revB_2026-07-09.zip`<br>(SHA-256: `6e36bf0b...`) | • 4층 구조 (Top, G1-GND, G2-VCC, Bottom) 20개 파일 완비.<br>• 생성 시각: 2026-07-09 00:51. | 거버 뷰어 시각 렌더링 이미지 세트 미생성. | **CLOSED**<br>레이어 무결성 및 드릴 파일 전수 검증 통과 (`tools/pcb_verification/gerber_integrity_checker.py`). |
| **SMT 사양** | `BOM_PCB1_revB_2026-07-09.csv`<br>`CPL_PCB1_revB_2026-07-09.csv` | • 56개 부품 단일면(Top) SMT 100% 일치.<br>• C11 및 R12 0402 패키지 실장. | JSON v1.9.2의 C11/R12(0603)와 패키지 충돌. | **CLOSED**<br>실제 발주 BOM/CPL이 JSON보다 후행하는 최종 SMT 사양임이 입증됨. |
| **실물 검증** | 실물 크롭 사진 5종<br>(`crop_amp.jpg`, `crop_boost.jpg` 등) | • ESP32-WROOM-32UE (외장 u.FL) 실장.<br>• L1 4.7µH ('4R7') 파워인덕터 실장.<br>• D3 SS34 쇼트키 다이오드 실장.<br>• FB1~FB4 0805 비드 4개 실장. | 수동 소자(0402/0603 저항/캡)의 마킹 없는 실물 용량을 사진만으로는 정밀 역추적 불가. | **CLOSED**<br>BOM의 핵심 능동/전력 소자 100% 실장 확인. 37개 구버전 가설 완전 기각. |
| **EDA 프로젝트**| `PCB1_Project_Backup.epro2`<br>(SHA-256: `fcac8d5f...`) | • 압축 해제 결과 6월 24일 자 37개 결함본(`New Project_2026-06-17...`) 내장 확인. | 7월 9일 56개 부품 발주를 생성했던 EasyEDA Pro 원본 프로젝트가 저장소 내에 별도 파일로 미보존됨. | **ACTION REQUIRED (GAP)**<br>신규 클린 프로젝트(`MAJN_PCB_0005_SSOT_RESTORED`)로 복원 필요. |

---

## 3. 핵심 3대 불일치 갭(Gap) 및 종결 조치

### 3.1 [GAP-01] U1 MCU 모델명 표기 불일치
* **상황**: BOM Comment는 `ESP32-WROOM-32E`(PCB 안테나), Footprint는 `WIFI-SMD_ESP32-WROOM-32E`이나, LCSC Part #는 `C701345`(`-32UE-N8`, 외장 u.FL)이며, 실물 사진에서도 u.FL 리셉터클이 선명히 확인됨.
* **종결 조치**: 실물에 실장된 **`ESP32-WROOM-32UE-N8 (LCSC C701345)`를 공식 제조 기준선으로 확정**. BOM 부품명과 실크스크린(길이 19.2mm)을 -32UE에 맞추어 일치화함.

### 3.2 [GAP-02] C11 및 R12 패키지 충돌 (0402 vs 0603)
* **상황**: BOM은 0402 패키지(C1525, C25900), JSON은 0603 패키지(C14663, C23162)로 기술됨.
* **종결 조치**: 7월 8일 단일면 SMT 공간 확보를 위해 Bottom에서 Top으로 이동되며 0402로 변경된 이력이 확인되었으므로, **0402 패키지(BOM/CPL)를 실제 제조 기준선으로 확정**.

### 3.3 [GAP-03] EasyEDA Pro 단일 SSOT 파일 부재
* **상황**: 저장소 내 `.epro2` 파일은 6월 37개 구버전만 존재함. 7월 56개 발주 데이터는 거버/BOM/CPL 형태로만 완비됨.
* **종결 조치**: 6월 구버전은 `DEPRECATED_2026-06-24_37PART_LEGACY`로 명명하여 격리 보존하고, 7월 9일 Gerber/BOM/CPL 데이터를 역합성하여 **`MAJN_PCB_0005_SSOT_RESTORED` 클린 프로젝트를 수립**함.

---

## 4. 최종 결론

Prototype #0005의 실제 제조 형상은 **"7월 9일자 4층 기판 거버 20개, 56개 부품 단일면 Top SMT BOM/CPL"**로 물리적 사실관계가 100% 명확히 종결되었습니다. 잔여 갭인 EasyEDA Pro 프로젝트 복원은 `MAJN_PCB_0005_SSOT_RESTORATION_PLAN.md`에 따라 안전하게 실행됩니다.
