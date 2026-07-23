# Security policy

## Security scope (alpha)

`canvas-mcp` is currently **alpha** software intended for local, single-user workflows.
Security hardening is ongoing and may evolve as the project matures.

Current scope:

- Local MCP server process on your machine.
- Canvas API access using your own personal access token.
- Configuration loaded from `~/.canvas.env`.

Out of scope:

- Managed hosting, multi-tenant deployments, or enterprise controls.
- Guarantees beyond best-effort support for an alpha project.

## Token handling and local configuration

- Store your Canvas token in `~/.canvas.env` (see `.canvas.env.example`).
- **Never commit `~/.canvas.env` or tokens to git.**
- Use a dedicated token for this workflow where possible.

Recommended local file permissions:

```bash
chmod 600 ~/.canvas.env
```

## Least-privilege recommendations

- Use the minimum Canvas permissions/scopes needed for your use case.
- Avoid reusing high-privilege tokens from other tools.
- Prefer short-lived or easy-to-rotate credentials when available in your Canvas environment.

## Rotation and revocation

If you suspect token exposure:

1. Revoke the token in Canvas (**Account → Settings → Approved Integrations**).
2. Create a new token with minimal required permissions.
3. Update `~/.canvas.env` with the new token.
4. Review shell history, logs, and local files for accidental token disclosure.

## Reporting a vulnerability

Please include:

- A clear description of the issue and potential impact.
- Reproduction steps.
- Affected versions/commit SHA.
- Any relevant environment details (OS, Python version, MCP client).

Please **do not** include:

- Tokens, credentials, API keys, or session secrets.
- Personal data (student records, grades, emails, identifiers).

Reporting channel:

- Use the existing project contact listed in the repository (`admin@agente404.com`), or
- Use GitHub Security Advisories **if** private vulnerability reporting is enabled for this repository.
