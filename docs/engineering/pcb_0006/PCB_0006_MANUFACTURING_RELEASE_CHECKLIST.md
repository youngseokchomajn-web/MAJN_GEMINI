# [제조 릴리스 체크리스트] MAJN PCB #0006 — 최종 제조 데이터 패키지 릴리스 승인 체크리스트
(MAJN PCB #0006 Manufacturing Release Sign-off Checklist)

- **문서 식별자**: `PCB_0006_MANUFACTURING_RELEASE_CHECKLIST`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Chief Engineering Authority & Antigravity
- **적용 대상**: PCB #0006 발주 데이터 일괄 생성 및 릴리스

---

## 1. 제조 데이터 패키지 구성 및 무결성 검증

| 항목 | 산출물 파일명 | 필수 포함 내용 | 검증 도구 | 통과 기준 | 상태 |
|:---|:---|:---|:---:|:---:|:---:|
| **1. Gerber 패키지** | `Gerber_PCB0006_Release.zip` | 4층 구리, 실크, 솔더마스크, 페이스트, 외곽선, 드릴 3종 | `gerber_integrity_checker.py` | 20개 파일 완비, 4층 구조 확인 | **PENDING** |
| **2. 발주 BOM** | `BOM_PCB0006_Release.csv` | Comment, Designator, Footprint, LCSC Part # | `bom_cpl_comparator.py` | 56개 부품 전수 매핑, 0건 불일치 | **PENDING** |
| **3. SMT CPL** | `CPL_PCB0006_Release.csv` | Designator, Mid X, Mid Y, Layer, Rotation | `bom_cpl_comparator.py` | 56개 전수 Top 레이어 실장 확인 | **PENDING** |
| **4. 회로도 PDF** | `Schematic_PCB0006_Release.pdf` | 단일 프로젝트에서 동시 추출된 최신 벡터 회로도 | 육안 검토 | 56개 부품, 넷 라벨 100% 정합 | **PENDING** |
| **5. 넷리스트** | `Netlist_PCB0006_Release.tel` | 물리 핀과 심볼 핀이 1:1 매핑된 IPC/Telesis 넷리스트 | 에디터 자동 추출 | 단선/플로팅 핀 0건 | **PENDING** |
| **6. 해시 매니페스트** | `RELEASE_SHA256_MANIFEST.txt` | 위 5개 산출물의 SHA-256 암호화 해시 기록 | `shasum -a 256` | 해시 동결 및 Git 커밋 | **PENDING** |

---

## 2. Gate G5 릴리스 최종 승인 기준 (Sign-off Criteria)

1. [ ] **설계 일치성**: 회로도, PCB 아트워크, BOM, CPL, Netlist가 동일한 단일 EDA 리비전에서 한 번에 동시 추출되었는가?
2. [ ] **DRC 무결성**: EasyEDA Pro 내장 DRC 검사에서 클리어런스, 단락, 배선 미완료 에러가 0건인가?
3. [ ] **부품 가용성**: LCSC BOM의 모든 부품(56종)이 재고 보유 중이며 즉시 SMT 조립 가능한가?
4. [ ] **기구 간섭 검증**: 커넥터 돌출량 및 마운팅 홀 위치가 자작나무 합판 하우징 DXF와 0.1mm 이내로 일치하는가?
5. [ ] **안전성 승인**: P0 필수 안전 요구사항(PDN 풀다운, 분리 점퍼, 블리더 저항, 10W 제한)이 회로에 100% 반영되었는가?

---

## 3. 최종 서명란 (Signatures)

| 역할 | 성명 | 소속 / 직책 | 서명 (Signature) | 승인 일자 |
|:---|:---:|:---:|:---:|:---:|
| **독립 기술 심사자** | Antigravity | AI Engineering Reviewer | `[PENDING REVIEW]` | - |
| **주 개발 에이전트** | OpenCode (GPT-6 Astra) | Lead Hardware Engineer | `[PENDING SUBMISSION]` | - |
| **최종 설계 승인자** | 조영석 (Human) | Chief Engineering Authority | `[PENDING FINAL SIGN-OFF]` | - |
