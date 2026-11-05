# [도구 로드맵] MAJN 스마트 배시넷 — 하드웨어 자동 검증 도구 계획서
(MAJN Automated Hardware Validation Tool Suite Roadmap & Implementation Plan)

- **문서 식별자**: `MAJN_AUTOMATED_VALIDATION_TOOL_PLAN`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)

---

## 1. 개요 및 도구 구축 목표

AI 에이전트와 엔지니어가 수작업으로 수백 개의 핀, 부품, 좌표를 대조하는 과정에서 발생하는 휴먼 에러를 원천 제거하기 위해, **파이썬 기반 자동 검증 도구(Automated Validation Tool Suite)**를 구축하여 형상 무결성을 보장한다.

---

## 2. 구축 완료 도구 (Phase 0 구현 완료)

| 도구 스크립트 | 주 실행 명령 | 입력 데이터 | 검증 항목 및 출력 | 상태 |
|:---|:---|:---|:---|:---:|
| **1. 부품/좌표 대조기** | `python3 tools/pcb_verification/bom_cpl_comparator.py` | BOM.csv, CPL.csv, design.json | • 56개 Designator 집합 일치율<br>• LCSC Part # 불일치 탐지<br>• CPL vs JSON 좌표 편차(>0.05mm) 탐지 | **구축 완료<br>(VERIFIED)** |
| **2. 거버 무결성 검사기** | `python3 tools/pcb_verification/gerber_integrity_checker.py` | Gerber.zip | • 20개 레이어 파일 존재 여부<br>• 4층 스택업(G1 GND, G2 VCC) 검증<br>• 드릴 파일(PTH, NPTH, Via) 검증 | **구축 완료<br>(VERIFIED)** |
| **3. 요구사항 추적성 검사기**| `python3 tools/pcb_verification/requirements_traceability_checker.py` | RTM.csv | • 필수 요구사항 ID(12종) 누락 검사<br>• 구현/검증 상태 통계<br>• 결측 트레이서빌리티 탐지 | **구축 완료<br>(VERIFIED)** |

---

## 3. 후속 추가 개발 도구 로드맵 (Phase 3 ~ Phase 5)

1. **`netlist_pin_comparator.py` (개발 예정, Phase 3)**:
   - 회로도 넷리스트(`.tel`)와 PCB 레이아웃 넷리스트를 핀 단위로 교차 파싱하여, 단선(1-pin), 단락(쇼트), GND 오흡수 넷을 100% 자동 탐지.
2. **`eco_validator.py` (개발 예정, Phase 4)**:
   - ECO 제안서의 Before/After 넷리스트 및 BOM을 비교하여, 제안되지 않은 임의의 회로 변경이 혼입되었는지 자동 감시.
3. **`release_sha_manifest_generator.py` (개발 예정, Phase 5)**:
   - 최종 릴리스 폴더 내의 모든 Gerber, BOM, CPL, PDF, 펌웨어 바이너리의 SHA-256 해시를 수집하여 공식 `RELEASE_SHA256_MANIFEST.txt` 자동 생성.

---

## 4. 로컬 CI 검증 파이프라인 연계 (`git commit` 전 자동 실행)

개발자가 로컬에서 커밋하거나 푸시하기 전 다음 원라이너 명령을 통해 전체 하드웨어 무결성을 일괄 검증한다:

```bash
# 하드웨어 자동 무결성 전수 검사 스위트 구동
python3 tools/pcb_verification/bom_cpl_comparator.py && \
python3 tools/pcb_verification/gerber_integrity_checker.py && \
python3 tools/pcb_verification/requirements_traceability_checker.py && \
node tests/test_protocol_vectors.js && \
python3 tools/test_command_parser.py
```
* 위 5개 검증 단계가 **100% PASS**인 경우에만 `git commit` 및 `git push`가 허용됨.
