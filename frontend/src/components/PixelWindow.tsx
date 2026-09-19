import React from "react";
import { NavTab } from "./PixelEnvironment";

interface PixelWindowProps {
  title: string;
  subtitle: string;
  icon: string;
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-overlay-in"
      style={{ backgroundColor: "rgba(40, 60, 45, 0.35)", backdropFilter: "blur(2px)" }}
    >
      <div
        className="pixel-window w-full max-w-5xl h-[84vh] flex flex-col overflow-hidden relative animate-window-in"
      >
        {/* Decorative wood grain strip at very top */}
        <div
          className="h-1.5 w-full"
          style={{
            background: themeAccent
              ? `linear-gradient(90deg, var(--window-header), ${themeAccent}, var(--window-header))`
              : "linear-gradient(90deg, var(--window-header), var(--earth-light), var(--window-header))",
          }}
        />

        {/* Title Bar — warm wood header */}
        <div
          className="flex items-center justify-between px-5 py-3 select-none"
          style={{
            backgroundColor: "var(--window-header)",
          }}
        >
          {/* Left: Icon & Title */}
          <div className="flex items-center gap-3">
            <span className="text-xl">{icon}</span>
            <div>
              <h2
                className="text-base font-pixel-heading tracking-wide"
                style={{ color: "#f5efe4" }}
              >
                {title}
              </h2>
              <p
                className="text-xs mt-0.5"
                style={{ color: "#c4a882", fontFamily: "var(--font-body)" }}
              >
                {subtitle}
              </p>
            </div>
          </div>

          {/* Right: Close Button */}
          <button
            onClick={onClose}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-pixel-heading rounded-md transition-all"
            style={{
              backgroundColor: "var(--earth-main)",
              border: "1.5px solid var(--earth-light)",
              color: "#f5efe4",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "var(--wood-roof)";
              e.currentTarget.style.transform = "translateY(-1px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "var(--earth-main)";
              e.currentTarget.style.transform = "translateY(0)";
            }}
            title="Return to world view"
          >
            ← Back to World
          </button>
        </div>

        {/* Content Area — warm parchment */}
        <div
          className="flex-1 overflow-y-auto p-6 sm:p-7"
          style={{ backgroundColor: "var(--window-bg)" }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
