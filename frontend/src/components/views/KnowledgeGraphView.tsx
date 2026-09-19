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

export const KnowledgeGraphView: React.FC = () => {
  const [traversalMode, setTraversalMode] = useState<"dfs" | "bfs">("dfs");
  const [selectedNode, setSelectedNode] = useState<ConceptNode>(SAMPLE_NODES[0]);

  return (
    <div className="space-y-4">
      {/* Engine Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded pixel-panel gap-3 text-xs font-pixel-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-300">Traversal Algorithm:</span>
          <div className="flex gap-1">
            <button
              onClick={() => setTraversalMode("dfs")}
              className={`px-2.5 py-1 rounded font-pixel-heading text-xs ${
                traversalMode === "dfs"
                  ? "bg-emerald-700 text-white"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              DFS (Depth-First)
            </button>
            <button
              onClick={() => setTraversalMode("bfs")}
              className={`px-2.5 py-1 rounded font-pixel-heading text-xs ${
                traversalMode === "bfs"
                  ? "bg-emerald-700 text-white"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              BFS (Breadth-First)
            </button>
          </div>
        </div>

        <div className="text-slate-400">
          Cycle Detection: <span className="text-emerald-400">ENABLED</span>
        </div>
      </div>

      {/* Main Graph Grid & Node Inspector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Nodes List */}
        <div className="md:col-span-2 p-4 rounded pixel-panel space-y-3">
          <h3 className="text-xs font-pixel-heading text-sky-400 mb-2">
            🕸️ CONCEPT NODES ({SAMPLE_NODES.length})
          </h3>
          <div className="space-y-2">
            {SAMPLE_NODES.map((node) => {
              const isSelected = selectedNode.id === node.id;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded border cursor-pointer transition-all flex items-center justify-between ${
                    isSelected
                      ? "bg-emerald-950/80 border-emerald-500 text-emerald-100"
                      : "bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300"
                  }`}
                >
                  <div>
                    <div className="font-pixel-heading text-xs mb-1">
                      {node.title}
                    </div>
                    <div className="text-[11px] font-pixel-mono text-slate-400">
                      Category: {node.category} • Prereqs: {node.prereqs.length > 0 ? node.prereqs.join(", ") : "None"}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-pixel-mono text-emerald-400 font-bold">
                      {node.mastery}%
                    </div>
                    <div className="w-16 bg-slate-800 h-1.5 rounded overflow-hidden mt-1">
                      <div
                        className="bg-emerald-500 h-full"
                        style={{ width: `${node.mastery}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details */}
        <div className="p-4 rounded pixel-panel space-y-3 border-l-2 border-l-sky-500">
          <h3 className="text-xs font-pixel-heading text-amber-400">
            🔍 NODE INSPECTOR
          </h3>
          <div>
            <div className="text-sm font-semibold text-slate-200">
              {selectedNode.title}
            </div>
            <div className="text-xs font-pixel-mono text-slate-400 mt-0.5">
              ID: {selectedNode.id}
            </div>
          </div>

          <div className="p-3 rounded bg-slate-900 border border-slate-800 text-xs font-pixel-mono space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Mastery Level:</span>
              <span className="text-emerald-400">{selectedNode.mastery}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Prerequisite Chain:</span>
              <span className="text-sky-300">
                {selectedNode.prereqs.length === 0 ? "Root Concept" : `${selectedNode.prereqs.length} parent`}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Graph Depth:</span>
              <span className="text-amber-300">Level 2</span>
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
