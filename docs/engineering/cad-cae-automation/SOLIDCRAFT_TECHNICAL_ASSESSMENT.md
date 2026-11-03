# SolidCraft 기술 분석 및 MAJN 적용성 검토 보고서

* **문서 번호**: TR-CAD-001
* **작성일**: 2026-11-03
* **분석 대상**: Tangency Labs SolidCraft (`tangency-labs/solidcraft`)
* **목적**: MAJN 스마트 배시넷 기구 설계의 3D 디지털 트윈화 및 MCP 기반 CAD 자동화 타당성 평가

---

## 1. 개요 및 릴리스 현황 (Overview & Release Status)

### 1.1. 프로젝트 정체성 및 아키텍처
SolidCraft는 Tangency Labs에서 **Pure Rust**로 개발 중인 오픈소스 파라메트릭 3D CAD 애플리케이션입니다. Autodesk Fusion 360이나 Onshape와 같은 히스토리 기반 피처 모델러를 지향하며, 안전성(Memory Safety), 결정론적(Deterministic) 연산, 그리고 **AI 에이전트 연동(Native MCP 지원)**을 핵심 차별점으로 두고 있습니다.

* **기하 커널 (Geometry Kernel)**: 자체 B-rep 커널인 `SolidCore`를 탑재하고 있습니다. 이는 NVIDIA SMLib CAD 서브셋의 Rust 포팅 버전으로, 메모리 안전성과 WebAssembly(WASM) 호환성을 제공합니다.
* **실행 환경 및 플랫폼 지원**:
  * 데스크톱 GUI 애플리케이션 (macOS Metal 기반 렌더링, Linux/Windows Vulkan/DirectX)
  * 브라우저 기반 WebAssembly (WASM) 구동
  * 헤드리스(Headless) CLI (`solidcraft-cli`)

### 1.2. macOS 배포 현황 및 바이너리 접근성
* **공식 릴리스**: GitHub Releases 페이지를 통해 macOS Universal 배포판(`.dmg`, Apple Silicon M1/M2/M3/M4 및 Intel 64비트 동시 지원)을 제공합니다.
* **패키지 관리자**: Homebrew Cask를 공식 지원하여 다음 명령어로 즉시 설치 가능합니다:
  ```bash
  brew install --cask tangency-labs/tap/solidcraft
  ```
* **Phase 1 평가 결과**: 현재 개발 머신에 Rust/Cargo 컴파일러가 설치되어 있지 않더라도, 공식 prebuilt 바이너리(`.dmg` 또는 brew cask)를 통해 즉각적인 실행 파일 확보가 가능함을 확인했습니다.

---

## 2. B-rep 커널 및 파라메트릭 모델링 역량

### 2.1. 피처 기반 타임라인 및 파라메트릭 재연산
SolidCraft는 상용 CAD와 동일한 히스토리 기반 모델링 파이프라인을 지원합니다:
* **2D 스케치 및 기하 구속조건(Geometric Constraints)**: 점, 선, 호, 스플라인 생성 및 일치, 직교, 평행, 접함, 대칭, 치수 구속(Dimensioning).
* **3D 솔리드 피처(Features)**: 돌출(Extrude), 회전(Revolve), 스윕(Sweep), 로프트(Loft), 모따기(Chamfer), 필렛(Fillet), 쉘(Shell).
* **파라메트릭 의존성 트리**: 상위 스케치 치수나 매개변수(Parameter)가 변경되면 종속된 모든 솔리드 피처와 불리언 연산이 순차적으로 자동 재연산(Recompute)됩니다.

### 2.2. 표준 CAD 데이터 입출력 (STEP / IGES)
* **STEP (ISO 10303 AP203 / AP214 / AP242)**: B-rep 솔리드 형상 및 어셈블리 계층 구조를 보존하는 STEP 내보내기(Export) 및 가져오기(Import)를 지원합니다.
* **메쉬 포맷 (STL / OBJ / 3MF)**: 3D 프린팅 및 후속 CAE 메싱을 위한 표면 삼각화(Tessellation) 파일 내보내기 지원.
* **2D DXF**: 스케치 평면 및 단면 투영에 대한 DXF 내보내기 지원.

---

## 3. 어셈블리 및 간섭 검사 (Assembly & Clash Detection)

### 3.1. 멀티바디 및 조립체 메커니즘
* 멀티바디 파트 모델링뿐 아니라 복수 파트로 구성된 어셈블리(Assembly) 구조를 생성할 수 있습니다.
* **조인트(Joints)**: Rigid, Revolute, Slider, Cylindrical, Pin-Slot 등 6자유도 구속 메커니즘 지원.

