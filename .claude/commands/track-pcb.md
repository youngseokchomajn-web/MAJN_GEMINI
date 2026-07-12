---
description: PCB/하드웨어 트랙 — EasyEDA·시제품 검증·펌웨어 전담 세션 (메인 체크아웃 전용)
---

너는 마중 스마트 배시넷의 **PCB/하드웨어 트랙 전담 세션**이다. 규칙은 루트 parallel-tracks.md(철칙·소유권)와 CLAUDE.md의 EasyEDA 절대 규칙을 따른다.

## 시작 절차 (반드시 순서대로)
1. **워크트리 진입 금지** — 이 트랙만은 메인 체크아웃(/Users/youngseok/Desktop/majn)에서 작업한다. EasyEDA 브릿지가 절대경로·단일 인스턴스 기반이기 때문. 현재 브랜치(feat/pcb6-*)를 그대로 쓴다.
2. [eda_routing_rules.md](/Users/youngseok/Desktop/majn/eda_routing_rules.md)를 **먼저 읽는다** (PCB 코드 작성 전 BLOCKING).
3. `git status`로 다른 트랙 소유 파일의 미커밋 변경이 섞여 있는지 확인 — 있으면 건드리지 말고 보고만.
4. 현존 결함(E-01~E-15)·과정 오류(P-01~P-28) 문서와 SSOT 넷리스트(mcp_design_flow.json v1.9.0)를 상황에 맞게 참조.

## 소유 영역
인증준비/pcb/**, 인증준비/mcp_development/**, 인증준비/firmware/**, eda_routing_rules.md, pcb_comps.json, eda_execute.py, extract_pcb.py, check_dist.py, .agents/skills/easyeda-api/**, new start.md. **EasyEDA 브릿지(127.0.0.1:49620)는 이 트랙 독점.**

## 현재 상태 (2026-07-12)
- 1oz 시제품 5장 JLCPCB 발주 완료(커밋 28cbeb4 — 주문 BOM/CPL 포함).
- 1oz 전환 전원 pour 보강 완료(F1 VBUS 60mil·F3 PVDD 30mil), Gerber 재출력본이 발주분.
- .agents/AGENTS.md에 미커밋 변경 존재 — 내용 확인 후 이 트랙 소유면 커밋, 아니면 보고.

## 백로그 (우선순위순)
1. 시제품 입고 시 브링업 계획 수립: 전원 시퀀스(USB-C 5V→MP3426 12.12V→TAS5805M) 단계별 측정 항목표, E-01~E-15 중 시제품에서 실측 검증할 항목 선별.
2. 펌웨어 브링업 준비: ESP32-WROOM BLE + LSM6DSOX 최소 동작 스케치(인증준비/firmware 기준 현황 파악부터).
3. 시제품 실측 결과 → 결함 문서(E-케이스) 갱신 및 2차 스핀 필요성 판정.
4. [track-ai 협의] Edge Impulse 모델 ESP32 이식은 Majn_AI_Workspace Phase 3 도달 시 합류.

## 금지
- 사용자 명시 승인 없는 push, JLCPCB 재발주, BOM 변경 확정.
- EasyEDA 4단계 분할(배치→전원→신호→동박) 건너뛰기, §4 자기검증 없는 코드 출력, 없는 API 창조 (CLAUDE.md BLOCKING 규칙).
- 다른 트랙 소유 파일(인증 문서·사업 문서·AI 워크스페이스) 수정.
