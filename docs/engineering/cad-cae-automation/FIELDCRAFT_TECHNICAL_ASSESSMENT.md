# FieldCraft 기술 분석 및 CAE 해석 정합성 검토 보고서

* **문서 번호**: TR-CAE-001
* **작성일**: 2026-11-03
* **분석 대상**: Tangency Labs FieldCraft (`tangency-labs/fieldcraft`)
* **목적**: MAJN 스마트 배시넷 구조 강성 및 모달 해석 타당성, Abaqus 호환성 및 한계 검증

---

## 1. 개요 및 개발 현황 (Overview & Status)

### 1.1. 프로젝트 아키텍처 및 철학
FieldCraft는 Tangency Labs에서 **Pure Rust**로 처음부터 구축 중인 차세대 오픈소스 컴퓨터 응용 공학(CAE) 및 다중물리 시뮬레이션 플랫폼입니다. SolidCraft의 3D CAD B-rep 형상을 받아 물리 검증(유한요소해석, 열전달, Lattice Boltzmann CFD)을 수행합니다.

* **표준 레퍼런스 모델**: 산업 표준 해석 도구인 **Dassault Systèmes Abaqus/CAE**를 기능 범위, 요소 라이브러리, 키워드 체계의 벤치마크 레퍼런스로 삼고 있습니다.
* **실행 환경**:
  * 데스크톱 GUI (macOS 환경에서 Metal 네이티브 백엔드 구동, Linux/Windows Vulkan)
  * 헤드리스 CLI (`fieldcraft-cli`)
  * 네이티브 MCP 서버 (`fieldcraft-cli mcp`)

### 1.2. 릴리스 및 바이너리 배포 현황
* macOS 11 이상 지원 Universal 배포판(`.dmg`, Apple Silicon & Intel)이 공식 CI를 통해 빌드 및 공증(Notarization)되어 배포되고 있습니다.
* 따라서 Rust/Cargo 컴파일러 없이도 공식 prebuilt 바이너리를 통해 즉각적인 테스트가 가능합니다.

---

## 2. 요소 라이브러리 및 메싱 역량 (README vs parity.md 대조 분석)

### 2.1. 유한요소(FE) 라이브러리 구현 상태
FieldCraft 내부 유한요소 엔진(`crates/fem`) 및 요소 명세는 다음과 같습니다:

| 요소 계열 | 내부 요소 명칭 | Abaqus 매핑 | 지원 수치 정식화 (Formulation) | 구현 상태 |
| :--- | :--- | :--- | :--- | :--- |
| **1차 사면체** | `Tet4` | `C3D4` | 4절점 등매개변수 1차 사면체 (전단 잠김 주의) | **완료 (Stable)** |
| **2차 사면체** | `Tet10` | `C3D10` | 10절점 2차 사면체 (굽힘 해석 표준) | **완료 (Stable)** |
| **1차 육면체** | `Hex8` | `C3D8` / `C3D8R` | 완전적분(Full), 비적합 모드(Incompatible Modes), 균일변형률(1점 적분 + Hourglass 제어) | **완료 (Stable)** |
| **2차 육면체** | `Hex20` | `C3D20` / `C3D20R` | 20절점 2차 벽돌 요소 | 부분 지원 / 검증 중 |
| **쉘/보 요소** | `Shell4`, `Beam2` | `S4R`, `B31` | 감차적분 쉘 요소, 티모셴코 1D 보 요소 | 완료 |

### 2.2. 메싱(Meshing) 기능의 실제 상태 (핵심 구별)
* **사면체(Tet) 자동 메싱**:
  * 3D CAD B-rep 모델의 서피스 삼각화 후 내부 체적에 대한 Delaunay 기반 사면체 메싱은 **완전 자동화되어 안정적으로 동작**합니다.
* **육면체(Hex) 메싱의 실질적 한계 (README vs `docs/parity.md` 대조)**:
  * README는 다양한 Hex 메싱 기법을 소개하고 있으나, 상세 체크리스트(`docs/parity.md`)와 로드맵을 확인한 결과 **"임의의 복잡한 3D 비정형 형상에 대한 완전 자동 Hex 메싱"은 미완성 상태**입니다.
  * 현재 실질적으로 가동 가능한 Hex 메싱은 직육면체 프리즘 영역 분할(Cartesian/Octree) 또는 단순 2.5D 돌출 스윕(Sweep) 형상에 국한됩니다.
  * **MAJN 판정**: 4.5T 하판 단품과 같은 2.5D 판재는 Hex8 스윕 메싱이 가능하지만, 카운터싱크 홀이나 스탠드오프 결합부 등 곡면 천이 구간은 **Tet10(2차 사면체) 메싱을 기본 전략으로 채택**해야 합니다.

---

## 3. 구조 해석 솔버 분석 (정적 및 모달 해석)

