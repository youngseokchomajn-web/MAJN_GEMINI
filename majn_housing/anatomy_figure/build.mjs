import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../.agents/skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "../../.agents/skills/anatomy/scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const isLight = process.argv.includes("--light");
const theme = isLight ? "light" : "dark";

const WIDTH = 820;
const HEIGHT = 600;

// Housing geometry (scaled for screen units: 450x250 -> 360x200, 1 unit approx 1.25mm)
const PAD_W = 360;
const PAD_D = 200;
const PAD_R = 16; // R20 scaled

const PAD_PLAN = { x: -PAD_W / 2, y: -PAD_D / 2, w: PAD_W, d: PAD_D, r: PAD_R };
const T_WOOD = 4.5 * 0.8; // 3.6
const H_CAV = 13.5 * 0.8; // 10.8
const T_GASKET = 1.2 * 0.8; // 1.0

// Workbench base plate
const BENCH_PLATE = { x: -210, y: -130, w: 420, d: 260, r: 12 };
const BENCH_H = 8;
const BENCH_FOOT = 6;

// Camera projection setup
const P = k.fitProjection(
  [
    ...k.boxCorners(BENCH_PLATE, -BENCH_H - BENCH_FOOT, 0),
    ...k.boxCorners(PAD_PLAN, 0, 160) // expanded vertical space for exploded stack
  ],
  WIDTH,
  HEIGHT,
  { pad: 40, azimuth: 45 }
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (points) => [...points].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));

// Bolt positions (8 locations: 4 corners + 4 midpoints along long edges)
const BOLTS = [
  [-PAD_W / 2 + 18, -PAD_D / 2 + 18],
  [PAD_W / 2 - 18, -PAD_D / 2 + 18],
  [-PAD_W / 2 + 18, PAD_D / 2 - 18],
  [PAD_W / 2 - 18, PAD_D / 2 - 18],
  [-PAD_W / 6, -PAD_D / 2 + 12],
  [PAD_W / 6, -PAD_D / 2 + 12],
  [-PAD_W / 6, PAD_D / 2 - 12],
  [PAD_W / 6, PAD_D / 2 - 12]
];

// Exciters (4 positions: golden ratio layout toward corners)
const EXCITERS = [
  [-PAD_W / 3, -PAD_D / 3.4],
  [PAD_W / 3, -PAD_D / 3.4],
  [-PAD_W / 3, PAD_D / 3.4],
  [PAD_W / 3, PAD_D / 3.4]
];

// 1. Workbench granite base with ruler & feet
function drawWorkbench() {
  const out = [];
  out.push(`<path class="iso-halo" d="${k.haloOf(BENCH_PLATE, -BENCH_H - BENCH_FOOT, BENCH_H, P)}"/>`);
  
  // Feet
  for (const [x, y] of byDepth(k.corners(BENCH_PLATE, 20))) {
    out.push(S(k.cylinder(x, y, 9, -BENCH_H - BENCH_FOOT, 2, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 7, -BENCH_H - BENCH_FOOT + 2, BENCH_FOOT - 2, P, 28), { tone: "mid" }));
  }

  // Base slab
  out.push(S(k.slabOf(BENCH_PLATE, -BENCH_H, BENCH_H, P, 12, 1.8), { tone: "lo" }));
  out.push(L(k.planOutline(k.insetPlan(BENCH_PLATE, 6), 0, P), { tone: "lo" }));

  // Corner mounting screws on workbench
  const screws = k.corners(BENCH_PLATE, 12);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.5, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));

  // Calibration ruler strip on front bench edge
  const strip = { x: -PAD_W / 2 + 10, y: BENCH_PLATE.y + BENCH_PLATE.d - 18, w: PAD_W - 20, d: 8, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.8, P, 2), { tone: "mid", crease: "none" }));
  const ticks = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 5, 5, strip.y + 1, 0.8, [2.5, 4.5], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "hi" }));

  return out.join("");
}

