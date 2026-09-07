from __future__ import annotations

import copy
import json
from html import escape
from typing import Any

from .core import build_matrix


def validate_sources(data: dict[str, Any]) -> None:
    characters = {item["id"] for item in data["characters"]}
    for item in data.get("knowledge", []):
        source = item.get("source")
        if source is None:
            continue
        if not isinstance(source, dict) or source.get("kind") not in {
            "witnessed",
            "told",
            "document",
            "inferred",
        }:
            raise ValueError("knowledge source requires kind witnessed/told/document/inferred")
        if not isinstance(source.get("evidence"), str) or not source["evidence"].strip():
            raise ValueError("knowledge source requires evidence text")
        if source["kind"] == "told" and (
            source.get("character") not in characters or source["character"] == item["character"]
        ):
            raise ValueError("told source requires a different known character")


def build_review(
    data: dict[str, Any],
    through: str | None = None,
    compare_from: str | None = None,
    alternate: Any = None,
) -> dict[str, Any]:
    validate_sources(data)
    ids = [item["id"] for item in data["scenes"]]
    report = build_matrix(data, through, compare_from)
    visible = ids[: ids.index(report["through"]) + 1]
    snapshots = []
    source_issues = []
    for scene in visible:
        snapshot = build_matrix(data, scene)
        snapshots.append({"scene": scene, "rows": snapshot["rows"], "issues": snapshot["issues"]})
    for item in data.get("knowledge", []):
        if item["scene"] not in visible:
            continue
        source = item.get("source", {})
        if source.get("kind") == "told":
            current = build_matrix(data, item["scene"])
            states = [
                cell["state"]
                for row in current["rows"]
                if row["id"] == item["revelation"]
                for cell in row["characters"]
                if cell["character"] == source["character"]
            ]
            if not states or states[0] not in {"confirmed", "corrected"}:
                source_issues.append(
                    {
                        "type": "unconfirmed-source",
                        "scene": item["scene"],
                        "character": item["character"],
                        "revelation": item["revelation"],
                        "reason": "Telling character has no confirmed record by this scene; review author intent",
                    }
                )
    report["source_issues"] = source_issues
    report["sources"] = [
        {
            "scene": item["scene"],
            "character": item["character"],
            "revelation": item["revelation"],
            "source": item["source"],
        }
        for item in data.get("knowledge", [])
        if item["scene"] in visible and "source" in item
    ]
    report["scene_grid"] = snapshots
    if alternate is not None:
        if (
            not isinstance(alternate, list)
            or any(not isinstance(item, str) for item in alternate)
            or len(alternate) != len(ids)
            or set(alternate) != set(ids)
        ):
            raise ValueError("alternate order must contain every scene ID exactly once")
        reordered = copy.deepcopy(data)
        lookup = {item["id"]: item for item in data["scenes"]}
        reordered["scenes"] = [lookup[item] for item in alternate]
        # Compare complete author-defined sequences; this is explicit full-story review.
        original = build_matrix(data)
        changed = build_matrix(reordered)

        def key(item: dict[str, Any]) -> str:
            return json.dumps(item, sort_keys=True)

        old, new = (
            {key(item): item for item in original["issues"]},
            {key(item): item for item in changed["issues"]},
        )
        report["alternate_comparison"] = {
            "scope": "full-story",
            "order": alternate,
            "added": [new[k] for k in sorted(new.keys() - old.keys())],
            "removed": [old[k] for k in sorted(old.keys() - new.keys())],
        }
    return report


def render_html(report: dict[str, Any]) -> str:
    headers = "".join(
        '<th scope="col">' + escape(scene["scene"]) + "</th>" for scene in report["scene_grid"]
    )
    rows = []
    evidence = []
    index = 0
    for character in report["characters"]:
        cells = []
        for scene in report["scene_grid"]:
            entries = []
            for revelation in scene["rows"]:
                cell = next(
                    item
                    for item in revelation["characters"]
                    if item["character"] == character["id"]
                )
                index += 1
                entries.append(
                    f'<a href="#evidence-{index}">{escape(revelation["summary"])}: {escape(cell["state"])}</a>'
                )
                evidence.append(
                    f'<li id="evidence-{index}"><strong>{escape(character.get("name", character["id"]))} / {escape(scene["scene"])} / {escape(revelation["summary"])}</strong><p>{escape(str(cell["evidence"] or "No evidence recorded"))}</p></li>'
                )
            cells.append("<td>" + "<br>".join(entries) + "</td>")
        rows.append(
            '<tr><th scope="row">'
            + escape(character.get("name", character["id"]))
            + "</th>"
            + "".join(cells)
            + "</tr>"
        )
    warnings = "".join(
        "<li>" + escape(item["scene"] + ": " + item["reason"]) + "</li>"
        for item in report["issues"] + report["source_issues"]
    )
    sources = "".join(
        "<li>"
        + escape(
            item["scene"]
            + " / "
            + item["character"]
            + ": "
            + item["source"]["kind"]
            + " - "
            + item["source"]["evidence"]
        )
        + "</li>"
        for item in report["sources"]
    )
    comparison = report.get("alternate_comparison")
    comparison_html = (
        "<h2>Alternate order: full-story comparison</h2><p>"
        + str(len(comparison["added"]))
        + " added continuity warnings; "
        + str(len(comparison["removed"]))
        + " removed.</p><ul>"
        + "".join(
            "<li>" + escape(label + ": " + item["scene"] + " / " + item["reason"]) + "</li>"
            for label in ("added", "removed")
            for item in comparison[label]
        )
        + "</ul>"
        if comparison
        else ""
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Knowledge scene review</title><style>body{font:17px system-ui;background:#111c2a;color:#f1f5f9;max-width:1200px;margin:auto;padding:22px;line-height:1.6}a{color:#94deff}input{font:inherit;padding:10px;max-width:90%}.scroll{overflow:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #547080;padding:14px;min-width:140px;text-align:left}li{margin:16px 0;overflow-wrap:anywhere}:target{outline:2px solid #ffd173}h1{font-size:2rem}@media(max-width:600px){body{padding:12px}}</style><h1>Character knowledge by scene</h1><p>Author-supplied knowledge and evidence. Warnings are review prompts, not inferred narrative errors. Same-scene records have no finer event timing.</p><label>Filter characters <input id="filter" type="search"></label><div class="scroll"><table><thead><tr><th>Character</th>'
        + headers
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div><h2>Continuity warnings</h2><ul>"
        + (warnings or "<li>No warnings in selected boundary</li>")
        + "</ul><h2>Knowledge sources</h2><ul>"
        + sources
        + "</ul>"
        + comparison_html
        + "<h2>Linked evidence</h2><ul>"
        + "".join(evidence)
        + '</ul><script>document.getElementById("filter").addEventListener("input",e=>{for(const row of document.querySelectorAll("tbody tr"))row.hidden=!row.querySelector("th").textContent.toLowerCase().includes(e.target.value.toLowerCase())})</script></html>'
    )
