import { useState } from "react";

function CanvasImportModal({ isOpen, onClose, onImport }) {
  const [apiKey, setApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await onImport(apiKey);
      setApiKey("");
      onClose();
    } catch (err) {
      setError(err.message || "Failed to import from Canvas");
    } finally {
      setIsLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-2xl border border-[#FFE3B3]/30 bg-[#26648E] p-6 shadow-2xl">
        <h2 className="mb-4 text-xl font-bold text-white">Import from Canvas</h2>
        
        <div className="mb-4 rounded-lg bg-[#1f4d6f]/50 p-3 text-sm text-[#EAF9FD]">
          <p className="font-semibold text-[#FFE3B3]">Demo Mode</p>
          <p className="mt-1">Use API key: <code className="rounded bg-[#26648E] px-1.5 py-0.5 font-mono text-xs">canvas_demo_2026</code></p>
          <p className="mt-2 text-xs">This will import 4 courses with sample documents</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-[#FFE3B3]">
              Canvas API Key
            </label>
            <input
              type="text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Canvas API key"
              disabled={isLoading}
              className="w-full rounded-lg border border-[#53D2DC]/30 bg-[#1f4d6f]/50 px-3 py-2 text-white placeholder-gray-400 focus:border-[#FFE3B3] focus:outline-none focus:ring-1 focus:ring-[#FFE3B3] disabled:opacity-50"
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-500/20 border border-red-400/30 p-3 text-sm text-red-200">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 rounded-lg border border-[#FFE3B3]/40 px-4 py-2 text-sm font-medium text-[#FFE3B3] transition hover:bg-[#FFE3B3]/10 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !apiKey.trim()}
              className="flex-1 rounded-lg bg-[#FFE3B3] px-4 py-2 text-sm font-semibold text-[#1f4d6f] transition hover:bg-[#fff0cf] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Importing..." : "Import Courses"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CanvasImportModal;