// 2. Exploded layer groups (animated by live script)
function drawExplodedAssemblies() {
  const layers = [];

  // LAYER 1: BOTTOM PLATE (Z offset: 5)
  // 4.5T Birch Plywood bottom with 8 countersunk bolt holes
  const lBottom = [];
  lBottom.push(`<g class="wood-material">`);
  lBottom.push(S(k.slabOf(PAD_PLAN, 0, T_WOOD, P, PAD_R, 0.8), { tone: "mid" }));
  lBottom.push(L(k.planOutline(k.insetPlan(PAD_PLAN, 3), T_WOOD, P), { tone: "lo" }));
  // 8 bolt holes
  for (const [bx, by] of BOLTS) {
    lBottom.push(L(k.ring(bx, by, 3.2, T_WOOD, P, 14), { tone: "hi" }));
    lBottom.push(L(k.ring(bx, by, 1.8, 0, P, 14), { tone: "lo" }));
    lBottom.push(D([at([bx, by, T_WOOD])], { size: 0.45 }));
  }
  lBottom.push(`</g>`);
  layers.push({ id: "layer-bottom", zRest: 6, zExplode: 12, svg: lBottom.join("") });

  // LAYER 1.5: 8 STAINLESS M3 BOLTS
  const lBolts = [];
  lBolts.push(`<g class="steel-material">`);
  for (const [bx, by] of BOLTS) {
    lBolts.push(S(k.cylinder(bx, by, 2.8, -4, 2.5, P, 14), { tone: "hi" }));
    lBolts.push(S(k.cylinder(bx, by, 1.5, -1.5, 8, P, 12), { tone: "mid" }));
    lBolts.push(D([at([bx, by, -4])], { size: 0.5 }));
  }
  lBolts.push(`</g>`);
  layers.push({ id: "layer-bolts", zRest: 2, zExplode: -16, svg: lBolts.join("") });

  // LAYER 2: SILICONE GASKET (Custom laser-cut 1.2mm, Rev 2 upgrade)
  const lGasket = [];
  lGasket.push(`<g class="silicone-material">`);
  const gasketPlan = k.insetPlan(PAD_PLAN, 2);
  const gasketInner = k.insetPlan(PAD_PLAN, 14);
  lGasket.push(S(k.slabOf(gasketPlan, 0, T_GASKET, P, PAD_R - 2, 0.4), { tone: "hi" }));
  lGasket.push(L(k.planOutline(gasketInner, T_GASKET, P), { tone: "mid" }));
  // gasket punch holes for bolts
  for (const [bx, by] of BOLTS) {
    lGasket.push(L(k.ring(bx, by, 2.0, T_GASKET, P, 12), { tone: "lo" }));
  }
  lGasket.push(`</g>`);
  layers.push({ id: "layer-gasket", zRest: 12, zExplode: 34, svg: lGasket.join("") });

  // LAYER 3: MIDDLE CAVITY FRAME (4.5T x 3 stack = 13.5mm height)
  // Outer frame + 4 R20 Corner Columns + 4 Screw Bosses + Brass Inserts + Grommet
  const lFrame = [];
  lFrame.push(`<g class="wood-material">`);
  // Outer frame boundary
  lFrame.push(S(k.slabOf(PAD_PLAN, 0, H_CAV, P, PAD_R, 1.2), { tone: "mid" }));
  // Inner cavity cutout (recessed wall)
  const cavPlan = k.insetPlan(PAD_PLAN, 14);
  lFrame.push(L(k.planOutline(cavPlan, H_CAV, P), { tone: "lo" }));

  // 4 Corner R20 stacked wooden columns
  for (const [cx, cy] of k.corners(PAD_PLAN, 20)) {
    lFrame.push(S(k.cylinder(cx, cy, 14, 0, H_CAV, P, 18), { tone: "lo" }));
  }
  lFrame.push(`</g>`);

  // 8 M3 Brass Knurled Threaded Inserts (embedded in bosses)
  lFrame.push(`<g class="brass-material">`);
  for (const [bx, by] of BOLTS) {
    lFrame.push(S(k.cylinder(bx, by, 3.2, H_CAV - 5, 5, P, 16), { tone: "lit" })); // Brass glow
    lFrame.push(L(k.ring(bx, by, 2.2, H_CAV, P, 12), { tone: "hi" }));
    lFrame.push(D([at([bx, by, H_CAV])], { size: 0.4 }));
  }
  lFrame.push(`</g>`);

  // Side cable grommet on left short edge (⌀7mm)
  lFrame.push(`<g class="grommet-material">`);
  const grommetX = -PAD_W / 2;
  const grommetY = 0;
  lFrame.push(S(k.cylinder(grommetX + 3, grommetY, 4.5, H_CAV / 2 - 3, 6, P, 16), { tone: "hi" }));
  lFrame.push(L(k.ring(grommetX, grommetY, 3.5, H_CAV / 2, P, 14), { tone: "lit" }));
  lFrame.push(`</g>`);

  layers.push({ id: "layer-frame", zRest: 16, zExplode: 60, svg: lFrame.join("") });

  // LAYER 4: 4-CHANNEL TEAX14C02 EXCITERS
  const lExciters = [];
  lExciters.push(`<g class="exciter-material">`);
  for (let i = 0; i < EXCITERS.length; i++) {
    const [ex, ey] = EXCITERS[i];
    // Exciter outer mounting ring (⌀40mm)
    lExciters.push(S(k.cylinder(ex, ey, 16, 0, 2.5, P, 24), { tone: "mid" }));
    // Voice coil center (⌀14mm)
    lExciters.push(S(k.cylinder(ex, ey, 8, 2.5, 5.5, P, 20), { tone: "lit" }));
    // Contact pads & wire terminal
    lExciters.push(D([at([ex - 4, ey, 8]), at([ex + 4, ey, 8])], { size: 0.5 }));
    lExciters.push(L(k.ring(ex, ey, 8, 8, P, 16), { tone: "hi" }));
  }
  lExciters.push(`</g>`);
  layers.push({ id: "layer-exciters", zRest: 26, zExplode: 88, svg: lExciters.join("") });

  // LAYER 5: TOP PANEL (4.5T Birch Plywood + Food-Safe PU Waterproof Coating)
  const lTop = [];
  lTop.push(`<g class="wood-material wood-top-panel">`);
  lTop.push(S(k.slabOf(PAD_PLAN, 0, T_WOOD, P, PAD_R, 1.4), { tone: "hi" }));
  // Bevel line around smooth top edge
  lTop.push(L(k.planOutline(k.insetPlan(PAD_PLAN, 2), T_WOOD, P), { tone: "mid" }));
  
  // Laser-marked INFO rings for exciter alignment on underside
  for (const [ex, ey] of EXCITERS) {
    lTop.push(L(k.ring(ex, ey, 15, 0.4, P, 20), { tone: "lo" }));
    lTop.push(L(k.ring(ex, ey, 6, 0.4, P, 16), { tone: "lo" }));
  }

  // Micro brand engraving badge
  const badge = { x: -30, y: PAD_D / 2 - 25, w: 60, d: 14, r: 2 };
  lTop.push(S(k.slabOf(badge, T_WOOD, 0.4, P, 2), { tone: "lo", crease: "none" }));
  lTop.push(k.faceTextSvg(k.topMatrix([0, PAD_D / 2 - 18], T_WOOD + 0.5, P), "MAJN BASSINET", { size: 3.5, tone: "hi", anchor: "middle" }));
  lTop.push(`</g>`);

  layers.push({ id: "layer-top", zRest: 31, zExplode: 118, svg: lTop.join("") });

  // LAYER 6: 2ND DEFENSE - ULTRASONIC WELDED TPU WATERPROOF SLEEVE (Translucent)
  const lTPU = [];
  lTPU.push(`<g class="tpu-material">`);
  const tpuPlan = { x: -PAD_W / 2 - 4, y: -PAD_D / 2 - 4, w: PAD_W + 8, d: PAD_D + 8, r: PAD_R + 3 };
  lTPU.push(S(k.slabOf(tpuPlan, 0, 1.5, P, PAD_R + 3, 0.5), { tone: "lo" }));
  lTPU.push(L(k.planOutline(tpuPlan, 1.5, P), { tone: "hi" }));
  lTPU.push(k.faceTextSvg(k.topMatrix([0, 0], 2, P), "TPU BARRIER (IPX5)", { size: 5, tone: "lit", anchor: "middle" }));
  lTPU.push(`</g>`);
  layers.push({ id: "layer-tpu", zRest: 36, zExplode: 150, svg: lTPU.join("") });

  // LAYER 7: 1ST DEFENSE - WASHABLE COTTON/MODAL FABRIC COVER (With Zipper)
  const lFabric = [];
  lFabric.push(`<g class="fabric-material">`);
  const fabPlan = { x: -PAD_W / 2 - 8, y: -PAD_D / 2 - 8, w: PAD_W + 16, d: PAD_D + 16, r: PAD_R + 6 };
  lFabric.push(S(k.slabOf(fabPlan, 0, 2.0, P, PAD_R + 6, 0.6), { tone: "mid" }));
  lFabric.push(L(k.planOutline(fabPlan, 2.0, P), { tone: "lo" }));
  // Zipper line along perimeter
  const zipPlan = k.insetPlan(fabPlan, 3);
  lFabric.push(L(k.planOutline(zipPlan, 1.0, P), { tone: "hi" }));
  lFabric.push(k.faceTextSvg(k.topMatrix([0, 0], 3, P), "WASHABLE FABRIC SLEEVE", { size: 5, tone: "mid", anchor: "middle" }));
  lFabric.push(`</g>`);
  layers.push({ id: "layer-fabric", zRest: 40, zExplode: 185, svg: lFabric.join("") });

  return layers;
}

