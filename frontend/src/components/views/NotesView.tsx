import React, { useState } from "react";

export const NotesView: React.FC = () => {
  const [notes] = useState([
    {
      id: "1",
      title: "Understanding Async IO Event Loops",
      date: "2026-09-19",
      tags: ["python", "concurrency"],
      content:
        "The event loop manages execution of asynchronous tasks using single-threaded non-blocking IO. It monitors multiple IO operations and dispatches callbacks when operations complete, enabling efficient concurrent programming without true parallelism.",
    },
    {
      id: "2",
      title: "Memory Allocation & Garbage Collection",
      date: "2026-09-18",
      tags: ["systems", "memory"],
      content:
        "Reference counting handles immediate deallocation while cyclical garbage collection handles circular references. Python uses a generational garbage collector with three generations, where objects that survive collection cycles are promoted to older generations.",
    },
  ]);

  const [activeNote, setActiveNote] = useState(notes[0]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 h-full" style={{ minHeight: "420px" }}>
      {/* Notes Sidebar */}
      <div
        className="p-4 rounded-lg space-y-3"
        style={{
          backgroundColor: "var(--window-card)",
          border: "1.5px solid var(--window-border-light)",
        }}
      >
        <div className="flex items-center justify-between mb-1">
          <span
            className="text-sm font-pixel-heading flex items-center gap-2"
            style={{ color: "var(--accent-sage)" }}
          >
            <span>📓</span> Notes ({notes.length})
          </span>
          <button className="pixel-button text-xs py-1.5 px-3">
            + New
          </button>
        </div>

        <div className="space-y-2">
          {notes.map((note) => (
            <div
              key={note.id}
              onClick={() => setActiveNote(note)}
              className="p-3 rounded-lg cursor-pointer transition-all"
              style={{
                backgroundColor:
                  activeNote.id === note.id
                    ? "var(--accent-sage-bg)"
                    : "var(--window-bg)",
                border: `1.5px solid ${
                  activeNote.id === note.id
                    ? "var(--accent-sage)"
                    : "var(--window-border-light)"
                }`,
              }}
              onMouseEnter={(e) => {
                if (activeNote.id !== note.id) e.currentTarget.style.borderColor = "var(--window-border)";
              }}
              onMouseLeave={(e) => {
                if (activeNote.id !== note.id) e.currentTarget.style.borderColor = "var(--window-border-light)";
              }}
            >
              <div
                className="text-sm font-medium mb-1"
                style={{ color: "var(--window-text-primary)" }}
              >
                {note.title}
              </div>
              <div className="flex items-center justify-between text-xs">
                <span style={{ color: "var(--window-text-faint)" }}>
                  {note.date}
                </span>
                <span style={{ color: "var(--accent-amber)" }}>
                  {note.tags.map((t) => `#${t}`).join(" ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Editor Pane — notebook/paper feel */}
      <div
        className="md:col-span-2 p-5 rounded-lg flex flex-col space-y-4"
        style={{
          backgroundColor: "var(--window-bg-subtle)",
          border: "1.5px solid var(--window-border-light)",
          /* Subtle lined-paper effect */
          backgroundImage:
            "repeating-linear-gradient(transparent, transparent 31px, var(--window-border-light) 31px, var(--window-border-light) 32px)",
          backgroundSize: "100% 32px",
          backgroundPositionY: "80px",
        }}
      >
        {/* Title */}
        <input
          type="text"
          value={activeNote.title}
          readOnly
          className="text-lg font-medium bg-transparent pb-2 focus:outline-none"
          style={{
            color: "var(--window-text-primary)",
            borderBottom: "2px solid var(--window-border-light)",
            fontFamily: "var(--font-body)",
          }}
        />

        {/* Metadata */}
        <div className="flex items-center gap-3 text-sm">
          <span style={{ color: "var(--window-text-faint)" }}>
            {activeNote.date}
          </span>
          <span style={{ color: "var(--window-border)" }}>·</span>
          <div className="flex gap-1.5">
            {activeNote.tags.map((tag) => (
              <span
                key={tag}
                className="pixel-badge pixel-badge-neutral"
                style={{ fontSize: "11px" }}
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <textarea
          value={activeNote.content}
          readOnly
          className="flex-1 w-full p-4 rounded-lg text-sm leading-relaxed resize-none focus:outline-none"
          style={{
            backgroundColor: "transparent",
            color: "var(--window-text-primary)",
            border: "none",
            fontFamily: "var(--font-body)",
            lineHeight: "32px",
            minHeight: "240px",
          }}
        />
      </div>
    </div>
  );
};
