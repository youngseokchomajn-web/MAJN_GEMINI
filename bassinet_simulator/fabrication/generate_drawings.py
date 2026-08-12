#!/usr/bin/env python3
"""
MAJN Nucu Pad v3.2 — 제작 도면 생성기 (Rev.C)
코어 450x250x20mm / 자작합판 4mm SE0~E0 / 측판 12mm 샌드위치
발주 의도서(2026-08-06) 반영: 상판 완전접착(무타공)+R20 / 하판 나사 분리형 6점 /
통합 삼각 코너블록(4mm 3겹 적층) / 장변 중앙 스크류보스 / 배선홀 측판 원형
출력: nucu_pad_v3_cnc.dxf (CNC 레이저 발주용) + nucu_pad_v3_drawing.svg (치수 도면 시트)
"""
import ezdxf
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── 확정 규격 (v3.2 Rev.C) ──────────────────────────────────
W, L = 450.0, 250.0          # 상하판 외경
T = 4.0                       # 합판 두께
WALL_H = 12.0                 # 측판 높이(=내부 유효고)
TOTAL_H = T + WALL_H + T      # 20.0
WALL_FB = (450.0, WALL_H)     # 전/후면 측판 2장
WALL_LR = (242.0, WALL_H)     # 좌/우 측판 2장 (250 - 2*4)
R_TOP = 20.0                  # 상판 코너 라운딩 (발주 단계 2D 가공)
EXC = [(112.5, 62.5), (337.5, 62.5), (112.5, 187.5), (337.5, 187.5)]  # 익사이터 중심
EXC_FOOT = (40.2, 19.5)       # TEAX14C02-8 VHB 배치 존 (높이 실측 9.85 확정 2026-08-06)
TRI_LEG = 30.0                # 통합 삼각 코너블록 다리 길이 (R20 백킹 조건 ≥25)
BOSS_W, BOSS_D = 40.0, 15.0   # 장변 중앙 스크류보스 (폭×깊이)
SCREW_D = 3.2                 # 하판 ⌀3 목나사 관통홀
PILOT_D = 2.0                 # 블록 파일럿 홀
CSK_D = 6.5                   # 하판 하면 카운터싱크(90°) 참고 지름
# 하판 나사 6점: 코너 4(삼각블록 물림) + 장변 중앙 2(보스 물림)
SCREWS = [(14, 14), (436, 14), (14, 236), (436, 236), (225, 11.5), (225, 238.5)]
CABLE_HOLE = (35.0, 8.0)      # 후면 측판 배선홀: 좌측 코너에서 35mm, ⌀8 (코너블록 30~40mm 이격)

# ══════════════════════════════ DXF ══════════════════════════════
doc = ezdxf.new("R2010", setup=True)
msp = doc.modelspace()
doc.layers.add("CUT", color=1)      # 빨강 = 절단
doc.layers.add("REF", color=3)      # 초록 = 참고(비절단) — 익사이터 VHB 존, 라벨
doc.layers.add("DRILL", color=5)    # 파랑 = 홀 (관통/파일럿)

BULGE_90 = math.tan(math.radians(90) / 4)  # 0.4142 — 90도 원호

def rect(x, y, w, h, layer="CUT"):
    msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                       close=True, dxfattribs={"layer": layer})

def rounded_rect(x, y, w, h, r, layer="CUT"):
    # 4코너 R 라운딩 사각형 (bulge 원호), CCW
    pts = [
        (x + r, y, 0), (x + w - r, y, BULGE_90),
        (x + w, y + r, 0), (x + w, y + h - r, BULGE_90),
        (x + w - r, y + h, 0), (x + r, y + h, BULGE_90),
        (x, y + h - r, 0), (x, y + r, BULGE_90),
    ]
    msp.add_lwpolyline([(px, py, 0, 0, b) for px, py, b in pts],
                       close=True, dxfattribs={"layer": layer})

