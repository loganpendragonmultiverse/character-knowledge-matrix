from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _id_map(items: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list) or not items:
        raise TypeError(f"{label} must be a non-empty list")
    result = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise TypeError(f"each {label} item requires a string id")
        if item["id"] in result:
            raise ValueError(f"duplicate {label} id: {item['id']}")
        result[item["id"]] = item
    return result


def load_project(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("project must be a version 1 object")
    scenes = _id_map(data.get("scenes"), "scenes")
    characters = _id_map(data.get("characters"), "characters")
    revelations = _id_map(data.get("revelations"), "revelations")
    for revelation in revelations.values():
        if revelation.get("introduced_scene") not in scenes or not isinstance(
            revelation.get("summary"), str
        ):
            raise ValueError(
                f"revelation {revelation['id']} requires a summary and valid introduced_scene"
            )
    for label in ("knowledge", "uses"):
        records = data.get(label, [])
        if not isinstance(records, list):
            raise TypeError(f"{label} must be a list")
        for record in records:
            if (
                not isinstance(record, dict)
                or record.get("character") not in characters
                or record.get("revelation") not in revelations
                or record.get("scene") not in scenes
            ):
                raise ValueError(f"{label} record has an unknown character, revelation, or scene")
    return data


def build_matrix(data: dict[str, Any], through: str | None = None) -> dict[str, Any]:
    scene_ids = [item["id"] for item in data["scenes"]]
    if through is not None and through not in scene_ids:
        raise ValueError(f"unknown scene: {through}")
    boundary = scene_ids.index(through) if through else len(scene_ids) - 1
    visible = set(scene_ids[: boundary + 1])
    learned: dict[tuple[str, str], str] = {}
    for record in data.get("knowledge", []):
        key = (record["character"], record["revelation"])
        if record["scene"] in visible and (
            key not in learned or scene_ids.index(record["scene"]) < scene_ids.index(learned[key])
        ):
            learned[key] = record["scene"]
    rows = []
    for revelation in data["revelations"]:
        if revelation["introduced_scene"] not in visible:
            continue
        cells = []
        for character in data["characters"]:
            learned_scene = learned.get((character["id"], revelation["id"]))
            cells.append(
                {
                    "character": character["id"],
                    "knows": learned_scene is not None,
                    "learned_scene": learned_scene,
                }
            )
        rows.append(
            {
                "id": revelation["id"],
                "summary": revelation["summary"],
                "introduced_scene": revelation["introduced_scene"],
                "characters": cells,
            }
        )
    issues = []
    for usage in data.get("uses", []):
        if usage["scene"] not in visible:
            continue
        learned_scene = learned.get((usage["character"], usage["revelation"]))
        if learned_scene is None or scene_ids.index(learned_scene) > scene_ids.index(
            usage["scene"]
        ):
            issues.append(
                {**usage, "reason": "character uses revelation before recorded knowledge"}
            )
    return {
        "version": 1,
        "through": scene_ids[boundary],
        "characters": data["characters"],
        "rows": rows,
        "issue_count": len(issues),
        "issues": issues,
    }


def render_markdown(report: dict[str, Any]) -> str:
    headers = [character["name"] for character in report["characters"]]
    lines = [
        "# Character Knowledge Matrix",
        "",
        f"Through **{report['through']}** · Continuity issues: **{report['issue_count']}**",
        "",
        "| Revelation | " + " | ".join(headers) + " |",
        "|---|" + "---|" * len(headers),
    ]
    for row in report["rows"]:
        cells = [
            f"Yes ({item['learned_scene']})" if item["knows"] else "No record"
            for item in row["characters"]
        ]
        lines.append(f"| {row['summary']} | " + " | ".join(cells) + " |")
    if report["issues"]:
        lines.extend(["", "## Review", ""])
        lines.extend(
            f"- `{item['scene']}`: `{item['character']}` uses `{item['revelation']}` before recorded knowledge."
            for item in report["issues"]
        )
    return "\n".join(lines).rstrip() + "\n"
