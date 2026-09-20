import React from "react";

// Illustrated Architectural Landmarks for Layer A World

export const CottageSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Chimney Smoke */}
    <g className="animate-float" style={{ animationDuration: '4s' }}>
      <circle cx="92" cy="18" r="7" fill="#f4efe6" opacity="0.6" />
      <circle cx="98" cy="10" r="10" fill="#f4efe6" opacity="0.4" />
      <circle cx="106" cy="4" r="12" fill="#ffffff" opacity="0.25" />
    </g>

    {/* Chimney */}
    <rect x="82" y="24" width="14" height="28" rx="2" fill="#4a3a30" />
    <rect x="80" y="22" width="18" height="5" rx="1.5" fill="#6a5445" />

    {/* Main Roof */}
    <path d="M12 56L60 16L108 56H12Z" fill="#a05238" />
    <path d="M18 56L60 21L102 56H18Z" fill="#b85f42" />
    <path d="M10 56L60 14L110 56" stroke="#4a2e1e" strokeWidth="4" strokeLinecap="round" />

    {/* House Walls */}
    <rect x="22" y="56" width="76" height="50" rx="3" fill="#f2e8d8" />
    <rect x="22" y="56" width="6" height="50" fill="#dfd2be" />

    {/* Timber Frames */}
    <line x1="22" y1="56" x2="98" y2="56" stroke="#594436" strokeWidth="3" />
    <line x1="22" y1="78" x2="98" y2="78" stroke="#594436" strokeWidth="3" />
    <line x1="60" y1="56" x2="60" y2="78" stroke="#594436" strokeWidth="3" />

    {/* Glowing Windows */}
    <rect x="30" y="62" width="18" height="12" rx="2" fill="#f9d77e" stroke="#594436" strokeWidth="2" />
    <line x1="39" y1="62" x2="39" y2="74" stroke="#594436" strokeWidth="1.5" />
    <line x1="30" y1="68" x2="48" y2="68" stroke="#594436" strokeWidth="1.5" />

    <rect x="72" y="62" width="18" height="12" rx="2" fill="#f9d77e" stroke="#594436" strokeWidth="2" />
    <line x1="81" y1="62" x2="81" y2="74" stroke="#594436" strokeWidth="1.5" />
    <line x1="72" y1="68" x2="90" y2="68" stroke="#594436" strokeWidth="1.5" />

    {/* Arched Doorway */}
    <path d="M50 106V88C50 82.4772 54.4772 78 60 78C65.5228 78 70 82.4772 70 88V106H50Z" fill="#593b28" stroke="#3a271a" strokeWidth="2" />
    <circle cx="66" cy="94" r="2" fill="#f9d77e" />

    {/* Potted Plants & Flowers */}
    <rect x="26" y="98" width="10" height="8" rx="2" fill="#b85b40" />
    <circle cx="29" cy="95" r="4" fill="#528663" />
    <circle cx="33" cy="95" r="4" fill="#3a684a" />
    <circle cx="31" cy="92" r="3" fill="#e89d84" />

    {/* Stone Foundation Base */}
    <rect x="16" y="104" width="88" height="8" rx="4" fill="#7a6c5d" />
  </svg>
);

export const LibraryTowerSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Spire Roof */}
    <path d="M60 8L36 36H84L60 8Z" fill="#3c5264" />
    <path d="M60 12L42 36H78L60 12Z" fill="#4d677d" />
    <path d="M60 4V8" stroke="#d49f42" strokeWidth="3" strokeLinecap="round" />
    <circle cx="60" cy="4" r="3" fill="#f9d77e" />

    {/* Stone Library Walls */}
    <rect x="40" y="36" width="40" height="72" rx="3" fill="#849098" stroke="#48545c" strokeWidth="2" />
    <rect x="40" y="36" width="6" height="72" fill="#707c84" />

    {/* Architectural Trim */}
    <rect x="36" y="35" width="48" height="5" rx="1.5" fill="#5c6870" />
    <rect x="36" y="65" width="48" height="4" rx="1" fill="#5c6870" />

    {/* Arched Library Windows with Book Stacks */}
    <path d="M50 44C50 41.5 54.5 40 60 40C65.5 40 70 41.5 70 44V58H50V44Z" fill="#f9d77e" stroke="#48545c" strokeWidth="2" />
    <rect x="53" y="48" width="4" height="10" fill="#b85b40" />
    <rect x="58" y="46" width="4" height="12" fill="#3a684a" />
    <rect x="63" y="49" width="4" height="9" fill="#427890" />

    <path d="M50 74C50 71.5 54.5 70 60 70C65.5 70 70 71.5 70 74V88H50V74Z" fill="#f9d77e" stroke="#48545c" strokeWidth="2" />
    <rect x="53" y="78" width="4" height="10" fill="#b8822c" />
    <rect x="58" y="76" width="4" height="12" fill="#594436" />
    <rect x="63" y="79" width="4" height="9" fill="#b85b40" />

    {/* Entrance Doorway */}
    <path d="M52 108V96C52 92 55.5 89 60 89C64.5 89 68 92 68 96V108H52Z" fill="#4a3425" />
    <rect x="58" y="88" width="4" height="2" fill="#d49f42" />

    {/* Stone Steps */}
    <rect x="30" y="106" width="60" height="6" rx="3" fill="#606c74" />
  </svg>
);

