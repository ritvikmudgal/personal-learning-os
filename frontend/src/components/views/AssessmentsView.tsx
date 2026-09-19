import React from "react";

export const AssessmentsView: React.FC = () => {
  const assessments = [
    {
      type: "Quick Diagnostic",
      typeColor: "var(--accent-moss)",
      typeBg: "var(--accent-moss-bg)",
      title: "Python Event Loop & Async Tasks",
      description: "5 targeted questions to verify current mastery and detect hidden misconceptions.",
      duration: "5 mins",
      icon: "⚡",
    },
    {
      type: "Misconception Probe",
      typeColor: "var(--accent-sky)",
      typeBg: "var(--accent-sky-bg)",
      title: "Memory Management & Pointers",
      description: "Diagnostic test specifically designed to detect reference counting misunderstandings.",
      duration: "10 mins",
      icon: "🔍",
    },
    {
      type: "Full Exam Session",
      typeColor: "var(--accent-amber)",
      typeBg: "var(--accent-amber-bg)",
      title: "Comprehensive Systems Exam",
      description: "Multi-concept exam covering algorithms, data structures, and memory models.",
      duration: "30 mins",
      icon: "🏆",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div
        className="p-5 rounded-lg"
        style={{
          backgroundColor: "var(--accent-amber-bg)",
          border: "1.5px solid var(--accent-amber)",
        }}
      >
        <h2
          className="text-base font-pixel-heading flex items-center gap-2 mb-1"
          style={{ color: "var(--window-text-primary)" }}
        >
          <span>📝</span> Shrine of Mastery
        </h2>
        <p className="text-sm" style={{ color: "var(--window-text-muted)" }}>
          Test your understanding with targeted quizzes, diagnostic probes, and comprehensive exams.
        </p>
      </div>

      {/* Assessment Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {assessments.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-lg flex flex-col justify-between transition-all"
            style={{
              backgroundColor: "var(--window-card)",
              border: "1.5px solid var(--window-border-light)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = item.typeColor;
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 16px rgba(92, 61, 46, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--window-border-light)";
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div>
              {/* Type badge */}
              <div className="flex items-center justify-between mb-3">
                <span
                  className="pixel-badge"
                  style={{
                    backgroundColor: item.typeBg,
                    borderColor: item.typeColor,
                    color: item.typeColor,
                  }}
                >
                  {item.icon} {item.type}
                </span>
                <span className="text-xs" style={{ color: "var(--window-text-faint)" }}>
                  ~{item.duration}
                </span>
              </div>

              <h3
                className="text-base font-medium mb-2"
                style={{ color: "var(--window-text-primary)" }}
              >
                {item.title}
              </h3>
              <p
                className="text-sm mb-5 leading-relaxed"
                style={{ color: "var(--window-text-muted)" }}
              >
                {item.description}
              </p>
            </div>

            <button className="pixel-button pixel-button-primary w-full text-xs">
              Begin Assessment
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
