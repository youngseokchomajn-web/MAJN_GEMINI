# Gem 운영 정책 v1

## 기본 원칙

1. 현재 GitHub 상태와 커밋 증거를 먼저 읽는다.
2. 문제 → 가설 → 검증 → 실패 → 수정 → 재검증 → 최종결정의 흐름을 유지한다.
3. 이 단계에서는 read-only가 기본이다.
4. 인증 통과, EMC 적합, 설계 안전성을 추측으로 선언하지 않는다.
5. EasyEDA Live PCB와 GitHub export가 다를 수 있음을 전제로 한다.

## 자동화 경계

- main 직접 push 금지
- PCB master 자동 수정 금지
- 인증/EMC 합격 판정 자동 확정 금지
- 외부 서비스에 비밀정보 전달 금지
- 자동 생성 결과는 증거와 함께 Draft PR 대상으로만 취급한다.
- 자동 생성 커밋은 [gem-auto] 태그를 사용하고 watcher 재실행을 방지한다.

## 트랙 분리

- PCB: geometry, net, footprint, routing
- 인증/EMC: 위험도, 시험전략, 인증준비 문서
- firmware: 펌웨어/bring-up
- ai_ops: Gem orchestration 자체

트랙 경계를 넘는 변경은 영향 범위를 명시하고 사람 확인을 요구한다.

## EasyEDA

GitHub Actions가 사용자 PC의 EasyEDA Pro 세션에 직접 접근한다고 가정하지 않는다.
Live PCB 검증은 로컬 Bridge/API가 실제 연결된 환경에서만 수행한다.

## 상태

[PASS] 검증 통과
[FAIL] 현재 검증 실패
[BLOCKED] 필요한 실행/접근 조건이 없음
[NEEDS_EVIDENCE] 증거 부족
[UNCERTAIN] 결론 보류

PASS는 자동 인증 합격을 의미하지 않는다.
FAIL은 제품 실패가 아니라 현재 검증 실패일 수 있다.
