```
 ____  _   _ __  __ ____    _      _   _    _    ____  _   _ _____ ____ ____
| __ )| | | |  \/  | __ )  / \    | | | |  / \  |  _ \| \ | | ____/ ___/ ___|
|  _ \| | | | |\/| |  _ \ / _ \   | |_| | / _ \ | |_) |  \| |  _| \___ \___ \
| |_) | |_| | |  | | |_) / ___ \  |  _  |/ ___ \|  _ <| |\  | |___ ___) |__) |
|____/ \___/|_|  |_|____/_/   \_\ |_| |_/_/   \_\_| \_\_| \_|_____|____/____/
```

<br>

# Bumba CC Harness

Bumba CC Harness is a local, single-operator agent harness that connects a
Discord control surface, durable SQLite memory, scheduled automation services,
and Claude Code CLI execution. This variant is the Claude Code baseline: the
main bridge path invokes Claude Code with `claude -p` and expects the operator
to authenticate the Claude Code CLI locally.

The repository is prepared for public adoption. It does not include private
deployment history, local machine paths, personal job-search data, resumes,
portfolio links, API keys, OAuth tokens, browser profiles, or runtime databases.
The job-search workflow ships as a configurable scaffold and fails closed until
an adopter supplies their own profile, criteria, secrets, and approval database.

## What It Does

- Runs a Discord bot that accepts operator messages and routes them through the
  bridge.
- Persists conversation state, service state, events, and operational memory in
  SQLite.
- Supports scheduled services for briefings, calendar/email workflows, job
  search, knowledge review, health checks, and maintenance.
- Provides a Zone 4 department system where chiefs route work to typed
  specialists with explicit tool boundaries.
- Vendors two MCP servers, `bumba-memory` and `bumba-sandbox`, so deployments do
  not depend on local absolute paths.
- Uses Claude Code CLI as the primary execution backend.

## Repository Layout

```text
.
├── agent/                  Python bridge, services, teams, configs, tests
├── mcp-servers/            Vendored MCP servers used by the harness
├── docs/                   Public adoption and architecture notes
├── .github/                Public CI and issue/PR templates
├── Makefile                Common local developer commands
└── README.md
```

The canonical Python package root is `agent/`. Source, tests, runtime config,
and Python scripts should stay under that directory.

## Requirements

- Python 3.13
- `uv`
- Git
- Claude Code CLI authenticated for the runtime operator
- Optional for MCP server development: Node.js 20.x or 22.x
- Optional for live operation: Discord bot credentials and any service
  credentials you enable

## Quickstart

The smoke path does not require secrets or networked model calls.

```bash
git clone https://github.com/your-org/bumba-cc-harness.git
cd bumba-cc-harness
make setup
make test
```

For a narrower first check:

```bash
cd agent
uv sync --extra dev
.venv/bin/python -m pytest tests/test_app.py::TestAppInitialize -q
```

## Claude Code Setup

Secrets are loaded from the flat `.secrets` file described in
`agent/data/.secrets-template`. For a Claude Code-backed run, provide:

```text
discord_token=
operator_discord_id=
claude_oauth_token=
claude_oauth_refresh_token=
claude_oauth_expires_at=0
```

The bridge resolves the Claude binary from `BUMBA_CLAUDE_BIN` or `PATH`.
The default backend policy keeps routing on Claude Code. If you enable the
backend registry explicitly, keep the policy on `claude` unless you have added
and tested another backend implementation:

```toml
[backends]
enabled = true
main = "claude"
chiefs_default = "claude"
specialists_default = "claude"
```

See [docs/configuration.md](docs/configuration.md).

## Running Locally

Development checks:

```bash
make test
make lint
make validate-services
make secrets-scan
```

Live bridge operation is intentionally not one-command. Before enabling it,
create a local secrets file, review `agent/config/bridge.toml`, confirm Claude
Code CLI authentication, and disable any services you do not intend to operate.
The public defaults keep voice off and leave job-search automation incomplete
until you add adopter-owned data.

## Job Search Scaffold

The job-search package is included because it is part of the harness shape, but
it has been scrubbed of personal materials. To use it, create local copies of:

- `agent/job_search/candidate.json.example`
- `agent/job_search/criteria.json.example`

Then provide your own resume URL, profile links, board credentials, and Notion
database ID. Without `BUMBA_NOTION_JOB_DB_ID` or `notion_job_db_id` in
`.secrets`, the approval pipeline refuses to run. See
[docs/job-search.md](docs/job-search.md).

## Security Posture

This public tree is intended to be safe to inspect and fork. It still operates
automation surfaces that can touch external systems when configured, so adopters
must keep runtime state out of Git:

- Do not commit `.secrets`, `.mcp.json`, browser profiles, SQLite databases,
  logs, OAuth caches, or generated worktrees.
- Run `make secrets-scan` before publishing changes.
- Treat every service credential as adopter-owned and rotate it if it is ever
  printed or committed.

Security reporting details are in [SECURITY.md](SECURITY.md).

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Development](docs/development.md)
- [Job search](docs/job-search.md)
- [Publication cleanup notes](docs/publication-cleanup.md)

## License

MIT. See [LICENSE](LICENSE).
