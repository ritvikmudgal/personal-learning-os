import React from "react";
import { NavTab } from "./PixelEnvironment";
import { CloseIcon } from "./WorldIcons";

interface PixelWindowProps {
  title: string;
  subtitle: string;
  icon?: React.ReactNode | string;
  activeTab: NavTab;
  themeAccent?: string;
  onClose: () => void;
  children: React.ReactNode;
}

export const PixelWindow: React.FC<PixelWindowProps> = ({
  title,
  subtitle,
  icon,
  themeAccent,
  onClose,
  children,
}) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 animate-fade-in"
      style={{
        backgroundColor: "rgba(32, 44, 38, 0.45)",
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        className="world-window w-full max-w-6xl h-[88vh] flex flex-col relative animate-window-in"
      >
        {/* Decorative subtle accent bar at top */}
        <div
          className="h-1 w-full"
          style={{
            background: themeAccent
              ? `linear-gradient(90deg, var(--window-header), ${themeAccent}, var(--window-header))`
              : "linear-gradient(90deg, var(--window-header), var(--accent-sage), var(--window-header))",
          }}
        />

        {/* Title Bar — warm desktop software header */}
        <div className="world-window-header select-none">
          {/* Left: Icon & Title */}
          <div className="flex items-center gap-3">
            {icon && (
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-amber-200 border border-white/10">
                {typeof icon === "string" ? <span className="text-lg">{icon}</span> : icon}
              </div>
            )}
            <div>
              <h2 className="text-base font-heading font-semibold text-amber-50 tracking-tight">
                {title}
              </h2>
              <p className="text-xs text-amber-200/70 font-body font-normal">
                {subtitle}
              </p>
            </div>
          </div>

          {/* Right: Controls & Close */}
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-heading font-medium rounded-lg transition-all duration-150 bg-white/10 hover:bg-white/20 text-amber-100 border border-white/15 active:scale-95"
              title="Return to World landscape"
            >
              <CloseIcon size={14} />
              <span>Back to World</span>
            </button>
          </div>
        </div>

        {/* Content Area — warm parchment software canvas */}
        <div
          className="flex-1 overflow-y-auto p-5 sm:p-7 custom-scrollbar"
          style={{ backgroundColor: "var(--window-bg)" }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