export const TreeObservatorySVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Oak Tree Foliage Canopy */}
    <circle cx="60" cy="45" r="38" fill="#2d5238" />
    <circle cx="42" cy="50" r="26" fill="#3a684a" />
    <circle cx="78" cy="50" r="26" fill="#3a684a" />
    <circle cx="60" cy="36" r="28" fill="#528663" />

    {/* Brass Telescope Dome atop Tree */}
    <path d="M46 30C46 22.268 52.268 16 60 16C67.732 16 74 22.268 74 30H46Z" fill="#52798e" stroke="#2c4d5e" strokeWidth="2" />
    <rect x="44" y="29" width="32" height="4" rx="1" fill="#3d6275" />
    
    {/* Telescope Lens */}
    <path d="M68 20L84 10" stroke="#d49f42" strokeWidth="5" strokeLinecap="round" />
    <circle cx="85" cy="9" r="4" fill="#a4d8ec" stroke="#d49f42" strokeWidth="1.5" />

    {/* Tree Trunk & Observatory Platform */}
    <rect x="52" y="65" width="16" height="44" rx="2" fill="#523d30" />
    <path d="M42 66L60 62L78 66V70H42V66Z" fill="#7a5c48" />

    {/* Constellation Glow Sparkles */}
    <circle cx="34" cy="42" r="3" fill="#f9d77e" className="animate-pulse-glow" />
    <circle cx="86" cy="38" r="3" fill="#f9d77e" className="animate-pulse-glow" style={{ animationDelay: '1s' }} />
    <circle cx="60" cy="52" r="2.5" fill="#a4d8ec" className="animate-pulse-glow" style={{ animationDelay: '1.8s' }} />

    {/* Roots Base */}
    <path d="M40 108C48 105 52 108 60 108C68 108 72 105 80 108" stroke="#3a2b22" strokeWidth="4" strokeLinecap="round" />
  </svg>
);

export const ExamShrineSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Curved Pavilion Roof */}
    <path d="M16 38C32 30 88 30 104 38L96 46H24L16 38Z" fill="#a05238" stroke="#592e1e" strokeWidth="2" />
    <path d="M22 36C36 28 84 28 98 36" stroke="#b85f42" strokeWidth="4" strokeLinecap="round" />
    <rect x="56" y="22" width="8" height="10" fill="#d49f42" rx="1" />

    {/* Pavilion Columns */}
    <rect x="26" y="46" width="7" height="54" fill="#6a4c3b" />
    <rect x="87" y="46" width="7" height="54" fill="#6a4c3b" />
    <rect x="56" y="46" width="8" height="54" fill="#52392b" />

    {/* Study Podium & Scroll */}
    <rect x="42" y="74" width="36" height="22" rx="2" fill="#e4dabf" stroke="#594436" strokeWidth="2" />
    <rect x="48" y="64" width="24" height="14" rx="2" fill="#faf7f2" stroke="#b8822c" strokeWidth="1.5" />
    <line x1="52" y1="69" x2="68" y2="69" stroke="#736556" strokeWidth="1.5" />
    <line x1="52" y1="73" x2="64" y2="73" stroke="#736556" strokeWidth="1.5" />

    {/* Warm Lanterns */}
    <rect x="34" y="52" width="8" height="10" rx="2" fill="#f9d77e" stroke="#594436" strokeWidth="1.5" />
    <rect x="78" y="52" width="8" height="10" rx="2" fill="#f9d77e" stroke="#594436" strokeWidth="1.5" />

    {/* Stone Pavilion Terraced Steps */}
    <rect x="18" y="100" width="84" height="6" rx="2" fill="#847464" />
    <rect x="12" y="106" width="96" height="6" rx="3" fill="#685a4c" />
  </svg>
);

