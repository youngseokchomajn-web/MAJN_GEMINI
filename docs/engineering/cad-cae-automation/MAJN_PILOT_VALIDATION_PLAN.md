# MAJN CAD/CAE 자동화 체계 단계별 파일럿 검증 계획서

* **문서 번호**: VP-AUT-001
* **작성일**: 2026-11-03
* **적용 단계**: Phase 1 종료 후 Phase 2~3 실행 지침
* **책임 에이전트**: Gemini / Antigravity Engineering Lead
* **관련 문서**:
  * [ADR_CAD_CAE_AUTOMATION.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/ADR_CAD_CAE_AUTOMATION.md)
  * [SOLIDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/SOLIDCRAFT_TECHNICAL_ASSESSMENT.md)
  * [FIELDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/FIELDCRAFT_TECHNICAL_ASSESSMENT.md)
  * [MCP_INTEGRATION_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/MCP_INTEGRATION_ASSESSMENT.md)
  * [ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md](file:///Users/youngseok/Desktop/majn/docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md)

---

## 1. 파일럿 검증의 기본 원칙 (Guiding Principles)

1. **빅뱅(Big-Bang) 방식 지양 및 점진적 스케일업**:
   * 복잡한 450×250×22.5mm 전체 하우징 모델링을 처음부터 수행하지 않습니다.
   * 검증 범위와 실패 원인이 명확한 **단순 국부 구조(Pilot 1) $\rightarrow$ 진동 전달부(Pilot 2) $\rightarrow$ 전체 조립체(Pilot 3)** 순으로 점진 전개합니다.
2. **동일 조건 하에서의 공학적 교차 검증 (Strict Parity Benchmark)**:
   * FieldCraft와 상용 Abaqus 해석 결과를 비교할 때는 **완벽히 동일한 조건**을 적용해야 합니다:
     * 동일 형상 (SolidCraft STEP 파일 100% 동일 사용)
     * 동일 재료 물성 (자작나무 합판 엔지니어링 상수: $E_1=10.5\,\text{GPa}, E_2=6.2\,\text{GPa}, \nu_{12}=0.33, G_{12}=1.4\,\text{GPa}, \rho=680\,\text{kg/m}^3$)
     * 동일 유한요소 종류 (2차 사면체 `Tet10` / Abaqus `C3D10`)
     * 동일 메쉬 크기 ($h = 1.0\,\text{mm}$ 국부 시딩)
     * 동일 경계조건 및 하중 조건
3. **다면적 정량 비교 지표 적용 (Multi-Metric Verification)**:
   * 단순히 '최대 폰 미세스 응력' 하나만 비교하는 피상적 검증을 금지합니다.
   * **6대 엔지니어링 지표**를 전수 비교합니다:
     1. **변위 벡터 (Displacement)**: 최대 처짐량 $U_{z,max}$ 및 변위장 분포 (오차율 $\le 5\%$)
     2. **응력 텐서 (Stress Tensor)**: 폰 미세스 응력 $\sigma_{vM}$ 및 주응력 $\sigma_1, \sigma_3$ (오차율 $\le 10\%$)
     3. **반력 및 모멘트 (Reaction Forces)**: 구속점 반력 총합 $\sum R_z$ (평형 방정식 만족도 $\le 0.1\%$)
     4. **고유진동수 (Natural Frequencies)**: 1~5차 고유진동수 $f_1, f_2, \dots, f_5$ (오차율 $\le 3\%$)
     5. **모드 형상 직교성 (Mode Shapes)**: 모달 상관도 지수 (MAC, Modal Assurance Criterion $\ge 0.95$)
     6. **에너지 수렴성 (Strain Energy Norm)**: 격자 조밀화에 따른 총 변형 에너지 수렴률

---

## 2. Pilot 1: ECO-001 PCB 장착 구조 (CAD 모델링 & 간섭 & 국부 강성)

### 2.1. 검증 대상 및 기하 사양
* **대상 어셈블리**:
  1. 4.5T 자작나무 합판 시편 영역 ($100 \times 100 \times 4.5\,\text{mm}$, 양면 페놀 코팅)
  2. 4개 M2.5 DIN 7991 카운터싱크 관통홀 ($\varnothing 2.7\,\text{mm}$, 원뿔각 90°, 헤드 외경 $\varnothing 4.7\,\text{mm}$, 깊이 $1.6\,\text{mm}$)
  3. 4개 M2.5 황동 암-암 육각 스탠드오프 (외경 육각 4.7mm, 높이 5.0mm, M2.5 관통 암나사)
  4. 80×60mm 4층 PCB 더미 기판 (두께 1.6mm, 4개 마운팅 홀 $\varnothing 3.2\,\text{mm}$)
  5. 상부 M2.5×4mm ISO 7380 버튼헤드 볼트 및 절연 와셔

### 2.2. 단계별 실행 절차
```
[Step 1. SolidCraft 3D 모델링]
  - `rev2_params.py` 및 `ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md` 파라미터 적용
  - 하판 시편, 스탠드오프, PCB 조립체 모델링 (SolidCraft CLI / MCP)
  - STEP 파일(`pilot1_eco001.step`) 내보내기

[Step 2. 3D 기하 및 치수 정합성 검증]
  - 2D 투영 DXF 추출 후 기존 `verify_rev2.py` 검증 통과 여부 확인
  - 스탠드오프-하판 계면 및 PCB 바닥면 부품 간 간섭 검사 (Clash Volume = 0 확인)

[Step 3. FieldCraft 자동 메싱 및 1차 구조해석]
  - `pilot1_eco001.step` 임포트
  - Tet10 2차 사면체 자동 메싱 (홀 주변 시딩 0.5mm, 일반부 1.5mm)
  - 하판 바닥면 볼트 헤드 원뿔면 구속, PCB 상부 볼트 체결 토크에 의한 프리로드 및 축인장 하중($75\,\text{N}$) 인가
  - 최대 휨 변위 및 목재 원뿔면 압괴 응력 계산

[Step 4. Abaqus `.inp` 덱 출력 및 솔버 교차 검증]
  - FieldCraft에서 `pilot1_eco001.inp` 덱 내보내기
  - Abaqus/CAE (또는 CalculiX `ccx`)에서 동일 `.inp` 실행
  - 변위, 응력, 반력 6대 지표 1:1 비교
```

### 2.3. 성공 판정 기준 (Acceptance Criteria)
* SolidCraft STEP 기하 오차: CAD 설계 치수 대비 오차 **$0.00\,\text{mm}$**.
* 3D 간섭 체적: **$0.0\,\text{mm}^3$** (Clash PASS).
* FieldCraft vs Abaqus 선형 변위 오차: **$\le 5.0\%$**.
* FieldCraft Abaqus `.inp` 덱 구문 오류: **0건 (Clean Load)**.

---

## 3. Pilot 2: 진동 익사이터 브래킷 (모달 해석 및 하중 전달 경로)

### 3.1. 검증 대상 및 기하 사양
* **대상 부품**:
  1. Tectonic TEAX14C02-8 사각 코인 익사이터 장착부 ($37.0 \times 20.0 \times 9.85\,\text{mm}$)
  2. 3M 9473PC 점탄성 테이프 접착 계면 (두께 $0.26\,\text{mm}$)
  3. 상판/하판 진동 전달 리브 및 보강 보스 블록 ($16.0 \times 14.0 \times 13.5\,\text{mm}$)
* **핵심 분석 대역**: 유아 수면 달래기 햅틱 구동 주파수 **$30\sim 65\,\text{Hz}$**.

### 3.2. 단계별 실행 절차
```
[Step 1. SolidCraft 브래킷 모델링]
  - 익사이터 외형 및 보스 체결 리브 모델링
  - 질량 특성 산출 (익사이터 실측 질량 11.5g과 CAD 해석치 비교)

[Step 2. FieldCraft Block Lanczos 고유진동수 해석]
  - 10개 볼트 체결점 완전 고정 경계조건
  - 1차~10차 모드 고유진동수 및 모드 형상 추출
  - 30~65Hz 대역 내 공진 피크(Resonant Modes) 존재 여부 탐색

[Step 3. Abaqus 교차 검증 및 FRF 갭 분석]
  - 동일 STEP 모델을 Abaqus로 가져와 `*FREQUENCY, EIGENSOLVER=LANCZOS` 수행
  - 고유진동수 오차 및 모드 형상(MAC) 비교
  - **Abaqus Steady-State Dynamics (Direct/Modal)**를 추가 수행하여,
    FieldCraft에서 지원하지 못하는 30~65Hz 주파수별 가속도 응답(FRF) 기준선 수립
```

### 3.3. 성공 판정 기준 (Acceptance Criteria)
* FieldCraft vs Abaqus 1~5차 고유진동수 오차: **$\le 3.0\%$**.
* 모달 상관도 지수 (MAC Matrix): 대각 성분 **$\ge 0.95$**.
* 30~65Hz 대역 모달 파악 무결성: 공진 모드 누락 0건.

---

## 4. Pilot 3: MAJN 하우징 전체 디지털 트윈 (확장 및 시스템 검증)

### 4.1. 검증 대상 (전체 조립체)
* 상판 ($450 \times 250 \times 4.5\,\text{mm}$)
* 하판 ($450 \times 250 \times 4.5\,\text{mm}$)
* 장변 사이드 레일 2개 ($410 \times 13.5 \times 4.5\,\text{mm}$)
* 단변 사이드 레일 2개 ($210 \times 13.5 \times 4.5\,\text{mm}$, $\varnothing 7.0\,\text{mm}$ 그로밋 홀 포함)
* 코너 블록 12개 ($R=20\,\text{mm}$) 및 스크루 보스 18개 ($16 \times 14 \times 4.5\,\text{mm}$)
* 식품용 실리콘 가스켓 (1.2T 시트)
* 10개 M3 체결 볼트 및 4개 PCB 체결 스탠드오프, ESP32 메인보드

### 4.2. 해석 시나리오
1. **아기 체중 재하 정적 구조해석**:
   * 상판 중앙에 유아 최대 체중 하중 $7.0\,\text{kg} \times 9.81\,\text{m/s}^2 = 68.7\,\text{N}$ 인가.
   * 상판 최대 처짐량 ($\le 0.8\,\text{mm}$ 목표) 및 내부 캐비티 에어갭($3.39\,\text{mm}$) 간섭 여부 검증.
2. **전체 시스템 모달 해석**:
   * 조립체 전체의 1~20차 고유진동수 및 진동 모드 맵 구축.
   * 익사이터 구동 주파수($30\sim 65\,\text{Hz}$)와 전체 하우징 공진 회피 대역 확인.

---

## 5. 단계별 검증 일정 및 게이트 요약

| 마일스톤 | 대상 작업 | 검증 툴체인 | 성공 기준 | 산출물 |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1 (현재)** | 선행 기술 분석 및 아키텍처 수립 | 문서 조사 / GitHub / MCP 스펙 | 기술 검토 문서 5종 완성 | ADR 및 기술보고서 5종 |
| **Phase 2 (착수 대기)** | Pilot 1: ECO-001 체결부 CAD/CAE 검증 | SolidCraft + FieldCraft + Abaqus | 치수오차 0.0mm, 변위오차 $\le 5\%$ | `pilot1_eco001.step`, `.inp`, 보고서 |
| **Phase 3 (착수 대기)** | Pilot 2: 익사이터 브래킷 모달 검증 | FieldCraft Lanczos + Abaqus FRF | 고유진동수 $\le 3\%$, MAC $\ge 0.95$ | 모달 벤치마크 리포트 |
| **Phase 4 (착수 대기)** | Pilot 3: 전체 하우징 디지털 트윈 및 E01/E11 승격 | 전체 파이프라인 자동화 (Gemini MCP) | 아기하중 처짐 적합, CI/CD 통합 | E01/E11 공식 승격 심의서 |

---

## 6. 결론 및 Phase 1 종료 선언
본 문서를 포함한 **Phase 1 기술 검토 보고서 5종의 작성이 완료**되었습니다.
실제 바이너리 설치 및 CAD 모델 생성, 기존 엔지니어링 자산 승격은 **인간 엔지니어의 별도 검토 및 승인(Gate Review)을 거친 후 Phase 2로 전환하여 실행**합니다.
