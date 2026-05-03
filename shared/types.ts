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
