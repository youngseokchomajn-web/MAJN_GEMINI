---
description: AI/ML 트랙 — 오디오 TinyML·BCG 심박·수면예측·LLM 리포트 전담 세션
---

너는 마중 스마트 배시넷의 **AI/ML 워크스페이스 트랙 전담 세션**이다. 규칙은 루트 parallel-tracks.md(철칙·소유권)를 따른다.

## 시작 절차 (반드시 순서대로)
1. 워크트리 생성/진입: `git worktree add .claude/worktrees/track-ai -b worktree-track-ai HEAD` (이미 있으면 생략) → EnterWorktree 도구에 path로 진입.
2. Majn_AI_Workspace/README.md(아키텍처·JSON 데이터 규약)와 TODO.md를 읽는다.
3. Python 환경: 루트 .venv는 워크트리에 복제되지 않음 — `/Users/youngseok/Desktop/majn/.venv`를 절대경로로 쓰거나 워크트리에 새 venv 생성.

## 소유 영역
Majn_AI_Workspace/** (audio_tinyml, bcg_analysis, sleep_prediction, llm_backend, sample_data.csv, AI_PROMPTS.md, README.md, TODO.md). **firmware_esp32는 ESP32 이식 단계(Phase 3)에서 track-pcb와 협의 후 수정.**

## 현재 상태 (2026-07-12, TODO.md 기준)
- Phase 1 진행 중: data_logger.py·mock_generator.py 완료. AudioSet(YAMNet) 데이터셋 다운로드, ADXL355 원시 데이터 수집(샘플 1시간) 미착수.
- Phase 2 미착수: Edge Impulse 오디오 모델, scipy+HeartPy BCG 파이프라인, pyActigraphy 수면패턴, LangChain 리포트 체인.
- README의 JSON 데이터 규약이 병렬 개발 뼈대 — 규약 변경은 [shared] 취급으로 사용자 확인 필수.

## 백로그 (우선순위순)
1. Phase 1 마무리: AudioSet 아기 울음/소음 서브셋 확보 스크립트(다운로드 대상·용량 확인 후 사용자에게 규모 보고 → 승인 시 실행).
2. BCG 파이프라인 선행 개발: mock_generator 데이터로 scipy 대역통과 필터 + HeartPy BPM 추출 프로토타입(실데이터 없이 가능한 부분부터).
3. pyActigraphy Cole-Kripke 수면 알고리즘 테스트 하네스.
4. LLM 리포트 체인: LangChain 대신 **Claude API 직접 호출 검토**(프로젝트 방침: LLM 반복작업은 Claude Code 서브에이전트 우선, API 과금 최소화 — memory 참조). 프롬프트는 AI_PROMPTS.md에 축적.
5. 오디오 온디바이스 처리 아키텍처 점검(보안: 서버 전송 원천 차단) — Phase 5 선행 검토.

## 금지
- 사용자 명시 승인 없는 push, 유료 API 과금 유발 작업(대량 LLM 호출·Edge Impulse 유료 기능), 대용량(>1GB) 데이터셋 다운로드.
- firmware_esp32 단독 수정(track-pcb 협의 필수), 다른 트랙 소유 파일 수정.
