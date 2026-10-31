"""
MAJN Smart Bassinet Enclosure Rev 2 - Single Source of Truth (SSOT) Parameters
All dimensions in millimeters (mm).
Target material: 4.5T Birch Plywood (Top, Bottom, Side rails, Blocks)
Gasket material: 1.2T Food-grade Silicone Sheet
Cutting: Laser Cutting (Haekwang Laser, Hongdae)
"""

# Overall Enclosure Dimensions
ENCLOSURE_W = 450.0  # Length (X-axis)
ENCLOSURE_D = 250.0  # Width (Y-axis)
CORNER_R = 20.0      # 4 Corner outer radius

# Material Thickness
T_PLYWOOD = 4.5      # Nominal thickness of birch plywood
STACK_LAYERS = 3     # 3 layers of 4.5T = 13.5mm cavity height
H_CAVITY = T_PLYWOOD * STACK_LAYERS  # 13.5mm
TOTAL_HEIGHT = T_PLYWOOD * 2 + H_CAVITY  # 22.5mm (wood only), 23.5mm with 1.0mm compressed gasket

# Exciter Specifications (Tectonic Elements TEAX14C02-8)
EXCITER_W = 37.0     # Rectangular footprint length
EXCITER_D = 20.0     # Rectangular footprint width
EXCITER_H = 9.85     # Body height
VOICE_COIL_D = 14.0  # Center voice coil diameter
TAPE_THICKNESS = 0.26 # 3M 9473PC transfer tape
EXCITER_TOTAL_Z = EXCITER_H + TAPE_THICKNESS # 10.11mm
AIR_GAP_STATIC = H_CAVITY - EXCITER_TOTAL_Z  # 3.39mm safety margin

# 4 Exciter Target Coordinates (on Top Plate, 0 <= X <= 450, 0 <= Y <= 250)
# (Haptic Rev 2 confirmed coordinates)
EXCITER_COORDS = [
    (120.0, 60.0),   # Bottom Left (Head Left)
    (330.0, 60.0),   # Bottom Right (Head Right)
    (120.0, 190.0),  # Top Left (Foot Left)
    (330.0, 190.0)   # Top Right (Foot Right)
]

# Fastener & Hole Specifications
FASTENER_THREAD = "M3"
HOLE_BOLT_THROUGH = 3.2    # Bottom plate bolt clearance hole
HOLE_COUNTERSINK_D = 6.5   # 90-degree DIN 7991 countersink outer diameter
HOLE_COUNTERSINK_DEPTH = 1.7 # Countersink depth
HOLE_INSERT_D = 4.2        # Brass threaded insert press-fit hole (OD 4.2 x L 5.0mm)
HOLE_GROMMET_D = 7.0       # Silicone cable grommet hole on short side rail
GROMMET_Z = H_CAVITY / 2.0 # 6.75mm center height

# 10 Bolt Locations (on 450x250 Plate)
# 4 Corners: at (14, 14), (436, 14), (14, 236), (436, 236)
# 4 Long Edges: X = 150, 300; Y = 10.5, 239.5 (10.5mm offset from edge)
# 2 Short Edges: X = 10.5, 439.5; Y = 125.0 (Center of short edge)
BOLT_COORDS = [
    # 4 Corners
    (14.0, 14.0),
    (436.0, 14.0),
    (14.0, 236.0),
    (436.0, 236.0),
    # 4 Long edge midpoints
    (150.0, 10.5),
    (300.0, 10.5),
    (150.0, 239.5),
    (300.0, 239.5),
    # 2 Short edge centers
    (10.5, 125.0),
    (439.5, 125.0)
]

# Side Rails Dimensions (4 pieces per enclosure)
# Long Rails: 410.0 x 13.5 x 4.5 mm (Qty: 2)
RAIL_LONG_L = 410.0
RAIL_LONG_H = H_CAVITY  # 13.5mm
# Short Rails: 210.0 x 13.5 x 4.5 mm (Qty: 2)
RAIL_SHORT_L = 210.0
RAIL_SHORT_H = H_CAVITY # 13.5mm

# Corner Blocks (R20 Sector Blocks)
# Arc radius = 20mm, Qty: 12 (3 layers x 4 corners)
CORNER_BLOCK_R = 20.0
CORNER_BLOCK_QTY = 12

# Screw Boss Blocks (for 6 non-corner bolts: 4 long edge + 2 short edge)
# Enlarged to 16.0 x 14.0 mm for robust wall thickness
BOSS_W = 16.0
BOSS_D = 14.0
BOSS_QTY = 18  # 3 layers x 6 sites = 18 pieces

# Silicone Gasket Dimensions (1.2T sheet)
GASKET_BASE_RIM = 12.0 # Standard perimeter rim width
GASKET_LUG_R = 10.0    # 20mm diameter lug around bolt centers
GASKET_BOLT_HOLE = 2.8 # Snug fit for M3 bolts
