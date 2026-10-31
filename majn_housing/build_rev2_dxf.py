"""
Script to generate official Rev 2 DXF files using ezdxf.
Outputs:
1. majung_bassinet_4.5T_rev2_master.dxf (Birch plywood nesting)
2. majung_silicone_gasket_rev2.dxf (Silicone gasket)
"""

import math
import ezdxf
from rev2_params import *

def add_rounded_rect(msp, x0, y0, w, h, r, layer="CUT", color=1):
    """
    Draw a rectangle with 4 rounded corners using LWPOLYLINE and bulge.
    bulge = tan(pi / 8) = 0.41421356237309503
    """
    bulge = math.tan(math.pi / 8)
    # Start at bottom edge before bottom-right arc
    points = [
        (x0 + w - r, y0, 0, 0, bulge),
        (x0 + w, y0 + r, 0, 0, 0),
        (x0 + w, y0 + h - r, 0, 0, bulge),
        (x0 + w - r, y0 + h, 0, 0, 0),
        (x0 + r, y0 + h, 0, 0, bulge),
        (x0, y0 + h - r, 0, 0, 0),
        (x0, y0 + r, 0, 0, bulge),
        (x0 + r, y0, 0, 0, 0)
    ]
    poly = msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer, "color": color})
    return poly

def add_rect(msp, x0, y0, w, h, layer="CUT", color=1):
    points = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    return msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer, "color": color})

def add_circle(msp, cx, cy, r, layer="HOLE", color=5):
    return msp.add_circle((cx, cy), r, dxfattribs={"layer": layer, "color": color})

def add_text(msp, text, insert, height=5.0, layer="TEXT", color=7):
    return msp.add_text(text, dxfattribs={"layer": layer, "color": color, "height": height, "insert": insert})

