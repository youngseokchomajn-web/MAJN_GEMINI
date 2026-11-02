# MAJN Integrated Engineering System — Master Plan

- Status: Draft for engineering baseline review
- Scope: MAJN smart bassinet product engineering, from requirements through lifecycle
- Owner: MAJN project team
- Baseline: Not yet approved; existing artifacts must be audited before being treated as authoritative

## 1. Purpose

Build one traceable engineering system connecting product requirements, mechanical design, electrical design, embedded software, cable routing, CAE, verification, safety, research, regulatory assessment, manufacturing, quality, and lifecycle support.

This is not a proposal to replace every existing tool or rewrite existing work. Existing repositories, CAD, PCB, firmware, simulator, measurement plans, and decision records are to be inventoried, assessed, and linked. Rebuild only where evidence shows it is necessary.

## 2. Governing principles

1. **One controlled baseline:** no dimension, BOM, board revision, or performance value becomes authoritative merely because it appears in a file.
2. **Separate source from derivatives:** DXF/approved drawings, native CAD, STEP, GLB, solver meshes, reports, and rendered images have different purposes.
3. **Traceability by IDs:** requirements, systems, parts, cables, drawings, firmware, analyses, risks, tests, evidence, and changes share stable identifiers.
4. **Revision-aware results:** every test and analysis identifies the exact product, hardware, firmware, CAD, and configuration revisions used.
5. **Verification is not authorship:** AI-generated files and reports remain draft until independently checked; an agent cannot approve its own safety-critical output.
6. **Risk-driven sequencing:** resolve baseline conflicts and safety-critical unknowns before automating downstream workflows.
7. **Human approval at gates:** engineering, safety, regulatory, clinical/research, and release decisions require accountable human review.
8. **Reproducibility:** scripts, tool versions, solver settings, inputs, logs, and raw measurements are retained.
9. **No unsupported claims:** simulation, bench measurements, user observations, clinical evidence, certification, and regulatory status are kept distinct.
10. **Avoid duplicate systems:** extend the current Three.js viewer, FreeCAD/CAD workflow, EasyEDA, PlatformIO, and CAE environment where practical; adopt new tools only for a documented capability gap.

## 3. Engineering domains

The authoritative domain list is in [ENGINEERING_DOMAIN_REGISTER.md](ENGINEERING_DOMAIN_REGISTER.md). The 18 domains are:

- E01 Product requirements and intended use
- E02 System architecture and interface definition
- E03 Engineering data, configuration, BOM, and change control
- E04 Parametric 3D modeling and CAD
- E05 3D visualization and digital assembly presentation
- E06 Electrical packaging, cable routing, and harness integration
- E07 Electronics, schematic, PCB, power, and EMC design
- E08 Embedded firmware, communications, and control
- E09 Drawing and design verification
- E10 Assembly, serviceability, and maintainability
- E11 CAE and physical simulation
- E12 Product safety, hazard analysis, and reliability
- E13 Verification, measurement, and test engineering
- E14 Usability and human factors
- E15 Research and clinical evidence collaboration
- E16 Regulatory strategy and conformity assessment
- E17 Manufacturing engineering and quality
- E18 Product lifecycle, packaging, service, and post-market feedback

AI/automation is a cross-cutting execution layer, not a nineteenth engineering domain.

## 4. Domain development plans

### E01 — Product requirements
Develop a controlled requirements register covering intended use, users, use environments, functional behavior, measurable performance, constraints, safety requirements, and non-goals. Each requirement gets an ID, rationale, source, owner, priority, status, verification method, acceptance criteria, and linked evidence. Separate confirmed requirements from hypotheses and open questions.
**Outputs:** requirements register, verification cross-reference, change history.
**Exit:** all critical requirements have measurable acceptance criteria or an explicitly approved open issue.

