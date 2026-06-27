# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pickle, math

d = pickle.load(open('_geom.pkl', 'rb'))
L = d['L']   # [net, layer, sx, sy, ex, ey, width]
V = d['V']   # [net, x, y, hole, dia]

def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

def seg_seg(p1, p2, p3, p4):
    # min distance between segment p1p2 and p3p4
    x1,y1=p1; x2,y2=p2; x3,y3=p3; x4,y4=p4
    ux,uy=x2-x1,y2-y1
    vx,vy=x4-x3,y4-y3
    wx,wy=x1-x3,y1-y3
    a=ux*ux+uy*uy; b=ux*vx+uy*vy; c=vx*vx+vy*vy
    dd=ux*wx+uy*wy; e=vx*wx+vy*wy
    D=a*c-b*b
    sc=sN=D; tc=tN=D
    if D < 1e-9:
        sN=0.0; sD=1.0; tN=e; tD=c
    else:
        sN=(b*e-c*dd); tN=(a*e-b*dd); sD=D; tD=D
        if sN<0: sN=0.0; tN=e; tD=c
        elif sN>sD: sN=sD; tN=e+b; tD=c
    if tN<0:
        tN=0.0
        if -dd<0: sN=0.0
        elif -dd>a: sN=a
        else: sN=-dd; sD=a
    elif tN>tD:
        tN=tD
        if (-dd+b)<0: sN=0
        elif (-dd+b)>a: sN=a
        else: sN=-dd+b; sD=a
    sc = 0.0 if abs(sD)<1e-9 else sN/sD
    tc = 0.0 if abs(tD)<1e-9 else tN/tD
    dx = wx + sc*ux - tc*vx
    dy = wy + sc*uy - tc*vy
    return math.hypot(dx, dy)

def pt_seg(px, py, p1, p2):
    x1,y1=p1; x2,y2=p2
    dx,dy=x2-x1,y2-y1
    L2=dx*dx+dy*dy
    if L2<1e-9: return math.hypot(px-x1,py-y1)
    t=clamp(((px-x1)*dx+(py-y1)*dy)/L2,0,1)
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

# Layer sets: a line is on its layer; a via is on ALL copper layers (1,2,15,16)
# bin lines by layer
from collections import defaultdict
byl = defaultdict(list)
for i,(net,layer,sx,sy,ex,ey,w) in enumerate(L):
    byl[layer].append((net,(sx,sy),(ex,ey),w))

CLR = 6.0   # clearance rule mil
FLAG = 5.5  # flag gap below this (gap = edge-to-edge)

def diffnet(a,b):
    if a==b: return False
    # treat '' as physically-GND EP copper: don't flag against GND, flag against others as 'EPviaCosmetic'
    return True

shorts=[]    # gap<0.5 (real touching / overlap)
near=[]      # 0.5<=gap<FLAG
epitems=0
for layer, segs in byl.items():
    n=len(segs)
    for i in range(n):
        neti,a1,a2,wi=segs[i]
        for j in range(i+1,n):
            netj,b1,b2,wj=segs[j]
            if neti==netj: continue
            cl=seg_seg(a1,a2,b1,b2)
            gap=cl-(wi/2.0)-(wj/2.0)
            if gap<FLAG:
                pair=(neti,netj)
                if '' in pair:
                    epitems+=1; continue
                rec=(round(gap,2),neti,netj,layer,(round(a1[0]),round(a1[1])))
                if gap<0.5: shorts.append(rec)
                else: near.append(rec)

# via vs line (via on all layers); via radius=dia/2
viaR=[ (net,(x,y),dia/2.0) for net,x,y,hole,dia in V ]
for net,(vx,vy),r in viaR:
    for layer,segs in byl.items():
        for netj,b1,b2,wj in segs:
            if netj==net: continue
            cl=pt_seg(vx,vy,b1,b2)
            gap=cl-r-(wj/2.0)
            if gap<FLAG:
                pair=(net,netj)
                if '' in pair: epitems+=1; continue
                rec=(round(gap,2),net,netj,'via-trace',(round(vx),round(vy)))
                if gap<0.5: shorts.append(rec)
                else: near.append(rec)

# via vs via
nv=len(viaR)
for i in range(nv):
    neti,(xi,yi),ri=viaR[i]
    for j in range(i+1,nv):
        netj,(xj,yj),rj=viaR[j]
        if neti==netj: continue
        gap=math.hypot(xi-xj,yi-yj)-ri-rj
        if gap<FLAG:
            if '' in (neti,netj): epitems+=1; continue
            rec=(round(gap,2),neti,netj,'via-via',(round(xi),round(yi)))
            if gap<0.5: shorts.append(rec)
            else: near.append(rec)

print('=== 단락/근접 (다른 넷 구리, net="" EP비아 제외) ===')
print('실제 단락/접촉 (gap<0.5mil):', len(shorts))
for r in sorted(shorts)[:40]: print('   ', r)
print()
print('근접 위반 (0.5<=gap<%.1fmil, clearance %smil):'%(FLAG,CLR), len(near))
for r in sorted(near)[:40]: print('   ', r)
print()
print('net="" EP비아 관련 근접 항목 수 (위에서 제외, DRC clearance 노이즈):', epitems)
