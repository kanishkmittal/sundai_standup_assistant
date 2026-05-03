# Anusha — Frontend & FastAPI Routes

**Branch:** `feature/frontend-api`
**Folder:** `anusha/`

## Status

| Task | Status | Notes |
|------|--------|-------|
| Vite + React + Tailwind scaffold | Not started | |
| Config form component | Not started | |
| Generate button + loading state | Not started | |
| Standup output panel (markdown) | Not started | |
| Edit/copy controls | Not started | |
| FastAPI routes (`app.py`) | Not started | |
| CORS + static file serving | Not started | |
| Wire frontend to backend | Not started | Needs Deepika's orchestrator |

## FastAPI Routes — `app.py`

### Endpoints
```
POST /api/generate
  Body: GenerateRequest
  Response: StandupResponse { standup_markdown, sources_used, generated_at }

GET /api/health
  Response: { status: "ok" }
```

### Setup
- `FastAPI()` with CORS middleware (allow `localhost:5173` for Vite dev server)
- `python-dotenv` to load `.env` from project root
- Call `deepika.orchestrator.generate_standup(config)` and wrap result
- In production, serve `anusha/frontend/dist/` as static files via `StaticFiles`

## React Frontend — `anusha/frontend/`

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

### API Client (`frontend/src/api.ts`)
Already scaffolded. Imports shared types from `shared/types.ts`.
- Dev: `http://localhost:8000`
- Prod: relative `/api/...`

### Styling
- Clean, minimal layout
- Dark mode friendly (optional stretch goal)
- Mobile-responsive not required for hackathon demo

## Dependencies

### Python (`requirements.txt`)
- `fastapi`, `uvicorn`, `python-dotenv`

### Frontend (to install via npm/bun)
- `react`, `react-dom`
- `react-markdown`
- `tailwindcss`, `@tailwindcss/vite`
- `vite`, `@vitejs/plugin-react`

## Integration Contract
- Frontend calls `POST /api/generate` with `GenerateRequest`
- Backend returns `StandupResponse`
- Types defined in `shared/types.ts` (frontend) and `shared/__init__.py` (backend)
- `app.py` imports and calls `deepika.orchestrator.generate_standup(config)`

## Notes / Log
_Update this section as you work — what you tried, what worked, what didn't._
