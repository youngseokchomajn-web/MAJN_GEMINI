# 마중 스마트 요람/배시넷 PCB (MAJN Smart Cradle)

USB-C 5V → MP3426 부스트 12.12V (PVDD) → TAS5805M Class-D 앰프 → 2× 8Ω 진동 트랜스듀서(10W RMS/30W Max).
ESP32-WROOM(BLE 제어), LSM6DSOX IMU, AP2112K-3.3 LDO. KC 국내인증(진동 액세서리). **4층 PCB.**

---

## 📁 이 GitHub repo = 설계 소스 + 문서

| 파일 | 내용 |
|---|---|
| `인증준비/mcp_development/mcp_design_flow.json` | **SSOT** — 전체 넷리스트·부품(56개), v1.9.0 |
| `인증준비/mcp_development/run_draw_schematic.py` | SSOT에서 **회로도 자동 재생성** (EasyEDA 브릿지) |
| `인증준비/mcp_development/a1_symbol_verify.json` | 검증된 라이브 심볼 핀맵(222핀) |
| `인증준비/mcp_development/MAJN_*.md` | 설계기록·fresh-eye 리뷰·ECO 절차 문서 |

## 🌐 회로도 + PCB 실물 = EasyEDA Pro 클라우드

회로도·PCB **전체(배치+배선)**는 EasyEDA Pro 클라우드(**newdongoh** 계정)에 저장돼 있습니다:
- 프로젝트: **`new start`** → Board1 → **Schematic1** + **PCB1**
- 명명 백업: **`github_v190_2026-06-25`** (File → Projects Backup → Backup Management 에서 복원/다운로드)

### 다른 컴퓨터에서 다운/편집하는 법
1. **[EasyEDA Pro](https://pro.easyeda.com) 설치 + `newdongoh` 계정 로그인** → `new start` 프로젝트 열기 (전체 배선·배치 그대로)
2. 회로도만 필요하면 → 이 repo의 `run_draw_schematic.py`로 `mcp_design_flow.json`에서 재생성
3. (선택) Backup Management에서 `.epro2`로 내보내 다른 EasyEDA에 import

> PCB 배선/배치는 EasyEDA 클라우드에만 있고 git으로 재생성 불가 → **클라우드 프로젝트가 PCB의 정본(master)**.

## ✅ 설계 상태 (v1.9.0)
- **앰프 ADR 핵심버그 수정 완료**: U4/3을 GND직결 → **R12 4.7k→DVDD** (I2C 주소 0x2C). 안 고치면 앰프 I2C 죽음.
- **회로도 ↔ PCB 넷리스트 완전 일관** (정공법 ECO: 회로도 재생성 → Update PCB)
- **EP 12 써멀비아 GND화 + re-pour** (rebuildCopperRegion) — Class-D 접지·방열
- **R12(ADR)/R13(GPIO15 풀업)/R14(GPIO5 풀업) 배치+배선**
- 전원폭 유지: VBUS/PVDD/BOOST_SW Top pour + 2oz 외층(발주지정)

### 권위 DRC ≈ 63건 — 정체
- **~52건**: U4 EP 써멀비아 영역의 조밀한 GND-GND 간격 → **써멀비아 표준, 제조정상**(일반 간격룰이 플래그)
- **6건 connection**: 구리는 실제로 연결됨(검증), EasyEDA가 브릿지생성 동박을 인식 못한 아티팩트 → Gerber상 연결됨
- **진짜 short/open 결함 0**

## ⚠️ 발주 전 잔여 (선택/권장)
1. EP 써멀비아 간격룰 = DFM 예외 수용
2. 6건 connection = 신뢰성 위해 EasyEDA 인터랙티브 라우터로 재연결(선택)
3. 강건성(유아 제품): 부스트 인덕터 8A 교체·입력 퓨즈(PPTC)·LDO 발열 실측
4. 펌웨어: 최대 SPL 하드리밋, ADR PVDD후 100ms 유지, 스프레드스펙트럼

## 📖 상세 문서
- `MAJN_FreshEye_재검증_2026-06-24.md` — fresh-eye 리뷰 + false positive 재검증
- `MAJN_PCB_완성기록_2026-06-24.md` — 배치/배선/전원폭 기록
- `MAJN_PCB_ECO_TODO_2026-06-24.md` — ECO 절차
