# Did This Character Know That? Matrix

[![CI](https://github.com/loganpendragonmultiverse/character-knowledge-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/character-knowledge-matrix/actions/workflows/ci.yml)

Did This Character Know That? Matrix maps revelations against characters and ordered scenes. It shows when knowledge was recorded and flags supplied scene uses that occur before the character's recorded learning point.

## Three-minute start

```bash
python -m pip install .
knowledge-matrix examples/novel.json
knowledge-matrix examples/novel.json --through arrival --format json
```

Inputs explicitly define scenes, characters, revelations, knowledge events, and optional uses. A scene boundary hides later revelations, learning events, and uses. Output is deterministic Markdown or JSON and existing files are refused.

The tool validates author-maintained notes; it does not extract facts from prose or prove that a continuity issue exists. Missing knowledge records can create false positives, while ambiguous dialogue may not imply knowledge. Requires Python 3.10 or newer.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).
