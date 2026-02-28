import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import config from "../config";
import { getUserIdentifier } from "../utils/auth";

function StudyPlanPanel({ panelClassName = "" }) {
  const [plan, setPlan] = useState(null);
  const [editing, setEditing] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function fetchPlan() {
      try {
        const res = await fetch(
          `${config.API_BASE_URL}/api/study-plan?user_identifier=${encodeURIComponent(getUserIdentifier())}`
        );
        if (!res.ok) throw new Error("Failed to load");
        const data = await res.json();
        if (!cancelled) {
          setPlan(data.plan);
          setEditing(
            data.plan
              ? typeof data.plan === "string"
                ? data.plan
                : JSON.stringify(data.plan, null, 2)
              : ""
          );
        }
      } catch (e) {
        if (!cancelled) setPlan(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchPlan();
    return () => { cancelled = true; };
  }, []);

  async function savePlan() {
    setSaving(true);
    try {
      let toSave = editing.trim();
      try {
        toSave = JSON.parse(toSave);
      } catch {
        toSave = { notes: toSave };
      }
      const res = await fetch(`${config.API_BASE_URL}/api/study-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_identifier: getUserIdentifier(),
          plan: toSave,
        }),
      });
      if (res.ok) {
        setPlan(toSave);
      }
    } catch (e) {
      console.error(e);
    } finally {
    setSaving(false);
    }
  }

  return (
    <section
      className={`fade-in-up flex min-h-[320px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-9 lg:min-h-0 ${panelClassName}`}
    >
      <header className="mb-4 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Learning</p>
        <h2 className="mt-0.5 text-2xl font-semibold leading-tight text-white">
          My study plan
        </h2>
        <p className="mt-1 text-sm text-[#E8F7FB]">
          Long-term adaptive plan. Edit as markdown or JSON and save.
        </p>
      </header>
      <div className="flex-1 overflow-y-auto pr-1">
        {loading ? (
          <p className="text-sm text-[#E8F7FB]">Loading…</p>
        ) : (
          <>
            <textarea
              value={editing}
              onChange={(e) => setEditing(e.target.value)}
              placeholder="e.g. Weekly goals, topics to review, or JSON: { &quot;goals&quot;: [], &quot;schedule&quot;: {} }"
              className="mb-2 min-h-[120px] w-full rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 p-3 text-sm text-white placeholder:text-[#b9dfe9]"
              rows={6}
            />
            <button
              type="button"
              onClick={savePlan}
              disabled={saving}
              className="rounded-xl bg-[#FFE3B3] px-4 py-2 text-sm font-semibold text-[#1f4d6f] hover:bg-[#fff0cf] disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save plan"}
            </button>
            {plan && (
              <div className="prose prose-invert mt-4 max-w-none rounded-xl border border-[#FFE3B3]/30 bg-[#26648E]/30 p-4 text-sm">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {typeof plan === "string"
                    ? plan
                    : JSON.stringify(plan, null, 2)}
                </ReactMarkdown>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}

export default StudyPlanPanel;
