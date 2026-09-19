import React from "react";

export const LearnerStateView: React.FC = () => {
  const stateDimensions = [
    {
      name: "Mastery Probability",
      value: "78%",
      color: "var(--grass-light)",
      desc: "Estimated probability of solving complex problem correctly.",
      icon: "🎯",
    },
    {
      name: "Knowledge Strength",
      value: "8.4 days",
      color: "var(--window-accent-sky)",
      desc: "Memory half-life retention parameter under spaced retrieval.",
      icon: "⚡",
    },
    {
      name: "Forgetting State",
      value: "Low Decay (0.12)",
      color: "var(--window-accent-warm)",
      desc: "Current position on Ebbinghaus forgetting curve.",
      icon: "⏳",
    },
    {
      name: "Confidence Score",
      value: "85%",
      color: "#bbf2c4",
      desc: "Self-assessed metacognitive confidence rating.",
      icon: "🧠",
    },
    {
      name: "Evidence Reliability",
      value: "High (14 quizzes)",
      color: "#a4c6d4",
      desc: "Diagnostic test count & empirical observation density.",
      icon: "📊",
    },
    {
      name: "Misconception Severity",
      value: "None Detected",
      color: "#70b37b",
      desc: "Flagged cognitive traps or faulty mental models.",
      icon: "🛡️",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="p-4 rounded pixel-panel border-l-4 border-l-teal-500">
        <h2 className="text-sm font-pixel-heading text-teal-300 mb-1">
          📊 Multi-Dimensional Learner Knowledge State
        </h2>
        <p className="text-xs font-pixel-mono text-slate-300">
          The persistent 6-dimensional model representing knowledge strength, memory decay, and misconceptions.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stateDimensions.map((dim, idx) => (
          <div
            key={idx}
            className="p-4 rounded pixel-panel border border-slate-800 space-y-2 hover:border-teal-500 transition-all"
          >
            <div className="flex items-center justify-between">
              <span className="text-xl">{dim.icon}</span>
              <span
                className="text-sm font-pixel-heading"
                style={{ color: dim.color }}
              >
                {dim.value}
              </span>
            </div>
            <div className="font-semibold text-xs text-slate-200">
              {dim.name}
            </div>
            <p className="text-[11px] font-pixel-mono text-slate-400">
              {dim.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
