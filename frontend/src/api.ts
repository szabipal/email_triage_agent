export type InboxItem = {
  email_id: string;
  subject: string;
  sender: string;
  received_at: string;
  summary: string;
  category: string;
  action_required: boolean;
  priority_band: "low" | "normal" | "high";
  priority_score: number;
};

export type EmailDetail = {
  email: { id: string; subject: string; body_raw: string };
  analysis: {
    explanation?: string | null;
    errors: string[];
  };
  factors: { name: string; direction: string; weight: number }[];
  retrieved_context: {
    id: string;
    summary: string;
    skip_reason?: string | null;
  }[];
  proposals: Proposal[];
};

export type Preference = {
  id: string;
  preference_type: "sender" | "category" | "keyword" | "output_language";
  value: string;
  effect: "boost" | "penalize" | "display";
  weight: number;
  enabled: boolean;
};

export type Proposal = {
  id: string;
  email_id: string;
  title: string;
  start_at: string | null;
  end_at?: string | null;
  status: string;
  source: string;
  confidence?: number | null;
  missing_fields: string[];
  provider_event_id?: string | null;
};

export type GmailSyncResult = {
  imported: number;
  processed: number;
  errors: string[];
};

const base = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

export const api = {
  inbox: () => request<InboxItem[]>("/inbox"),
  detail: (id: string) => request<EmailDetail>(`/emails/${id}`),
  preferences: () => request<Preference[]>("/preferences"),
  savePreference: (preference: Preference) =>
    request<Preference>(`/preferences/${preference.id}`, {
      method: "PUT",
      body: JSON.stringify(preference),
    }),
  proposals: () => request<Proposal[]>("/proposals"),
  decideProposal: (id: string, decision: "approved" | "rejected") =>
    request(`/proposals/${id}/approval`, {
      method: "POST",
      body: JSON.stringify({ decision, decided_by: "user" }),
    }),
  executeProposal: (id: string) =>
    request<Proposal>(`/proposals/${id}/execute`, { method: "POST" }),
  syncGmail: () =>
    request<GmailSyncResult>("/sync/gmail", {
      method: "POST",
      body: JSON.stringify({ limit: 10 }),
    }),
};
