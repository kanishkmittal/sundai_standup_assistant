# Standup Assistant - SundAI Hackathon Project Plan

**Built at Sundai** | May 2026

## Overview

A web app that generates daily standup updates by pulling context from Microsoft Teams group chats, GitHub commits, and Jira tickets. Uses the Claude API to synthesize a standup draft covering:

- What I did yesterday
- What I'm working on today
- What I'm blocked on

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              React Frontend (Anusha)                  │
│              anusha/frontend/                         │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Routes (Anusha)                  │
│              anusha/app.py                            │
│                      │                               │
│                      ▼                               │
│         Orchestrator + Prompt (Deepika)               │
│         deepika/orchestrator.py + prompt.py           │
│                      │                               │
│       ┌──────────────┼──────────────┐                │
│       ▼              ▼              ▼                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │
│  │  Teams   │  │  GitHub  │  │    Jira      │       │
│  │(Kanishk) │  │(Kanishk) │  │  (Deepika)   │       │
│  └──────────┘  └──────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────┘
```

## Directory Structure (Disjoint Workstreams)

Each person owns their own top-level folder. No file overlap. No merge conflicts.

```
sundai_standup_assistant/
├── shared/                          ← agreed upfront, then frozen
│   ├── __init__.py                  ← ConnectorRecord dataclass
│   └── types.ts                     ← TypeScript request/response types
│
├── kanishk/                         ← Kanishk's folder (Teams + GitHub)
│   ├── __init__.py
│   ├── teams.py
│   ├── github_connector.py
│   ├── requirements.txt
│   └── PLAN_KANISHK.md
│
├── deepika/                         ← Deepika's folder (Jira + orchestrator + prompt)
│   ├── __init__.py
│   ├── jira_connector.py
│   ├── orchestrator.py
│   ├── prompt.py
│   ├── requirements.txt
│   └── PLAN_DEEPIKA.md
│
├── anusha/                          ← Anusha's folder (frontend + API routes)
│   ├── __init__.py
│   ├── app.py
│   ├── requirements.txt
│   ├── PLAN_ANUSHA.md
│   └── frontend/
│       └── src/
│           ├── App.tsx
│           ├── api.ts
│           └── components/
│
├── .env.example
├── .gitignore
├── PROJECT_PLAN.md
└── LICENSE
```

## Team Assignments

### Kanishk — Backend / APIs
**Branch:** `feature/teams-github-connectors` | **Folder:** `kanishk/` | **Plan:** `kanishk/PLAN_KANISHK.md`

Owns the Teams and GitHub connectors. These are the two integrations most likely to hit auth/permission snags, so they go to the strongest API person.

**Teams Connector (`teams.py`)**
- Authenticate via Microsoft Graph API (OAuth2 delegated or application flow)
- Fetch messages from a specified group chat from yesterday
- Filter to messages sent by the authenticated user
- Return structured data: `list[Message]` with timestamp, text, channel

**GitHub Connector (`github_connector.py`)**
- Authenticate via GitHub personal access token
- Fetch commits from yesterday across multiple repos (configurable list)
- Filter to commits by the authenticated user
- Return structured data: `list[Commit]` with repo, message, timestamp, files changed

**Shared interface** — both connectors expose:
```python
async def fetch(config: dict) -> list[ConnectorRecord]:
    """Returns normalized records with: source, timestamp, summary, raw_data"""
```

### Deepika — Product / Orchestration
**Branch:** `feature/jira-orchestrator-prompt` | **Folder:** `deepika/` | **Plan:** `deepika/PLAN_DEEPIKA.md`

Owns Jira integration, the orchestration layer that calls all connectors, and the Claude prompt.

**Jira Connector (`jira_connector.py`)**
- Authenticate via Jira API token (basic auth with email + token)
- Fetch tickets assigned to the user that were updated yesterday
- Fetch comments the user left yesterday
- Pull ticket status (especially "Blocked" status or blocker flags)
- Pull sprint deadlines and current sprint info
- Return structured data: `list[JiraItem]` with ticket key, summary, status, comments, sprint info

**Orchestrator (`orchestrator.py`)**
- Call all three connectors in parallel (asyncio.gather)
- Merge results into a unified timeline
- Pass merged context to the prompt module
- Return the generated standup to the API layer

**Prompt (`prompt.py`)**
- Build the Claude API prompt from the merged context
- System prompt instructs Claude to generate a standup with three sections:
  1. **Yesterday** — synthesize from Teams messages + commits + Jira updates
  2. **Today** — infer from sprint deadlines, open tickets, and yesterday's messages about planned work
  3. **Blockers** — surface tickets marked as blocked, stale PRs, or unresolved discussion threads
- Use `anthropic` Python SDK, model: `claude-sonnet-4-6-20250514`
- Return the standup as markdown text

### Anusha — Frontend
**Branch:** `feature/frontend-api` | **Folder:** `anusha/` | **Plan:** `anusha/PLAN_ANUSHA.md`

Owns the web interface and the thin FastAPI layer that serves it.

**FastAPI Routes (`anusha/app.py`)**
- `POST /api/generate` — accepts config (repos, Jira project, Teams chat ID), calls orchestrator, returns standup markdown
- `GET /api/health` — health check
- Serves the built frontend as static files in production
- CORS middleware for local dev

**React Frontend (`anusha/frontend/`)**
- Single-page app with:
  - Config form: GitHub repos, Jira project key, Teams chat ID
  - "Generate Standup" button
  - Standup output panel (rendered markdown)
  - Edit/copy controls so the user can tweak the draft before posting
- Minimal styling (Tailwind CSS)
- API client module (`api.ts`) for calling the backend

## Shared Interfaces

All three people should agree on these types upfront (first 15 minutes):

```python
# shared/__init__.py — Python interface (used by kanishk/ and deepika/)

