import { useMemo, useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import config from "../config";

function ChatPanel({ courseName, selectedCourseId, selectedDocuments, panelClassName = "" }) {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "assistant",
      text: "Hi! I am your AI homework helper. Ask me anything about your course material.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const greeting = useMemo(
    () => `Ask questions about ${courseName}, assignments, and concepts.`,
    [courseName],
  );

  // Clear chat history when course changes
  useEffect(() => {
    setMessages([
      {
        id: 1,
        sender: "assistant",
        text: "Hi! I am your AI homework helper. Ask me anything about your course material.",
      },
    ]);
  }, [selectedCourseId]);

  async function handleSend(event) {
    event.preventDefault();
    const cleanDraft = draft.trim();
    if (!cleanDraft || isLoading) return;

    const newMessage = {
      id: Date.now(),
      sender: "student",
      text: cleanDraft,
    };

    setMessages((prev) => [...prev, newMessage]);
    setDraft("");
    setIsLoading(true);

    try {
      // Build conversation history for the backend (excluding the initial greeting)
      const conversationHistory = messages
        .filter(msg => msg.id !== 1) // Exclude initial greeting
        .map(msg => ({
          role: msg.sender === "student" ? "user" : "assistant",
          content: msg.text
        }));
      
      // Add the new message
      conversationHistory.push({
        role: "user",
        content: cleanDraft
      });

      // Call backend API with conversation history
      const response = await fetch(`${config.API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: cleanDraft,
          course_name: courseName,
          conversation_history: conversationHistory,
          document_filenames: selectedDocuments,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from AI');
      }

      const data = await response.json();

      // Add AI response to messages
      const aiMessage = {
        id: Date.now() + 1,
        sender: "assistant",
        text: data.response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error calling AI:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        sender: "assistant",
        text: "Sorry, I encountered an error. Please make sure the backend server is running and try again.",
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className={`fade-in-up flex min-h-[420px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-6 lg:min-h-0 ${panelClassName}`}>
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
            {message.sender === "assistant" ? (
              <div className="markdown-content">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {message.text}
                </ReactMarkdown>
              </div>
            ) : (
              message.text
            )}
          </div>
        ))}
      </div>

      <form className="mt-4 grid grid-cols-[1fr_auto_auto] items-center gap-2" onSubmit={handleSend}>
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Type your question..."
          disabled={isLoading}
          className="h-11 w-full rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-4 text-sm text-white placeholder:text-[#b9dfe9] transition-all duration-300 focus:border-[#FFE3B3] focus:outline-none focus:ring-2 focus:ring-[#FFE3B3]/45 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="button"
          className="inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-xl border border-[#FFE3B3]/60 bg-[#26648E]/60 text-sm text-[#FFE3B3] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#FFE3B3]/20"
          title="Voice input (UI only)"
          disabled={isLoading}
        >
          🎤
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex h-11 cursor-pointer items-center justify-center rounded-xl bg-[#FFE3B3] px-5 text-sm font-semibold text-[#1f4d6f] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#fff0cf] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </section>
  );
}

export default ChatPanel;
