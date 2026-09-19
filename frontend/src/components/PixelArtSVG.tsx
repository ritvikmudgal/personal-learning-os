import React from "react";

// Crisp pixel art SVG icons/buildings using shape-rendering="crispEdges"

export const CottageSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Chimney Smoke */}
    <rect x="22" y="3" width="2" height="2" fill="#d9e5d6" opacity="0.6" />
    <rect x="23" y="1" width="3" height="2" fill="#ffffff" opacity="0.4" />
    
    {/* Chimney */}
    <rect x="21" y="6" width="3" height="6" fill="#4a3728" />
    <rect x="21" y="5" width="4" height="1" fill="#684a38" />

    {/* Roof */}
    <rect x="15" y="6" width="2" height="2" fill="#9e4c34" />
    <rect x="13" y="8" width="6" height="2" fill="#9e4c34" />
    <rect x="11" y="10" width="10" height="2" fill="#9e4c34" />
    <rect x="9" y="12" width="14" height="2" fill="#833c27" />
    <rect x="7" y="14" width="18" height="2" fill="#833c27" />

    {/* Walls */}
    <rect x="8" y="16" width="16" height="13" fill="#d4ad84" />
    <rect x="8" y="16" width="1" height="13" fill="#b38b64" />
    <rect x="23" y="16" width="1" height="13" fill="#b38b64" />

    {/* Timber Beams */}
    <rect x="8" y="16" width="16" height="1" fill="#5c3d2e" />
    <rect x="8" y="22" width="16" height="1" fill="#5c3d2e" />
    <rect x="15" y="16" width="2" height="6" fill="#5c3d2e" />

    {/* Door */}
    <rect x="14" y="23" width="4" height="6" fill="#4a2e1b" />
    <rect x="17" y="26" width="1" height="1" fill="#ffd700" /> {/* Knob */}

    {/* Warm Window Glow */}
    <rect x="10" y="18" width="3" height="3" fill="#ffe066" />
    <rect x="11" y="18" width="1" height="3" fill="#5c3d2e" />
    <rect x="10" y="19" width="3" height="1" fill="#5c3d2e" />

    <rect x="19" y="18" width="3" height="3" fill="#ffe066" />
    <rect x="20" y="18" width="1" height="3" fill="#5c3d2e" />
    <rect x="19" y="19" width="3" height="1" fill="#5c3d2e" />

    {/* Foundation / Grass base */}
    <rect x="6" y="29" width="20" height="2" fill="#386e42" />
  </svg>
);

export const TreeObservatorySVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Trunk */}
    <rect x="14" y="16" width="4" height="13" fill="#402e23" />
    <rect x="13" y="25" width="2" height="4" fill="#33241b" />
    <rect x="17" y="26" width="2" height="3" fill="#33241b" />

    {/* Leaves Layer 1 */}
    <rect x="8" y="8" width="16" height="10" fill="#2f5d37" />
    <rect x="6" y="11" width="20" height="6" fill="#386e42" />
    <rect x="10" y="5" width="12" height="6" fill="#4a8c54" />

    {/* Glowing Concept Runes in Tree */}
    <rect x="9" y="12" width="2" height="2" fill="#70b2c4" opacity="0.9" />
    <rect x="19" y="9" width="2" height="2" fill="#70b2c4" opacity="0.9" />
    <rect x="14" y="7" width="2" height="2" fill="#bbf2c4" opacity="0.9" />
    <rect x="21" y="14" width="2" height="2" fill="#e3b067" opacity="0.9" />

    {/* Telescope Dome on branch */}
    <rect x="18" y="2" width="6" height="4" fill="#688b9a" />
    <rect x="19" y="1" width="4" height="1" fill="#a4c6d4" />
    <rect x="22" y="0" width="3" height="2" fill="#d9eaf0" /> {/* Telescope Lens */}

    {/* Base */}
    <rect x="11" y="29" width="10" height="2" fill="#2d5a35" />
  </svg>
);

export const LibraryTowerSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Roof Spire */}
    <rect x="15" y="1" width="2" height="3" fill="#833c27" />
    <rect x="14" y="4" width="4" height="2" fill="#9e4c34" />
    <rect x="12" y="6" width="8" height="2" fill="#833c27" />
    <rect x="10" y="8" width="12" height="2" fill="#9e4c34" />

    {/* Stone Tower Walls */}
    <rect x="11" y="10" width="10" height="19" fill="#5e686d" />
    <rect x="11" y="10" width="1" height="19" fill="#424b50" />
    <rect x="20" y="10" width="1" height="19" fill="#424b50" />

    {/* Stone Bricks detail */}
    <rect x="13" y="12" width="3" height="1" fill="#758288" />
    <rect x="17" y="15" width="2" height="1" fill="#758288" />
    <rect x="12" y="19" width="3" height="1" fill="#758288" />
    <rect x="16" y="23" width="3" height="1" fill="#758288" />

    {/* Bookshelf Windows */}
    <rect x="14" y="12" width="4" height="4" fill="#ffe066" />
    <rect x="15" y="13" width="1" height="3" fill="#833c27" />
    <rect x="16" y="13" width="1" height="3" fill="#2b5c73" />

    <rect x="14" y="18" width="4" height="4" fill="#ffe066" />
    <rect x="15" y="19" width="1" height="3" fill="#4a8c54" />
    <rect x="16" y="19" width="1" height="3" fill="#9e4c34" />

    {/* Archway Door */}
    <rect x="14" y="24" width="4" height="5" fill="#33241b" />
    <rect x="15" y="24" width="2" height="1" fill="#4e3425" />

    {/* Base */}
    <rect x="9" y="29" width="14" height="2" fill="#2d5a35" />
  </svg>
);

