# MAJN PCB 재설계 v2 — Option 2 (회로도 유지, PCB 처음부터 클린 빌드)

작성 2026-06-22. 목표: Schematic1 유지, 새 PCB를 **근본 원인을 먼저 차단**하고 처음부터.
결과 기준: 4층, 전원 정폭, 네이티브 DRC 클린(또는 via-in-pad만 문서화), KC 적합.
프로젝트 `eaca910eadcb42049fff04c549930a59` / Board1_2 / Schematic1 uuid `1b62a2b269c7d7ab`.

---

## A. 실수·오류 전체 카탈로그 + 우회법 (모두 반영)

### 검증
| # | 실수/오류 | 우회법 |
|---|---|---|
| V1 | 자체 기하 도구(find_unrouted·conn3)가 레이어 무시 → "완료" 오판 | **네이티브 DRC `eda.pcb_Drc.check(true,false,true)`(verbose 필수)만 신뢰**. 자체도구는 보조참고만 |
| V2 | UI "Check DRC" 버튼 "All(0)" 신뢰 불가 | UI버튼 신뢰 금지. 브릿지 네이티브 DRC만 |
| V3 | 브릿지 DRC가 몇 회 후 120초 타임아웃(degrade) | 변경 다 모은 뒤 **재시작 직후 1회만** DRC |

### 브릿지 API
| # | 함정 | 우회법 |
|---|---|---|
| B1 | 라인 create는 `.done()` 호출해야 영속(없으면 유령) | 라인: `create()`+`await .done()` |
| B2 | 비아 `.done()`는 "对象参数不正确" 에러 | **비아: create만**(자동 커밋, .done() 금지) |
| B3 | 규칙쓰기 API 전부 no-op(setAsDefault/overwriteCurrent/saveRuleConfiguration) | 규칙은 **UI 대화상자**로만 |
| B4 | copyPcb/copyBoard/createNetClass no-op | importChanges 플로우 사용 |
| B5 | pour 직후 getCurrentRenderedAreaImage = 렌더러 멈춤 | pour 후 이미지캡처 금지. fill은 UI Shift+B |
| B6 | 재시작 후 브릿지가 빈/호스트 창에 바인딩 | 재시작 후 /health로 새 activeWindowId→WINID 갱신, UI로 PCB 열기 |

### EasyEDA 구조/규칙
| # | 함정 | 우회법 |
|---|---|---|
| S1 | Board=(회로도+PCB)쌍, createPcb=고아 | importChanges(회로도uuid)로 링크 |
| S2 | 규칙 활성이 "Two Layers"로 리셋(default는 Multiple) | 새 보드 UI에서 4층 프로파일 적용 시도 |
| S3 | Design Rule 대화상자 로딩 무한멈춤(PCB5 config 손상 의심) | **새 보드는 정상일 가능성** → Phase0서 즉시 확인. 안 되면 기본값(보수적,제조OK) 수용 |

### 풋프린트 (★핵심 근본원인)
| # | 문제 | 우회법 |
|---|---|---|
| F1 | U4 EP 열비아 넷없음(via-in-pad 플래그 근원), PCB서 수정 불가(재생성) | **풋프린트에서 EP비아 GND 확정**(또는 클린 재임포트로 GND 상속 확인) |
| F2 | U1 EP 열비아 넷없음 + 신호가 EP 위 배선 → 실제 클리어런스 | F1 동일 + **EP를 GND 확정 후 오토라우트**(라우터가 GND EP 위 신호 회피) |

### 배선/배치
| # | 실수 | 우회법 |
|---|---|---|
| R1 | 블라인드 수동배선(조밀)→577 클리어런스 | 조밀구역 수동배선 금지, **오토라우터** |
| R2 | 사후 전원 정폭→504 폭발 | **power-first** 또는 규칙 전원폭 후 오토라우트 |
| R3 | 한 층(Top) 과밀→512 | **Top/Bottom/Inner2 3신호층** + Inner1 GND평면 |
| R4 | 신호가 EP 위 배선 | F1/F2(EP GND확정) 후 라우트 |
| R5 | GND 미연결 핀(autoroute 누락) | GND평면+풋프린트 열비아로 접지, DRC로 검증 |
| R6 | 안테나 keepout이 U1 패드와 겹침 | keepout을 안테나 끝만(U1 패드 제외) 크기/위치 정확히 |

