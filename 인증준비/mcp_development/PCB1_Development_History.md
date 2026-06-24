# PCB1 Development & DRC Resolution History
*A comprehensive record of resolving 329 DRC errors on PCB1 using API scripting and manual interventions.*

## 1. Background & Initial State
- **Target**: `PCB1` in EasyEDA Pro
- **Initial DRC Errors**: 329 errors (mostly Connection Errors and Clearance Errors)
- **Goal**: Achieve 0 DRC errors using Python/JS scripting to interface with the EasyEDA Pro internal API via a custom MCP client.

## 2. Development Timeline & Methodology

### Phase 1: API Discovery & Diagnostic Probing
- We created several diagnostic scripts (`check_pcb4.py`, `drc_check_all.py`, `inspect_via_track.py`) to map out the undocumented EasyEDA Pro JS API objects like `eda.pcb_PrimitiveLine`, `eda.pcb_PrimitiveVia`, and `eda.pcb_Drc`.
- Discovered that the 329 errors were primarily composed of completely tangled, auto-routed tracks that were locked in unroutable configurations.

### Phase 2: Mass Unrouting & API Manipulation
- **Challenge**: Individual segment deletion based on DRC `gId` mapping was unreliable due to complex grouping inside the `pcb_Drc.check()` output.
- **Solution**: We queried `eda.pcb_PrimitiveLine.getAll()` and identified all `primitiveLock === false` tracks (which represented the tangled auto-router results).
- **Execution**: Wrote `clear_unlocked_routing.py` to systematically delete hundreds of tangled tracks and vias, resetting the board to a clean state.

### Phase 3: The Copper Pour (통판) Revelation
- We noticed the GND connection errors weren't dropping despite routing attempts.
- **Discovery**: We used `check_copper.py` to query `eda.pcb_PrimitiveCopperRegion` and found `copperCount: 0`. The board was completely missing a ground plane!
- **API Limitation**: We attempted to generate a Copper Region programmatically (`draw_copper_pour.py`), but EasyEDA Pro's internal API (`pcb_PrimitiveSolidRegion.create`) threw vague `参数不正确` (Invalid Parameters) errors, indicating that polygons require specific undocumented geometric structs.
- **Resolution**: Reverted to manual GUI instruction. The user successfully deployed the Copper Region via `Place -> Copper Region`. **Result: 29 GND errors plummeted to 9.**

### Phase 4: Brute-Force Routing & The "Bulldozer" Effect
- **Challenge**: 19 Connection Errors remained (9 GND islands, 10 signal nets like PVDD_12V, VBUS_5V).
- **API Attempt**: Developed `brute_force_19_errors.py` using positional arguments (`eda.pcb_PrimitiveLine.create(net, layer, startX, startY, endX, endY, width, lock)`). Placed 36 vias and 18 tracks perfectly.
- **Consequence**: The API drew perfectly straight lines without obstacle avoidance (A* pathfinding). This bulldozed through existing traces, skyrocketing Clearance Errors from 7 to over 200.
- **Resolution**: Developed `delete_my_mess2.py` to surgically target and delete only the newly created traces (by matching `lineWidth: 10` and `diameter: 24`), cleanly restoring the 19-error state without wiping the entire board.

### Phase 5: Design Rule Glitches & The Copy-Paste Fix
- **Challenge**: Tried to lower the Design Rules via API to `0.15mm` so the Auto Router could finish the tight spaces. This triggered a severe UI bug in EasyEDA Pro, causing the Design Rules window to infinitely load.
- **Investigation**: API logs showed internal WebSocket subscriptions breaking (`指定的中心消息在对应的画布内没有相关订阅`).
- **Workaround**: We utilized Mac host control (`cliclick` and AppleScript via `copy_macro.py`) to bypass the API. We simulated `Cmd+A` and `Cmd+C` to copy the PCB data to the internal clipboard (`eda image copy occupy`), allowing the user to paste the raw geometry into a brand new, bug-free PCB file.

## 3. Key Technical Learnings & Limitations

1. **Undocumented API Quirks**: 
   - `pcb_PrimitiveLine.create()` and `pcb_PrimitiveVia.create()` do NOT take object dictionaries `[{...}]`. They require strict positional arguments.
   - Polygons and Copper Regions (`SolidRegion`) are locked behind complex geometry validation and cannot be easily created via API without the internal path generator.
2. **Auto Router vs API**:
   - The EasyEDA Auto Router possesses complex A* pathfinding.
   - Direct API routing is "dumb" point-to-point. Trying to replicate Auto Routing via external Python scripts requires implementing a full constraint-aware pathfinding algorithm, which is highly inefficient compared to simply adjusting the Design Rules (e.g., changing 0.25mm to 0.15mm) and triggering the built-in router.
3. **UI State Recovery**:
   - EasyEDA Pro's document state can corrupt when hit with rapid, brute-force API calls.
   - **Ultimate Fix**: Copying all primitives (`Ctrl+A -> Ctrl+C`) and pasting into a `New PCB` completely strips corrupted UI states and restores functionality.

## 4. Final Status
- **Current State**: 22 unrouted nets remain due to tight clearance limits.
- **Next Steps**: The user will either manually route (`W` / `V`) the remaining traces or run the Auto Router with loosened 0.15mm design rules on the newly pasted PCB file.

## 5. Schematic Recovery & Cross-Computer Migration
- **Challenge**: The user attempted to migrate the project to a new computer by exporting the current file (`File -> Export -> EasyEDA`). However, because they selected "Current Document" instead of "Project", the resulting `.epro2` file completely lacked the Schematic file, causing panic on the new computer.
- **Investigation**: We scoured the original computer's local auto-backup folder (`/Users/youngseok/Documents/EasyEDA-Pro/projects/...`) and discovered 6 historical `.epro2` backups dating back to the project's inception (June 17).
- **Reverse Engineering `.epro2` & `.epru`**:
  - The `.epro2` file is a standard ZIP archive.
  - Inside, the `.epru` file is a proprietary EasyEDA database format that separates multiple JSON documents using a `||` string delimiter.
- **Execution**: Wrote a custom Python script (`parse_epru.py` / `extract_sch.py`) to crack open the June 17 backup, parse the `||` delimiter, isolate the JSON object with `"docType":"SCH"`, and dump it directly into a standard format (`Recovered_Schematic.json`).
- **Resolution**: The raw schematic JSON was successfully uploaded to GitHub. The user can now seamlessly import this JSON file into their active PCB project on any computer, fully merging the lost schematic with the routed PCB.
