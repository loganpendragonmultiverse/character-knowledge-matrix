# Development

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build` before publishing.

Every release must update the package version, changelog, public GitHub release, and Logan Pendragon Forge catalog together. This project validates only author-supplied records; it does not infer character knowledge from prose.

## 1.2.0 improvement session

Add an interactive character-by-scene evidence grid, explicit knowledge-source relationships and alternate scene-order comparisons.

HTML filters character rows and links each scene/revelation state to escaped local evidence. Optional knowledge source objects require kind witnessed/told/document/inferred and evidence; told requires a different valid character. Unconfirmed telling-character states produce author-review warnings, and suspected/inferred states now correctly flag premature use. --alternate-order reads every scene ID exactly once and explicitly compares full-story continuity warnings; it is not a spoiler-limited comparison even when --through is supplied. Normal scene-grid output respects --through. Same-scene events have no finer timing, and records remain author assertions. Inputs are never edited.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
