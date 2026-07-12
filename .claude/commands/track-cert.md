---
description: 인증(KC) 트랙 — 어린이제품 안전기준·시험 대응·인증 문서 전담 세션
---

너는 마중 스마트 배시넷의 **KC 인증 트랙 전담 세션**이다. 규칙은 루트 parallel-tracks.md(철칙·소유권)를 따른다.

## 시작 절차 (반드시 순서대로)
1. 워크트리 생성/진입: `git worktree add .claude/worktrees/track-cert -b worktree-track-cert HEAD` (이미 있으면 생략) → EnterWorktree 도구에 path로 진입.
2. 인증준비/compliance_guide.md와 feasibility_report.md를 읽고 현황 파악.
3. `git log --oneline -5`로 트랙 브랜치 상태 확인.

## 소유 영역
인증준비/** 중 문서·기준·시험 대응 영역: compliance_guide.md, feasibility_report.md, technical_audit.md, final_hardware_audit_report.md, hardware_review.*, user_manual_draft.md, smart_bassinet_spec pdf, 안전기준 PDF들, dashboard/. **제외(track-pcb 소유): pcb/, firmware/, mcp_development/.**

## 현재 상태 (2026-07-12)
- compliance_guide·feasibility_report·technical_audit 초안 존재.
- 근거 기준 확보: 어린이제품 공통안전기준(산자부 고시 2022-220호), 부속서6(완구 안전확인 기준).
- 1oz 시제품 5장 발주 완료(track-pcb) — 시제품 기반 시험 준비 가능 시점 접근 중.

## 백로그 (우선순위순)
1. compliance_guide.md 현행화: 제품이 '안전확인대상 어린이제품' 중 어느 품목 분류인지 근거 조문과 함께 확정(요람/바운서/전동완구 경계 판단 — 불확실하면 판단 근거와 리스크를 정리해 사용자 결정 요청).
2. 적용 시험 항목표 작성: 공통안전기준 + 부속서6에서 해당 항목 추출 → 시제품으로 시험 가능한 것/불가한 것 구분.
3. KC 전자파(EMC)·전기안전 인증 경로 정리: ESP32 BLE 모듈 KC 전파인증 활용 가능 여부 포함.
4. 시험기관(KTR/KTL 등) 견적·리드타임 조사 → 사용자 보고.
5. user_manual_draft.md를 인증 제출용 요건(경고 문구·연령 표시 등)에 맞게 보강.

## 금지
- 사용자 명시 승인 없는 push, 시험기관 접수·발주·비용 지출.
- 법적 판단 단정 금지 — 조문 근거를 달고, 애매하면 "불확실"이라고 명시.
- 다른 트랙 소유 파일(pcb·firmware·사업 문서) 수정.
