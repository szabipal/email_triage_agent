import { FormEvent, useEffect, useState } from "react";
import { api, EmailDetail, InboxItem, Preference, Proposal } from "./api";

const emptyPreference: Preference = {
  id: "preference-ui",
  preference_type: "sender",
  value: "",
  effect: "boost",
  weight: 1,
  enabled: true,
};

export function App() {
  const [inbox, setInbox] = useState<InboxItem[]>([]);
  const [selectedId, setSelectedId] = useState<string>();
  const [detail, setDetail] = useState<EmailDetail>();
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [draftPreference, setDraftPreference] =
    useState<Preference>(emptyPreference);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string>();
  const [notice, setNotice] = useState<string>();

  async function load() {
    setLoading(true);
    setError(undefined);
    try {
      const [nextInbox, nextPreferences, nextProposals] = await Promise.all([
        api.inbox(),
        api.preferences(),
        api.proposals(),
      ]);
      setInbox(nextInbox);
      setPreferences(nextPreferences);
      setProposals(nextProposals);
      setSelectedId((current) => current ?? nextInbox[0]?.email_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load inbox");
    } finally {
      setLoading(false);
    }
  }

  async function syncGmail() {
    setSyncing(true);
    setError(undefined);
    setNotice(undefined);
    try {
      const result = await api.syncGmail();
      setNotice(
        `Gmail sync imported ${result.imported}, analyzed ${result.processed}, and labeled ${result.labeled}.`,
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sync Gmail");
    } finally {
      setSyncing(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setDetail(undefined);
      return;
    }
    api
      .detail(selectedId)
      .then(setDetail)
      .catch((err) => {
        setDetail(undefined);
        setError(err instanceof Error ? err.message : "Unable to load email");
      });
  }, [selectedId]);

  async function savePreference(event: FormEvent) {
    event.preventDefault();
    const saved = await api.savePreference(draftPreference);
    setPreferences((items) => [
      saved,
      ...items.filter((item) => item.id !== saved.id),
    ]);
  }

  async function decide(proposal: Proposal, decision: "approved" | "rejected") {
    await api.decideProposal(proposal.id, decision);
    if (decision === "approved") await api.executeProposal(proposal.id);
    await load();
    if (selectedId) setDetail(await api.detail(selectedId));
  }

  const selected = inbox.find((item) => item.email_id === selectedId);

  return (
    <main>
      <header>
        <div>
          <h1>Email Agent</h1>
          <p>{inbox.length} analyzed messages</p>
        </div>
        <div className="header-actions">
          <button disabled={syncing} onClick={() => void syncGmail()}>
            {syncing ? "Syncing..." : "Sync Gmail"}
          </button>
          <button onClick={() => void load()}>Refresh</button>
        </div>
      </header>

      {loading && <p role="status">Loading inbox...</p>}
      {error && <p role="alert">Could not load data.</p>}
      {notice && <p role="status">{notice}</p>}

      <section className="layout">
        <aside aria-label="Prioritized inbox">
          {inbox.length === 0 && !loading ? (
            <p>No analyzed emails yet.</p>
          ) : (
            inbox.map((item) => (
              <button
                className={item.email_id === selectedId ? "selected" : ""}
                key={item.email_id}
                onClick={() => setSelectedId(item.email_id)}
              >
                <span className={`band ${item.priority_band}`}>
                  {item.priority_band}
                </span>
                <strong>{item.subject}</strong>
                <span>{item.sender}</span>
                <small>{item.summary}</small>
              </button>
            ))
          )}
        </aside>

        <article>
          <h2>{selected?.subject ?? "Email detail"}</h2>
          {detail ? (
            <>
              <p>{selected?.summary}</p>
              <dl>
                <dt>Category</dt>
                <dd>{selected?.category}</dd>
                <dt>Action</dt>
                <dd>{selected?.action_required ? "Required" : "None"}</dd>
                <dt>Priority</dt>
                <dd>
                  {selected?.priority_band} {selected?.priority_score}
                </dd>
              </dl>
              <h3>Why</h3>
              <p>{detail.analysis.explanation ?? "No explanation recorded."}</p>
              <ul>
                {detail.factors.map((factor) => (
                  <li key={factor.name}>
                    {factor.name}: {factor.direction} ({factor.weight})
                  </li>
                ))}
              </ul>
              <h3>Context</h3>
              {detail.retrieved_context.length ? (
                <ul>
                  {detail.retrieved_context.map((context) => (
                    <li key={context.id}>{context.summary}</li>
                  ))}
                </ul>
              ) : (
                <p>No retrieved context used.</p>
              )}
            </>
          ) : (
            !loading && <p>Select an email to inspect it.</p>
          )}
        </article>

        <section aria-label="Preferences and proposals">
          <h2>Preferences</h2>
          <form onSubmit={(event) => void savePreference(event)}>
            <select
              value={draftPreference.preference_type}
              onChange={(event) =>
                setDraftPreference({
                  ...draftPreference,
                  preference_type: event.target
                    .value as Preference["preference_type"],
                })
              }
            >
              <option value="sender">Sender</option>
              <option value="category">Category</option>
              <option value="keyword">Keyword</option>
              <option value="output_language">Output language</option>
            </select>
            <input
              aria-label="Preference value"
              value={draftPreference.value}
              onChange={(event) =>
                setDraftPreference({
                  ...draftPreference,
                  value: event.target.value,
                })
              }
            />
            <button>Save</button>
          </form>
          <ul>
            {preferences.map((preference) => (
              <li key={preference.id}>
                {preference.preference_type}: {String(preference.value)}
              </li>
            ))}
          </ul>

          <h2>Calendar Proposals</h2>
          {proposals.length ? (
            proposals.map((proposal) => (
              <div className="proposal" key={proposal.id}>
                <strong>{proposal.title}</strong>
                <span>{proposal.status}</span>
                <small>
                  {proposal.start_at ?? proposal.missing_fields.join(", ")}
                </small>
                <div>
                  <button
                    disabled={proposal.status !== "pending"}
                    onClick={() => void decide(proposal, "approved")}
                  >
                    Approve
                  </button>
                  <button
                    disabled={
                      !["pending", "incomplete"].includes(proposal.status)
                    }
                    onClick={() => void decide(proposal, "rejected")}
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p>No calendar proposals.</p>
          )}
        </section>
      </section>
    </main>
  );
}
