# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math
d = pickle.load(open('_freshdata.pkl', 'rb'))
V = d['V']; PADS = d['PADS']; L = d['L']; COMPS = d['COMPS']
POUR = {'GND', 'VBUS_5V', 'PVDD_12V', 'BOOST_SW'}

def ptseg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1; LL = dx*dx+dy*dy
    t = 0 if LL < 1 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/LL))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def padbox(p):
    g = p[6]; nums = [v for v in g[1:] if isinstance(v, (int, float))] if isinstance(g, list) else []
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
    for v in V:
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
    from collections import defaultdict
    cc = defaultdict(list)
    for i in range(N): cc[find(i)].append(objs[i][1])
    pc = [sorted(set(m for m in mem if '.' in m)) for mem in cc.values()]
    return [p for p in pc if p]

# net -> pads map
from collections import defaultdict
net2pads = defaultdict(list)
for p in PADS:
    if p[2]: net2pads[p[2]].append(p[0]+'.'+p[1])

if __name__ == '__main__':
    import sys as _s
    mode = _s.argv[1] if len(_s.argv) > 1 else 'open'
    if mode == 'open':
        print('=== 신호넷(비-pour) 개방 전수검사 (층인식 flood-fill) ===')
        opens = 0
        for net in sorted(net2pads):
            if net in POUR: continue
            pads = net2pads[net]
            if len(pads) < 2: continue
            pc = components(net)
            if len(pc) > 1:
                opens += 1
                print('  OPEN %s: %d성분 %s' % (net, len(pc), pc))
        print('  → 신호넷 개방:', opens)
        print('=== pour넷 (DRC=0이 연결보장, 패드수만) ===')
        for net in sorted(POUR):
            print('  %s: %d패드' % (net, len(net2pads.get(net, []))))
    elif mode == 'ic':
        for ic in _s.argv[2:]:
            print('=== %s 핀-넷 ===' % ic)
            for p in sorted([p for p in PADS if p[0] == ic], key=lambda x: (len(x[1]), x[1])):
                print('  %s.%-4s %s' % (p[0], p[1], p[2] or 'NC'))
    elif mode == 'net':
        for net in _s.argv[2:]:
            print('  %s: %s' % (net, ', '.join(sorted(net2pads.get(net, [])))))
    elif mode == 'comp':
        for c in COMPS:
            print('  %-6s %-30s %s' % (c['d'], c['dev'], c['val']))
