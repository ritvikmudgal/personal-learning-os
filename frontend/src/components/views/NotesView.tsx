import React, { useState } from "react";

export const NotesView: React.FC = () => {
  const [notes] = useState([
    {
      id: "1",
      title: "Understanding Async IO Event Loops",
      date: "2026-09-19",
      tags: ["python", "concurrency"],
      content:
        "The event loop manages execution of asynchronous tasks using single-threaded non-blocking IO...",
    },
    {
      id: "2",
      title: "Memory Allocation & Garbage Collection",
      date: "2026-09-18",
      tags: ["systems", "memory"],
      content:
        "Reference counting handles immediate deallocation while cyclical garbage collection handles circular references...",
    },
  ]);

  const [activeNote, setActiveNote] = useState(notes[0]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
      {/* Notes List Sidebar */}
      <div className="p-3 rounded pixel-panel space-y-2 border-r border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-pixel-heading text-emerald-400">
            📓 NOTES ({notes.length})
          </span>
          <button className="pixel-button text-[10px] py-0.5 px-2">
            + NEW NOTE
          </button>
        </div>

        {notes.map((note) => (
          <div
            key={note.id}
            onClick={() => setActiveNote(note)}
            className={`p-2.5 rounded cursor-pointer transition-all border ${
              activeNote.id === note.id
                ? "bg-emerald-950/80 border-emerald-500 text-emerald-100"
                : "bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <div className="font-semibold text-xs mb-1">{note.title}</div>
            <div className="text-[10px] font-pixel-mono text-slate-400 flex items-center justify-between">
              <span>{note.date}</span>
              <span className="text-amber-300">{note.tags.map((t) => `#${t}`).join(" ")}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Editor Main Content Pane */}
      <div className="md:col-span-2 p-4 rounded pixel-panel flex flex-col space-y-3">
        <input
          type="text"
          value={activeNote.title}
          readOnly
          className="text-base font-pixel-heading text-amber-300 bg-transparent border-b border-slate-700 pb-2 focus:outline-none"
        />
        <div className="flex items-center gap-2 text-xs font-pixel-mono text-slate-400">
          <span>Date: {activeNote.date}</span>
          <span>•</span>
          <span>Tags: {activeNote.tags.join(", ")}</span>
        </div>
        <textarea
          value={activeNote.content}
          readOnly
          rows={12}
          className="flex-1 w-full bg-slate-900 p-3 rounded text-xs font-mono text-slate-200 border border-slate-800 focus:outline-none resize-none"
        />
      </div>
    </div>
  );
};
