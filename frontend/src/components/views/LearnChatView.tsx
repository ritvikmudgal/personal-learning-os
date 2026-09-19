import React, { useState } from "react";

export const LearnChatView: React.FC = () => {
  const [messages, setMessages] = useState<
    { sender: "user" | "ai"; text: string; time: string }[]
  >([
    {
      sender: "ai",
      text: "Welcome to your study cottage! What concept or topic would you like to explore today? We can break down complex ideas step-by-step.",
      time: "10:00 AM",
    },
  ]);
  const [input, setInput] = useState("");
  const [isGuidedMode, setIsGuidedMode] = useState(true);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user" as const, text: input, time: "Now" };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // Simulate AI response response placeholder connected to Ollama Engine
    setTimeout(() => {
      const aiReply = {
        sender: "ai" as const,
        text: `I've analyzed your question on "${input}". Based on your concept graph state, let's break this down into prerequisites before diving deeper.`,
        time: "Now",
      };
      setMessages((prev) => [...prev, aiReply]);
    }, 600);
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Top Controls Bar */}
      <div className="flex items-center justify-between p-3 rounded pixel-panel text-xs font-pixel-mono">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-200">
            Model: <strong className="text-emerald-300">Ollama qwen2.5:3b</strong>
          </span>
        </div>

        <button
          onClick={() => setIsGuidedMode(!isGuidedMode)}
          className={`px-3 py-1 rounded text-xs font-pixel-heading border transition-colors ${
            isGuidedMode
              ? "bg-emerald-800 text-emerald-100 border-emerald-500"
              : "bg-slate-800 text-slate-400 border-slate-600"
          }`}
        >
          {isGuidedMode ? "🌿 Guided Study Mode: ON" : "💬 Freeform Mode"}
        </button>
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 overflow-y-auto space-y-3 p-3 rounded pixel-panel min-h-[300px] max-h-[460px]">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${
              msg.sender === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[85%] p-3 rounded text-xs leading-relaxed ${
                msg.sender === "user"
                  ? "bg-emerald-900/90 text-emerald-100 border border-emerald-600/60"
                  : "bg-slate-800 text-slate-200 border border-slate-700"
              }`}
            >
              <div className="font-pixel-heading text-[10px] text-amber-300/90 mb-1">
                {msg.sender === "user" ? "Learner" : "AI Study Assistant"}
              </div>
              <p>{msg.text}</p>
            </div>
            <span className="text-[10px] font-pixel-mono text-slate-500 mt-1">
              {msg.time}
            </span>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question or explain a concept..."
          className="flex-1 p-3 rounded pixel-panel text-xs text-slate-100 bg-slate-900 border border-slate-700 focus:outline-none focus:border-emerald-500 font-pixel-mono"
        />
        <button
          onClick={handleSend}
          className="pixel-button pixel-button-primary text-xs"
        >
          SEND ➔
        </button>
      </div>
    </div>
  );
};
