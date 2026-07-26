# 📘 [마중 3D CAE 파이프라인] 전체 개발 및 구조 총정리 문서 (MAJN 3D CAE Summary)

마중 스마트 배시넷 하우징 3D CAE 간이 시뮬레이터부터 직교이방성 물리 연산, CalculiX Abaqus `.INP` 내보내기 브릿지까지의 **전체 개발 내역 및 아키텍처 총정리 마크다운 보고서**입니다.

---

## 📌 1. 프로젝트 개요 & 목적
* **프로젝트명**: 마중 스마트 배시넷 3D 박스 하우징 CAE 파이프라인 (MAJN Smart Bassinet CAE Pipeline)
* **목적**:
  1. 영아 재우기용 진동 모듈(Tectonic 익사이터)의 자작합판/ABS 박스 하우징 부착 시 **변위량($10\sim 12\,\mu\text{m}$ SVS 영유아 안전 달래기 진폭 달성 여부)** 정밀 추정.
  2. 하우징 공진 회피, 볼트 체결부 자가풀림($S < 1.0$) 수명 및 발열 오버플로우 사전 검증.
  3. B2B 렌탈 영업 및 투자자 피칭용 60fps 실시간 3D 관제 및 Abaqus 호환 `.INP` 인풋 파일 세대 연동.

---

## 🛠️ 2. 주요 개선 & 버그 교정 완료 내역 (Fix Log)

| 분류 | 항목 | 주요 개선 & 원인 해결 내역 | 관련 파일 |
|---|---|---|---|
| **사운드** | Web Audio ReferenceError 원복 | `audioFilterNode`, `audioGainNode` 선언 및 볼륨 슬라이더 `audioGainNode` 동기화, `stopAudio()` 완전 독립 분리 | `app.js` |
| **B2B 연동** | RentalRefurbishmentManager 연동 | 클래스명 오타 정정 및 `new RentalRefurbishmentManager(femEngine)` 인스턴스 정상 전달 | `index_pro.html` |
| **3D 조작** | Top View 360도 수직 짐벌락 해제 | `OrbitControls.minPolarAngle = 0.001`, `maxPolarAngle = Math.PI - 0.001`로 개방하여 전방향 무한 상하 드래그 회전 구현 | `fem_visualizer.js` |
| **발열 연산** | 190°C 오버플로우 온도 교정 | 익사이터 접촉 면적을 $1.54\text{cm}^2 \rightarrow 28\text{cm}^2$ (알루미늄 링 플랜지)로 교정하여 $29.9^\circ\text{C} \sim 34.8^\circ\text{C}$ 현실적 수치 보정 | `displacement_solver.js` |
| **물리 해석** | C3D10 2-Layer 휨 솔버 원복 및 이방성 휨 적용 | `c3d10_solver.js` 미선언 변수 `ReferenceError` 버그 완벽 복구, `D_ortho` 자작합판 결 방향 휨 강성 100% 정상 연동 | `c3d10_solver.js` |
| **브릿지** | CalculiX `.INP` 파일 생성 브릿지 | `[🔬 CalculiX FEA .INP 생성 및 벤치마크]` 버튼 클릭 시 Abaqus 규격 인풋 파일 동적 세대 및 벤치마크 미리보기 브릿지 구현 | `fem_wasm_solver.js` |

---

## 🏗️ 3. 핵심 시스템 아키텍처 (System Architecture)

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │                            [ MAJN 3D CAE 파이프라인 전체 아키텍처 ]                      │
 ├──────────────────────────┬──────────────────────────┬──────────────────────────┬─────────┤
 │ 1. UI / Controls         │ 2. 3D WebGL Engine       │ 3. FEA / Thermal Solvers │ 4. Output / Export     │
 │ • 3축 자유 치수 (W,L,H) │ • Three.js OrbitControls │ • C3D10 Solid Solver     │ • 2D Hotspot Contour   │
 │ • 자작합판/ABS 소재 선택 │ • (0,0,-H/2) 타겟 고정   │ • Mindlin Orthotropic    │ • 3D CAD (.OBJ) 내보내기│
 │ • 📍 S1 2D 센서 드래그   │ • 4종 뷰포트 컨투어 색상 │ • CalculiX .INP Bridge   │ • Abaqus .INP 내보내기 │
 └──────────────────────────┴──────────────────────────┴──────────────────────────┴─────────┘
```

---

## 🌐 4. 최신 라이브 웹 서비스 주소

* 🔬 **MAJN 3D CAE 마스터 시뮬레이터**: [https://243bf769.majn-bassinet-simulator.pages.dev/fem_simulator.html](https://243bf769.majn-bassinet-simulator.pages.dev/fem_simulator.html)
* 🏬 **MAJN Pro B2B 관제 스튜디오**: [https://243bf769.majn-bassinet-simulator.pages.dev/index_pro.html](https://243bf769.majn-bassinet-simulator.pages.dev/index_pro.html)
* 📂 **독립 코드 검토용 사본 상대 경로**: `./code_review_copy/`
