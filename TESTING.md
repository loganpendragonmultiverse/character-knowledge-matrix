# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.2.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Add an interactive character-by-scene evidence grid, explicit knowledge-source relationships and alternate scene-order comparisons.

## 1.3 event-order regressions

Cover learning/correction/revocation before and after use, cross-character telling evidence, partial/duplicate/invalid positions, legacy unordered scenes, source immutability, cutoff canaries and alternate scene order. Run the complete existing suite and build installed artifacts before release.

## 1.3.2 input and report reliability

Validate public report inputs and author display/evidence fields. Hide future revelations from early warning, source and evidence channels. Use source evidence when top-level evidence is absent, while preserving explicit top-level evidence. Include telling-source warnings and full-story alternate-order summaries in Markdown. Escape author text in Markdown, preserve fallback character IDs and create outputs exclusively, including dangling symlink refusal.

Run all documented checks plus the validation/report regressions. Install both the wheel and source distribution in fresh environments and exercise every documented output format; source files must remain unchanged. Linux acceptance supplements the required GitHub Windows/macOS/Linux CI matrix.

The wheel installs the README, development/testing contract, changelog and JSON examples under the installation data directory at `share/character-knowledge-matrix/`. The source distribution also includes these files in their original paths. Release acceptance compares both archives with the exact tagged files before testing fresh installations.
