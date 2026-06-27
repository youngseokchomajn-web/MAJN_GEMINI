# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math
r = pickle.load(open('_padfull.pkl', 'rb'))
C = r['C']; PADS = r['PADS']

def aabb(pad):
    # pad = [des,padnum,net,x,y,layer,[shape,w,h,rot]]
    x, y, ly, g = pad[3], pad[4], pad[5], pad[6]
    if not g or not isinstance(g, list) or len(g) < 2: return None
    shape = g[0]
    nums = [v for v in g[1:] if isinstance(v, (int, float))]
    if len(nums) == 0: return None
    if len(nums) >= 3:
        w, h, rot = nums[0], nums[1], nums[2]
    elif len(nums) == 2:
        w, h, rot = nums[0], nums[1], 0
    else:
        w = h = nums[0]; rot = 0
    rot = abs(rot) % 180
    if 45 < rot < 135:
        w, h = h, w
    return (x - w/2, y - h/2, x + w/2, y + h/2, ly)

boxes = []
for p in PADS:
    bb = aabb(p)
    if bb: boxes.append((p[0], p[1], p[2], bb))

def gap(b1, b2):
    # axis-aligned box gap (negative = overlap); also need same layer
    if not (layer_ovl(b1[4], b2[4])): return None
    dx = max(b1[0]-b2[2], b2[0]-b1[2], 0)
    dy = max(b1[1]-b2[3], b2[1]-b1[3], 0)
    if b1[0] < b2[2] and b2[0] < b1[2] and b1[1] < b2[3] and b2[1] < b1[3]:
        # overlap
        ox = min(b1[2],b2[2]) - max(b1[0],b2[0])
        oy = min(b1[3],b2[3]) - max(b1[1],b2[1])
        return -min(ox, oy)
    return math.hypot(dx, dy)

def layer_ovl(l1, l2):
    s1 = {1,2,15,16} if l1 == 12 else {l1}
    s2 = {1,2,15,16} if l2 == 12 else {l2}
    return bool(s1 & s2)

print('=== ⑮ 패드-패드 클리어런스 (다른 넷, gap<5mil) ===')
flagged = []
n = len(boxes)
for i in range(n):
    di, pi, ni, bi = boxes[i]
    for j in range(i+1, n):
        dj, pj, nj, bj = boxes[j]
        if ni == nj and ni != '': continue  # same net ok (incl empty? treat empty separately)
        gp = gap(bi, bj)
        if gp is None: continue
        if gp < 5:
            samecomp = (di == dj)
            flagged.append((round(gp,2), di+'.'+pi, ni or "''", dj+'.'+pj, nj or "''", 'same-fp' if samecomp else 'CROSS'))

flagged.sort()
realshort = [f for f in flagged if f[0] < 0.5]
print('  실제 접촉/겹침(gap<0.5):', len(realshort))
for f in realshort[:25]: print('     ', f)
nearp = [f for f in flagged if f[0] >= 0.5]
print('  근접(0.5~5mil):', len(nearp))
for f in nearp[:30]: print('     ', f)
print()
# polarity / polarized caps
print('=== ⑯ 극성 부품 ===')
padnet = {(p[0], p[1]): p[2] for p in PADS}
for d in ['D1', 'D2', 'D3', 'D4']:
    if d in C:
        n1 = padnet.get((d,'1'),'?'); n2 = padnet.get((d,'2'),'?')
        print('   %s (%s): pad1=%s  pad2=%s' % (d, C[d]['val'][:30], n1, n2))
# polarized caps: scan for tantalum/electrolytic keywords
print('   --- 캡 중 극성소자(탄탈/전해) 탐색 ---')
pol = []
for d in C:
    if not d.startswith('C'): continue
    v = C[d]['val']; fp = C[d]['fp']
    if any(k in v for k in ['钽','电解','Tantal','tantal','Polar','铝电解']) or 'CASE' in fp.upper() or 'TANT' in fp.upper():
        pol.append((d, v, fp))
if pol:
    for x in pol: print('     ', x)
else:
    print('     없음 → 모든 캡 MLCC(무극성), 극성 오류 불가')