// Assemble full SVG figure & interactive HTML
function buildPage() {
  const workbenchSvg = drawWorkbench();
  const layers = drawExplodedAssemblies();

  const layersSvg = layers
    .map(
      (layer) => `
    <g id="${layer.id}" class="assembly-layer" data-z-rest="${layer.zRest}" data-z-explode="${layer.zExplode}">
      ${layer.svg}
    </g>`
    )
    .join("\n");

  const fullSvg = `
    <svg viewBox="0 0 ${WIDTH} ${HEIGHT}" class="w-full h-full select-none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.25"/>
        </filter>
        <linearGradient id="birchGrain" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fdfbf7"/>
          <stop offset="50%" stop-color="#eed8be"/>
          <stop offset="100%" stop-color="#e2c49f"/>
        </linearGradient>
      </defs>
      <style>
        /* 🪵 Realistic Birch Wood Material Palette */
        .wood-material .iso-fill { fill: #f5e4ce !important; }
        .wood-material .iso-top { fill: #fdf6ec !important; }
        .wood-material .iso-shade[data-shade="0"] { fill: #d5b591 !important; }
        .wood-material .iso-shade[data-shade="1"] { fill: #dec09e !important; }
        .wood-material .iso-shade[data-shade="2"] { fill: #e7caab !important; }
        .wood-material .iso-shade[data-shade="3"] { fill: #f0d8bf !important; }
        .wood-material .iso-line { stroke: #8c6843 !important; }
        .wood-material .iso-line[data-tone="hi"] { stroke: #5c3e21 !important; stroke-width: 0.9px; }
        .wood-material .iso-line[data-tone="mid"] { stroke: #8c6843 !important; }
        .wood-material .iso-line[data-tone="lo"] { stroke: #bfa382 !important; }

        /* Top panel warm lacquer sheen */
        .wood-top-panel .iso-top { fill: #fffaf0 !important; }

        /* 🔩 Brass Knurled Threaded Inserts (Gold/Brass) */
        .brass-material .iso-fill { fill: #fef08a !important; }
        .brass-material .iso-top { fill: #fef9c3 !important; }
        .brass-material .iso-shade { fill: #ca8a04 !important; }
        .brass-material .iso-line { stroke: #854d0e !important; }

        /* 💎 Translucent Medical Silicone Gasket */
        .silicone-material .iso-fill { fill: rgba(186, 230, 253, 0.75) !important; }
        .silicone-material .iso-top { fill: rgba(224, 242, 254, 0.85) !important; }
        .silicone-material .iso-shade { fill: rgba(125, 211, 252, 0.7) !important; }
        .silicone-material .iso-line { stroke: #0284c7 !important; stroke-width: 0.8px; }

        /* ⚙️ Stainless Steel Bolts */
        .steel-material .iso-fill { fill: #94a3b8 !important; }
        .steel-material .iso-top { fill: #e2e8f0 !important; }
        .steel-material .iso-shade { fill: #64748b !important; }
        .steel-material .iso-line { stroke: #334155 !important; }

        /* 🔊 TEAX14C02 Exciters (Anodized Dark Body + Copper Core) */
        .exciter-material .iso-fill { fill: #1e293b !important; }
        .exciter-material .iso-top { fill: #334155 !important; }
        .exciter-material .iso-shade { fill: #0f172a !important; }
        .exciter-material .iso-solid[data-lit] > .iso-top { fill: #fb923c !important; } /* Copper core */
        .exciter-material .iso-solid[data-lit] > .iso-shade { fill: #c2410c !important; }
        .exciter-material .iso-line { stroke: #475569 !important; }
        .exciter-material .iso-line[data-tone="hi"] { stroke: #f97316 !important; }

        /* 🛡️ TPU Waterproof Membrane (Translucent Aqua Green) */
        .tpu-material .iso-fill { fill: rgba(167, 243, 208, 0.45) !important; }
        .tpu-material .iso-top { fill: rgba(209, 250, 229, 0.6) !important; }
        .tpu-material .iso-shade { fill: rgba(110, 231, 183, 0.4) !important; }
        .tpu-material .iso-line { stroke: #059669 !important; }

        /* 👕 Washable Cotton Sleeve (Warm Off-White Linen) */
        .fabric-material .iso-fill { fill: #faf5ee !important; }
        .fabric-material .iso-top { fill: #ffffff !important; }
        .fabric-material .iso-shade { fill: #f3ece0 !important; }
        .fabric-material .iso-line { stroke: #a89f91 !important; }

        /* 🔌 Rubber Cable Grommet */
        .grommet-material .iso-fill { fill: #334155 !important; }
        .grommet-material .iso-top { fill: #475569 !important; }
        .grommet-material .iso-shade { fill: #1e293b !important; }
        .grommet-material .iso-line { stroke: #0f172a !important; }
      </style>
      <g id="workbench-group">
        ${workbenchSvg}
      </g>
      <g id="explodable-stack">
        ${layersSvg}
      </g>
    </svg>
  `;

  const plateContent = `
    <div class="anatomy-card relative bg-[var(--card,#ffffff)] border border-[var(--border,#e2e8f0)] rounded-2xl shadow-2xl overflow-hidden flex flex-col font-sans">
      
      <!-- Top Title Bar -->
      <div class="p-4 sm:p-5 border-b border-[var(--border,#e2e8f0)] flex flex-wrap items-center justify-between gap-3 bg-[var(--background,#f8fafc)]/80">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-600 text-white">FIG 01</span>
            <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Refurbishment Anatomy</span>
          </div>
          <h2 class="text-lg sm:text-xl font-bold mt-0.5 text-slate-900 dark:text-slate-100 flex items-center gap-2">
            MAJN Bassinet 4.5T — 렌탈 방수 최적화 정밀 분해도
          </h2>
        </div>

        <!-- Mode & Explode Control -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 bg-slate-200/70 dark:bg-slate-800 p-1.5 rounded-xl border border-slate-300 dark:border-slate-700">
            <label class="text-xs font-medium text-slate-600 dark:text-slate-300 pl-1">분해도:</label>
            <input type="range" id="explodeSlider" min="0" max="100" value="75" class="w-28 sm:w-36 h-1.5 bg-slate-400 rounded-lg appearance-none cursor-pointer accent-blue-600">
            <span id="explodeReadout" class="text-xs font-mono font-bold w-10 text-right text-blue-600 dark:text-blue-400">75%</span>
          </div>
          <button id="toggleBtn" class="px-3 py-1.5 text-xs font-bold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition">
            원터치 결합/분해
          </button>
        </div>
      </div>

      <!-- Main Visual Workspace -->
      <div class="relative w-full aspect-[16/10] bg-gradient-to-b from-slate-50 via-slate-100/50 to-slate-200/30 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center p-2">
        ${fullSvg}
      </div>

      <!-- Live Engineering Readout Footer -->
      <div class="p-4 sm:p-5 border-t border-[var(--border,#e2e8f0)] bg-[var(--background,#f8fafc)]/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
          <div class="text-[10px] text-slate-500 uppercase tracking-wider">체결 볼트 & 너트</div>
          <div class="text-sm font-mono font-bold text-slate-900 dark:text-slate-100 mt-0.5">8× M3 황동 인서트</div>
          <div class="text-[10px] text-emerald-600 font-semibold">100회+ 무손상 체결</div>
        </div>
        <div class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
          <div class="text-[10px] text-slate-500 uppercase tracking-wider">방수 실링재</div>
          <div class="text-sm font-mono font-bold text-slate-900 dark:text-slate-100 mt-0.5">1.2mm 실리콘 가스켓</div>
          <div class="text-[10px] text-emerald-600 font-semibold">무접착 1초 탈착 (IPX5)</div>
        </div>
        <div class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
          <div class="text-[10px] text-slate-500 uppercase tracking-wider">리퍼비시 소요시간</div>
          <div class="text-sm font-mono font-bold text-emerald-600 mt-0.5">2분 30초 / 대</div>
          <div class="text-[10px] text-slate-500">기존 25분 대비 90% 절감</div>
        </div>
        <div class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
          <div class="text-[10px] text-slate-500 uppercase tracking-wider">조립 완성 외경</div>
          <div class="text-sm font-mono font-bold text-slate-900 dark:text-slate-100 mt-0.5">450 × 250 × 23.5 mm</div>
          <div class="text-[10px] text-blue-600 font-semibold">홍대 해광레이저 4.5T 규격</div>
        </div>
      </div>

    </div>
  `;

  // Dynamic live script for smooth isometric Z-displacement
  const liveScript = `
    const slider = document.getElementById('explodeSlider');
    const readout = document.getElementById('explodeReadout');
    const toggleBtn = document.getElementById('toggleBtn');
    const layers = document.querySelectorAll('.assembly-layer');

    // Dz factor in world coordinate projection
    // Camera azimuth 45, elevation 30 -> screen dy for z: -cos(elev)
    const Z_FACTOR = -1.25;

    function setExplode(percent) {
      const f = percent / 100;
      readout.innerText = percent + '%';
      
      layers.forEach(layer => {
        const zRest = parseFloat(layer.getAttribute('data-z-rest'));
        const zExplode = parseFloat(layer.getAttribute('data-z-explode'));
        const currentZ = zRest + (zExplode - zRest) * f;
        const dy = (currentZ - zRest) * Z_FACTOR;
        layer.style.transform = \`translateY(\${dy}px)\`;
        layer.style.transition = 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)';
      });
    }

    slider.addEventListener('input', (e) => {
      setExplode(parseInt(e.target.value, 10));
    });

    toggleBtn.addEventListener('click', () => {
      if (parseInt(slider.value, 10) > 20) {
        slider.value = 0;
      } else {
        slider.value = 85;
      }
      setExplode(parseInt(slider.value, 10));
    });

    // Initialize
    setExplode(75);
  `;

  return k.pageHtml({
    title: "MAJN Bassinet Anatomy — 4.5T Enclosure & Refurbishment",
    body: `<div class="p-3 sm:p-6 max-w-5xl mx-auto">${plateContent}</div>`,
    script: liveScript,
    theme
  });
}

const outFileName = isLight ? "index-light.html" : "index.html";
const html = buildPage();
writeFileSync(join(HERE, outFileName), html);
console.log("Successfully built MAJN Anatomy figure:", join(HERE, outFileName));
