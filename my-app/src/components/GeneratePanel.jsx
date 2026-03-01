import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import config from "../config";
import { getUserIdentifier } from "../utils/auth";

/** Normalize LLM math: convert [ \lim... ] / ( f(x) ) style to $$...$$ and $...$ so KaTeX renders. */
function normalizeMathForDisplay(text) {
  if (!text || typeof text !== "string") return text;
  let out = text;
  // Display math: [ \something ... ] → $$...$$
  out = out.replace(/\[\s*((?:[^[\]]|\\.)*?)\s*\]/g, (_, inner) => {
    if (/\\\w+|\\frac|\\lim|\\sum|\\int|\\to/.test(inner)) {
      return `$$${inner.trim()}$$`;
    }
    return `[ ${inner} ]`;
  });
  // Inline math: ( \something ) or ( formula with \ ) → $...$ (only when it looks like LaTeX)
  out = out.replace(/\(\s*((?:[^()]|\\.)+?)\s*\)/g, (_, inner) => {
    const t = inner.trim();
    if (/\\\w+|\\frac|\^|_\{|\\to/.test(t)) {
      return `$${t}$`;
    }
    return `( ${inner} )`;
  });
  return out;
}

function GeneratePanel({
  courseName,
  selectedDocuments,
  panelClassName = "",
}) {
  const [topic, setTopic] = useState("");
  const [studyGuide, setStudyGuide] = useState("");
  const [practiceExam, setPracticeExam] = useState("");
  const [loadingGuide, setLoadingGuide] = useState(false);
  const [loadingExam, setLoadingExam] = useState(false);

  async function generateStudyGuide() {
    setLoadingGuide(true);
    setStudyGuide("");
    try {
      const res = await fetch(`${config.API_BASE_URL}/api/generate-study-guide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          course_name: courseName,
          topic: topic.trim() || undefined,
          document_filenames: selectedDocuments || [],
        }),
      });
      const data = await res.json();
      setStudyGuide(data.study_guide || "Failed to generate.");
    } catch (e) {
      setStudyGuide("Failed to generate.");
    } finally {
      setLoadingGuide(false);
    }
  }

  async function generatePracticeExam() {
    setLoadingExam(true);
    setPracticeExam("");
    try {
      const res = await fetch(`${config.API_BASE_URL}/api/generate-practice-exam`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          course_name: courseName,
          topic: topic.trim() || undefined,
          document_filenames: selectedDocuments || [],
        }),
      });
      const data = await res.json();
      setPracticeExam(data.practice_exam || "Failed to generate.");
    } catch (e) {
      setPracticeExam("Failed to generate.");
    } finally {
      setLoadingExam(false);
    }
  }

  return (
    <section
      className={`fade-in-up flex min-h-[320px] flex-col overflow-hidden rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-9 lg:h-full lg:min-h-0 ${panelClassName}`}
    >
      <header className="mb-4 shrink-0 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Learning</p>
        <h2 className="mt-0.5 text-2xl font-semibold leading-tight text-white">
          Generate study materials
        </h2>
        <p className="mt-1 text-sm text-[#E8F7FB]">
          Create study guides or practice exams for {courseName}. Optionally narrow by topic and use selected documents.
        </p>
        <input
          type="text"
          placeholder="Topic (optional)"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="mt-2 w-full max-w-xs rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-3 py-1.5 text-sm text-white placeholder:text-[#b9dfe9]"
        />
      </header>
      <div className="shrink-0 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={generateStudyGuide}
          disabled={loadingGuide}
          className="rounded-xl bg-[#FFE3B3] px-4 py-2 text-sm font-semibold text-[#1f4d6f] hover:bg-[#fff0cf] disabled:opacity-50"
        >
          {loadingGuide ? "Generating…" : "Generate study guide"}
        </button>
        <button
          type="button"
          onClick={generatePracticeExam}
          disabled={loadingExam}
          className="rounded-xl border border-[#FFE3B3]/70 bg-[#26648E]/50 px-4 py-2 text-sm font-semibold text-[#FFE3B3] hover:bg-[#FFE3B3]/20 disabled:opacity-50"
        >
          {loadingExam ? "Generating…" : "Generate practice exam"}
        </button>
      </div>
      <div className="mt-4 min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
        {studyGuide && (
          <div className="rounded-xl border border-[#FFE3B3]/30 bg-[#26648E]/30 p-4">
            <h3 className="text-sm font-semibold text-[#FFE3B3]">Study guide</h3>
            <div className="prose prose-invert mt-2 max-w-none overflow-x-auto text-sm markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {normalizeMathForDisplay(studyGuide)}
              </ReactMarkdown>
            </div>
          </div>
        )}
        {practiceExam && (
          <div className="rounded-xl border border-[#FFE3B3]/30 bg-[#26648E]/30 p-4">
            <h3 className="text-sm font-semibold text-[#FFE3B3]">Practice exam</h3>
            <div className="prose prose-invert mt-2 max-w-none overflow-x-auto text-sm markdown-content practice-exam-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {normalizeMathForDisplay(practiceExam)}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default GeneratePanel;
