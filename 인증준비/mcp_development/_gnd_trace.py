# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math

g = pickle.load(open('_geom.pkl', 'rb'))
c = pickle.load(open('_conn.pkl', 'rb'))
L = g['L']; V = g['V']; PADS = c['PADS']; POURS = c['P']

def pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    L2 = dx*dx+dy*dy
    if L2 < 1e-9: return math.hypot(px-x1, py-y1)
    t = max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L2))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def in_rect(poly, x, y):
    _, rx, ry, w, h = poly[0], poly[1], poly[2], poly[3], poly[4]
    return (rx <= x <= rx+w) and (ry-h <= y <= ry)

pourmap = {p['net']: (p['layer'], p['poly']['polygon']) for p in POURS}

def check(net):
    pads = [(d+'.'+p, x, y, ly) for d,p,n,x,y,ly in PADS if n == net]
    lines = [(sx,sy,ex,ey,w) for nn,layer,sx,sy,ex,ey,w in L if nn == net]
    vias = [(x,y,dia) for nn,x,y,h,dia in V if nn == net]
    bad = []
    for name, px, py, ly in pads:
        best = 1e9
        for sx,sy,ex,ey,w in lines:
            best = min(best, pt_seg(px,py,sx,sy,ex,ey) - w/2.0)
        for vx,vy,dia in vias:
            best = min(best, math.hypot(px-vx,py-vy) - dia/2.0)
        inpour = False
        if net in pourmap:
            player, poly = pourmap[net]
            # top pad reaches a top pour directly; multi/TH pad reaches any pour
            if player in (1,2,15,16):
                if in_rect(poly, px, py):
                    inpour = True  # note: inner-plane pour only helps if pad reaches that layer
        # classify
        touched = best <= 6
        if not touched and not inpour:
            bad.append((name, round(best,1), (round(px),round(py))))
    return pads, lines, vias, bad

for net in ['GND','VBUS_5V','PVDD_12V','BOOST_SW','VCC_3V3','AVDD','VR_DIG','BOOST_VDD']:
    pads, lines, vias, bad = check(net)
    print('=== %-10s pads=%d lines=%d vias=%d ===' % (net, len(pads), len(lines), len(vias)))
    if not bad:
        print('   ✅ 모든 패드가 트레이스/비아/pour에 접촉')
    else:
        print('   ⚠️ 로컬 GND구리/비아/pour 없는 패드 %d개:' % len(bad))
        for nm, gp, pos in bad:
            print('       %-14s 최근접 트레이스/비아 갭=%6.1f mil @ %s' % (nm, gp, pos))
