import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import config from "../config";
import { getUserIdentifier } from "../utils/auth";

function WeeklyReviewPanel({ courseName, panelClassName = "" }) {
  const [prompts, setPrompts] = useState([]);
  const [fullText, setFullText] = useState("");
  const [loading, setLoading] = useState(false);

  async function generateReview() {
    setLoading(true);
    setPrompts([]);
    setFullText("");
    try {
      const res = await fetch(`${config.API_BASE_URL}/api/weekly-review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_identifier: getUserIdentifier(),
          course: courseName || undefined,
        }),
      });
      const data = await res.json();
      if (data.review_prompts) setPrompts(data.review_prompts);
      if (data.full_text) setFullText(data.full_text);
      if (data.message && !data.review_prompts?.length) setFullText(data.message);
    } catch (e) {
      setFullText("Failed to generate review.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className={`fade-in-up flex min-h-[320px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-9 lg:min-h-0 ${panelClassName}`}
    >
      <header className="mb-4 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Learning</p>
        <h2 className="mt-0.5 text-2xl font-semibold leading-tight text-white">
          Weekly review
        </h2>
        <p className="mt-1 text-sm text-[#E8F7FB]">
          Generate review prompts based on your recorded mistakes and weak areas.
        </p>
        <button
          type="button"
          onClick={generateReview}
          disabled={loading}
          className="mt-3 rounded-xl bg-[#FFE3B3] px-4 py-2 text-sm font-semibold text-[#1f4d6f] hover:bg-[#fff0cf] disabled:opacity-50"
        >
          {loading ? "Generating…" : "Generate weekly review"}
        </button>
      </header>
      <div className="flex-1 space-y-2 overflow-y-auto pr-1">
        {prompts.length > 0 && (
          <ul className="list-inside list-decimal space-y-1 text-sm text-[#E8F7FB]">
            {prompts.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        )}
        {fullText && (
          <div className="prose prose-invert max-w-none text-sm text-[#E8F7FB]">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{fullText}</ReactMarkdown>
          </div>
        )}
      </div>
    </section>
  );
}

export default WeeklyReviewPanel;