@dataclass
class ConnectorRecord:
    source: str        # "teams" | "github" | "jira"
    timestamp: datetime
    summary: str       # one-line human-readable summary
    category: str      # "message" | "commit" | "ticket_update" | "comment"
    raw_data: dict     # full payload for the prompt to use
```

```typescript
// shared/types.ts — TypeScript interface (used by anusha/frontend/)

interface GenerateRequest {
  github_repos: string[];
  github_username: string;
  jira_project_key: string;
  jira_email: string;
  teams_chat_id: string;
}

interface StandupResponse {
  standup_markdown: string;
  sources_used: number;
  generated_at: string;
}
```

## Timeline (3-4 hours)

| Time | Phase | Everyone | Kanishk | Deepika | Anusha |
|------|-------|----------|---------|---------|--------|
| 0:00-0:15 | Setup | Agree on interfaces, set up .env, install deps | — | — | — |
| 0:15-0:30 | Scaffold | — | Scaffold connectors/ | Scaffold orchestrator + prompt | Scaffold FastAPI + Vite app |
| 0:30-1:30 | Build | — | Teams + GitHub connectors | Jira connector + orchestrator | Frontend UI + API routes |
| 1:30-2:00 | Integrate | Merge branches, wire end-to-end | — | — | — |
| 2:00-2:30 | Test | Test with sample Teams chat, sample repos, sample Jira | Debug auth flows | Tune prompt with real data | Fix UI bugs |
| 2:30-3:00 | Polish | — | Fallback: if Teams Graph API blocked, stub it or pivot to Slack | Iterate on prompt quality | Add edit/copy UX |
| 3:00-3:30 | Demo prep | README, project card on sundai.club/projects, demo script | — | — | — |

## Setup Checklist

### Credentials Needed (put in `.env`, never commit)
- `ANTHROPIC_API_KEY` — Claude API key
- `GITHUB_TOKEN` — Personal access token with `repo` scope
- `JIRA_BASE_URL` — e.g. `https://yourorg.atlassian.net`
- `JIRA_EMAIL` — Jira account email
- `JIRA_API_TOKEN` — Jira API token (from id.atlassian.com)
- `TEAMS_CLIENT_ID` — Azure AD app registration client ID
- `TEAMS_CLIENT_SECRET` — Azure AD app registration client secret
- `TEAMS_TENANT_ID` — Azure AD tenant ID

### Sample Environment for Testing
- Create a test Teams group chat with a few messages
- Set up a test Jira project with a sprint, a few tickets, and some comments
- Use your real GitHub repos (read-only access, no risk)

## Risk: Teams Graph API Permissions

The user's organization may not grant Microsoft Graph API permissions for chat access. Mitigation plan:

1. **Try first:** Register an Azure AD app, request `Chat.Read` delegated permission, attempt interactive OAuth login
2. **If blocked:** Fall back to Slack (Slack Bot Token + `channels:history` scope is much easier to get)
3. **If both blocked:** Accept manual paste of chat messages into the web UI as a text box, still generate the standup from Jira + GitHub + pasted text

## Sundai Requirements
- Code must be open-source (already MIT licensed)
- Include "Built at Sundai" in README and any public materials
- Create a project card at sundai.club/projects after the hack
- All work must be published by end of event

## Git Workflow

Each person works on their own branch to avoid merge conflicts:
- `feature/teams-github-connectors` — Kanishk
- `feature/jira-orchestrator-prompt` — Deepika
- `feature/frontend-api` — Anusha

Since directory ownership is disjoint, merges to `main` should be conflict-free. Integrate after the Build phase (~1.5 hours in).
