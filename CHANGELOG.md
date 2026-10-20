# Changelog

## 1.3.2 - 2026-10-20

- Bundle operating documentation and JSON examples in wheels as well as source distributions.

- Validate public report inputs and author display/evidence fields. Hide future revelations from early warning, source and evidence channels. Use source evidence when top-level evidence is absent, while preserving explicit top-level evidence. Include telling-source warnings and full-story alternate-order summaries in Markdown. Escape author text in Markdown, preserve fallback character IDs and create outputs exclusively, including dangling symlink refusal.

## 1.3.0 - 2026-10-15

- Explain unordered and explicitly ordered scene timing accurately in HTML reports.

- Support validated explicit intra-scene order across knowledge events and uses.
- Evaluate use and telling-character warnings at the supplied event position.
- Preserve unordered scene semantics and cutoff behavior; reject reversed scene comparisons and make change ordering deterministic.

## 1.2.0 - 2026-09-07

- Add an interactive character-by-scene evidence grid, explicit knowledge-source relationships and alternate scene-order comparisons.
- Added regression coverage for the audited behavior and invalid inputs.

## 1.1.0 - 2026-07-27

- Added confirmed, inferred, suspected, false-belief, corrected, and revoked knowledge states.
- Added evidence tracking, per-character summaries, and between-scene comparisons.
- Added typed premature-use, contradictory-belief, and missing-evidence warnings.

## 1.0.0 - 2026-07-26

- Added versioned scenes, characters, revelations, learning events, and uses.
- Added scene-bounded knowledge matrices.
- Added evidence-backed review flags for uses before recorded knowledge.

## Unpublished verification candidate: v1.3.1

The immutable v1.3.1 tag was a verification candidate, with no public GitHub release. Its wheel did not bundle the separate operating guides and examples. v1.3.2 supersedes that candidate and includes the reviewed runtime repairs together with complete installed guidance.
