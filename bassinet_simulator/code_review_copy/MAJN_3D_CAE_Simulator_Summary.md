# 📘 [마중 3D CAE 파이프라인] 전체 개발 및 구조 총정리 문서 (MAJN 3D CAE Summary)

마중 스마트 배시넷 하우징 3D CAE 간이 시뮬레이터부터 산후조리원 $720 \times 390 \times 45\,\text{mm}$ 아크릴 핏팅, ESP32 SVS 5-Tone 임상 가진 알고리즘 이식, 2.5D 하이브리드 Shell 요소 보정 및 AI 다목적 최적화 탐색 엔진까지의 **전체 개발 내역 및 아키텍처 총정리 마크다운 보고서**입니다.

---

## 📌 1. 프로젝트 개요 & 목적
* **프로젝트명**: 마중 스마트 배시넷 3D 박스 하우징 CAE 파이프라인 (MAJN Smart Bassinet CAE Pipeline)
* **목적**:
  1. 산후조리원 표준 투명 아크릴 바스켓 카트($750 \times 420\,\text{mm}$) 인셋 규격인 **$720 \times 390 \times 45\,\text{mm}$ 완전 방수(IP67)** 하우징 핏팅.
  2. 영아 재우기용 진동 모듈(Tectonic 익사이터)의 자작합판/ABS 박스 하우징 부착 시 **변위량($10\sim 12\,\mu\text{m}$ SVS 영유아 안전 달래기 피크 진폭 달성 여부)** 정밀 추정.
  3. ESP32 펌웨어의 5-Tone 임상 가진 수식(`computeSVS`)을 이식하여 하우징 공진 회피, 볼트 체결부 자가풀림($S < 1.0$) 수명 및 발열 오버플로우 사전 검증.
  4. B2B 렌탈 영업 및 투자자 피칭용 60fps 실시간 3D 관제, AI 다목적 최적 탐색 엔진 및 Abaqus 호환 `.INP` 인풋 파일 세대 연동.

---

## 🛠️ 2. 주요 개선 & 버그 교정 완료 내역 (Fix Log)

| 분류 | 항목 | 주요 개선 & 원인 해결 내역 | 관련 파일 |
|---|---|---|---|
| **치수통일** | 산후조리원 720x390x45mm 규격 전파 | `loadConfig()`, `cad_assembler.js`, `index_pro.html`, `cad_viewer.html` 하드코딩 라벨 및 볼트/브래킷 3D 위치를 $720 \times 390 \times 45\,\text{mm}$에 맞춰 100% 안착 동기화 | `fem_engine.js`, `cad_assembler.js`, `cad_viewer.html`, `index_pro.html` |
| **AI 최적화**| 실시간 탐색 루프 구동 | `runAIOptimizer()` 더미 alert를 제거하고 실제 실소재 DB, 볼트 링 배열, 휨 변위, 안전율을 수치 탐색하는 다목적 최적화 알고리즘 구현 | `index_pro.html`, `fem_simulator.html` |
| **SVS 가진** | ESP32 펌웨어 5-Tone 수식 이식 | ESP32 `main.cpp`의 임상 가진 수식(`computeSVS`: 30Hz, 14.2Hz, 22.7Hz, 7.4Hz, 33.1Hz)을 `c3d10_solver.js`에 1:1 완벽 이식 | `c3d10_solver.js` |
| **데이터통일**| SVS 동적 변폭 & FRF 피크 포락선 동기화 | `calculateSensorFRF()`와 `getSensorTelemetry()`가 모두 `e.dynamicDeflections` 피크 포락선을 동일 참조하도록 바로잡아 요동 현상 완벽 제거 | `displacement_solver.js`, `c3d10_solver.js` |
| **B2B 렌탈** | RentalRefurbishmentManager UI 연동 | B2B 관제 스튜디오(`index_pro.html`)에 렌탈 리퍼비시 원가/시간 메트릭 카드 신설 및 동적 연동 | `rental_manager.js`, `index_pro.html` |
| **컨셉 비교** | ConceptEvaluator 동적 FEA 스케일 연동 | 실소재 및 하우징 치수 변경 시 4개 컨셉 지표(순수목재, EVA, L-브래킷, 하이브리드)가 FEM 수치에 연동되어 자동 재계산되도록 이식 | `concept_evaluator.js` |
| **코드클린** | `app.js` 변수 정리 | 안 쓰이던 미사용 변수 `gainNode` 선언 제거 | `app.js` |
| **Kbox교정** | 높이 의존 박스 강성 일반화 (v2) | 구 45mm 하우징 잔재 `Kbox=6.5` 고정값을 $K_{box}=1+5.5(H/45)$ 높이 의존식으로 교정(18mm→3.20). 임상 밴드 구동력 3.5N→**1.8N** 재산출, `run_ai_optimizer.py`를 웹 솔버와 정합 캘리브레이션 후 설계 제약 4종 하드 제약 탐색으로 최적 사양(자작합판 4mm 600×340×18) 재확증 | `fem_engine.js`, `c3d10_solver.js`, `run_ai_optimizer.py`, `fem_simulator.html` |

---

## 🏗️ 3. 핵심 시스템 아키텍처 (System Architecture)

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │                            [ MAJN 3D CAE 파이프라인 전체 아키텍처 ]                      │
 ├──────────────────────────┬──────────────────────────┬──────────────────────────┬─────────┤
 │ 1. UI / Controls         │ 2. 3D WebGL Engine       │ 3. FEA / Thermal Solvers │ 4. Output / Export     │
 │ • 720x390x45mm 산후조리원│ • Three.js OrbitControls │ • 2.5D Hybrid Shell/Solid│ • 2D Hotspot Contour   │
 │ • 자작합판/ABS 소재 선택 │ • (0,0,-H/2) 타겟 고정   │ • Mindlin Orthotropic    │ • 3D CAD (.OBJ) 내보내기│
 │ • 📍 S1 2D 센서 드래그   │ • 4종 뷰포트 컨투어 색상 │ • ESP32 5-Tone SVS Sync  │ • Abaqus .INP 내보내기 │
 └──────────────────────────┴──────────────────────────┴──────────────────────────┴─────────┘
```

---

## 🌐 4. 최신 라이브 웹 서비스 주소

* 🔬 **MAJN 3D CAE 마스터 시뮬레이터**: [https://ce2fcb50.majn-bassinet-simulator.pages.dev/fem_simulator.html](https://ce2fcb50.majn-bassinet-simulator.pages.dev/fem_simulator.html)
* 🏬 **MAJN Pro B2B 관제 스튜디오**: [https://ce2fcb50.majn-bassinet-simulator.pages.dev/index_pro.html](https://ce2fcb50.majn-bassinet-simulator.pages.dev/index_pro.html)
* 📂 **독립 코드 검토용 사본 상대 경로**: `./code_review_copy/`
