import type { QueryResult, SessionResponse, UploadResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClientError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiClientError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
  return handle<UploadResponse>(res);
}

export async function loadSample(): Promise<UploadResponse> {
  const res = await fetch(`${API_BASE}/api/sample`);
  return handle<UploadResponse>(res);
}

export async function askQuery(sessionId: string, query: string): Promise<QueryResult> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, query }),
  });
  return handle<QueryResult>(res);
}

export async function refreshSession(sessionId: string): Promise<SessionResponse> {
  const res = await fetch(`${API_BASE}/api/session/${sessionId}`);
  return handle<SessionResponse>(res);
}

export { ApiClientError };
