# CAD/CAE 도구의 MCP 연동 및 에이전트 제어 아키텍처 검토서

* **문서 번호**: TR-MCP-001
* **작성일**: 2026-11-03
* **분석 대상**: Model Context Protocol (MCP) in SolidCraft & FieldCraft
* **목적**: Gemini / Antigravity 환경에서 CAD/CAE 도구를 안전하고 자율적으로 제어하기 위한 프로토콜 인터페이스 분석

---

## 1. 개요 및 통신 프로토콜 (Protocol Architecture)

### 1.1. 표준 전송 규격: `stdio` 기반 JSON-RPC 2.0
SolidCraft와 FieldCraft는 Anthropic 및 오픈소스 진영의 표준 규격인 **Model Context Protocol (MCP)**을 네이티브로 구현하고 있습니다.

* **전송 계층**: 표준 입출력(`stdio`) 스트림.
* **메시지 포맷**: JSON-RPC 2.0 사양 준수.
* **실행 명령어**:
  * SolidCraft MCP 서버: `solidcraft-cli mcp`
  * FieldCraft MCP 서버: `fieldcraft-cli mcp`
* **엔진 통일성 (Engine Command Parity)**:
  * MCP 서버가 호출하는 도구(Tool)들은 내부 CAD/CAE 코어 엔진의 기본 명령(Command)과 100% 동일한 함수를 호출합니다.
  * GUI 툴바 클릭, 파이썬 스크립트 실행, 에이전트 MCP 호출이 모두 동일한 내부 트랜잭션을 거치므로, 비정상적인 백도어나 팝업 블로킹 없이 결정론적(Deterministic)으로 실행됩니다.

---

## 2. 듀얼 실행 모드 분석: Headless vs GUI Bridged

SolidCraft와 FieldCraft는 에이전트의 동작 환경에 따라 2가지 실행 모드를 제공합니다:

```
[모드 1: Headless 모드 (CI/CD 및 배치 실행)]
Gemini / Antigravity  ──stdio (JSON-RPC)──>  solidcraft-cli mcp (독립 프로세스)
                                              └── 메모리 상 B-rep 모델링 & STEP 출력

[모드 2: GUI Bridged 모드 (인간-AI 협업 실시간 시각화)]
Gemini / Antigravity  ──stdio (JSON-RPC)──>  solidcraft-cli mcp --connect 127.0.0.1:49810
                                                                   │ (Local Socket)
                                                                   ▼
                                             SolidCraft.app 데스크톱 GUI 창
                                             (에이전트 조작 과정 화면 실시간 렌더링)
```

| 비교 항목 | Headless 모드 (`solidcraft-cli mcp`) | GUI Bridged 모드 (`--connect 127.0.0.1:PORT`) |
| :--- | :--- | :--- |
| **GUI 창 표시** | 화면에 아무것도 뜨지 않음 (백그라운드) | 로컬 데스크톱 앱 창이 열리고 실시간 조작 시각화 |
| **GPU 자원 소모** | 최소화 (렌더링 뷰포트 생략) | Metal GPU 렌더링 파이프라인 가동 |
| **사용 사례** | Git 커밋 전 자동 DRC 검증, 야간 배치 해석, CI/CD | 에이전트와 실시간 대화형 페어 프로그래밍, 설계 확인 |
| **MAJN 권고** | **Phase 1~2 초기 검증 시 GUI Bridged 권장**<br>(형상 왜곡 및 간섭을 엔지니어가 눈으로 직접 확인) | **Phase 4 정식 파이프라인 승격 후 Headless 전환** |

---

## 3. 보안 샌드박싱 및 경로 접근 제어 (`--allow-path`)

AI 에이전트가 CAD/CAE 도구를 조작할 때 시스템의 다른 중요 파일(기존 소스코드, 시스템 라이브러리)을 훼손하지 않도록 엄격한 파일 시스템 격리가 제공됩니다:

* **경로 화이트리스트 플래그**: `--allow-path <ABSOLUTE_PATH>`
  * 예시 실행:
    ```bash
    solidcraft-cli mcp --allow-path /Users/youngseok/Desktop/majn/docs/engineering/cad-cae-automation/sandbox
    ```
* **동작 원칙**:
  * 에이전트가 지정된 디렉토리 외부의 경로로 STEP 내보내기, 파일 로딩, 스크립트 실행을 시도할 경우, MCP 서버는 즉시 에러 코드(`-32602: Invalid params / Path not allowed`)를 반환하며 실행을 거부합니다.
  * 기존 MAJN 형상 SSOT 파일(`rev2_params.py`, `build_rev2_dxf.py`)을 덮어쓰지 못하도록 샌드박스 폴더 내부로만 출력을 제한할 수 있습니다.

---

## 4. 장시간 연산(Long-Running) 및 오류 복구 메커니즘

유한요소해석(FEA) 및 복잡한 B-rep 지오메트리 연산(Fillet, Shell, Boolean)은 수십 초 이상 소요될 수 있으며, 일반적인 MCP 타임아웃(기본 60초)을 초과할 위험이 있습니다.

### 4.1. 비동기 폴링 프로토콜 (`control.pending`)
1. 에이전트가 형상 생성 또는 메싱/해석 명령을 송신합니다.
2. 실행 시간이 60초를 경과하면, 서버는 세션을 강제 종료하지 않고 **`"still running"` 상태 코드**를 반환합니다.
3. MCP 브릿지는 내부 제어 채널(`control.pending`)을 통해 0.5초 간격으로 진행 상황을 주기적으로 폴링합니다.
4. 최대 **240초(4분)**까지 백그라운드 연산을 유지하며, 완료 시 최종 해석 결과(응력, 변위 JSON)를 수신하여 에이전트에게 전달합니다.

