import React from "react";
import { NavTab } from "../PixelEnvironment";
import {
  StudyIcon,
  LibraryIcon,
  KnowledgeIcon,
  AssessmentIcon,
  NotesIcon,
  LearnerIcon,
  SparklesIcon,
  TrendingUpIcon,
  BookOpenIcon,
} from "../WorldIcons";

interface HomeViewProps {
  onNavigate: (tab: NavTab) => void;
}

export const HomeView: React.FC<HomeViewProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Welcome Sanctuary Header */}
      <div className="world-panel p-6 bg-gradient-to-r from-amber-50/80 via-emerald-50/40 to-amber-50/80 border-l-4 border-l-emerald-700 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-800 mb-1">
            <SparklesIcon size={18} />
            <span className="font-heading font-semibold text-xs tracking-wider uppercase">
              Personal Desktop Learning Sanctuary
            </span>
          </div>
          <h1 className="text-xl font-heading font-bold text-slate-900">
            Welcome to Your Personal Learning World
          </h1>
          <p className="text-sm text-slate-600 font-body max-w-xl mt-1">
            A quiet, reflective digital space built for deep comprehension, structured recall, and knowledge growth.
          </p>
        </div>
        <button
          onClick={() => onNavigate("learn")}
          className="world-button world-button-primary px-5 py-2.5 shadow-sm hover:shadow"
        >
          <StudyIcon size={18} />
          <span>Begin Guided Study Session</span>
        </button>
      </div>

      {/* Daily Focus & Core Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Daily Target */}
        <div className="world-panel p-5 bg-white">
          <div className="flex items-center gap-2 text-amber-700 text-xs font-heading font-semibold tracking-wider uppercase mb-2">
            <TrendingUpIcon size={16} />
            <span>Daily Focus Target</span>
          </div>
          <div className="text-base font-heading font-semibold text-slate-800 mb-3">
            Python Asynchronous Traversal
          </div>
          <div className="w-full h-2 bg-amber-100/80 rounded-full overflow-hidden mb-2">
            <div className="w-2/3 h-full bg-amber-600 rounded-full" />
          </div>
          <div className="flex justify-between text-xs text-slate-500 font-body">
            <span>Progress: 65%</span>
            <span>Target: 45 mins</span>
          </div>
        </div>

        {/* Concept Graph State */}
        <div className="world-panel p-5 bg-white">
          <div className="flex items-center gap-2 text-emerald-700 text-xs font-heading font-semibold tracking-wider uppercase mb-2">
            <KnowledgeIcon size={16} />
            <span>Concept Graph State</span>
          </div>
          <div className="text-2xl font-heading font-bold text-slate-900 mb-1">
            42 <span className="text-xs font-normal text-slate-500">Concepts Linked</span>
          </div>
          <p className="text-xs text-slate-500 font-body">
            DFS / BFS Traversal Engine Active • Cycle Detection Ready
          </p>
        </div>

        {/* Learner Model */}
        <div className="world-panel p-5 bg-white">
          <div className="flex items-center gap-2 text-sky-700 text-xs font-heading font-semibold tracking-wider uppercase mb-2">
            <LearnerIcon size={16} />
            <span>Learner Knowledge State</span>
          </div>
          <div className="text-2xl font-heading font-bold text-slate-900 mb-1">
            6 <span className="text-xs font-normal text-slate-500">Active Dimensions</span>
          </div>
          <p className="text-xs text-slate-500 font-body">
            Mastery, Strength, Decay, Confidence, Reliability, Misconceptions
          </p>
        </div>
      </div>

      {/* World Destinations Grid */}
      <div>
        <h2 className="text-base font-heading font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <BookOpenIcon size={18} className="text-emerald-700" />
          <span>World Destinations & Learning Modules</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Study Cottage */}
          <div
            onClick={() => onNavigate("learn")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-emerald-600 hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-100/70 text-emerald-800 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <StudyIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-emerald-800 transition-colors">
              Study Cottage
            </div>
            <div className="text-xs font-medium text-emerald-700 mb-2">
              Interactive Guided Tutor
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Engage with your local AI study assistant for guided explanations, tailored practice, and conceptual clarity.
            </p>
          </div>

          {/* Library Archive */}
          <div
            onClick={() => onNavigate("library")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-amber-600 hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-100/70 text-amber-800 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <LibraryIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-amber-800 transition-colors">
              Archive Library
            </div>
            <div className="text-xs font-medium text-amber-700 mb-2">
              Document Ingestion & Semantic Vault
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Upload PDFs and markdown notes, run semantic search queries, and view extracted document chunks.
            </p>
          </div>

          {/* Concept Observatory */}
          <div
            onClick={() => onNavigate("knowledge")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-sky-600 hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-sky-100/70 text-sky-800 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <KnowledgeIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-sky-800 transition-colors">
              Concept Observatory
            </div>
            <div className="text-xs font-medium text-sky-700 mb-2">
              Prerequisite DAG & Force Graph
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Visualize prerequisite concept networks, inspect topic nodes, and identify learning gaps.
            </p>
          </div>

          {/* Learner Garden */}
          <div
            onClick={() => onNavigate("learner_state")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-emerald-600 hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-100/70 text-emerald-800 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <LearnerIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-emerald-800 transition-colors">
              Learner Garden
            </div>
            <div className="text-xs font-medium text-emerald-700 mb-2">
              Multi-Dimensional Mastery State
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Monitor memory decay rates, confidence levels, and concept mastery growth over time.
            </p>
          </div>

          {/* Writing Studio */}
          <div
            onClick={() => onNavigate("notes")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-amber-600 hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-100/70 text-amber-800 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <NotesIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-amber-800 transition-colors">
              Writing Studio
            </div>
            <div className="text-xs font-medium text-amber-700 mb-2">
              Learner Notes & Reflection Journal
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Jot down personal study notes, synthesize key learnings, and organize study thoughts.
            </p>
          </div>

          {/* Assessment Pavilion */}
          <div
            onClick={() => onNavigate("assessments")}
            className="world-panel p-5 bg-white cursor-pointer hover:border-terracotta hover:-translate-y-0.5 transition-all duration-150 group"
          >
            <div className="w-10 h-10 rounded-xl bg-orange-100/70 text-amber-900 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <AssessmentIcon size={22} />
            </div>
            <div className="text-base font-heading font-semibold text-slate-900 mb-1 group-hover:text-amber-900 transition-colors">
              Assessment Pavilion
            </div>
            <div className="text-xs font-medium text-amber-800 mb-2">
              Mastery Diagnostics & Practice
            </div>
            <p className="text-xs text-slate-600 font-body leading-relaxed">
              Evaluate topic comprehension through quiet, focused diagnostic checks and practice exercises.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
