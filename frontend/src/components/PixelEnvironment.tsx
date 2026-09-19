import React, { useState } from "react";
import {
  CottageSVG,
  TreeObservatorySVG,
  LibraryTowerSVG,
  ExamShrineSVG,
  WritingGazeboSVG,
  CrystalMonolithSVG,
  CentralHearthSVG,
} from "./PixelArtSVG";

export type NavTab =
  | "home"
  | "learn"
  | "knowledge"
  | "assessments"
  | "notes"
  | "library"
  | "learner_state";

interface PixelEnvironmentProps {
  activeTab: NavTab | null;
  onSelectTab: (tab: NavTab) => void;
}

interface WorldLocation {
  id: NavTab;
  name: string;
  subtitle: string;
  x: string; // CSS percentage position
  y: string;
  component: React.ReactNode;
}

export const PixelEnvironment: React.FC<PixelEnvironmentProps> = ({
  activeTab,
  onSelectTab,
}) => {
  const [hoveredTab, setHoveredTab] = useState<NavTab | null>(null);

  const locations: WorldLocation[] = [
    {
      id: "home",
      name: "Central Hearth",
      subtitle: "Sanctuary & Daily Target",
      x: "47%",
      y: "48%",
      component: <CentralHearthSVG size={90} />,
    },
    {
      id: "learn",
      name: "Study Cottage",
      subtitle: "AI Learn & Guided Chat",
      x: "22%",
      y: "42%",
      component: <CottageSVG size={100} />,
    },
    {
      id: "knowledge",
      name: "Concept Observatory",
      subtitle: "Tree of Knowledge & Graph",
      x: "72%",
      y: "32%",
      component: <TreeObservatorySVG size={104} />,
    },
    {
      id: "assessments",
      name: "Shrine of Mastery",
      subtitle: "Quizzes & Diagnostics",
      x: "82%",
      y: "56%",
      component: <ExamShrineSVG size={96} />,
    },
    {
      id: "notes",
      name: "Willow Writing Gazebo",
      subtitle: "Learner Journal & Notes",
      x: "15%",
      y: "65%",
      component: <WritingGazeboSVG size={96} />,
    },
    {
      id: "library",
      name: "Archive Library",
      subtitle: "Resources & Reference Vault",
      x: "62%",
      y: "62%",
      component: <LibraryTowerSVG size={100} />,
    },
    {
      id: "learner_state",
      name: "Crystal Monolith",
      subtitle: "Multi-Dim Knowledge State",
      x: "34%",
      y: "30%",
      component: <CrystalMonolithSVG size={90} />,
    },
  ];

  return (
    <div className="relative w-full h-full overflow-hidden select-none">
      {/* ----------------------------------------------------
         1. SKY & ATMOSPHERE
         ---------------------------------------------------- */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background:
            "linear-gradient(to bottom, var(--sky-top) 0%, var(--sky-mid) 45%, var(--sky-bottom) 70%, var(--grass-light) 100%)",
        }}
      >
        {/* Pixel Sun with Soft Glow */}
        <div className="absolute top-8 left-16 flex items-center justify-center animate-float">
          <div
            className="w-16 h-16 rounded-full pixelated"
            style={{
              backgroundColor: "#fff3b0",
              boxShadow: "0 0 40px rgba(255, 243, 176, 0.6), 0 0 10px #ffe066",
            }}
          />
        </div>

        {/* Drifting Pixel Clouds */}
        <div className="absolute top-10 w-full pointer-events-none">
          <div className="absolute top-2 animate-cloud-slow flex gap-1 opacity-90">
            <div className="w-12 h-6 bg-white rounded-t-md opacity-90" />
            <div className="w-16 h-8 bg-white rounded-t-md -ml-4" />
            <div className="w-10 h-5 bg-white rounded-t-md -ml-3" />
          </div>

          <div className="absolute top-14 animate-cloud-fast flex gap-1 opacity-75">
            <div className="w-16 h-7 bg-white rounded-t-md" />
            <div className="w-20 h-9 bg-white rounded-t-md -ml-4" />
          </div>
        </div>

        {/* Distant Mountain Silhouettes */}
        <svg
          className="absolute bottom-1/3 w-full h-40 opacity-40 pointer-events-none"
          viewBox="0 0 1000 120"
          preserveAspectRatio="none"
          style={{ shapeRendering: "crispEdges" }}
        >
          <polygon points="0,120 120,40 240,120" fill="#3a5a40" />
          <polygon points="180,120 340,25 500,120" fill="#2d4a35" />
          <polygon points="450,120 580,50 700,120" fill="#3a5a40" />
          <polygon points="650,120 800,20 950,120" fill="#2d4a35" />
          <polygon points="880,120 960,60 1000,120" fill="#3a5a40" />
        </svg>
      </div>

      {/* ----------------------------------------------------
         2. TERRAIN & NATURE LANDSCAPE (Grass & River)
         ---------------------------------------------------- */}
      <div className="absolute bottom-0 w-full h-3/4 pointer-events-none">
        {/* Background Grass Hill */}
        <div
          className="absolute bottom-0 w-full h-5/6"
          style={{
            clipPath: "ellipse(85% 65% at 50% 65%)",
            backgroundColor: "var(--grass-main)",
          }}
        />

        {/* Foreground Meadow Hill */}
        <div
          className="absolute bottom-0 w-full h-4/6"
          style={{
            clipPath: "ellipse(95% 70% at 50% 75%)",
            backgroundColor: "var(--grass-light)",
          }}
        />

        {/* Winding River Stream */}
        <svg
          className="absolute bottom-0 w-full h-full opacity-90"
          viewBox="0 0 1000 600"
          preserveAspectRatio="none"
          style={{ shapeRendering: "crispEdges" }}
        >
          {/* Riverbed/Water Flow */}
          <path
            d="M 380 180 C 420 280, 520 340, 480 440 C 450 510, 360 550, 320 600 L 410 600 C 460 540, 550 490, 570 430 C 610 320, 500 250, 450 180 Z"
            fill="var(--river-mid)"
          />
          <path
            d="M 390 180 C 428 280, 528 340, 488 440 C 458 510, 368 550, 335 600 L 380 600 C 430 540, 520 490, 540 430 C 580 320, 485 250, 430 180 Z"
            fill="var(--river-light)"
            opacity="0.6"
          />

          {/* Wooden Bridge crossing the River */}
          <rect x="475" y="360" width="60" height="24" fill="#684a38" rx="2" />
          <rect x="475" y="360" width="60" height="4" fill="#8d5b4c" />
          <rect x="475" y="380" width="60" height="4" fill="#8d5b4c" />
          <rect x="470" y="356" width="6" height="32" fill="#402e23" />
          <rect x="530" y="356" width="6" height="32" fill="#402e23" />
        </svg>

        {/* Cobblestone Dirt Paths Connecting Buildings */}
        <svg
          className="absolute inset-0 w-full h-full opacity-40"
          viewBox="0 0 1000 600"
          preserveAspectRatio="none"
          style={{ shapeRendering: "crispEdges" }}
        >
          <path
            d="M 230 260 Q 350 280 470 300 Q 600 250 720 200"
            stroke="#684a38"
            strokeWidth="12"
            strokeDasharray="6 6"
            fill="none"
          />
          <path
            d="M 470 300 L 485 365 M 520 380 Q 560 410 630 400 M 200 400 Q 300 380 470 300"
            stroke="#684a38"
            strokeWidth="10"
            strokeDasharray="4 6"
            fill="none"
          />
        </svg>

        {/* Scattered Pixel Trees & Flowers in Meadow */}
        <div className="absolute bottom-12 left-10 w-8 h-12 bg-emerald-800 rounded-t-full opacity-80" />
        <div className="absolute bottom-20 left-28 w-10 h-16 bg-emerald-900 rounded-t-full opacity-80" />
        <div className="absolute bottom-32 right-12 w-12 h-20 bg-emerald-800 rounded-t-full opacity-80" />
      </div>

      {/* ----------------------------------------------------
         3. INTERACTIVE PIXEL BUILDINGS & OBJECTS
         ---------------------------------------------------- */}
      <div className="absolute inset-0 w-full h-full">
        {locations.map((loc) => {
          const isHovered = hoveredTab === loc.id;
          const isActive = activeTab === loc.id;

          return (
            <div
              key={loc.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
              style={{ left: loc.x, top: loc.y, zIndex: isActive ? 40 : 20 }}
              onMouseEnter={() => setHoveredTab(loc.id)}
              onMouseLeave={() => setHoveredTab(null)}
              onClick={() => onSelectTab(loc.id)}
            >
              {/* Building Container with Hover Lift & Pulse */}
              <div
                className={`transition-all duration-200 flex flex-col items-center ${
                  isHovered ? "-translate-y-2 scale-105" : "translate-y-0"
                }`}
              >
                {/* Pixel Floating Marker / Badge */}
                <div
                  className={`mb-1 px-3 py-1 text-xs font-pixel-heading rounded border transition-all duration-200 shadow-md ${
                    isActive
                      ? "bg-emerald-600 text-white border-emerald-300 scale-110"
                      : isHovered
                      ? "bg-amber-100 text-amber-950 border-amber-400 scale-105"
                      : "bg-slate-900/80 text-emerald-200 border-emerald-800/80"
                  }`}
                  style={{
                    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                    letterSpacing: "0.02em",
                  }}
                >
                  <span className="mr-1.5">{isHovered ? "✦" : "📍"}</span>
                  {loc.name}
                </div>

                {/* SVG Pixel Building Render */}
                <div
                  className={`relative ${
                    isHovered ? "drop-shadow-[0_8px_16px_rgba(255,255,255,0.3)]" : ""
                  }`}
                >
                  {loc.component}
                </div>

                {/* Hover Subtitle Tooltip */}
                {isHovered && (
                  <div
                    className="absolute -bottom-8 whitespace-nowrap text-[11px] font-pixel-mono px-2 py-0.5 rounded bg-black/80 text-amber-200 border border-amber-500/40 pointer-events-none animate-float"
                    style={{ zIndex: 50 }}
                  >
                    {loc.subtitle}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* ----------------------------------------------------
         4. SOOTHING ENVIRONMENTAL TITLE OVERLAY
         ---------------------------------------------------- */}
      <div className="absolute top-4 left-6 pointer-events-none z-10 flex items-center gap-3">
        <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse pixelated border border-white" />
        <div>
          <h1 className="text-sm font-pixel-heading text-slate-900 tracking-wide drop-shadow-sm">
            PERSONAL LEARNING OS
          </h1>
          <p className="text-xs font-pixel-mono text-slate-800 opacity-90">
            Sanctuary World • Layer 2 Foundation Active
          </p>
        </div>
      </div>
    </div>
  );
};
