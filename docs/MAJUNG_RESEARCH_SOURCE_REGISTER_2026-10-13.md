# MAJUNG 연구 및 규제 출처 총괄 등록부 (Research Source Register)
작성일: 2026-10-13  
상태: 공식 등록부 (버전 1.0)  
기준 저장소: https://github.com/youngseokchomajn-web/MAJN_GEMINI

---

## 1. 개요 및 출처 관리 원칙

본 문서는 MAJUNG(마중 스마트 배시넷) 프로젝트의 근거 기반 설계, 공학 시험, 임상 프로토콜 및 규제 대응을 위해 조사·분석된 모든 문헌과 공식 자료의 단일 진실 공급원(Single Source of Truth) 등록부다.

### 핵심 관리 규칙
1. **문헌 유형 및 근거 직접성 분리**: 대상군(건강 만삭아 vs 미숙아 vs NOWS 환아), 중재 방식(진동 vs 흔들림 vs 백색소음 vs 복합), 측정 변수(호흡/생리 vs 수면/울음)를 엄격히 분리한다.
2. **원문 추적성(Locator) 명시**: DOI, 공식 URL, 인쇄본 페이지, 표/그림 번호, 절(Section)을 구체적으로 기록한다.
3. **규제/임상 vs 마케팅 주장 구별**: 문헌의 생리학적 안정화 결과나 FDA 특정 적응증 허가를 일반 소비자용 배시넷의 '진정·수면 개선' 직접 근거로 비약하지 않는다.

---

## 2. 1차 핵심 문헌군 (Primary Evidence: E001 Series)

