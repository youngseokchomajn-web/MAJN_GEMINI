# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math

g = pickle.load(open('_geom.pkl', 'rb'))
c = pickle.load(open('_conn.pkl', 'rb'))
L = g['L']; V = g['V']; PADS = c['PADS']

def pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    L2 = dx*dx+dy*dy
    if L2 < 1e-9: return math.hypot(px-x1, py-y1)
    t = max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L2))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def analyze(net):
    print('\n===== %s =====' % net)
    pads = [(d+'.'+p, x, y, ly) for d,p,n,x,y,ly in PADS if n == net]
    lines = [(layer, sx, sy, ex, ey, w) for nn,layer,sx,sy,ex,ey,w in L if nn == net]
    vias = [(x, y, dia) for nn,x,y,h,dia in V if nn == net]
    print('  pads:', [(p[0], (round(p[1]),round(p[2]))) for p in pads])
    print('  #lines:', len(lines), ' #vias:', len(vias))
    # For each pad, nearest copper (line or via) of same net, excluding its own pad point
    for name, px, py, ly in pads:
        best = 1e9; bestwhat = None
        for layer, sx, sy, ex, ey, w in lines:
            dd = pt_seg(px, py, sx, sy, ex, ey) - w/2.0
            if dd < best: best = dd; bestwhat = ('line', layer, (round(sx),round(sy)), (round(ex),round(ey)))
        for vx, vy, dia in vias:
            dd = math.hypot(px-vx, py-vy) - dia/2.0
            if dd < best: best = dd; bestwhat = ('via', (round(vx),round(vy)))
        tag = 'OK(touch)' if best <= 6 else ('NEAR %.1f' % best if best < 30 else 'OPEN %.1f' % best)
        print('   pad %-14s nearest copper gap=%6.1f mil  %-9s %s' % (name, best, tag, bestwhat))
    # also: do the lines themselves form a path between the pad clusters? check line endpoint chain gap
    # min gap between any two line endpoints that are NOT connected (rough)

for net in ['AMP_ADR', 'AMP_OUT_A-', 'SPI_CS', 'AMP_OUT_A+', 'AMP_OUT_B-', 'AMP_OUT_B+']:
    analyze(net)
