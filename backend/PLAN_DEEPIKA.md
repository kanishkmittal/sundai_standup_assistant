# Deepika — Jira Connector, Orchestrator & Prompt

**Branch:** `feature/jira-orchestrator-prompt`
**Files I own:** `backend/connectors/jira_connector.py`, `backend/orchestrator.py`, `backend/prompt.py`

## Status

| Task | Status | Notes |
|------|--------|-------|
| Jira auth setup | Not started | Basic auth with email + API token |
| Jira ticket fetch | Not started | |
| Jira comment fetch | Not started | |
| Jira sprint/blocker detection | Not started | |
| Orchestrator (parallel connector calls) | Not started | |
| Claude prompt design | Not started | |
| Claude API integration | Not started | |
| End-to-end test | Not started | Needs Kanishk's connectors merged |

## Jira Connector — `jira_connector.py`

### Auth
- Basic auth: base64-encode `{email}:{api_token}`
- Pass as `Authorization: Basic <encoded>` header
- API tokens created at https://id.atlassian.com/manage-profile/security/api-tokens

### API Calls
1. **Assigned tickets updated yesterday:**
   ```
   GET /rest/api/3/search?jql=assignee=currentUser() AND updated >= -1d ORDER BY updated DESC
   ```
2. **Comments by the user yesterday:**
   - For each ticket above, `GET /rest/api/3/issue/{key}/comment`
   - Filter comments where `author.accountId` matches and `created` is yesterday
3. **Sprint info:**
   ```
   GET /rest/agile/1.0/board/{boardId}/sprint?state=active
   ```
   Then get sprint details for deadline/end date
4. **Blocker detection:**
   - Check `status.name` for "Blocked" or similar
   - Check `issuelinks` for blocker-type links

### Output
Return `list[ConnectorRecord]` where each record is one of:
- Ticket update: `category = "ticket_update"`, `raw_data` includes key, summary, status, priority, sprint
- Comment: `category = "comment"`, `raw_data` includes ticket key, comment body
- Blocker: `category = "ticket_update"` with `raw_data.blocked = true`

## Orchestrator — `orchestrator.py`

### Flow
```python
async def generate_standup(config: dict) -> str:
    # 1. Call all connectors in parallel
    teams_records, github_records, jira_records = await asyncio.gather(
        teams.fetch(config),
        github_connector.fetch(config),
        jira_connector.fetch(config),
    )

    # 2. Merge and sort by timestamp
    all_records = sorted(
        teams_records + github_records + jira_records,
        key=lambda r: r.timestamp
    )

    # 3. Generate standup
    return await prompt.generate(all_records)
```

### Error Handling
- If a connector fails, log the error and continue with the others (partial data is better than no data)
- Return metadata about which sources succeeded/failed alongside the standup

## Prompt — `prompt.py`

### System Prompt (draft)
```
You are a standup assistant. Given the user's activity from yesterday across
Teams messages, GitHub commits, and Jira tickets, generate a concise daily
standup update.

Structure your response as:

## Yesterday
- Summarize what the user accomplished based on commits, ticket updates, and messages

## Today
- Infer priorities from: open sprint tickets, deadlines, and any forward-looking
  messages the user sent yesterday (e.g., "tomorrow I'll work on X")

## Blockers
- Surface any tickets marked as Blocked, stale items with no progress,
  or unresolved discussion threads

Keep each section to 3-5 bullet points. Be specific — reference ticket keys,
repo names, and PR numbers. Write in first person ("I did X", not "The user did X").
```

### User Prompt
Serialize all `ConnectorRecord` objects as a JSON array and pass as the user message.

### API Call
- SDK: `anthropic` Python package
- Model: `claude-sonnet-4-6-20250514`
- Max tokens: 1024
- Temperature: 0.3 (factual, low creativity)

## Dependencies
- `httpx` for Jira API calls
- `anthropic` for Claude API
- `python-dotenv` for env vars

## Integration Contract
- Orchestrator imports `connectors.teams`, `connectors.github_connector`, `connectors.jira_connector`
- Each exposes `async def fetch(config: dict) -> list[ConnectorRecord]`
- Anusha's `app.py` calls `orchestrator.generate_standup(config)` and returns the result

## Notes / Log
_Update this section as you work — what you tried, what worked, what didn't._