### E02 — System architecture
Create system context, functional block diagrams, subsystem decomposition, state/data/power flows, interface control documents (ICDs), fault-state behavior, and allocation of requirements to subsystems. Include mechanical, actuator, amplifier, power, sensing, ESP32, mobile/web UI, wireless, and external accessories where applicable.
**Outputs:** architecture diagrams, subsystem registry, ICDs, interface matrix.
**Exit:** every critical interface has defined owner, signals/power/mechanics, limits, connector/pin mapping where relevant, and verification method.

### E03 — Engineering data and configuration management
Establish stable IDs for parts, assemblies, cables, PCBs, firmware, drawings, analyses, tests, risks, evidence, and engineering changes. Maintain master BOM, approved source pointers, revision state, compatibility matrix, and Engineering Change Orders (ECOs). Preserve legacy paths until migration is verified.
**Outputs:** part registry, BOM, revision registry, ECO log, configuration manifest.
**Exit:** a physical prototype can be reconstructed from a recorded configuration manifest.

### E04 — 3D modeling and CAD
Audit DXF layers, units, scale, dimensions, constraints, and drawing revision. Build dimension-driven native CAD parts and assemblies; manage material, thickness, hole, bend, fastener, and interface parameters. Export STEP for exchange and manufacturing/CAE handoff. Keep native editable source as the design authority after approval; do not treat GLB as CAD source.
**Tools:** existing CAD workflow and FreeCAD; CadQuery only where scripted parametric generation adds clear value.
**Outputs:** native CAD, STEP, part geometry metadata, model validation report.
**Exit:** critical dimensions and interfaces match the approved drawing/parameter baseline; exports pass geometry and unit checks.

### E05 — 3D visualization
Extend the existing Three.js viewer. Import GLB/glTF derivatives, link model nodes to part IDs and BOM metadata, support visibility, exploded views, section/cutaway views, selection, revision comparison, and overlays for sensor/test locations or CAE results. Visualization is not a substitute for dimensional verification.
**Outputs:** viewer, model-to-part mapping, visualization build manifest.
**Exit:** all displayed parts resolve to controlled part IDs and the viewer identifies the source revision.

### E06 — Electrical packaging and cable routing
Model PCB, amplifier, power supply, sensors, connectors, cable paths, clips, grommets, strain relief, and service loops in the mechanical assembly. Calculate length and voltage drop; check bend radius, clearance, abrasion, pinch points, moving/vibrating sections, connector access, assembly order, and separation of power/signal/RF paths. Maintain a wiring diagram, pin map, cable BOM, and harness revision. EMI and fatigue risks require physical validation.
**Outputs:** 3D harness, wiring diagram, cable/connector BOM, routing review.
**Exit:** each cable has endpoint IDs, pinout, electrical rating, length, route, retention method, and inspection/test criteria.

### E07 — Electronics and PCB
Control schematic, symbols/footprints, netlist, PCB layout, power tree, protection, thermal design, sensor interfaces, amplifier/load compatibility, grounding, EMC pre-compliance, and manufacturing outputs. Automate ERC/DRC and BOM/netlist checks. Keep design files, fabrication files, assembled-board identity, and test evidence tied to a board revision.
**Outputs:** schematic, PCB source, Gerber/fabrication package, BOM, DRC/ERC report, board test record.
**Exit:** manufacturing package and assembled hardware are revision-consistent; unresolved electrical risks are documented and gated.

### E08 — Firmware and control
Maintain architecture, state machine, protocol specification, drivers, control limits, sensor calibration, fault handling, watchdog, safe-state behavior, OTA/recovery, logging, and automated tests. Include hardware-in-loop tests where feasible. Record source commit, compiler/platform versions, build flags, binary hash, board revision, and configuration.
**Outputs:** firmware release manifest, protocol specification, unit/integration/HIL test results.
**Exit:** release candidate passes defined tests on identified hardware and fault scenarios; no unverified claim of safe infant use is made.