export const WritingGazeboSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Weeping Willow Canopy */}
    <path d="M20 20C10 35 15 70 12 90" stroke="#487c5e" strokeWidth="5" strokeLinecap="round" />
    <path d="M30 15C20 35 25 70 22 95" stroke="#5e8469" strokeWidth="6" strokeLinecap="round" />
    <circle cx="35" cy="30" r="28" fill="#3a684a" opacity="0.85" />
    <circle cx="28" cy="22" r="20" fill="#528663" opacity="0.9" />

    {/* Writing Desk under Canopy */}
    <rect x="50" y="68" width="54" height="28" rx="4" fill="#6a4c3b" stroke="#3a271a" strokeWidth="2" />
    <rect x="56" y="96" width="8" height="14" fill="#4a3425" />
    <rect x="90" y="96" width="8" height="14" fill="#4a3425" />

    {/* Notebook Studio Details */}
    <rect x="58" y="60" width="22" height="14" rx="2" fill="#faf7f2" stroke="#b8822c" strokeWidth="1.5" transform="rotate(-4 58 60)" />
    <path d="M88 56L94 66" stroke="#d49f42" strokeWidth="2.5" strokeLinecap="round" /> {/* Ink Quill */}
    
    {/* Warm Reading Desk Lamp */}
    <path d="M96 66C96 60 92 56 86 56" stroke="#3a271a" strokeWidth="2" />
    <circle cx="86" cy="56" r="5" fill="#f9d77e" />

    {/* Wooden Deck Base */}
    <rect x="42" y="106" width="70" height="6" rx="3" fill="#52392b" />
  </svg>
);

export const CrystalMonolithSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Glasshouse Greenhouse */}
    <path d="M60 18L24 46V104H96V46L60 18Z" fill="#e8f3ee" opacity="0.75" stroke="#3a684a" strokeWidth="2.5" />
    <path d="M60 18V104" stroke="#528663" strokeWidth="2" />
    <line x1="24" y1="46" x2="96" y2="46" stroke="#528663" strokeWidth="2" />
    <line x1="24" y1="75" x2="96" y2="75" stroke="#528663" strokeWidth="2" />

    {/* Botanical Terraced Beds & Growing Plants */}
    <rect x="32" y="78" width="24" height="24" rx="2" fill="#594436" />
    <circle cx="44" cy="74" r="8" fill="#528663" />
    <circle cx="44" cy="68" r="6" fill="#70a684" />

    <rect x="64" y="78" width="24" height="24" rx="2" fill="#594436" />
    <path d="M76 78V66C76 60 84 58 86 64" stroke="#3a684a" strokeWidth="3" strokeLinecap="round" />
    <circle cx="82" cy="60" r="4" fill="#b85b40" />

    {/* Sun Ray Reflections on Glass */}
    <path d="M36 28L70 80" stroke="#ffffff" strokeWidth="3" opacity="0.5" strokeLinecap="round" />
    <path d="M48 24L82 76" stroke="#ffffff" strokeWidth="2" opacity="0.3" strokeLinecap="round" />

    {/* Base Stone Border */}
    <rect x="18" y="104" width="84" height="6" rx="3" fill="#3a5946" />
  </svg>
);

export const CentralHearthSVG: React.FC<{ size?: number; className?: string }> = ({ size = 120, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    {/* Ancient Hearth Oak Tree */}
    <circle cx="60" cy="40" r="34" fill="#2e5942" />
    <circle cx="40" cy="46" r="24" fill="#487c5e" />
    <circle cx="80" cy="46" r="24" fill="#487c5e" />

    <rect x="52" y="58" width="16" height="42" rx="3" fill="#594436" />

    {/* Campfire Ring & Warm Glow */}
    <ellipse cx="60" cy="98" rx="24" ry="10" fill="#3a2b22" />
    <circle cx="60" cy="96" r="8" fill="#b85b40" />
    <circle cx="60" cy="94" r="5" fill="#d49f42" className="animate-pulse-glow" />

    {/* Wooden Bench Seats */}
    <rect x="22" y="92" width="20" height="8" rx="2" fill="#806753" />
    <rect x="78" y="92" width="20" height="8" rx="2" fill="#806753" />

    {/* Meadow Base */}
    <rect x="12" y="104" width="96" height="6" rx="3" fill="#2e5942" />
  </svg>
);
