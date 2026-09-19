import React from "react";

export const AssessmentsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="p-4 rounded pixel-panel border-l-4 border-l-amber-500">
        <h2 className="text-sm font-pixel-heading text-amber-400 mb-1">
           Shrine of Mastery & Examination Dojo
        </h2>
        <p className="text-xs font-pixel-mono text-slate-300">
          Targeted quizzes, diagnostic exams, and evidence reliability tracking.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="p-4 rounded pixel-panel border border-slate-700 hover:border-amber-500 transition-all flex flex-col justify-between">
          <div>
            <div className="text-xs font-pixel-heading text-emerald-400 mb-1">
              ⚡ QUICK DIAGNOSTIC
            </div>
            <h3 className="text-sm font-semibold text-slate-200 mb-2">
              Python Event Loop & Async Tasks
            </h3>
            <p className="text-xs font-pixel-mono text-slate-400 mb-4">
              5 targeted questions to verify current mastery and detect hidden misconceptions.
            </p>
          </div>
          <button className="pixel-button pixel-button-primary text-xs w-full">
            START QUIZ (5 mins)
          </button>
        </div>

        <div className="p-4 rounded pixel-panel border border-slate-700 hover:border-amber-500 transition-all flex flex-col justify-between">
          <div>
            <div className="text-xs font-pixel-heading text-sky-400 mb-1">
              🔍 MISCONCEPTION PROBE
            </div>
            <h3 className="text-sm font-semibold text-slate-200 mb-2">
              Memory Management & Pointers
            </h3>
            <p className="text-xs font-pixel-mono text-slate-400 mb-4">
              Diagnostic test specifically designed to detect reference counting misunderstandings.
            </p>
          </div>
          <button className="pixel-button text-xs w-full">
            RUN DIAGNOSTIC
          </button>
        </div>

        <div className="p-4 rounded pixel-panel border border-slate-700 hover:border-amber-500 transition-all flex flex-col justify-between">
          <div>
            <div className="text-xs font-pixel-heading text-purple-400 mb-1">
              🏆 FULL EXAM SESSION
            </div>
            <h3 className="text-sm font-semibold text-slate-200 mb-2">
              Comprehensive Systems Exam
            </h3>
            <p className="text-xs font-pixel-mono text-slate-400 mb-4">
              Multi-concept exam covering algorithms, data structures, and memory models.
            </p>
          </div>
          <button className="pixel-button text-xs w-full">
            GENERATE EXAM
          </button>
        </div>
      </div>
    </div>
  );
};
