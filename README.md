# canvas-mcp

Local-first MCP server for Canvas LMS. Stdio transport, no network round-trips beyond the official Canvas API.

## Why

Canvas is built for instructors. As a student you get a fragmented UI, no cross-course search, and notifications that arrive late or never. This server exposes the Canvas REST API as MCP tools so you can drive the LMS from any MCP-compatible client (Claude Code, Claude Desktop, etc.).

## Architecture

```
[client] ──stdio──> [server.py] ──https──> [Canvas API]
```

- Token lives in `~/.canvas.env` (`chmod 600`)
- Server runs locally, no third party in the path
- ~125 lines of Python, fully auditable

## Tools exposed

`list_courses`, `list_assignments`, `list_modules`, `list_announcements`, `get_page`, `get_file_info`, `get_grades`, `planner_items`, `upcoming_events`, `todo`.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .canvas.env.example ~/.canvas.env
chmod 600 ~/.canvas.env
# edit ~/.canvas.env with your Canvas URL + personal access token
```

Register with your MCP client (Claude Code example):
```bash
claude mcp add canvas-local -- python3 /path/to/server.py
```

## Bulk dump

`dump.py` downloads every file the user has access to (course materials, syllabi). Useful for offline indexing.

## License

MIT — see `LICENSE`.

---

Built by [AGENTE 404 S.L.](https://www.agente404.com) · admin@agente404.com