def build_wood_master_dxf(filename="majung_bassinet_4.5T_rev2_master.dxf"):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Create Standard Layers
    doc.layers.add("CUT", color=1)      # Red (Cut path)
    doc.layers.add("HOLE", color=5)     # Blue (Holes)
    doc.layers.add("INFO", color=3)     # Green (Laser low-power marking)
    doc.layers.add("DIM", color=2)      # Yellow (Dimensions)
    doc.layers.add("TEXT", color=7)     # White/Black (Notes)

    # 1. TOP PLATE (450 x 250 mm) at (0, 0)
    add_rounded_rect(msp, 0, 0, ENCLOSURE_W, ENCLOSURE_D, CORNER_R, layer="CUT", color=1)
    add_text(msp, "1. TOP PLATE (450x250x4.5mm, QTY 1, EDGE ROUNDOVER R1~R2)", (25, 20), height=4.5)
    
    # Exciter INFO Markings on Top Plate (Underside orientation)
    # Rectangular 37 x 20 mm + Center Circle d=14 mm + Crosshairs
    for ex, ey in EXCITER_COORDS:
        # 37 x 20 Rect centered at (ex, ey)
        rx = ex - EXCITER_W / 2.0
        ry = ey - EXCITER_D / 2.0
        add_rect(msp, rx, ry, EXCITER_W, EXCITER_D, layer="INFO", color=3)
        # Center Voice Coil Circle
        add_circle(msp, ex, ey, VOICE_COIL_D / 2.0, layer="INFO", color=3)
        # Crosshair lines
        msp.add_line((ex - 10, ey), (ex + 10, ey), dxfattribs={"layer": "INFO", "color": 3})
        msp.add_line((ex, ey - 7), (ex, ey + 7), dxfattribs={"layer": "INFO", "color": 3})
        add_text(msp, "TEAX14C02 (37x20)", (ex - 18, ey - 16), height=2.8, layer="INFO", color=3)

    # 2. BOTTOM PLATE (450 x 250 mm) at (0, 280)
    y_bot = 280.0
    add_rounded_rect(msp, 0, y_bot, ENCLOSURE_W, ENCLOSURE_D, CORNER_R, layer="CUT", color=1)
    add_text(msp, "2. BOTTOM PLATE (450x250x4.5mm, QTY 1, 10-DIA 3.2 C/S HOLES)", (25, y_bot + 20), height=4.5)

    # 10 Bolt Clearance Holes (dia 3.2 mm) on Bottom Plate
    for bx, by in BOLT_COORDS:
        add_circle(msp, bx, y_bot + by, HOLE_BOLT_THROUGH / 2.0, layer="HOLE", color=5)
        # Countersink marking circle (d = 6.5 mm) for operator visual reference
        add_circle(msp, bx, y_bot + by, HOLE_COUNTERSINK_D / 2.0, layer="INFO", color=3)

    # 3. LONG SIDE RAILS (410 x 13.5 mm, QTY: 2) at (0, 560) and (0, 582)
    add_rect(msp, 0, 560, RAIL_LONG_L, RAIL_LONG_H, layer="CUT", color=1)
    add_rect(msp, 0, 582, RAIL_LONG_L, RAIL_LONG_H, layer="CUT", color=1)
    add_text(msp, "3. SIDE RAIL LONG (410x13.5x4.5mm, QTY 2)", (10, 563.5), height=3.5)

    # 4. SHORT SIDE RAILS (210 x 13.5 mm, QTY: 2) at (0, 610) and (0, 632)
    add_rect(msp, 0, 610, RAIL_SHORT_L, RAIL_SHORT_H, layer="CUT", color=1)
    add_rect(msp, 0, 632, RAIL_SHORT_L, RAIL_SHORT_H, layer="CUT", color=1)
    # One short rail has dia 7.0mm grommet hole (at X = 30 mm, Y = 6.75 mm center)
    add_circle(msp, 30.0, 632 + GROMMET_Z, HOLE_GROMMET_D / 2.0, layer="HOLE", color=5)
    add_text(msp, "4. SIDE RAIL SHORT (210x13.5x4.5mm, QTY 2, 1-DIA 7.0 GROMMET HOLE)", (10, 613.5), height=3.5)

    # 5. CORNER BLOCKS R20 (QTY: 12) placed in grid starting at (475, 0)
    # Sector: (0,0) -> (20,0) with arc to (0,20) -> (0,0)
    bulge = math.tan(math.pi / 8)
    for i in range(12):
        row = i // 4
        col = i % 4
        bx = 475.0 + col * 26.0
        by = 0.0 + row * 26.0
        pts = [
            (bx, by, 0, 0, 0),
            (bx + CORNER_BLOCK_R, by, 0, 0, bulge),
            (bx, by + CORNER_BLOCK_R, 0, 0, 0)
        ]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT", "color": 1})
        # Insert hole dia 4.2mm at (bx + 8.5, by + 8.5) (matching corner hole offset from corner)
        add_circle(msp, bx + 8.5, by + 8.5, HOLE_INSERT_D / 2.0, layer="HOLE", color=5)

    add_text(msp, "5. CORNER BLOCK R20 with DIA 4.2 HOLE (QTY 12, 4.5T)", (475, 85), height=3.5)
    add_text(msp, "(3 LAYERS x 4 CORNERS = 13.5mm HEIGHT)", (475, 76), height=3.0)

    # 6. SCREW BOSSES (16 x 14 mm, QTY: 18) for 6 mid-bolts (3 layers x 6 sites = 18 pieces)
    for i in range(18):
        row = i // 6
        col = i % 6
        bx = 475.0 + col * 20.0
        by = 110.0 + row * 18.0
        add_rect(msp, bx, by, BOSS_W, BOSS_D, layer="CUT", color=1)
        # Center insert hole dia 4.2mm
        add_circle(msp, bx + BOSS_W / 2.0, by + BOSS_D / 2.0, HOLE_INSERT_D / 2.0, layer="HOLE", color=5)

    add_text(msp, "6. SCREW BOSS 16x14mm with DIA 4.2 HOLE (QTY 18, 4.5T)", (475, 175), height=3.5)
    add_text(msp, "(3 LAYERS x 6 SITES: 4 LONG + 2 SHORT MID-BOLTS)", (475, 166), height=3.0)

    # Title & Metadata
    add_text(msp, "MAJUNG BASSINET HOUSING Rev 2 | 4.5T BIRCH PLYWOOD | 10-BOLT REFURBISHMENT READY", (0, -30), height=6.0)

    doc.saveas(filename)
    print(f"Generated Wood Master DXF: {filename}")

def build_silicone_gasket_dxf(filename="majung_silicone_gasket_rev2.dxf"):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    doc.layers.add("CUT", color=1)
    doc.layers.add("HOLE", color=5)
    doc.layers.add("TEXT", color=7)

    # Outer perimeter: 450 x 250 with R20
    add_rounded_rect(msp, 0, 0, ENCLOSURE_W, ENCLOSURE_D, CORNER_R, layer="CUT", color=1)

    # Inner perimeter cutout (12mm rim with 10 bolt lobes of R10)
    # Inner basic boundary: inset by 12mm -> 426 x 226 mm, corner R8
    rim = GASKET_BASE_RIM
    add_rounded_rect(msp, rim, rim, ENCLOSURE_W - 2 * rim, ENCLOSURE_D - 2 * rim, CORNER_R - rim, layer="CUT", color=1)

    # 10 Bolt Holes (dia 2.8mm for tight snug seal on M3 bolts)
    for bx, by in BOLT_COORDS:
        add_circle(msp, bx, by, GASKET_BOLT_HOLE / 2.0, layer="HOLE", color=5)

    add_text(msp, "MAJUNG SILICONE GASKET Rev 2 | 1.2T FOOD-GRADE SILICONE | 10-BOLT LOBED RIM", (0, -25), height=5.0)

    doc.saveas(filename)
    print(f"Generated Silicone Gasket DXF: {filename}")

if __name__ == "__main__":
    build_wood_master_dxf("majung_bassinet_4.5T_rev2_master.dxf")
    build_silicone_gasket_dxf("majung_silicone_gasket_rev2.dxf")
