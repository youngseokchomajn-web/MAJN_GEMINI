#!/usr/bin/env python3
"""
MAJN Nucu Pad v3 — 제작 도면 생성기
코어 450x250x20mm / 자작합판 4mm / 측판 12mm 샌드위치 (v3.1: 캐비티 12mm — 익사이터 바터밍 방지)
출력: nucu_pad_v3_cnc.dxf (CNC 레이저 발주용) + nucu_pad_v3_drawing.svg (치수 도면 시트)
"""
import ezdxf
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── 확정 규격 ──────────────────────────────────────────────
W, L = 450.0, 250.0          # 상하판 외경
T = 4.0                       # 합판 두께
WALL_H = 12.0                 # 측판 높이(=내부 유효고, v3.1: 10→12 상향 — 15kg 상판 꺼짐 1.8mm + 익사이터 9.55~9.85 여유)
TOTAL_H = T + WALL_H + T      # 20.0
WALL_FB = (450.0, WALL_H)     # 전/후면 측판 2장
WALL_LR = (242.0, WALL_H)     # 좌/우 측판 2장 (250 - 2*4)
EXC = [(112.5, 62.5), (337.5, 62.5), (112.5, 187.5), (337.5, 187.5)]  # 익사이터 중심
EXC_FOOT = (40.2, 19.5)       # TEAX14C02-8 풋프린트 (⚠발주 전 데이터시트/실측 확정: 40.2x19.5 vs 37x20 상충)
HOLE_D = 3.2                  # M3 관통홀
CSK_D = 6.5                   # 상판 카운터싱크(90°) 참고 지름
# 체결 블록(각재 20x20x12) 중심: 코너 4 + 변 중앙 4 — 벽 안쪽 밀착(벽 4 + 블록 반폭 10 = 14)
BOLTS = [(14, 14), (436, 14), (14, 236), (436, 236),
         (225, 14), (225, 236), (14, 125), (436, 125)]
CABLE_NOTCH = (225.0, 10.0, 6.0)  # 후면 측판 케이블 노치: 중심x, 폭, 깊이

# ══════════════════════════════ DXF ══════════════════════════════
doc = ezdxf.new("R2010", setup=True)
msp = doc.modelspace()
doc.layers.add("CUT", color=1)      # 빨강 = 절단
doc.layers.add("REF", color=3)      # 초록 = 참고(비절단) — 익사이터 VHB 존, 라벨
doc.layers.add("DRILL", color=5)    # 파랑 = 홀

def rect(x, y, w, h, layer="CUT"):
    msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                       close=True, dxfattribs={"layer": layer})

def circle(cx, cy, d, layer="DRILL"):
    msp.add_circle((cx, cy), d / 2.0, dxfattribs={"layer": layer})

def label(x, y, text, h=6, layer="REF"):
    msp.add_text(text, dxfattribs={"layer": layer, "height": h}).set_placement((x, y))

def panel_with_holes(ox, oy, name, top=False):
    rect(ox, oy, W, L)
    for bx, by in BOLTS:
        circle(ox + bx, oy + by, HOLE_D)
    if top:
        for ex, ey in EXC:  # 익사이터 VHB 존은 안쪽면 기준 — 참고선
            rect(ox + ex - EXC_FOOT[0]/2, oy + ey - EXC_FOOT[1]/2, *EXC_FOOT, layer="REF")
            circle(ox + ex, oy + ey, 2.0, layer="REF")
    label(ox, oy - 12, name)

