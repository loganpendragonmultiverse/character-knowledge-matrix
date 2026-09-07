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

HTML filters character rows and links each scene/revelation state to escaped local evidence. Optional knowledge source objects require kind witnessed/told/document/inferred and evidence; told requires a different valid character. Unconfirmed telling-character states produce author-review warnings, and suspected/inferred states now correctly flag premature use. --alternate-order reads every scene ID exactly once and explicitly compares full-story continuity warnings; it is not a spoiler-limited comparison even when --through is supplied. Normal scene-grid output respects --through. Same-scene events have no finer timing, and records remain author assertions. Inputs are never edited.
