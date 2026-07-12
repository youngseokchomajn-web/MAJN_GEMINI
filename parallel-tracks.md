# 마중(MAJN) 루트 병렬 개발 트랙 (SSOT)

> 갱신: 2026-07-12. majn 루트 repo(MAJN_GEMINI)를 세션 여러 개로 병렬 작업하기 위한 분할 기준.
> 각 트랙은 새 Claude Code 세션(작업 폴더: `/Users/youngseok/Desktop/majn`)에서 `/track-<이름>` 커맨드로 시작한다.
> 플랫폼(웹)은 **2026-07-12 완전 분리됨** → `/Users/youngseok/Desktop/majn-platform` (별도 repo, 트랙 4개는 그쪽 docs/parallel-tracks.md 참조).
> 이 repo(하드웨어·인증·사업)와 플랫폼은 서로 참조·수정하지 않는다.

## 철칙 (모든 트랙 공통)

1. **자기 소유 폴더만 수정** — 아래 소유권 표 기준. 남의 트랙 파일을 고쳐야 하면 그 트랙 백로그에 남기고 넘어간다.
2. **스테이징은 파일 단위로** — `git add -A`·`git add .` 금지. 자기 소유 파일만 명시적으로 스테이징.
3. **push는 사용자 승인 후에만.** 브랜치 병합 시점도 사용자가 결정.
4. **EasyEDA 브릿지(49620)는 track-pcb 독점** — 다른 트랙은 EasyEDA/브릿지에 접근 금지.
5. 워크트리 트랙(cert·biz·ai)은 반드시 커맨드의 시작 절차로 워크트리에 진입 후 작업. 메인 체크아웃은 track-pcb 전용.
6. 미추적 대용량 폴더(GEMINI/, Claude-Kaggle/, .venv 등)는 워크트리에 복제되지 않음 — 필요하면 절대경로로 참조만.

## 트랙 정의

| 트랙 | 커맨드 | 작업 위치 | 소유 영역 |
|---|---|---|---|
| ① PCB/하드웨어 | `/track-pcb` | **메인 체크아웃** (브랜치 feat/pcb6-*) | pcb 관련 전부: 인증준비/pcb·mcp_development, eda_routing_rules.md, pcb_comps.json, eda/extract 스크립트, .agents/skills/easyeda-api, 인증준비/firmware |
| ② 인증(KC) | `/track-cert` | 워크트리 track-cert | 인증준비/** (pcb·firmware·mcp_development 제외 — 문서·기준·시험 대응) |
| ③ 사업/투자 문서 | `/track-biz` | 워크트리 track-biz | 사업계획서/**, 프라이머 배치 지원/**, 경쟁제품조사/**, 단톡방/**(참고자료) |
| ④ AI/ML 워크스페이스 | `/track-ai` | 워크트리 track-ai | Majn_AI_Workspace/** (firmware_esp32 이식 단계는 track-pcb와 협의) |

**공유 파일(수정 전 충돌 확인)**: 루트 `CLAUDE.md`, `README.md`, `.agents/AGENTS.md`, 이 문서(parallel-tracks.md).
공유 파일을 고치는 커밋은 메시지에 `[shared]`를 붙인다.

## 워크트리 규약 (cert·biz·ai)

- 생성: `git worktree add .claude/worktrees/track-<이름> -b worktree-track-<이름> HEAD` (현재 HEAD 기준 — origin이 오래됐으므로 origin 기준 금지)
- 진입: EnterWorktree 도구에 `path`로 위 경로 전달.
- 병합: 트랙 브랜치에서 작업 → 사용자 승인 후 메인 체크아웃 브랜치에 병합(담당: track-pcb 세션 또는 사용자).
- 문서(.docx/.pages/.xlsx)는 바이너리라 git 병합 불가 — **같은 문서는 한 트랙만 만진다.**

## 현재 상태 스냅샷 (2026-07-12)

- 루트 repo 브랜치: `feat/pcb6-power-first` (origin/MAJN_GEMINI에 미푸시 상태 여부는 세션에서 확인).
- **PCB**: 1oz 시제품 5장 JLCPCB 발주 완료(28cbeb4). 현존 결함 E-01~E-15, 과정 오류 P-01~P-28 문서 참조(인증준비/mcp_development/).
- **인증**: compliance_guide.md·feasibility_report.md 초안 존재. 어린이제품 공통안전기준(고시 2022-220호)·부속서6 PDF 확보.
- **사업**: 예비창업패키지 사업계획서 작성 중([작성중] docx, 루트), 초안·원가산정은 사업계획서/. 프라이머 29기 지원서 제출본 보관.
- **AI**: Majn_AI_Workspace TODO.md Phase 1 진행 중(데이터 로거·mock 생성기 완료, AudioSet 다운로드·ADXL355 수집 미착수).
- **플랫폼**: /Users/youngseok/Desktop/majn-platform 으로 분리됨(2026-07-12). 이 repo와 무관.
