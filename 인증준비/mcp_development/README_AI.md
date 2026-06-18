# EasyEDA Pro AI 자동 설계 파이프라인 개발 환경 구축 가이드 (README_AI.md)

이 문서는 다른 컴퓨터에서 AI 에이전트가 본 프로젝트의 EasyEDA Pro 자동 설계 및 DRC 검증 파이프라인을 이어서 개발하고 실행할 수 있도록 환경 구축 절차를 안내합니다. AI 에이전트는 이 지침을 순서대로 읽고 명령어를 실행하십시오.

---

## 1. 시스템 아키텍처

본 프로젝트는 AI 에이전트와 로컬 EasyEDA Pro 에디터 간의 양방향 통신을 기반으로 작동합니다.

```text
┌───────────────────────┐   HTTP POST (execute)  ┌──────────────────┐   WebSocket   ┌─────────────────────┐
│  AI Agent / Python    │ ─────────────────────> │  Bridge Server   │ <───────────> │ EasyEDA Pro 에디터  │
│ (run_mcp_design_flow) │ <───────────────────── │ (Node.js/49620)  │               │ (run-api-gateway)   │
└───────────────────────┘     Execute Response   └──────────────────┘               └─────────────────────┘
```

---

## 2. 사전 준비 사항

설치를 진행하기 전에 다른 PC에 아래 소프트웨어가 설치되어 있어야 합니다.
1. **EasyEDA Pro 데스크톱 클라이언트** (혹은 웹 브라우저 에디터 사용 가능)
2. **Node.js** (v16 이상 권장)
3. **Python 3** (v3.8 이상 권장)

---

## 3. 개발 환경 구축 단계 (AI 에이전트용 실행 지침)

### Step 1. EasyEDA Pro 플러그인(확장) 설치
1. EasyEDA Pro 에디터를 실행합니다.
2. 상단 메뉴의 **플러그인/확장 관리자**에서 `run-api-gateway`를 검색하여 설치하거나, 다음 URL에서 확장을 다운로드하여 로드합니다:
   - https://ext.lceda.cn/item/oshwhub/run-api-gateway
3. 플러그인이 로드되면 에디터가 로컬 포트(`49620~49629`)를 스캔하여 브릿지 서버와의 연결을 대기합니다.

### Step 2. Bridge Server 구동 (Node.js)
1. `easyeda-api-skill` 디렉토리로 이동하여 의존성 라이브러리를 설치합니다.
   ```bash
   cd easyeda-api-skill
   npm install
   ```
2. Bridge Server를 구동합니다. 이 서버는 파이썬 스크립트와 EasyEDA Pro 클라이언트를 중계합니다.
   ```bash
   npm run server
   # 또는 직접 실행: node scripts/bridge-server.mjs
   ```
3. 서버가 시작되면 `http://localhost:49620`에서 연결을 수신 대기하며, EasyEDA Pro 에디터와 웹소켓 핸드셰이크가 이루어집니다.

### Step 3. Python 실행 환경 확인
자동 설계 스크립트는 표준 라이브러리(`urllib`, `json`, `math`, `base64`, `os`, `sys` 등) 위주로 작성되어 별도의 복잡한 패키지 설치가 요구되지 않습니다. 다만, 실행 전 Bridge Server가 정상 작동하는지 확인하십시오.
* **서버 헬스체크 확인 명령어**:
  ```bash
  curl http://localhost:49620/health
  ```

---

## 4. 파이프라인 및 도구 실행 명령어

모든 명령은 프로젝트 루트 디렉토리(`mcp_development`)에서 실행해야 합니다.

### 1) 자동 부품 배치, 오토라우팅 및 설계 구축 실행
설계 정의 데이터(`mcp_design_flow.json`)를 바탕으로 에디터에 부품을 배치하고 네트 연결 및 레이아웃을 생성합니다.
```bash
python3 run_mcp_design_flow.py
```

### 2) 자체 기하학적 DRC 및 내장 DRC 검증 실행
설계 정합성, 클리어런스 충돌 및 에디터 내부 DRC 결과를 검증하여 요약 리포트를 출력합니다.
```bash
python3 run_full_drc.py
```

### 3) 거버(Gerber) 제조 파일 내보내기
설계 완료된 PCB의 거버 파일을 `.zip` 압축 파일로 다운로드하여 로컬에 저장합니다.
```bash
python3 run_export_gerber.py
```
* **출력 파일**: `Gerber_Output.zip` (프로젝트 루트에 저장)

---

## 5. 핵심 파일 설명

* **`mcp_design_flow.json`**: 부품 좌표, 각도, LCSC ID, 네트리스트 정보, Clearance 제약 조건 등이 정의된 설정 파일.
* **`easyeda_mcp_client.py`**: Bridge Server를 통해 EasyEDA JS API를 실행하는 래퍼 클래스.
* **`mcp_drc_engine.py`**: 오프라인에서 트랙 교차 및 핀-트랙 클리어런스를 기하학적으로 연산하는 검증 엔진.
* **`run_export_gerber.py`**: 에디터에서 완성된 거버 파일을 추출하는 실행 스크립트.

---

## 6. 에러 대응 및 팁 (Troubleshooting)

* **Bridge Server 연결 실패**: 에디터가 백그라운드에서 실행 중인지, `run-api-gateway` 확장이 활성화되어 있는지 확인하십시오.
* **부품 배치 오류 (`place_component` 실패)**:
  * 에디터의 '라이브러리(Library)' 패널(단축키 `Shift+F`)을 열고, `mcp_design_flow.json`에 정의된 LCSC ID를 한 번 검색하여 에디터 로컬 캐시에 등록해야 자동 배치가 원활히 작동합니다.
* **동박 미반영**: 배선이나 동박이 화면 상에서 업데이트되지 않았다면 EasyEDA Pro 에디터에서 **`Shift + B`**(동박 재구축)를 눌러 수동 갱신을 수행하십시오.
