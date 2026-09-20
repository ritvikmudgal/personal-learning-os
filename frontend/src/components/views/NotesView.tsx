import React, { useState } from "react";
import {
  NotesIcon,
  PlusIcon,
  SparklesIcon,
} from "../WorldIcons";

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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 min-h-[420px]">
      {/* Sidebar: Notes Navigation */}
      <div className="world-panel p-4 bg-white space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-800">
            <NotesIcon size={18} className="text-amber-800" />
            <span className="font-heading font-bold text-sm">
              Writing Studio ({notes.length})
            </span>
          </div>
          <button className="world-button text-xs py-1.5 px-3">
            <PlusIcon size={14} />
            <span>New Note</span>
          </button>
        </div>

        <div className="space-y-2">
          {notes.map((note) => {
            const isSelected = activeNote.id === note.id;

            return (
              <div
                key={note.id}
                onClick={() => setActiveNote(note)}
                className={`p-3.5 rounded-xl cursor-pointer transition-all duration-150 border ${
                  isSelected
                    ? "bg-amber-50/80 border-amber-600 shadow-xs"
                    : "bg-slate-50/50 border-slate-200 hover:border-slate-300"
                }`}
              >
                <h4 className="text-xs font-heading font-semibold text-slate-900 mb-1">
                  {note.title}
                </h4>
                <div className="flex items-center justify-between text-[11px] text-slate-400 font-body">
                  <span>{note.date}</span>
                  <div className="flex gap-1">
                    {note.tags.map((t) => (
                      <span key={t} className="px-1.5 py-0.5 rounded bg-amber-100/70 text-amber-900 font-medium">
                        #{t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Editor Main Canvas */}
      <div className="md:col-span-2 world-panel p-6 bg-white border-l-4 border-l-amber-700 flex flex-col justify-between">
        <div className="space-y-4">
          <div className="flex items-start justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-lg font-heading font-bold text-slate-900">
                {activeNote.title}
              </h3>
              <p className="text-xs text-slate-400 font-body">
                Last modified: {activeNote.date}
              </p>
            </div>
            <div className="flex gap-1.5">
              {activeNote.tags.map((t) => (
                <span key={t} className="world-badge world-badge-neutral text-xs">
                  #{t}
                </span>
              ))}
            </div>
          </div>

          <div className="prose prose-slate max-w-none text-sm text-slate-700 font-body leading-relaxed whitespace-pre-wrap p-4 bg-amber-50/40 rounded-xl border border-amber-100">
            {activeNote.content}
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400 font-body">
          <span>Writing Studio • Auto-saved locally</span>
          <span className="text-emerald-700 font-medium flex items-center gap-1">
            <SparklesIcon size={14} /> Linked to Concept Graph
          </span>
        </div>
      </div>
    </div>
  );
};
