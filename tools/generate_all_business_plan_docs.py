#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_all_business_plan_docs.py
Generates and synchronizes all 4 business plan files:
1. 모두의창업_공식자료/성명_1R_사업계획서_마중_최종본.md
2. 모두의창업_공식자료/성명_1R_사업계획서_마중_최종본.txt
3. 모두의창업_공식자료/27-3. (261020)성명_1R 사업계획서_마중_작성본.docx
4. 모두의창업_공식자료/모두의창업_1R_사업계획서_작성완료본_미리보기.html
"""

import os
import re
import docx
from docx.shared import Pt, Inches, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(WORKSPACE, "모두의창업_공식자료")

MD_PATH = os.path.join(OUT_DIR, "성명_1R_사업계획서_마중_최종본.md")
TXT_PATH = os.path.join(OUT_DIR, "성명_1R_사업계획서_마중_최종본.txt")
DOCX_PATH = os.path.join(OUT_DIR, "27-3. (261020)성명_1R 사업계획서_마중_작성본.docx")
HTML_PATH = os.path.join(OUT_DIR, "모두의창업_1R_사업계획서_작성완료본_미리보기.html")

# Canonical Text Structure
HEADER_LINES = [
    "[표지]",
    "2026년 2차 모두의 창업 프로젝트",
    "1R 사업계획서",
    "멘토기관 : 하나은행 (서울 권역) / 담당 멘토: 기획전략팀 김지영 팀장",
    "성명 (대표자) : 조영석 (기술 총괄) / 오동규 (사업 총괄)",
    "창업아이템명 : 20mm 언더매트리스 스마트 신생아 수면·진정 패드 「마중 (MAJN)」",
    "[아이템 요약]",
    "침대 전체를 교체하지 않고 기존 매트리스 하단에 삽입하여 사용하는 20mm 슬림형 영아 진정 보조 패드임.",
    "기존 고가 완제품 스마트 침대의 한계(요람 전체 흔들림에 따른 보호자 불안, 거대한 부피, 200만 원대 가격)를 언더매트리스 모듈화 구조로 개선하여 조리원 현장 도입 장벽을 대폭 낮춤.",
    "30~60Hz 대역 미세진동의 진정 효과 가설을 바탕으로, 1R에서는 미검증 부가기능(SaaS 모니터링, 센서 자동 반응, 백색소음 동기화 등)을 후속 과제로 분리하고 제어보드(PCB #0006) 벤치 구동, 전원부 발열 제어 및 비영아 벤치 진동 안정성 검증에 집중함.",
    "1차 핵심 목표 고객을 신생아실 야간 돌봄 부담이 큰 산후조리원으로 명확히 설정하고, 1R 기간 동안 초기 협력 조리원(1~2개소)과의 규격 협의 및 비영아 벤치 측정을 완료한 후, 향후 단계적 상용 납품 및 B2C 렌탈 확장으로 연계하고자 함.",
]

Q1_LINES = [
    "Q1. 문제 인식(problem)",
    "※ 아이디어의 개발 동기·목적 및 목표 시장 등",
    "1. 창업 배경 및 해결 대상 문제",
    "◦ 산후조리원 신생아실의 야간 집중 돌봄 병목 및 연쇄 각성 문제",
    " - 산후조리원 신생아실은 다수의 신생아가 동일 공간에서 생활하는 집단 돌봄 환경으로 야간 시간대 집중적인 수면 관리가 필수적임.",
    " - 모자보건법 시행규칙 [별표 3] 상의 기준(간호사 1인당 신생아 7명) 대비, 수도권 소재 산후조리원 2개소 현장 심층 인터뷰 및 관찰(2026.10, A조리원 16실, B조리원 21실 대상 조사) 결과 실제 야간 교대근무 시 당직 간호인력 1명이 영아 8~12명을 동시 전담하는 과밀 집중 관리 환경이 확인됨.",
    " - 신생아는 1~2시간 단위로 각성하며, 한 영아의 울음과 보챔이 다인실 전체로 번지는 '연쇄 각성' 발생 시 1인의 간호인력이 다수 영아를 동시에 1:1로 안아 달래기 불가능한 구조적 돌봄 병목에 직면함.",
    " - 이로 인해 야간 간호인력의 육체적·정신적 피로가 누적되고 야간 낙상 등 안전사고 위험이 증가하며, 산모의 야간 휴식 보장 및 조리원 운영 신뢰도 저하로 이어짐.",
    "◦ 조리원 운영 현장의 도입 장벽 및 기존 인프라 제약",
    " - 조리원 운영자는 신생아실 내 감염 방지를 위해 70% 알코올 소독제 상시 접촉에 견디는 위생 내화학성을 엄격히 요구함.",
    " - 또한 기존에 구축된 아크릴 바구니 카트(내측 650×400mm) 인프라를 전면 폐기하고 고가 완제품 스마트 침대(대당 약 200만 원)를 도입하는 것은 과도한 초기 투자비와 공간 제약으로 채택이 불가능함.",
    " - 따라서 기존 아크릴 카트 매트리스 하단에 슬라이드 방식으로 결합하여 무단차로 호환되는 20mm 슬림 패드 형태의 진정 보조 모듈이 가장 현실적인 현장 요구 대안임.",
    "◦ 미세진동 진정 메커니즘 착안 및 공학적 가설 설정",
    " - 차량 주행 시 발생하는 30~60Hz 대역 미세진동이 태아기 자궁 내 혈류 파동과 유사하여 안정감을 유도한다는 선행 연구(Spencer et al., 1990; Bloch-Salisbury et al., 2009) 및 영아 관찰 사례에 착안함.",
    " - 다만 30~60Hz 주파수 설정 자체만으로 영아의 수면 개선이나 진정 효과가 보장되는 의학적 효능은 아니므로, 이를 과학적 가설로 규정하고 매트리스 표면에서의 합성 가속도(RMS)와 공학적 안전성을 실측 검증하는 것이 선행 과제임을 인식함.",
    "◦ 최종 수혜자인 가정 양육자의 산후 수면 부담 (배경 통계)",
    " - 조리원 퇴소 후 가정 환경에서도 영아 야간 수면 문제는 지속되며, 2024년 보건복지부 산모 실태조사(출산 후 100일 이내 산모 3,221명 대상 표본조사) 결과 산후 애로사항 1위로 '수면 부족(84.2%)'이 보고됨.",
    " - 한국리서치 정기 여론조사(2025, 전국 20~30대 신혼부부 1,000명 대상 설문)에서도 출산·양육의 최대 부담 요인으로 '육체적·정신적 피로(75.0%)'가 지목됨.",
    " - 이에 따라 1차적으로 조리원 신생아실의 야간 돌봄 문제를 해결하고, 안전성이 검증된 기기를 가정용 렌탈로 연계하는 단계적 문제 해결 전략을 추진함.",
    "2. 문제를 겪는 목표 고객과 문제의 크기·시급성",
    "◦ 1차 핵심 목표 고객: 산후조리원 원장 및 신생아실 운영 책임자",
    " - 구매·도입 이유: 야간 1:8~12 과밀 집중 돌봄 병목 완화, 신생아실 연쇄 각성 차단, 야간 간호인력 근무 안정성 확보 및 산모 케어 만족도 제고.",
    " - 위생 및 설치 조건: 기존 아크릴 바구니 카트(내측 650×400mm) 규격 내 단차 없는 거치, 알코올 소독제 내화학성 및 무독성 분리형 방수 커버 필수.",
    " - 가격 지불 의향: 신생아 1인 침대당 35만 원 선(기존 고가 스마트 침대 200만 원 대비 약 1/6 수준)으로 전 베드 일괄 또는 단계적 도입 의향 타진.",
    " - 1R 실증 과제: 조리원 운영자 및 현장 간호인력의 실제 구매/도입 이유, 위생·설치 규격 조건, 가격 지불 의향을 1~2개소 현장에서 실측 검증하는 것임.",
    "◦ 최종 수혜자: 신생아실 간호인력 및 퇴소 산모(가정 양육자)",
    " - 신생아실 간호인력: 동시다발적 영아 보챔 시 초기 진정을 보조받아 1인당 담당 영아 대응 시간을 확보하고 야간 피로도를 완화함.",
    " - 퇴소 산모: 조리원에서 안전성이 확인된 진정 보조 방식을 퇴소 후 가정에서도 렌탈 형태로 연속 활용할 수 있는 잠재적 최종 수혜자임.",
    "3. 목표 시장 및 기존 대체재의 한계",
    "◦ 보건복지부 조리원 현황 및 전국 잠재 인프라 상한치(TAM) 산출표",
    "구분 | 통계 지표 및 산출 기준 | 수치 및 규모 | 성격 및 비고",
    "전국 산후조리원 인프라 | 보건복지부 전국 산후조리원 현황 (2024년 기준) | 전국 680개소 (총 정원 12,500실) | 개소당 전국 평균 18.38실(약 18.4실)",
    "표본 실측 조리원 | 수도권 소재 협력 조리원 2개소 현장 실측 (2026.10) | A소(16실), B소(21실) / 평균 18.5실 | 아크릴 카트 규격(650×400mm) 실측 확인",
    "이론적 TAM 상한치 (전국) | 전국 12,500실 전량 일시 보급 가정 (대당 35만 원) | 약 43억 7,500만 원 (12,500실 × 35만 원) | 전국 인프라 일회성 잠재 상한치 (TAM)",
    "가설 모델 상한치 (표본) | 표본 평균(18.5실) 전국 680개소 적용 시 (12,580실) | 약 44억 300만 원 (약 44억 원) | 초기 가설 모델링 상한치 (TAM 상한)",
    "실제 1R 검증 목표 (현장) | 초기 협력 조리원 1~2개소 비영아 벤치 및 규격 검증 | 1~2개소 (약 30~40베드 규모) | 연간 시장(SAM)으로 단정 불가, 단계적 실증",
    "* 상기 43억 7,500만 원 및 44억 원은 매년 반복 발생하는 연간 시장이나 검증된 시장 규모(SAM)가 아니라 전국 인프라 일회성 보급 가정 시의 이론적 최대 잠재매출 상한(TAM 상한)임.",
    " - 1R에서는 미검증 전국 시장 수치에 매몰되지 않고, 초기 협력 조리원 1~2개소(약 30~40베드 규모) 대상의 현장 실증 및 도입 가설 검증에 집중함.",
    "◦ 기존 대안의 한계 분석",
    " - 수동 바운서: 보호자나 간호사가 손으로 지속 조작해야 하므로 실질적인 업무 경감이나 휴식이 불가함.",
    " - 전동 요람(미국 SNOO, 수입가 약 220만 원): 침대 프레임 전체를 좌우로 크게 흔드는 구조로, 신체 요동에 대한 보호자의 안전 우려가 크고 조리원 아크릴 카트 규격에 배치가 불가능함.",
    " - 이에 따라 기존 침대 매트리스 하단에 삽입하여 신체 요동 없이 미세 파동만 전달하는 20mm 슬림 패드 방식의 진정 보조 기기 개발 필요성을 도출함.",
]

Q2_LINES = [
    "Q2. 실현 가능성(solution)",
    "※ 아이디어의 개발 방안, 준비 정도, 차별화 방안",
    "1. 제품 핵심 기능 및 공학적 검증 가설",
    "◦ 30~60Hz 대역 미세진동 전달 메커니즘 (가설 및 공학 설계)",
    " - 매트리스 표면에 30~60Hz 대역의 미세진동을 전달하여 영아의 진정을 보조하는 메커니즘은 확정된 의학적 치료 효과가 아닌 공학적 연구 검증 가설(Hypothesis)임.",
    " - 영아의 신체 흔들림을 배제하고 좌우 대칭형 진동 구동 모듈을 배치하여 매트리스 하단에서 균일한 진동 파동을 형성하도록 설계함.",
    " - 실제 매트리스 표면에서의 합성 실효 가속도(RMS), 최대 진폭(Amplitude), 공간적 균일성(Uniformity), 투과 소음 및 발열을 객관적으로 계측하여 공학적 안전 기준선을 수립하는 것을 선행 연구 목표로 설정함.",
    " - 영아 대상의 진정 및 수면 개선 효과는 비영아 벤치 측정 완료 후 전문 연구기관 및 의학 전문가 자문, 연구윤리(IRB) 절차를 거치기 전까지 확정 표현을 엄격히 배제함.",
    "◦ 기기 구동 소음 제어 및 AAP 음향 가이드라인 참조 (잠정 개발 목표)",
    " - 매트리스 상부 30cm 이격 거리(영아 귀 위치 모사) 기준 기기 구동음의 투과 음압 소음을 50dBA 이하로 제어하는 것을 잠정 내부 개발 품질 관리 목표로 설정함.",
    " - 본 50dBA 수치는 공식적인 완제품 법적 안전 규격이 아니라, 미국소아과학회(AAP, 2023 정책자료 'Preventing Excessive Noise Exposure in Infants')의 병원 신생아 중환자실(NICU) 주변 배경 소음 권고 수준(45~50dBA Leq)을 참고하여 설정한 당사의 잠정 내부 개발 목표임.",
    " - 병원 환경의 주변 배경 소음 권고와 제품 30cm 이격 거리 계측은 측정 환경과 목적이 상이하므로, 이를 제품 합격선으로 단정하지 않고 비영아 벤치에서의 잠정 소음 제어선으로 관리함.",
    "◦ 하드웨어 상태 및 기능 사실 관리 기준표 (사실표)",
    "구분 | 대상 항목 | 현황 및 1R 검증 목표 | 판정 및 주의사항",
    "확인 완료 사실 | 제어 회로 및 기구 설계 | PCB 아트워크 설계 완료, 20mm 슬림 목업 CAD 모델링 완료 | KiCad/CAD 설계 완료, PCB #0006 제작 대기 상태",
    "확인 완료 사실 | 조리원 규격 실측 | 수도권 조리원 2개소 방문, 아크릴 카트(650×400mm) 실측 | 기존 카트 무단차 삽입 호환성 기구 확인",
    "확인 완료 사실 | 무선 통신 인터페이스 | ESP32 기반 BLE 기본 연결 및 패킷 제어 구조 정의 | 스마트폰-보드 간 기본 연결 확인",
    "1R 구현·실물 검증 | 하드웨어 벤치 구동 | 차기 제어보드(PCB #0006) 벤치 전원 인가 및 진동 출력 확인 | 물리적 진동 가진 여부 검증 (벤치 시작 전)",
    "1R 구현·실물 검증 | 전원부 발열 제어 | 60분 부하 구동 시 보드 전원부 및 표면 온도 실측 | 잠정 목표: 주요 IC 75℃ 이하, 표면 40℃ 이하",
    "1R 구현·실물 검증 | 비영아 표면 진동 계측 | 3.5kg 더미 하중 하 매트리스 상부 3축 가속도(RMS)·진폭 실측 | 잠정 목표: 0.05~0.15g RMS, 0.2mm 이내, 편차 20%",
    "1R 구현·실물 검증 | 과열 자동 차단 연동 | 이상 과열 시 바이메탈 전원 차단 회로 연동 벤치 동작 시험 | 실물 검증 전까지 확보된 안전 기능으로 단정 금지",
    "미확인 사항 | 영아 임상 진정 효능 | 30~60Hz 미세진동의 영아 수면 유도 및 진정 효과 | 의학적·임상적 효능 미확인 (공학적 가설 단계)",
    "미확인 사항 | 매트리스 감쇠 및 내구 | 매트리스 재질(폼/에어메시)별 진동 감쇠율 및 장기 내구성 | 1R 비영아 벤치 반복 측정을 통해 데이터 확보 예정",
    "향후 후속 과제 | 백색소음 음향 동기화 | 저주파 백색소음 출력 모듈과 진동 제어 동기화 연동 | 진동 구동 하드웨어 안정성 확인 후 후속 통합",
    "향후 후속 과제 | 센서 반응 로직 및 SaaS | 외장 마이크·압전센서 연동 자동 감지 및 조리원 모니터링 | 1R 이후 단계적 고도화 추진 (아이템명 분리)",
    "향후 후속 과제 | 영아 대상 실증 평가 | 실제 영아 대상 사용성 및 진정 효과 관찰 평가 | 1R 공학 벤치 안전 확보 및 IRB/윤리 승인 후 추진",
    "향후 후속 과제 | B2C 렌탈 물류망 | 회수 배송, 고온 살균 세척 및 재상품화 인프라 구축 | 조리원 1차 현장 실증 완료 후 후속 연계",
    "* 상기 사실표에 따라 1R에서는 미검증 부가기능을 배제하고 제어보드 벤치 구동, 전원부 발열 제어 및 비영아 표면 진동 계측에 개발 역량을 집중함.",
    "2. 기구 설계 혁신: 20mm 언더매트리스 모듈화",
    "◦ 슬림형 패드 구조 적용",
    " - 침대 프레임 전체를 제조하지 않고, 기존 매트리스 하단에 슬라이드 방식으로 삽입하여 사용하는 20mm 두께의 복합 패드 형태로 설계함.",
    " - 산후조리원 아크릴 카트 매트리스(650×400mm) 규격에 맞추어 단차 없이 호환 가능하도록 치수를 표준화하고 영아 낙상 위험을 원천 방지함.",
    "◦ 제조 및 공급 리스크 최소화",
    " - 대형 완제품 가구 제조 방식 대비 금형비, 조달 원가, 물류 보관 및 운송 비용을 대폭 절감할 수 있는 구조적 이점을 확보함.",
    "3. 단계적 기술개발 및 연구기관 협력을 통한 검증 역량 확보",
    "◦ 핵심 기능 중심의 컴팩트 MVP 자체 개발 집중",
    " - 초기 개발 효율성과 핵심 기능의 검증 가능성을 고려하여 필수 기본 기능에 개발 범위를 한정함.",
    " - [자체 개발 우선순위] : 1) 30~60Hz 진동 가진 출력 여부 확인, 2) 전원부 발열 제어 및 연속 구동 안정성, 3) 기본 물리 스위치 및 타이머 제어 인터페이스, 4) 바이메탈 전원 차단 회로 연동 실측.",
    " - 복잡한 센서 반응 로직이나 SaaS 모니터링, 백색소음 동기화는 후속 개발 단계로 분리하여 초기 제품의 기본 물리적 성능과 발열 안전성을 우선 확보함.",
    "◦ 1R 비영아 벤치 테스트 측정 조건 및 잠정 내부 개발 목표",
    " - [대상 매트리스 종류별 특성] : 산후조리원 다빈도 매트리스 2종(고밀도 압축 폼 20mm: 탄성 지지형, 통기성 3D 에어메시 30mm: 공기 순환 및 고감쇠형).",
    " - [측정 환경 및 반복 조건] : 영아 모사 더미(3.5kg 하중 분산 모델) 거치 상태에서 매트리스 상부 3개 포인트(두부, 체간부, 둔부)에 3축 디지털 가속도 센서를 부착하고, 주파수 대역(30Hz, 45Hz, 60Hz)별 각 10분 연속 구동 후 5회 이상 반복 실측하여 평균값 및 최대 편차를 산출함.",
    " - [측정 항목별 정의 및 잠정 내부 개발 목표치] :",
    "   * 표면 진동 가속도: 영아 모사 더미(3.5kg) 하중 하 매트리스 표면 3개 위치에서 3축 가속도계로 측정한 30~60Hz 대역 합성 실효 가속도를 0.05g~0.15g RMS 범위로 제어하는 것을 잠정 내부 개발 목표로 설정함 (일상 주행 차량 시트 수준의 미세 전달 파동 목표, 0.2g 초과 피크 충격 배제).",
    "   * 표면 최대 진폭: 레이저 변위 센서 기준 매트리스 표면 상하 변위 0.2mm 이내 유지 목표.",
    "   * 위치별 균일성: 두부, 체간, 둔부 간 RMS 가속도 편차 20% 이내 유지 목표 (특정 부위 국소 진동 집중 방지).",
    "   * 투과 음압 소음: 매트리스 상부 30cm 이격 거리 기준 50dBA 이하 (AAP NICU 주변 환경 소음 권고를 준용한 잠정 품질 관리 목표).",
    "   * 전원부 발열 제어: 60분 연속 구동 시 보드 주요 전원 IC 75℃ 이하, 하우징 표면 40℃ 이하 유지 목표 (이상 과열 시 자동 셧다운 회로 연동 벤치 시험).",
    "   * 상기 수치들은 법적 안전 합격선이 아닌 당사의 잠정 내부 개발 목표치이며, 향후 전문 연구기관과의 정밀 계측 및 전문가 검토를 거쳐 최종 안전 기준선으로 확정할 예정임.",
    " - [영아 대상 실증 유예 원칙] : 영아 대상 직접 실증은 1R 비영아 공학 벤치 계측 완료 후, 별도의 윤리적·의학적 안전성 검토(IRB 심의 또는 소아청소년과 전문의 자문) 절차를 거친 이후 단계로 유예함.",
    "◦ 전문 연구기관 협력을 통한 객관적 계측·평가 체계 확보",
    " - 자체 개발만으로 확보하기 어려운 전문 측정 기술(진동 주파수 응답, RMS 가속도, 진폭, 비정상 구동 안전성)과 평가 지표 검토를 외부 전문 연구기관과 협력하여 확보하고자 함.",
    " - [KETI (한국전자기술연구원) 등] : 관련 시험 인프라 활용 및 신뢰성 평가 지원 프로그램을 검토 중이며, 제품의 진동 특성, 성능 및 신뢰성 평가를 위한 시험·분석 가능성을 타진할 계획임 (현재 확정 성과가 아닌 협력 타진 단계임).",
    "◦ 대체 기술 확보 경로 (기술이전 대안)",
    " - 연구기관 프로그램 추진과 병행하여, KETI 및 대학 연구기관이 기보유한 진동 제어 및 신뢰성 평가 관련 특허·연구성과의 기술이전 또는 실시권 확보 대안도 함께 조사·검토함.",
    "◦ 추진 팀 역량",
    " - 조영석(기술 총괄) : 공작기계 제조업체(DN솔루션즈) 구조·진동 CAE 시뮬레이션 엔지니어 3년 재직. 핵심 진동 메커니즘 설계, 회로 및 펌웨어 제어를 직접 수행함.",
    " - 오동규(사업 총괄) : Duke University MBA 졸업, 글로벌 리서치 기업 PM·세일즈 역량 보유. 시장 분석 및 조리원 B2B 제휴 전략을 총괄함.",
]

Q3_LINES = [
    "Q3. 성장전략(scale-up)",
    "※ 사업화 계획, 추진일정, 자금 소요 및 조달 계획",
    "1. 비즈니스 모델 및 단위 원가·수익 산식 구조",
    "◦ 초도 소량 배치(100~500대 기준) 대당 제조원가 산출 내역 (목표 추정치)",
    " - 본 원가 내역은 최종 확정 견적서가 아니며, 주요 전자부품 유통사 온라인 공시 단가 및 SMT·판금 임가공 업체의 사전 상담을 바탕으로 산정한 목표 원가 추정치임.",
    " - 부품 소량 사입 단가, 조립 공임 및 초기 A/S 예비비를 보수적으로 반영하여 대당 총 제조원가를 105,000원(약 10.5만 원)으로 산정함(초도 100~500대 기준 모델 추정치).",
    " - [순수 부품 자재비(BOM 목표 추정치) : 소계 91,000원]",
    "   * 메인 제어보드(PCBA): 25,000원 (ESP32 MCU, 오디오 앰프 IC, 부스트 전원부 실장 / 산출 근거: SMT 외주사 소량 임가공 상담 단가 추정치)",
    "   * 진동 구동 액추에이터: 22,000원 (좌우 대칭형 정밀 음향 엑사이터 2EA / 산출 근거: 부품 유통사 LCSC 소량 사입 단가 기준 추정치)",
    "   * 20mm 슬림 하우징 및 프레임: 26,000원 (알루미늄 절곡 판재 및 내부 ABS 스페이서 / 산출 근거: 수도권 판금 가공소 소량 제작 견적 추정치)",
    "   * 음향 출력 및 연결 부품: 10,000원 (저주파 음향 트랜스듀서, 인터페이스 케이블, 배선 하네스 / 산출 근거: 전자부품 유통사 소량 사입 단가 추정치)",
    "   * 전원 어댑터 및 개별 포장재: 8,000원 (KC인증 5V/3A 외장 전원 어댑터, Type-C 케이블, 완충 패키징 박스 / 산출 근거: 국내 전원 부품 유통사 초도 발주 단가 추정치)",
    " - [직접 제조 공임 및 품질 관리비 : 소계 14,000원]",
    "   * 조립 공임 및 출하 검수(QC): 6,000원 (기구 조립 및 주파수·진동 출력 전수 점검 공임 추정치)",
    "   * 초기 품질 보증 및 A/S 예비비: 8,000원 (초기 불량 무상 교체 및 A/S 대응 버퍼, 총 제조원가의 약 7.6% 반영)",
    " - [1,000대 이상 양산 시 원가 절감 목표 추정] : 간이금형 감가상각 종료(-10,000원), PCBA 릴 단위 대량 사입 및 자동화 공임 절감(-6,000원), 엑사이터 제조사 직납 계약(-4,000원)을 통해 대당 약 85,000원선으로 원가 절감 추진 목표(추정치).",
    "◦ 판매 및 렌탈 마진 산식 구조",
    " - [1차 B2B 산후조리원 공급 마진] : 대당 공급가 350,000원 기준 (수수료율 3.3% 통일 적용)",
    "   * 총 제조원가(추정치) 105,000원 차감 시 매출총이익 245,000원 (매출총이익률 70.0%)",
    "   * 직접 변동비 36,550원 차감: 화물 배송비 10,000원 + 조리원 현장 세팅/안내 공임 15,000원 + 결제/정산 수수료(공급가의 3.3%) 11,550원",
    "   * 직접 변동비 차감 후 공헌이익: 208,450원 (공헌이익률 약 59.6% 확보)",
    " - [후속 B2C 렌탈 투자회수 산식 및 운영 비용 상세 구조] : 월 렌탈료 29,900원 (6개월 의무 약정 기준, 후속 사업화 모델)",
    "   * 1) 월 정기 고정 공제비용 (월 소계 약 2,400원): PG 카드 결제 수수료(3.3%) 월 987원 + 고객 상담/CS 및 시스템 관리비 월 1,413원 공제 → 기본 운영 월 실수령액은 월 약 27,500원 수준임.",
    "   * 2) 회차별 변동 운영비용 (반납/재상품화 소계 약 13,000원): 6개월 약정 종료 후 기기 회수 입고 배송비(회당 약 5,000원 가정) + 전문 고온 살균 세척·소독비(회당 약 8,000원 외주 용역비 가정). 부품 점검 및 수리비는 BOM에 기 반영된 대당 A/S 예비비(8,000원) 내에서 충당함.",
    "   * 3) 공실 기간 리스크 가정: 사용자 간 반납 후 세척·점검 및 차기 사용자 재배송까지 평균 0.5~1개월의 유휴 공실 기간(기회비용)을 보수적으로 반영함.",
    "◦ B2C 렌탈 투자회수 기간 및 월차별 현금흐름 계산표",
    "구분 | 항목별 수치 및 산출 가정 | 회차/월 환산액 | 현금흐름 영향 및 산식",
    "초기 투자원금 (Hardware) | 총 제조원가 10.5만 원 + 초기 패키징·배송비 1.5만 원 | 일시 지출 (1회) | -120,000원 (대당 초기 투자금)",
    "월 렌탈 매출 (Revenue) | B2C 가정용 렌탈 이용료 (6개월 의무약정 기준) | 월 수령액 | +29,900원 / 월",
    "월 고정 운영비 (Opex) | PG 결제 수수료(3.3%, 987원) + 고객 CS·시스템비(1,413원) | 월 공제액 | -2,400원 / 월",
    "월 기본 순유입 (Gross Net) | 월 렌탈료(29,900원) - 월 고정 공제비(2,400원) | 월 실수령액 | +27,500원 / 월",
    "회수·세척비 (Refurbish) | 반납 배송비(5,000원) + 고온 살균 소독비(8,000원) | 6개월 주기 13,000원 | 월할 충당금 반영 시: -2,167원 / 월",
    "월 실질 순유입 (Real Net) | 월 기본 순유입(27,500원) - 월할 회수세척 충당금(2,167원) | 실질 순유입액 | +25,333원 / 월",
    "공실 기간 가정 (Vacancy) | 사용자 간 반납 후 세척·점검 및 차기 사용자 인도 대기 | 출고/이전 시 0.5~1개월 | 무수익 유휴 공실 기간 반영",
    "단순 원금 회수 기간 | 초기 투자금(120,000원) ÷ 월 기본 순유입액(27,500원) | 단순 산술 회수 | 약 4.36개월 (약 4.4개월)",
    "실질 원금 회수 기간 | 초기 투자금(120,000원) ÷ 월 실질 순유입액(25,333원) | 세척비 충당 후 | 약 4.74개월 (약 4.7개월)",
    "최종 실질 회수 시점 | 실질 회수 기간(4.74개월) + 초기/이전 유휴 공실(0.5~1.0개월) | 공실 위험 가산 | 약 5.2~5.7개월 (약 5~6개월차 회수 완결)",
    "* 6개월 의무 약정 만료 시 총 순유입액은 165,000원(27,500원 × 6개월)이며, 반납 시 회수·세척비(13,000원) 차감 후 실질 순회수액은 152,000원으로 초기 투자금(120,000원)을 초과 회수함.",
    "* 본 렌탈 모델은 1R 즉시 실행 모델이 아니며, 조리원 1차 현장 검증 완료 후 추진할 후속 B2C 확장 과제임.",
    "2. 1R 현장 검증 및 단계적 시장 진입 계획",
    "◦ 조리원 1~2개소 현장 협의 도입 조건의 단계화",
    " - [1단계: 1R 현장 협의 착수 조건 (현재 실행 기준)]",
    "   * 1) 설치 규격 적합성: 조리원 아크릴 바구니 카트(650×400mm 내외) 규격 내 단차 없는 삽입 확인.",
    "   * 2) 비영아 벤치 환경 협조: 신생아가 없는 별도 유휴 공간에서 3.5kg 더미를 활용한 비접촉 진동·소음 계측 공간 협조.",
    "   * 3) 현장 의견 청취: 야간 근무 간호인력 대상 조작 인터페이스 및 기능 요구사항 정성 인터뷰.",
    " - [2단계: 실증 후 상용 납품 추진 조건 (1R 검증 완료 후 후속 조건)]",
    "   * 1) 공학 벤치 안전 데이터 제출: 비영아 벤치 표면 진동(0.05~0.15g RMS), 투과 소음(50dBA 이하), 발열(40℃ 이하) 실측 보고서 사전 제출.",
    "   * 2) 위생 및 내화학성 공인 시험: 분리형 방수/방오 커버의 70% 에탄올 소독제 접촉 안전성 확인.",
    "   * 3) 법적 안전 분계 확보: 비의료기기 웰니스 가전 확인 및 제조물 책임(PL) 보험 가입 확약.",
    "   * 4) 도입 가격 합의: 베드당 350,000원 공급가에 대한 조리원 원장단 구매/도입 의향서(LOI) 체결.",
    "◦ 단계별 시장 진입 로드맵 및 잠재 인프라 시장 추정",
    " - [전국 조리원 인프라 잠재 시장 상한(TAM 약 44억 원 모델치)] : 보건복지부 전국 산후조리원 현황(2024년 기준 전국 약 680개소, 총 정원 약 12,500실)에 대당 공급가 350,000원을 적용한 전국 인프라 잠재 상한치는 약 43억 7,500만 원(개소당 평균 18.4실 기준)에서 약 44억 원(수도권 방문 조리원 평균 18.5실을 전국 680개소에 가설 적용 시 44억 300만 원) 수준임. 본 수치는 검증된 연간 시장(SAM)이 아니라 전국 전체 베드 일시 보급 가정의 이론적 상한치이며, 실제 사업화는 현장 1~2개소 실증부터 단계적으로 추진함.",
    " - [1단계 (1R)] : 초기 협력 조리원 1~2개소(약 30~40베드 규모) 발굴, 카트 규격 실측 및 비영아 벤치 테스트 수행.",
    " - [2단계 (2R)] : 비영아 벤치 측정 데이터 확보 후 협력 조리원 대상 시범 도입 타진 (무상 데모 후 유상 구매 전환 협의).",
    " - [3단계 (후속)] : 조리원 사용 경험을 바탕으로 퇴소 산모 대상 B2C 연계 렌탈 채널 구축.",
    "3. 비즈니스 운영 모델 벤치마크 (SNOO 및 KeePer Giken)",
    "◦ 렌탈 물류 프로세스 참고 (미국 SNOO)",
    " - 미국 SNOO는 본 제품의 수요나 효능을 입증하는 근거가 아니며, 배송·반납·세척·CS 고객지원이 결합된 가정용 렌탈 물류 운영 프로세스 설계를 위한 비즈니스 참고 모델로 한정함.",
    "◦ 현장 표준화 및 제휴망 구축 참고 (일본 KeePer Giken)",
    " - 일본 KeePer Giken 역시 본 제품의 수요 증빙이 아닌, 제품 신뢰성 확보 후 현장 설치 매뉴얼 표준화 및 제휴 네트워크를 단계적으로 확장하는 파트너십 운영 모델로 참고함.",
    "4. 1R 핵심 추진 일정 및 목표 (6주 실행계획)",
    "단계     | 주요 추진 내용                     | 목표 결과물",
    "1단계    | PCB #0006 벤치 구동 및 진동 출력 확인 | 물리적 진동 출력 여부 검증 및 회로 점검표",
    "2단계    | 전원부 발열 제어 및 연속 구동 시험  | 60분 부하 테스트 발열 측정 데이터",
    "3단계    | 비영아 벤치 매트리스 표면 진동 계측 | 3.5kg 더미 하중 하 가속도(RMS)·진폭 실측치",
    "4단계    | KETI 등 시험 인프라 협력 타진       | 외부 연구기관 시험 가능 항목 및 절차 확인",
    "5단계    | 협력 조리원(1~2개소) 현장 규격 검증  | 아크릴 카트 장착성 확인 및 현장 의견서",
    "6단계    | 1R 결과 종합 및 2R 고도화 계획 수립 | 1R 실측 데이터북 및 2R 개발 로드맵",
    "* 상기 단계는 연구기관 협력 검토와 기술이전 조사를 병행하여 추진함.",
    "5. 후속 연계 제휴 방안 (하나금융그룹 제안형)",
    "◦ 하나은행 저출생 대응 금융상품 연계 검토 (후속 연계)",
    " - 하나은행 '아이키움 적금' 등 영유아 관련 금융상품 가입 고객 대상 렌탈 할인 혜택 제공 방안 협의 제안.",
    "◦ 하나카드 렌탈 금융 시스템 연계 검토 (후속 연계)",
    " - 초기 일시불 구매 부담 완화를 위한 분할 렌탈 결제 시스템 도입 가능성 타진.",
    "◦ 그룹사 보육 시설 실증 제안 (후속 연계)",
    " - 향후 하드웨어 안전 검증 완료 시 하나금융 직장/국공립 어린이집 영아실 대상 시범 도입 가능성 타진.",
]

Q4_LINES = [
    "Q4. 향후 발전방안 (development)",
    "※ 중장기 아이템 고도화 및 사업 확장 계획",
    "1. 1R 핵심 과제: 하드웨어 공학 안전성 확보 및 규제·인증 대응",
    "◦ 전원부 발열 제어 및 실물 구동 안정성 확보 (최우선 과제)",
    " - 60분 연속 부하 구동 시 보드 전원부 및 하우징 외측 표면 발열을 잠정 내부 관리 목표치(표면 40℃ 이하, 주요 IC 75℃ 이하) 이내로 엄격히 제어함.",
    " - 비영아 벤치 환경에서 연속 부하 테스트를 수행하고, 이상 과열 시 전원을 물리적으로 차단하는 바이메탈 서멀 셧다운 보호 회로 동작을 벤치에서 실측 검증함.",
    "◦ 지식재산권 확보 및 청구항 설계",
    " - '언더매트리스 장착형 영아 미세진동 유도 장치 및 제어 방법'에 대한 특허 및 실용신안을 1R 협약 기간 내 출원 준비함.",
    " - 20mm 초슬림 복합 패드 구조, 대칭형 액추에이터 진동 감쇠 제어 로직을 핵심 청구항으로 구성하여 기술적 진입 장벽을 구축함.",
    "◦ 비의료기기 포지셔닝을 통한 인허가 리스크 사전 관리",
    " - 치료·의학적 진단 목적의 의료기기가 아닌, 수면 환경 개선을 위한 웰니스 생활가전으로 제품 범주를 명확히 정의하여 인허가 지연 리스크를 사전에 배제함.",
    " - 식약처 의료기기 해당 여부 공식 질의(민원 유권해석) 절차를 진행하여 비의료기기 해당 확인 공문을 확보하고 사업화 규제 불확실성을 완전히 해소함.",
    "◦ KC 인증 사전 대응 및 하드웨어 보호 설계",
    " - 신생아 피부 간접 접촉 가능성을 고려하여 무독성 실리콘 소재를 적용하고, 5V 외장 어댑터 직접 전원 공급 방식을 채택하여 배터리 발열·폭발 위험을 원천 차단함.",
    " - 역전압 방지 쇼트키 다이오드, 과전류 방지 복합 퓨즈(PTC), EMI/EMC 노이즈 필터를 전원 입력단에 실장하여 KC 전기용품안전 및 전자파 적합성 기준을 충족하도록 사전 회로 설계를 반영함.",
    "◦ 1R 멘토링 피드백 반영 및 양산 설계 보완",
    " - 하나은행 기술 멘토링 및 하드웨어 전문가 자문 의견을 수렴하여 초기 시작품의 내구성 취약 부위(케이블 인입부 스트레인 릴리프 단선 방지, 진동 피로 파손)를 사전 보강하고 양산 단가를 고려한 부품 공용화 설계를 진행함.",
    "2. 중장기 아이템 고도화 및 확장 가능성 (후속 연계 검토 과제)",
    "◦ 영아 수면 모니터링 SaaS 연계 검토 (후속 개발 과제)",
    " - 1R 하드웨어 안전 검증 완료 후, 각 패드의 동작 데이터 및 영아 수면 패턴을 연계 관리하는 조리원 화면 및 모바일 SaaS 솔루션 도입을 장기 과제로 검토함.",
    "◦ 제품 라인업 확장 가능성 (중장기 로드맵)",
    " - 0~6개월(신생아기): 언더매트리스 슬림 패드 (1R 핵심 타깃 단일 기본 모델에 집중).",
    " - 6~24개월(유아기): 1R 기본 모델 안정화 이후 뒤집힘 감지 센서를 포함한 유아용 매트 형태로 파생 모델 개발 검토.",
    " - 성인·시니어 케어 적용 검토: 미세 진동을 활용한 장기 요양 환자 체위 관리 보조용 매트로 원천 진동 구조의 장기적 응용 가능성 검토.",
]

ATTACHMENT_LINES = [
    "[붙임] 증빙 자료 기획 (최대 3장)",
    "1. 20mm 슬림 패드 구조도 및 매트리스 장착 개념도",
    " - [기확보 실적] 20mm 알루미늄-ABS 복합 슬림 목업 CAD 단면도 및 치수 도면.",
    " - [기확보 실적] 산후조리원 아크릴 바구니 카트 매트리스(650×400mm) 실측 치수 매핑 구조도.",
    "2. 30~60Hz 진동 주파수 응답 기초 해석 데이터 및 비영아 벤치 측정 계획",
    " - [기확보 실적] CAE 진동 감쇠율 기초 시뮬레이션 해석 그래프.",
    " - [1R 계획 증빙] 비영아 벤치(3.5kg 더미 모델) 3축 가속도계 부착 시험 구성도 및 매트리스 투과 진동 측정 계획서.",
    "3. 산후조리원 현장 방문 인터뷰 기록 및 협력 모델 구조도",
    " - [기확보 실적] 수도권 산후조리원 2개소 현장 방문, 원장단 인터뷰 메모 및 카트 실측 사진.",
    " - [후속 제휴 계획] 하나은행 적금 및 하나카드 렌탈 금융 연계 제안 구조도.",
]

ALL_SECTIONS = [
    ("HEADER", HEADER_LINES),
    ("Q1", Q1_LINES),
    ("Q2", Q2_LINES),
    ("Q3", Q3_LINES),
    ("Q4", Q4_LINES),
    ("ATTACHMENT", ATTACHMENT_LINES),
]

def build_markdown_and_txt():
    def format_section(lines):
        out = []
        for i, line in enumerate(lines):
            # Add blank line before numbered headings (e.g. "1. ", "2. ") if not at start
            if i > 0 and (re.match(r"^[1-5]\. ", line) or line.startswith("Q") or line.startswith("[붙임]")):
                out.append("")
            out.append(line)
        return "\n".join(out)

    content_blocks = []
    
    # Header block
    content_blocks.append("\n".join(HEADER_LINES[:3]) + "\n\n" + "\n".join(HEADER_LINES[3:6]) + "\n\n" + HEADER_LINES[6] + "\n" + "\n".join(HEADER_LINES[7:]))
    
    # Q1
    content_blocks.append(format_section(Q1_LINES))
    # Q2
    content_blocks.append(format_section(Q2_LINES))
    # Q3
    content_blocks.append(format_section(Q3_LINES))
    # Q4
    content_blocks.append(format_section(Q4_LINES))
    # Attachment
    content_blocks.append(format_section(ATTACHMENT_LINES))
    
    full_text = ("\n\n--------------------------------------------------\n\n").join(content_blocks) + "\n"
    return full_text

def build_docx(all_lines, output_path):
    doc = docx.Document()
    
    # Set page size to A4 (210mm x 297mm)
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    for line in all_lines:
        line_str = line.strip()
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.35
        
        # Style determination
        if line_str == "[표지]":
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(10.5)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
        elif line_str == "2026년 2차 모두의 창업 프로젝트":
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(15.0)
            run.bold = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
        elif line_str == "1R 사업계획서":
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(20.0)
            run.bold = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
        elif line_str.startswith("Q") and ("." in line_str) and ("(" in line_str):
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(13.0)
            run.bold = True
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
        elif line_str.startswith("[붙임]"):
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(13.0)
            run.bold = True
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
        elif line_str.startswith("※"):
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(100, 100, 100)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
        elif re.match(r"^[1-5]\. ", line_str) or line_str == "[아이템 요약]":
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(11.5)
            run.bold = True
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
        elif line_str.startswith("◦"):
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(10.5)
            run.bold = True
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(3)
        elif "|" in line_str:
            # Table line formatted as structured text
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(9.0)
            if any(h in line_str for h in ["주요 추진 내용", "통계 지표", "대상 항목", "산출 가정", "수치 및 산출"]):
                run.bold = True
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
        else:
            run = p.add_run(line_str)
            run.font.name = "맑은 고딕"
            run.font.size = Pt(10.5)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)

    doc.save(output_path)

def build_html(output_path):
    mentor_val = HEADER_LINES[3].split(":", 1)[1].strip()
    name_val = HEADER_LINES[4].split(":", 1)[1].strip()
    item_name_val = HEADER_LINES[5].split(":", 1)[1].strip()

    summary_paras = []
    for line in HEADER_LINES[7:]:
        summary_paras.append(f'        <p style="margin: 0 0 6px 0;">{line}</p>')
    summary_html = "\n".join(summary_paras)

    def section_lines_to_html(lines):
        res = []
        in_table = False
        table_rows = []
        for line in lines:
            line_str = line.strip()
            if "|" in line_str and not line_str.startswith("*"):
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append([c.strip() for c in line_str.split("|")])
                continue
            else:
                if in_table:
                    res.append('  <table class="content-table">')
                    for r_idx, row in enumerate(table_rows):
                        tag = "th" if r_idx == 0 else "td"
                        if r_idx == 0:
                            row_html = "".join([f"<{tag}>{c}</{tag}>" for c in row])
                        else:
                            row_html = f"<td><strong>{row[0]}</strong></td>" + "".join([f"<td>{c}</td>" for c in row[1:]])
                        res.append(f"    <tr>{row_html}</tr>")
                    res.append('  </table>')
                    in_table = False

            if line_str.startswith("Q") and ("." in line_str) and ("(" in line_str):
                res.append(f'  <div class="q-box">{line_str}</div>')
            elif line_str.startswith("[붙임]"):
                res.append(f'  <div class="q-box">{line_str}</div>')
            elif line_str.startswith("※"):
                res.append(f'  <div class="guide">{line_str}</div>')
            elif re.match(r"^[1-5]\. ", line_str):
                res.append(f'  <div class="sec-title">{line_str}</div>')
            elif line_str.startswith("◦"):
                res.append(f'  <div class="bullet-main">{line_str}</div>')
            else:
                safe_text = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                res.append(f'  <p>{safe_text}</p>')

        if in_table:
            res.append('  <table class="content-table">')
            for r_idx, row in enumerate(table_rows):
                tag = "th" if r_idx == 0 else "td"
                if r_idx == 0:
                    row_html = "".join([f"<{tag}>{c}</{tag}>" for c in row])
                else:
                    row_html = f"<td><strong>{row[0]}</strong></td>" + "".join([f"<td>{c}</td>" for c in row[1:]])
                res.append(f"    <tr>{row_html}</tr>")
            res.append('  </table>')
        return "\n".join(res)

    body_html_parts = []
    body_html_parts.append(section_lines_to_html(Q1_LINES))
    body_html_parts.append(section_lines_to_html(Q2_LINES))
    body_html_parts.append(section_lines_to_html(Q3_LINES))
    body_html_parts.append(section_lines_to_html(Q4_LINES))
    body_html_parts.append(section_lines_to_html(ATTACHMENT_LINES))
    sections_html = "\n\n".join(body_html_parts)

    html_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>2026년 2차 모두의 창업 프로젝트 1R 사업계획서 - 마중 (MAJN)</title>
<style>
  @page {{ size: A4; margin: 15mm; }}
  body {{
    font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    background: #e5e7eb;
    margin: 0;
    padding: 24px;
    color: #111827;
    line-height: 1.6;
  }}
  .toolbar {{
    max-width: 210mm;
    margin: 0 auto 16px auto;
    background: #1f2937;
    color: #fff;
    padding: 12px 20px;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .toolbar h2 {{ margin: 0; font-size: 15px; font-weight: 600; }}
  .toolbar button {{
    background: #2563eb;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
  }}
  .page {{
    width: 210mm;
    min-height: 297mm;
    box-sizing: border-box;
    margin: 0 auto 20px auto;
    background: #fff;
    padding: 20mm 20mm;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }}
  .header-area {{
    text-align: center;
    border-bottom: 2px solid #111;
    padding-bottom: 14px;
    margin-bottom: 20px;
  }}
  .header-area h2 {{ font-size: 14pt; margin: 0 0 6px 0; color: #4b5563; }}
  .header-area h1 {{ font-size: 22pt; margin: 0; letter-spacing: 4px; }}
  
  table.meta {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    font-size: 10pt;
  }}
  table.meta th {{
    background: #f3f4f6;
    border: 1px solid #9ca3af;
    padding: 6px 10px;
    width: 22%;
    text-align: center;
  }}
  table.meta td {{
    border: 1px solid #9ca3af;
    padding: 6px 10px;
  }}
  table.content-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 9.5pt;
  }}
  table.content-table th, table.content-table td {{
    border: 1px solid #cbd5e1;
    padding: 6px 8px;
  }}
  table.content-table th {{ background: #f1f5f9; text-align: center; font-weight: bold; }}
  
  .q-box {{
    background: #f3f4f6;
    border: 1px solid #6b7280;
    padding: 8px 12px;
    font-size: 12pt;
    font-weight: bold;
    margin: 22px 0 10px 0;
  }}
  .guide {{
    color: #6b7280;
    font-size: 9pt;
    margin: -6px 0 10px 4px;
  }}
  .sec-title {{
    font-size: 11pt;
    font-weight: bold;
    margin: 14px 0 6px 0;
    color: #1f2937;
  }}
  .bullet-main {{
    font-weight: bold;
    font-size: 10pt;
    margin: 8px 0 4px 6px;
    color: #111827;
  }}
  p {{
    margin: 4px 0 4px 14px;
    font-size: 9.8pt;
    text-align: justify;
  }}
  .divider {{
    border-top: 1px dashed #d1d5db;
    margin: 20px 0;
  }}
  @media print {{
    body {{ background: #fff; padding: 0; }}
    .toolbar {{ display: none; }}
    .page {{ box-shadow: none; margin: 0; padding: 15mm; }}
  }}
</style>
</head>
<body>

<div class="toolbar">
  <h2>모두의 창업 프로젝트 1R 사업계획서 웹 뷰어 (공식 양식 규격 동기화)</h2>
  <button onclick="window.print()">인쇄 / PDF 저장</button>
</div>

<div class="page">
  <div class="header-area">
    <h2>2026년 2차 모두의 창업 프로젝트</h2>
    <h1>1R 사업계획서</h1>
  </div>

  <table class="meta">
    <tr><th>멘토기관</th><td>{mentor_val}</td></tr>
    <tr><th>성명 (대표자)</th><td>{name_val}</td></tr>
    <tr><th>창업아이템명</th><td>{item_name_val}</td></tr>
    <tr>
      <th>아이템 요약</th>
      <td>
{summary_html}
      </td>
    </tr>
  </table>

  <div class="divider"></div>

{sections_html}
</div>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_code)

def main():
    print("[1/5] Building Markdown and TXT...")
    full_text = build_markdown_and_txt()
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_text)
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  -> Written to {MD_PATH}")
    print(f"  -> Written to {TXT_PATH}")
    
    print("[2/5] Building DOCX...")
    raw_lines = [l.strip() for l in full_text.splitlines() if l.strip() and not l.strip().startswith("---")]
    build_docx(raw_lines, DOCX_PATH)
    print(f"  -> Written to {DOCX_PATH}")
    
    print("[3/5] Building HTML...")
    build_html(HTML_PATH)
    print(f"  -> Written to {HTML_PATH}")
    
    print("[4/5] Running Self-Verification...")
    # 1. Byte-level diff between MD and TXT
    with open(MD_PATH, "rb") as f1, open(TXT_PATH, "rb") as f2:
        assert f1.read() == f2.read(), "MD and TXT do not match byte-for-byte!"
    print("  ✓ MD and TXT are 100% byte-for-byte identical.")
    
    # 2. Markdown forbidden syntax check
    forbidden = re.findall(r"(\*\*|##|`|\[.+?\]\(.+?\))", full_text)
    assert len(forbidden) == 0, f"Found forbidden markdown syntax: {forbidden}"
    print("  ✓ Pure official document style verified (0 markdown artifacts).")
    
    # 3. Line by line DOCX verification
    doc = docx.Document(DOCX_PATH)
    doc_paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    assert len(raw_lines) == len(doc_paras), f"Line mismatch: MD={len(raw_lines)} vs DOCX={len(doc_paras)}"
    for idx, (m, d) in enumerate(zip(raw_lines, doc_paras)):
        assert m == d, f"Mismatch at line {idx}:\nMD: {m}\nDOCX: {d}"
    print(f"  ✓ DOCX paragraphs match MD lines 100% ({len(raw_lines)} paragraphs).")
    
    # 4. Character counts per question
    sections = re.split(r"\n(?=Q[1-4]\. )", full_text)
    for s in sections[1:]:
        header = s.split("\n")[0]
        content = s.split("--------------------------------------------------")[0]
        no_ws = len("".join(content.split()))
        with_ws = len(content)
        assert no_ws >= 1000, f"{header} has only {no_ws} chars without whitespace (<1000)!"
        print(f"  ✓ {header[:25]}: {with_ws} chars (with ws), {no_ws} chars (no ws) -> PASS (>1,000 chars)")
        
    # 5. Key terms and numbers in HTML and MD
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    key_numbers = [
        "105,000원", "91,000원", "14,000원", "85,000원",
        "44억 원", "43억 7,500만 원", "18.5실", "18.4실", "12,500실",
        "350,000원", "208,450원", "59.6%", "11,550원",
        "4.4개월", "4.36개월", "4.74개월", "5~6개월", "27,500원", "25,333원", "2,167원", "987원", "1,413원", "5,000원", "8,000원", "13,000원",
        "120,000원", "165,000원", "152,000원",
        "0.05g~0.15g", "0.2mm", "50dBA", "40℃", "75℃",
        "84.2%", "75.0%", "8~12명"
    ]
    for num in key_numbers:
        assert num in html_content, f"Key metric '{num}' missing from HTML!"
        assert num in full_text, f"Key metric '{num}' missing from MD!"
    print(f"  ✓ All {len(key_numbers)} key metrics verified across all files.")
    
    print("\n[5/5] ALL GENERATION & VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