GAP = 25
# 상판 / 하판
panel_with_holes(0, 0, "TOP 450x250x4 (홀 8x D3.2, 상면 CSK D6.5x90deg / 익사이터 존=안쪽면 참고)", top=True)
panel_with_holes(0, L + GAP, "BOTTOM 450x250x4 (홀 8x D3.2)")
# 측판 4장
wy = 2 * (L + GAP)
rect(0, wy, *WALL_FB)
label(0, wy - 12, "WALL-FRONT 450x12x4")
# 후면 측판: 케이블 노치(하단 중앙, 폭10 x 깊이6)
nx, nw, nd = CABLE_NOTCH
y0 = wy + WALL_H + GAP
msp.add_lwpolyline([
    (0, y0), (0, y0 + WALL_H), (450, y0 + WALL_H), (450, y0),
    (nx + nw/2, y0), (nx + nw/2, y0 + nd), (nx - nw/2, y0 + nd), (nx - nw/2, y0)
], close=True, dxfattribs={"layer": "CUT"})
label(0, y0 - 12, "WALL-REAR 450x12x4 (케이블 노치 10x6 @중앙)")
wy2 = y0 + WALL_H + GAP
rect(0, wy2, *WALL_LR)
label(0, wy2 - 12, "WALL-LEFT 242x12x4")
rect(WALL_LR[0] + GAP, wy2, *WALL_LR)
label(WALL_LR[0] + GAP, wy2 - 12, "WALL-RIGHT 242x12x4")
label(0, wy2 + WALL_H + 18,
      "MAJN NUCU PAD v3.1 CORE 450x250x20 | BIRCH PLY 4mm | CUT=red DRILL=blue REF=green(NO CUT)", h=7)
label(0, wy2 + WALL_H + 32,
      "별도자재: 체결블록 각재 20x20x12 x8 (D3.2 관통) / M3x25 접시볼트+너트 x8 / 목공본드(E0급) / EVA보더 별도", h=5)

dxf_path = os.path.join(OUT, "nucu_pad_v3_cnc.dxf")
doc.saveas(dxf_path)
print("DXF:", dxf_path)

# ══════════════════════════════ SVG 도면 시트 ══════════════════════════════
S = 1.6  # mm→px
def P(v): return v * S

def svg_rect(x, y, w, h, cls, rx=0):
    return f'<rect x="{P(x):.1f}" y="{P(y):.1f}" width="{P(w):.1f}" height="{P(h):.1f}" rx="{rx}" class="{cls}"/>'

def svg_circle(cx, cy, d, cls):
    return f'<circle cx="{P(cx):.1f}" cy="{P(cy):.1f}" r="{P(d/2):.1f}" class="{cls}"/>'

def svg_text(x, y, t, cls="t", anchor="middle"):
    return f'<text x="{P(x):.1f}" y="{P(y):.1f}" class="{cls}" text-anchor="{anchor}">{t}</text>'

def hdim(x1, x2, y, t):  # 수평 치수선
    return (f'<line x1="{P(x1):.1f}" y1="{P(y):.1f}" x2="{P(x2):.1f}" y2="{P(y):.1f}" class="dim"/>'
            f'<line x1="{P(x1):.1f}" y1="{P(y)-4:.1f}" x2="{P(x1):.1f}" y2="{P(y)+4:.1f}" class="dim"/>'
            f'<line x1="{P(x2):.1f}" y1="{P(y)-4:.1f}" x2="{P(x2):.1f}" y2="{P(y)+4:.1f}" class="dim"/>'
            + svg_text((x1+x2)/2, y - 2.2, t, "dt"))

def vdim(y1, y2, x, t):  # 수직 치수선
    return (f'<line x1="{P(x):.1f}" y1="{P(y1):.1f}" x2="{P(x):.1f}" y2="{P(y2):.1f}" class="dim"/>'
            f'<line x1="{P(x)-4:.1f}" y1="{P(y1):.1f}" x2="{P(x)+4:.1f}" y2="{P(y1):.1f}" class="dim"/>'
            f'<line x1="{P(x)-4:.1f}" y1="{P(y2):.1f}" x2="{P(x)+4:.1f}" y2="{P(y2):.1f}" class="dim"/>'
            f'<text x="{P(x)+3:.1f}" y="{P((y1+y2)/2):.1f}" class="dt" text-anchor="start">{t}</text>')

# 도면 원점 오프셋 (top view)
OX, OY = 60, 55
def tv(x, y): return (OX + x, OY + y)  # top-view 좌표계

