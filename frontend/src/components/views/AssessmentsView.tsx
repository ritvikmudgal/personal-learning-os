import React from "react";
import {
  AssessmentIcon,
  BrainIcon,
  ChevronRightIcon,
  SparklesIcon,
} from "../WorldIcons";

export const AssessmentsView: React.FC = () => {
  const assessments = [
    {
      type: "Quick Diagnostic",
      typeBadge: "world-badge-ok",
      title: "Python Event Loop & Async Tasks",
      description: "5 targeted questions to verify current mastery and detect hidden misconceptions.",
      duration: "5 mins",
      icon: <BrainIcon size={20} className="text-emerald-700" />,
    },
    {
      type: "Misconception Probe",
      typeBadge: "world-badge-info",
      title: "Memory Management & Pointers",
      description: "Diagnostic test specifically designed to detect reference counting misunderstandings.",
      duration: "10 mins",
      icon: <SparklesIcon size={20} className="text-sky-700" />,
    },
    {
      type: "Full Exam Session",
      typeBadge: "world-badge-warning",
      title: "Comprehensive Systems Exam",
      description: "Multi-concept exam covering algorithms, data structures, and memory models.",
      duration: "30 mins",
      icon: <AssessmentIcon size={20} className="text-amber-800" />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="world-panel p-5 bg-gradient-to-r from-orange-50/90 via-amber-50/40 to-orange-50/90 border-l-4 border-l-amber-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-900 mb-1">
            <AssessmentIcon size={20} />
            <h2 className="text-base font-heading font-bold text-slate-900">
              Assessment Pavilion • Diagnostic Checkpoint
            </h2>
          </div>
          <p className="text-xs text-slate-600 font-body max-w-xl">
            Evaluate topic comprehension through quiet, focused diagnostic checks and adaptive practice exercises.
          </p>
        </div>
      </div>

      {/* Assessment Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {assessments.map((item, idx) => (
          <div
            key={idx}
            className="world-panel p-5 bg-white hover:border-amber-600 hover:-translate-y-0.5 transition-all duration-150 flex flex-col justify-between gap-4 group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-amber-50 group-hover:bg-amber-100 transition-colors">
                  {item.icon}
                </div>
                <span className={`world-badge ${item.typeBadge} text-[11px]`}>
                  {item.type}
                </span>
              </div>

              <h3 className="text-base font-heading font-semibold text-slate-900 mb-1.5">
                {item.title}
              </h3>

              <p className="text-xs text-slate-600 font-body leading-relaxed">
                {item.description}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-400 font-body">
                ⏱️ Est. {item.duration}
              </span>
              <button className="world-button world-button-primary text-xs px-3 py-1.5 shadow-xs">
                <span>Start Quiz</span>
                <ChevronRightIcon size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
