import { useState, useEffect } from "react";

function formatFileSize(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileUploadPanel() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Load already-uploaded files from backend on mount
  useEffect(() => {
    fetch("/api/uploads")
      .then((r) => r.json())
      .then((data) => setUploadedFiles(data.files ?? []))
      .catch(() => {}); // backend may not be running yet
  }, []);

  async function handleFileSelect(event) {
    const selectedFiles = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError("");
    setSuccess("");

    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("/api/upload", { method: "POST", body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Upload failed");
        setUploadedFiles((prev) => [data, ...prev]);
        setSuccess(`"${file.name}" uploaded successfully!`);
      } catch (err) {
        setError(`Failed to upload "${file.name}": ${err.message}`);
      }
    }

    setUploading(false);
  }

  function removeFile(filename) {
    setUploadedFiles((prev) => prev.filter((f) => f.filename !== filename));
  }

  return (
    <aside className="fade-in-up flex min-h-[320px] flex-col rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-5 shadow-xl backdrop-blur-xl lg:col-span-3 lg:min-h-0">
      <div className="mb-4 border-b border-[#FFE3B3]/25 pb-3">
        <p className="text-xs uppercase tracking-wide text-[#FFE3B3]">Resources</p>
        <h2 className="text-lg font-semibold text-white">Upload files</h2>
        <p className="mt-1 text-sm text-[#E8F7FB]">
          Add notes, slides, or assignments for future AI analysis.
        </p>
      </div>

      <label className={`inline-flex h-24 cursor-pointer items-center justify-center rounded-2xl border border-dashed border-[#FFE3B3]/70 bg-[#FFE3B3]/18 p-4 text-center text-sm text-[#FFF1D5] transition-all duration-300 hover:bg-[#FFE3B3]/28 ${uploading ? "opacity-50 pointer-events-none" : ""}`}>
        <input type="file" multiple className="hidden" onChange={handleFileSelect} disabled={uploading} />
        {uploading ? "Uploading…" : "Click to upload files"}
      </label>

      {error && (
        <p className="mt-2 rounded-xl bg-red-500/20 p-2 text-xs text-red-300">{error}</p>
      )}
      {success && !error && (
        <p className="mt-2 rounded-xl bg-green-500/20 p-2 text-xs text-green-300">{success}</p>
      )}

      <div className="mt-4 flex-1 space-y-2 overflow-y-auto pr-1 lg:min-h-0">
        {uploadedFiles.length === 0 ? (
          <p className="rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#D7EEF8]">
            No files uploaded yet.
          </p>
        ) : (
          uploadedFiles.map((file) => (
            <div
              key={file.filename}
              className="flex items-center justify-between rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#EAF9FD]"
            >
              <div className="min-w-0">
                <p className="truncate font-medium">{file.filename}</p>
                <p className="text-xs text-[#c8e8f3]">
                  {formatFileSize(file.size)} · {file.type || "unknown type"}
                </p>
              </div>
              <button
                onClick={() => removeFile(file.filename)}
                className="ml-2 flex-shrink-0 rounded-lg bg-red-500/20 px-2 py-1 text-xs text-red-300 hover:bg-red-500/40"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default FileUploadPanel;
