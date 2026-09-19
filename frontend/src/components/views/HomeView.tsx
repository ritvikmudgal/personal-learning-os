import React from "react";
import { NavTab } from "../PixelEnvironment";

interface HomeViewProps {
  onNavigate: (tab: NavTab) => void;
}

export const HomeView: React.FC<HomeViewProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Welcome Sanctuary Header */}
      <div className="p-5 rounded pixel-panel border-l-4 border-l-emerald-500 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-pixel-heading text-emerald-400 mb-1">
            Welcome to Your Personal Learning Sanctuary
          </h1>
          <p className="text-xs font-pixel-mono text-slate-300">
            A quiet digital world built for focused, deep comprehension.
          </p>
        </div>
        <button
          onClick={() => onNavigate("learn")}
          className="pixel-button pixel-button-primary whitespace-nowrap text-xs"
        >
          💬 Begin Guided Study Session
        </button>
      </div>

      {/* Daily Target & Core Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded pixel-panel border border-emerald-900/50">
          <div className="text-xs font-pixel-heading text-amber-400 mb-1">
            🎯 DAILY FOCUS TARGET
          </div>
          <div className="text-sm font-semibold text-slate-200 mb-2">
            Python Asynchronous Traversal
          </div>
          <div className="w-full bg-slate-800 rounded h-2 overflow-hidden mb-2">
            <div className="bg-amber-400 h-full w-2/3" />
          </div>
          <div className="text-[11px] font-pixel-mono text-slate-400 flex justify-between">
            <span>Progress: 65%</span>
            <span>Target: 45 mins</span>
          </div>
        </div>

        <div className="p-4 rounded pixel-panel border border-emerald-900/50">
          <div className="text-xs font-pixel-heading text-emerald-400 mb-1">
            🕸️ CONCEPT GRAPH STATE
          </div>
          <div className="text-2xl font-pixel-heading text-slate-100 mb-1">
            42 <span className="text-xs font-normal text-slate-400">Concepts</span>
          </div>
          <div className="text-[11px] font-pixel-mono text-slate-400">
            DFS / BFS Traversal Engine Active • Cycle Detection Ready
          </div>
        </div>

        <div className="p-4 rounded pixel-panel border border-emerald-900/50">
          <div className="text-xs font-pixel-heading text-sky-400 mb-1">
            📊 LEARNER MODEL
          </div>
          <div className="text-2xl font-pixel-heading text-slate-100 mb-1">
            6 <span className="text-xs font-normal text-slate-400">Dimensions</span>
          </div>
          <div className="text-[11px] font-pixel-mono text-slate-400">
            Mastery, Strength, Decay, Confidence, Reliability, Misconceptions
          </div>
        </div>
      </div>

      {/* World Locations Map */}
      <div>
        <h2 className="text-sm font-pixel-heading text-slate-200 mb-3">
          🏞️ WORLD LOCATIONS & MODULES
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            onClick={() => onNavigate("learn")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              💬 Study Cottage
            </div>
            <div className="text-xs font-pixel-heading text-emerald-400 mb-1">
              Learn / Chat
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Talk with your local AI study assistant for guided concept explanations.
            </p>
          </div>

          <div
            onClick={() => onNavigate("knowledge")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              🕸️ Concept Observatory
            </div>
            <div className="text-xs font-pixel-heading text-sky-400 mb-1">
              Knowledge Graph
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Explore prerequisite concept relationships and knowledge trees.
            </p>
          </div>

          <div
            onClick={() => onNavigate("assessments")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              📝 Shrine of Mastery
            </div>
            <div className="text-xs font-pixel-heading text-amber-400 mb-1">
              Assessments
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Test your understanding with targeted quizzes and exams.
            </p>
          </div>

          <div
            onClick={() => onNavigate("notes")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              📓 Writing Gazebo
            </div>
            <div className="text-xs font-pixel-heading text-emerald-300 mb-1">
              Learner Notes
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Record reflections, code snippets, and study journal entries.
            </p>
          </div>

          <div
            onClick={() => onNavigate("library")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              📚 Archive Library
            </div>
            <div className="text-xs font-pixel-heading text-purple-400 mb-1">
              Reference Library
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Store and reference textbook PDFs, documentation, and articles.
            </p>
          </div>

          <div
            onClick={() => onNavigate("learner_state")}
            className="p-4 rounded pixel-panel hover:border-emerald-500 cursor-pointer transition-all group"
          >
            <div className="text-lg mb-1 group-hover:scale-110 transition-transform origin-left">
              📊 Crystal Monolith
            </div>
            <div className="text-xs font-pixel-heading text-teal-300 mb-1">
              Learner State
            </div>
            <p className="text-xs font-pixel-mono text-slate-400">
              Track multi-dimensional knowledge retention, decay, and confidence.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
