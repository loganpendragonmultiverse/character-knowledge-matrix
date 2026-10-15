import copy
import json

import pytest
from test_review import sample

from character_knowledge_matrix.cli import main
from character_knowledge_matrix.core import build_matrix, load_project
from character_knowledge_matrix.review import build_review, render_html


def ordered():
    data = sample()
    data["uses"][0].update(scene="learn", event_order=2)
    data["knowledge"][0]["event_order"] = 1
    return data


def test_learning_before_after_use_changes_only_warning():
    data = ordered()
    original = copy.deepcopy(data)
    good = build_review(data)
    assert not good["issues"]
    data["knowledge"][0]["event_order"] = 3
    bad = build_review(data)
    assert bad["issues"][0]["type"] == "premature-use"
    assert bad["rows"] == good["rows"]
    assert original["knowledge"][0]["event_order"] == 1


@pytest.mark.parametrize(
    "state,warning",
    [("revoked", "premature-use"), ("false-belief", "contradictory-belief"), ("corrected", None)],
)
def test_correction_revocation_and_supplied_list_order(state, warning):
    data = ordered()
    data["knowledge"].insert(0, {**data["knowledge"][0], "state": state, "event_order": 3})
    data["uses"].append({**data["uses"][0], "event_order": 4})
    report = build_review(data)
    assert [i["type"] for i in report["issues"]] == ([warning] if warning else [])
    assert report["rows"][0]["characters"][0]["state"] == state


@pytest.mark.parametrize("order", [None, True, 0, -1, 1.5, "2", 1])
def test_partial_invalid_duplicate_orders_reject(order, tmp_path):
    data = ordered()
    data["uses"][0]["event_order"] = order
    with pytest.raises(ValueError):
        build_matrix(data)
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_project(path)
    data["uses"][0].pop("event_order")
    with pytest.raises(ValueError, match="every"):
        build_review(data)


def test_legacy_unordered_same_scene_and_sparse_orders():
    data = ordered()
    for label in ("knowledge", "uses"):
        for record in data[label]:
            record.pop("event_order")
    assert not build_review(data)["issues"]
    data = ordered()
    data["knowledge"][0]["event_order"] = 10
    data["uses"][0]["event_order"] = 20
    assert not build_review(data)["issues"]


def test_source_character_checked_at_telling_event():
    data = ordered()
    data["uses"] = []
    data["knowledge"][0]["event_order"] = 3
    data["knowledge"].append(
        {
            "character": "b",
            "revelation": "r",
            "scene": "learn",
            "event_order": 2,
            "evidence": "told",
            "source": {"kind": "told", "character": "a", "evidence": "spoken"},
        }
    )
    assert build_review(data)["source_issues"][0]["type"] == "unconfirmed-source"
    data["knowledge"][0]["event_order"] = 1
    assert not build_review(data)["source_issues"]


def test_cutoffs_alternate_orders_and_cli(tmp_path, capsys):
    data = ordered()
    data["knowledge"].append(
        {
            "character": "a",
            "revelation": "r",
            "scene": "act",
            "state": "revoked",
            "evidence": "FUTURE-CANARY",
        }
    )
    original = copy.deepcopy(data)
    early = build_review(data, "learn")
    assert "FUTURE-CANARY" not in json.dumps(early)
    assert "FUTURE-CANARY" not in render_html(early)
    assert (
        build_review(data, "learn", alternate=["act", "learn"])["alternate_comparison"]["scope"]
        == "full-story"
    )
    assert data == original
    with pytest.raises(ValueError, match="must not follow"):
        build_matrix(data, "learn", "act")
    path = tmp_path / "project.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    source_bytes = path.read_bytes()
    assert main([str(path), "--through", "learn", "--format", "json"]) == 0
    assert "FUTURE-CANARY" not in capsys.readouterr().out
    assert path.read_bytes() == source_bytes
