"""Tests for canvas_local_mcp.server against a mocked Canvas API."""
import json

import httpx
import pytest

from canvas_local_mcp import server

RealClient = httpx.Client


def make_client_factory(handler):
    """Return a replacement for httpx.Client that routes through a MockTransport."""
    transport = httpx.MockTransport(handler)

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return RealClient(*args, **kwargs)

    return factory


@pytest.fixture(autouse=True)
def canvas_env(monkeypatch):
    monkeypatch.setattr(server, "BASE", "https://canvas.test")
    monkeypatch.setattr(server, "HEAD", {"Authorization": "Bearer x"})


def test_load_env_reads_file(monkeypatch, tmp_path):
    env = tmp_path / ".canvas.env"
    env.write_text(
        "# comment\n"
        "CANVAS_BASE_URL=https://canvas.test/\n"
        "CANVAS_TOKEN=tok=with=equals\n"
    )
    monkeypatch.setattr(server, "ENV_FILE", env)
    monkeypatch.delenv("CANVAS_BASE_URL", raising=False)
    monkeypatch.delenv("CANVAS_TOKEN", raising=False)
    server._load_env()
    assert server.BASE == "https://canvas.test"
    assert server.HEAD == {"Authorization": "Bearer tok=with=equals"}


def test_load_env_missing_vars_exits(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "ENV_FILE", tmp_path / "missing.env")
    monkeypatch.delenv("CANVAS_BASE_URL", raising=False)
    monkeypatch.delenv("CANVAS_TOKEN", raising=False)
    with pytest.raises(SystemExit, match="CANVAS_BASE_URL"):
        server._load_env()


def test_get_follows_link_pagination(monkeypatch):
    def handler(request):
        if request.url.params.get("page") == "2":
            return httpx.Response(200, json=[{"id": 2}])
        return httpx.Response(
            200,
            json=[{"id": 1}],
            headers={"Link": '<https://canvas.test/api/v1/courses?page=2>; rel="next"'},
        )

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    assert server._get("/api/v1/courses") == [{"id": 1}, {"id": 2}]


def test_get_returns_single_object(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"id": 7, "name": "syllabus.pdf"})

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    assert server._get("/api/v1/courses/1/files/7")["id"] == 7


def test_get_raises_on_http_error(monkeypatch):
    def handler(request):
        return httpx.Response(401, json={"errors": "unauthorized"})

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    with pytest.raises(httpx.HTTPStatusError):
        server._get("/api/v1/courses")


def test_list_courses_shapes_output(monkeypatch):
    def handler(request):
        assert request.url.params["enrollment_state"] == "active"
        return httpx.Response(
            200,
            json=[{"id": 1, "name": "Proyecto de Software", "course_code": "PS-101", "extra": "x"}],
        )

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    assert server.list_courses() == [
        {"id": 1, "name": "Proyecto de Software", "course_code": "PS-101"}
    ]


def test_list_assignments_with_submissions(monkeypatch):
    def handler(request):
        assert request.url.params["include[]"] == "submission"
        return httpx.Response(
            200,
            json=[
                {
                    "id": 10,
                    "name": "Práctica 1",
                    "due_at": "2026-06-01T22:00:00Z",
                    "points_possible": 10,
                    "html_url": "https://canvas.test/a/10",
                    "submission_types": ["online_upload"],
                    "submission": {"score": 9.5, "submitted_at": "2026-05-30", "workflow_state": "graded"},
                }
            ],
        )

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    out = server.list_assignments(1, include_submissions=True)
    assert out[0]["submission"]["score"] == 9.5
    assert out[0]["name"] == "Práctica 1"


def test_get_grades_all_enrollments(monkeypatch):
    def handler(request):
        assert request.url.path == "/api/v1/users/self/enrollments"
        return httpx.Response(
            200,
            json=[{"course_id": 1, "grades": {"current_score": 88.0}, "type": "StudentEnrollment"}],
        )

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    assert server.get_grades()[0]["grade"]["current_score"] == 88.0


def test_get_grades_single_course(monkeypatch):
    def handler(request):
        assert request.url.path == "/api/v1/courses/42/enrollments"
        return httpx.Response(200, json=[{"course_id": 42, "grades": {}, "type": "StudentEnrollment"}])

    monkeypatch.setattr(server.httpx, "Client", make_client_factory(handler))
    assert server.get_grades(42)[0]["course_id"] == 42


def test_tools_are_registered():
    import anyio

    tools = anyio.run(server.mcp.list_tools)
    names = {t.name for t in tools}
    assert names == {
        "list_courses",
        "list_assignments",
        "upcoming_events",
        "planner_items",
        "list_announcements",
        "list_modules",
        "get_file_info",
        "get_grades",
        "get_page",
        "todo",
    }
    assert all(t.description for t in tools)


def test_env_example_matches_required_vars():
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / ".canvas.env.example"
    keys = {line.split("=")[0] for line in example.read_text().splitlines() if "=" in line}
    assert keys == {"CANVAS_BASE_URL", "CANVAS_TOKEN"}


def test_server_json_version_matches_package():
    from pathlib import Path

    import canvas_local_mcp

    server_json = json.loads((Path(__file__).resolve().parents[1] / "server.json").read_text())
    assert server_json["version"] == canvas_local_mcp.__version__
    assert server_json["packages"][0]["version"] == canvas_local_mcp.__version__
