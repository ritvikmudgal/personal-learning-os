import { useState, useEffect, useCallback } from "react";
import { PixelEnvironment, NavTab } from "./components/PixelEnvironment";
import { PixelWindow } from "./components/PixelWindow";
import { PixelDock, SystemStatus } from "./components/PixelDock";

import { HomeView } from "./components/views/HomeView";
import { LearnChatView } from "./components/views/LearnChatView";
import { KnowledgeGraphView } from "./components/views/KnowledgeGraphView";
import { AssessmentsView } from "./components/views/AssessmentsView";
import { NotesView } from "./components/views/NotesView";
import { LibraryView } from "./components/views/LibraryView";
import { LearnerStateView } from "./components/views/LearnerStateView";

const API_BASE = "http://127.0.0.1:8000/api";

const INITIAL_STATUS: SystemStatus = {
  backend: { level: "loading", message: "Checking..." },
  ollama: { level: "loading", message: "Checking..." },
  llm: { level: "loading", message: "Checking..." },
};

const MODULE_META: Record<
  NavTab,
  { title: string; subtitle: string; icon: string }
> = {
  home: {
    title: "Sanctuary Hearth & Overview",
    subtitle: "Personal Learning OS Home & Daily Target",
    icon: "🏠",
  },
  learn: {
    title: "Study Cottage & AI Assistant",
    subtitle: "AI Guided Learning & Conceptual Breakdown",
    icon: "💬",
  },
  knowledge: {
    title: "Concept Graph & Observatory",
    subtitle: "Prerequisite Relationships & Traversal Engine",
    icon: "🕸️",
  },
  assessments: {
    title: "Shrine of Mastery & Examination Dojo",
    subtitle: "Diagnostic Quizzes, Exams & Misconceptions",
    icon: "📝",
  },
  notes: {
    title: "Writing Gazebo & Reflection Journal",
    subtitle: "Learner Reflection Notes & Markdown Journal",
    icon: "📓",
  },
  library: {
    title: "Archive Library & Reference Vault",
    subtitle: "Study Materials, Documents & Reference Files",
    icon: "📚",
  },
  learner_state: {
    title: "Crystal Monolith & Knowledge State",
    subtitle: "Multi-Dimensional Knowledge Tracking & Retention",
    icon: "📊",
  },
};

function App() {
  const [activeTab, setActiveTab] = useState<NavTab | null>("home");
  const [status, setStatus] = useState<SystemStatus>(INITIAL_STATUS);

  const checkStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setStatus((prev) => ({
          ...prev,
          backend: { level: "ok", message: `${data.app} v${data.version}` },
        }));
      } else {
        setStatus((prev) => ({
          ...prev,
          backend: { level: "error", message: `HTTP ${res.status}` },
        }));
      }
    } catch {
      setStatus((prev) => ({
        ...prev,
        backend: { level: "error", message: "Backend Offline" },
      }));
    }

    try {
      const res = await fetch(`${API_BASE}/health/ollama`);
      if (res.ok) {
        const data = await res.json();
        const level = data.status === "available" ? "ok" : "warning";
        setStatus((prev) => ({
          ...prev,
          ollama: {
            level,
            message: data.message,
            model: data.active_model || data.configured_model,
          },
        }));
      }
    } catch {
      setStatus((prev) => ({
        ...prev,
        ollama: { level: "error", message: "Ollama Unavailable" },
      }));
    }

    try {
      const res = await fetch(`${API_BASE}/health/llm`);
      if (res.ok) {
        const data = await res.json();
        const level = data.primary_status === "available" ? "ok" : "warning";
        setStatus((prev) => ({
          ...prev,
          llm: {
            level,
            message: `${data.primary_provider}: ${data.primary_status}`,
          },
        }));
      }
    } catch {
      setStatus((prev) => ({
        ...prev,
        llm: { level: "error", message: "LLM Provider Error" },
      }));
    }
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  const renderActiveView = () => {
    if (!activeTab) return null;
    switch (activeTab) {
      case "home":
        return <HomeView onNavigate={(tab) => setActiveTab(tab)} />;
      case "learn":
        return <LearnChatView />;
      case "knowledge":
        return <KnowledgeGraphView />;
      case "assessments":
        return <AssessmentsView />;
      case "notes":
        return <NotesView />;
      case "library":
        return <LibraryView />;
      case "learner_state":
        return <LearnerStateView />;
      default:
        return null;
    }
  };

  const meta = activeTab ? MODULE_META[activeTab] : null;

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-900">
      {/* 1. Full-screen Pixel Nature World Landscape */}
      <PixelEnvironment
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
      />

      {/* 2. Focused Retro Pixel Window (When a building or tab is selected) */}
      {activeTab && meta && (
        <PixelWindow
          title={meta.title}
          subtitle={meta.subtitle}
          icon={meta.icon}
          activeTab={activeTab}
          onClose={() => setActiveTab(null)}
        >
          {renderActiveView()}
        </PixelWindow>
      )}

      {/* 3. Bottom Quick Navigation Dock & Diegetic System Status */}
      <PixelDock
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
        status={status}
      />
    </div>
  );
}

export default App;
