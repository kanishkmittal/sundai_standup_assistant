import type { GenerateRequest, StandupResponse } from "../../shared/types";

const BASE_URL = import.meta.env.DEV ? "http://localhost:8000" : "";

export async function generateStandup(
  req: GenerateRequest
): Promise<StandupResponse> {
  const res = await fetch(`${BASE_URL}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export type { GenerateRequest, StandupResponse };
