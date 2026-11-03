# ADR-008: MAJN CAD/CAE 엔지니어링 자동화 체계 도입 (SolidCraft + FieldCraft + Abaqus + Gemini MCP)

* **상태 (Status)**: PROPOSED / UNDER_REVIEW (Phase 1 기술 검토)
* **작성일 (Date)**: 2026-11-03
* **영역 (Domain)**: E01 (CAD·기구설계), E11 (CAE·물리 시뮬레이션), E14 (자동화 파이프라인)
* **책임 에이전트**: Gemini / Antigravity Engineering Lead
* **관련 문서**:
  * [SOLIDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/SOLIDCRAFT_TECHNICAL_ASSESSMENT.md)
  * [FIELDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/FIELDCRAFT_TECHNICAL_ASSESSMENT.md)
  * [MCP_INTEGRATION_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/MCP_INTEGRATION_ASSESSMENT.md)
  * [MAJN_PILOT_VALIDATION_PLAN.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/MAJN_PILOT_VALIDATION_PLAN.md)
  * [ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md](file:///Users/youngseok/Desktop/majn/docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md)
  * [WP00_WP01_INTEGRATED_AUDIT_REPORT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/WP00_WP01_INTEGRATED_AUDIT_REPORT.md)

---

## 1. 배경 및 현황 (Context)

현재 MAJN 스마트 배시넷 프로젝트의 기구 설계 및 엔지니어링 해석 자산은 다음과 같은 구조적 단절을 겪고 있습니다:

1. **기구 CAD의 2.5D 의존성**:
   * 기구 형상 SSOT가 Python 스크립트 기반 2.5D DXF 생성(`build_rev2_dxf.py`, `rev2_params.py`)과 Anatomy 스킬 기반 2.5D 아이소메트릭 SVG에 머물러 있습니다.
   * 부품 간 3차원 공간 간섭(PCB 부품 높이, 하판 볼트 헤드 카운터싱크 단차, 실리콘 그로밋 케이블 경로)을 수학적 2D 투영 평면에서 좌표 연산으로만 점검해야 하는 한계가 존재합니다.
2. **CAE 시뮬레이션 워크플로의 파편화**:
   * 브라우저 기반 WebGL FEM 시뮬레이터([`bassinet_simulator/fem_wasm_solver.js`](file:///Users/youngseok/Desktop/majn/bassinet_simulator/fem_wasm_solver.js))가 자작나무 직교이방성 물성 기반 Abaqus `.INP` 포맷 생성기를 갖추고 있으나, CAD 형상에서 3D 사면체/육면체 메쉬를 자동으로 분할하여 솔버로 전달하는 파이프라인이 부재합니다.
   * 실무에서 정밀 검증용으로 운용되는 상용 Abaqus 해석과 로컬 설계 파라미터 간의 자동화된 브릿지가 없습니다.
3. **AI 에이전트(Gemini) 제어 인터페이스의 불균형**:
   * 전자/PCB 도메인은 EasyEDA Pro WebSocket 브릿지(포트 `49620`)를 통해 에이전트가 넷리스트, 부품 배치, DRC 검사를 실시간 수행할 수 있으나, 기구(CAD) 및 구조/진동(CAE) 도메인은 실시간 상호작용 도구가 전무하여 정적 텍스트 및 스크립트 검토에 의존하고 있습니다.

이러한 문제를 해결하기 위해 Tangency Labs의 오픈소스 Rust 기반 3D CAD인 **SolidCraft**와 다중물리 해석 도구인 **FieldCraft**의 도입 가능성을 검토합니다.

---

## 2. 결정 동인 (Decision Drivers)

1. **기존 엔지니어링 기준선(SSOT)의 100% 보존**:
   * 기존 Python 파라미터(`rev2_params.py`), 레이저 커팅 마스터 DXF, 회로도 SSOT(`mcp_design_flow.json`), 펌웨어 소스는 일체 임의 덮어쓰기나 왜곡 없이 보존되어야 합니다.
2. **도구의 성숙도에 부합하는 현실적 역할 분담**:
   * FieldCraft는 현재 초기 개발 단계(50개 벤치마크 중 6개 실패 보고, 접촉/좌굴/주파수 의존 동특성 미지원)이므로, 산업 표준인 **Abaqus의 '완전 대체재'로 취급하지 않고**, **"Abaqus의 프론트엔드 프리프로세서(Auto Mesher + Pre-deck Generator) 및 1차 스크리닝 솔버"**로 역할을 명확히 한정합니다.
3. **Modal Analysis(고유진동수)와 Mode-based FRF(주파수 응답)의 엄격한 구별**:
   * 선형 주파수 해석(Block Lanczos) 역량과 실제 제품에서 요구되는 감쇠(Damping), 모달 전달함수(FRF), 회전속도 의존 강성 해석을 혼동하지 않고 독립적으로 검증합니다.
4. **Agent-Native 아키텍처(MCP) 확보**:
   * 두 도구가 기본 제공하는 Model Context Protocol (stdio JSON-RPC 2.0) 서버를 활용하여 Gemini가 Headless 및 GUI Bridged 모드로 자율 제어할 수 있는 기반을 구축합니다.
5. **단계적 검증(Phased Pilot Verification)**:
   * 450×250×4.5T 하판 전체를 한 번에 전환하지 않고, ECO-001 PCB 체결부(Pilot 1) $\rightarrow$ 진동 익사이터 브래킷(Pilot 2) $\rightarrow$ 전체 하우징 디지털 트윈(Pilot 3)으로 단계별 검증을 수행합니다.

---

## 3. 아키텍처 결정 사항 (Decision)

### 3.1. 4-Tier 통합 엔지니어링 아키텍처 채택

MAJN 프로젝트의 형상 설계 및 해석 체계를 다음과 같이 4계층으로 분리하여 구축합니다:

```
┌────────────────────────────────────────────────────────────────────────┐
│               Tier 1: Gemini / Antigravity Orchestrator                 │
│  - 설계 의도(Intent) 수립, 엔지니어링 규칙 준수 감시, 파라미터 조정 지시   │
│  - MCP(Model Context Protocol) 클라이언트를 통한 하위 툴체인 자율 구동   │
└───────┬────────────────────────┬───────────────────────────────┬───────┘
        │ (1) 형상 파라미터 제어     │ (2) 자동 메싱 & 1차 스크리닝     │ (3) 정밀/인증 해석
        ▼                        ▼                               ▼
 ┌───────────────┐        ┌───────────────┐             ┌─────────────────┐
 │ Tier 2: CAD   │        │ Tier 3: CAE   │             │ Tier 4: SOLVER  │
 │  SolidCraft   │        │  FieldCraft   │             │  Abaqus / CCX   │
 │ (Pure Rust)   │        │ (Pure Rust)   │             │ (Industry Std)  │
 ├───────────────┤        ├───────────────┤             ├─────────────────┤
 │ • B-rep 커널   │───────>│ • 자동 메싱   │────────────>│ • 비선형 접촉   │
 │ • 피처 타임라인│ (STEP) │ • 선형 정적   │ (.inp 덱)    │ • Mode-based FRF│
 │ • 3D 어셈블리 │        │ • Block Lanczos│             │ • 주파수/감쇠 동특성│
 │ • 간섭 검사   │        │   (고유진동수) │             │ • 규제 인증 해석│
 └───────┬───────┘        └───────┬───────┘             └────────┬────────┘
         │                        │                              │
         └────────────────────────┼──────────────────────────────┘
                                  ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    Tier 0: MAJN Engineering SSOT                      │
 │  - Git 형상 관리 (rev2_params.py, 마스터 DXF, 검증 스크립트, 거버)      │
 │  - 검증 완료된 ADR 및 시험 결과 데이터베이스 (Verification Log)        │
 └────────────────────────────────────────────────────────────────────────┘
```

### 3.2. 도메인별 세부 역할 및 경계 정의

| 구분 | 전담 도구 | 명확한 책임 범위 (In-Scope) | 명시적 제한 범위 (Out-of-Scope / 금지 사항) |
| :--- | :--- | :--- | :--- |
| **Tier 1: 조율** | **Gemini / Antigravity** | • MCP 명령 송수신 및 자율 설계-해석 피드백 루프<br>• 오차 분석 및 파라미터 역산 제어 | • 공학적 승인 없이 형상 기준선(SSOT) 임의 덮어쓰기 금지 |
| **Tier 2: 기구** | **SolidCraft** | • 3D B-rep 파라메트릭 솔리드 모델링<br>• STEP/IGES 파일 입출력<br>• 기구-PCB 3D 어셈블리 간섭 검사(Clash Detection) | • 도면 공차 및 제작 기준선 승인 권한 없음 (1차 모델러) |
| **Tier 3: 해석 전처리** | **FieldCraft** | • 자동 사면체(Tet) 및 육면체(Hex) 메싱<br>• 1차 선형 정적 해석(응력/처짐 스크리닝)<br>• Block Lanczos 고유진동수 및 모드 형상 해석<br>• **Abaqus `.inp` 덱 자동 변환 및 익스포트** | • **Mode-based FRF(주파수 응답) 최종 판정 금지**<br>• **복잡한 비선형 접촉 및 회전체 베어링 강성 해석 금지** |
| **Tier 4: 정밀 해석** | **Abaqus / CalculiX** | • 30~65Hz 바운싱 대역 Steady-State Dynamics (FRF)<br>• 재료 비선형, 대변형 접촉, 볼트 프리로드 비선형 해석<br>• KC/FCC 규제 인증 및 최종 양산 안전율 판정 | • 단순 형상 변경 시마다 수동 모델링하는 비효율 배제 |

---

## 4. 환경 구축 및 실행 방침 (Implementation Principles)

1. **설치 전략 (macOS Prebuilt Binary 우선)**:
   * 현재 로컬 환경에 Rust/Cargo 컴파일러가 설치되어 있지 않으므로, 소스 코드 빌드를 강제하지 않습니다.
   * SolidCraft 및 FieldCraft는 공식 macOS Universal 배포판(`.dmg` 및 Homebrew Cask `tangency-labs/tap`)을 제공하므로, 실제 설치 시 **공식 바이너리 우선 원칙**을 엄격히 적용합니다.
2. **비파괴(Non-Destructive) 원칙**:
   * Phase 1에서는 일체의 파일 설치나 기존 CAD/DXF 파일 수정을 진행하지 않으며, 기술 분석 및 통합 검토서 작성으로 한정합니다.
3. **정식 승격 게이트 (Promotion Gate)**:
   * E01(CAD), E11(CAE) 공식 엔지니어링 자산 승격은 3단계 파일럿 검증을 완전히 통과하고 회귀 검증이 완료된 이후 별도 승인 절차를 거칩니다.

---

## 5. 기대 효과 및 향후 계획 (Consequences)

### 긍정적 효과 (Positive)
* **3D 디지털 트윈 완성**: 2.5D DXF 평면에 갇혀 있던 하우징 및 PCB 체결 구조가 3D STEP 및 솔리드로 구체화되어 간섭 오류 사전 차단.
* **CAE 해석 파이프라인의 획기적 단축**: 수동 메싱과 덱 작성 없이, SolidCraft 형상 $\rightarrow$ FieldCraft 자동 메싱 $\rightarrow$ Abaqus `.inp` 덱 출력이 원클릭으로 연결됨.
* **AI 폐루프 엔지니어링 구현**: Gemini가 MCP를 통해 형상 변경 $\rightarrow$ 해석 $\rightarrow$ 보정 피드백 루프를 자율적으로 가동할 수 있는 미래 인프라 확보.

### 위험 요소 및 완화 대책 (Risks & Mitigations)
* **위험**: FieldCraft의 수치적 오차 또는 비선형성 처리 한계로 인한 잘못된 설계 판단.
  * **완화**: FieldCraft의 해석 결과는 '스크리닝' 목적으로만 활용하며, 중요한 설계 결정은 Abaqus `.inp` 덱을 통한 교차 검증을 필수화함.
* **위험**: MCP 통신 중 타임아웃 또는 형상 연산 오류로 인한 에이전트 세션 블로킹.
  * **완화**: SolidCraft의 `control.pending` 긴 요청 처리 프로토콜 및 읽기 전용 검증 도구 분리 운용.

---

## 6. 결론 및 승인 요건 (Approval Criteria)
본 ADR은 Phase 1 기술 분석 문서 4종([SOLIDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/SOLIDCRAFT_TECHNICAL_ASSESSMENT.md), [FIELDCRAFT_TECHNICAL_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/FIELDCRAFT_TECHNICAL_ASSESSMENT.md), [MCP_INTEGRATION_ASSESSMENT.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/MCP_INTEGRATION_ASSESSMENT.md), [MAJN_PILOT_VALIDATION_PLAN.md](file:///Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/MAJN_PILOT_VALIDATION_PLAN.md))의 완료와 함께 인간 엔지니어의 최종 서명을 통해 승인됩니다.
