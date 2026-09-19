import React from "react";

export const LibraryView: React.FC = () => {
  const resources = [
    { name: "Fluent Python 2nd Edition.pdf", type: "PDF Book", size: "14.2 MB", added: "2026-09-15" },
    { name: "Asyncio Official Documentation.md", type: "Doc Reference", size: "1.8 MB", added: "2026-09-17" },
    { name: "Memory Models & CPython Internals.pdf", type: "Paper", size: "4.5 MB", added: "2026-09-18" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-3 rounded pixel-panel">
        <div>
          <h2 className="text-sm font-pixel-heading text-purple-400">
            📚 Archive Library & Reference Vault
          </h2>
          <p className="text-xs font-pixel-mono text-slate-300">
            Local reference collection for guided extraction and AI retrieval.
          </p>
        </div>
        <button className="pixel-button pixel-button-primary text-xs">
          + IMPORT FILE
        </button>
      </div>

      <div className="space-y-2">
        {resources.map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded pixel-panel flex items-center justify-between hover:border-purple-500 transition-all border border-slate-800"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">📄</span>
              <div>
                <div className="text-xs font-semibold text-slate-200">
                  {item.name}
                </div>
                <div className="text-[11px] font-pixel-mono text-slate-400">
                  {item.type} • {item.size} • Added: {item.added}
                </div>
              </div>
            </div>

            <button className="pixel-button text-xs py-1 px-3">
              INSPECT
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
