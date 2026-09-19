import React from "react";

interface DimensionCard {
  name: string;
  value: string;
  badge: string;
  badgeBg: string;
  badgeColor: string;
  desc: string;
  icon: string;
  detail: string;
}

export const LearnerStateView: React.FC = () => {
  const stateDimensions: DimensionCard[] = [
    {
      name: "Mastery Probability",
      value: "78%",
      badge: "High Mastery",
      badgeBg: "var(--accent-moss-bg)",
      badgeColor: "var(--accent-moss-text)",
      desc: "Estimated probability of solving complex problems correctly.",
      icon: "🎯",
      detail: "Based on Bayesian Knowledge Tracing across 14 diagnostic evaluations.",
    },
    {
      name: "Knowledge Strength",
      value: "8.4 days",
      badge: "Optimal",
      badgeBg: "var(--accent-sky-bg)",
      badgeColor: "var(--accent-sky-text)",
      desc: "Memory half-life retention parameter under spaced retrieval.",
      icon: "⚡",
      detail: "Represents stability S in the half-life memory model.",
    },
    {
      name: "Forgetting State",
      value: "0.12 (Low Decay)",
      badge: "Stable",
      badgeBg: "#fef3c7",
      badgeColor: "#92400e",
      desc: "Current position on the Ebbinghaus exponential forgetting curve.",
      icon: "⏳",
      detail: "R = e^(-t/S), indicating 88% estimated retrieval likelihood today.",
    },
    {
      name: "Confidence Score",
      value: "85%",
      badge: "Well-Calibrated",
      badgeBg: "var(--accent-moss-bg)",
      badgeColor: "var(--accent-moss-text)",
      desc: "Self-assessed metacognitive confidence rating vs actual accuracy.",
      icon: "🧠",
      detail: "Low overconfidence gap; strong self-awareness detected.",
    },
    {
      name: "Evidence Reliability",
      value: "High (14 evaluations)",
      badge: "Robust Data",
      badgeBg: "var(--accent-sky-bg)",
      badgeColor: "var(--accent-sky-text)",
      desc: "Diagnostic test count & empirical observation density.",
      icon: "📊",
      detail: "Sufficient data density for high-confidence mastery estimation.",
    },
    {
      name: "Misconception Severity",
      value: "None Detected",
      badge: "Clear",
      badgeBg: "var(--accent-moss-bg)",
      badgeColor: "var(--accent-moss-text)",
      desc: "Flagged cognitive traps or faulty mental models.",
      icon: "🛡️",
      detail: "No systemic error patterns observed in recent assessments.",
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Overview Banner */}
      <div
        className="pixel-card"
        style={{
          padding: "1.5rem",
          background: "linear-gradient(135deg, #fdfbf7 0%, #f4eee1 100%)",
          borderLeft: "4px solid #2b6b84",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
          <span style={{ fontSize: "1.5rem" }}>📊</span>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.15rem",
              fontWeight: 700,
              color: "var(--ink-primary)",
              margin: 0,
            }}
          >
            Multi-Dimensional Learner Knowledge State
          </h2>
        </div>
        <p
          style={{
            fontSize: "0.875rem",
            color: "var(--ink-secondary)",
            margin: 0,
            lineHeight: 1.5,
          }}
        >
          The learner’s state is NOT a single scalar score. Each user × concept pair maintains 6 independent cognitive dimensions to model true understanding and guide personalized review schedules.
        </p>
      </div>

      {/* 6 Dimensions Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "1.1rem",
        }}
      >
        {stateDimensions.map((dim, idx) => (
          <div
            key={idx}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              gap: "0.75rem",
              background: "#ffffff",
              border: "1px solid var(--wood-light)",
              transition: "transform 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "#2b6b84";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            {/* Header row */}
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "0.5rem",
                }}
              >
                <span style={{ fontSize: "1.4rem" }}>{dim.icon}</span>
                <span
                  style={{
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    padding: "0.2rem 0.55rem",
                    borderRadius: "4px",
                    backgroundColor: dim.badgeBg,
                    color: dim.badgeColor,
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  {dim.badge}
                </span>
              </div>

              <div
                style={{
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  fontFamily: "var(--font-heading)",
                  color: "var(--ink-primary)",
                  marginBottom: "0.2rem",
                }}
              >
                {dim.value}
              </div>

              <div
                style={{
                  fontSize: "0.88rem",
                  fontWeight: 600,
                  color: "var(--ink-primary)",
                  marginBottom: "0.4rem",
                }}
              >
                {dim.name}
              </div>

              <p
                style={{
                  fontSize: "0.8rem",
                  color: "var(--ink-secondary)",
                  margin: 0,
                  lineHeight: 1.4,
                }}
              >
                {dim.desc}
              </p>
            </div>

            {/* Footer detail */}
            <div
              style={{
                paddingTop: "0.6rem",
                borderTop: "1px dashed var(--wood-light)",
                fontSize: "0.75rem",
                color: "var(--ink-muted)",
                fontFamily: "var(--font-mono)",
                lineHeight: 1.35,
              }}
            >
              {dim.detail}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

