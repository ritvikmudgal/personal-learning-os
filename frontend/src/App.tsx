import React, { useState, useEffect, useCallback } from "react";
import { PixelEnvironment, NavTab } from "./components/PixelEnvironment";
import { PixelWindow } from "./components/PixelWindow";
import { PixelDock, SystemStatus } from "./components/PixelDock";
import {
  HomeIcon,
  StudyIcon,
  LibraryIcon,
  KnowledgeIcon,
  AssessmentIcon,
  NotesIcon,
  LearnerIcon,
} from "./components/WorldIcons";

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
  { title: string; subtitle: string; icon: React.ReactNode; themeAccent: string }
> = {
  home: {
    title: "Central Hearth",
    subtitle: "Your Personal Learning World & Daily Sanctuary",
    icon: <HomeIcon size={20} />,
    themeAccent: "#70b37b",
  },
  learn: {
    title: "Study Cottage",
    subtitle: "AI-Guided Learning & Interactive Tutor Room",
    icon: <StudyIcon size={20} />,
    themeAccent: "#3a684a",
  },
  knowledge: {
    title: "Concept Observatory",
    subtitle: "Knowledge Graph & Prerequisite Trees",
    icon: <KnowledgeIcon size={20} />,
    themeAccent: "#427890",
  },
  assessments: {
    title: "Assessment Pavilion",
    subtitle: "Diagnostics & Mastery Quizzes",
    icon: <AssessmentIcon size={20} />,
    themeAccent: "#b8822c",
  },
  notes: {
    title: "Writing Studio",
    subtitle: "Personal Study Journal & Notes",
    icon: <NotesIcon size={20} />,
    themeAccent: "#785a3c",
  },
  library: {
    title: "Archive Library",
    subtitle: "Study Materials & Semantic Vault",
    icon: <LibraryIcon size={20} />,
    themeAccent: "#b85b40",
  },
  learner_state: {
    title: "Learner Garden",
    subtitle: "Multi-Dimensional Mastery & Memory Growth",
    icon: <LearnerIcon size={20} />,
    themeAccent: "#3a684a",
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
      {/* 1. Layer A: Illustrated Personal Learning World */}
      <PixelEnvironment
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
      />

      {/* 2. Layer B: Software Window (When a destination or tab is active) */}
      {activeTab && meta && (
        <PixelWindow
          title={meta.title}
          subtitle={meta.subtitle}
          icon={meta.icon}
          activeTab={activeTab}
          themeAccent={meta.themeAccent}
          onClose={() => setActiveTab(null)}
        >
          {renderActiveView()}
        </PixelWindow>
      )}

      {/* 3. Bottom Desktop Application Launcher Shelf */}
      <PixelDock
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
        status={status}
      />
    </div>
  );
}

export default App;
