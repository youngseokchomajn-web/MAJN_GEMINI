# [AI 워크플로우] MAJN 스마트 배시넷 — Dual-AI 엔지니어링 협업 및 형상 통제 가이드
(MAJN Dual-AI Engineering Workflow & Configuration Control Guide)

- **문서 식별자**: `MAJN_AI_ENGINEERING_WORKFLOW`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)

---

## 1. 3자 협업 체계 및 역할 분담 (Tripartite Collaboration)

| 주체 | 주 모델 / 시스템 | 역할 및 기본 권한 | 핵심 책임 및 행동 범위 |
|:---|:---|:---|:---|
| **OpenCode** | GPT-6 Astra | **주 개발 에이전트 (Lead)**<br>작업공간 수정 권한 | • 회로 설계 분석 및 변경안 작성<br>• EasyEDA API를 통한 승인된 작업 실행<br>• 개발계획 및 코드 구현 |
| **Antigravity** | Gemini 3.1 Pro / Flash | **독립 기술 검토자 (Reviewer)**<br>**읽기 전용 (Read-Only) 원칙** | • 기술적 반론, 누락/위험 사전 탐지<br>• Git diff 및 무결성 감시<br>• 자동 검증 스크립트 구축 및 시험 결과 감리 |
| **인간 (Human)** | 조영석 | **최종 설계 승인권자 (Chief Authority)**<br>절대 최종 결정권 | • 회로 원본 수정 및 부품 변경 최종 승인<br>• Gate 통과 여부 확정<br>• 제조 발주 및 릴리스 서명 |

---

## 2. 작업 큐 디렉토리 구조 (`.majn_ai_workflow/`)

```
.majn_ai_workflow/
├── inbox/         # 신규 검토 요청 및 이슈 등록
├── plans/         # OpenCode 개발계획서 및 변경 제안서
├── reviews/       # Antigravity 독립 기술 심사 보고서
├── approved/      # 인간 설계권자가 승인한 작업 (Execution 대기)
├── execution/     # 현재 진행 중인 실시간 작업
├── verification/  # 자동 DRC, 스크립트 및 실측 시험 결과
├── completed/     # 최종 완료 및 Gate 승인 아카이브
└── state/         # 시스템 상태 머신 JSON (현재 활성 태스크 추적)
```

---

## 3. 엄격한 충돌 방지 및 Git 통제 원칙

1. **동시 수정 원천 차단**: 동일한 파일(예: 회로도 JSON, BOM, 펌웨어 헤더)을 두 AI 에이전트가 동시에 수정할 수 없음.
2. **사전 검증(No Blind Push)**: 모든 `git push` 실행 전 `tools/pcb_verification/` 도구를 구동하여 불일치 0건을 확인한 후 원격 저장소(`origin`) 상태를 선제 스캔(`git fetch`)함 (`git_safe_sync_guard` 준수).
3. **증거 기반 커밋 메시지**: 커밋 메시지에는 반드시 변경 ID(ECO 번호 또는 DOC 번호)와 검증 결과 요약을 포함함.
