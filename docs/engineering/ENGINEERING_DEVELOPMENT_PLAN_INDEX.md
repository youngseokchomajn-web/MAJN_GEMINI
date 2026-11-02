# MAJN 엔지니어링 통합 시스템 개발계획 — 문서 인덱스

- 상태: Draft for review and staged execution
- 기준 감사 브랜치: `docs/engineering-system-wp00-wp01-baseline`
- 이 브랜치: `docs/engineering-system-development-plan`

## 읽는 순서

1. [상세 개발 실행계획](ENGINEERING_DEVELOPMENT_EXECUTION_PLAN.md) — 전체 아키텍처, 18개 영역, 단계별 개발, 게이트, 역할, 통제 원칙
2. [예상 이슈·충돌·리스크 관리대장](ENGINEERING_RISK_AND_CONFLICT_REGISTER.md) — 초기 P0/P1/P2 리스크와 충돌, 상태 체계, ECO 영향평가
3. [기구·전장·케이블 통합계획](ENGINEERING_INTEGRATION_AND_INTERFACE_PLAN.md) — Cable Routing, PCB 장착, RF, 전원/BTL, 3D Viewer 통합
4. [검증·계측·안전·릴리즈 계획](ENGINEERING_VERIFICATION_AND_RELEASE_PLAN.md) — 시험 계층, 실측, CAE V&V, 안전, 연구/임상, CI 및 릴리즈
5. [Work Package 실행 백로그](ENGINEERING_WORK_PACKAGE_BACKLOG.md) — 30개 실행 티켓, 의존성, 첫 2주 계획, 중단 조건

## 현재 실행 권고

첫 작업은 ENG-001~ENG-006의 기준선 충돌 해결이다. 그와 병행해 데이터 스키마/레지스터 초안을 만들 수 있지만, 미확정 기구 치수·PCB 구성·익사이터 부하·안테나 조건을 설계 기준으로 승격하지 않는다.

## 승인 경계

이 문서 세트는 개발계획이다. 다음 항목은 별도 승인 전까지 HOLD:
- PCB Rev-C 제조 발주
- 하판/하우징의 PCB mounting hole 가공
- 8Ω 익사이터 양산 적용
- RF 안테나 모델 및 인증 범위 확정
- 450×250 / 720×390 제품군의 상용 제품 범위 확정
- 영아 안전/진정 효능 기준 및 관련 주장
- 제품 규제 적합성/인증 완료 선언

기존 원본과 WP-00/WP-01 감사 산출물은 이 브랜치에서 수정하지 않았다. 개발 실행 시에는 별도 작업 브랜치와 ECO/PR을 사용한다.
