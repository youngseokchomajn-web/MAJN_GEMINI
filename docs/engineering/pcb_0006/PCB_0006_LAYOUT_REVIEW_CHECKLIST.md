# [레이아웃 체크리스트] MAJN PCB #0006 — PCB Layout 및 고전류/EMC 설계 체크리스트
(MAJN PCB #0006 PCB Layout, High-Current & EMC Review Checklist)

- **문서 식별자**: `PCB_0006_LAYOUT_REVIEW_CHECKLIST`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **적용 대상**: 차기 제어 보드 PCB #0006 아트워크 검토

---

## 1. 4층 기판 표준 스택업 (Stackup Specification)

JLC04161H-7628 표준 4층 스택업 ($1.6\text{ mm}$ 두께, $1\text{ oz}$ 동박):

```
Layer 1 (Top Layer):      35µm (1 oz) 구리 ─── 부품 실장 (단일면 SMT), 신호 및 고전류 파워
Dielectric 1 (Prepreg):  0.2104mm (7628 Prepreg)
Layer 2 (Inner Layer 1): 35µm (1 oz) 구리 ─── GND 무손실 완전 접지 플레인 (Solid Plane)
Core Dielectric:         1.0650mm (FR-4 Core)
Layer 3 (Inner Layer 2): 35µm (1 oz) 구리 ─── VBUS, PVDD 12V 전원 플레인 및 보조 신호
Dielectric 2 (Prepreg):  0.2104mm (7628 Prepreg)
Layer 4 (Bottom Layer):   35µm (1 oz) 구리 ─── 보조 접지 및 비드 필터링 귀환, 부품 없음
```

---

## 2. 레이아웃 검토 체크리스트

| 검토 영역 | 체크 항목 | 설계 기준 (Design Rules) | 중요도 | 상태 |
|:---|:---|:---|:---:|:---:|
| **고전류 경로** | VBUS 5V 배선 폭 | 최소 배선폭 $\ge 1.5\text{ mm}$ (2A continuous, $\Delta T < 10^\circ\text{C}$) | CRITICAL | **PENDING** |
| | PVDD 12V 배선 폭 | 최소 배선폭 $\ge 1.2\text{ mm}$ (1.5A peak, $\Delta T < 10^\circ\text{C}$) | CRITICAL | **PENDING** |
| | 전원/접지 비아 개수 | 고전류 경로 비아 1개당 정격 1A $\rightarrow$ 분기점마다 **2개 이상 병렬 비아** 배치 | MAJOR | **PENDING** |
| **스위칭 전원 (MP3426)** | 스위치 노드(SW) 면적 | U3 Pin 14 $\rightarrow$ L1 $\rightarrow$ D3 사이 구리 면적을 **최소화**하여 방사 노이즈 차단 | CRITICAL | **PENDING** |
| | 입력 커패시터 근접도 | C5(10µF)를 MP3426 입력 핀과 GND 핀 바로 옆에 최단 거리 배치 | CRITICAL | **PENDING** |
| | 피드백(FB) 배선 격리 | R1/R2 피드백 트레이스를 SW 고전압 노드 및 인덕터로부터 완전 이격(차폐) | MAJOR | **PENDING** |
| **오디오 앰프 (TAS5805M)**| PVDD 디커플링 근접도 | C6/C7 및 C8/C9 MLCC를 U4 PVDD 핀(Pin 15, 16, 27, 28)에 초밀착 배치 | CRITICAL | **PENDING** |
| | BTL 출력 대칭성 | OUT_A/B 및 OUT_C/D 차동 배선의 길이/폭 대칭 유지 ($\Delta L < 1\text{ mm}$) | MAJOR | **PENDING** |
| | 서멀 패드 비아 어레이 | U4 파워패드 하부에 **$\phi 0.3\text{ mm}$ 열 비아(Thermal Via) 9개(3x3)** 배치 | CRITICAL | **PENDING** |
| **RF 및 안테나 (ESP32)** | u.FL 주변 Keepout | u.FL 커넥터 주변 15mm 영역 모든 레이어에 구리 패턴 및 비아 금지 | MAJOR | **PENDING** |
| | 모듈 실크스크린 | 19.2mm 길이의 -32UE 전용 실크 외곽선 적용 (빈 영역 노출 제거) | MINOR | **PENDING** |
| **신호 무결성 (SI)** | I2S 오디오 버스 | BCLK, LRCLK, DOUT 트레이스를 GND 플레인 위로 최단 거리 라우팅 | MAJOR | **PENDING** |
| | I2C 버스 배선 | SDA/SCL 배선에 4.7k 풀업 인접 배치, 고주파 스위칭 노드와 교차 금지 | MAJOR | **PENDING** |
| | IMU SPI 버스 | SPI_SCLK(18) 라인 링잉 방지 및 직교 라우팅 | MAJOR | **PENDING** |
| **기구 인터페이스** | 마운팅 홀 클리어런스 | MH1~4 주변 반경 5.0mm 이내 부품 및 배선 배치 금지 (와셔 간섭 방지) | CRITICAL | **PENDING** |
| | 단일면 SMT 준수 | Bottom 면 부품 개수 **0개 (100% Top 실장)** 유지 | CRITICAL | **PENDING** |
