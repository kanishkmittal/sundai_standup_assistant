# Anusha — Frontend & FastAPI Routes

**Branch:** `feature/frontend-api`
**Files I own:** `frontend/` (entire directory), `backend/app.py`

## Status

| Task | Status | Notes |
|------|--------|-------|
| Vite + React + Tailwind scaffold | Not started | |
| Config form component | Not started | |
| Generate button + loading state | Not started | |
| Standup output panel (markdown) | Not started | |
| Edit/copy controls | Not started | |
| FastAPI routes | Not started | |
| CORS + static file serving | Not started | |
| Wire frontend to backend | Not started | Needs Deepika's orchestrator |

## FastAPI Routes — `backend/app.py`

### Endpoints
```
POST /api/generate
  Body: GenerateRequest (see api.ts types)
  Response: StandupResponse { standup_markdown, sources_used, generated_at }

GET /api/health
  Response: { status: "ok" }
```

### Setup
- `FastAPI()` with CORS middleware (allow `localhost:5173` for Vite dev server)
- `python-dotenv` to load `.env`
- Call `orchestrator.generate_standup(config)` and wrap result
- In production, serve `frontend/dist/` as static files via `StaticFiles`

## React Frontend — `frontend/`

### Scaffold
- Vite + React + TypeScript
- Tailwind CSS for styling
- No component library needed — keep it simple

### Pages / Components
Single page with three sections:

#### 1. Config Form (`components/ConfigForm.tsx`)
- GitHub repos (comma-separated text input)
- GitHub username (text input)
- Jira project key (text input)
- Jira email (text input)
- Teams chat ID (text input)
- "Generate Standup" button
- Save config to localStorage so it persists between sessions

#### 2. Loading State
- Spinner or skeleton while waiting for `/api/generate`
- Show which sources are being queried (Teams, GitHub, Jira)

#### 3. Standup Output (`components/StandupOutput.tsx`)
- Render the returned markdown (use `react-markdown` or similar)
- "Edit" toggle — switch to a textarea for manual edits
- "Copy to Clipboard" button
- "Regenerate" button
- Timestamp of when it was generated

### API Client (`src/api.ts`)
Already scaffolded with types. Just needs the base URL config:
- Dev: `http://localhost:8000`
- Prod: relative `/api/...`

### Styling
- Clean, minimal layout
- Dark mode friendly (optional stretch goal)
- Mobile-responsive not required for hackathon demo

## Dependencies
- `react-markdown` for rendering standup output
- `tailwindcss` for styling
- `vite` + `@vitejs/plugin-react` for build

### package.json deps (to install)
```
react react-dom
react-markdown
tailwindcss @tailwindcss/vite
```

## Integration Contract
- Frontend calls `POST /api/generate` with `GenerateRequest`
- Backend returns `StandupResponse`
- Types are defined in `frontend/src/api.ts`
- Deepika's orchestrator is called inside `app.py` — Anusha just needs to import and call it

## Notes / Log
_Update this section as you work — what you tried, what worked, what didn't._
