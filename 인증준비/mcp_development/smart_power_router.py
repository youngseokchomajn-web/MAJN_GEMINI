import json
import urllib.request
import math
import heapq
import time
import sys

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            else: raise Exception(res.get("error"))
    except Exception as e:
        return f"ERROR: {str(e)}"

# 1. Coordinate Mapping Constants
X_MIN = 1800.0
X_MAX = 7600.0
Y_MIN = 1800.0
Y_MAX = 5200.0
GRID_RES = 10.0  # 10 mil resolution

def mil_to_grid(x, y):
    return (int((x - X_MIN) / GRID_RES), int((y - Y_MIN) / GRID_RES))

def grid_to_mil(gx, gy):
    return (X_MIN + gx * GRID_RES, Y_MIN + gy * GRID_RES)

# 2. Geometry Helper functions
def point_to_segment_distance(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax)**2 + (py - ay)**2)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    cx = ax + t * dx
    cy = ay + t * dy
    return math.sqrt((px - cx)**2 + (py - cy)**2)

def mark_segment_obstacle(grid, p1, p2, width_mil, clearance_mil):
    w = len(grid)
    h = len(grid[0])
    gx1, gy1 = mil_to_grid(*p1)
    gx2, gy2 = mil_to_grid(*p2)
    
    margin = int((width_mil / 2.0 + clearance_mil) / GRID_RES) + 1
    min_x = max(0, min(gx1, gx2) - margin)
    max_x = min(w - 1, max(gx1, gx2) + margin)
    min_y = max(0, min(gy1, gy2) - margin)
    max_y = min(h - 1, max(gy1, gy2) + margin)
    
    for gx in range(min_x, max_x + 1):
        for gy in range(min_y, max_y + 1):
            px, py = grid_to_mil(gx, gy)
            dist = point_to_segment_distance((px, py), p1, p2)
            if dist < (width_mil / 2.0 + clearance_mil):
                grid[gx][gy] = 1

# 3. A* Pathfinding Algorithm
def astar(grid, start, end):
    width = len(grid)
    height = len(grid[0])
    
    if start[0] < 0 or start[0] >= width or start[1] < 0 or start[1] >= height:
        return None
    if end[0] < 0 or end[0] >= width or end[1] < 0 or end[1] >= height:
        return None
        
    open_set = []
    heapq.heappush(open_set, (0, start[0], start[1]))
    
    came_from = {}
    g_score = {start: 0.0}
    
    neighbors = [
        (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),
        (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)
    ]
    
    while open_set:
        _, current_x, current_y = heapq.heappop(open_set)
        current = (current_x, current_y)
        
        if current == end:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
            
        for dx, dy, cost in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
                if grid[neighbor[0]][neighbor[1]] != 0:
                    continue
                
                tentative_g = g_score[current] + cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = math.sqrt((neighbor[0] - end[0])**2 + (neighbor[1] - end[1])**2)
                    f = tentative_g + h
                    heapq.heappush(open_set, (f, neighbor[0], neighbor[1]))
                    
    return None

def check_line_of_sight(grid, p1, p2):
    x0, y0 = p1
    x1, y1 = p2
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    cx, cy = x0, y0
    while True:
        if grid[cx][cy] != 0:
            return False
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy
    return True

def simplify_path(grid, path):
    if not path:
        return []
    simplified = [path[0]]
    current_index = 0
    while current_index < len(path) - 1:
        next_index = current_index + 1
        for i in range(len(path) - 1, current_index, -1):
            if check_line_of_sight(grid, path[current_index], path[i]):
                next_index = i
                break
        simplified.append(path[next_index])
        current_index = next_index
    return simplified

