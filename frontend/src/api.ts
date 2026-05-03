// Anusha — API client for backend

export interface GenerateRequest {
  github_repos: string[];
  github_username: string;
  jira_project_key: string;
  jira_email: string;
  teams_chat_id: string;
}

export interface StandupResponse {
  standup_markdown: string;
  sources_used: number;
  generated_at: string;
}

export async function generateStandup(
  req: GenerateRequest
): Promise<StandupResponse> {
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
