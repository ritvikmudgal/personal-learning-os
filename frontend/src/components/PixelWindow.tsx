import React from "react";
import { NavTab } from "./PixelEnvironment";

interface PixelWindowProps {
  title: string;
  subtitle: string;
  icon: string;
  activeTab: NavTab;
  onClose: () => void;
  children: React.ReactNode;
}

export const PixelWindow: React.FC<PixelWindowProps> = ({
  title,
  subtitle,
  icon,
  onClose,
  children,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/40 backdrop-blur-[2px] animate-fade-in">
      <div
        className="pixel-window w-full max-w-5xl h-[84vh] flex flex-col overflow-hidden relative"
        style={{
          boxShadow: "0 16px 48px rgba(0, 0, 0, 0.6), 0 0 0 4px var(--window-border)",
        }}
      >
        {/* Retro Title Bar */}
        <div
          className="flex items-center justify-between px-4 py-2.5 border-b-2 select-none"
          style={{
            backgroundColor: "var(--window-header)",
            borderColor: "var(--window-border)",
          }}
        >
          {/* Left: Icon & Title */}
          <div className="flex items-center gap-3">
            <span className="text-lg">{icon}</span>
            <div>
              <h2
                className="text-sm font-pixel-heading tracking-wide"
                style={{ color: "var(--window-accent)" }}
              >
                {title}
              </h2>
              <p
                className="text-xs font-pixel-mono"
                style={{ color: "var(--window-text-muted)" }}
              >
                {subtitle}
              </p>
            </div>
          </div>

          {/* Right: Window Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-2.5 py-0.5 text-xs font-pixel-heading rounded border transition-colors"
              style={{
                backgroundColor: "var(--wood-roof)",
                borderColor: "#b3472b",
                color: "#ffffff",
              }}
              title="Close window to enter world view"
            >
              ✖ CLOSE
            </button>
          </div>
        </div>

        {/* Inner Window Scrollable Content Area */}
        <div
          className="flex-1 overflow-y-auto p-5 sm:p-6"
          style={{ backgroundColor: "var(--window-bg)" }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
