import React, { useState, useRef, useEffect } from "react";
import {
  StudyIcon,
  SparklesIcon,
  BrainIcon,
  BookOpenIcon,
  ChevronRightIcon,
} from "../WorldIcons";

const API_BASE = "http://127.0.0.1:8000/api";

interface MessageProvenance {
  type: string;
  title: string;
  detail: string;
}

interface MessageTurn {
  sender: "user" | "ai";
  text: string;
  time: string;
  provenance?: MessageProvenance[];
  teaching_plan?: string[];
  target_concept_name?: string;
}

export const LearnChatView: React.FC = () => {
  const [messages, setMessages] = useState<MessageTurn[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [teachingPlan, setTeachingPlan] = useState<string[]>([]);
  const [activeConcept, setActiveConcept] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load existing active session on mount
  useEffect(() => {
    const fetchActiveSession = async () => {
      try {
        const res = await fetch(`${API_BASE}/tutor/session/active`);
        if (res.ok) {
          const data = await res.json();
          if (data.active && data.session) {
            setSessionId(data.session.id);
            setTeachingPlan(data.session.teaching_plan || []);
            const msgs: MessageTurn[] = (data.session.messages || []).map((m: any) => ({
              sender: m.sender,
              text: m.text,
              time: "Saved",
              provenance: m.metadata?.provenance || [],
              teaching_plan: m.metadata?.teaching_plan || [],
              target_concept_name: m.metadata?.target_concept_name,
            }));
            setMessages(msgs);
          }
        }
      } catch (err) {
        console.error("Failed to load active tutor session:", err);
      }
    };
    fetchActiveSession();
  }, []);

  const handleSend = async (customPrompt?: string) => {
    const promptToSend = (customPrompt || input).trim();
    if (!promptToSend || isLoading) return;

    const userMsg: MessageTurn = {
      sender: "user",
      text: promptToSend,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!customPrompt) setInput("");
    setIsLoading(true);

    try {
      // 30-second timeout to prevent infinite hanging
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000);

      const response = await fetch(`${API_BASE}/tutor/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: promptToSend,
          session_id: sessionId,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const contentType = response.headers.get("content-type") || "";

      // --- Path 1: Instant JSON response (NORMAL_CONVERSATION) ---
      if (contentType.includes("application/json")) {
        const data = await response.json();
        const aiMsg: MessageTurn = {
          sender: "ai",
          text: data.text || "Hello! Welcome to your Study Cottage. What would you like to explore today?",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          provenance: data.provenance || [],
          teaching_plan: data.teaching_plan || [],
          target_concept_name: data.target_concept_name,
        };
        setMessages((prev) => [...prev, aiMsg]);
        if (data.session_id) setSessionId(data.session_id);
        if (data.teaching_plan) setTeachingPlan(data.teaching_plan);
        if (data.target_concept_name) setActiveConcept(data.target_concept_name);
        return;
      }

      // --- Path 2: SSE streaming response (study/learning requests) ---
      if (!response.body) {
        throw new Error("No response body for streaming");
      }

      // Add placeholder AI message for streaming token display
      const placeholderAiMsg: MessageTurn = {
        sender: "ai",
        text: "",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        provenance: [],
        teaching_plan: [],
        target_concept_name: undefined,
      };
      setMessages((prev) => [...prev, placeholderAiMsg]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          let eventType = "message";
          let dataStr = "";

          const eventMatch = line.match(/^event:\s*(.+)$/m);
          if (eventMatch) eventType = eventMatch[1].trim();

          const dataMatch = line.match(/^data:\s*(.+)$/m);
          if (dataMatch) dataStr = dataMatch[1].trim();

          if (dataStr) {
            try {
              const parsedData = JSON.parse(dataStr);
              if (eventType === "metadata") {
                if (parsedData.session_id) setSessionId(parsedData.session_id);
                if (parsedData.teaching_plan) setTeachingPlan(parsedData.teaching_plan);
                if (parsedData.target_concept_name) setActiveConcept(parsedData.target_concept_name);

                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.sender === "ai") {
                    last.provenance = parsedData.provenance || [];
                    last.teaching_plan = parsedData.teaching_plan || [];
                    last.target_concept_name = parsedData.target_concept_name;
                  }
                  return updated;
                });
              } else if (eventType === "token") {
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.sender === "ai") {
                    last.text += parsedData;
                  }
                  return updated;
                });
              } else if (eventType === "done") {
                if (parsedData.session_id) setSessionId(parsedData.session_id);
              } else if (eventType === "error") {
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.sender === "ai") {
                    last.text = parsedData.text || "Something went wrong while processing that. Please try again.";
                  }
                  return updated;
                });
              }
            } catch (e) {
              console.warn("Error parsing stream chunk:", e, dataStr);
            }
          }
        }
      }
    } catch (err: any) {
      console.error("Chat request failed:", err);
      const errorMsg: MessageTurn = {
        sender: "ai",
        text: err.name === "AbortError" 
          ? "Request timed out after 30s. The AI tutor might be busy. Please try asking again."
          : "Could not connect to tutor service. Please check your backend connection.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[75vh] max-h-[800px] gap-4">
      {/* Top Banner: Study Cottage Focus Header */}
      <div className="world-panel p-4 bg-gradient-to-r from-emerald-50/90 via-amber-50/50 to-emerald-50/90 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-800 text-emerald-100 flex items-center justify-center">
            <StudyIcon size={20} />
          </div>
          <div>
            <h2 className="text-sm font-heading font-bold text-slate-800">
              Study Room • Guided Learning Assistant
            </h2>
            <p className="text-xs text-slate-600 font-body">
              {activeConcept ? `Focus Topic: ${activeConcept}` : "Interactive conceptual tutor & inquiry room"}
            </p>
          </div>
        </div>
        {teachingPlan.length > 0 && (
          <div className="world-badge world-badge-ok text-xs">
            <span>Plan: {teachingPlan.length} Steps</span>
          </div>
        )}
      </div>

      {/* Main Study Chat Canvas */}
      <div className="flex-1 overflow-y-auto p-5 rounded-xl border border-amber-200/60 bg-[#fdfbf7] custom-scrollbar space-y-4">
        {messages.length === 0 ? (
          <div className="world-empty-state h-full my-auto">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center mb-4">
              <SparklesIcon size={28} />
            </div>
            <h3 className="world-empty-state-title">Welcome to Study Cottage</h3>
            <p className="world-empty-state-desc mb-6">
              Ask anything you'd like to learn, or request a step-by-step topic breakdown.
            </p>

            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {[
                { label: "Teach me Binary Search", icon: <BrainIcon size={16} /> },
                { label: "Explain Recursion simply", icon: <BookOpenIcon size={16} /> },
                { label: "Review my weak concepts", icon: <SparklesIcon size={16} /> },
              ].map((sug) => (
                <button
                  key={sug.label}
                  onClick={() => handleSend(sug.label)}
                  className="world-button hover:border-emerald-600 hover:text-emerald-900 bg-white text-xs px-3.5 py-2 shadow-xs"
                >
                  <span className="text-emerald-700">{sug.icon}</span>
                  <span>{sug.label}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[78%] p-4 rounded-2xl shadow-xs font-body ${
                  msg.sender === "user"
                    ? "bg-amber-100/60 text-slate-900 border border-amber-300/60 rounded-br-sm"
                    : "bg-white text-slate-800 border border-emerald-200/80 rounded-bl-sm"
                }`}
              >
                {/* Header */}
                <div className="flex items-center justify-between text-xs font-heading font-medium mb-1.5 gap-4">
                  <span className={msg.sender === "user" ? "text-amber-900 font-semibold" : "text-emerald-800 font-semibold"}>
                    {msg.sender === "user" ? "You" : "🌿 AI Tutor"}
                  </span>
                  <span className="text-[11px] text-slate-400 font-normal">
                    {msg.time}
                  </span>
                </div>

                {/* Message Body Text */}
                <div className="text-sm leading-relaxed whitespace-pre-wrap text-slate-800">
                  {msg.text}
                </div>

                {/* Provenance Badges */}
                {msg.provenance && msg.provenance.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-200/80 flex flex-wrap gap-1.5">
                    {msg.provenance.map((p, pIdx) => (
                      <span
                        key={pIdx}
                        className="text-[11px] font-heading px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200"
                      >
                        {p.type === "material" ? "📚 Note: " : p.type === "prerequisite" ? "⚠️ Gap: " : "🌱 Context: "}
                        {p.title}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="p-3.5 rounded-xl bg-white border border-emerald-200 text-emerald-800 text-xs font-body flex items-center gap-2 animate-pulse">
              <SparklesIcon size={16} />
              <span>AI Tutor is thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex items-center gap-2 p-2 bg-white border border-amber-200/80 rounded-xl shadow-xs">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a study question (e.g., 'Teach me binary search')..."
          disabled={isLoading}
          className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-800 outline-none font-body placeholder:italic placeholder:text-slate-400"
        />
        <button
          onClick={() => handleSend()}
          disabled={isLoading || !input.trim()}
          className="world-button world-button-primary px-4 py-2 text-xs font-medium"
        >
          <span>{isLoading ? "Thinking..." : "Send"}</span>
          <ChevronRightIcon size={14} />
        </button>
      </div>
    </div>
  );
};