| Source ID | 완전 서지사항 (Citation) | DOI / 공식 식별자 / URL | 대상군 및 연구 설계 | 중재 특성 및 노출 | 핵심 관찰 결과 | AE 보고 코딩 | 직접성 (Directness) |
|---|---|---|---|---|---|---|---|
| **E001-A** | Smith VC, et al. Stochastic Resonance Effects on Apnea, Bradycardia, and Oxygenation: A Randomized Controlled Trial. *Pediatrics*. 2015;136(6):e1561–e1568. | DOI: [10.1542/peds.2015-1334](https://doi.org/10.1542/peds.2015-1334)<br>PMCID: [PMC4657600](https://pmc.ncbi.nlm.nih.gov/articles/PMC4657600/) | 무호흡/서맥 이력 미숙아 36명; 무작위 교차(Crossover) 설계 | 30–60 Hz 매트리스 확률 공명(SR) 진동, 10–20 μm; 30분 ON/OFF 교대 | 산소탈포화 사건 18% 감소(P=.01), 지속시간 35% 감소(P<.0001); 무호흡 50% 감소; 서맥 빈도 변화 없음(강도 18% 감소) | authors reported none (시험 기간 내 이상사건/기기결함 미관찰) | 낮음 (미숙아 호흡 생리 지표; 건강아 진정·수면 아님) |
| **E001-B** | Bloch-Salisbury E, Indic P, Bednarek F, Paydarfar D. Stabilizing immature breathing patterns of preterm infants using stochastic mechanosensory stimulation. *J Appl Physiol*. 2009;107(4):1017–1027. | DOI: [10.1152/japplphysiol.00058.2009](https://doi.org/10.1152/japplphysiol.00058.2009)<br>PMCID: [PMC2763836](https://pmc.ncbi.nlm.nih.gov/articles/PMC2763836/) | 미숙아 10명; 반복 ON/OFF (10분 블록) 생리 측정 설계 | 30–60 Hz 확률 기계감각 자극; 0.021 mm RMS 변위 (최대 0.090 mm); 균일도 ±2% | 호흡 간격(IBI) 분산 50% 감소(P=.003); 산소탈포화 시간 65% 감소(P=.04); 수면/각성 상태 전이율 변화 없음 | not clearly reported in extracted source (체계적 AE 표 미기재) | 낮음 (소규모 생리 기전 및 공학 측정 선례; 건강아 진정 아님) |
| **E001-C** | Zuzarte I, Indic P, Barton B, Paydarfar D, Bednarek F, Bloch-Salisbury E. Vibrotactile stimulation: A non-pharmacological intervention for opioid-exposed newborns. *PLOS ONE*. 2017;12(4):e0175981. | DOI: [10.1371/journal.pone.0175981](https://doi.org/10.1371/journal.pone.0175981)<br>PMCID: [PMC5398650](https://pmc.ncbi.nlm.nih.gov/articles/PMC5398650/) | 산전 오피오이드 노출(NOWS) 만삭아 26명 (모르핀 투여 중); 개체 내 교차 비교 | 30–60 Hz 확률 진동 매트리스; 10–12 μm RMS; 30분 ON/OFF 교대 (6–8시간) | 절대 움직임 활동 40% OFF vs 26% ON (35% 상대 감소, P<.001); 30초 초과 움직임 감소; 심박수/호흡수 소폭 안정화; 체온/산소포화도 유지 | authors reported none (FDA 검토서 상 이상사건 미보고 확인) | 중간 (움직임 감소 관찰되었으나 약물치료 환아 대상; 건강아 수면 아님) |
| **E001-D** | FDA Center for Devices and Radiological Health. De Novo Classification Request for Prapela SVS Hospital Bassinet Pad (Model P01). DEN240031. 2024. | FDA 공식 URL: [DEN240031.pdf](https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240031.pdf) | 규제 의사결정 요약서 (21 CFR 880.5151, Class II, 코드 QVY); 9페이지 공식 문서 | 병원용 진동 매트리스 패드; 확률 진동(DRMS 규정); 3시간 주기 제어 | 적응증: NOWS 환아(≥37주)의 보조 비약물 요법; 벤치 적합성, 전기안전/EMC 입증; 2017 자료는 안전성 뒷받침, 2023 RCT는 임상 유효성 평가 | bounded report (제출된 임상시험 범위 내 이상사건 미관찰) | 중간-낮음 (특정 질환 의료기기 허가; 일반 영아용 배시넷 인허가 아님) |
| **E001-E** | Bloch-Salisbury E, Wilson JD, Rodriguez N, et al. Efficacy of a Vibrating Crib Mattress to Reduce Pharmacologic Treatment in Opioid-Exposed Newborns: A Randomized Clinical Trial. *JAMA Pediatr*. 2023;177(7):665–674. | DOI: [10.1001/jamapediatrics.2023.1077](https://doi.org/10.1001/jamapediatrics.2023.1077)<br>PMCID: [PMC10186209](https://pmc.ncbi.nlm.nih.gov/articles/PMC10186209/) | 산전 오피오이드 노출 신생아 208명 무작위 배정 (181명 최종 분석); 다기관 무작위 대조군 시험(RCT) | SVS 매트리스 + 표준치료(TAU) vs 표준치료 단독; 30–60 Hz, 10–12 μm RMS | 1차 결과(모르핀 투여율) 30.9% vs 35.6% (P=.60, 유의차 없음); 노출시간당 투여위험 aOR 0.88 (95% CI 0.81–0.93); 반응군(≤21일 치료완료 32명)에서 치료일수 3.18일 단축 | bounded protocol observation (중단 후 24시간 내 6/58명 약물기준 충족; 기기 이상사건 없음) | 낮음 (NOWS 약물치료율 평가; 건강아 진정/울음/수면 endpoint 아님) |
| **E001-F** | Singh R, Trinquart L, Koethe B, et al. Efficacy of stochastic vibro-tactile stimulation for newborns at risk of neonatal opioid withdrawal syndrome. *Pediatr Res*. 2026;99(1):276–282. (Online 2025). | DOI: [10.1038/s41390-025-04162-2](https://doi.org/10.1038/s41390-025-04162-2)<br>PMCID: [PMC13134440](https://pmc.ncbi.nlm.nih.gov/articles/PMC13134440/)<br>Trial: [NCT04834297](https://clinicaltrials.gov/study/NCT04834297) | NOWS 위험 신생아(≥35주) 62명 (계획 120명 중 조기 종료); 다기관 비눈가림 RCT (2:1 배정) | 지속적 저수준 SVS (40명) vs 표준 매트리스 (22명); 30–60 Hz, 10–12 μm RMS | 1차 결과(5일 내 약물시작) 10.0% vs 18.2% (aOR 0.54, 95% CI 0.10–2.85, P=.46, 비유의); 울음 하위분석(n=46)에서 보챔/통증 울음 시간 차이 없음 (P=.82); 양육자 만족도 높음 | authors reported none (두 군 모두 이상사건 미관찰) | 낮음 (NOWS 고위험군 대상; 울음 하위분석 비유의; 주관적 만족도는 객관적 효능 아님) |

---

## 3. 2순위 추가 문헌군 (Secondary & Contextual Evidence)

### 3.1 건강 만삭 영아 진동·수면·울음 직접 연구군
* **E002-A (Spencer et al. 1990)**: *Vibrotactile stimulation and infant state.*
  - 내용: 만삭아 대상 국소/전신 진동 자극 시 행동 상태(State) 및 심박 반응 연구. 진동 자극이 일시적인 각성 또는 안정화에 미치는 상반된 효과 지적.
  - 한계: 표본 수가 적고 현대적 지속 진동 배시넷 환경과 자극 프로파일이 상이함.
* **E002-B (Byrne & Horowitz 1981)**: *Rocking and vibration effects on infant calming.*
  - 내용: 기계적 흔들림(Rocking, <1 Hz 대변위)과 진동(Vibration, 고주파 저변위)을 비교. 진정(Calming)에는 흔들림이 더 즉각적인 효과를 보였으며 고주파 진동은 자극 과다(Overstimulation) 유발 가능성 보고.
  - 의의: MAJUNG 설계 시 진동 주파수/진폭의 임계값 설정 중요성 시사.

### 3.2 대체 및 복합 중재 제품군 (Rocking, Sound, Multi-modal)
* **E003-A (SNOO / Karp et al. / NCT05711927)**: *Responsive Bassinet Clinical Registry.*
  - 내용: 지속적 백색소음 + 반응형 흔들림(약 0.5–1.5 Hz 진자 운동) + 전용 스와들 결합.
  - 해석 경계: SNOO의 수면 개선 주장은 복합 중재(소음+스와들+요람 흔들림)의 결과이며, 단순 미세 진동 매트리스 단독 효과로 환원할 수 없음.
* **E003-B (Cochrane Review: Non-pharmacological interventions for infant colic / crying)**:
  - 내용: 영아 산통 및 과도한 울음에 대한 비약물적 중재 체계적 문헌고찰.
  - 결론: 진동 단독 중재에 대한 고품질 대규모 무작위 대조군 근거는 극히 부족하며, 근거 수준이 대부분 '매우 낮음(Very Low)'으로 분류됨.

### 3.3 영아 수면 및 행동 상태 측정 타당도 (Measurement Validity)
* **E004-A (Sadeh et al. / Meltzer et al.)**: *Pediatric actigraphy and video PSG validation.*
  - 내용: 영아 수면 평가에서 가속도계(Actigraphy)와 비디오 수면다원검사(Video-PSG)의 일치도 검증.
  - **MAJUNG 공학적 핵심 주의점**: 배시넷 자체의 기계적 진동(30–60 Hz)이 영아 착용 또는 매트리스 내장 가속도계에 강한 진동 노이즈(Artifact)로 유입되어 '깨어있음(Wake)' 또는 '움직임'으로 오인식될 위험이 큼. 밴드패스/노치 필터링 또는 영상 기반 독립 검증 필수.

---

## 4. 규제 기준 및 안전 규격 등록부 (Regulatory & Safety Standards)

1. **FDA 21 CFR 880.5151 (Therapeutic vibrational mattress pad)**
   - 분류: Class II, 제품 코드 QVY.
   - 특별 규제(Special Controls): 벤치 진동 출력 및 균일도 검증, 최대 음향 소음 한계(Auditory sound level), 기계적 침구 적합성, 전기기계적 안전성(IEC 60601-1), 전자파 적합성(IEC 60601-1-2), 생체적합성(ISO 10993), 소프트웨어 검증 및 위험 관리(ISO 14971).
2. **ASTM F2194-22 / 16 CFR Part 1218 (Standard Consumer Safety Specification for Bassinets and Cradles)**
   - 규제 기관: 미국 CPSC (소비자제품안전위원회).
   - 필수 요건: 매트리스 두께 및 견고성(Firmness), 질식 위험 방지, 평평도(최대 각도 10도 이하), 측면 통기성, 전원 코드/끼임(Entrapment) 방지, 전도(Tip-over) 안정성.
3. **어린이제품 안전 특별법 (산업통상자원부 고시 제2022-220호 / 부속서 6 완구 및 유아용 가구 기준)**
   - 국내 KC 안전확인 기준: 유해화학물질(프탈레이트, 폼알데하이드, 납/카드뮴), 기계적 강도, 모서리 및 틈새 끼임 방지, 가연성 시험.
4. **KC 방송통신기자재등의 적합등록 (전파법 제58조의2)**
   - 무선(BLE/Wi-Fi) 통신모듈 장착 배시넷의 전자파 적합성(EMC) 및 무선 규격 인증.

---

## 5. 결론 및 연구팀 지침

현재 등록된 문헌 중 **"건강한 만삭 영아를 대상으로 MAJUNG과 유사한 진동 매트리스 단독 중재가 울음을 줄이거나 수면을 개선했다"는 1차 직접 임상 근거는 전무(Zero)**하다.  
따라서 향후 단계에서는 기존 문헌의 공학적 계측 파라미터(E001-B, E001-D)를 벤치 시험에 참고하되, 효능 입증은 자체 IRB 승인 임상 연구(WP-2/WP-3)를 통해 독립적으로 확보해야 한다.