def tri(x, y, leg, flip_x=False, flip_y=False, layer="CUT"):
    # 직각 삼각형 (다리 leg, 직각점 (x,y))
    dx = -leg if flip_x else leg
    dy = -leg if flip_y else leg
    msp.add_lwpolyline([(x, y), (x + dx, y), (x, y + dy)],
                       close=True, dxfattribs={"layer": layer})

def circle(cx, cy, d, layer="DRILL"):
    msp.add_circle((cx, cy), d / 2.0, dxfattribs={"layer": layer})

def label(x, y, text, h=6, layer="REF"):
    msp.add_text(text, dxfattribs={"layer": layer, "height": h}).set_placement((x, y))

GAP = 25
# ── 상판: 무타공 + R20, 익사이터 존은 REF ──
rounded_rect(0, 0, W, L, R_TOP)
for ex, ey in EXC:
    rect(ex - EXC_FOOT[0]/2, ey - EXC_FOOT[1]/2, EXC_FOOT[0], EXC_FOOT[1], layer="REF")
    circle(ex, ey, 2.0, layer="REF")
label(0, -12, "TOP 450x250x4 R20 — 무타공(완전접착), 익사이터 존=안쪽면 REF")

# ── 하판: 사각(라운딩 없음) + 나사 6점 관통 ⌀3.2 (하면 CSK ⌀6.5x90deg) ──
oy = L + GAP
rect(0, oy, W, L)
for sx_, sy_ in SCREWS:
    circle(sx_, oy + sy_, SCREW_D)
label(0, oy - 12, "BOTTOM 450x250x4 — 나사 6x D3.2 관통, 하면 CSK D6.5x90deg (분리형)")

# ── 측판 4장 ──
wy = 2 * (L + GAP)
rect(0, wy, *WALL_FB)
label(0, wy - 12, "WALL-FRONT 450x12x4 (그레인=길이방향 450 필수)")
y0 = wy + WALL_H + GAP
rect(0, y0, *WALL_FB)
circle(CABLE_HOLE[0], y0 + WALL_H/2, CABLE_HOLE[1])
label(0, y0 - 12, "WALL-REAR 450x12x4 — 배선홀 D8 @좌코너 35mm, 중간높이 (그레인=450)")
wy2 = y0 + WALL_H + GAP
rect(0, wy2, *WALL_LR)
label(0, wy2 - 12, "WALL-LEFT 242x12x4")
rect(WALL_LR[0] + GAP, wy2, *WALL_LR)
label(WALL_LR[0] + GAP, wy2 - 12, "WALL-RIGHT 242x12x4")

# ── 보강 블록 (정식 품목): 삼각 코너블록 4mm x 3겹 = 12장, 보스 3겹 = 6장 ──
by = wy2 + WALL_H + GAP + 10
label(0, by + TRI_LEG + 8, "CORNER-TRI 30x30 x12장 (3겹 적층->블록 4개, 파일럿 D2)", h=5)
for i in range(12):
    col, row = i % 6, i // 6
    tx, ty = col * (TRI_LEG + 10), by - row * (TRI_LEG + 10)
    tri(tx, ty, TRI_LEG)
    circle(tx + 11, ty + 11, PILOT_D)   # 파일럿 (하판 나사 위치 정합: 코너에서 14,14 - 벽 4mm 오프셋)
bx = 6 * (TRI_LEG + 10) + 20
label(bx, by + TRI_LEG + 8, "BOSS 40x15 x6장 (3겹->보스 2개, 파일럿 D2)", h=5)
for i in range(6):
    col, row = i % 3, i // 3
    px, py = bx + col * (BOSS_W + 10), by - row * (BOSS_D + 20)
    rect(px, py, BOSS_W, BOSS_D)
    circle(px + BOSS_W/2, py + BOSS_D/2, PILOT_D)

