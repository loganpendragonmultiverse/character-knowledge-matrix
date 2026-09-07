import copy
import json
from pathlib import Path

import pytest

from character_knowledge_matrix.cli import main
from character_knowledge_matrix.review import build_review, render_html


def sample():
    return {
        "version": 1,
        "scenes": [{"id": "learn"}, {"id": "act"}],
        "characters": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
        "revelations": [{"id": "r", "introduced_scene": "learn", "summary": "A secret"}],
        "knowledge": [
            {
                "character": "a",
                "revelation": "r",
                "scene": "learn",
                "evidence": "Witnessed the event",
                "source": {"kind": "witnessed", "evidence": "Scene note"},
            }
        ],
        "uses": [{"character": "a", "revelation": "r", "scene": "act"}],
    }


def test_grid_evidence_alternate_and_immutable(tmp_path: Path):
    data = sample()
    before = copy.deepcopy(data)
    report = build_review(data, alternate=["act", "learn"])
    assert len(report["alternate_comparison"]["added"]) == 1
    assert report["alternate_comparison"]["removed"] == []
    assert len(report["scene_grid"]) == 2
    html = render_html(report)
    assert "Witnessed the event" in html and "#evidence-1" in html
    assert "1 added continuity warnings" in html
    assert data == before
    source, order, output = (
        tmp_path / name for name in ("source.json", "order.json", "review.html")
    )
    source.write_text(json.dumps(data))
    order.write_text(json.dumps(["act", "learn"]))
    assert (
        main(
            [
                str(source),
                "--alternate-order",
                str(order),
                "--format",
                "html",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert source.read_text() == json.dumps(data)
    assert main([str(source), "--output", str(output)]) == 2


def test_told_relationships_and_boundaries():
    data = sample()
    data["knowledge"].append(
        {
            "character": "b",
            "revelation": "r",
            "scene": "act",
            "source": {"kind": "told", "character": "a", "evidence": "LATER-CANARY"},
            "evidence": "</script><img src=x>",
        }
    )
    assert not build_review(data)["source_issues"]
    early = build_review(data, "learn")
    assert "LATER-CANARY" not in json.dumps(early)
    assert len(early["scene_grid"]) == 1
    html = render_html(build_review(data))
    assert "</script><img" not in html
    data["knowledge"][0]["state"] = "suspected"
    report = build_review(data)
    assert report["source_issues"][0]["type"] == "unconfirmed-source"
    assert report["issues"][0]["type"] == "premature-use"
    assert "unconfirmed" not in render_html(report) or report["source_issues"]


@pytest.mark.parametrize(
    "source",
    [
        [],
        {"kind": "magic"},
        {"kind": "inferred"},
        {"kind": "told", "evidence": "x", "character": "a"},
        {"kind": "told", "evidence": "x", "character": "missing"},
    ],
)
def test_invalid_source(source):
    data = sample()
    data["knowledge"][0]["source"] = source
    with pytest.raises(ValueError):
        build_review(data)


@pytest.mark.parametrize("order", [{}, ["learn", "learn"], ["learn"], [None, "act"]])
def test_invalid_alternate(order):
    with pytest.raises(ValueError):
        build_review(sample(), alternate=order)
