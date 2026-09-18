import { useState, useEffect, useCallback } from "react";

/** Backend API base URL */
const API_BASE = "http://127.0.0.1:8000/api";

/** Status indicator types */
type StatusLevel = "loading" | "ok" | "warning" | "error";

interface SystemStatus {
  backend: { level: StatusLevel; message: string };
  ollama: { level: StatusLevel; message: string; model?: string };
  llm: { level: StatusLevel; message: string };
}

const INITIAL_STATUS: SystemStatus = {
  backend: { level: "loading", message: "Checking..." },
  ollama: { level: "loading", message: "Checking..." },
  llm: { level: "loading", message: "Checking..." },
};

function StatusDot({ level }: { level: StatusLevel }) {
  const colors: Record<StatusLevel, string> = {
    loading: "bg-yellow-400 animate-pulse",
    ok: "bg-green-400",
    warning: "bg-yellow-400",
    error: "bg-red-400",
  };
  return <span className={`inline-block w-2.5 h-2.5 rounded-full ${colors[level]}`} />;
}

function App() {
  const [status, setStatus] = useState<SystemStatus>(INITIAL_STATUS);

  const checkStatus = useCallback(async () => {
    // Check backend health
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
        backend: { level: "error", message: "Cannot connect to backend" },
      }));
    }

    // Check Ollama
    try {
      const res = await fetch(`${API_BASE}/health/ollama`);
      if (res.ok) {
        const data = await res.json();
        const level: StatusLevel = data.status === "available" ? "ok" : "warning";
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
        ollama: { level: "error", message: "Cannot check Ollama status" },
      }));
    }

    // Check LLM provider
    try {
      const res = await fetch(`${API_BASE}/health/llm`);
      if (res.ok) {
        const data = await res.json();
        const level: StatusLevel =
          data.primary_status === "available" ? "ok" : "warning";
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
        llm: { level: "error", message: "Cannot check LLM status" },
      }));
    }
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="max-w-lg w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--accent)" }}>
            Personal Learning OS
          </h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Foundation Layer — System Status
          </p>
        </div>

        {/* Status Cards */}
        <div className="space-y-3">
          <StatusCard label="Backend API" {...status.backend} />
          <StatusCard label="Ollama" {...status.ollama} model={status.ollama.model} />
          <StatusCard label="LLM Provider" {...status.llm} />
        </div>

        {/* Refresh Button */}
        <div className="text-center">
          <button
            onClick={checkStatus}
            className="px-4 py-2 text-sm rounded-md transition-colors cursor-pointer"
            style={{
              backgroundColor: "var(--bg-secondary)",
              color: "var(--text-secondary)",
              border: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            Refresh Status
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs" style={{ color: "var(--text-secondary)" }}>
          Tauri + React + TypeScript • FastAPI + SQLite • Ollama
        </p>
      </div>
    </div>
  );
}

function StatusCard({
  label,
  level,
  message,
  model,
}: {
  label: string;
  level: StatusLevel;
  message: string;
  model?: string;
}) {
  return (
    <div
      className="p-4 rounded-lg flex items-start gap-3"
      style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      <div className="mt-1">
        <StatusDot level={level} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{label}</span>
          {model && (
            <span
              className="text-xs px-2 py-0.5 rounded"
              style={{ backgroundColor: "rgba(108,140,255,0.15)", color: "var(--accent)" }}
            >
              {model}
            </span>
          )}
        </div>
        <p className="text-xs mt-1 truncate" style={{ color: "var(--text-secondary)" }}>
          {message}
        </p>
      </div>
    </div>
  );
}

export default App;