label(0, by + TRI_LEG + 34,
      "MAJN NUCU PAD v3.2 Rev.C CORE 450x250x20 | BIRCH PLY 4mm SE0/E0 | CUT=red DRILL=blue REF=green(NO CUT)", h=7)
label(0, by + TRI_LEG + 20,
      "별도자재: D3x12 접시 목나사 x6 / 목공본드(E0) / VHB 9473PC / 펠트 개스킷 1mm(하판 둘레) / EVA보더 별도", h=5)

dxf_path = os.path.join(OUT, "nucu_pad_v3_cnc.dxf")
doc.saveas(dxf_path)
print("DXF:", dxf_path)

# ══════════════════════════════ SVG 도면 시트 ══════════════════════════════
S = 1.6  # mm→px
def P(v): return v * S

def svg_rect(x, y, w, h, cls, rx=0):
    return f'<rect x="{P(x):.1f}" y="{P(y):.1f}" width="{P(w):.1f}" height="{P(h):.1f}" rx="{P(rx):.1f}" class="{cls}"/>'

def svg_circle(cx, cy, d, cls):
    return f'<circle cx="{P(cx):.1f}" cy="{P(cy):.1f}" r="{P(d/2):.1f}" class="{cls}"/>'

def svg_tri(x, y, leg, cls):
    return f'<path d="M {P(x):.1f} {P(y):.1f} L {P(x+leg):.1f} {P(y):.1f} L {P(x):.1f} {P(y+leg):.1f} Z" class="{cls}"/>'

def svg_text(x, y, t, cls="t", anchor="middle"):
    return f'<text x="{P(x):.1f}" y="{P(y):.1f}" class="{cls}" text-anchor="{anchor}">{t}</text>'

def hdim(x1, x2, y, t):
    return (f'<line x1="{P(x1):.1f}" y1="{P(y):.1f}" x2="{P(x2):.1f}" y2="{P(y):.1f}" class="dim"/>'
            f'<line x1="{P(x1):.1f}" y1="{P(y)-4:.1f}" x2="{P(x1):.1f}" y2="{P(y)+4:.1f}" class="dim"/>'
            f'<line x1="{P(x2):.1f}" y1="{P(y)-4:.1f}" x2="{P(x2):.1f}" y2="{P(y)+4:.1f}" class="dim"/>'
            + svg_text((x1+x2)/2, y - 2.2, t, "dt"))

def vdim(y1, y2, x, t):
    return (f'<line x1="{P(x):.1f}" y1="{P(y1):.1f}" x2="{P(x):.1f}" y2="{P(y2):.1f}" class="dim"/>'
            f'<line x1="{P(x)-4:.1f}" y1="{P(y1):.1f}" x2="{P(x)+4:.1f}" y2="{P(y1):.1f}" class="dim"/>'
            f'<line x1="{P(x)-4:.1f}" y1="{P(y2):.1f}" x2="{P(x)+4:.1f}" y2="{P(y2):.1f}" class="dim"/>'
            f'<text x="{P(x)+3:.1f}" y="{P((y1+y2)/2):.1f}" class="dt" text-anchor="start">{t}</text>')

OX, OY = 60, 55
svg_parts = ['<g>']
svg_parts.append(svg_text(OX + W/2, 22, "MAJN 누쿠 패드 v3.2 — 진동 코어 450×250×20mm 제작 도면 (Rev.C / 2026-08-06)", "title"))
svg_parts.append(svg_text(OX + W/2, 36, "자작합판 4.0mm SE0/E0급 · 상판 완전접착(무타공)·R20 / 하판 나사 분리형 6점 · 근거: 보고서 §7~§10 + 발주 의도서", "sub"))