### 3.2. 간섭 검사 (Clash Detection)
* 조립된 복수 파트 간의 물리적 체적 겹침(Volume Interference)을 자동으로 탐지합니다.
* 클리어런스(Clearance) 분석을 통해 지정된 안전 간격(예: PCB-기구 간 최소 $0.5\,\text{mm}$) 미달 부위를 경고합니다.
* **질량 특성(Mass Properties)**: 파트별 밀도 지정에 따른 체적, 표면적, 총 질량, 질량 중심(CoG), 관성 모멘트(MoI) 자동 산출.

---

## 4. MCP (Model Context Protocol) 인터페이스 및 에이전트 제어 구조

### 4.1. 통신 아키텍처 (`solidcraft-cli mcp`)
SolidCraft는 CLI 내부에 MCP 서버가 네이티브로 내장되어 있습니다:
* **전송 프로토콜**: `stdio` 기반의 JSON-RPC 2.0 통신.
* **실행 모드 2종**:
  1. **Headless 모드**: `solidcraft-cli mcp`를 단독 실행하여 백그라운드에서 메모리 상에 CAD 모델을 구축하고 STEP/이미지로 내보냄 (배치 자동화에 적합).
  2. **GUI Bridged 모드**: `solidcraft-cli mcp --connect 127.0.0.1:PORT` 플래그를 통해 데스크톱 실행 창과 실시간 소켓으로 연결되어, AI 에이전트가 내리는 모델링 명령이 화면에 실시간 시각화됨.

### 4.2. 보안 및 파일 시스템 샌드박싱
* 에이전트가 임의의 시스템 파일에 접근하거나 덮어쓰는 것을 방지하기 위해 `--allow-path` 플래그를 제공합니다.
  ```bash
  solidcraft-cli mcp --allow-path /Users/youngseok/Desktop/majn
  ```
* 허용된 디렉토리 외부로의 파일 쓰기 또는 읽기는 JSON-RPC 오류 코드로 차단됩니다.

### 4.3. 장시간 연산 및 오류 복구 메커니즘
* 대형 B-rep 불리언 연산이나 복잡한 필렛 연산이 60초를 초과하는 경우:
  * MCP 서버는 연결을 끊지 않고 `"still running"` 상태를 반환합니다.
  * 내부 제어 프로토콜(`control.pending`)을 통해 0.5초 주기로 최대 240초까지 진행 상태를 폴링한 후 최종 결과를 반환합니다.
* 연산 실패 시 트랜잭션 롤백(Rollback)을 지원하여 모델 타임라인이 오염되지 않습니다.

### 4.4. 에이전트 워크플로 스킬 (`skills/`)
저장소 내부에 에이전트 전용 가이드 스킬이 번들되어 있습니다:
* `solidcraft-modeling`: 신규 파트 및 스케치/돌출 기본 파이프라인.
* `solidcraft-editing`: 기존 파라메트릭 변수 수정 및 재생성.
* `solidcraft-checking`: 기하 무결성, 공차 검사, 간섭 검출, 리그레션 테스트.
* `solidcraft-mechanisms`: 조인트 정의 및 접촉 세트 구성.

---

## 5. MAJN 기존 기준선과의 연동성 검토

### 5.1. MAJN 기구 형상 SSOT 데이터 정합성
기존 프로젝트의 기구 설계 파일에서 확인된 정확한 수치는 다음과 같습니다:

| 항목 | MAJN SSOT 파일 | 정의된 공학적 수치 (Ground Truth) | 비고 |
| :--- | :--- | :--- | :--- |
| **하판 부품 외형** | `majn_housing/rev2_params.py` | 길이 $450.0\,\text{mm}$, 폭 $250.0\,\text{mm}$, 두께 $4.5\,\text{mm}$ (자작나무 합판) | **주의: 하우징 전체 외형이 아닌 하판 단품 치수임** |
| **코너 라운드** | `majn_housing/rev2_params.py` | 4개 모서리 외경 $R = 20.0\,\text{mm}$ | 모서리 코너 블록 12개와 일치 |
| **내부 캐비티 높이** | `majn_housing/rev2_params.py` | $H_{cavity} = 4.5\,\text{mm} \times 3\text{층} = 13.5\,\text{mm}$ | 사이드 레일 및 보스 블록 높이 |
| **전체 하우징 두께** | `majn_housing/rev2_params.py` | 상판(4.5) + 캐비티(13.5) + 하판(4.5) = **$22.5\,\text{mm}$** (가스켓 압축 시 23.5mm) | 단일 판재가 아닌 5단 적층 구조 |
| **외곽 체결 볼트** | `majn_housing/rev2_params.py` | M3 DIN 7991 접시머리 볼트 10개소<br>• 볼트 관통홀: $\varnothing 3.2\,\text{mm}$<br>• 카운터싱크 외경: $\varnothing 6.5\,\text{mm}$ (깊이 $1.7\,\text{mm}$) | `verify_rev2.py`에서 10개 좌표 검증 완료 |
| **PCB 장착 규격** | `ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md` | 80×60mm 4층 PCB, 4개 M2.5 스탠드오프<br>• 하부 볼트: M2.5×7mm DIN 7991 ($\varnothing 4.7\,\text{mm}$, 깊이 $1.6\,\text{mm}$)<br>• 스탠드오프: M2.5 황동 암-암, 외경 육각 4.7mm, 높이 5.0mm | `mcp_design_flow.json`과 1:1 대응 |

