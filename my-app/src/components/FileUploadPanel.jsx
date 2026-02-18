import { useEffect, useState } from "react";

const API_BASE_URL = "http://localhost:5000";

function formatFileSize(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileUploadPanel() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  // Load existing files on mount
  useEffect(() => {
    fetchFiles();
  }, []);

  async function fetchFiles() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/files`);
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (err) {
      console.error("Failed to fetch files:", err);
    }
  }

  async function handleFileSelect(event) {
    const selectedFiles = Array.from(event.target.files ?? []);
    event.target.value = "";

    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Upload failed");
        }
      }

      // Refresh file list after upload
      await fetchFiles();
    } catch (err) {
      setError(err.message);
      console.error("Upload error:", err);
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteFile(filename) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/files/${filename}`, {
        method: "DELETE",
      });

      if (response.ok) {
        await fetchFiles();
      }
    } catch (err) {
      console.error("Delete error:", err);
    }
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

      {error && (
        <div className="mb-3 rounded-xl bg-red-500/20 border border-red-400/50 p-3 text-sm text-red-100">
          {error}
        </div>
      )}

      <label className="inline-flex h-24 cursor-pointer items-center justify-center rounded-2xl border border-dashed border-[#FFE3B3]/70 bg-[#FFE3B3]/18 p-4 text-center text-sm text-[#FFF1D5] transition-all duration-300 hover:bg-[#FFE3B3]/28">
        <input 
          type="file" 
          multiple 
          className="hidden" 
          onChange={handleFileSelect}
          disabled={uploading}
        />
        {uploading ? "Uploading..." : "Click to upload files"}
      </label>

      <div className="mt-4 flex-1 space-y-2 overflow-y-auto pr-1 lg:min-h-0">
        {files.length === 0 ? (
          <p className="rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#D7EEF8]">
            No files uploaded yet.
          </p>
        ) : (
          files.map((file, index) => (
            <div
              key={file.filename || `${file.name}-${index}`}
              className="rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#EAF9FD] flex items-start justify-between"
            >
              <div className="flex-1 min-w-0">
                <p className="truncate font-medium">
                  {file.originalName || file.filename || file.name}
                </p>
                <p className="text-xs text-[#c8e8f3]">
                  {formatFileSize(file.size)}
                </p>
              </div>
              <button
                onClick={() => handleDeleteFile(file.filename)}
                className="ml-2 text-[#FFE3B3] hover:text-red-300 transition-colors"
                title="Delete file"
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
