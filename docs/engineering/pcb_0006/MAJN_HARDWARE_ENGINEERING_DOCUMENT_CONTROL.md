# [문서 관리 규정] MAJN 스마트 배시넷 — 하드웨어 엔지니어링 문서 관리 및 SSOT 통제 규정
(MAJN Hardware Engineering Document Control & SSOT Management Standard)

- **문서 식별자**: `MAJN_HARDWARE_ENGINEERING_DOCUMENT_CONTROL`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)

---

## 1. 개요 및 목적

본 규정은 MAJN 스마트 배시넷 하드웨어 및 회로 개발 과정에서 생성되는 모든 기술 문서, 설계 데이터, 시험 성적서의 **문서 식별 체계, 버전 관리, 단일 진실 공급원(SSOT) 유지, 그리고 폐기/격리 절차**를 공식 표준화한다.

---

## 2. 문서 식별 번호 체계 (Document ID Schema)

모든 엔지니어링 문서는 다음 표준 접두사와 번호 규칙을 따른다:

```
[도메인]_[보드식별자]_[문서유형]_[버전/일자]
예시: DOC03_PCB0006_ELECTRICAL_DESIGN_REQUIREMENTS_v1.2.md
```

* **도메인 분류 코드**:
  - `REQ`: 요구사항 정의서 (Requirements)
  - `ARCH`: 시스템 및 서브시스템 아키텍처 (Architecture)
  - `SPEC`: 상세 설계 사양서 (Specification)
  - `SCH` / `PCB`: 회로도 및 레이아웃 관련 문서
  - `DVP` / `TP`: 시험 계획서 및 절차서 (Test Procedures)
  - `FMEA` / `FA`: 신뢰성 분석 및 고장 분석 보고서 (Failure Analysis)
  - `ECO`: 엔지니어링 변경 명령서 (Engineering Change Order)
  - `CERT`: 법정 인증 및 규제 대응 문서 (Certification)

---

## 3. 리비전 및 상태 머신 관리 규칙

모든 문서는 헤더에 다음 4대 상태 중 하나를 명시해야 한다:
1. `DRAFT`: 초안 작성 단계 (검토 미완료).
2. `UNDER_REVIEW`: 독립 기술 심사 에이전트(Antigravity) 검토 진행 중.
3. `APPROVED`: 최종 설계 승인자(Chief Authority) 공식 승인 완료.
4. `DEPRECATED`: 상위 리비전 제정으로 폐기 및 격리된 상태.

> [!WARNING]
> **단일 진실 공급원(SSOT) 절대 원칙**
> - 동일한 설계 정보(예: 부품 LCSC 번호, 핀 매핑 등)를 여러 문서에 파편화하여 중복 기술하지 않는다.
> - 부품 정보의 SSOT는 `docs/engineering/pcb_0006/PCB_0006_COMPONENT_SELECTION_MATRIX.csv`이며, 요구사항의 SSOT는 `PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv`이다.
> - 타 문서는 SSOT 문서를 링크 참조(`[파일명](file:///...)`)해야 한다.
