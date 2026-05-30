# Agent Instructions — subaru-telemetry-client

## Ecosystem context

This repository is the **Python client library** for the Subaru Telemetry System (STS). It is used
as a dependency by sensor polling scripts in the companion repositories:

- [`subaru-telemetry-server`](https://github.com/Subaru-InstDiv/subaru-telemetry-server) — STSboard
  daemon, radio server, alarm subsystem, and all sensor polling scripts
- [`subaru-telemetry-web`](https://github.com/Subaru-InstDiv/subaru-telemetry-web) — Flask web
  frontend for telemetry dashboards

This library encodes the **STS binary wire protocol**. Any change to `Radio.pack` or `Radio.unpack`
affects every sensor script in the ecosystem and must be treated with extreme care.

---

## Commands

```bash
uv sync                                                     # install / refresh the environment
uv run pytest                                               # run all tests (may attempt network I/O)
uv run pytest -k 'not transmit_method and not receive_method'  # unit tests only (no network)
uv run ruff format .                                        # format code
uv run ruff check . --fix                                   # lint and auto-fix
```

Coverage must stay at or above **80 %**. The CI gate will fail below this threshold.

---

## Git workflow

**Never commit directly to `main`.** All changes must go through a feature branch and pull request.

```sh
git checkout main && git pull          # start from a fresh main
git checkout -b <type>/<description>   # create a feature branch
# ... make changes ...
git push -u origin <branch-name>
gh pr create --base main
```

Branch names follow `<type>/<short-description>` in lowercase kebab-case:

| Type | When to use |
|---|---|
| `feat/` | new public API, new datum format support |
| `fix/` | bug fix |
| `chore/` | dependency updates, config changes |
| `docs/` | README or documentation only |
| `refactor/` | internal restructuring with no behaviour change |
| `test/` | adding or improving tests |

Examples: `feat/add-datum-batch-helper`, `fix/radio-recv-timeout`, `chore/bump-ruff`

### Commit message format

```
feat: add FloatArray datum format
fix: handle partial recv in _recvn
chore: upgrade ruff to 0.9.0
```

Keep the subject line under 72 characters. Add a blank line and body if the change is non-obvious.

---

## Architecture

### `Datum` — `src/subaru/sts/client/datum.py`

A lightweight, immutable-by-convention value container. Instances are created via factory class
methods:

| Factory method | Format constant | Python value type |
|---|---|---|
| `Datum.Integer(id, timestamp, value)` | `INTEGER` | `int` |
| `Datum.Float(id, timestamp, value)` | `FLOAT` | `int \| float` |
| `Datum.Text(id, timestamp, value)` | `TEXT` | `str` |
| `Datum.IntegerWithText(id, timestamp, value)` | `INTEGER_WITH_TEXT` | `tuple[int, str]` |
| `Datum.FloatWithText(id, timestamp, value)` | `FLOAT_WITH_TEXT` | `tuple[float, str]` |
| `Datum.Exponent(id, timestamp, value)` | `EXPONENT` | `int \| float` |

`EXPONENT` is identical to `FLOAT` on the wire; the distinction is presentational (the STS web
frontend may render it in scientific notation).

The constructor validates that the value type matches the declared format and raises `ValueError`
on mismatch.

### `Radio` — `src/subaru/sts/client/radio.py`

The TCP client. Connects to the STS board (default `host="sts"`, `port=9001`), speaks the binary
protocol, and exposes two public methods:

- `radio.transmit(data)` — sends a list of `Datum` objects
- `radio.receive(ids)` — fetches the latest `Datum` for each ID in `ids`

Pass `dry_run=True` to the constructor (or to `transmit()`) to exercise packing without touching
the network — useful for sensor script development and unit tests.

### Binary protocol

Each packet is a `bytearray` with the structure:

```
Header  (10 bytes):  !BIBI  →  size | 0x80, datum_id, format, timestamp
Payload (variable):  format-specific (integer = 4 B, float/exponent = 8 B, text = up to 117 B)
```

Maximum packet size is 127 bytes. Text payloads are silently truncated to fit.

---

## Code conventions

- **Python ≥ 3.12** everywhere.
- **Absolute imports** starting from `subaru` (e.g. `from subaru.sts.client import Datum, Radio`).
- **Numpy-style docstrings** on all public classes, methods, and functions.
- **Ruff** for formatting and linting — configuration lives in `pyproject.toml`. Line length 100.
- Do not add logging frameworks. This is a library; callers control their own logging.
- Do not introduce runtime dependencies. The library intentionally has no `dependencies` in
  `pyproject.toml` beyond the Python standard library.

---

## Testing

Tests live in `tests/`. Two categories:

- **Unit tests** — test packing/unpacking, factory methods, and validation logic with no network.
  These can always run offline.
- **Integration tests** — `test_radio.py` methods tagged `transmit_method` and `receive_method`
  open a real TCP connection to the STS board. Skip these when working offline:
  ```bash
  uv run pytest -k 'not transmit_method and not receive_method'
  ```

When adding a new datum format or changing pack/unpack logic, add a round-trip test that packs a
`Datum` and immediately unpacks the result, verifying the values are identical.

Test files in `tests/` may omit module-level and function-level docstrings (`D100`, `D103` are
ignored there by ruff).

---

## Adding a new datum format

If the STS board protocol is extended to support a new format:

1. Add the new constant to `DatumFormat` in `datum.py`.
2. Add a factory class method on `Datum`.
3. Add value validation in `Datum._validate_value`.
4. Add `pack` and `unpack` branches in `Radio.pack` / `Radio.unpack`.
5. Add unit tests covering the factory method, validation, pack, and unpack.
6. Update `README.md` with the new factory method and value type.

---

## What NOT to do

- Do not commit directly to `main`.
- Do not add third-party runtime dependencies.
- Do not change `Radio.pack` or `Radio.unpack` without adding or updating round-trip tests.
- Do not lower the 80 % coverage threshold.
- Do not hard-code machine-specific paths (e.g., absolute paths to `uv`) in source code or tests.
- Do not use relative imports — all imports must start from `subaru`.

---

# Jira Integration via MCP

## Project Configuration
- **Jira Site:** subaru-naoj.atlassian.net
- **Project Key:** STS
- **Project ID:** 10099
- **Default Issue Type:** Task (ID: 10007)

## Creating Jira Issues

When creating issues in the STS project, use the MCP `jira_create_issue` tool with these fields:

### Required Fields
| Field       | Key         | Value                  |
|-------------|-------------|------------------------|
| Project     | `project`   | `{"key": "STS"}`       |
| Issue Type  | `issuetype` | `{"id": "10007"}`      |
| Summary     | `summary`   | Brief description      |

### Optional Fields
| Field       | Key           | Format / Notes                        |
|-------------|---------------|---------------------------------------|
| Description | `description` | Atlassian Document Format (ADF)       |
| Priority    | `priority`    | See priority table below              |
| Assignee    | `assignee`    | `{"accountId": "<id>"}`               |
| Labels      | `labels`      | Array of strings, e.g. `["sensor"]`   |
| Due date    | `duedate`     | `YYYY-MM-DD`                          |
| Parent      | `parent`      | `{"key": "STS-XX"}` for sub-tasks     |

### Priority Values
| Name                          | ID      |
|-------------------------------|---------|
| Safety Emergency              | `10033` |
| Critical to Night Observation | `10034` |
| Blocker                       | `10066` |
| Normal priority               | `10000` |
| Medium (default)              | `3`     |
| Low                           | `4`     |

### Components
Available components: `Intranet`, `Jira`, `Public website`

## Guidelines
- Always use project key `STS` and issue type Task unless specifically asked otherwise.
- Include the Jira issue key (e.g. `STS-42`) in branch names and commit messages
  so the GitHub-Jira integration links them automatically.
  Example branch: `STS-42-fix-sensor-calibration`
- Use Sub-task (ID `10008`) only when breaking down an existing Task.
- Do NOT use JSM request types (IDs 10067, 10068, 10069) — those are for the
  customer portal only.

## Development Workflow

Follow this workflow for all non-trivial changes (bug fixes, features, refactors):

### 1. Before Starting Work
- **Find or create a Jira ticket.** Search STS for an existing ticket that covers your
  task. If none exists, create one (Task type, project STS) with a clear summary and
  description of the work.
- Assign the ticket to yourself if unassigned.
- Transition the ticket to **In Progress**.

### 2. Creating a Branch
- Name the branch using the ticket key:
  `STS-<number>-short-description` (e.g. `STS-42-fix-sensor-calibration`)
- This links the branch to the Jira ticket automatically via the GitHub integration.

### 3. While Working
- Reference the ticket key in every commit message:
  `STS-42 fix: correct calibration offset calculation`
- Keep the ticket updated with any blockers or scope changes via comments.

### 4. Opening a Pull Request
- Include the ticket key in the PR title: `STS-42 fix: sensor calibration`
- Opening a PR does **not** automatically mean the work is ready for review — further
  commits are expected.
- Only transition the ticket to **Under Review** when explicitly asked to request a
  review (e.g. "request a review", "mark for review", "this is ready for review").
  If no review was requested, the ticket should remain **In Progress** until merge.

### 5. After Merge
- The ticket will transition to **Done** automatically if the GitHub-Jira integration
  is configured. If not, close it manually.
- Delete the feature branch after merge.

### When NOT to Create a Ticket
- Trivial single-line typo/doc fixes committed directly to main are fine without a ticket.
- When in doubt, create one — it's cheap and keeps the board accurate.

## Agent Attribution

Whenever you create or edit a Jira issue, comment, or any Atlassian content, append a
footer identifying the tool and model that performed the action:

```
---
*Edited by [tool-name] ([model-name]) on behalf of @[github-username]*
```

Example:
```
---
*Edited by GitHub Copilot CLI (claude-sonnet-4.6) on behalf of @wtgee*
```

## MCP Server Setup

Atlassian hosts the MCP server remotely — no local installation, Docker, or container needed.
The default and recommended approach is to connect directly to the Atlassian-hosted server.

### 1. Create an API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token", give it a label (e.g. "MCP Agent"), and copy the token.

Note: API tokens inherit your full account permissions. For least-privilege access,
use OAuth 2.0 with scopes: `read:jira-work`, `write:jira-work`, `read:jira-user`.

### 2. Create Your Basic Auth Credential

```bash
echo -n "your-email@example.com:your-api-token" | base64
```

### 3. Configure Your MCP Client

**GitHub Copilot CLI** — add to `~/.copilot/mcp-config.json`:
```json
{
  "mcpServers": {
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v1/mcp",
      "headers": {
        "Authorization": "Basic <your-base64-credential>"
      }
    }
  }
}
```

**VS Code / GitHub Copilot Chat** — add to `.vscode/mcp.json` or user MCP settings:
```json
{
  "mcpServers": {
    "atlassian": {
      "type": "local",
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "https://mcp.atlassian.com/v1/mcp",
        "--header",
        "Authorization: Basic <your-base64-credential>"
      ]
    }
  }
}
```