### E09 — Drawing and design review
Automate drawing/model/BOM consistency, dimensions, hole positions, tolerances, missing views/notes, material/finish callouts, fastener interfaces, and manufacturability checks. Classify findings by severity and record approved deviations. Automated geometry checks must distinguish exact checks from heuristic warnings.
**Outputs:** drawing review report, dimensional checklist, issue register.
**Exit:** all critical findings closed or formally accepted with rationale and owner.

### E10 — Assembly and serviceability
Review assembly sequence, tool access, fastener reach, connector mating, cable installation, tolerance accumulation, part orientation, human access, replacement, cleaning, and disassembly. Validate critical steps with a physical build, not only a CAD animation.
**Outputs:** assembly sequence, exploded view, work instructions, serviceability review.
**Exit:** critical assembly steps are demonstrated without undocumented forcing, damage, or inaccessible operations.

### E11 — CAE and simulation
Establish validated material properties, contacts/joints, fastener representations, boundary conditions, mesh quality, loads, damping assumptions, solver settings, and convergence checks. Scope includes static, modal, harmonic response, FRF/transmissibility, thermal, fatigue, and optimization only where justified. Correlate with measured data; report uncertainty and model limitations.
**Outputs:** solver-ready model, input deck, logs, results, correlation report.
**Exit:** model assumptions and verification are documented; prediction accuracy is evaluated against suitable physical measurements before design decisions rely on it.

### E12 — Safety and reliability
Maintain hazard log, FMEA/FMECA where useful, fault trees for critical hazards, risk controls, residual risk, fault injection scenarios, reliability assumptions, durability, and post-production feedback. Cover mechanical stability, entrapment/pinch, accessible cables, electrical/thermal hazards, unintended motion/vibration, software faults, cleaning/material concerns, and foreseeable misuse. Applicable standards depend on confirmed product classification and intended use.
**Outputs:** hazard log, FMEA, fault matrix, risk-control verification matrix.
**Exit:** critical hazards have documented controls and verification evidence; residual risks receive accountable review.

### E13 — Verification and measurement
Define test protocols, equipment, calibration, uncertainty, sample/configuration identification, environmental/load conditions, raw-data retention, analysis scripts, acceptance criteria, deviations, and report templates. Separate electrical output, actuator behavior, bassinet structure, mattress/contact-surface response, sound, temperature, endurance, and user/clinical outcomes.
**Outputs:** test plans, raw data, processed data, test reports, calibration records.
**Exit:** critical requirements have repeatable verification results or approved open verification actions.

### E14 — Usability and human factors
Map caregiver and service-user journeys, setup, operation, cleaning, transport, charging/power, alerts, error recovery, foreseeable misuse, and information comprehension. Conduct formative evaluations and controlled usability studies appropriate to development stage.
**Outputs:** use scenarios, use-error register, usability test report, labeling inputs.
**Exit:** critical use errors and mitigations are documented and reviewed.

### E15 — Research and clinical evidence
Maintain evidence matrix distinguishing literature, engineering bench tests, observational studies, feasibility studies, and clinical efficacy/safety evidence. Define research questions, outcomes, measurement instruments, protocols, statistical plans, data governance, collaborators, ethics review, and regulatory consultation as appropriate. Do not infer calming, sleep, or health benefits from vibration output measurements alone.
**Outputs:** research question register, evidence matrix, study protocol, analysis plan.
**Exit:** each external claim is matched to evidence of appropriate type and strength; human-subject research follows applicable approvals.

### E16 — Regulatory and conformity assessment
Determine intended use, product classification, applicable Korean and export-market regulations, required safety/EMC/radio/material tests, labeling, technical documentation, and test-lab engagement. Treat KC categories and medical/child-product classification as questions to resolve with qualified bodies, not assumptions.
**Outputs:** regulatory applicability matrix, certification plan, technical file index, pre-compliance results.
**Exit:** classification and required conformity path are documented and reviewed by qualified parties.

