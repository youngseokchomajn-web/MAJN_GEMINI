# MAJN Engineering Domain Register

This register defines the scope and boundaries of the 18 engineering domains. It is the authority for domain ownership; detailed execution sequencing belongs in ENGINEERING_ROADMAP.md.

| ID | Domain | Primary responsibility | Inputs | Controlled outputs | Main downstream consumers |
|---|---|---|---|---|---|
| E01 | Product requirements | Intended use, users, needs, measurable requirements, acceptance criteria | Product strategy, user/research/regulatory input | REQ register, verification cross-reference | All domains |
| E02 | System architecture | Subsystems, interfaces, power/data/mechanical flows, fault states | E01, product concept | Architecture, ICD, interface matrix | E04–E18 |
| E03 | Engineering data & configuration | IDs, BOM, revisions, ECO, configuration manifest | All domain artifacts | Part registry, BOM, revision/ECO records | All domains |
| E04 | 3D modeling & CAD | Editable dimension-driven geometry and assemblies | Approved drawings, dimensions, part specs | Native CAD, STEP, geometry metadata | E05, E06, E09–E11 |
| E05 | 3D visualization | Human-readable model presentation and overlays | Approved CAD derivatives, part mapping | GLB, viewer, visualization manifest | Design review, assembly, communication |
| E06 | Electrical packaging & cable routing | Physical integration of cables, connectors, retention, routing | CAD, PCB/enclosure, ICD, electrical ratings | Harness model, wiring diagram, cable BOM | E07, E09, E10, E12, E13, E17 |
| E07 | Electronics & PCB | Schematic, PCB, power, sensing, amplifier, protection, EMC | E01/E02, component datasheets, mechanical constraints | PCB source, fabrication package, electrical BOM, DRC/ERC | E06, E08, E12, E13, E16, E17 |
| E08 | Firmware & control | Embedded behavior, communication, control, OTA, fault response | ICD, PCB, actuator/sensor specifications | Firmware release, protocol, build/test manifest | E12, E13, E14, E16, E18 |
| E09 | Drawing & design review | Dimension/tolerance/drawing/BOM/DFM checks | CAD, drawings, BOM, manufacturing constraints | Review reports, deviations, issue register | E04, E06, E07, E10, E17 |
| E10 | Assembly & serviceability | Build sequence, access, tool clearance, repair/replacement | CAD, harness, fasteners, service scenarios | Assembly sequence, work instructions, service review | E04, E06, E17, E18 |
| E11 | CAE & simulation | Structural, modal, harmonic, FRF, thermal, fatigue as justified | CAD, material, joints, loads, boundary conditions | Solver model, logs, results, correlation | E04, E06, E09, E12, E13 |
| E12 | Safety & reliability | Hazards, FMEA, fault analysis, risk controls, durability | Requirements, architecture, design, use scenarios | Hazard log, FMEA, risk-control verification | All design domains, E13, E16–E18 |
| E13 | Verification & measurement | Test methods, instrumentation, raw data, acceptance evidence | Requirements, risk controls, prototypes, test articles | Protocols, raw/processed data, reports | E01, E04–E18 |
| E14 | Usability & human factors | Use scenarios, use errors, interaction, labeling inputs | User needs, UI, product configuration | Use-error register, usability reports | E01, E08, E12, E15, E16, E18 |
| E15 | Research & clinical evidence | Literature, study design, research collaboration, ethics/data plan | Research questions, prototype, measurement methods | Evidence matrix, protocol, research reports | E01, E12–E16, claims review |
| E16 | Regulatory & conformity | Product classification, applicable regulations/standards, test route | Intended use, architecture, safety, product claims | Applicability matrix, certification plan, technical file index | E07, E12–E18 |
| E17 | Manufacturing & quality | DFM/DFA, supplier, process, inspection, CAPA, pilot build | Approved design, BOM, risk/critical characteristics | M-BOM, work instructions, inspection/quality records | E03, E09–E13, E16, E18 |
| E18 | Product lifecycle | Packaging, labeling, manuals, service, complaints, field action, obsolescence | Approved product configuration, usability/regulatory/quality | Release docs, service records, complaint/field action log | E01, E03, E08, E12, E14–E17 |

## Boundary rules

- **3D modeling vs visualization:** E04 owns editable geometry and dimensional correctness. E05 owns rendering and interaction; visual similarity is not dimensional proof.
- **Cable routing vs PCB:** E06 owns physical harness route, retention, access, and cable BOM. E07 owns circuit topology, electrical ratings, PCB and pin-level electrical design. Shared interfaces are controlled through ICD and connector/pin registry.
- **Drawing review vs assembly review:** E09 checks design definition and manufacturability. E10 checks whether people can assemble, disassemble, and service the design.
- **CAE vs test:** E11 predicts behavior under modeled assumptions. E13 measures real behavior and records uncertainty. Neither silently substitutes for the other.
- **Safety vs regulatory:** E12 identifies and controls product risks. E16 determines applicable legal/conformity obligations. Regulatory compliance does not automatically prove all product risks are controlled.
- **Research vs engineering verification:** E15 addresses research questions and human outcomes. E13 verifies engineering requirements. Bench vibration data alone does not establish infant calming/sleep efficacy.
- **AI/automation:** cross-domain service. It does not own engineering approval or replace accountable domain owners.

## Common artifact lifecycle

`draft → in_review → approved → verified → released`

Additional states: `blocked`, `rejected`, `superseded`, `withdrawn`. Not every artifact requires every state. Approval and verification are distinct; a document can be approved as a plan without its future test results being verified.

## Required metadata

Every controlled artifact should carry, where applicable:
- artifact ID and artifact type;
- domain and responsible owner;
- product configuration and revision;
- source artifact IDs and hashes;
- related requirements, parts, interfaces, risks, tests, and ECOs;
- tool/software version and execution environment;
- status, reviewer, approval date, and validation status.

## Change impact minimum

Any ECO must identify affected requirements, parts/assemblies, CAD/drawings, cables/connectors, PCB, firmware/protocol, CAE, hazards/risk controls, test protocols/results, manufacturing documents, regulatory records, and lifecycle documents. Mark each as affected, reviewed-no-change, not-applicable, or unresolved.
