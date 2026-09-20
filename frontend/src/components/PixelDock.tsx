import React, { useState } from "react";
import { NavTab } from "./PixelEnvironment";
import {
  HomeIcon,
  StudyIcon,
  LibraryIcon,
  KnowledgeIcon,
  AssessmentIcon,
  NotesIcon,
  LearnerIcon,
  BrainIcon,
  CloseIcon,
} from "./WorldIcons";

export interface SystemStatus {
  backend: { level: "loading" | "ok" | "warning" | "error"; message: string };
  ollama: { level: "loading" | "ok" | "warning" | "error"; message: string; model?: string };
  llm: { level: "loading" | "ok" | "warning" | "error"; message: string };
}

interface PixelDockProps {
  activeTab: NavTab | null;
  onSelectTab: (tab: NavTab) => void;
  status: SystemStatus;
}

const NAV_ITEMS: { id: NavTab; label: string; icon: React.ReactNode }[] = [
  { id: "home", label: "World Home", icon: <HomeIcon size={20} /> },
  { id: "learn", label: "Study Cottage", icon: <StudyIcon size={20} /> },
  { id: "library", label: "Archive Library", icon: <LibraryIcon size={20} /> },
  { id: "knowledge", label: "Observatory", icon: <KnowledgeIcon size={20} /> },
  { id: "learner_state", label: "Learner Garden", icon: <LearnerIcon size={20} /> },
  { id: "notes", label: "Writing Studio", icon: <NotesIcon size={20} /> },
  { id: "assessments", label: "Assessments", icon: <AssessmentIcon size={20} /> },
];

export const PixelDock: React.FC<PixelDockProps> = ({
  activeTab,
  onSelectTab,
  status,
}) => {
  const [showStatusModal, setShowStatusModal] = useState(false);

  const getStatusColor = (level: string) => {
    switch (level) {
      case "ok":
        return "#528663";
      case "warning":
        return "#d49f42";
      case "error":
        return "#b85b40";
      default:
        return "#d49f42";
    }
  };

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-40 flex flex-col items-center select-none">
      {/* System Status Inspector Modal */}
      {showStatusModal && (
        <div className="mb-3 p-5 rounded-xl w-80 shadow-2xl animate-fade-in bg-slate-900/95 text-amber-50 border border-slate-700/80 backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-700/80 pb-3 mb-3">
            <div className="flex items-center gap-2">
              <BrainIcon size={18} className="text-emerald-400" />
              <span className="font-heading font-semibold text-sm text-emerald-300">
                System Engine Status
              </span>
            </div>
            <button
              onClick={() => setShowStatusModal(false)}
              className="p-1 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            >
              <CloseIcon size={16} />
            </button>
          </div>
          <div className="space-y-3 font-body text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Backend API</span>
              <span className="font-semibold text-emerald-400">
                {status.backend.message}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Local AI (Ollama)</span>
              <span className="font-semibold text-amber-300">
                {status.ollama.model || status.ollama.message}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Tutor Router</span>
              <span className="font-semibold text-slate-300">
                {status.llm.message}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Desktop Application Launcher Shelf */}
      <div
        className="flex items-center gap-1.5 px-3 py-2 rounded-2xl shadow-2xl transition-all duration-200"
        style={{
          backgroundColor: "rgba(34, 26, 21, 0.88)",
          backdropFilter: "blur(12px)",
          border: "1px solid rgba(228, 218, 202, 0.2)",
          boxShadow: "0 12px 36px rgba(18, 14, 10, 0.4), 0 2px 6px rgba(0,0,0,0.2)",
        }}
      >
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id || (item.id === "home" && activeTab === null);

          return (
            <div key={item.id} className="relative group">
              <button
                onClick={() => onSelectTab(item.id)}
                className={`relative flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-amber-100/15 text-amber-200 shadow-inner scale-105"
                    : "text-amber-100/70 hover:text-white hover:bg-white/10 hover:scale-105"
                }`}
                title={item.label}
              >
                {item.icon}

                {/* Active Indicator Dot */}
                {isActive && (
                  <span className="absolute -bottom-1 w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399]" />
                )}
              </button>

              {/* Hover Label Tooltip */}
              <div className="absolute -top-9 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-nowrap px-2.5 py-1 text-[11px] font-heading font-medium bg-slate-900/90 text-amber-100 rounded-md border border-slate-700/80 shadow-lg">
                {item.label}
              </div>
            </div>
          );
        })}

        <div className="h-6 w-[1px] mx-1 bg-white/15" />

        {/* Engine Status Pill */}
        <button
          onClick={() => setShowStatusModal(!showStatusModal)}
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-body text-amber-100/80 hover:text-white hover:bg-white/10 transition-all duration-150"
          title="Inspect AI Engine & Server Status"
        >
          <span
            className="w-2.5 h-2.5 rounded-full animate-pulse"
            style={{ backgroundColor: getStatusColor(status.backend.level) }}
          />
          <span className="hidden lg:inline font-medium">
            {status.ollama.model ? `qwen2.5:3b` : `Engine`}
          </span>
        </button>
      </div>
    </div>
  );
};