### 3.1. 선형 정적 해석 (Linear Static Analysis)
* 순수 Rust 희소 행렬(Sparse Matrix) 직접 솔버를 탑재하여, 다자유도(DoF) 모델의 변위 벡터 $\{u\}$, 반력 $\{R\}$, 폰 미세스(von Mises) 및 주응력(Principal Stress) 텐서를 안정적으로 계산합니다.

### 3.2. 고유진동수 해석 (Block Lanczos Modal Analysis)
* **알고리즘**: **Shift-Invert Block Lanczos** 알고리즘을 자체 구현했습니다.
  * 블록 크기: 6
  * 완전 재직교화(Full Reorthogonalization) 적용
  * 연산 방정식: $(K - \sigma M) \phi = \lambda M \phi$
  * 구속 구조물은 $\sigma = 0$, 자유 경계 구조물은 미소 음수 시프트를 적용하여 강체 모드(Rigid-body mode)를 분리.
* **출력 데이터**: 질량 정규화 모드 형상(Mass-normalized mode shape), 모달 참여 계수(Modal Participation Factors), 유효 질량(Effective Mass).
* **결과 내보내기**: VTU 포맷을 지원하여 ParaView 등 외부 후처리 도구에서 고유진동 모드 3D 시각화 가능.

### 3.3. ⚠️ 핵심 갭 분석: 모달 해석 $\ne$ Mode-based FRF 해석
**엔지니어링 실무에서 가장 중요한 구별점**입니다:

1. **고유진동수 해석 (Modal Analysis, 현재 지원)**:
   * 시스템의 질량 행렬 $[M]$과 강성 행렬 $[K]$로부터 비감쇠 고유진동수 $\omega_n$과 모드 형상 $\phi_n$을 도출하는 고윳값 해석(Eigenvalue problem)입니다.
2. **주파수 응답 해석 (Mode-based FRF / Steady-State Dynamics, 미지원)**:
   * 특정 주파수 대역(예: MAJN의 $30\sim 65\,\text{Hz}$ 바운싱 진동)에서 조화 가진 하중(Harmonic Excitation)이 가해졌을 때, 시스템의 변위/가속도 전달함수(FRF, Frequency Response Function)를 계산하는 해석입니다.
   * **로드맵 상태 확인**: FieldCraft 공식 로드맵(`docs/ROADMAP.md`)에서 조화 주파수 응답(Direct & Modal Steady-State Response)은 **마일스톤 M16 (개발 진행 중)**으로 분류되어 있습니다.
   * **물성 지원 한계**: 주파수 의존 감쇠(Frequency-dependent Damping), 재료 복소 탄성계수(Loss Factor $\eta$), 회전속도 의존 베어링 동특성(Speed-dependent Bearing Stiffness)은 **현재 지원되지 않습니다**.

---

## 4. Abaqus Input Writer (`crates/decks/src/abaqus.rs`) 매핑 및 한계

### 4.1. 덱 생성 구조 및 키워드 매핑
FieldCraft의 `crates/decks` 크레이트는 모델 데이터를 표준 솔버 덱(`.inp`)으로 변환합니다:

| FieldCraft 엔티티 | Abaqus 키워드 | 변환 매핑 무결성 |
| :--- | :--- | :--- |
| 절점 좌표계 | `*NODE` | 3차원 절대 좌표 $X, Y, Z$ 1:1 완벽 변환 |
| 요소 연결성 | `*ELEMENT, TYPE=...` | `Tet4` $\rightarrow$ `C3D4`, `Tet10` $\rightarrow$ `C3D10`, `Hex8` $\rightarrow$ `C3D8R`, `Shell4` $\rightarrow$ `S4R` |
| 재료 물성 | `*MATERIAL, NAME=...`<br>`*ELASTIC`<br>`*DENSITY` | 등방성 탄성계수 $E, \nu$ 및 밀도 $\rho$ 변환 지원.<br>※ 엔지니어링 상수(직교이방성)는 텍스트 파라미터 매핑 필요. |
| 경계 조건 | `*BOUNDARY` | 6자유도 구속 조건 매핑 지원 |
| 정적 해석 단계 | `*STEP`<br>`*STATIC`<br>`*CLOAD` / `*DLOAD` | 집중 하중 및 분포 압력 하중 변환 지원 |
| 모달 해석 단계 | `*STEP`<br>`*FREQUENCY`<br>`*END STEP` | 고유진동수 추출 횟수 및 주파수 범위 키워드 변환 지원 |

### 4.2. 엄격한 변환 철학: *"Refusing by name what it cannot express"*
FieldCraft의 덱 작성기는 모호한 특성을 임의로 왜곡하여 출력하지 않고, **Abaqus 문법으로 완벽히 표현할 수 없는 특성은 출력 단계에서 명시적으로 거부(Refuse with Error)**하도록 설계되어 있습니다:
* **비선형 접촉의 한계**: 볼트 머리와 판재 사이의 면대면 접촉(`*CONTACT PAIR`, `*SURFACE INTERACTION`)은 FieldCraft 덱 작성기가 완벽히 지원하지 못할 수 있으며, 이 경우 Rigid MPC(`*TIE`)로 대체되거나 에러가 반환됩니다.
* **복합재 적층(Composite Layup)**: 자작나무 합판의 다층 적층 섬유각 정의(`*SHELL SECTION, COMPOSITE`)는 단일 직교이방성 솔리드 물성으로 축약해야 합니다.

