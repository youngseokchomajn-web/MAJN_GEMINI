# 마중 PCB — ECO TODO (SSOT v1.9.0 → PCB 반영)

Fresh-eye 재검증으로 확정된 SSOT 보정을 PCB에 반영하는 작업. **설계(design_flow)는 완료·커밋됨. PCB 물리반영만 남음.**
⚠️ **브릿지로 PCB 부품추가 불가**(pcb_PrimitiveComponent/lib_Device create 메서드 없음) → UI ECO 필요.

## 반영할 변경 (3저항 + 1넷변경)
| 부품 | 값/LCSC | 배치(근처) | 배선 |
|---|---|---|---|
| **R12** | 4.7k / C23162 | U4 핀3 (1460,1580 mil) | U4/3↔R12/1(**AMP_ADR**), R12/2→VCC_3V3. **U4/3 기존 GND배선 제거** |
| **R13** | 10k / C25804 | U4 핀12 (PDN) 근처 | AMP_PDN↔R13/1, R13/2→VCC_3V3 |
| **R14** | 10k / C25804 | U5 핀12 (CS) 근처 | SPI_CS↔R14/1, R14/2→VCC_3V3 |

## 권장 절차 (안전한 ECO)
1. **회로도 재생성**: `run_draw_schematic.py`로 보정 SSOT(v1.9.0) 반영 → R12/R13/R14 + AMP_ADR 넷 + U4/3 GND분리 반영.
2. **EasyEDA "Update PCB"**(Import Changes) → ECO로 3저항 추가 + 넷변경, **기존 배치/배선은 보존**.
3. **배치**: R12/R13/R14를 위 위치에. (de-overlap 주의 — 디커플링처럼 핀근접)
4. **배선**: 짧은 연결 + U4/3 기존 GND트레이스 삭제 후 R12로.
5. **pour 재충전(Shift+B) → 재시작 후 권위 DRC 1회**.
6. **검증**: 100% 라우팅 유지, clearance 신규 0, 넷 일관성.

## 같은 ECO에서 함께 처리 권장
- **EP 써멀비아 net='' (보류중)**: TAS5805M 풋프린트 EP 비아가 net='' → **풋프린트 에디터에서 EP비아에 GND 할당**(인스턴스 setState_Net 미반영·재생성됨). 또는 무해 아티팩트로 문서화.
- **FW 주의**: ADR은 PVDD 인가 후 PDN 100ms 유지 뒤 샘플(Table 7-5). 펌웨어 부팅시퀀스 반영.

## 검증완료 / 변경불요 (참고)
- IMU(U5) pin8=VDD 정상(스왑 아님), MP3426 핀정상, D1 SMAJ5.0A 유지(Vbr 6.4V>5.25V).
- 출력필터·SPI·I2S·부스트 토폴로지 등 정상.