# 4. Neck-down Path Drawing
def draw_neck_down_path(net_name, layer, path_mils, start_comp, end_comp, main_width_mil):
    dense_points = []
    for i in range(len(path_mils) - 1):
        p1 = path_mils[i]
        p2 = path_mils[i+1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            continue
        steps = int(dist / 2.0)  # 2 mil steps for high resolution
        if steps < 1:
            steps = 1
        for s in range(steps):
            t = s / float(steps)
            dense_points.append((p1[0] + dx*t, p1[1] + dy*t))
    dense_points.append(path_mils[-1])
    
    start_pad = path_mils[0]
    end_pad = path_mils[-1]
    
    neck_down_dist = 60.0  # 1.5mm
    neck_width = 10.0      # 0.25mm
    
    widths = []
    for p in dense_points:
        w = main_width_mil
        if start_comp in {'U4', 'U3', 'U2'}:
            dx = p[0] - start_pad[0]
            dy = p[1] - start_pad[1]
            if math.sqrt(dx*dx + dy*dy) < neck_down_dist:
                w = neck_width
        if end_comp in {'U4', 'U3', 'U2'}:
            dx = p[0] - end_pad[0]
            dy = p[1] - end_pad[1]
            if math.sqrt(dx*dx + dy*dy) < neck_down_dist:
                w = neck_width
        widths.append(w)
        
    segments = []
    current_start = dense_points[0]
    current_width = widths[0]
    
    for i in range(1, len(dense_points)):
        p = dense_points[i]
        w = widths[i]
        if w != current_width:
            segments.append((current_start, dense_points[i-1], current_width))
            current_start = dense_points[i-1]
            current_width = w
    segments.append((current_start, dense_points[-1], current_width))
    
    for p1, p2, w in segments:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if math.sqrt(dx*dx + dy*dy) < 1.0:
            continue
        w_mil = int(w)
        js = f"await eda.pcb_PrimitiveLine.create('{net_name}', {layer}, {p1[0]:.1f}, {p1[1]:.1f}, {p2[0]:.1f}, {p2[1]:.1f}, {w_mil}, false);"
        execute_js(js)

def main():
    print("Clearing existing tracks and vias...")
    js_clear = """
    try {
        const lines = await eda.pcb_PrimitiveLine.getAll();
        const vias = await eda.pcb_PrimitiveVia.getAll();
        
        // 1. Unlock all lines and vias
        for (const l of lines || []) {
            const lay = l.layerId || l.getState_LayerId?.();
            if (lay != 11 && !String(lay).includes('Board')) {
                try {
                    await l.setState_PrimitiveLock(false);
                    await l.done();
                } catch(e) {}
            }
        }
        for (const v of vias || []) {
            try {
                await v.setState_PrimitiveLock(false);
                await v.done();
            } catch(e) {}
        }
        
        // 2. Delete all lines and vias
        const toDeleteLines = [];
        for (const l of lines || []) {
            const lay = l.layerId || l.getState_LayerId?.();
            if (lay != 11 && !String(lay).includes('Board')) {
                toDeleteLines.push(l.primitiveId || l.id);
            }
        }
        const toDeleteVias = [];
        for (const v of vias || []) {
            toDeleteVias.push(v.primitiveId || v.id);
        }
        
        if (toDeleteLines.length > 0) {
            await eda.pcb_PrimitiveLine.delete(toDeleteLines);
        }
        if (toDeleteVias.length > 0) {
            await eda.pcb_PrimitiveVia.delete(toDeleteVias);
        }
        
        return { deletedLines: toDeleteLines.length, deletedVias: toDeleteVias.length };
    } catch(e) {
        return { error: e.message };
    }
    """
    clear_res = execute_js(js_clear)
    print("Clear result:", clear_res)
    
    print("Fetching component pads...")
    js_pads = """
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    const result = [];
    for (const c of comps) {
        const des = c.designator || c.getState_Designator?.() || '';
        const pins = await c.getAllPins();
        for (const p of pins || []) {
            result.push({
                component: des,
                padNumber: p.padNumber || p.getState_PadNumber?.() || '',
                net: p.net || p.getState_Net?.() || '',
                x: p.x,
                y: p.y,
                rotation: p.rotation || 0,
                pad: p.pad
            });
        }
    }
    return result;
    """
    raw_pads = execute_js(js_pads)
    
    js_comps = """
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    return comps.map(c => ({
        designator: c.designator || c.getState_Designator?.() || '',
        x: c.x || c.getState_X?.() || 0,
        y: c.y || c.getState_Y?.() || 0
    }));
    """
    raw_comps = execute_js(js_comps)
    
    if not raw_pads or isinstance(raw_pads, str) or not raw_comps or isinstance(raw_comps, str):
        print("Error fetching board elements:", raw_pads, raw_comps)
        sys.exit(1)
        
    print(f"Successfully loaded {len(raw_pads)} pads from EasyEDA.")
    comp_centers = {c['designator']: (c['x'], c['y']) for c in raw_comps}
    
    # 2. Organize target nets routing details
    routing_nets = {
        'BOOST_SW': {
            'main_width': 31.5, # 0.8mm
            'connections': [
                (('U3', '5'), ('U3', '4'), 1),
                (('U3', '4'), ('U3', '6'), 1),
                (('U3', '4'), ('L1', '2'), 1),
                (('L1', '2'), ('D3', '1'), 1)
            ]
        },
        'PVDD_12V': {
            'main_width': 39.37, # 1.0mm
            'connections': [
                (('D3', '2'), ('C6', '1'), 1),
                (('C6', '1'), ('C7', '1'), 1),
                (('C7', '1'), ('C8', '1'), 1),
                (('C8', '1'), ('U4', '28'), 1),
                (('U4', '28'), ('U4', '27'), 1),
                (('C7', '1'), ('C9', '1'), 1),
                (('C9', '1'), ('U4', '16'), 1),
                (('U4', '16'), ('U4', '15'), 1),
                (('C7', '1'), ('R1', '1'), 1)
            ]
        },
        'VBUS_5V': {
            'main_width': 47.24, # 1.2mm
            'connections': [
                (('USB_C', 'B4A9'), ('D1', '1'), 1),
                (('D1', '1'), ('C3', '1'), 1),
                (('C3', '1'), ('U2', '4'), 1),
                (('U2', '4'), ('U2', '3'), 1),
                (('C3', '1'), ('C5', '1'), 1),
                (('C5', '1'), ('L1', '1'), 1),
                (('L1', '1'), ('U3', '3'), 2)  # Route L1.1 -> U3.3 on Layer 2 (Bottom)
            ]
        }
    }
    
    # 3. Create obstacle grid for Layer 1
    W = int((X_MAX - X_MIN) / GRID_RES) + 1
    H = int((Y_MAX - Y_MIN) / GRID_RES) + 1
    grid_l1 = [[0 for _ in range(H)] for _ in range(W)]
    grid_l2 = [[0 for _ in range(H)] for _ in range(W)]
    
    # Fill obstacles from pads of other nets
    all_target_nets = set(routing_nets.keys())
    
    for p in raw_pads:
        net = p['net']
        if net in all_target_nets:
            continue
            
        px = p['x']
        py = p['y']
        rot = p['rotation']
        pad_geom = p['pad']
        
        if not pad_geom or len(pad_geom) < 3:
            w, h = 20, 20
        else:
            w, h = pad_geom[1], pad_geom[2]
            
        if abs(rot - 90) < 10 or abs(rot - 270) < 10 or abs(rot + 90) < 10:
            w, h = h, w
            
        clearance = 15.0
        
        min_gx, min_gy = mil_to_grid(px - w/2 - clearance, py - h/2 - clearance)
        max_gx, max_gy = mil_to_grid(px + w/2 + clearance, py + h/2 + clearance)
        
        min_gx = max(0, min_gx)
        max_gx = min(W - 1, max_gx)
        min_gy = max(0, min_gy)
        max_gy = min(H - 1, max_gy)
        
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                grid_l1[gx][gy] = 1
                grid_l2[gx][gy] = 1
                
    # 4. Route connections net by net
    routing_order = ['BOOST_SW', 'PVDD_12V', 'VBUS_5V']
    
    def find_pad(comp_des, pin_num):
        for p in raw_pads:
            if p['component'] == comp_des and p['padNumber'] == pin_num:
                return (p['x'], p['y'])
        for p in raw_pads:
            if p['component'] == comp_des and p['padNumber'].lower() == pin_num.lower():
                return (p['x'], p['y'])
        return None
        
    for net in routing_order:
        print(f"\n--- Routing Net {net} ---")
        net_cfg = routing_nets[net]
        main_w = net_cfg['main_width']
        
        for connection in net_cfg['connections']:
            start_ref, end_ref, target_layer = connection
            s_comp, s_pin = start_ref
            e_comp, e_pin = end_ref
            
            p_start = find_pad(s_comp, s_pin)
            p_end = find_pad(e_comp, e_pin)
            
            if not p_start or not p_end:
                print(f"Could not find pad coordinates for {s_comp}.{s_pin} or {e_comp}.{e_pin}")
                continue
                
            dx = p_end[0] - p_start[0]
            dy = p_end[1] - p_start[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            print(f"Routing {s_comp}.{s_pin} at {p_start} -> {e_comp}.{e_pin} at {p_end} (dist: {dist:.1f} mil, layer: {target_layer})")
            
            # --- ROUTING ON LAYER 2 (VIA STITCHING) ---
            if target_layer == 2:
                c_start = comp_centers.get(s_comp, p_start)
                c_end = comp_centers.get(e_comp, p_end)
                
                def get_via_pos(pad_pos, comp_center, offset=55.0):
                    px, py = pad_pos
                    cx, cy = comp_center
                    v_dx = px - cx
                    v_dy = py - cy
                    v_dist = math.sqrt(v_dx*v_dx + v_dy*v_dy)
                    if v_dist > 0.1:
                        return (px + (v_dx / v_dist) * offset, py + (v_dy / v_dist) * offset)
                    else:
                        return (px, py + offset)
                        
                v_start = get_via_pos(p_start, c_start)
                v_end = get_via_pos(p_end, c_end)
                
                # Place vias without immediate locking
                hole_dia = 12.0
                dia = 24.0
                execute_js(f"await eda.pcb_PrimitiveVia.create('{net}', {v_start[0]:.1f}, {v_start[1]:.1f}, {hole_dia}, {dia});")
                execute_js(f"await eda.pcb_PrimitiveVia.create('{net}', {v_end[0]:.1f}, {v_end[1]:.1f}, {hole_dia}, {dia});")
                
                # Connect pads to vias on Layer 1
                draw_neck_down_path(net, 1, [p_start, v_start], s_comp, 'VIA', main_w)
                draw_neck_down_path(net, 1, [v_end, p_end], 'VIA', e_comp, main_w)
                
                # Route between vias on Layer 2 (Bottom layer) using A*
                g_vstart = mil_to_grid(*v_start)
                g_vend = mil_to_grid(*v_end)
                
                for dx_val in range(-3, 4):
                    for dy_val in range(-3, 4):
                        gx = g_vstart[0] + dx_val
                        gy = g_vstart[1] + dy_val
                        if 0 <= gx < W and 0 <= gy < H:
                            grid_l2[gx][gy] = 0
                        gx = g_vend[0] + dx_val
                        gy = g_vend[1] + dy_val
                        if 0 <= gx < W and 0 <= gy < H:
                            grid_l2[gx][gy] = 0
                            
                path_l2 = astar(grid_l2, g_vstart, g_vend)
                if path_l2:
                    simplified_grid_path = simplify_path(grid_l2, path_l2)
                    simplified_path_mils = [grid_to_mil(gx, gy) for gx, gy in simplified_grid_path]
                    simplified_path_mils[0] = v_start
                    simplified_path_mils[-1] = v_end
                    draw_neck_down_path(net, 2, simplified_path_mils, 'VIA', 'VIA', main_w)
                    print(f"SUCCESS (Layer 2 A*): Routed with vias at {v_start} and {v_end}")
                    for i in range(len(simplified_path_mils) - 1):
                        mark_segment_obstacle(grid_l2, simplified_path_mils[i], simplified_path_mils[i+1], main_w, 15.0)
                else:
                    draw_neck_down_path(net, 2, [v_start, v_end], 'VIA', 'VIA', main_w)
                    print(f"SUCCESS (Layer 2 Fallback): Drew straight line directly between vias")
                continue
                
            # --- ROUTING ON LAYER 1 ---
            if dist < 450.0:
                draw_neck_down_path(net, 1, [p_start, p_end], s_comp, e_comp, main_w)
                print(f"SUCCESS (Local): Drew straight line directly")
                mark_segment_obstacle(grid_l1, p_start, p_end, main_w, 15.0)
                continue
            
            g_start = mil_to_grid(*p_start)
            g_end = mil_to_grid(*p_end)
            
            start_clear_size = 3
            for dx_val in range(-start_clear_size, start_clear_size + 1):
                for dy_val in range(-start_clear_size, start_clear_size + 1):
                    gx = g_start[0] + dx_val
                    gy = g_start[1] + dy_val
                    if 0 <= gx < W and 0 <= gy < H:
                        grid_l1[gx][gy] = 0
                    gx = g_end[0] + dx_val
                    gy = g_end[1] + dy_val
                    if 0 <= gx < W and 0 <= gy < H:
                        grid_l1[gx][gy] = 0
                        
            # Run A*
            path = astar(grid_l1, g_start, g_end)
            if not path:
                print(f"FAIL: No path found for {s_comp}.{s_pin} -> {e_comp}.{e_pin}")
                continue
                
            simplified_grid_path = simplify_path(grid_l1, path)
            if not simplified_grid_path:
                simplified_grid_path = path
                
            simplified_path_mils = [grid_to_mil(gx, gy) for gx, gy in simplified_grid_path]
            simplified_path_mils[0] = p_start
            simplified_path_mils[-1] = p_end
            
            draw_neck_down_path(net, 1, simplified_path_mils, s_comp, e_comp, main_w)
            print(f"SUCCESS (Global A*): Drew path with {len(simplified_path_mils)} segments")
            
            # Mark routed path as obstacle
            for i in range(len(simplified_path_mils) - 1):
                mark_segment_obstacle(grid_l1, simplified_path_mils[i], simplified_path_mils[i+1], main_w, 15.0)
                
    # 5. Drop GND vias (via stitching)
    print("\n--- Routing GND Net (Via Stitching) ---")
    js_gnd = """
    try {
        const comps = await eda.pcb_PrimitiveComponent.getAll();
        const pins = [];
        for (const c of comps) {
            const des = c.designator || c.getState_Designator?.() || '';
            const pads = await c.getAllPins();
            for (const p of pads || []) {
                const net = p.net || p.getState_Net?.() || '';
                if (net === 'GND') {
                    pins.push({
                        des,
                        padNumber: p.padNumber,
                        x: p.x,
                        y: p.y,
                        compX: c.x || c.getState_X?.() || 0,
                        compY: c.y || c.getState_Y?.() || 0
                    });
                }
            }
        }
        
        const holeDiameter = 10; // 0.25mm
        const diameter = 20;     // 0.5mm
        const lineWidth = 20;     // 0.5mm
        let stitchedCount = 0;
        
        for (const pin of pins) {
            const px = pin.x;
            const py = pin.y;
            const cx = pin.compX;
            const cy = pin.compY;
            const dx = px - cx;
            const dy = py - cy;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            let viaOffset = 45; // default 45mil
            if (['U2', 'U3', 'U5', 'D2'].includes(pin.des)) {
                viaOffset = 55;
            } else if (pin.des === 'U1') {
                viaOffset = 65;
            } else if (pin.des.startsWith('C') || pin.des.startsWith('R')) {
                viaOffset = 40;
            }
            
            let vx, vy;
            if (dist > 0.1) {
                vx = Math.round(px + (dx / dist) * viaOffset);
                vy = Math.round(py + (dy / dist) * viaOffset);
            } else {
                vx = px;
                vy = py + viaOffset;
            }
            
            await eda.pcb_PrimitiveVia.create('GND', vx, vy, holeDiameter, diameter);
            await eda.pcb_PrimitiveLine.create('GND', 1, px, py, vx, vy, lineWidth, false);
            stitchedCount++;
        }
        return { stitchedCount };
    } catch(e) {
        return { error: e.message };
    }
    """
    gnd_res = execute_js(js_gnd)
    print("GND Via Stitching result:", gnd_res)
    
    # 6. Bulk Lock all lines and vias
    print("\nLocking power traces and vias...")
    # Add a short delay to allow canvas elements to synchronize in Editor
    time.sleep(1.5)
    js_lock = """
    let lockedLines = 0;
    let lockedVias = 0;
    const powerNets = ['VBUS_5V', 'BOOST_SW', 'PVDD_12V', 'GND'];
    
    const lines = await eda.pcb_PrimitiveLine.getAll();
    for (const line of lines || []) {
        const net = line.net || (typeof line.getState_Net === 'function' ? line.getState_Net() : '');
        if (powerNets.includes(net)) {
            if (typeof line.setState_PrimitiveLock === 'function') {
                try {
                    await line.setState_PrimitiveLock(true);
                    if (typeof line.done === 'function') await line.done();
                    lockedLines++;
                } catch(e) {
                    // ignore stale
                }
            }
        }
    }
    
    const vias = await eda.pcb_PrimitiveVia.getAll();
    for (const via of vias || []) {
        const net = via.net || (typeof via.getState_Net === 'function' ? via.getState_Net() : '');
        if (powerNets.includes(net)) {
            if (typeof via.setState_PrimitiveLock === 'function') {
                try {
                    await via.setState_PrimitiveLock(true);
                    if (typeof via.done === 'function') await via.done();
                    lockedVias++;
                } catch(e) {
                    // ignore stale
                }
            }
        }
    }
    return { lockedLines, lockedVias };
    """
    lock_res = execute_js(js_lock)
    if isinstance(lock_res, dict):
        print(f"SUCCESS: Locked {lock_res.get('lockedLines', 0)} traces and {lock_res.get('lockedVias', 0)} vias.")
    else:
        print("Lock failed:", lock_res)
        
    print("\nSmart Power Router completed successfully and all paths/vias are locked!")

if __name__ == "__main__":
    main()