parts = []
parts.append('<g>')
parts.append(svg_text(OX + W/2, 22, "MAJN 누쿠 패드 v3.1 — 진동 코어 450×250×20mm 제작 도면 (Rev.B / 2026-08-04)", "title"))
parts.append(svg_text(OX + W/2, 36, "자작합판(Birch Plywood) 4.0mm · 축척 1:1(mm) · 근거: NUCU_PAD_ULTRA_SLIM_ENGINEERING_REPORT.md §4·§7 (d7668df)", "sub"))

# ── VIEW 1: 평면도(상판, 안쪽면 기준) ──
x0, y0 = tv(0, 0)
parts.append(svg_rect(x0, y0, W, L, "cut"))
for ex, ey in EXC:
    parts.append(svg_rect(x0 + ex - EXC_FOOT[0]/2, y0 + ey - EXC_FOOT[1]/2, EXC_FOOT[0], EXC_FOOT[1], "ref"))
    parts.append(svg_circle(x0 + ex, y0 + ey, 3, "refc"))
    parts.append(svg_text(x0 + ex, y0 + ey - 14, f"EXC ({ex:g}, {ey:g})", "small"))
for bx, by in BOLTS:
    parts.append(svg_circle(x0 + bx, y0 + by, HOLE_D, "hole"))
# 내벽선(참고)
parts.append(svg_rect(x0 + T, y0 + T, W - 2*T, L - 2*T, "wallref"))
parts.append(svg_text(x0 + W/2, y0 + L/2 + 4, "평면도 — 상판 안쪽면 (익사이터 VHB 존 40.2×19.5*, 홀 8×⌀3.2)", "cap"))

svg_parts = parts
svg_parts.append(hdim(OX, OX + W, OY - 10, "450"))
svg_parts.append(vdim(OY, OY + L, OX - 12, "250"))
svg_parts.append(hdim(OX, OX + EXC[0][0], OY + L + 12, "112.5"))
svg_parts.append(hdim(OX + EXC[0][0], OX + EXC[1][0], OY + L + 12, "225"))
svg_parts.append(vdim(OY, OY + EXC[0][1], OX + W + 14, "62.5"))
svg_parts.append(vdim(OY + EXC[0][1], OY + EXC[2][1], OX + W + 14, "125"))

# ── VIEW 2: 단면도 A-A (두께 스택) ──
sx, sy = OX, OY + L + 45
SCALE_SEC = 3.0  # 단면 세로 과장 없음, 가로 축소 표시 위해 부분 단면 150mm만
sec_w = 150
svg_parts.append(svg_text(sx + sec_w/2, sy - 6, "단면 A-A (부분, 좌측 150mm)", "cap2"))
# 상판/하판/벽/블록
svg_parts.append(svg_rect(sx, sy, sec_w, T, "cut"))                       # top
svg_parts.append(svg_rect(sx, sy + T + WALL_H, sec_w, T, "cut"))          # bottom
svg_parts.append(svg_rect(sx, sy + T, T, WALL_H, "cut"))                  # left wall
svg_parts.append(svg_rect(sx + T, sy + T, 20, WALL_H, "block"))           # corner block
svg_parts.append(svg_text(sx + T + 10, sy + T + WALL_H/2 + 1.5, "블록", "small"))
svg_parts.append(svg_rect(sx + 92.5 - EXC_FOOT[1]/2, sy + T, EXC_FOOT[1], 9.55, "exc"))
svg_parts.append(svg_text(sx + 92.5, sy + T + 5.5, "EXC 9.55*", "small"))
svg_parts.append(vdim(sy, sy + T, sx - 8, "4"))
svg_parts.append(vdim(sy + T, sy + T + WALL_H, sx - 8, "12"))
svg_parts.append(vdim(sy + T + WALL_H, sy + TOTAL_H, sx - 8, "4"))
svg_parts.append(vdim(sy, sy + TOTAL_H, sx - 22, "20"))
# 볼트 상징선
svg_parts.append(f'<line x1="{P(sx+T+10):.1f}" y1="{P(sy-3):.1f}" x2="{P(sx+T+10):.1f}" y2="{P(sy+TOTAL_H+3):.1f}" class="bolt"/>')
svg_parts.append(svg_text(sx + T + 10, sy + TOTAL_H + 9, "M3×25 CSK", "small"))

