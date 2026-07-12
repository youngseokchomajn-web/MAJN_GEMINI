# CLAUDE.md — 프로젝트 작업 규칙

## ⚠️ 병렬 트랙 세션
이 repo는 세션을 나눠 병렬 개발한다 — **[parallel-tracks.md](parallel-tracks.md)(철칙·소유권)를 먼저 읽을 것.**
루트 트랙: `/track-pcb`(메인 체크아웃 전용) · `/track-cert` · `/track-biz` · `/track-ai`(워크트리).
플랫폼(웹)은 **별도 폴더의 별도 repo** — `/Users/youngseok/Desktop/majn-platform` (이 repo와 완전 무관, 참조·수정 금지).
플랫폼 작업은 그 폴더에서 세션을 열어 `/track-infra` 등 4트랙 사용.

## 프로젝트: 마중(MAJN) 스마트 요람/배시넷 PCB
USB-C 5V → MP3426 부스트 12.12V(PVDD) → TAS5805M Class-D 앰프 → 2×8Ω 진동 트랜스듀서.
ESP32-WROOM(BLE), LSM6DSOX(IMU), AP2112K-3.3(LDO). 80×60mm 4층. KC 국내인증. EasyEDA Pro `new start`/PCB1.

---

## ⚠️ EasyEDA / PCB 작업 절대 규칙 (BLOCKING)

**EasyEDA 브릿지로 PCB 코드를 작성·수정하기 전에 반드시:**

1. **[eda_routing_rules.md](eda_routing_rules.md)를 먼저 읽는다.** (자아성찰용 족쇄 — 공간감각·물리·연결성 오판·API 창조 차단)
2. **4단계 분할 진행**: 배치 → 전원 → 신호 → 동박. **한 번에 다 짜지 말 것.** 각 단계 후 멈추고 자기검증 결과 보고 + 사용자 컨펌 전 다음 단계 금지.
3. **각 단계 §4 자기검증을 수치로 통과**(겹침·넥·클리어런스·연결성). 통과 못 하면 코드 출력 금지.
4. **연결성은 union-find/flood-fill로 단정 금지** → 직접 갭분석(넷별 패드 최근접 구리 gap) 또는 권위 DRC만 신뢰.
5. **영속/비영속 구분** — `setState_*`·풋프린트정의 EP비아 modify는 복귀됨. "수정 완료" 보고 전 영속 확인.
6. **없는 API 창조 금지** — `eda_routing_rules.md §5`의 검증된 메서드/getter만. 모르면 `.agents/skills/easyeda-api/references/` 확인.

### 브릿지 기동 순서
```
node .agents/skills/easyeda-api/scripts/bridge-server.mjs (백그라운드)
→ EasyEDA에서 PCB1 열기 → 메뉴 "API Gateway" → Reconnect
→ curl http://127.0.0.1:49620/health 로 edaConnected:true 확인
```

### 참고 문서
- 현존 결함: [MAJN_에러케이스_정리_2026-06-27.md](인증준비/mcp_development/MAJN_에러케이스_정리_2026-06-27.md) (E-01~E-15)
- 과정 오류 회고: [MAJN_프로세스_오류정리_2026-06-27.md](인증준비/mcp_development/MAJN_프로세스_오류정리_2026-06-27.md) (P-01~P-28)
- SSOT 넷리스트: `인증준비/mcp_development/mcp_design_flow.json` (v1.9.0)

---

## 일반 작업 규칙
- 설계 변경·검증은 **DRC 의존 말고 전 도메인 기하검증**(단락·개방·극성·전력수지·EMI·열·기구).
- 극성·정격은 **데이터시트/실측**으로 확인(가정 금지).
- 정직하게 보고 — 안 되면 안 된다고, 불확실하면 불확실하다고. 과대약속 금지.