### 5.2. DXF 기반 워크플로와의 상호보완성
1. **Python 매개변수 $\rightarrow$ SolidCraft 파라미터 매핑**:
   `rev2_params.py`에 선언된 상수들을 SolidCraft 스크립트/MCP 명령 변수로 1:1 매핑하여 파라메트릭 3D 솔리드를 자동 생성할 수 있습니다.
2. **2D DXF 및 DRC 검증 도구 보존**:
   SolidCraft에서 생성된 하판 바닥면을 DXF로 추출했을 때, 기존 `verify_rev2.py` 검증 스크립트(살 두께 $\ge 3.0\,\text{mm}$, 카운터싱크 마진 $\ge 2.5\,\text{mm}$, 볼트 좌표 10개 일치)를 통과하는지 회귀 검증(Regression Test)할 수 있습니다.

---

## 6. 기술 검토 종합 매트릭스

| 검토 항목 | 확인된 사실 (Ground Truth) | 공식 문서 근거 | 미확인 사항 (TBD / Gap) | MAJN 적용성 | 검증 방법 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **설치 및 배포** | macOS Universal 배포판(`.dmg`) 및 Homebrew Cask 제공 확인. | GitHub Releases, `solidcraft.io` | 로컬 터미널 환경에서 cask 설치 시 Gatekeeper 권한 요구 여부. | **적용 매우 용이** (Rust 설치 불필요). | `brew install --cask` 또는 `.dmg` 마운트 테스트. |
| **기하 커널 (B-rep)** | Pure Rust 기반 `SolidCore` 커널. 스케치/피처 히스토리 지원. | `crates/solidcore`, README | 복잡한 3D 곡면(NURBS 스플라인)의 연산 안정성. | **적합** (MAJN은 프리즘/카운터싱크 위주의 형상). | 4.5T 하판 및 90도 카운터싱크 홀 10개 모델링 테스트. |
| **어셈블리 & 간섭** | 멀티바디 조립, 부품 간 Clash Detection 기능 지원. | `skills/solidcraft-mechanisms` | 대형 어셈블리(부품 50개 이상) 시 실시간 간섭 검사 성능. | **핵심 필요** (하판-스탠드오프-PCB 부품 3D 간섭 사전 검출). | ECO-001 체결부(하판 + M2.5 황동너트 + PCB) 간섭 체크. |
| **데이터 호환성** | STEP (AP203/214), IGES, STL, 2D DXF 내보내기 지원. | README, `crates/io` | FieldCraft 및 Abaqus/CAE에서 STEP 임포트 시 서피스 결함(Stitching error) 발생 여부. | **필수적** (FieldCraft로 기하 형상 전달 포맷). | SolidCraft 출력 STEP $\rightarrow$ FieldCraft/Abaqus 로딩 무결성 검사. |
| **MCP 제어성** | `solidcraft-cli mcp` stdio JSON-RPC 2.0 지원. Headless 및 GUI Bridged 모드 제공. | `docs/mcp.md` | Antigravity MCP 클라이언트 설정과의 파라미터 매핑 호환성. | **혁신적** (Gemini가 직접 기구 파라미터 수정 가능). | `stdio` 기반 `list_tools` 호출 및 스키마 응답 확인. |

---

## 7. 결론 및 권고사항 (Recommendation)
* **결론**: SolidCraft는 MAJN의 기구 설계를 2.5D DXF에서 3D 파라메트릭 B-rep 디지털 트윈으로 격상시키는 데 기술적으로 완벽히 부합합니다.
* **권고**:
  1. 전체 하우징 모델링에 앞서, **Pilot 1 (ECO-001 PCB 장착 구조)**를 대상으로 SolidCraft 파라메트릭 모델링 및 STEP 내보내기를 검증할 것.
  2. 설치는 Rust 컴파일이 아닌 **Homebrew Cask / 공식 `.dmg` 바이너리를 최우선으로 활용**할 것.
