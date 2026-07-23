# Canvas LMS MCP Server (`canvas-mcp`)

<!-- mcp-name: io.github.admin978/canvas-mcp -->

[![CI](https://github.com/admin978/canvas-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/admin978/canvas-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/canvas-local-mcp)](https://pypi.org/project/canvas-local-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/canvas-local-mcp)](https://pypi.org/project/canvas-local-mcp/)
[![License](https://img.shields.io/github/license/admin978/canvas-mcp)](https://github.com/admin978/canvas-mcp/blob/main/LICENSE)

Ask Claude about your Canvas courses, assignments, deadlines, modules and grades from one place.

`canvas-mcp` is a local-first MCP server for Canvas LMS users (students, instructors, and MCP builders). It turns Canvas REST API actions into MCP tools that work from Claude Code, Claude Desktop, and other MCP-compatible clients.

> **Status:** alpha. Single-user, no warranty, API surface may still shift. File issues if it breaks.

## Who this is for

- **Students** who want one view across multiple courses
- **Educators** who want faster access to assignments, modules and announcements
- **MCP users** who want Canvas data in local Claude workflows

## What you can ask Claude

- “What assignments are due this week across all my active courses?”
- “Show upcoming events and planner items for the next 7 days.”
- “List my current grades by course.”
- “Get the modules (with items) for course `12345`.”
- “Show announcements for course `12345`.”
- “Fetch the page `syllabus` from course `12345`.”

## Quick start

Prerequisite: **Python 3.10+**.

### 1) Create a Canvas personal access token

In Canvas: **Account > Settings > Approved Integrations > + New Access Token**.
Copy the token shown (Canvas does not show it again later).

### 2) Install

From PyPI (recommended):

```bash
pip install canvas-local-mcp
```

Or from source:

```bash
git clone https://github.com/admin978/canvas-mcp.git && cd canvas-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 3) Configure `~/.canvas.env`

```bash
curl -fsSL https://raw.githubusercontent.com/admin978/canvas-mcp/main/.canvas.env.example -o ~/.canvas.env
chmod 600 ~/.canvas.env
# edit ~/.canvas.env: set CANVAS_BASE_URL (institution root, no /api/v1)
# and paste the token into CANVAS_TOKEN
```

### 4) Register in your MCP client

Claude Code:

```bash
claude mcp add canvas-local -- canvas-local-mcp
```

Claude Desktop:

- macOS example path: `~/Library/Application Support/Claude/claude_desktop_config.json`
- On Windows/Linux, use your platform-specific Claude Desktop config path

```json
{
  "mcpServers": {
    "canvas-local": {
      "command": "canvas-local-mcp"
    }
  }
}
```

## Tools exposed

- `list_courses`
- `list_assignments`
- `list_modules`
- `list_announcements`
- `get_page`
- `get_file_info`
- `get_grades`
- `planner_items`
- `upcoming_events`
- `todo`

## Bulk dump

`canvas-local-mcp-dump` downloads course files and related content for offline indexing.

```bash
canvas-local-mcp-dump              # all active courses
canvas-local-mcp-dump 12345 67890  # specific course IDs
```

Output goes to `./canvas-dump/` by default. Override with `CANVAS_DUMP_DIR=/path/to/dir`.

## Local-first, privacy and token flow

- The server runs locally and uses **stdio** transport with your MCP client.
- Configuration is read from `~/.canvas.env` (`CANVAS_BASE_URL`, `CANVAS_TOKEN`).
- Requests go from your local server to the official Canvas API endpoints.
- No external token broker is used in the request path.

## Development

Requires **Python 3.10+**.

```bash
pip install -e ".[dev]"
ruff check canvas_local_mcp tests   # lint
pytest                              # tests run against a mocked Canvas API — no token needed
```

CI runs lint + tests on Python 3.10–3.13 for every push and pull request.

## Contributing, roadmap and support

- Issues / feature requests: <https://github.com/admin978/canvas-mcp/issues>
- Pull requests are welcome for bug fixes and Canvas workflow improvements
- Roadmap direction currently lives in open issues and upcoming PRs

If this project helps you manage Canvas with Claude, consider giving it a ⭐ so other students and educators can find it.

## License

MIT — see `LICENSE`.

---

Built by [AGENTE 404 S.L.](https://www.agente404.com) · admin@agente404.com
