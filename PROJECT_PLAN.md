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
│                   React Frontend                     │
│              (TypeScript / Vite)                      │
│         /frontend                                    │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│                 FastAPI Backend                       │
│              /backend/app.py                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │
│  │  Teams   │  │  GitHub  │  │    Jira      │       │
│  │ Connector│  │ Connector│  │  Connector   │       │
│  └──────────┘  └──────────┘  └──────────────┘       │
│       │              │              │                 │
│       └──────────────┼──────────────┘                │
│                      ▼                               │
│              Orchestrator                            │
│          /backend/orchestrator.py                     │
│                      │                               │
│                      ▼                               │
│              Claude API (Prompt)                      │
│          /backend/prompt.py                           │
└──────────────────────────────────────────────────────┘
```

## Directory Structure (Disjoint Workstreams)

```
sundai_standup_assistant/
├── backend/
│   ├── connectors/
│   │   ├── __init__.py          ← shared interface
│   │   ├── teams.py             ← Person A
│   │   ├── github_connector.py  ← Person A
│   │   └── jira_connector.py    ← Person B
│   ├── orchestrator.py          ← Person B
│   ├── prompt.py                ← Person B
│   ├── app.py                   ← Person C (thin FastAPI routes)
│   └── requirements.txt
├── frontend/                    ← Person C (entire directory)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── api.ts
│   ├── package.json
│   └── vite.config.ts
├── .env.example
├── PROJECT_PLAN.md
├── LICENSE
└── README.md
```

## Team Assignments

### Person A — Backend / APIs
**Files:** `backend/connectors/teams.py`, `backend/connectors/github_connector.py`

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
async def fetch(config: dict) -> list[dict]:
    """Returns normalized records with: source, timestamp, summary, raw_data"""
```

### Person B — Product / Orchestration
**Files:** `backend/connectors/jira_connector.py`, `backend/orchestrator.py`, `backend/prompt.py`

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

### Person C — Frontend
**Files:** `frontend/` (entire directory), `backend/app.py`

Owns the web interface and the thin FastAPI layer that serves it.

**FastAPI Routes (`backend/app.py`)**
- `POST /api/generate` — accepts config (repos, Jira project, Teams chat ID), calls orchestrator, returns standup markdown
- `GET /api/health` — health check
- Serves the built frontend as static files in production
- CORS middleware for local dev

**React Frontend (`frontend/`)**
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
# backend/connectors/__init__.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConnectorRecord:
    source: str        # "teams" | "github" | "jira"
    timestamp: datetime
    summary: str       # one-line human-readable summary
    category: str      # "message" | "commit" | "ticket_update" | "comment"
    raw_data: dict     # full payload for the prompt to use
```

```typescript
// frontend/src/api.ts

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

| Time | Phase | Everyone | Person A | Person B | Person C |
|------|-------|----------|----------|----------|----------|
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
- `feature/teams-github-connectors` — Person A
- `feature/jira-orchestrator-prompt` — Person B
- `feature/frontend-api` — Person C

Since directory ownership is disjoint, merges to `main` should be conflict-free. Integrate after the Build phase (~1.5 hours in).
