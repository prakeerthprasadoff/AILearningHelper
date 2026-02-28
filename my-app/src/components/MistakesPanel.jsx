import { useEffect, useState } from "react";
import config from "../config";
import { getUserIdentifier } from "../utils/auth";

function MistakesPanel({ courseName, panelClassName = "" }) {
  const [mistakes, setMistakes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterCourse, setFilterCourse] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function fetchMistakes() {
      try {
        const url = new URL(`${config.API_BASE_URL}/api/mistakes`);
        url.searchParams.set("user_identifier", getUserIdentifier());
        if (filterCourse) url.searchParams.set("course", filterCourse);
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to load");
        const data = await res.json();
        if (!cancelled) setMistakes(data.mistakes || []);
      } catch (e) {
        if (!cancelled) setMistakes([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchMistakes();
    return () => { cancelled = true; };
  }, [filterCourse]);

  async function deleteMistake(id) {
    try {
      const res = await fetch(
        `${config.API_BASE_URL}/api/mistakes/${id}?user_identifier=${encodeURIComponent(getUserIdentifier())}`,
        { method: "DELETE" }
      );
      if (res.ok) setMistakes((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <section
      className={`fade-in-up flex min-h-[320px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-9 lg:min-h-0 ${panelClassName}`}
    >
      <header className="mb-4 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Learning</p>
        <h2 className="mt-0.5 text-2xl font-semibold leading-tight text-white">
          My mistakes
        </h2>
        <p className="mt-1 text-sm text-[#E8F7FB]">
          Track weak areas for personalized review. Filter by course or show all.
        </p>
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            placeholder="Filter by course name (optional)"
            value={filterCourse}
            onChange={(e) => setFilterCourse(e.target.value)}
            className="rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-3 py-1.5 text-sm text-white placeholder:text-[#b9dfe9]"
          />
        </div>
      </header>
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {loading ? (
          <p className="text-sm text-[#E8F7FB]">Loading…</p>
        ) : mistakes.length === 0 ? (
          <p className="text-sm text-[#E8F7FB]">
            No mistakes recorded yet. Use “Add to my mistakes” in the chat to build your list.
          </p>
        ) : (
          mistakes.map((m) => (
            <div
              key={m.id}
              className="rounded-xl border border-[#FFE3B3]/40 bg-[#26648E]/40 p-3 text-sm"
            >
              <p className="text-[#FFE3B3] font-medium">{m.course}</p>
              {m.topic && (
                <p className="mt-0.5 text-xs text-[#E8F7FB]">Topic: {m.topic}</p>
              )}
              <p className="mt-1 text-white">{m.question}</p>
              {m.correction && (
                <p className="mt-1 text-[#E8F7FB]">Note: {m.correction}</p>
              )}
              <button
                type="button"
                onClick={() => deleteMistake(m.id)}
                className="mt-2 rounded-lg border border-[#FFE3B3]/50 px-2 py-1 text-xs text-[#FFE3B3] hover:bg-[#FFE3B3]/20"
              >
                Remove
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default MistakesPanel;
