import React, { useState } from "react";
import { NavTab } from "./PixelEnvironment";

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

const NAV_ITEMS: { id: NavTab; label: string; icon: string }[] = [
  { id: "home", label: "Home", icon: "🏠" },
  { id: "learn", label: "Learn", icon: "💬" },
  { id: "knowledge", label: "Graph", icon: "🕸️" },
  { id: "assessments", label: "Assess", icon: "📝" },
  { id: "notes", label: "Notes", icon: "📓" },
  { id: "library", label: "Library", icon: "📚" },
  { id: "learner_state", label: "State", icon: "📊" },
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
        return "#70b37b"; // Moss Green
      case "warning":
        return "#e3b067"; // Amber
      case "error":
        return "#d96b6b"; // Soft Coral Red
      default:
        return "#d4a373"; // Loading Gold
    }
  };

  return (
    <div className="fixed bottom-3 left-1/2 transform -translate-x-1/2 z-40 flex flex-col items-center">
      {/* Subtle Status Modal Popover */}
      {showStatusModal && (
        <div
          className="mb-3 p-4 rounded pixel-window text-xs font-pixel-mono w-80 shadow-2xl animate-fade-in"
          style={{ backgroundColor: "var(--window-header)" }}
        >
          <div className="flex items-center justify-between border-b pb-2 mb-2 border-emerald-900/60">
            <span className="font-pixel-heading text-emerald-400">
              ⚡ SYSTEM DIAGNOSTICS
            </span>
            <button
              onClick={() => setShowStatusModal(false)}
              className="text-slate-400 hover:text-white"
            >
              ✖
            </button>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Backend Core Engine:</span>
              <span style={{ color: getStatusColor(status.backend.level) }}>
                {status.backend.message}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Ollama Local AI:</span>
              <span style={{ color: getStatusColor(status.ollama.level) }}>
                {status.ollama.model || status.ollama.message}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">LLM Provider Fallback:</span>
              <span style={{ color: getStatusColor(status.llm.level) }}>
                {status.llm.message}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Bottom Dock Bar */}
      <div
        className="flex items-center gap-1 sm:gap-2 px-3 py-2 rounded-lg shadow-2xl border-2"
        style={{
          backgroundColor: "var(--window-header)",
          borderColor: "var(--window-border)",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
        }}
      >
        {/* World Icon */}
        <button
          onClick={() => onSelectTab("home")}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded transition-all text-xs font-pixel-heading ${
            activeTab === null
              ? "bg-emerald-900/80 text-emerald-200 border border-emerald-500/50"
              : "text-slate-300 hover:bg-slate-800"
          }`}
          title="Return to World View"
        >
          <span>🌍</span>
          <span className="hidden md:inline">World</span>
        </button>

        <div className="h-5 w-[1px] bg-slate-700/60 mx-0.5" />

        {/* Application Dock Buttons */}
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded transition-all text-xs font-pixel-heading ${
                isActive
                  ? "bg-emerald-700 text-white border border-emerald-400 shadow"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <span>{item.icon}</span>
              <span className="hidden sm:inline">{item.label}</span>
            </button>
          );
        })}

        <div className="h-5 w-[1px] bg-slate-700/60 mx-0.5" />

        {/* Diegetic System Status Pill */}
        <button
          onClick={() => setShowStatusModal(!showStatusModal)}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-pixel-mono hover:bg-slate-800 transition-colors"
          title="Click to inspect system status"
        >
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: getStatusColor(status.backend.level) }}
          />
          <span className="text-slate-300 hidden lg:inline">
            {status.ollama.model ? `qwen2.5:3b` : `Engine`}
          </span>
        </button>
      </div>
    </div>
  );
};
