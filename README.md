# Did This Character Know That? Matrix

[![CI](https://github.com/loganpendragonmultiverse/character-knowledge-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/character-knowledge-matrix/actions/workflows/ci.yml)

Did This Character Know That? Matrix maps revelations against characters and ordered scenes. It shows when knowledge was recorded and flags supplied scene uses that occur before the character's recorded learning point.

## Three-minute start

```bash
python -m pip install .
knowledge-matrix examples/novel.json
knowledge-matrix examples/novel.json --through arrival --format json
knowledge-matrix examples/novel.json --compare-from arrival --through letter
```

Inputs explicitly define scenes, characters, revelations, knowledge events, and optional uses. A scene boundary hides later revelations, learning events, and uses. Output is deterministic Markdown or JSON and existing files are refused.

Version 1.1 accepts a `state` on every knowledge event: `confirmed`, `inferred`, `suspected`, `false-belief`, `corrected`, or `revoked`. Add `evidence` to identify the source scene or note. `--compare-from` reports state changes between two scenes, and the output includes per-character summaries plus typed review warnings.

The tool validates author-maintained notes; it does not extract facts from prose or prove that a continuity issue exists. Missing knowledge records can create false positives, while ambiguous dialogue may not imply knowledge. Requires Python 3.10 or newer.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.2.0: reviewed improvements

Add an interactive character-by-scene evidence grid, explicit knowledge-source relationships and alternate scene-order comparisons.

```bash
knowledge-matrix project.json --format html --output review.html
```

HTML filters character rows and links each scene/revelation state to escaped local evidence. Optional knowledge source objects require kind witnessed/told/document/inferred and evidence; told requires a different valid character. Unconfirmed telling-character states produce author-review warnings, and suspected/inferred states now correctly flag premature use. --alternate-order reads every scene ID exactly once and explicitly compares full-story continuity warnings; it is not a spoiler-limited comparison even when --through is supplied. Normal scene-grid output respects --through. Unordered same-scene events have no finer timing, and records remain author assertions. Inputs are never edited.

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

Validate public report inputs and author display/evidence fields. Hide future revelations from early warning, source and evidence channels. Use source evidence when top-level evidence is absent, while preserving explicit top-level evidence. Include telling-source warnings and full-story alternate-order summaries in Markdown. Escape author text in Markdown, preserve fallback character IDs and create outputs exclusively, including dangling symlink refusal.

Run all documented checks plus the validation/report regressions. Install both the wheel and source distribution in fresh environments and exercise every documented output format; source files must remain unchanged. Linux acceptance supplements the required GitHub Windows/macOS/Linux CI matrix.
