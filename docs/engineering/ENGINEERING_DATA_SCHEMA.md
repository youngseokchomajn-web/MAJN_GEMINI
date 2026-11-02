# MAJN Engineering Data Schema and Traceability Rules

- Status: Draft
- Purpose: common identifiers and metadata for cross-domain traceability
- This document defines a logical contract; implementation may use JSON/YAML/CSV initially. Avoid introducing a database until repository workflows prove insufficient.

## 1. Identifier conventions

Use stable, human-readable IDs. Do not encode mutable dimensions, revision, or file paths into IDs.

| Entity | Pattern | Example |
|---|---|---|
| Requirement | REQ-{DOMAIN}-{NNN} | REQ-MECH-001 |
| System/subsystem | SYS-{NAME}-{NNN} | SYS-ACTUATOR-001 |
| Interface | IF-{FROM}-{TO}-{NNN} | IF-AMP-EXC-001 |
| Part | PART-{CATEGORY}-{NNN} | PART-HOUSING-001 |
| Assembly | ASM-{NAME}-{NNN} | ASM-BASE-001 |
| Cable/harness | CABLE-{NAME}-{NNN} | CABLE-EXC-001 |
| PCB/board | PCB-{NAME}-{NNN} | PCB-MAIN-001 |
| Firmware item/release | FW-{NAME}-{NNN} | FW-SAFETY-001 |
| Drawing | DRW-{NAME}-{NNN} | DRW-HOUSING-001 |
| Analysis | CAE-{TYPE}-{NNN} | CAE-MODAL-001 |
| Risk/hazard | RISK-{TYPE}-{NNN} | RISK-THERMAL-001 |
| Test | TEST-{TYPE}-{NNN} | TEST-VIB-001 |
| Evidence | EVID-{TYPE}-{NNN} | EVID-MEAS-001 |
| Change order | ECO-{YYYY}-{NNN} | ECO-2026-001 |
| Build/configuration | CFG-{NAME}-{NNN} | CFG-PROTOTYPE-001 |

IDs are never reused. Revision is a separate field.

## 2. Common artifact envelope

Example only; each domain may extend this schema with required fields.

```json
{
  "artifact_id": "CAE-MODAL-001",
  "artifact_type": "analysis",
  "domain": "E11",
  "title": "Base assembly modal analysis",
  "revision": "A",
  "status": "draft",
  "product_configuration_id": "CFG-PROTOTYPE-001",
  "source_artifacts": [
    {
      "artifact_id": "ASM-BASE-001",
      "revision": "B",
      "sha256": "..."
    }
  ],
  "related_requirements": ["REQ-MECH-001"],
  "related_parts": ["PART-HOUSING-001"],
  "related_interfaces": [],
  "related_risks": [],
  "related_tests": [],
  "toolchain": {
    "tool": "FreeCAD/CalculiX",
    "version": "record-exact-version"
  },
  "created_by": "human-or-agent-id",
  "reviewed_by": null,
  "approval_reference": null,
  "validation_status": "not_validated",
  "created_at": "YYYY-MM-DD",
  "notes": []
}
```

Do not use placeholder hashes or invented version values in real records. The example is a template.

## 3. Status semantics

- `draft`: work in progress; not an approved design input.
- `in_review`: submitted for review.
- `approved`: approved for the stated purpose/revision.
- `verified`: verification activity passed against defined criteria.
- `released`: authorized for a defined downstream use, build, or production stage.
- `blocked`: a prerequisite or decision prevents progress.
- `rejected`: reviewed and not accepted.
- `superseded`: replaced by a later controlled revision.
- `withdrawn`: intentionally removed from scope.

Do not conflate artifact approval with product verification. A test protocol may be approved while the test result does not yet exist.

## 4. Revision and configuration

- Use revision labels per artifact (A, B, C… or an explicitly documented scheme).
- A product configuration manifest records exact revisions of mechanical assemblies, PCB, cables, firmware binary/source commit, parameters, and relevant accessories.
- A prototype serial/asset ID points to one immutable configuration manifest.
- Test and CAE results must reference the configuration actually used, not the latest branch or current default.
- Never silently rewrite released results after a source change; issue a new result revision and supersede the prior one.

## 5. Requirements-to-evidence traceability

Each requirement record should include:
- ID, statement, rationale, source, owner, priority, status;
- measurable acceptance criteria and units where applicable;
- verification method (inspection, analysis, demonstration, test, or research);
- linked design artifacts and risks;
- test/evidence IDs and result state;
- open issues and approved deviations.

Recommended verification states: `not_planned`, `planned`, `in_progress`, `pass`, `fail`, `waived_with_approval`, `not_applicable_with_rationale`.

## 6. ECO minimum fields

- ECO ID, requester, date, reason, and change description;
- before/after configuration;
- affected artifact IDs;
- impact assessment for all 18 domains;
- required reviews and regression tests;
- safety/regulatory/research impact;
- approvals, implementation commit, and closure evidence.

Every domain must be marked `affected`, `reviewed_no_change`, `not_applicable`, or `unresolved`. An empty field is not an impact assessment.

## 7. Data integrity rules

1. Store native source files and generated derivatives separately.
2. Record file hashes for released/verified artifacts.
3. Record units explicitly; never infer DXF units from visual scale.
4. Preserve raw measurements unchanged; derived data references raw source and processing script/version.
5. Store numeric values with units and test conditions.
6. Keep credentials, private keys, personal data, and sensitive participant data out of the repository.
7. Large binaries may use Git LFS or controlled artifact storage; keep manifests and hashes in Git.
8. A JSON schema or validator should reject missing IDs, invalid status, duplicate IDs, unknown references, and missing units for dimensional values.

## 8. Suggested initial files

- `core/requirements/requirements_register.csv`
- `core/configuration/part_registry.csv`
- `core/configuration/master_bom.csv`
- `core/configuration/configuration_manifest.schema.json`
- `core/interfaces/interface_registry.csv`
- `core/changes/eco_register.csv`
- `core/traceability/verification_matrix.csv`

Do not populate these with guessed dimensions or inferred revision states. Initial rows should be imported from audited sources and carry provenance/status.
