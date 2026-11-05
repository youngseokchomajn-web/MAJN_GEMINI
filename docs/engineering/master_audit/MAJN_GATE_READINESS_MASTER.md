# [Gate 마스터 평가서] MAJN 차기 제어기 (PCB #0006) 9대 승인 Gate 마스터 평가표
(MAJN PCB #0006 Master Gate G0~G8 Readiness & Physical Exit Criteria Assessment)

- **문서 식별자**: `MAJN_GATE_READINESS_MASTER`
- **리비전**: v2.0 (마스터 감사 기준선)
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (독립 기술 심사 에이전트)
- **승인 권한**: Human Chief Authority
- **종합 판정**: **G0~G5 전원 HOLD (임의 설계 착수 및 거버 생성 동결) | G6~G8 NOT_STARTED**

---

## 1. 개요 및 Gate 승인 통제 규칙

본 문서는 MAJN 차기 제어기(PCB #0006) 개발 파이프라인에서 **"각 Gate의 진입 요건(Entry Criteria)과 물리적 퇴출 요건(Physical Exit Criteria)"을 엄격히 규정**하여, 선행 Gate가 승인되지 않은 상태에서 후행 작업(회로 수정, 배선, 거버 발주)이 진행되는 것을 원천 차단합니다.

### Gate 운영 3대 절대 원칙
1. **No Bypassing**: 선행 Gate가 통과되지 않으면 후행 Gate 착수는 불가함.
2. **Physical Evidence First**: 문서나 시뮬레이션 결과만으로 물리적 안전성 Gate를 통과시킬 수 없음.
3. **Sole Chief Authority**: 설계 기준선 변경, 부품 교체, 거버 발주 승인은 오직 Human Chief Authority의 정식 서명으로만 효력을 발휘함.

---

## 2. 9대 승인 Gate 종합 평가 매트릭스

| Gate | 명칭 | 진입 기준 (Entry Criteria) | 필수 물리/공학적 증거 (Required Exit Evidence) | 현재 판정 (Status) | 승인 주체 | 잔여 갭 및 액션 아이템 |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **G0** | **제조 기준선 복원** | 7월 제조 발주 파일 및 실물 증거 확보 | • 4층 거버 20개 파일 일치<br>• BOM/CPL 56개 단일면 SMT 100% 일치<br>• 실물 사진 대조 확인<br>• 클린 `.epro2` 넷리스트 1:1 일치 | **HOLD**<br>(조건부 진행 중) | Antigravity (검증)<br>Chief Authority (승인) | • EasyEDA Pro 클린 SSOT 프로젝트(`.epro2`) 역합성 완료<br>• C11/R12 실물 치수 현미경 실측 사진 첨부 |
| **G1** | **고장 분석/FMEA 확정** | 선행 시제품 고장 이력 수집 | • 12대 고장 모드 메커니즘 규명<br>• FMEA RPN 평가 완료<br>• TP-01~04 오실로스코프 실측 파형 | **HOLD**<br>(조건부 진행 중) | OpenCode (분석)<br>Antigravity (검증)<br>Chief Authority (승인) | • Prototype #0005 실물 벤치 오실로스코프 파형(TP-01 과도 전압, TP-03 역기전력) 획득 및 리포트 첨부 |
| **G2** | **요구사항/아키텍처 확정** | G0, G1 조건부 통과 및 시스템 요구사항 확정 | • Core 12개 요구사항 동결<br>• Extended 3개 채택 여부 최종 결정<br>• 전력 예산(10W vs 16.5W) 정합성 입증<br>• 시스템 블록도 및 인터페이스 동결 | **HOLD**<br>(의사결정 대기) | Human Chief Authority (단독 승인) | • 확장 제안 3건(REQ-P0-06, P1-08, P1-09) 채택 여부 최종 서명<br>• `DOC03` v1.2 개정 서명 |
| **G3** | **회로 상세 설계/부품 승인** | G2 공식 승인 완료 | • 회로도 수정안 및 넷리스트 100% 일치<br>• ERC 0 Error / 0 Warning<br>• GPIO13 PDN 배정 및 FW 동기화 승인<br>• L1(7.5A), C6-C9(35V) 부품 승인<br>• BTL 보호 토폴로지 승인 | **HOLD**<br>(설계 수정 동결) | Lead Engineer<br>Antigravity<br>Chief Authority (승인) | • Read-Only 규칙 유지 중<br>• G2 확정 후 회로도 수정 착수 및 부품 ECO 결재 |
| **G4** | **PCB Layout & DFM 검토** | G3 공식 승인 완료 | • 4층 PCB 스택업(JLCPCB 7628 확인)<br>• 파워 루프 최소화 및 동박 Rebuild<br>• DRC 0 Error (Clearance/Crossing)<br>• 션트 패드 및 TP1~TP10 배치<br>• 기구 하우징 3D 간섭 검토 | **HOLD**<br>(배선 착수 동결) | Lead Engineer<br>Antigravity | • G3 승인 후 배선 착수<br>• JLCPCB 공식 스택업 성적서 수령<br>• 온라인 DFM 통과 |
| **G5** | **제조 데이터 Release** | G4 공식 승인 및 DRC 완전 통과 | • 최종 Gerber_Output.zip (SHA-256 동결)<br>• BOM/CPL 100% 매칭 검증<br>• 제조 발주 매니페스트 서명 | **HOLD**<br>(발주 금지) | Human Chief Authority (단독 서명) | • 모든 선행 Gate 종결 후 최종 서명 및 거버 생성 |
| **G6** | **하드웨어 Bring-up 검증** | 실물 PCB #0006 제작 및 수령 | • DMM 임피던스 쇼트 검사<br>• 전원 시퀀싱 실측<br>• 오버슈트(<13.2V) 오실로스코프 파형<br>• 10W 연속 부하 열화상(<55°C) 계측 | **NOT_STARTED** | Lead Hardware Engineer<br>Chief Authority | • 물리 보드 제작 완료 후 진행 |
| **G7** | **규제 인증 적합성** | G6 하드웨어 정상 동작 확인 | • KC 전자파(KN 32/35) 사전 시험성적서<br>• 영유아 안전기준(음압 <75dB, 온도 <60°C)<br>• 모터 구속/단락 시 안전 차단(<100ms) 입증 | **NOT_STARTED** | 공인시험소<br>Chief Authority | • 공인 인증 기관 사전 시험 의뢰 |
| **G8** | **최종 양산 Release 확정** | G0~G7 전원 합격 및 잔여 이슈 제로 | • 양산 금형/조립 공정 매뉴얼(SOP)<br>• 최종 제조 거버/BOM/CPL 형상 동결<br>• KC/FCC 정식 인증서 수령 | **NOT_STARTED** | Human Chief Authority | • 양산 승인 및 이력 최종 아카이빙 |

---

## 3. 결론

1. 현재 프로젝트는 **Gate G0/G1의 물리적 증거 보완 단계**에 머물러 있으며, **Gate G2~G5는 완전한 동결(Strict HOLD)** 상태입니다.
2. 소프트웨어 CI 검증 도구가 100% PASS 되었다고 하여 PCB #0006 회로가 검증된 것이 아니며, **각 Gate의 물리적 퇴출 요건(Physical Exit Criteria)이 만족되어야 다음 Gate로 진입**합니다.
