import { useState } from "react";

function formatFileSize(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileUploadPanel() {
  const [files, setFiles] = useState([]);

  function handleFileSelect(event) {
    const selectedFiles = Array.from(event.target.files ?? []);
    setFiles((prev) => [...prev, ...selectedFiles]);
    event.target.value = "";
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

      <label className="inline-flex h-24 cursor-pointer items-center justify-center rounded-2xl border border-dashed border-[#FFE3B3]/70 bg-[#FFE3B3]/18 p-4 text-center text-sm text-[#FFF1D5] transition-all duration-300 hover:bg-[#FFE3B3]/28">
        <input type="file" multiple className="hidden" onChange={handleFileSelect} />
        Click to upload files
      </label>

      <div className="mt-4 flex-1 space-y-2 overflow-y-auto pr-1 lg:min-h-0">
        {files.length === 0 ? (
          <p className="rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#D7EEF8]">
            No files uploaded yet.
          </p>
        ) : (
          files.map((file, index) => (
            <div
              key={`${file.name}-${file.size}-${index}`}
              className="rounded-xl bg-[#26648E]/55 p-3 text-sm text-[#EAF9FD]"
            >
              <p className="truncate font-medium">{file.name}</p>
              <p className="text-xs text-[#c8e8f3]">{formatFileSize(file.size)}</p>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default FileUploadPanel;