export const ExamShrineSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Curved Roof */}
    <rect x="6" y="8" width="20" height="2" fill="#833c27" />
    <rect x="4" y="10" width="24" height="2" fill="#9e4c34" />
    <rect x="2" y="11" width="3" height="1" fill="#833c27" />
    <rect x="27" y="11" width="3" height="1" fill="#833c27" />

    {/* Pillars */}
    <rect x="7" y="12" width="2" height="16" fill="#833c27" />
    <rect x="23" y="12" width="2" height="16" fill="#833c27" />
    <rect x="15" y="12" width="2" height="16" fill="#68301f" />

    {/* Assessment Desk & Scroll Inside */}
    <rect x="11" y="21" width="10" height="2" fill="#d4ad84" />
    <rect x="13" y="17" width="6" height="4" fill="#fdfbf7" />
    <rect x="14" y="18" width="4" height="1" fill="#833c27" />
    <rect x="14" y="20" width="3" height="1" fill="#833c27" />

    {/* Shrine Lantern Glow */}
    <rect x="9" y="14" width="2" height="3" fill="#ffe066" />
    <rect x="21" y="14" width="2" height="3" fill="#ffe066" />

    {/* Base Steps */}
    <rect x="5" y="28" width="22" height="2" fill="#684a38" />
    <rect x="3" y="30" width="26" height="2" fill="#52392a" />
  </svg>
);

export const WritingGazeboSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Willow Tree Backdrop */}
    <rect x="3" y="4" width="12" height="18" fill="#386e42" opacity="0.8" />
    <rect x="1" y="7" width="8" height="12" fill="#4a8c54" opacity="0.8" />

    {/* Gazebo Roof */}
    <rect x="15" y="6" width="12" height="2" fill="#684a38" />
    <rect x="13" y="8" width="16" height="2" fill="#866049" />

    {/* Posts */}
    <rect x="14" y="10" width="2" height="18" fill="#52392a" />
    <rect x="26" y="10" width="2" height="18" fill="#52392a" />

    {/* Notes Desk & Lamp */}
    <rect x="17" y="20" width="8" height="2" fill="#b08968" />
    <rect x="18" y="16" width="3" height="4" fill="#fffbe6" /> {/* Notebook */}
    <rect x="23" y="17" width="2" height="3" fill="#ffd166" /> {/* Candle Lamp */}

    {/* Deck Base */}
    <rect x="12" y="28" width="18" height="2" fill="#684a38" />
  </svg>
);

export const CrystalMonolithSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Glowing Monolith Pillar */}
    <rect x="13" y="6" width="6" height="20" fill="#3a5a40" />
    <rect x="14" y="4" width="4" height="2" fill="#588157" />
    <rect x="15" y="2" width="2" height="2" fill="#a3b18a" />

    {/* Inner Crystal Core */}
    <rect x="14" y="8" width="4" height="16" fill="#70b2c4" />
    <rect x="15" y="10" width="2" height="12" fill="#bbf2c4" />

    {/* Floating Energy Particles */}
    <rect x="10" y="10" width="2" height="2" fill="#bbf2c4" opacity="0.8" />
    <rect x="20" y="14" width="2" height="2" fill="#70b2c4" opacity="0.8" />
    <rect x="9" y="18" width="1" height="2" fill="#e3b067" opacity="0.8" />
    <rect x="22" y="8" width="2" height="2" fill="#bbf2c4" opacity="0.8" />

    {/* Stone Base Ring */}
    <rect x="10" y="26" width="12" height="4" fill="#344e41" />
    <rect x="8" y="28" width="16" height="2" fill="#2a3d33" />
  </svg>
);

export const CentralHearthSVG: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ shapeRendering: "crispEdges" }} className={className}>
    {/* Great Oak Canopy behind */}
    <rect x="6" y="2" width="20" height="12" fill="#386e42" />
    <rect x="10" y="0" width="12" height="4" fill="#4a8c54" />
    <rect x="13" y="14" width="6" height="8" fill="#52392a" />

    {/* Campfire Stones */}
    <rect x="12" y="24" width="8" height="4" fill="#5c677d" />
    <rect x="14" y="22" width="4" height="2" fill="#f77f00" /> {/* Flame */}
    <rect x="15" y="20" width="2" height="2" fill="#fcbf49" /> {/* Flame core */}

    {/* Log Benches */}
    <rect x="6" y="24" width="5" height="3" fill="#7f5539" />
    <rect x="21" y="24" width="5" height="3" fill="#7f5539" />

    {/* Meadow Base */}
    <rect x="4" y="28" width="24" height="3" fill="#2d5a35" />
  </svg>
);
