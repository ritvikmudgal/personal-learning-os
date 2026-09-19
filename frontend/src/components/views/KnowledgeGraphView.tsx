import React, { useState } from "react";

interface ConceptNode {
  id: string;
  title: string;
  category: string;
  mastery: number; // 0-100
  prereqs: string[];
}

const SAMPLE_NODES: ConceptNode[] = [
  { id: "python_basics", title: "Python Fundamentals", category: "Language", mastery: 92, prereqs: [] },
  { id: "async_io", title: "Asynchronous IO & Event Loop", category: "Concurrency", mastery: 68, prereqs: ["python_basics"] },
  { id: "memory_mgmt", title: "Memory Allocation & Garbage Collection", category: "Systems", mastery: 45, prereqs: ["python_basics"] },
  { id: "data_structs", title: "Data Structures & Trees", category: "Algorithms", mastery: 84, prereqs: ["python_basics"] },
  { id: "graph_traversal", title: "Graph Traversal (DFS/BFS)", category: "Algorithms", mastery: 76, prereqs: ["data_structs"] },
];

const getMasteryColor = (mastery: number) => {
  if (mastery >= 80) return "var(--accent-moss)";
  if (mastery >= 60) return "var(--accent-amber)";
  if (mastery >= 40) return "var(--accent-sky)";
  return "var(--accent-coral)";
};

const getMasteryLabel = (mastery: number) => {
  if (mastery >= 80) return "Strong";
  if (mastery >= 60) return "Growing";
  if (mastery >= 40) return "Developing";
  return "Needs attention";
};

export const KnowledgeGraphView: React.FC = () => {
  const [traversalMode, setTraversalMode] = useState<"dfs" | "bfs">("dfs");
  const [selectedNode, setSelectedNode] = useState<ConceptNode>(SAMPLE_NODES[0]);

  return (
    <div className="space-y-5">
      {/* Controls Bar */}
      <div
        className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg gap-3"
        style={{
          backgroundColor: "var(--accent-sky-bg)",
          border: "1.5px solid var(--accent-sky)",
        }}
      >
        <div className="flex items-center gap-3 text-sm">
          <span style={{ color: "var(--window-text-muted)" }}>Traversal:</span>
          <div className="flex gap-1.5">
            {(["dfs", "bfs"] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setTraversalMode(mode)}
                className="px-3 py-1.5 rounded-md text-xs font-pixel-heading transition-all"
                style={{
                  backgroundColor:
                    traversalMode === mode
                      ? "var(--accent-sky)"
                      : "var(--window-bg)",
                  color:
                    traversalMode === mode
                      ? "#ffffff"
                      : "var(--window-text-muted)",
                  border: `1px solid ${
                    traversalMode === mode
                      ? "var(--accent-sky)"
                      : "var(--window-border-light)"
                  }`,
                }}
              >
                {mode === "dfs" ? "Depth-First" : "Breadth-First"}
              </button>
            ))}
          </div>
        </div>

        <span
          className="pixel-badge pixel-badge-ok"
        >
          Cycle Detection Active
        </span>
      </div>

      {/* Main Grid — Concept nodes + Inspector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Concepts List */}
        <div className="md:col-span-2 space-y-3">
          <h3
            className="text-sm font-pixel-heading px-1 flex items-center gap-2"
            style={{ color: "var(--window-text-muted)" }}
          >
            <span>🌳</span> Knowledge Tree ({SAMPLE_NODES.length} concepts)
          </h3>
          <div className="space-y-2">
            {SAMPLE_NODES.map((node) => {
              const isSelected = selectedNode.id === node.id;
              const masteryColor = getMasteryColor(node.mastery);
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className="p-4 rounded-lg cursor-pointer transition-all flex items-center justify-between"
                  style={{
                    backgroundColor: isSelected
                      ? "var(--accent-sky-bg)"
                      : "var(--window-card)",
                    border: `1.5px solid ${
                      isSelected
                        ? "var(--accent-sky)"
                        : "var(--window-border-light)"
                    }`,
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.borderColor = "var(--window-border)";
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.borderColor = "var(--window-border-light)";
                  }}
                >
                  <div>
                    <div
                      className="text-sm font-medium mb-1"
                      style={{ color: "var(--window-text-primary)" }}
                    >
                      {node.title}
                    </div>
                    <div className="text-xs" style={{ color: "var(--window-text-muted)" }}>
                      {node.category}
                      {node.prereqs.length > 0 && (
                        <span> · Requires: {node.prereqs.join(", ")}</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Mastery indicator — colored dot + label instead of progress bar */}
                  <div className="flex items-center gap-2 text-right">
                    <div>
                      <div className="text-xs font-pixel-heading" style={{ color: masteryColor }}>
                        {node.mastery}%
                      </div>
                      <div className="text-[11px]" style={{ color: "var(--window-text-faint)" }}>
                        {getMasteryLabel(node.mastery)}
                      </div>
                    </div>
                    {/* Mastery ring indicator */}
                    <svg width="28" height="28" viewBox="0 0 28 28">
                      <circle cx="14" cy="14" r="11" fill="none" stroke="var(--window-border-light)" strokeWidth="2.5" />
                      <circle
                        cx="14" cy="14" r="11"
                        fill="none"
                        stroke={masteryColor}
                        strokeWidth="2.5"
                        strokeDasharray={`${(node.mastery / 100) * 69.1} 69.1`}
                        strokeLinecap="round"
                        transform="rotate(-90 14 14)"
                        style={{ transition: "stroke-dasharray 0.4s ease" }}
                      />
                      <circle cx="14" cy="14" r="3" fill={masteryColor} opacity="0.6" />
                    </svg>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Node Inspector */}
        <div
          className="p-5 rounded-lg space-y-4 h-fit"
          style={{
            backgroundColor: "var(--window-card)",
            border: "1.5px solid var(--window-border-light)",
            borderLeft: "4px solid var(--accent-sky)",
          }}
        >
          <h3
            className="text-sm font-pixel-heading flex items-center gap-2"
            style={{ color: "var(--accent-sky)" }}
          >
            <span>🔍</span> Concept Details
          </h3>
          <div>
            <div
              className="text-base font-medium mb-1"
              style={{ color: "var(--window-text-primary)" }}
            >
              {selectedNode.title}
            </div>
            <div className="text-xs" style={{ color: "var(--window-text-faint)" }}>
              {selectedNode.id}
            </div>
          </div>

          <div
            className="p-4 rounded-lg space-y-3"
            style={{
              backgroundColor: "var(--window-bg)",
              border: "1px solid var(--window-border-light)",
            }}
          >
            <div className="flex justify-between text-sm">
              <span style={{ color: "var(--window-text-muted)" }}>Mastery</span>
              <span className="font-pixel-heading text-xs" style={{ color: getMasteryColor(selectedNode.mastery) }}>
                {selectedNode.mastery}% · {getMasteryLabel(selectedNode.mastery)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span style={{ color: "var(--window-text-muted)" }}>Prerequisites</span>
              <span style={{ color: "var(--accent-sky)" }}>
                {selectedNode.prereqs.length === 0 ? "Root Concept" : `${selectedNode.prereqs.length} parent(s)`}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span style={{ color: "var(--window-text-muted)" }}>Category</span>
              <span style={{ color: "var(--accent-earth)" }}>
                {selectedNode.category}
              </span>
            </div>
          </div>

          <button className="pixel-button pixel-button-primary w-full text-xs mt-2">
            🌱 Explore Prerequisite Tree
          </button>
        </div>
      </div>
    </div>
  );
};
