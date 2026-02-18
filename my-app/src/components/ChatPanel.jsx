import { useMemo, useState } from "react";

function ChatPanel({ courseName }) {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "assistant",
      text: "Hi! I am your AI homework helper. Ask me anything about your course material.",
    },
  ]);

  const greeting = useMemo(
    () => `Ask questions about ${courseName}, assignments, and concepts.`,
    [courseName],
  );

  function handleSend(event) {
    event.preventDefault();
    const cleanDraft = draft.trim();
    if (!cleanDraft) return;

    const newMessage = {
      id: Date.now(),
      sender: "student",
      text: cleanDraft,
    };

    setMessages((prev) => [...prev, newMessage]);
    setDraft("");
  }

  return (
    <section className="fade-in-up flex min-h-[420px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-6 lg:min-h-0">
      <header className="mb-4 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">AI Chat</p>
        <h2 className="mt-0.5 text-2xl font-semibold leading-tight text-white">{courseName}</h2>
        <p className="mt-1 text-sm leading-6 text-[#E8F7FB]">{greeting}</p>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto pr-1 lg:min-h-0">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
              message.sender === "assistant"
                ? "bg-[#FFE3B3]/85 text-[#1f4d6f]"
                : "ml-auto bg-[#4F8FC0]/75 text-white"
            }`}
          >
            {message.text}
          </div>
        ))}
      </div>

      <form className="mt-4 grid grid-cols-[1fr_auto_auto] items-center gap-2" onSubmit={handleSend}>
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Type your question..."
          className="h-11 w-full rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-4 text-sm text-white placeholder:text-[#b9dfe9] transition-all duration-300 focus:border-[#FFE3B3] focus:outline-none focus:ring-2 focus:ring-[#FFE3B3]/45"
        />
        <button
          type="button"
          className="inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-xl border border-[#FFE3B3]/60 bg-[#26648E]/60 text-sm text-[#FFE3B3] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#FFE3B3]/20"
          title="Voice input (UI only)"
        >
          🎤
        </button>
        <button
          type="submit"
          className="inline-flex h-11 cursor-pointer items-center justify-center rounded-xl bg-[#FFE3B3] px-5 text-sm font-semibold text-[#1f4d6f] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#fff0cf]"
        >
          Send
        </button>
      </form>
    </section>
  );
}

export default ChatPanel;