# ── VIEW 3: 부품표 ──
bx0, by0 = OX + 190, sy - 2
rows = [
    ("①", "상판", "450 × 250 × 4", "1", "홀 8×⌀3.2 + 상면 CSK ⌀6.5"),
    ("②", "하판", "450 × 250 × 4", "1", "홀 8×⌀3.2"),
    ("③", "전면 측판", "450 × 12 × 4", "1", "결 방향 무관"),
    ("④", "후면 측판", "450 × 12 × 4", "1", "케이블 노치 10×6 중앙"),
    ("⑤", "좌/우 측판", "242 × 12 × 4", "2", ""),
    ("⑥", "체결 블록", "20 × 20 × 12 각재", "8", "⌀3.2 관통, 별도 재단"),
    ("⑦", "익사이터", "TEAX14C02-8", "4", "VHB 9473PC, 상판 안쪽면"),
    ("⑧", "볼트/너트", "M3×25 접시 + 너트", "8", "0.8 N·m"),
    ("⑨", "EVA 보더", "두께 20, 경도 60~70C", "-", "배시넷 바닥 실측 후 재단"),
]
svg_parts.append(svg_text(bx0 + 62, by0 - 6, "부품표 (BOM)", "cap2", "start"))
rh = 13
for i, (no, nm, dim, qty, note) in enumerate(rows):
    yy = by0 + i * rh
    svg_parts.append(f'<rect x="{P(bx0):.1f}" y="{P(yy):.1f}" width="{P(245):.1f}" height="{P(rh):.1f}" class="tbl"/>')
    svg_parts.append(svg_text(bx0 + 6, yy + 9, no, "small", "start"))
    svg_parts.append(svg_text(bx0 + 18, yy + 9, nm, "small", "start"))
    svg_parts.append(svg_text(bx0 + 78, yy + 9, dim, "small", "start"))
    svg_parts.append(svg_text(bx0 + 152, yy + 9, f"×{qty}", "small", "start"))
    svg_parts.append(svg_text(bx0 + 170, yy + 9, note, "small", "start"))

# ── 주기(Notes) ──
ny0 = by0 + len(rows) * rh + 14
notes = [
    "1. 소재: 자작합판 4.0mm BB급↑, 결 방향=장변(450) 필수(해석 전제). 레이저 kerf 0.1~0.2 보정.",
    "2. 조립: 완전 접착 밀폐 — E0급 목공본드 전둘레 + 체결블록⑥ 8개소 M3×25 관통볼트(0.8N·m). 밀폐 후 AS 불가.",
    "3. 익사이터 4개 VHB로 [상판 안쪽면] 지정 위치 부착 → 배선 직렬 16Ω/채널, 후면 노치로 인출.",
    "4. 마감: 방수 실링 + 어린이제품 유해물질 기준(E0/E1) 도료. 외곽 모서리 R3 이상 + 사포.",
    "5. 검수: 총높이 20.0±0.3 · 15kg 중앙 정적 휨 ≤2.3mm · 익사이터 치수 실측 확인(9.55* vs 9.85 상충).",
    "6. EVA 보더⑨는 배시넷 바닥 내치수 실측 후 별도 도면 (조리원 카트 720×390 기준 예상).",
]
svg_parts.append(svg_text(bx0, ny0, "주기 (NOTES)", "cap2", "start"))
for i, n in enumerate(notes):
    svg_parts.append(svg_text(bx0, ny0 + 11 + i * 11, n, "note", "start"))
svg_parts.append('</g>')

width_px = P(W + 130)
height_px = P(ny0 + 11 + len(notes) * 11 + 20)  # 노트 마지막 줄까지 포함
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
  text {{ dominant-baseline: auto; }}
</style>
<rect width="100%" height="100%" fill="#fdfdfb"/>
{chr(10).join(svg_parts)}
</svg>'''

svg_path = os.path.join(OUT, "nucu_pad_v3_drawing.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)
print("SVG:", svg_path)