### 4.2. 트랜잭션 롤백 및 세션 복구
* 연산 도중 기하 오류(Geometry Kernel Non-manifold error)나 메싱 발산이 발생하면, 해당 연산 이전의 피처 타임라인 체크포인트로 **자동 롤백(Rollback)**됩니다.
* 모델 트리가 오염되지 않은 상태를 유지하므로, 에이전트가 이전 정상 상태에서 파라미터를 보정하여 재시도할 수 있습니다.

---

## 5. Antigravity / Gemini 환경 연동 구성 방안

### 5.1. MCP 서버 등록 설정 (Concept Blueprint)
Antigravity 환경의 설정 파일 또는 Claude Desktop 설정(`claude_desktop_config.json`)과 동일한 규격으로 등록할 수 있습니다:

```json
{
  "mcpServers": {
    "solidcraft": {
      "command": "/Applications/SolidCraft.app/Contents/MacOS/solidcraft-cli",
      "args": [
        "mcp",
        "--allow-path",
        "/Users/youngseok/Desktop/majn"
      ]
    },
    "fieldcraft": {
      "command": "/Applications/FieldCraft.app/Contents/MacOS/fieldcraft-cli",
      "args": [
        "mcp",
        "--allow-path",
        "/Users/youngseok/Desktop/majn"
      ]
    }
  }
}
```

### 5.2. 도구(Tools) 권한 분리 원칙
에이전트의 안정적인 제어를 위해 도구군을 다음과 같이 2개 레벨로 분리 운용해야 합니다:

1. **안전한 읽기/검증 도구 (Read-Only / Safe Tools)**:
   * `inspect_geometry`: 파트 치수, 바운딩 박스, 체적 조회.
   * `detect_clash`: 부품 간 간섭 부피 및 최소 간격 조회.
   * `read_fe_results`: 기 계산된 해석 결과(최대 응력, 변위, 고유진동수) 조회.
   * *특징*: 모델을 변경하지 않으므로 무조건 자동 승인 가능.
2. **상태 변경/생성 도구 (Mutating Tools)**:
   * `create_feature`, `modify_parameter`: 파라미터 변경 및 형상 재연산.
   * `run_mesh_and_solve`: 메쉬 생성 및 솔버 구동.
   * `export_step`, `export_abaqus_deck`: 파일 시스템에 파일 생성.
   * *특징*: 지정된 샌드박스 디렉토리 내부 쓰기만 허용.

---

## 6. 기술 검토 종합 매트릭스

| 검토 항목 | 확인된 사실 (Ground Truth) | 공식 문서 근거 | 미확인 사항 (TBD / Gap) | MAJN 적용성 | 검증 방법 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **통신 규격** | stdio JSON-RPC 2.0 프로토콜 공식 채택. | `docs/mcp.md` | Gemini 환경과의 stdin/stdout 버퍼링 이슈 여부. | **매우 높음** (Antigravity 표준 MCP 규격 일치). | 터미널 파이프를 통한 기본 `ping` 및 `initialize` 핸드셰이크 테스트. |
| **실행 모드** | Headless 및 GUI Bridged (`--connect`) 듀얼 모드 지원. | `docs/mcp.md` | 로컬 소켓 포트 충돌 시 자동 재할당 기능 여부. | **최적** (인간 엔지니어가 실시간 화면 확인 가능). | 데스크톱 앱 실행 후 `--connect 127.0.0.1:PORT` 연결 시험. |
| **경로 보안** | `--allow-path` 플래그로 파일 시스템 접근 디렉토리 격리. | `docs/mcp.md` | 심볼릭 링크(Symlink) 경로 추적 차단 여부. | **필수적** (기존 SSOT 파일 보호 완벽 달성). | 허용되지 않은 상위 디렉토리 파일 생성 시도시 거부 에러 확인. |
| **장시간 연산** | 60초 초과 시 `"still running"` 반환, `control.pending` 240초 폴링. | `docs/mcp.md` | 대규모 유한요소 메싱(10만 절점 이상) 시 240초 초과 타임아웃 대책. | **충분함** (MAJN 파일럿 모델은 수초 이내 연산 완료 예상). | 고밀도 메쉬 생성 명령으로 타임아웃 폴링 시퀀스 재현. |
| **에러 복구** | 실패 시 이전 피처 트리 체크포인트 자동 롤백. | `skills/solidcraft-checking` | 솔버 비정상 종료 시 메모리 누수 또는 좀비 프로세스 잔존 여부. | **안전성 확보** (연속 작업 시 세션 유지 가능). | 의도적인 형상 간섭/발산 조건 주입 후 롤백 무결성 확인. |

---

## 7. 결론 및 권고사항 (Recommendation)
* **결론**: SolidCraft와 FieldCraft의 MCP 아키텍처는 EasyEDA Pro 브릿지에 버금가는 정밀하고 안전한 제어 인터페이스를 갖추고 있습니다.
* **권고**:
  1. 초기 검증 단계에서는 에이전트가 화면을 보면서 작업할 수 있도록 **GUI Bridged 모드로 연동**할 것.
  2. 에이전트의 작업 공간을 `docs/engineering/cad-cae-automation/sandbox/`로 엄격히 한정하여 기존 SSOT 파일 훼손을 100% 방지할 것.
