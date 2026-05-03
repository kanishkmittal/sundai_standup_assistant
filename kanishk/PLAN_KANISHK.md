# Kanishk — Teams & GitHub Connectors

**Branch:** `feature/teams-github-connectors`
**Folder:** `kanishk/`

## Status

| Task | Status | Notes |
|------|--------|-------|
| Teams OAuth setup | Not started | Need to test if org allows Graph API `Chat.Read` |
| Teams message fetch | Not started | |
| GitHub auth | Not started | PAT with `repo` scope |
| GitHub multi-repo commit fetch | Not started | |
| Integration test with orchestrator | Not started | Blocked on Deepika's orchestrator |

## Teams Connector — `teams.py`

### Auth
- Register an Azure AD app (or use an existing one) with delegated permission `Chat.Read`
- Use MSAL (Microsoft Authentication Library) for OAuth2 interactive login
- Token goes in `Authorization: Bearer <token>` header
- **If org blocks Graph API access:** fall back to Slack (`channels:history` scope) or a manual paste input

### API Calls
1. **List chats** — `GET https://graph.microsoft.com/v1.0/me/chats` to find the target group chat
2. **Get messages** — `GET https://graph.microsoft.com/v1.0/me/chats/{chat-id}/messages` with `$filter` on `createdDateTime` for yesterday
3. **Filter** — only return messages where `from.user.id` matches the authenticated user

### Output
Return `list[ConnectorRecord]` where:
- `source = "teams"`
- `category = "message"`
- `summary` = first 100 chars of message body
- `raw_data` = full message payload (body, mentions, attachments)

### Edge Cases
- Paginated results (>50 messages) — follow `@odata.nextLink`
- Messages with attachments or adaptive cards — extract text content
- Rate limiting — Graph API allows 10,000 requests per 10 minutes, not a concern for this use case

## GitHub Connector — `github_connector.py`

### Auth
- Personal access token (classic) with `repo` scope
- Pass as `Authorization: Bearer <token>` header

### API Calls
1. **For each repo** in config `github_repos` list:
   - `GET https://api.github.com/repos/{owner}/{repo}/commits?author={username}&since={yesterday_iso}&until={today_iso}`
2. Collect commits across all repos

### Output
Return `list[ConnectorRecord]` where:
- `source = "github"`
- `category = "commit"`
- `summary` = commit message (first line)
- `raw_data` = `{ repo, sha, message, url, files_changed, additions, deletions }`

### Edge Cases
- Repos the user has access to but no commits yesterday — return empty list, don't error
- Merge commits — include them (they represent work done)
- Pagination — unlikely for one day of commits, but handle `Link` header if present

## Dependencies
- `httpx` for async HTTP calls
- `msal` for Teams OAuth
- `python-dotenv` for env vars

## Integration Contract
Both connectors expose:
```python
async def fetch(config: dict) -> list[ConnectorRecord]
```
Deepika's orchestrator will import `kanishk.teams` and `kanishk.github_connector` and call `fetch()`.

## Notes / Log
_Update this section as you work — what you tried, what worked, what didn't._