### E17 — Manufacturing and quality
Develop DFM/DFA, supplier qualification, approved vendor/part list, process flow, critical-to-quality characteristics, incoming/in-process/final inspection, traceability, nonconformance/CAPA, pilot build, yield, and production test fixtures. Maintain engineering BOM and manufacturing BOM separately where needed.
**Outputs:** manufacturing BOM, work instructions, inspection plan, supplier register, quality records.
**Exit:** pilot build demonstrates repeatable assembly and inspection against approved configuration.

### E18 — Product lifecycle
Plan packaging/transport protection, labels, user/service manuals, installation, maintenance, firmware support, complaint intake, field issue triage, corrective actions/recall readiness, spare parts, supplier obsolescence, and end-of-life.
**Outputs:** packaging spec, manuals, service process, complaint/field action records.
**Exit:** post-release ownership, traceability, and escalation process are defined before release.

## 5. Cross-domain lifecycle and gates

Use a systems-engineering V-model with iterative change loops:

1. **G0 — Baseline integrity:** source files, dimensions, board/firmware identity, and product configuration are reconciled or explicitly marked unresolved.
2. **G1 — Requirements and architecture:** intended use, requirements, system decomposition, and interfaces are reviewed.
3. **G2 — Design release candidate:** CAD, electrical, cable, firmware, and BOM revisions are mutually compatible.
4. **G3 — Design verification readiness:** drawings, assembly, CAE assumptions, risk controls, and test protocols are reviewed.
5. **G4 — Prototype verification:** defined tests are executed on configuration-identified hardware; failures and deviations are tracked.
6. **G5 — Productization readiness:** manufacturing, quality, regulatory, usability, labeling, and service evidence are reviewed.
7. **G6 — Release and lifecycle:** release authorization, field monitoring, complaint handling, and change control are active.

A gate may be passed with documented non-critical open actions only when an accountable owner, due date, risk rationale, and closure condition exist. Critical safety/regulatory blockers cannot be waived by an AI agent.

## 6. Dependency rules

- E01 feeds all domains; E02 allocates requirements and defines interfaces.
- E03 provides identity/revision/configuration services to all domains.
- E04 is the geometry source for E05, E06, E09, E10, and E11.
- E06 and E07 jointly define physical/electrical interconnects; E08 consumes the controlled interface.
- E09/E10 findings feed back to E04/E06/E07 through ECO.
- E11 predictions must be linked to E13 measurements for correlation.
- E12 risk controls generate verification needs for E13 and design changes for relevant domains.
- E14 use errors feed E01/E08/E16/E18.
- E15 evidence informs claims and product decisions but does not replace E13 engineering verification.
- E16 applicability decisions constrain E07/E12/E13/E17/E18.
- E17 pilot-build findings and E18 field feedback trigger ECOs and regression tests.

## 7. Cross-cutting automation and AI governance

AI agents may draft, transform, analyze, run tests, and prepare review packages. They must:
- use controlled input revisions;
- write to a branch or staging area;
- produce logs and machine-readable reports;
- never overwrite approved source without change control;
- identify uncertainty and unverified assumptions;
- request human approval for release, safety, regulatory, and research decisions;
- never self-approve their own output.

Recommended roles: Engineering Planner, CAD/Mechanical Agent, Electrical Integration Agent, Firmware Agent, CAE/Data Agent, Verification/Quality Agent, and independent Reviewer. Keep role boundaries narrow; add agents only when workload justifies them.

## 8. Initial priority

Do not start by building every automation. Start with WP-00 source audit and G0. The first deliverable is a verified inventory and discrepancy register, not a new CAD model or dashboard. Resolve the current geometry/configuration ambiguity before downstream 3D, routing, assembly, or CAE automation.

## 9. Definition of done for the Engineering System

The system is operational when a controlled product configuration can be traced from requirements through parts, CAD, PCB, cables, firmware, analyses, risk controls, tests, manufacturing records, and lifecycle actions; a change can identify affected artifacts and required regression checks; and release decisions are based on reviewed evidence rather than generated status labels.