### 프로세스
| # | 실수 | 우회법 |
|---|---|---|
| P1 | 깨진 방법(규칙변경) 오래 매달림 | 2회 no-op이면 즉시 포기·우회 |
| P2 | 재시작 남발(매번 DRC degrade) | 변경 일괄→재시작 1회→DRC 1회 묶음 |

---

## B. 모든 작업 공통 원칙
1. 검증=네이티브 DRC만(재시작 직후 1회). 2. 라인 .done() / 비아 .done() 금지.
3. 조밀구역=오토라우터. 4. fill=UI Shift+B(pour후 캡처 금지). 5. 규칙=UI만.
6. EP는 GND 확정 후 라우트. 7. 재시작 후 WINID 갱신+UI로 열기.

## C. 실행 순서 (refined 2026-06-22 저녁 — 규칙대화상자 설치전반 고장 확인 + advisor 검문 반영)

★중대 사실: **규칙 대화상자가 EasyEDA 설치 전반 고장**(PCB3에서도 안 열림, 앱재시작 무효). 캐시정리(cache.x64.3의 Service Worker/Cache/Code Cache/GPUCache/Dawn* 삭제) 시도 중 — 단 **로그아웃됨**(세션이 캐시에). 로그인은 사용자가(구글 OAuth도 내가 대행 금지). ⇒ 규칙 변경 가능여부 = Phase0 게이트.

- **Phase 0 게이트(로그인 후)**: ①규칙 대화상자 테스트 → A(살아남)=규칙설정 가능 / B(죽음)=규칙우회. ②A면 PCB5 마무리가 더 빠를 수 있어 재논의.
- **Phase 1 ★풋프린트 EP 선수정**: U4·U1 EP 열비아 GND 확정(풋프린트 에디터, 규칙대화상자와 별개라 동작 가능). → via-in-pad/부유EP 근원 제거 + 오토라우터가 EP 위 신호배선 회피. 폴백: PCB6 배치후 EP에 GND비아 직접추가.
- **Phase 2 PCB6 생성**: createPcb+importChanges(Schematic1 uuid 1b62a2b269c7d7ab). 4층 Top/Inner1=GND평면/Inner2=신호/Bottom. 검증: 45부품·38넷·EP비아 GND. PCB5=고아백업.
- **Phase 3 규칙(분기)**: A=4층프로파일+via-in-pad허용+넷클래스폭(VBUS/PVDD/BOOST_SW굵게). B=생략→Phase6폴백.
- **Phase 4 배치**: PCB5 검증좌표 재사용 + U1을 keepout 위로 이격 + EP 주변 신호공간 확보. 겹침0.
- **Phase 5 평면+keepout**: Inner1 GND pour + 안테나 keepout을 U1 안테나끝만(패드 제외) 정확히.
- **Phase 6 라우팅+검문**: A=오토라우트 All/Remove/Top·Bottom·Inner2/45°(전원굵게+신호얇게 동시). B=얇게 오토라우트→동맥(VBUS/PVDD/BOOST_SW)만 스크립트로 정폭. ★advisor검문: 30초마다 진행률 캡처, 95%정체/미배선 안줄면 즉시중단→배치미세조정→재시도. 롤백=EasyEDA 버전기록(깃 아님).
- **Phase 7 fill+GND비아**: UI Shift+B + GND 스티칭/EP비아 확인.
- **Phase 8 검증**: 재시작→네이티브 DRC 1회→잔여 일괄수정→클린까지(B모드면 via-in-pad만 문서화).
- **Phase 9 Gerber**: 사용자 확인 후 출력.

### advisor 플랜(외부) 평가: 채택=실시간 검문. 기각=①autoroute벽 문제는 이미 3층 Remove로 해결됨 ②Alt B "넷클래스 규칙주입"=우리 진짜 블로커(규칙API no-op+대화상자고장+클라우드라 로컬JSON없음)라 불가 ③Alt A "Inner2 전원평면화"=신호층 잃어 과밀재발+다중전원레일 불가 ④"Git rollback"=PCB는 클라우드저장이라 깃 무효.

## D. 진행 로그
- (여기에 각 Phase 완료 시 기록)
