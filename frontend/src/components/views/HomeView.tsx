import React from "react";
import { NavTab } from "../PixelEnvironment";

interface HomeViewProps {
  onNavigate: (tab: NavTab) => void;
}

export const HomeView: React.FC<HomeViewProps> = ({ onNavigate }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Welcome Sanctuary Header */}
      <div
        className="pixel-card"
        style={{
          padding: "1.5rem",
          background: "linear-gradient(135deg, #fdfbf7 0%, #f4eee1 100%)",
          borderLeft: "4px solid var(--accent-moss)",
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
        }}
      >
        <div>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.25rem",
              fontWeight: 700,
              color: "var(--accent-moss-text)",
              margin: "0 0 0.35rem 0",
            }}
          >
            Welcome to Your Personal Learning Sanctuary
          </h1>
          <p
            style={{
              fontSize: "0.875rem",
              color: "var(--ink-secondary)",
              margin: 0,
              lineHeight: 1.5,
            }}
          >
            A quiet, reflective digital space built for deep comprehension and knowledge growth.
          </p>
        </div>
        <button
          onClick={() => onNavigate("learn")}
          className="pixel-button pixel-button-primary"
          style={{ whiteSpace: "nowrap", fontSize: "0.85rem" }}
        >
          💬 Begin Guided Study Session
        </button>
      </div>

      {/* Daily Target & Core Stats Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "1rem",
        }}
      >
        {/* Daily Target */}
        <div
          className="pixel-card"
          style={{
            padding: "1.25rem",
            background: "#ffffff",
            border: "1px solid var(--wood-light)",
          }}
        >
          <div
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.05em",
              color: "#b46912",
              textTransform: "uppercase",
              marginBottom: "0.35rem",
            }}
          >
            🎯 Daily Focus Target
          </div>
          <div
            style={{
              fontSize: "1rem",
              fontWeight: 600,
              color: "var(--ink-primary)",
              marginBottom: "0.75rem",
            }}
          >
            Python Asynchronous Traversal
          </div>
          <div
            style={{
              width: "100%",
              height: "8px",
              background: "var(--paper-dark)",
              borderRadius: "4px",
              overflow: "hidden",
              marginBottom: "0.5rem",
            }}
          >
            <div
              style={{
                width: "65%",
                height: "100%",
                background: "linear-gradient(90deg, #d9822b 0%, #e0a353 100%)",
                borderRadius: "4px",
              }}
            />
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "0.78rem",
              color: "var(--ink-muted)",
              fontFamily: "var(--font-mono)",
            }}
          >
            <span>Progress: 65%</span>
            <span>Target: 45 mins</span>
          </div>
        </div>

        {/* Concept Graph State */}
        <div
          className="pixel-card"
          style={{
            padding: "1.25rem",
            background: "#ffffff",
            border: "1px solid var(--wood-light)",
          }}
        >
          <div
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.05em",
              color: "var(--accent-moss-text)",
              textTransform: "uppercase",
              marginBottom: "0.35rem",
            }}
          >
            🌱 Concept Graph State
          </div>
          <div
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              fontFamily: "var(--font-heading)",
              color: "var(--ink-primary)",
              marginBottom: "0.25rem",
            }}
          >
            42{" "}
            <span
              style={{
                fontSize: "0.85rem",
                fontWeight: 400,
                color: "var(--ink-secondary)",
              }}
            >
              Concepts Linked
            </span>
          </div>
          <div
            style={{
              fontSize: "0.78rem",
              color: "var(--ink-muted)",
              lineHeight: 1.4,
            }}
          >
            DFS / BFS Traversal Engine Active • Cycle Detection Ready
          </div>
        </div>

        {/* Learner Model */}
        <div
          className="pixel-card"
          style={{
            padding: "1.25rem",
            background: "#ffffff",
            border: "1px solid var(--wood-light)",
          }}
        >
          <div
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.05em",
              color: "#2b6b84",
              textTransform: "uppercase",
              marginBottom: "0.35rem",
            }}
          >
            📊 Learner Knowledge State
          </div>
          <div
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              fontFamily: "var(--font-heading)",
              color: "var(--ink-primary)",
              marginBottom: "0.25rem",
            }}
          >
            6{" "}
            <span
              style={{
                fontSize: "0.85rem",
                fontWeight: 400,
                color: "var(--ink-secondary)",
              }}
            >
              Active Dimensions
            </span>
          </div>
          <div
            style={{
              fontSize: "0.78rem",
              color: "var(--ink-muted)",
              lineHeight: 1.4,
            }}
          >
            Mastery, Strength, Decay, Confidence, Reliability, Misconceptions
          </div>
        </div>
      </div>

      {/* World Locations Map */}
      <div>
        <h2
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "1rem",
            fontWeight: 700,
            color: "var(--ink-primary)",
            marginBottom: "0.85rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          🏞️ World Locations & Modules
        </h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "1rem",
          }}
        >
          {/* Study Cottage */}
          <div
            onClick={() => onNavigate("learn")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "var(--accent-moss)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>💬</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Study Cottage
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-moss-text)",
                marginBottom: "0.4rem",
              }}
            >
              Interactive Guided Tutor
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Talk with your local AI study assistant for guided explanations & tailored practice.
            </p>
          </div>

          {/* Knowledge Graph */}
          <div
            onClick={() => onNavigate("knowledge")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "var(--accent-sky)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>🌱</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Learning Garden
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-sky-text)",
                marginBottom: "0.4rem",
              }}
            >
              Concept Graph & DAG
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Explore prerequisite concept relationships, gaps, and mastery visualizers.
            </p>
          </div>

          {/* Assessments */}
          <div
            onClick={() => onNavigate("assessments")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "var(--accent-warm)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>📝</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Mastery Shrine
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-warm-text)",
                marginBottom: "0.4rem",
              }}
            >
              Diagnostics & Practice
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Test your understanding with adaptive diagnostics and track mastery growth.
            </p>
          </div>

          {/* Notes */}
          <div
            onClick={() => onNavigate("notes")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "var(--accent-moss)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>📓</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Writing Gazebo
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-moss-text)",
                marginBottom: "0.4rem",
              }}
            >
              Journal & Insights
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Record reflections, mental models, code notes, and personalized study logs.
            </p>
          </div>

          {/* Library */}
          <div
            onClick={() => onNavigate("library")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.borderColor = "var(--accent-plum)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--wood-light)";
            }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>📚</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Archive Library
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-plum-text)",
                marginBottom: "0.4rem",
              }}
            >
              Material & RAG Store
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Ingest textbooks, PDFs, and code docs into local semantic search retrieval.
            </p>
          </div>

          {/* Learner State */}
          <div
            onClick={() => onNavigate("learner_state")}
            className="pixel-card"
            style={{
              padding: "1.25rem",
              cursor: "pointer",
              transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease",
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
            <div style={{ fontSize: "1.5rem", marginBottom: "0.4rem" }}>📊</div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "var(--ink-primary)",
                marginBottom: "0.2rem",
              }}
            >
              Monolith of Reflection
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "#2b6b84",
                marginBottom: "0.4rem",
              }}
            >
              6D Learner State
            </div>
            <p
              style={{
                fontSize: "0.8rem",
                color: "var(--ink-secondary)",
                margin: 0,
                lineHeight: 1.4,
              }}
            >
              Track multi-dimensional retention, decay state, confidence, and misconceptions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

