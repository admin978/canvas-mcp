"""Tests for canvas_local_mcp.dump helpers."""
import io
import json

import pytest

from canvas_local_mcp import dump


def test_slug_replaces_unsafe_chars():
    assert dump.slug("Práctica 1: diseño/implementación") == "Práctica 1_ diseño_implementación"


def test_slug_handles_empty_and_none():
    assert dump.slug("") == "untitled"
    assert dump.slug(None) == "untitled"
    assert dump.slug("///") == "untitled"


def test_slug_truncates():
    assert len(dump.slug("a" * 500)) == 120


class FakeResponse(io.BytesIO):
    """Minimal stand-in for urllib's response: bytes + headers + context manager."""

    def __init__(self, payload, headers=None):
        super().__init__(json.dumps(payload).encode())
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_paged_follows_link_header(monkeypatch):
    calls = []

    def fake_req(url):
        calls.append(url)
        if "page=2" in url:
            return FakeResponse([{"id": 2}])
        return FakeResponse(
            [{"id": 1}],
            headers={"Link": '<https://canvas.test/api/v1/courses?page=2>; rel="next"'},
        )

    monkeypatch.setattr(dump, "req", fake_req)
    items = list(dump.paged("https://canvas.test/api/v1/courses"))
    assert items == [{"id": 1}, {"id": 2}]
    assert "per_page=100" in calls[0]


def test_paged_adds_per_page_to_existing_query(monkeypatch):
    calls = []

    def fake_req(url):
        calls.append(url)
        return FakeResponse([])

    monkeypatch.setattr(dump, "req", fake_req)
    list(dump.paged("https://canvas.test/api/v1/x?include[]=items"))
    assert calls[0].endswith("include[]=items&per_page=100")


def test_paged_yields_single_object(monkeypatch):
    monkeypatch.setattr(dump, "req", lambda url: FakeResponse({"id": 9}))
    assert list(dump.paged("https://canvas.test/api/v1/one")) == [{"id": 9}]


def test_download_skips_existing_file(tmp_path):
    dest = tmp_path / "syllabus.pdf"
    dest.write_bytes(b"already here")
    assert dump.download("https://canvas.test/f", dest) == "skip"
    assert dest.read_bytes() == b"already here"


def test_download_writes_file(monkeypatch, tmp_path):
    class RawResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(dump, "req", lambda url: RawResponse(b"pdf-bytes"))
    dest = tmp_path / "sub" / "file.pdf"
    assert dump.download("https://canvas.test/f", dest) == "ok"
    assert dest.read_bytes() == b"pdf-bytes"


def test_load_env_missing_vars_exits(monkeypatch, tmp_path):
    monkeypatch.setattr(dump, "ENV_FILE", tmp_path / "missing.env")
    monkeypatch.delenv("CANVAS_BASE_URL", raising=False)
    monkeypatch.delenv("CANVAS_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        dump._load_env()
