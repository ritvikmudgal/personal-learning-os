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
      subtitle: "Sanctuary & Daily Learning Focus",
      x: "48%",
      y: "49%",
      component: <CentralHearthSVG size={110} />,
    },
    {
      id: "learn",
      name: "Study Cottage",
      subtitle: "AI Learning Room & Guided Study",
      x: "22%",
      y: "43%",
      component: <CottageSVG size={120} />,
    },
    {
      id: "knowledge",
      name: "Concept Observatory",
      subtitle: "Tree of Knowledge & Graph",
      x: "74%",
      y: "32%",
      component: <TreeObservatorySVG size={120} />,
    },
    {
      id: "assessments",
      name: "Assessment Pavilion",
      subtitle: "Mastery Diagnostics & Quizzes",
      x: "82%",
      y: "58%",
      component: <ExamShrineSVG size={115} />,
    },
    {
      id: "notes",
      name: "Writing Studio",
      subtitle: "Notebook & Learner Journal",
      x: "16%",
      y: "66%",
      component: <WritingGazeboSVG size={115} />,
    },
    {
      id: "library",
      name: "Archive Library",
      subtitle: "Knowledge Repository & Vault",
      x: "60%",
      y: "63%",
      component: <LibraryTowerSVG size={120} />,
    },
    {
      id: "learner_state",
      name: "Learner Garden",
      subtitle: "Growing Mastery & Skills State",
      x: "34%",
      y: "31%",
      component: <CrystalMonolithSVG size={110} />,
    },
  ];

  return (
    <div className="relative w-full h-full overflow-hidden select-none">
      {/* ----------------------------------------------------
         1. LAYER A: SKY & ATMOSPHERIC DEPTH
         ---------------------------------------------------- */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background:
            "linear-gradient(to bottom, #dbe9e3 0%, #cce0d6 40%, #b8d4c7 70%, #9cbdae 100%)",
        }}
      >
        {/* Soft Daylight Sun */}
        <div className="absolute top-10 left-20 animate-float" style={{ animationDuration: '6s' }}>
          <div
            className="w-20 h-20 rounded-full"
            style={{
              background: "radial-gradient(circle, #fff7d6 0%, #fae69e 60%, rgba(255, 247, 214, 0) 100%)",
              filter: "blur(2px)",
            }}
          />
        </div>

        {/* Organic Silhouetted Clouds */}
        <div className="absolute top-8 w-full pointer-events-none">
          <svg className="absolute top-2 left-0 w-full h-32 animate-cloud-slow opacity-85" viewBox="0 0 1200 120">
            <path d="M50 60 Q70 40 100 45 Q130 30 170 40 Q210 35 240 55 Q260 75 220 80 Q150 85 50 80 Z" fill="#ffffff" opacity="0.85" />
            <path d="M450 40 Q470 20 510 25 Q540 15 580 25 Q610 15 650 35 Q670 60 630 65 Q550 70 450 65 Z" fill="#ffffff" opacity="0.75" />
            <path d="M850 50 Q870 30 910 35 Q940 25 980 35 Q1020 25 1060 45 Q1080 65 1040 70 Q960 75 850 70 Z" fill="#ffffff" opacity="0.8" />
          </svg>
        </div>

        {/* Layered Distant Mountain Silhouettes with Atmospheric Mist */}
        <svg
          className="absolute bottom-1/3 w-full h-48 opacity-45 pointer-events-none"
          viewBox="0 0 1200 160"
          preserveAspectRatio="none"
        >
          <path d="M0 160 L140 60 Q200 80 320 40 L480 160 Z" fill="#4d6f5c" />
          <path d="M260 160 L440 30 Q540 70 700 20 L860 160 Z" fill="#3b5949" />
          <path d="M680 160 L850 50 Q940 80 1060 30 L1200 160 Z" fill="#4d6f5c" />
        </svg>

        {/* Distant Mist Overlay */}
        <div
          className="absolute bottom-1/3 w-full h-16 pointer-events-none"
          style={{
            background: "linear-gradient(to top, rgba(184, 212, 199, 0.7), transparent)",
          }}
        />
      </div>

      {/* ----------------------------------------------------
         2. LAYER A: TERRAIN & NATURE LANDSCAPE (Forest, Hills, River)
         ---------------------------------------------------- */}
      <div className="absolute bottom-0 w-full h-4/5 pointer-events-none">
        {/* Background Forest Hill */}
        <div
          className="absolute bottom-0 w-full h-full"
          style={{
            clipPath: "ellipse(88% 65% at 50% 68%)",
            backgroundColor: "#2e5942",
          }}
        />

        {/* Foreground Meadow Slope */}
        <div
          className="absolute bottom-0 w-full h-5/6"
          style={{
            clipPath: "ellipse(96% 72% at 50% 76%)",
            backgroundColor: "#427658",
          }}
        />

        {/* Organic Curved River Stream & Reflections */}
        <svg
          className="absolute bottom-0 w-full h-full opacity-90"
          viewBox="0 0 1000 600"
          preserveAspectRatio="none"
        >
          {/* Main River Bed */}
          <path
            d="M 390 170 C 430 260, 530 330, 480 430 C 440 510, 350 550, 310 600 L 410 600 C 460 540, 560 490, 580 430 C 630 320, 510 250, 460 170 Z"
            fill="#366175"
          />
          {/* Water Highlight & Ripple Flow */}
          <path
            d="M 400 170 C 438 260, 538 330, 488 430 C 448 510, 358 550, 325 600 L 375 600 C 425 540, 530 490, 550 430 C 600 320, 495 250, 440 170 Z"
            fill="#528399"
            opacity="0.65"
          />

          {/* Wooden Footbridge */}
          <rect x="470" y="358" width="68" height="26" fill="#6a4c3b" rx="4" />
          <line x1="470" y1="364" x2="538" y2="364" stroke="#805d49" strokeWidth="3" />
          <line x1="470" y1="378" x2="538" y2="378" stroke="#805d49" strokeWidth="3" />
          <rect x="466" y="354" width="8" height="34" rx="2" fill="#4a3425" />
          <rect x="534" y="354" width="8" height="34" rx="2" fill="#4a3425" />
        </svg>

        {/* Winding Cobblestone Dirt Paths */}
        <svg
          className="absolute inset-0 w-full h-full opacity-35"
          viewBox="0 0 1000 600"
          preserveAspectRatio="none"
        >
          <path
            d="M 220 260 Q 340 280 480 300 Q 610 250 740 190"
            stroke="#594436"
            strokeWidth="14"
            strokeDasharray="6 8"
            fill="none"
          />
          <path
            d="M 480 300 L 490 365 M 530 380 Q 570 410 630 400 M 180 400 Q 300 380 480 300"
            stroke="#594436"
            strokeWidth="12"
            strokeDasharray="5 7"
            fill="none"
          />
        </svg>
      </div>

      {/* ----------------------------------------------------
         3. LAYER A: ARCHITECTURAL DESTINATIONS & LOCATIONS
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
              {/* Building Container with Hover Lift */}
              <div
                className={`transition-all duration-250 flex flex-col items-center ${
                  isHovered ? "-translate-y-2.5 scale-105" : "translate-y-0"
                }`}
              >
                {/* Location Badge */}
                <div
                  className={`mb-2 px-3.5 py-1 text-xs font-heading font-medium rounded-full transition-all duration-200 shadow-md flex items-center gap-1.5 ${
                    isActive
                      ? "bg-emerald-800 text-white border border-emerald-500 scale-110 shadow-lg"
                      : isHovered
                      ? "bg-amber-100 text-amber-950 border border-amber-400 scale-105"
                      : "bg-slate-900/80 text-amber-100 border border-slate-700/80 backdrop-blur-sm"
                  }`}
                  style={{
                    letterSpacing: "0.01em",
                  }}
                >
                  <span className="text-amber-400">{isHovered ? "✦" : "📍"}</span>
                  {loc.name}
                </div>

                {/* Building SVG Render */}
                <div
                  className={`relative transition-all duration-200 ${
                    isHovered ? "filter drop-shadow-[0_12px_24px_rgba(42,34,27,0.25)]" : ""
                  }`}
                >
                  {loc.component}
                </div>

                {/* Hover Subtitle Tooltip */}
                {isHovered && (
                  <div
                    className="absolute -bottom-9 whitespace-nowrap text-xs font-body px-3 py-1 rounded-md bg-slate-900/90 text-amber-100 border border-amber-400/40 shadow-xl pointer-events-none animate-fade-in"
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
      <div className="absolute top-5 left-7 pointer-events-none z-10 flex items-center gap-3">
        <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse ring-4 ring-emerald-500/20" />
        <div>
          <h1 className="text-sm font-heading font-bold text-slate-800 tracking-wide">
            PERSONAL LEARNING OS
          </h1>
          <p className="text-xs font-body text-slate-600 font-medium">
            Sanctuary World
          </p>
        </div>
      </div>
    </div>
  );
};
