import React, { useState, useRef, useEffect } from "react";

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
      const res = await fetch(`${API_BASE}/tutor/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: promptToSend,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setSessionId(data.session_id);
      if (data.teaching_plan && data.teaching_plan.length > 0) {
        setTeachingPlan(data.teaching_plan);
      }
      if (data.target_concept_name) {
        setActiveConcept(data.target_concept_name);
      }

      const aiReply: MessageTurn = {
        sender: "ai",
        text: data.text,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        provenance: data.provenance || [],
        teaching_plan: data.teaching_plan || [],
        target_concept_name: data.target_concept_name,
      };

      setMessages((prev) => [...prev, aiReply]);
    } catch (err) {
      console.error("Tutor API error:", err);
      const errorReply: MessageTurn = {
        sender: "ai",
        text: "I encountered a minor bump connecting to the local tutor engine. Make sure the backend server and Ollama (qwen2.5:3b) are running.",
        time: "Now",
      };
      setMessages((prev) => [...prev, errorReply]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearSession = async () => {
    if (!sessionId) {
      setMessages([]);
      setTeachingPlan([]);
      setActiveConcept(null);
      return;
    }
    try {
      await fetch(`${API_BASE}/tutor/session/${sessionId}/clear`, { method: "POST" });
    } catch (err) {
      console.error("Error clearing session:", err);
    }
    setSessionId(null);
    setMessages([]);
    setTeachingPlan([]);
    setActiveConcept(null);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full" style={{ minHeight: "480px" }}>
      {/* Top Session Status Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0.6rem 1rem",
          backgroundColor: "#ffffff",
          border: "1px solid var(--wood-light)",
          borderRadius: "8px",
          marginBottom: "0.85rem",
          gap: "1rem",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: "var(--accent-moss-text)",
              display: "inline-block",
            }}
          />
          <span style={{ fontSize: "0.8rem", color: "var(--ink-secondary)", fontFamily: "var(--font-mono)" }}>
            Model: <strong style={{ color: "var(--accent-moss-text)" }}>qwen2.5:3b</strong>
          </span>
          {activeConcept && (
            <span
              style={{
                fontSize: "0.75rem",
                padding: "0.15rem 0.5rem",
                borderRadius: "4px",
                backgroundColor: "var(--accent-sky-bg)",
                color: "var(--accent-sky-text)",
                fontWeight: 600,
                fontFamily: "var(--font-mono)",
              }}
            >
              Focus: {activeConcept}
            </span>
          )}
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          {messages.length > 0 && (
            <button
              onClick={handleClearSession}
              className="pixel-button"
              style={{ padding: "0.25rem 0.65rem", fontSize: "0.75rem", background: "#fef2f2", color: "#991b1b" }}
            >
              🔄 New Session
            </button>
          )}
        </div>
      </div>

      {/* Teaching Plan Bar (if present) */}
      {teachingPlan.length > 0 && (
        <div
          style={{
            padding: "0.75rem 1rem",
            backgroundColor: "var(--accent-moss-bg)",
            border: "1px solid var(--accent-moss)",
            borderRadius: "8px",
            marginBottom: "0.85rem",
          }}
        >
          <div
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "var(--accent-moss-text)",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              marginBottom: "0.35rem",
            }}
          >
            🗺️ Personalized Teaching Path
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
            {teachingPlan.map((step, idx) => (
              <div key={idx} style={{ fontSize: "0.8rem", color: "var(--ink-primary)", lineHeight: 1.35 }}>
                <span style={{ fontWeight: 600, color: "var(--accent-moss-text)" }}>{idx + 1}.</span> {step}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conversation Area */}
      <div
        className="custom-scrollbar"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "1.25rem",
          backgroundColor: "#ffffff",
          border: "1px solid var(--wood-light)",
          borderRadius: "8px",
          marginBottom: "0.85rem",
          minHeight: "280px",
        }}
      >
        {isEmpty ? (
          /* Empty State */
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", textAlign: "center", padding: "2rem 1rem" }}>
            <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>🏡</div>
            <h3
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "1.2rem",
                color: "var(--ink-primary)",
                margin: "0 0 0.35rem 0",
              }}
            >
              Welcome to the Study Cottage
            </h3>
            <p
              style={{
                fontSize: "0.875rem",
                color: "var(--ink-secondary)",
                maxWidth: "360px",
                margin: "0 0 1.5rem 0",
                lineHeight: 1.45,
              }}
            >
              What would you like to explore or learn today?
            </p>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", justifyContent: "center", maxWidth: "420px" }}>
              {[
                { label: "Teach me Binary Search", icon: "🔍", color: "var(--accent-moss)", bg: "var(--accent-moss-bg)" },
                { label: "Explain Recursion", icon: "🌱", color: "#2b6b84", bg: "var(--accent-sky-bg)" },
                { label: "Review my weak concepts", icon: "🔄", color: "#b46912", bg: "#fef3c7" },
              ].map((sug) => (
                <button
                  key={sug.label}
                  onClick={() => handleSend(sug.label)}
                  style={{
                    padding: "0.55rem 0.9rem",
                    borderRadius: "6px",
                    fontSize: "0.82rem",
                    border: `1px solid ${sug.color}`,
                    backgroundColor: sug.bg,
                    color: sug.color,
                    cursor: "pointer",
                    transition: "transform 0.12s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  <span style={{ marginRight: "0.35rem" }}>{sug.icon}</span>
                  {sug.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Message List */
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "82%",
                    padding: "0.85rem 1.1rem",
                    borderRadius: "12px",
                    backgroundColor: msg.sender === "user" ? "var(--paper-panel)" : "#f4f8f5",
                    border: msg.sender === "user" ? "1px solid var(--wood-light)" : "1px solid var(--accent-moss-bg)",
                    borderBottomRightRadius: msg.sender === "user" ? "2px" : "12px",
                    borderBottomLeftRadius: msg.sender === "ai" ? "2px" : "12px",
                  }}
                >
                  {/* Header */}
                  <div
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      fontFamily: "var(--font-heading)",
                      color: msg.sender === "user" ? "#b46912" : "var(--accent-moss-text)",
                      marginBottom: "0.35rem",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "0.5rem",
                    }}
                  >
                    <span>{msg.sender === "user" ? "You" : "🌿 AI Tutor"}</span>
                    <span style={{ fontSize: "0.68rem", fontWeight: 400, color: "var(--ink-muted)" }}>
                      {msg.time}
                    </span>
                  </div>

                  {/* Body Text */}
                  <div
                    style={{
                      fontSize: "0.88rem",
                      color: "var(--ink-primary)",
                      lineHeight: 1.55,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {msg.text}
                  </div>

                  {/* Provenance & Context Badges */}
                  {msg.provenance && msg.provenance.length > 0 && (
                    <div
                      style={{
                        marginTop: "0.65rem",
                        paddingTop: "0.5rem",
                        borderTop: "1px dashed var(--wood-light)",
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "0.4rem",
                      }}
                    >
                      {msg.provenance.map((p, pIdx) => (
                        <span
                          key={pIdx}
                          style={{
                            fontSize: "0.7rem",
                            padding: "0.15rem 0.45rem",
                            borderRadius: "4px",
                            fontFamily: "var(--font-mono)",
                            backgroundColor:
                              p.type === "material"
                                ? "var(--accent-plum-bg)"
                                : p.type === "prerequisite"
                                ? "#fef3c7"
                                : "var(--accent-sky-bg)",
                            color:
                              p.type === "material"
                                ? "var(--accent-plum-text)"
                                : p.type === "prerequisite"
                                ? "#92400e"
                                : "var(--accent-sky-text)",
                          }}
                        >
                          {p.type === "material" ? "📚 Note: " : p.type === "prerequisite" ? "⚠️ Gap: " : "🌱 Prior: "}
                          {p.title}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div style={{ display: "flex", justifyContent: "flex-start" }}>
                <div
                  style={{
                    padding: "0.75rem 1rem",
                    borderRadius: "12px",
                    backgroundColor: "#f4f8f5",
                    border: "1px solid var(--accent-moss-bg)",
                    fontSize: "0.85rem",
                    color: "var(--accent-moss-text)",
                    fontStyle: "italic",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <span>🌿 Tutor is reflecting on learner state & materials...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          padding: "0.5rem 0.75rem",
          backgroundColor: "#ffffff",
          border: "1px solid var(--wood-light)",
          borderRadius: "8px",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question, request a concept explanation (e.g. 'Teach me binary search')..."
          disabled={isLoading}
          style={{
            flex: 1,
            border: "none",
            outline: "none",
            backgroundColor: "transparent",
            fontSize: "0.88rem",
            color: "var(--ink-primary)",
            padding: "0.5rem",
          }}
        />
        <button
          onClick={() => handleSend()}
          disabled={isLoading || !input.trim()}
          className="pixel-button pixel-button-primary"
          style={{
            padding: "0.55rem 1.1rem",
            fontSize: "0.82rem",
            opacity: isLoading || !input.trim() ? 0.6 : 1,
          }}
        >
          {isLoading ? "Thinking..." : "Send →"}
        </button>
      </div>
    </div>
  );
};

