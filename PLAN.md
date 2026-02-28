# nlp-mdaug Refactor Plan

## Objective
Rebuild the project around the I/O contract and architecture defined in `SPEC.md` and `README.md`,
assuming most existing implementation is replaced while keeping only reusable ideas.

## Success Criteria
- All CLI commands match the documented input/output contract.
- Input sources are only `stdin` and `--file`.
- Output destinations are only `stdout` and `--out`.
- Command behavior is deterministic, validated, and covered by tests.
- Provider integrations are behind stable interfaces (no SDK coupling in core logic).
- README/SPEC examples are executable and validated in tests.

## Guiding Rules
- `SPEC.md` and `README.md` are source of truth.
- Prefer replacement over incremental patching where old design conflicts.
- Keep modules small, single-purpose, and easy to test.
- Add tests before or with each major implementation step.

## Phase 0: Baseline and Safety Net
### Goals
- Prevent breakage during large refactor.
- Capture current behavior only where worth preserving.

### Tasks
1. Create a refactor branch and checkpoint current tests.
2. Add a temporary compatibility note in docs that API is being aligned to SPEC.
3. Classify existing modules:
   - keep (reusable utility logic),
   - adapt (logic with useful core ideas),
   - archive/remove (conflicting architecture).
4. Add a minimal smoke test suite for current CLI entrypoints (if not present).

### Exit Criteria
- Refactor branch is isolated.
- Baseline test command is documented and runnable.
- Keep/adapt/remove inventory is committed.

## Phase 1: Target Architecture Skeleton
### Goals
- Introduce the structure described by SPEC without full feature implementation.

### Tasks
1. Create/normalize package layout:
   - `src/mdaug/cli/`
   - `src/mdaug/common/`
   - `src/mdaug/core/{analysis,extraction,generation,relevance}/`
   - `src/mdaug/providers/`
   - `src/mdaug/service/`
   - `src/mdaug/schemas/`
2. Add module-level docs and placeholder interfaces.
3. Wire the CLI app to command stubs only (no heavy model logic yet).

### Exit Criteria
- CLI commands exist and run.
- Imports and package boundaries reflect target architecture.

## Phase 2: Canonical Schemas and I/O Normalization
### Goals
- Implement a single parsing/normalization layer for request/response shape handling.

### Tasks
1. Implement public input parser supporting:
   - list of strings,
   - dict of id -> string,
   - list of groups,
   - dict of groups.
2. Implement output formatter that mirrors top-level request shape.
3. Implement strict validation errors with consistent JSON error payloads.
4. Add schema tests for all valid and invalid cases.

### Exit Criteria
- Every command shares the same input parser and output formatter.
- Error format and exit behavior match docs.

## Phase 3: CLI Contract Completion
### Goals
- Make CLI behavior fully match the documented UX.

### Tasks
1. Enforce exactly one input source (`stdin` xor `--file`).
2. Enforce output destination behavior (`stdout` default, `--out` optional).
3. Route logs/details to `stderr`.
4. Add tests for:
   - stdin path,
   - file path,
   - out file path,
   - bad JSON,
   - missing required fields.

### Exit Criteria
- CLI examples in docs execute as written.
- Contract tests pass for all commands.

## Phase 4: Provider Interface Layer
### Goals
- Isolate model/tool backends behind explicit interfaces.

### Tasks
1. Define interfaces/protocols for:
   - generative,
   - embeddings/relevance,
   - sentiment/analysis,
   - keyword/entity extraction.
2. Add provider registry/factory with config-driven selection.
3. Implement a default local/mock provider set for deterministic tests.
4. Remove direct backend calls from `core/*`.

### Exit Criteria
- Core logic depends only on provider interfaces.
- Provider selection is config-based and testable.

## Phase 5: Operation Rebuild (Command by Command)
### Goals
- Implement each command against the normalized contract.

### Tasks
1. Rebuild in this order:
   - `analyze`
   - `extract`
   - `compare`
   - `rank`
   - `summarize`
   - `tag`
   - `title`
   - `outline`
2. For each command:
   - add unit tests first for shape and semantics,
   - implement core logic,
   - validate output ordering and key mapping,
   - add integration CLI test.

### Exit Criteria
- All commands pass unit + integration tests.
- Output shape per command matches docs exactly.

## Phase 6: Configuration and Runtime Cleanup
### Goals
- Make configuration predictable and aligned with docs.

### Tasks
1. Implement precedence: CLI option -> env -> `config.yaml` -> default.
2. Consolidate config loading/validation in `common/config.py`.
3. Remove legacy config paths and dead flags.
4. Add tests for precedence and invalid config handling.

### Exit Criteria
- Config behavior is deterministic and documented.

## Phase 7: Decommission Legacy Code
### Goals
- Remove conflicting or unused pre-refactor code.

### Tasks
1. Delete archived modules identified as remove-only.
2. Remove compatibility shims no longer needed.
3. Update imports and dependency graph checks.
4. Run dead-code and lint/type checks.

### Exit Criteria
- No unreachable legacy paths remain in runtime flow.
- Static checks pass.

## Phase 8: Documentation and Example Validation
### Goals
- Ensure docs are accurate and continuously verified.

### Tasks
1. Sync command tables and examples with implemented outputs.
2. Add executable doc tests (or golden-file tests) for README/SPEC examples.
3. Add sample JSON files in `examples/` matching each command.
4. Add troubleshooting section for common CLI errors.

### Exit Criteria
- Documentation examples are validated in CI.

## Phase 9: Release Hardening
### Goals
- Stabilize for production-like usage.

### Tasks
1. Add regression suite for all commands and I/O variants.
2. Add performance sanity checks for batch/group inputs.
3. Add semantic versioning and changelog entry for the refactor release.
4. Tag release candidate and run full QA pass.

### Exit Criteria
- CI green on lint, type check, unit, integration, docs examples.
- Release candidate approved.

## Suggested Work Breakdown (Execution Order)
1. Phase 0-1: architecture and guardrails.
2. Phase 2-3: contract and CLI behavior.
3. Phase 4-5: provider abstraction and command implementations.
4. Phase 6-7: config alignment and legacy removal.
5. Phase 8-9: docs verification and release hardening.

## Risks and Mitigations
- Risk: hidden coupling in legacy code.
  - Mitigation: enforce interface boundaries early (Phase 4).
- Risk: doc drift during implementation.
  - Mitigation: executable example tests (Phase 8).
- Risk: inconsistent outputs across commands.
  - Mitigation: single normalization/formatting layer (Phase 2).
- Risk: slow progress from over-preserving old code.
  - Mitigation: keep/adapt/remove inventory and delete aggressively.

## Definition of Done
- Project behavior matches `SPEC.md` and `README.md`.
- Tests cover core logic and CLI contract paths.
- Legacy conflicting code is removed.
- Docs and examples are accurate, validated, and release-ready.
