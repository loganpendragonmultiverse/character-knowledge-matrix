from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATES = {"confirmed", "inferred", "suspected", "false-belief", "corrected", "revoked"}


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


def validate_event_order(data: dict[str, Any]) -> None:
    by_scene: dict[str, list[dict[str, Any]]] = {}
    for label in ("knowledge", "uses"):
        for record in data.get(label, []):
            by_scene.setdefault(record["scene"], []).append(record)
    for records in by_scene.values():
        if not any("event_order" in record for record in records):
            continue
        orders = []
        for record in records:
            order = record.get("event_order")
            if type(order) is not int or order < 1:
                raise ValueError(
                    "ordered scenes require a positive integer event_order on every knowledge/use record"
                )
            orders.append(order)
        if len(orders) != len(set(orders)):
            raise ValueError("event_order must be unique across knowledge and uses in a scene")


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
            if label == "knowledge" and record.get("state", "confirmed") not in STATES:
                raise ValueError("knowledge record has an unsupported state")
    validate_event_order(data)
    return data


def build_matrix(
    data: dict[str, Any],
    through: str | None = None,
    compare_from: str | None = None,
    *,
    before_order: int | None = None,
) -> dict[str, Any]:
    validate_event_order(data)
    scene_ids = [item["id"] for item in data["scenes"]]
    if through is not None and through not in scene_ids:
        raise ValueError(f"unknown scene: {through}")
    if compare_from is not None and compare_from not in scene_ids:
        raise ValueError(f"unknown scene: {compare_from}")
    boundary = scene_ids.index(through) if through else len(scene_ids) - 1
    if compare_from is not None and scene_ids.index(compare_from) > boundary:
        raise ValueError("comparison start must not follow through scene")
    visible = set(scene_ids[: boundary + 1])
    history: dict[tuple[str, str], list[dict[str, Any]]] = {}
    issues = []
    for record in data.get("knowledge", []):
        if record["scene"] not in visible:
            continue
        if (
            before_order is not None
            and scene_ids.index(record["scene"]) == boundary
            and record.get("event_order", 0) >= before_order
        ):
            continue
        entry = {
            **record,
            "state": record.get("state", "confirmed"),
            "evidence": record.get("evidence"),
        }
        if entry["state"] in {"confirmed", "corrected"} and not entry.get("evidence"):
            issues.append(
                {
                    **entry,
                    "type": "missing-evidence",
                    "reason": "confirmed knowledge has no evidence",
                }
            )
        history.setdefault((entry["character"], entry["revelation"]), []).append(entry)
    for values in history.values():
        values.sort(key=lambda x: (scene_ids.index(x["scene"]), x.get("event_order", 0)))

    def state_at(
        key: tuple[str, str], index: int, order: int | None = None
    ) -> dict[str, Any] | None:
        values = [
            x
            for x in history.get(key, [])
            if scene_ids.index(x["scene"]) < index
            or (
                scene_ids.index(x["scene"]) == index
                and (order is None or x.get("event_order", 0) < order)
            )
        ]
        return values[-1] if values else None

    rows = []
    summaries: dict[str, list[dict[str, Any]]] = {
        character["id"]: [] for character in data["characters"]
    }
    for revelation in data["revelations"]:
        if revelation["introduced_scene"] not in visible:
            continue
        cells = []
        for character in data["characters"]:
            current = state_at((character["id"], revelation["id"]), boundary)
            state = current["state"] if current else "unrecorded"
            cell = {
                "character": character["id"],
                "state": state,
                "knows": state in {"confirmed", "corrected"},
                "learned_scene": current["scene"] if current else None,
                "evidence": current.get("evidence") if current else None,
            }
            cells.append(cell)
            if state != "unrecorded":
                summaries[character["id"]].append({"revelation": revelation["id"], "state": state})
        rows.append(
            {
                "id": revelation["id"],
                "summary": revelation["summary"],
                "introduced_scene": revelation["introduced_scene"],
                "characters": cells,
            }
        )
    for usage in data.get("uses", []):
        if usage["scene"] not in visible:
            continue
        current = state_at(
            (usage["character"], usage["revelation"]),
            scene_ids.index(usage["scene"]),
            usage.get("event_order"),
        )
        if current is None or current["state"] not in {"confirmed", "corrected"}:
            issue_type = (
                "contradictory-belief"
                if current and current["state"] == "false-belief"
                else "premature-use"
            )
            issues.append(
                {
                    **usage,
                    "type": issue_type,
                    "reason": "character uses revelation before confirmed knowledge",
                }
            )
    changes = []
    if compare_from is not None:
        start = scene_ids.index(compare_from)
        for key in sorted(
            {
                (c["id"], r["id"])
                for c in data["characters"]
                for r in data["revelations"]
                if r["introduced_scene"] in visible
            }
        ):
            before, after = state_at(key, start), state_at(key, boundary)
            old, new = (
                before["state"] if before else "unrecorded",
                after["state"] if after else "unrecorded",
            )
            if old != new:
                changes.append({"character": key[0], "revelation": key[1], "from": old, "to": new})
    return {
        "version": 2,
        "through": scene_ids[boundary],
        "compare_from": compare_from,
        "characters": data["characters"],
        "rows": rows,
        "character_summaries": summaries,
        "changes": changes,
        "issue_count": len(issues),
        "issues": issues,
    }


def render_markdown(report: dict[str, Any]) -> str:
    headers = [character["name"] for character in report["characters"]]
    lines = [
        "# Character Knowledge Matrix",
        "",
        f"Through **{report['through']}** - Continuity issues: **{report['issue_count']}**",
        "",
        "| Revelation | " + " | ".join(headers) + " |",
        "|---|" + "---|" * len(headers),
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['summary']} | "
            + " | ".join(item["state"] for item in row["characters"])
            + " |"
        )
    if report["changes"]:
        lines.extend(["", "## Scene Comparison", ""])
        lines.extend(
            f"- `{x['character']}` / `{x['revelation']}`: {x['from']} -> {x['to']}"
            for x in report["changes"]
        )
    if report["issues"]:
        lines.extend(["", "## Review", ""])
        lines.extend(
            f"- **{item['type']}** in `{item['scene']}`: {item['reason']}"
            for item in report["issues"]
        )
    return "\n".join(lines).rstrip() + "\n"