---

## 5. 검증 벤치마크 분석 (`docs/verification.md`)

* **벤치마크 결과**: 50개 검증 사례(NAFEMS 표준 문제 등)의 176개 물리량 중 **170개 통과(Pass), 6개 알려진 실패(Known Failures)** 기록.
* **알려진 실패 항목의 성격**:
  1. 극심한 기하 비선형성(Large Deformation Snap-through)에서의 수렴 지연.
  2. 복잡한 마찰 접촉(Friction Contact Penalty)에서의 접촉력 진동.
  3. 특정 좌굴(Buckling) 고윳값 해석의 모드 반전.
* **MAJN에의 시사점**: MAJN의 4.5T 하판 처짐 및 볼트 체결부 강성은 미소 변형 선형 영역($< 1.0\,\text{mm}$)에 해당하므로, 6개 실패 항목의 위험 영역을 회피할 수 있습니다.

---

## 6. 기술 검토 종합 매트릭스

| 검토 항목 | 확인된 사실 (Ground Truth) | 공식 문서 근거 | 미확인 사항 (TBD / Gap) | MAJN 적용성 | 검증 방법 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **메싱 (Meshing)** | Tet4/Tet10 자동 메싱 완전 지원. 임의 3D 형상에 대한 자동 Hex 메싱은 미완성. | `docs/parity.md`, `crates/fem` | 4.5T 합판의 두께 방향(Z축) 최소 요소 레이어 수 분할 제어성. | **높음** (하판은 Tet10 2차 요소로 메싱 권장). | STEP 파일 임포트 후 메쉬 생성 및 요소 품질(Aspect Ratio, Jacobian) 검사. |
| **선형 정적 해석** | 순수 Rust 직접 솔버. 변위, 응력, 반력 계산 완료. | README, `docs/verification.md` | 직교이방성(Orthotropic) 탄성 상수 9개 입력 UI/CLI 지원 여부. | **적합** (아기 체중 하중 하판 처짐 및 볼트 인발 응력 1차 스크리닝). | 아기 무게($70\,\text{N}$) 중앙 집중 하중 인가 후 최대 처짐 비교. |
| **모달 해석** | Shift-Invert Block Lanczos 알고리즘으로 고유진동수 및 모드 형상 산출. | `crates/solvers/modal.rs` | 구속 조건(10개 볼트 고정) 하에서의 고유진동수 수렴 오차. | **적합** ($30\sim 65\,\text{Hz}$ 대역 공진 모드 존재 여부 1차 탐색). | 자유단 및 단순 지지 평판 이론 고유진동수와의 비교 오차 검증. |
| **FRF / 감쇠** | Mode-based FRF 및 조화 응답은 로드맵 **M16** 상태 (미지원). 주파수 의존 감쇠 미지원. | `docs/ROADMAP.md` (M16) | 향후 M16 릴리스 일정 및 감쇠 행렬 정식화 방향. | **적용 불가** (Abaqus에 위임 필수). | FRF 및 가속도 응답 해석은 FieldCraft가 아닌 Abaqus에서 전담. |
| **Abaqus 연동** | `crates/decks/src/abaqus.rs`로 `.inp` 덱 출력. 미지원 엔티티 명시적 거부. | `crates/decks/src/abaqus.rs` | 생성된 `.inp` 파일이 Abaqus 2023/2024에서 구문 오류 없이 열리는지 여부. | **핵심 브릿지** (Abaqus 전처리 자동화의 핵심). | 생성된 `.inp` 파일을 CalculiX(`ccx`) 또는 Abaqus 솔버로 드라이런(dry-run) 실행. |

---

## 7. 결론 및 권고사항 (Recommendation)
* **결론**: FieldCraft는 **Abaqus의 완전 대체재가 될 수 없으며**, 그렇게 취급해서도 안 됩니다. 그러나 **"SolidCraft CAD 모델을 받아 자동으로 Tet10 메싱을 수행하고, 1차 정적 처짐/고유진동수를 스크리닝한 뒤, 산업 표준 Abaqus `.inp` 덱을 무결하게 뽑아내는 AI 프리프로세서"**로서는 최상의 가치를 제공합니다.
* **권고**:
  1. MAJN 하우징의 $30\sim 65\,\text{Hz}$ 진동 전달 함수(FRF) 및 감쇠 해석은 **반드시 Abaqus(Tier 4)에서 수행**할 것.
  2. FieldCraft는 1차 선형 정적 처짐 계산 및 Abaqus `.inp` 덱 생성 파이프라인으로 한정 운용할 것.
