# Refactor Inventory (Phase 0)

## Keep
- `src/mdaug/common/config.py`
  - Keep as a seed for centralized config loading, but simplify and align to the new precedence model.
- `src/mdaug/core/relevance/relevance.py`
  - Keep as a source of relevance/scoring ideas, not as-is implementation.
- `src/mdaug/core/providers/*` (algorithmic concepts only)
  - Keep high-level ideas around provider abstraction and scoring utilities.

## Adapt
- `src/mdaug/core/analysis/*`
  - Adapt into command-focused analysis units behind provider interfaces.
- `src/mdaug/core/extraction/extract.py`
  - Adapt into extraction/tag command logic that returns documented output shapes.
- `src/mdaug/core/generation/*`
  - Adapt into summarize/title/outline command logic with strict I/O contracts.
- `src/mdaug/common/sample.py`
  - Adapt as optional test/demo fixture data only.

## Archive or Remove
- Any imports referencing `app.*` or `src.models.*`
  - Remove during migration; these are legacy paths from prior structure.
- Legacy test suite under `tests/unit/core/*`
  - Archive and replace with contract-driven tests aligned to `SPEC.md`.
- Provider README content tied to old structure assumptions
  - Replace with new provider interface documentation after Phase 4.

## Notes
- `SPEC.md` and root `README.md` are now considered source-of-truth for behavior.
- The new architecture skeleton is created in Phase 1 and old code can be retired incrementally.