# ── VIEW 1: 평면도(하판 기준 — 나사·블록 배치. 상판 무타공이므로 체결정보는 하판에 집중) ──
x0, y0 = OX, OY
svg_parts.append(svg_rect(x0, y0, W, L, "cut", rx=R_TOP))
for ex, ey in EXC:
    svg_parts.append(svg_rect(x0 + ex - EXC_FOOT[0]/2, y0 + ey - EXC_FOOT[1]/2, EXC_FOOT[0], EXC_FOOT[1], "ref"))
    svg_parts.append(svg_circle(x0 + ex, y0 + ey, 3, "refc"))
    svg_parts.append(svg_text(x0 + ex, y0 + ey - 14, f"EXC ({ex:g}, {ey:g})", "small"))
# 내벽선 + 삼각블록 + 보스 (참고)
svg_parts.append(svg_rect(x0 + T, y0 + T, W - 2*T, L - 2*T, "wallref"))
svg_parts.append(svg_tri(x0 + T, y0 + T, TRI_LEG, "block"))
svg_parts.append(f'<path d="M {P(x0+W-T):.1f} {P(y0+T):.1f} L {P(x0+W-T-TRI_LEG):.1f} {P(y0+T):.1f} L {P(x0+W-T):.1f} {P(y0+T+TRI_LEG):.1f} Z" class="block"/>')
svg_parts.append(f'<path d="M {P(x0+T):.1f} {P(y0+L-T):.1f} L {P(x0+T+TRI_LEG):.1f} {P(y0+L-T):.1f} L {P(x0+T):.1f} {P(y0+L-T-TRI_LEG):.1f} Z" class="block"/>')
svg_parts.append(f'<path d="M {P(x0+W-T):.1f} {P(y0+L-T):.1f} L {P(x0+W-T-TRI_LEG):.1f} {P(y0+L-T):.1f} L {P(x0+W-T):.1f} {P(y0+L-T-TRI_LEG):.1f} Z" class="block"/>')
svg_parts.append(svg_rect(x0 + 225 - BOSS_W/2, y0 + T, BOSS_W, BOSS_D, "block"))
svg_parts.append(svg_rect(x0 + 225 - BOSS_W/2, y0 + L - T - BOSS_D, BOSS_W, BOSS_D, "block"))
for sx_, sy_ in SCREWS:
    svg_parts.append(svg_circle(x0 + sx_, y0 + sy_, SCREW_D, "hole"))
# 배선홀 (후면=아래쪽 변 가정 표시)
svg_parts.append(svg_circle(x0 + CABLE_HOLE[0], y0 + L - T/2, CABLE_HOLE[1], "hole"))
svg_parts.append(svg_text(x0 + CABLE_HOLE[0] + 4, y0 + L + 9, "배선홀 ⌀8 @35 (후면 측판 중간높이)", "small", "start"))
svg_parts.append(svg_text(x0 + W/2, y0 + L/2 + 4, "평면도 — 상판 R20 무타공 / 하판 나사 6×⌀3.2(파랑) / 블록·보스(갈색)", "cap"))
svg_parts.append(hdim(OX, OX + W, OY - 10, "450"))
svg_parts.append(vdim(OY, OY + L, OX - 12, "250"))
svg_parts.append(hdim(OX, OX + EXC[0][0], OY + L + 20, "112.5"))
svg_parts.append(hdim(OX + EXC[0][0], OX + EXC[1][0], OY + L + 20, "225"))
svg_parts.append(vdim(OY, OY + EXC[0][1], OX + W + 14, "62.5"))
svg_parts.append(vdim(OY + EXC[0][1], OY + EXC[2][1], OX + W + 14, "125"))

