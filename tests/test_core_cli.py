import json

import pytest

from character_knowledge_matrix.cli import main
from character_knowledge_matrix.core import build_matrix, load_project, render_markdown


def project():
    return {
        "version": 1,
        "scenes": [{"id": "s1", "title": "Arrival"}, {"id": "s2", "title": "Letter"}],
        "characters": [{"id": "mara", "name": "Mara"}, {"id": "ivo", "name": "Ivo"}],
        "revelations": [{"id": "gate", "summary": "The gate is false", "introduced_scene": "s1"}],
        "knowledge": [{"character": "mara", "revelation": "gate", "scene": "s1"}],
        "uses": [
            {
                "character": "ivo",
                "revelation": "gate",
                "scene": "s2",
                "note": "Mentions the false gate",
            }
        ],
    }


def test_matrix_and_issue():
    report = build_matrix(project())
    assert report["rows"][0]["characters"][0]["knows"]
    assert not report["rows"][0]["characters"][1]["knows"]
    assert report["issue_count"] == 2
    assert "premature-use" in render_markdown(report)
    early = build_matrix(project(), "s1")
    assert early["issue_count"] == 1


def test_validation(tmp_path):
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project()), encoding="utf-8")
    assert load_project(path)["characters"][0]["id"] == "mara"
    bad = project()
    bad["knowledge"][0]["character"] = "unknown"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown"):
        load_project(path)
    with pytest.raises(ValueError, match="unknown scene"):
        build_matrix(project(), "s9")


@pytest.mark.parametrize(
    "payload", [{"version": 2}, {"version": 1, "scenes": [], "characters": [], "revelations": []}]
)
def test_rejects_bad_shapes(tmp_path, payload):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises((TypeError, ValueError)):
        load_project(path)


def test_cli_json(tmp_path, capsys):
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project()), encoding="utf-8")
    assert main([str(path), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["issue_count"] == 2


def test_earliest_knowledge_and_future_revelation_visibility():
    data = project()
    data["knowledge"].insert(0, {"character": "mara", "revelation": "gate", "scene": "s2"})
    data["revelations"].append(
        {"id": "signal", "summary": "The signal is false", "introduced_scene": "s2"}
    )
    report = build_matrix(data, "s1")
    assert report["rows"][0]["characters"][0]["learned_scene"] == "s1"
    assert len(report["rows"]) == 1


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda data: data["scenes"].append(data["scenes"][0]), "duplicate scenes"),
        (lambda data: data["characters"][0].pop("id"), "string id"),
        (lambda data: data["revelations"][0].update(summary=4), "requires a summary"),
        (lambda data: data.update(uses="bad"), "uses must be a list"),
        (lambda data: data["uses"][0].update(scene="missing"), "uses record has an unknown"),
    ],
)
def test_more_validation(tmp_path, change, message):
    data = project()
    change(data)
    path = tmp_path / "project.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises((TypeError, ValueError), match=message):
        load_project(path)


def test_cli_safe_output(tmp_path):
    path = tmp_path / "project.json"
    path.write_text(json.dumps(project()), encoding="utf-8")
    output = tmp_path / "report.md"
    assert main([str(path), "--output", str(output)]) == 0
    assert main([str(path), "--output", str(output)]) == 2


def test_states_corrections_and_comparison():
    data = project()
    data["knowledge"] = [
        {"character": "mara", "revelation": "gate", "scene": "s1", "state": "false-belief"},
        {
            "character": "mara",
            "revelation": "gate",
            "scene": "s2",
            "state": "corrected",
            "evidence": "letter",
        },
    ]
    report = build_matrix(data, "s2", "s1")
    assert report["rows"][0]["characters"][0]["state"] == "corrected"
    assert report["changes"][0]["from"] == "false-belief"
    assert report["character_summaries"]["mara"][0]["state"] == "corrected"
