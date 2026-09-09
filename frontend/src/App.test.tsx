import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { App } from "./App";

const inbox = [
  {
    email_id: "email-1",
    subject: "Planning",
    sender: "ada@example.com",
    received_at: "2026-01-02T14:00:00Z",
    summary: "Ada asks for planning.",
    category: "work",
    action_required: true,
    priority_band: "high",
    priority_score: 92,
  },
];

const detail = {
  email: { id: "email-1", subject: "Planning", body_raw: "Meet tomorrow." },
  analysis: { explanation: "Action required.", errors: [] },
  factors: [{ name: "action", direction: "positive", weight: 1 }],
  retrieved_context: [{ id: "ctx-1", summary: "Earlier context." }],
  proposals: [],
};

const proposals = [
  {
    id: "proposal-1",
    email_id: "email-1",
    title: "Planning",
    start_at: "2026-01-02T14:00:00Z",
    status: "pending",
    source: "meeting",
    missing_fields: [],
  },
];

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url =
        typeof input === "string"
          ? input
          : "url" in input
            ? input.url
            : input.toString();
      if (url.endsWith("/inbox")) return json(inbox);
      if (url.endsWith("/emails/email-1")) return json(detail);
      if (url.endsWith("/preferences")) return json([]);
      if (url.endsWith("/proposals") && !init?.method) return json(proposals);
      if (url.endsWith("/sync/gmail")) {
        return json({ imported: 1, processed: 1, errors: [] });
      }
      if (url.endsWith("/approval")) return json({ proposal_id: "proposal-1" });
      if (url.endsWith("/execute")) {
        return json({ ...proposals[0], status: "executed" });
      }
      return Promise.resolve(new Response("not found", { status: 404 }));
    }),
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("renders inbox detail, context, and proposal actions", async () => {
  render(<App />);

  expect(
    await screen.findByRole("heading", { name: "Planning" }),
  ).toBeInTheDocument();
  expect(await screen.findByText("Earlier context.")).toBeInTheDocument();
  expect(screen.getByText("Action")).toBeInTheDocument();
  expect(screen.getByText("Approve")).toBeEnabled();
});

test("approval calls approval then execution endpoints", async () => {
  render(<App />);

  fireEvent.click(await screen.findByText("Approve"));

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/proposals/proposal-1/execute"),
      expect.objectContaining({ method: "POST" }),
    );
  });
});

test("sync gmail calls endpoint and reloads inbox", async () => {
  render(<App />);

  fireEvent.click(await screen.findByText("Sync Gmail"));

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sync/gmail"),
      expect.objectContaining({ method: "POST" }),
    );
  });
  expect(
    await screen.findByText("Gmail sync imported 1 and analyzed 1."),
  ).toBeInTheDocument();
});

test("shows loading and error states", async () => {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response("offline", { status: 500 }),
  );

  render(<App />);

  expect(screen.getByRole("status")).toHaveTextContent("Loading inbox");
  expect(await screen.findByRole("alert")).toHaveTextContent("Could not load");
});

function json(value: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(value), {
      status: 200,
      headers: { "content-type": "application/json" },
    }),
  );
}
