# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math
from collections import defaultdict

g = pickle.load(open('_geom.pkl', 'rb'))    # L lines, V vias
c = pickle.load(open('_conn.pkl', 'rb'))    # P pours, PADS
L = g['L']; V = g['V']; PADS = c['PADS']; POURS = c['P']

ALL = {1, 2, 15, 16}
def padlayers(ly):
    if ly == 12: return set(ALL)
    if ly in (1, 2): return {ly}
    return {1}  # default top

# ---- build nodes ----
# node: dict idx -> (net, x, y, frozenset layers, kind, label)
nodes = []
def addnode(net, x, y, layers, kind, label):
    nodes.append([net, x, y, set(layers), kind, label]); return len(nodes)-1

pad_idx = []
for des, pn, net, x, y, ly in PADS:
    i = addnode(net, x, y, padlayers(ly), 'pad', des+'.'+pn)
    pad_idx.append(i)

line_ep = []  # list of (i1,i2)
for net, layer, sx, sy, ex, ey, w in L:
    if not net: continue
    a = addnode(net, sx, sy, {layer}, 'le', 'L')
    b = addnode(net, ex, ey, {layer}, 'le', 'L')
    line_ep.append((a, b))

via_idx = []
for net, x, y, hole, dia in V:
    i = addnode(net, x, y, set(ALL), 'via', 'V')
    via_idx.append(i)

N = len(nodes)
parent = list(range(N))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

# line endpoints same line
for a, b in line_ep: union(a, b)

# spatial grid for coincidence
TOL_EP = 12.0    # endpoint/via coincidence
TOL_PAD = 28.0   # pad to endpoint/via (pads have area)
CELL = 30.0
grid = defaultdict(list)
for i, (net, x, y, lys, kind, lab) in enumerate(nodes):
    grid[(int(x//CELL), int(y//CELL))].append(i)

def neighbors(i):
    net, x, y, lys, kind, lab = nodes[i]
    gx, gy = int(x//CELL), int(y//CELL)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for j in grid[(gx+dx, gy+dy)]:
                if j > i: yield j

for i in range(N):
    neti, xi, yi, lyi, ki, _ = nodes[i]
    if not neti: continue
    for j in neighbors(i):
        netj, xj, yj, lyj, kj, _ = nodes[j]
        if netj != neti: continue
        if not (lyi & lyj): continue
        dist = math.hypot(xi-xj, yi-yj)
        tol = TOL_PAD if ('pad' in (ki, kj)) else TOL_EP
        if dist <= tol:
            union(i, j)

# pours: virtual plane node per pour; union same-net nodes inside rect on pour layer (or via/multi)
def in_rect(poly, x, y):
    # ["R", rx, ry, w, h, 0,0] -> X[rx,rx+w], Y[ry-h,ry]
    _, rx, ry, w, h = poly[0], poly[1], poly[2], poly[3], poly[4]
    return (rx <= x <= rx+w) and (ry-h <= y <= ry)

for pour in POURS:
    pnet = pour['net']; player = pour['layer']
    poly = pour['poly']['polygon']
    plane = addnode(pnet, 0, 0, {player}, 'plane', 'PLANE_'+pnet)
    parent.append(len(parent))  # extend parent for the new node
    # (addnode appended to nodes but parent was sized to old N; fix below)

# rebuild parent size after adding plane nodes
while len(parent) < len(nodes):
    parent.append(len(parent))

# now union plane nodes
plane_nodes = [i for i in range(N, len(nodes))]
for pi in plane_nodes:
    pnet, _, _, plys, _, lab = nodes[pi]
    player = next(iter(plys))
    # find matching pour rect
    poly = None
    for pour in POURS:
        if pour['net']==pnet and pour['layer']==player:
            poly = pour['poly']['polygon']; break
    for j in range(N):
        netj, xj, yj, lyj, kj, _ = nodes[j]
        if netj != pnet: continue
        # node reaches pour layer if its layerset includes player (vias/multi do)
        if player not in lyj: continue
        if in_rect(poly, xj, yj):
            union(pi, j)

# ---- per-net component analysis over PADS ----
net_pads = defaultdict(list)
for k, i in enumerate(pad_idx):
    net = nodes[i][0]
    if net: net_pads[net].append(i)

print('=== 연결성(개방) — 넷별 패드 컴포넌트 수 ===')
opens = []
for net in sorted(net_pads):
    pis = net_pads[net]
    roots = {}
    for i in pis:
        r = find(i)
        roots.setdefault(r, []).append(nodes[i][5])
    if len(roots) > 1:
        opens.append((net, [v for v in roots.values()]))

if not opens:
    print('  ✅ 모든 넷의 패드가 단일 컴포넌트로 연결 (개방 0)')
else:
    print('  ⚠️ 분리된 넷:', len(opens))
    for net, groups in opens:
        print('  ──', net, '→', len(groups), '조각')
        for grp in groups:
            print('       ', grp[:12], ('...+%d'%(len(grp)-12) if len(grp)>12 else ''))
