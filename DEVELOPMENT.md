# Development

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build` before publishing.

Every release must update the package version, changelog, public GitHub release, and Logan Pendragon Forge catalog together. This project validates only author-supplied records; it does not infer character knowledge from prose.

## 1.2.0 improvement session

Add an interactive character-by-scene evidence grid, explicit knowledge-source relationships and alternate scene-order comparisons.

HTML filters character rows and links each scene/revelation state to escaped local evidence. Optional knowledge source objects require kind witnessed/told/document/inferred and evidence; told requires a different valid character. Unconfirmed telling-character states produce author-review warnings, and suspected/inferred states now correctly flag premature use. --alternate-order reads every scene ID exactly once and explicitly compares full-story continuity warnings; it is not a spoiler-limited comparison even when --through is supplied. Normal scene-grid output respects --through. Unordered same-scene events have no finer timing, and records remain author assertions. Inputs are never edited.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## Intra-scene event order (1.3)

Optionally add `event_order` to knowledge and use records. Once any record in a
scene has this field, every knowledge/use record in that scene must have a unique
positive integer order, shared across characters and revelations. Gaps are allowed;
booleans, partial ordering and duplicate positions reject. Scenes may independently
remain unordered. Input list order does not override explicit positions.

Uses see knowledge events strictly before their position. Learning or correction
before a use can confirm knowledge; later learning cannot. Revocation before a use
can restore a premature-use warning. Telling-character evidence is checked before
the recipient's ordered learning event. End-of-scene cells and scene comparisons
show the final recorded state. Unordered scenes preserve the legacy end-of-scene
semantics, including same-scene learning. Scene boundaries still hide later events;
`--alternate-order` explicitly compares full-story warnings and retains each scene's
internal order. Records remain author assertions, with no prose or timing inference.

## 1.3.1 input and report reliability

Validate public report inputs and author display/evidence fields. Hide future revelations from early warning, source and evidence channels. Include telling-source warnings and full-story alternate-order summaries in Markdown. Escape author text in Markdown, preserve fallback character IDs and create outputs exclusively, including dangling symlink refusal.

Run all documented checks plus the validation/report regressions. Install both the wheel and source distribution in fresh environments and exercise every documented output format; source files must remain unchanged. Linux acceptance supplements the required GitHub Windows/macOS/Linux CI matrix.
