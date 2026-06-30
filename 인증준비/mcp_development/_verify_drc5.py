# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math
d = pickle.load(open('_drc5.pkl', 'rb')); Vd = d['V']; PADS = d['PADS']; L = d['L']

def ptseg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1; LL = dx*dx+dy*dy
    t = 0 if LL < 1 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/LL))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def padbox(p):
    geom = p[6]
    nums = [v for v in geom[1:] if isinstance(v, (int, float))] if isinstance(geom, list) else []
    w = nums[0] if nums else 20; h = nums[1] if len(nums) > 1 else (nums[0] if nums else 20)
    rot = nums[2] if len(nums) > 2 else 0
    if 45 < abs(rot) % 180 < 135: w, h = h, w
    return (p[3]-w/2, p[4]-h/2, p[3]+w/2, p[4]+h/2, p[5])

def lc(a, b): return a == 99 or b == 99 or a == b or a == 12 or b == 12

def gap(a, b):
    if a[0] == 'plane' or b[0] == 'plane':
        o = b if a[0] == 'plane' else a
        return -1 if o[0] == 'via' else 9e9
    if not lc(a[2], b[2]): return 9e9
    ga, gb = a[3], b[3]
    if ga[0] == 'box' and gb[0] == 'box':
        dx = max(ga[1]-gb[3], gb[1]-ga[3]); dy = max(ga[2]-gb[4], gb[2]-ga[4])
        return (-min(-dx, -dy)) if (dx < 0 and dy < 0) else math.hypot(max(dx, 0), max(dy, 0))
    if ga[0] == 'via' and gb[0] == 'via': return math.hypot(ga[1]-gb[1], ga[2]-gb[2])-ga[3]/2-gb[3]/2
    if set([ga[0], gb[0]]) == {'box', 'via'}:
        bx = ga if ga[0] == 'box' else gb; vi = ga if ga[0] == 'via' else gb
        dx = max(bx[1]-vi[1], 0, vi[1]-bx[3]); dy = max(bx[2]-vi[2], 0, vi[2]-bx[4]); return math.hypot(dx, dy)-vi[3]/2
    if set([ga[0], gb[0]]) == {'box', 'seg'}:
        bx = ga if ga[0] == 'box' else gb; s = ga if ga[0] == 'seg' else gb; best = 1e9
        for k in range(21):
            px = s[1]+(s[3]-s[1])*k/20; py = s[2]+(s[4]-s[2])*k/20
            dx = max(bx[1]-px, 0, px-bx[3]); dy = max(bx[2]-py, 0, py-bx[4]); best = min(best, math.hypot(dx, dy))
        return best-s[5]/2
    if set([ga[0], gb[0]]) == {'via', 'seg'}:
        vi = ga if ga[0] == 'via' else gb; s = ga if ga[0] == 'seg' else gb
        return ptseg(vi[1], vi[2], s[1], s[2], s[3], s[4])-s[5]/2-vi[3]/2
    s1 = ga; s2 = gb; best = 1e9
    for k in range(21):
        px = s1[1]+(s1[3]-s1[1])*k/20; py = s1[2]+(s1[4]-s1[2])*k/20
        best = min(best, ptseg(px, py, s2[1], s2[2], s2[3], s2[4]))
    return best-s1[5]/2-s2[5]/2

def components(NET, plane=False):
    objs = []
    for p in PADS:
        if p[2] == NET: bx = padbox(p); objs.append(('pad', p[0]+'.'+p[1], bx[4], ('box',)+bx[:4]))
    for l in L:
        if l[0] == NET: objs.append(('trk', '', l[1], ('seg', l[2], l[3], l[4], l[5], l[6])))
    for v in Vd:
        if v['net'] == NET: objs.append(('via', '', 12, ('via', v['x'], v['y'], v['dia'])))
    PL = None
    if plane:
        PL = len(objs); objs.append(('plane', '', 99, None))
    N = len(objs); par = list(range(N))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(N):
        for j in range(i+1, N):
            if gap(objs[i], objs[j]) <= 0.6: par[find(i)] = find(j)
    if plane:
        return [objs[i][1] for i in range(N) if objs[i][0] == 'pad' and find(i) != find(PL)]
    from collections import defaultdict
    cc = defaultdict(list)
    for i in range(N): cc[find(i)].append(objs[i][1])
    pc = [sorted(set(m for m in mem if '.' in m)) for mem in cc.values()]
    return [p for p in pc if p]

def pad_dist(px, py, p):
    d_, num, net, x, y, ly, geom = p
    if not isinstance(geom, list): return None
    sh = geom[0]; nums = [v for v in geom[1:] if isinstance(v, (int, float))]
    if sh == 'OVAL' and len(nums) >= 2:
        w, h = nums[0], nums[1]
        if h >= w: rr = w/2; half = (h-w)/2; return ptseg(px, py, x, y-half, x, y+half)-rr
        rr = h/2; half = (w-h)/2; return ptseg(px, py, x-half, y, x+half, y)-rr
    if len(nums) >= 2: w, h = nums[0], nums[1]
    elif len(nums) == 1: w = h = nums[0]
    else: return None
    rot = nums[2] if len(nums) >= 3 else 0
    if 45 < abs(rot) % 180 < 135: w, h = h, w
    dx = max(x-w/2-px, 0, px-(x+w/2)); dy = max(y-h/2-py, 0, py-(y+h/2)); return math.hypot(dx, dy)

print('=== 연결성 ===')
for net in ['AMP_I2C_SDA', 'AMP_I2C_SCL', 'AMP_OUT_B+', 'AMP_ADR', 'VCC_3V3']:
    pc = components(net)
    print('  %-13s %s' % (net, '✅ 1성분 연결' if len(pc) <= 1 else '❌ %d성분 %s' % (len(pc), pc)))
disc = components('GND', plane=True)
print('  %-13s %s' % ('GND', '✅ 평면연결' if not disc else '❌ ' + str(disc)))

print('=== 비아↔다른넷패드 <6mil ===')
bad = 0
for v in Vd:
    for p in PADS:
        if p[2] == v['net']: continue
        dd = pad_dist(v['x'], v['y'], p)
        if dd is None: continue
        if dd-v['dia']/2 < 6:
            bad += 1; print('  비아(%s)@(%.1f,%.1f)↔%s.%s(%s) 구리갭%.2f' % (v['net'], v['x'], v['y'], p[0], p[1], p[2], dd-v['dia']/2))
print('  남은 패드충돌:', bad)

print('=== GND 비아 hole 겹침 ===')
gnd = [v for v in Vd if v['net'] == 'GND']; ov = 0
for i in range(len(gnd)):
    for j in range(i+1, len(gnd)):
        dc = math.hypot(gnd[i]['x']-gnd[j]['x'], gnd[i]['y']-gnd[j]['y'])
        if dc-gnd[i]['hole']/2-gnd[j]['hole']/2 < 0: ov += 1; print('  ❌ @(%.1f,%.1f)' % (gnd[i]['x'], gnd[i]['y']))
print('  hole겹침:', ov)
