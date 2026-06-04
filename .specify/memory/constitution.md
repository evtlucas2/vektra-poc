<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0
Principles added (new, replacing all placeholders):
  - I. Data Decoupling
  - II. ETL Discipline
  - III. Test-First Development (NON-NEGOTIABLE)
  - IV. Clean Code
  - V. Simplicity First (YAGNI)
Sections added:
  - Project Structure Constraints (replaces SECTION_2_NAME/CONTENT)
  - Development Workflow (replaces SECTION_3_NAME/CONTENT)
Sections removed: none
Templates reviewed:
  - .specify/templates/plan-template.md ✅ aligned (Constitution Check gate is per-feature; template structure unchanged)
  - .specify/templates/spec-template.md ✅ aligned (no mandatory section changes required)
  - .specify/templates/tasks-template.md ✅ aligned (TDD ordering already enforced: "Tests MUST be written and FAIL before implementation")
Deferred TODOs: none — all placeholders resolved.
-->

# Vektra POC Constitution

## Core Principles

### I. Data Decoupling

The data directory MUST reside outside the project source tree. Project code MUST NOT
hardcode absolute paths to data files or directories. All data root locations MUST be
resolved at runtime via the `DATA_ROOT` environment variable or a dedicated config file.
The project MUST include a `.env.example` documenting required path variables.

Rationale: Keeps the repository clean and portable; prevents accidental data commits;
enables the same codebase to run against different datasets without code changes.

### II. ETL Discipline

Extract, Transform, and Load phases MUST be implemented as separate, independently
callable and testable units. Transform functions MUST be pure — no I/O side effects
inside transform logic. Pipelines MUST compose these phases explicitly (no implicit
chaining). Each phase MUST accept typed inputs and return typed outputs; shared global
state between stages is forbidden.

Rationale: Isolation makes each phase testable in isolation, debuggable independently,
and replaceable without breaking the rest of the pipeline.

### III. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all features. The sequence is enforced:

1. Write the test — it MUST fail (Red).
2. Write the minimum implementation to make it pass (Green).
3. Refactor for clean code compliance, keeping tests green (Refactor).

This cycle applies to ETL pipelines, data analysis modules, and time-series components.
No implementation code is accepted without a corresponding failing test written first.

Rationale: Prevents regressions, forces clear interface design before implementation,
and ensures every code path has a known expected behavior.

### IV. Clean Code

- Functions MUST do exactly one thing.
- Names MUST be self-documenting; unexplained abbreviations are forbidden (exception:
  universally accepted domain shorthand such as `df` for DataFrame, `ts` for time-series).
- Functions MUST NOT exceed 25 lines; extract helpers when this limit is reached.
- Magic numbers and magic strings MUST be named constants.
- Dead code and commented-out code are forbidden; delete rather than comment.
- Comments explain WHY, never WHAT. If the code needs a "what" comment, rename it.

Rationale: Data science code frequently grows into unstructured notebooks and scripts;
these rules prevent that drift and keep the codebase maintainable as it grows.

### V. Simplicity First (YAGNI)

Start with the simplest structure that satisfies the current requirement. Abstractions
MUST NOT be introduced before the same pattern appears in three or more distinct places.
Premature optimisation is forbidden before profiling confirms a bottleneck. Flat module
structures are preferred over deep package hierarchies. If a piece of code can be deleted
and all tests still pass, it MUST be deleted.

Rationale: Data science projects accumulate complexity quickly. Deferring abstraction
keeps the codebase readable and prevents over-engineering features that may not survive
the next iteration.

## Project Structure Constraints

```
<project_root>/
├── src/
│   ├── etl/          # Extract, transform, load modules
│   ├── analysis/     # Data analysis modules
│   └── timeseries/   # Time-series analysis modules
├── tests/
│   ├── unit/         # Pure unit tests (no I/O)
│   └── integration/  # Tests that touch files or external systems
└── config/           # Configuration and .env.example

<data_root>/          # OUTSIDE the project root; resolved via DATA_ROOT env var
├── raw/              # Immutable source data — never modified by pipeline code
├── processed/        # Output of ETL transforms
└── output/           # Final analysis artefacts
```

The `<data_root>` directory MUST never be inside `<project_root>`. CI pipelines MUST
set `DATA_ROOT` to a fixture data directory under `tests/fixtures/` for test runs.

## Development Workflow

1. Write a failing test that captures the acceptance criteria (Principle III).
2. Implement the minimum code to make the test pass.
3. Refactor for clean code compliance (Principle IV).
4. If the feature touches data I/O, verify `DATA_ROOT` is resolved externally (Principle I).
5. Run the full test suite (`pytest` or equivalent) before opening a pull request.

All pull requests MUST pass CI (lint + full test suite) before merge. No exceptions.

## Governance

This constitution supersedes all prior conventions for this project. Amendments require:

1. A written rationale explaining the change and any migration impact.
2. A version bump per semantic versioning:
   - **MAJOR**: Removal or backward-incompatible redefinition of a principle.
   - **MINOR**: New principle or section added, or materially expanded guidance.
   - **PATCH**: Clarifications, wording, or typo fixes with no semantic change.
3. Updates to all dependent templates and docs within the same commit as the amendment.

Compliance reviews MUST occur at each pull request by verifying the Constitution Check
gate in the feature's `plan.md` before merging.

**Version**: 1.0.0 | **Ratified**: 2026-06-04 | **Last Amended**: 2026-06-04
