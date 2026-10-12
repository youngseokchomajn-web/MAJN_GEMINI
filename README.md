# 마중 스마트 요람/배시넷 PCB (MAJN Smart Cradle)

USB-C 5V → MP3426 부스트 → TAS5805M Class-D 앰프 → 진동 트랜스듀서 구성의 스마트 배시넷 PCB 프로젝트.
SSOT의 현재 부품 구성과 EasyEDA 클라우드 PCB가 일치하는지는 실제 설계 내보내기 및 비교로 확인해야 합니다. **4층 PCB 설계 기록.**

---

## 📁 이 GitHub repo = 설계 소스 + 문서

| 파일 | 내용 |
|---|---|
| `인증준비/mcp_development/mcp_design_flow.json` | **SSOT** — 전체 넷리스트·부품(56개), v1.9.2 (파일의 실제 version 필드 기준) |
| `인증준비/mcp_development/run_draw_schematic.py` | SSOT에서 **회로도 자동 재생성** (EasyEDA 브릿지) |
| `인증준비/mcp_development/a1_symbol_verify.json` | 검증된 라이브 심볼 핀맵(222핀) |
| `인증준비/mcp_development/MAJN_*.md` | 설계기록·fresh-eye 리뷰·ECO 절차 문서 |

## 🔬 연구 증거·의료협업 문서

마중의 효과·안전성 근거 구축을 위한 문헌 검토, 연구 설계, 측정 절차 및 연구자 전달 자료는 [연구 문서 색인](docs/MAJUNG_INDEX.md)에서 확인합니다.

**연구 상태 주의:** 문헌·계획 문서와 실제 시험 결과는 구분합니다. 현재 색인에 기록된 실행 패키지는 측정 템플릿이며, 그 자체가 MAJUNG의 실제 진동 출력 측정이나 임상 효능·안전성 입증을 의미하지 않습니다.

## 🌐 회로도 + PCB 실물 = EasyEDA Pro 클라우드

회로도·PCB **전체(배치+배선)**는 EasyEDA Pro 클라우드(**newdongoh** 계정)에 저장돼 있습니다:
- 프로젝트: **`new start`** → Board1 → **Schematic1** + **PCB1**
- 명명 백업: **`github_v190_2026-06-25`** (File → Projects Backup → Backup Management 에서 복원/다운로드)

### 다른 컴퓨터에서 다운/편집하는 법
1. **[EasyEDA Pro](https://pro.easyeda.com) 설치 + `newdongoh` 계정 로그인** → `new start` 프로젝트 열기 (전체 배선·배치 그대로)
2. 회로도만 필요하면 → 이 repo의 `run_draw_schematic.py`로 `mcp_design_flow.json`에서 재생성
3. (선택) Backup Management에서 `.epro2`로 내보내 다른 EasyEDA에 import

> PCB 배선/배치는 EasyEDA 클라우드에만 있고 git으로 재생성 불가 → **클라우드 프로젝트가 PCB의 정본(master)**.

## ⚠️ 설계 상태 해석 주의

SSOT 파일의 실제 버전 필드는 **v1.9.2**입니다. 아래 설계 상세 및 DRC 수치는 이전 설계 기록에서 가져온 상태 설명이며, 현재 SSOT와 EasyEDA 클라우드 PCB의 동기화 여부를 이번 점검에서 재검증하지 않았습니다. 따라서 이를 현재 발주 가능 판정이나 최신 DRC 결과로 해석하면 안 됩니다.

발주 전에는 다음을 다시 확인해야 합니다.
1. EasyEDA Pro에서 최신 Schematic1/PCB1을 내보내 SSOT와 부품·넷·풋프린트·배치·배선 차이를 비교
2. 최신 DRC/제조성 검토 및 실제 short/open 검증
3. 전원부·인덕터·발열·음향 출력 제한 등 제품 위험 항목 검토
4. 현재 펌웨어 및 PCB 리비전이 시험 대상 장치와 일치하는지 기록

과거 설계 메모는 하단의 설계 기록 문서를 참고하되, 최신 상태는 위 검증 후 갱신합니다.

## 📖 상세 문서
- `MAJN_FreshEye_재검증_2026-06-24.md` — fresh-eye 리뷰 + false positive 재검증
- `MAJN_PCB_완성기록_2026-06-24.md` — 배치/배선/전원폭 기록
- `MAJN_PCB_ECO_TODO_2026-06-24.md` — ECO 절차
