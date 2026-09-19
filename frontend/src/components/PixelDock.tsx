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
  { id: "learner_state", label: "State", icon: "🌱" },
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
        return "var(--status-ok)";
      case "warning":
        return "var(--accent-amber)";
      case "error":
        return "var(--accent-coral)";
      default:
        return "var(--accent-amber-light)";
    }
  };

  return (
    <div className="fixed bottom-3 left-1/2 transform -translate-x-1/2 z-40 flex flex-col items-center">
      {/* Status Modal Popover */}
      {showStatusModal && (
        <div
          className="mb-3 p-5 rounded-lg text-sm w-80 shadow-2xl animate-fade-in"
          style={{
            backgroundColor: "var(--window-bg)",
            border: "2px solid var(--window-border)",
            boxShadow: "0 8px 32px rgba(92, 61, 46, 0.2)",
          }}
        >
          <div className="flex items-center justify-between border-b pb-3 mb-3" style={{ borderColor: "var(--window-border-light)" }}>
            <span className="font-pixel-heading text-sm" style={{ color: "var(--accent-moss)" }}>
              System Status
            </span>
            <button
              onClick={() => setShowStatusModal(false)}
              className="text-sm hover:opacity-70 transition-opacity"
              style={{ color: "var(--window-text-muted)" }}
            >
              ✕
            </button>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: "var(--window-text-secondary)" }}>Backend Engine</span>
              <span className="font-pixel-heading text-xs" style={{ color: getStatusColor(status.backend.level) }}>
                {status.backend.message}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: "var(--window-text-secondary)" }}>Ollama AI</span>
              <span className="font-pixel-heading text-xs" style={{ color: getStatusColor(status.ollama.level) }}>
                {status.ollama.model || status.ollama.message}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: "var(--window-text-secondary)" }}>LLM Provider</span>
              <span className="font-pixel-heading text-xs" style={{ color: getStatusColor(status.llm.level) }}>
                {status.llm.message}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Bottom Dock Bar */}
      <div
        className="flex items-center gap-1 sm:gap-1.5 px-3 py-2 rounded-xl shadow-2xl"
        style={{
          backgroundColor: "rgba(92, 61, 46, 0.92)",
          backdropFilter: "blur(8px)",
          border: "2px solid var(--earth-light)",
          boxShadow: "0 4px 24px rgba(64, 46, 35, 0.35), 0 1px 3px rgba(0,0,0,0.15)",
        }}
      >
        {/* World Button */}
        <button
          onClick={() => onSelectTab("home")}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg transition-all text-xs font-pixel-heading"
          style={{
            backgroundColor: activeTab === null ? "rgba(255,255,255,0.15)" : "transparent",
            color: "#f5efe4",
          }}
          onMouseEnter={(e) => {
            if (activeTab !== null) e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.08)";
          }}
          onMouseLeave={(e) => {
            if (activeTab !== null) e.currentTarget.style.backgroundColor = "transparent";
          }}
          title="Return to World View"
        >
          <span>🌍</span>
          <span className="hidden md:inline">World</span>
        </button>

        <div className="h-5 w-[1px] mx-0.5" style={{ backgroundColor: "rgba(255,255,255,0.15)" }} />

        {/* Application Dock Buttons */}
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg transition-all text-xs font-pixel-heading"
              style={{
                backgroundColor: isActive ? "rgba(255,255,255,0.2)" : "transparent",
                color: isActive ? "#ffffff" : "#d4c4a8",
                boxShadow: isActive ? "0 1px 4px rgba(0,0,0,0.2)" : "none",
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.08)";
                  e.currentTarget.style.color = "#ffffff";
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = "transparent";
                  e.currentTarget.style.color = "#d4c4a8";
                }
              }}
            >
              <span>{item.icon}</span>
              <span className="hidden sm:inline">{item.label}</span>
            </button>
          );
        })}

        <div className="h-5 w-[1px] mx-0.5" style={{ backgroundColor: "rgba(255,255,255,0.15)" }} />

        {/* System Status Pill */}
        <button
          onClick={() => setShowStatusModal(!showStatusModal)}
          className="flex items-center gap-1.5 px-2.5 py-2 rounded-lg text-xs font-pixel-mono transition-all"
          style={{ color: "#d4c4a8" }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.08)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
          title="Click to inspect system status"
        >
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: getStatusColor(status.backend.level) }}
          />
          <span className="hidden lg:inline">
            {status.ollama.model ? `qwen2.5:3b` : `Engine`}
          </span>
        </button>
      </div>
    </div>
  );
};