# ── VIEW 2: 단면도 A-A ──
sx, sy = OX, OY + L + 52
sec_w = 150
svg_parts.append(svg_text(sx + sec_w/2, sy - 6, "단면 A-A (부분, 좌측 150mm)", "cap2"))
svg_parts.append(svg_rect(sx, sy, sec_w, T, "cut"))                       # top (완전접착)
svg_parts.append(svg_rect(sx, sy + T + WALL_H, sec_w, T, "cut"))          # bottom (분리형)
svg_parts.append(svg_rect(sx, sy + T, T, WALL_H, "cut"))                  # left wall
svg_parts.append(svg_rect(sx + T, sy + T, TRI_LEG, WALL_H, "block"))      # 통합블록(3겹 12mm)
svg_parts.append(svg_text(sx + T + TRI_LEG/2, sy + T + WALL_H/2 + 1.5, "블록 3겹", "small"))
svg_parts.append(svg_rect(sx + 92.5 - EXC_FOOT[1]/2, sy + T, EXC_FOOT[1], 9.85, "exc"))
svg_parts.append(svg_text(sx + 92.5, sy + T + 5.5, "EXC 9.85", "small"))
svg_parts.append(vdim(sy, sy + T, sx - 8, "4"))
svg_parts.append(vdim(sy + T, sy + T + WALL_H, sx - 8, "12"))
svg_parts.append(vdim(sy + T + WALL_H, sy + TOTAL_H, sx - 8, "4"))
svg_parts.append(vdim(sy, sy + TOTAL_H, sx - 22, "20"))
# 나사: 하판에서 블록으로 (상향 X — 하향 체결 표시)
svg_parts.append(f'<line x1="{P(sx+T+10):.1f}" y1="{P(sy+T+3):.1f}" x2="{P(sx+T+10):.1f}" y2="{P(sy+TOTAL_H+3):.1f}" class="bolt"/>')
svg_parts.append(svg_text(sx + T + 12, sy + TOTAL_H + 9, "⌀3×12 목나사(하판→블록, 파일럿 ⌀2)", "small", "start"))
svg_parts.append(svg_text(sx, sy + TOTAL_H + 18, "상판=E0 본드 완전접착(무타공) / 하판=나사 6점+펠트 개스킷 1mm(무본드)", "small", "start"))

# ── VIEW 3: 부품표 ──
bx0, by0 = OX + 190, sy - 2
rows = [
    ("①", "상판", "450 × 250 × 4 · R20", "1", "무타공, 익사이터 존=안쪽면"),
    ("②", "하판", "450 × 250 × 4", "1", "나사 6×⌀3.2 + 하면 CSK ⌀6.5"),
    ("③", "전면 측판", "450 × 12 × 4", "1", "그레인=450 필수"),
    ("④", "후면 측판", "450 × 12 × 4", "1", "배선홀 ⌀8 @코너 35mm·그레인=450"),
    ("⑤", "좌/우 측판", "242 × 12 × 4", "2", ""),
    ("⑥", "삼각 코너블록", "30×30, 4mm×3겹=12장", "블록4", "정식 품목·파일럿 ⌀2"),
    ("⑦", "스크류보스", "40×15, 4mm×3겹=6장", "보스2", "장변 중앙·파일럿 ⌀2"),
    ("⑧", "익사이터", "TEAX14C02-8 (H9.85 실측)", "4", "VHB 9473PC, 상판 안쪽면"),
    ("⑨", "목나사", "⌀3×12 접시", "6", "하판→블록, 개스킷 관통"),
    ("⑩", "펠트 개스킷", "1mm 스트립", "둘레", "하판-측판 사이 (래틀 방지)"),
    ("⑪", "EVA 보더", "두께 20, 경도 60~70C", "-", "배시넷 바닥 실측 후 재단"),
]
svg_parts.append(svg_text(bx0 + 62, by0 - 6, "부품표 (BOM)", "cap2", "start"))
rh = 13
for i, (no, nm, dim, qty, note) in enumerate(rows):
    yy = by0 + i * rh
    svg_parts.append(f'<rect x="{P(bx0):.1f}" y="{P(yy):.1f}" width="{P(250):.1f}" height="{P(rh):.1f}" class="tbl"/>')
    svg_parts.append(svg_text(bx0 + 6, yy + 9, no, "small", "start"))
    svg_parts.append(svg_text(bx0 + 18, yy + 9, nm, "small", "start"))
    svg_parts.append(svg_text(bx0 + 80, yy + 9, dim, "small", "start"))
    svg_parts.append(svg_text(bx0 + 168, yy + 9, f"×{qty}", "small", "start"))
    svg_parts.append(svg_text(bx0 + 192, yy + 9, note, "small", "start"))

