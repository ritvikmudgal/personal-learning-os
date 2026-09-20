import React, { useState } from "react";
import {
  KnowledgeIcon,
  BrainIcon,
  SparklesIcon,
  ChevronRightIcon,
} from "../WorldIcons";

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
  if (mastery >= 80) return "#3a684a";
  if (mastery >= 60) return "#b8822c";
  if (mastery >= 40) return "#427890";
  return "#b85b40";
};

const getMasteryLabel = (mastery: number) => {
  if (mastery >= 80) return "Mastered";
  if (mastery >= 60) return "Growing";
  if (mastery >= 40) return "Developing";
  return "Needs attention";
};

export const KnowledgeGraphView: React.FC = () => {
  const [traversalMode, setTraversalMode] = useState<"dfs" | "bfs">("dfs");
  const [selectedNode, setSelectedNode] = useState<ConceptNode>(SAMPLE_NODES[0]);

  return (
    <div className="space-y-6">
      {/* Observatory Controls Header */}
      <div className="world-panel p-4 bg-gradient-to-r from-sky-50/90 via-sky-100/40 to-sky-50/90 border-l-4 border-l-sky-700 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-sky-900 text-sky-100 flex items-center justify-center">
            <KnowledgeIcon size={20} />
          </div>
          <div>
            <h2 className="text-base font-heading font-bold text-slate-900">
              Concept Observatory & DAG Traversal
            </h2>
            <p className="text-xs text-slate-600 font-body">
              Prerequisite graph network, cycle detection, and concept node inspection
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-heading font-medium text-slate-600">Traversal:</span>
          <div className="flex gap-1 bg-white p-1 rounded-lg border border-slate-200">
            {(["dfs", "bfs"] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setTraversalMode(mode)}
                className={`px-3 py-1 rounded-md text-xs font-heading font-medium transition-all ${
                  traversalMode === mode
                    ? "bg-sky-800 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {mode === "dfs" ? "Depth-First (DFS)" : "Breadth-First (BFS)"}
              </button>
            ))}
          </div>
          <span className="world-badge world-badge-ok text-xs">
            Cycle Free
          </span>
        </div>
      </div>

      {/* Main Grid — Concept Nodes + Inspector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Concepts List */}
        <div className="md:col-span-2 space-y-3">
          <h3 className="text-xs font-heading font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-2">
            <BrainIcon size={16} className="text-sky-700" />
            <span>Knowledge Concept Nodes ({SAMPLE_NODES.length})</span>
          </h3>

          <div className="space-y-2">
            {SAMPLE_NODES.map((node) => {
              const isSelected = selectedNode.id === node.id;
              const masteryColor = getMasteryColor(node.mastery);

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`world-panel p-4 bg-white cursor-pointer transition-all duration-150 flex items-center justify-between ${
                    isSelected ? "border-sky-600 ring-2 ring-sky-600/10 shadow-sm" : "hover:border-slate-300"
                  }`}
                >
                  <div>
                    <h4 className="text-sm font-heading font-semibold text-slate-900 mb-0.5">
                      {node.title}
                    </h4>
                    <p className="text-xs text-slate-500 font-body">
                      Category: {node.category}
                      {node.prereqs.length > 0 && (
                        <span> · Requires: {node.prereqs.join(", ")}</span>
                      )}
                    </p>
                  </div>

                  {/* Mastery Indicator */}
                  <div className="flex items-center gap-3 text-right">
                    <div>
                      <div className="text-xs font-heading font-bold" style={{ color: masteryColor }}>
                        {node.mastery}%
                      </div>
                      <div className="text-[11px] text-slate-400 font-body">
                        {getMasteryLabel(node.mastery)}
                      </div>
                    </div>

                    <svg width="28" height="28" viewBox="0 0 28 28">
                      <circle cx="14" cy="14" r="11" fill="none" stroke="#e2e8f0" strokeWidth="2.5" />
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

        {/* Node Inspector Drawer */}
        <div className="world-panel p-5 bg-white border-l-4 border-l-sky-700 space-y-4 h-fit">
          <div className="flex items-center gap-2 text-sky-800">
            <SparklesIcon size={18} />
            <h3 className="text-sm font-heading font-bold text-slate-900">
              Concept Node Inspector
            </h3>
          </div>

          <div>
            <h4 className="text-base font-heading font-semibold text-slate-900">
              {selectedNode.title}
            </h4>
            <p className="text-xs text-slate-400 font-body">
              Symbol ID: {selectedNode.id}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5 font-body text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Mastery Level</span>
              <span className="font-semibold" style={{ color: getMasteryColor(selectedNode.mastery) }}>
                {selectedNode.mastery}% · {getMasteryLabel(selectedNode.mastery)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium font-body">Prerequisites</span>
              <span className="text-sky-800 font-semibold">
                {selectedNode.prereqs.length === 0 ? "Root Concept" : `${selectedNode.prereqs.length} required`}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium font-body">Domain Category</span>
              <span className="text-slate-700 font-semibold">
                {selectedNode.category}
              </span>
            </div>
          </div>

          <button className="world-button world-button-primary w-full text-xs py-2.5 shadow-xs">
            <span>Explore Traversal Subtree</span>
            <ChevronRightIcon size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};
