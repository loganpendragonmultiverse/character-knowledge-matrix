import copy
import json

import pytest
from test_review import sample

from character_knowledge_matrix.cli import main
from character_knowledge_matrix.core import build_matrix, render_markdown
from character_knowledge_matrix.review import build_review, render_html


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(version=True),
        lambda d: d["characters"][0].update(name=[]),
        lambda d: d["scenes"][0].update(id=" "),
        lambda d: d["knowledge"][0].update(character=[]),
        lambda d: d["knowledge"][0].update(state=[]),
        lambda d: d["knowledge"][0].update(evidence=4),
        lambda d: d["knowledge"][0].update(source={"kind": []}),
    ],
)
def test_malformed_fields_reject_without_traceback(tmp_path, capsys, mutate):
    data = sample()
    mutate(data)
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data))
    assert main([str(source)]) == 2
    assert "Traceback" not in capsys.readouterr().err
    with pytest.raises((ValueError, TypeError)):
        build_review(data)


def test_future_revelation_hidden_from_all_evidence_channels():
    data = sample()
    data["revelations"][0].update(id="FUTURE-SECRET", introduced_scene="act")
    for label in ("knowledge", "uses"):
        for item in data[label]:
            item.update(revelation="FUTURE-SECRET", scene="learn")
    data["knowledge"][0]["state"] = "confirmed"
    data["knowledge"][0]["evidence"] = "FUTURE-EVIDENCE"
    data["knowledge"][0]["source"]["evidence"] = "FUTURE-SOURCE"
    data["uses"][0]["character"] = "b"
    original = copy.deepcopy(data)
    report = build_review(data, "learn")
    for rendered in (json.dumps(report), render_markdown(report), render_html(report)):
        assert "FUTURE-" not in rendered
    assert build_review(data, "act")["rows"][0]["id"] == "FUTURE-SECRET"
    assert data == original


def test_markdown_escapes_author_text_and_missing_name_falls_back():
    data = sample()
    data["characters"][0]["name"] = "<img src=x>|*Mara*"
    data["characters"][1].pop("name")
    data["revelations"][0]["summary"] = "A|B\n<script>"
    rendered = render_markdown(build_matrix(data))
    assert "<img" not in rendered and "<script>" not in rendered
    assert r"A\|B" in rendered
    assert " | b |" in rendered


def test_exclusive_output_refuses_dangling_symlink(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(sample()))
    output, target = tmp_path / "output.md", tmp_path / "missing.md"
    output.symlink_to(target)
    assert main([str(source), "--output", str(output)]) == 2
    assert not target.exists()


def test_explicit_null_source_matches_absent_source(tmp_path, capsys):
    data = sample()
    data["knowledge"][0]["source"] = None
    assert build_review(data)["sources"] == []
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data))
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["sources"] == []


def test_markdown_includes_source_and_alternate_review():
    data = sample()
    data["knowledge"].append(
        {
            "character": "b",
            "revelation": "r",
            "scene": "learn",
            "evidence": "told",
            "source": {"kind": "told", "character": "a", "evidence": "spoken"},
        }
    )
    data["knowledge"][0]["state"] = "suspected"
    report = build_review(data, alternate=["act", "learn"])
    rendered = render_markdown(report)
    assert "Knowledge source review" in rendered
    assert "unconfirmed-source" in rendered
    assert "Alternate order: full-story comparison" in rendered
    assert "added continuity warnings" in rendered
