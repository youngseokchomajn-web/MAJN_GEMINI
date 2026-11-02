# MAJN Engineering Roadmap and Work Packages

- Status: Proposed sequence; dates are assigned only after WP-00 audit estimates effort.
- Rule: phase completion is determined by exit criteria, not calendar dates or generated progress percentages.

## Phase 0 — Source audit and baseline integrity

### WP-00: Repository and artifact inventory
- Inventory relevant repositories, branches, docs, CAD/DXF/STEP/GLB, PCB sources/fabrication outputs, firmware, simulator, CAE inputs/results, test data, and regulatory/evidence docs.
- For each item record path, owner, artifact type, revision if known, last-modified/commit, status, dependencies, and confidence.
- Identify duplicates, stale copies, generated files, missing native sources, and files whose provenance is unclear.

### WP-01: Configuration and discrepancy audit
- Reconcile enclosure dimensions and DXF units/layers against approved source drawings.
- Reconcile current CAD viewer and housing configuration against actual geometry.
- Identify which values are different product revisions, concept variants, simulation assumptions, or errors; do not choose a winner without evidence.
- Reconcile EasyEDA design source, manufacturing outputs, assembled PCB identity, and firmware compatibility.
- Reconcile prototype serial/board/module/antenna/exciter wiring and test records.
- Review CAE material, contacts, boundary conditions, loads, damping, mesh, and validation evidence.
- Mark every unresolved item as blocked/open, with owner and evidence required.

**Phase 0 exit:** source-of-truth matrix, configuration manifest for each known prototype, discrepancy register, and explicit approved baseline or a documented list of unresolved blockers. No downstream automation may assume unresolved values.

## Phase 1 — Engineering Core

### WP-02: Domain and artifact governance
- Publish domain register and owner/responsibility matrix.
- Adopt ID, revision, status, metadata, units, provenance, and file naming rules.
- Define source-vs-derivative rules and approval/verification separation.

### WP-03: Requirements, interfaces, and configuration registry
- Import existing requirements and interface facts with source links.
- Create requirements, part, BOM, interface, risk, test, evidence, and configuration registries.
- Create schema validation and cross-reference checks.
- Add ECO template and impact checklist.

**Phase 1 exit:** every new artifact has a valid ID and metadata; a sample prototype configuration can be reconstructed from registry records; validators run in CI.

## Phase 2 — Mechanical and electrical integration

### WP-04: CAD baseline and conversion pipeline
- Select the approved DXF/drawing baseline.
- Validate units, scale, layer mapping, dimensions, and closed profiles.
- Generate native CAD parts and assemblies; export STEP and GLB derivatives.
- Compare critical geometry against controlled dimensions and report deviations.
- Keep the existing Three.js viewer; connect nodes to part IDs.

### WP-05: Electrical packaging and cable harness
- Place PCB, amplifier, power source, actuator, sensors, connectors, and antenna in the approved assembly.
- Define cable endpoints, pinout, conductor/gauge, insulation/rating, length, bend radius, retention, service loop, and routing revision.
- Run geometric clearance/interference and voltage-drop checks where inputs are known.
- Create assembly/service access review and test plan for vibration abrasion/fatigue and EMC concerns.

### WP-06: Drawing, DFM, assembly review
- Automate drawing/BOM/CAD checks and hole/fastener/clearance checks.
- Define severity classes and deviation approval.
- Generate exploded view and assembly sequence.
- Validate critical steps with a physical build.

**Phase 2 exit:** approved design candidate has consistent CAD/drawing/BOM, routed harness, electrical interface map, review reports, and documented assembly feasibility.

## Phase 3 — Electronics, firmware, and CAE integration

### WP-07: PCB and firmware configuration integration
- Define board/firmware compatibility manifest.
- Automate ERC/DRC, build, unit tests, protocol tests, and binary hash capture.
- Add integration checks for amplifier, actuator load, sensor, power, wireless, and fault response.
- Add HIL tests as hardware fixtures become available.

### WP-08: CAE pipeline and correlation
- Create controlled geometry simplification rules.
- Version material data, joints, boundary conditions, loads, mesh settings, and solver version.
- Automate static/modal/harmonic/FRF analyses only where justified.
- Import physical test data and compare outputs under matched conditions.
- Document correlation error, uncertainty, and limitations.

**Phase 3 exit:** a named product configuration can reproduce its firmware build and selected CAE results with full input provenance; simulation is not used beyond validated scope.

## Phase 4 — Risk, verification, and research evidence

### WP-09: Risk and fault verification
- Build hazard log and FMEA from system architecture and use scenarios.
- Link risk controls to requirements, design artifacts, and tests.
- Define fault injection and fail-safe tests for power, sensor, amplifier, communications, and mechanical/electrical failures.

### WP-10: Measurement and test automation
- Standardize test article ID, sensor/equipment calibration, sample rate, units, load, mattress/contact surface, environment, and operator.
- Preserve raw data and processing scripts.
- Automate plots/metrics and requirement status updates without auto-approving results.
- Separate actuator electrical output from bassinet/contact-surface vibration and human outcome measures.

### WP-11: Research/evidence and usability preparation
- Map claims to evidence strength and gaps.
- Define study questions and measurement endpoints with qualified research partners.
- Prepare usability scenarios, use-error assessment, participant/data governance, and ethics/regulatory pre-checks.
- Do not conduct human-subject research before required approvals.

**Phase 4 exit:** critical requirements and risk controls have defined evidence; gaps and residual risks are reviewed; research claims remain bounded by evidence.

## Phase 5 — Manufacturing, regulatory, and lifecycle readiness

### WP-12: Manufacturing and quality package
- Separate engineering BOM and manufacturing BOM.
- Create supplier and approved part lists, process flow, critical-to-quality list, inspection plan, work instructions, pilot build records, nonconformance/CAPA process.
- Confirm traceability from built unit to exact configuration.

### WP-13: Regulatory and release documentation
- Confirm product classification and applicable conformity path with qualified parties/labs.
- Assemble technical documentation, pre-compliance and required test evidence, labels, manuals, packaging, service, complaint and field-action procedures.
- Define release authority and unresolved-risk disposition.

**Phase 5 exit:** pilot build, inspection, regulatory evidence, labeling/manuals, service and post-release processes are reviewed and approved by responsible people.

## Cross-phase control loops

- Any design change creates an ECO and impact assessment across all 18 domains.
- Affected tests and analyses are invalidated or marked for review; they are not silently carried forward.
- A changed CAD geometry can trigger rerouting, drawing, assembly, and CAE review.
- A changed PCB can trigger enclosure, cable, thermal, EMC, firmware, and test review.
- A firmware change can trigger protocol, safety, usability, and regression-test review.
- A changed intended use or product claim can trigger requirements, research, risk, and regulatory reassessment.
- Production or field failures feed back into risk, requirements, design, supplier, and verification records.

## Work package issue template

Each GitHub issue should include:
- WP ID and domain IDs;
- objective and scope/non-scope;
- prerequisites and source artifact IDs;
- implementation tasks;
- outputs and expected paths;
- validation commands/checks;
- acceptance criteria;
- risks and human approval required;
- affected domains and regression checks;
- owner, reviewer, and target milestone.

## First execution sequence

1. WP-00 inventory.
2. WP-01 discrepancy/configuration audit.
3. G0 review and baseline decision.
4. WP-02 domain/metadata governance.
5. WP-03 core registries and validation.
6. Only then begin automated CAD, cable-routing, drawing, and CAE pipelines.

Do not parallelize tasks that depend on unresolved geometry, PCB, or prototype identity. Independent document inventory and schema design may proceed in parallel.