# ── 주기(Notes) ──
ny0 = by0 + len(rows) * rh + 14
notes = [
    "1. 소재: 자작합판 4.0mm BB급↑ · SE0/E0(포름알데히드 저방출) 명시. 그레인=장변 방향 필수(해석 전제+측판 파손 방지).",
    "2. 조립: 상판·측판·블록 = E0급 목공본드 완전접착(무타공 매끈 외관). 하판 = 무본드, ⌀3×12 목나사 6점(AS 분리형).",
    "3. 삼각 코너블록(다리 30)은 R20 백킹 조건 — 측판 높이 12mm 전체 충전 + 상단 플러시 접착 필수.",
    "4. 익사이터 4개 VHB로 [상판 안쪽면] 부착 → 직렬 16Ω/채널, 후면 배선홀(⌀8, 코너 35mm 이격)로 인출 + 그로밋.",
    "5. 마감: 방수 실링 + 어린이제품 유해물질 기준(E0/E1) 도료. 조립 후 세로 모서리 후가공 라운드(사포/라우터).",
    "6. 검수: 총높이 20.0±0.3 · 15kg 중앙 정적 휨 ≤2.3mm · 하판 나사 체결 후 래틀 없음(프로토콜 G6).",
    "7. 레이저 kerf 0.1~0.2mm 보정. 블록·보스는 자투리 아닌 정식 수량 품목(누락 금지).",
]
svg_parts.append(svg_text(bx0, ny0, "주기 (NOTES)", "cap2", "start"))
for i, n in enumerate(notes):
    svg_parts.append(svg_text(bx0, ny0 + 11 + i * 11, n, "note", "start"))
svg_parts.append('</g>')

width_px = P(W + 130)
height_px = P(ny0 + 11 + len(notes) * 11 + 20)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px:.0f} {height_px:.0f}" font-family="'Noto Sans KR', sans-serif">
<style>
  .cut {{ fill: none; stroke: #d92b2b; stroke-width: 1.6; }}
  .ref {{ fill: rgba(16,150,80,0.10); stroke: #0d8a4f; stroke-width: 1.1; stroke-dasharray: 5 3; }}
  .refc {{ fill: none; stroke: #0d8a4f; stroke-width: 1; }}
  .wallref {{ fill: none; stroke: #999; stroke-width: 0.8; stroke-dasharray: 3 3; }}
  .hole {{ fill: none; stroke: #1550c9; stroke-width: 1.4; }}
  .block {{ fill: rgba(180,120,40,0.25); stroke: #8a5a1d; stroke-width: 1; }}
  .exc {{ fill: rgba(16,150,80,0.2); stroke: #0d8a4f; stroke-width: 1; }}
  .bolt {{ stroke: #1550c9; stroke-width: 1.6; stroke-dasharray: 6 2; }}
  .dim {{ stroke: #444; stroke-width: 0.9; }}
  .tbl {{ fill: none; stroke: #777; stroke-width: 0.7; }}
  .title {{ font-size: 17px; font-weight: 700; fill: #111; }}
  .sub {{ font-size: 11.5px; fill: #555; }}
  .cap {{ font-size: 12px; fill: #666; }}
  .cap2 {{ font-size: 12.5px; font-weight: 700; fill: #222; }}
  .dt {{ font-size: 11px; fill: #222; }}
  .small {{ font-size: 10.5px; fill: #333; }}
  .note {{ font-size: 11px; fill: #333; }}
</style>
<rect width="100%" height="100%" fill="#fdfdfb"/>
{chr(10).join(svg_parts)}
</svg>'''

svg_path = os.path.join(OUT, "nucu_pad_v3_drawing.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)
print("SVG:", svg_path)
