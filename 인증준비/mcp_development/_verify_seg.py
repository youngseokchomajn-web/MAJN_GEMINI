# -*- coding: utf-8 -*-
# Accurate clearance verifier: oval pads as stadium (obround), rect as AABB.
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math, json

g = pickle.load(open('_geom.pkl', 'rb')); pf = pickle.load(open('_padfull.pkl', 'rb'))
L = g['L']; V = g['V']; PADS = pf['PADS']

def ptseg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1; LL = dx*dx+dy*dy
    t = 0 if LL < 1 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/LL))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def pad_dist(px, py, p):
    # returns distance from point to pad EDGE (negative if inside), + layer
    d, num, net, x, y, ly, geom = p
    if not isinstance(geom, list): return None
    shape = geom[0]
    nums = [v for v in geom[1:] if isinstance(v, (int, float))]
    if shape == 'OVAL' and len(nums) >= 2:
        w, h = nums[0], nums[1]
        if h >= w:  # vertical stadium
            r = w/2; half = (h-w)/2
            return ptseg(px, py, x, y-half, x, y+half) - r, ly
        else:       # horizontal stadium
            r = h/2; half = (w-h)/2
            return ptseg(px, py, x-half, y, x+half, y) - r, ly
    if shape == 'ELLIPSE' and len(nums) >= 2 and abs(nums[0]-nums[1]) < 0.5:
        r = nums[0]/2
        return math.hypot(px-x, py-y) - r, ly
    # RECT / default: AABB
    if len(nums) >= 2: w, h = nums[0], nums[1]
    elif len(nums) == 1: w = h = nums[0]
    else: return None
    rot = nums[2] if len(nums) >= 3 else 0
    if 45 < abs(rot) % 180 < 135: w, h = h, w
    dx = max(x-w/2-px, 0, px-(x+w/2)); dy = max(y-h/2-py, 0, py-(y+h/2))
    return math.hypot(dx, dy), ly

def seg_clear(ax, ay, bx, by, net, layer, exclude_ids=()):
    """min clearance of a track (net,layer,width10) to different-net copper. Accurate pads."""
    best = 1e9; what = ''
    n = max(3, int(math.hypot(bx-ax, by-ay)/3))
    samples = [(ax+(bx-ax)*i/n, ay+(by-ay)*i/n) for i in range(n+1)]
    # pads
    for p in PADS:
        if p[2] == net and net != '': continue
        r = pad_dist(0, 0, p)
        if r is None: continue
        ply = p[5]
        if not (ply == layer or ply == 12 or layer == 12): continue
        for (px, py) in samples:
            dd, _ = pad_dist(px, py, p)
            c = dd - 5  # track half
            if c < best: best = c; what = 'pad '+p[0]+'.'+p[1]+'('+(p[2] or 'NC')+')'
    # tracks
    for l in L:
        if l[0] == net and net != '': continue
        if l[1] != layer: continue
        for (px, py) in samples:
            c = ptseg(px, py, l[2], l[3], l[4], l[5]) - l[6]/2 - 5
            if c < best: best = c; what = 'trk '+(l[0] or 'NC')
    # vias
    for v in V:
        if v[0] == net and net != '': continue
        for (px, py) in samples:
            c = math.hypot(px-v[1], py-v[2]) - v[4]/2 - 5
            if c < best: best = c; what = 'via '+(v[0] or 'NC')
    return round(best, 2), what

if __name__ == '__main__':
    net = json.loads(sys.argv[1]) if len(sys.argv) > 1 else 'AMP_OUT_B+'
    segs = json.loads(sys.argv[2])  # [[ax,ay,bx,by],...]
    print('검증 넷:', net)
    ok = True
    for s in segs:
        c, what = seg_clear(s[0], s[1], s[2], s[3], net, 1)
        flag = '✅' if c >= 6 else '❌'
        if c < 6: ok = False
        print('  %s (%d,%d)-(%d,%d): 최소클리어 %.2fmil (%s)' % (flag, s[0], s[1], s[2], s[3], c, what))
    print('전체:', '✅ 모두 ≥6mil' if ok else '❌ 위반 있음 — 실행 금지')
