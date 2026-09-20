import React from "react";
import {
  LearnerIcon,
  BrainIcon,
  TrendingUpIcon,
  SparklesIcon,
} from "../WorldIcons";

interface DimensionCard {
  name: string;
  value: string;
  badge: string;
  desc: string;
  icon: React.ReactNode;
  detail: string;
}

export const LearnerStateView: React.FC = () => {
  const stateDimensions: DimensionCard[] = [
    {
      name: "Mastery Probability",
      value: "78%",
      badge: "High Mastery",
      desc: "Estimated probability of solving complex problem tasks correctly.",
      icon: <BrainIcon size={20} className="text-emerald-700" />,
      detail: "Based on Bayesian Knowledge Tracing across 14 diagnostic evaluations.",
    },
    {
      name: "Knowledge Strength",
      value: "8.4 days",
      badge: "Optimal",
      desc: "Memory half-life retention parameter under spaced retrieval.",
      icon: <TrendingUpIcon size={20} className="text-sky-700" />,
      detail: "Represents stability S in the half-life memory model.",
    },
    {
      name: "Forgetting State",
      value: "0.12 (Low Decay)",
      badge: "Stable",
      desc: "Current position on the Ebbinghaus exponential forgetting curve.",
      icon: <SparklesIcon size={20} className="text-amber-700" />,
      detail: "R = e^(-t/S), indicating 88% estimated retrieval likelihood today.",
    },
    {
      name: "Confidence Score",
      value: "85%",
      badge: "Well-Calibrated",
      desc: "Self-assessed metacognitive confidence rating vs actual accuracy.",
      icon: <LearnerIcon size={20} className="text-emerald-700" />,
      detail: "Low overconfidence gap; strong self-awareness detected.",
    },
    {
      name: "Evidence Reliability",
      value: "High (14 evals)",
      badge: "Robust Data",
      desc: "Diagnostic test count & empirical observation density.",
      icon: <TrendingUpIcon size={20} className="text-sky-700" />,
      detail: "Sufficient data density for high-confidence mastery estimation.",
    },
    {
      name: "Misconception Severity",
      value: "None Detected",
      badge: "Clear",
      desc: "Flagged cognitive traps or faulty mental models.",
      icon: <BrainIcon size={20} className="text-emerald-700" />,
      detail: "No systemic error patterns observed in recent assessments.",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="world-panel p-5 bg-gradient-to-r from-emerald-50/90 via-emerald-100/40 to-emerald-50/90 border-l-4 border-l-emerald-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-900 mb-1">
            <LearnerIcon size={20} />
            <h2 className="text-base font-heading font-bold text-slate-900">
              Learner Garden • Knowledge Growth State
            </h2>
          </div>
          <p className="text-xs text-slate-600 font-body max-w-2xl leading-relaxed">
            Understanding is not a flat scalar. Each concept tracks 6 cognitive dimensions to model true comprehension, memory retention half-life, and personalized practice intervals.
          </p>
        </div>
      </div>

      {/* 6 Dimensions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stateDimensions.map((dim, idx) => (
          <div
            key={idx}
            className="world-panel p-5 bg-white hover:border-emerald-600 hover:-translate-y-0.5 transition-all duration-150 flex flex-col justify-between gap-3 group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-emerald-50 group-hover:bg-emerald-100 transition-colors">
                  {dim.icon}
                </div>
                <span className="world-badge world-badge-ok text-[11px]">
                  {dim.badge}
                </span>
              </div>

              <div className="text-2xl font-heading font-bold text-slate-900 mb-0.5">
                {dim.value}
              </div>

              <h4 className="text-sm font-heading font-semibold text-slate-800 mb-1.5">
                {dim.name}
              </h4>

              <p className="text-xs text-slate-600 font-body leading-relaxed">
                {dim.desc}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-body leading-normal">
              {dim.detail}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
