"""SQLAlchemy ORM models for the Personal Learning OS domain.

This module defines the complete database schema covering:
- Learner profiles
- Concepts and concept relationships (lightweight knowledge graph)
- Learner knowledge state per concept (multi-dimensional)
- Evidence records (persistent learning evidence)
- Learning events/history
- Assessment records
- Misconceptions (persistent, with severity and status tracking)
- Uploaded material metadata

Design decisions:
- JSON columns used for flexible/evolving fields (preferences, detected misconceptions)
- Concept relationships form a directed graph stored in a junction table
- Knowledge state tracks 6 independent dimensions per (learner, concept) pair
- Evidence is never deleted — learner state is an evolving estimate over evidence history
- Timestamps use UTC throughout
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# --- Enums ---

class RelationshipType(str, enum.Enum):
    """Types of relationships between concepts."""
    PREREQUISITE = "prerequisite"   # source is prerequisite of target
    RELATED = "related"             # concepts are related
    PART_OF = "part_of"             # source is part of target
    BUILDS_ON = "builds_on"         # source builds on target
    CONTRASTS = "contrasts"         # concepts contrast/oppose each other
    EXTENDS = "extends"             # source extends target
    APPLIED_IN = "applied_in"       # source is applied in target


class EventType(str, enum.Enum):
    """Types of learning events."""
    STUDY = "study"
    REVIEW = "review"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    AI_CONVERSATION = "ai_conversation"
    MATERIAL_READ = "material_read"


class AssessmentType(str, enum.Enum):
    """Types of assessments."""
    QUIZ = "quiz"
    EXAM = "exam"
    SELF_ASSESSMENT = "self_assessment"
    AI_ASSESSMENT = "ai_assessment"
    PRACTICE_PROBLEM = "practice_problem"


class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for concepts."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EvidenceType(str, enum.Enum):
    """Types of evidence that inform learner state.

    Each evidence type represents a different kind of observation
    about a learner's understanding of a concept.
    """
    STUDY_SESSION = "study_session"
    READING = "reading"
    EXPLANATION = "explanation"           # learner explained the concept
    ASSESSMENT_ANSWER = "assessment_answer"
    SOLVED_PROBLEM = "solved_problem"
    REPEATED_SUCCESS = "repeated_success"
    REPEATED_FAILURE = "repeated_failure"
    AI_OBSERVATION = "ai_observation"     # AI/teacher observation
    SELF_REPORT = "self_report"           # learner self-assessment


class MisconceptionStatus(str, enum.Enum):
    """Status of a tracked misconception."""
    ACTIVE = "active"           # currently held by learner
    WEAKENING = "weakening"     # showing signs of resolution
    RESOLVED = "resolved"       # no longer held


# --- Models ---

class LearnerProfile(Base):
    """A learner/user profile."""
    __tablename__ = "learner_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    knowledge_states: Mapped[list["KnowledgeState"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
    learning_events: Mapped[list["LearningEvent"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
    assessment_records: Mapped[list["AssessmentRecord"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
    misconceptions: Mapped[list["Misconception"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
    materials: Mapped[list["MaterialMetadata"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
    evidence_records: Mapped[list["Evidence"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )


class Concept(Base):
    """A learning concept/topic in the knowledge graph."""
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    difficulty_level: Mapped[DifficultyLevel | None] = mapped_column(
        Enum(DifficultyLevel), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships for the knowledge graph edges
    outgoing_relationships: Mapped[list["ConceptRelationship"]] = relationship(
        back_populates="source_concept",
        foreign_keys="ConceptRelationship.source_concept_id",
        cascade="all, delete-orphan",
    )
    incoming_relationships: Mapped[list["ConceptRelationship"]] = relationship(
        back_populates="target_concept",
        foreign_keys="ConceptRelationship.target_concept_id",
        cascade="all, delete-orphan",
    )
    knowledge_states: Mapped[list["KnowledgeState"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )


class ConceptRelationship(Base):
    """A directed edge in the concept knowledge graph.

    Example: "Algebra" --[prerequisite]--> "Calculus"
    means Algebra is a prerequisite of Calculus.
    """
    __tablename__ = "concept_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    target_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType), nullable=False
    )
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    source_concept: Mapped["Concept"] = relationship(
        back_populates="outgoing_relationships",
        foreign_keys=[source_concept_id],
    )
    target_concept: Mapped["Concept"] = relationship(
        back_populates="incoming_relationships",
        foreign_keys=[target_concept_id],
    )


class KnowledgeState(Base):
    """Multi-dimensional learner state for a specific concept.

    This is the core of the adaptive learning model. Each dimension
    represents a different aspect of the learner's relationship with
    a concept. Dimensions are independent — they can represent states
    like overconfidence (high confidence, low mastery) or underconfidence
    (low confidence, high mastery).

    Dimensions:
    - mastery_probability: Estimated probability that the learner has
      mastered this concept (0.0 = no mastery, 1.0 = full mastery)
    - knowledge_strength: How durable/stable the knowledge is. High
      strength means the knowledge is well-consolidated and resistant
      to forgetting (0.0 = fragile, 1.0 = deeply consolidated)
    - forgetting_state: Current level of forgetting. Increases with time
      since last reinforcement. Does NOT delete knowledge — only represents
      the current accessibility estimate (0.0 = fresh, 1.0 = fully forgotten)
    - confidence: Learner's self-reported confidence. Updated ONLY from
      explicit confidence data, never auto-calculated (0.0 = no confidence,
      1.0 = fully confident)
    - evidence_reliability: How much evidence backs the current state
      estimate. More diverse, high-quality evidence = higher reliability
      (0.0 = no evidence, 1.0 = abundant reliable evidence)
    - misconception_severity: Aggregate severity of active misconceptions
      about this concept (0.0 = no misconceptions, 1.0 = severe)
    """
    __tablename__ = "knowledge_states"
    __table_args__ = (
        UniqueConstraint("learner_id", "concept_id", name="uq_learner_concept"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )

    # --- 6 independent dimensions ---
    mastery_probability: Mapped[float] = mapped_column(Float, default=0.0)
    knowledge_strength: Mapped[float] = mapped_column(Float, default=0.0)
    forgetting_state: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_reliability: Mapped[float] = mapped_column(Float, default=0.0)
    misconception_severity: Mapped[float] = mapped_column(Float, default=0.0)

    # --- Timestamps ---
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_studied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_reinforced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="knowledge_states")
    concept: Mapped["Concept"] = relationship(back_populates="knowledge_states")


class Evidence(Base):
    """A persistent record of evidence about a learner's understanding.

    Evidence is never deleted. The learner's knowledge state is an
    evolving estimate computed from the full evidence history.

    Each record captures a single observation — e.g. a correct answer
    on a quiz question, an explanation the learner gave, a study session
    completion, or an AI observation about understanding.
    """
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType), nullable=False
    )
    result_quality: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    misconception_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="evidence_records")


class LearningEvent(Base):
    """A record of a learning activity."""
    __tablename__ = "learning_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="learning_events")


class AssessmentRecord(Base):
    """A record of an assessment/quiz/exam taken by a learner."""
    __tablename__ = "assessment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(
        Enum(AssessmentType), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    misconceptions_detected: Mapped[list | None] = mapped_column(
        JSON, nullable=True, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(
        back_populates="assessment_records"
    )


class Misconception(Base):
    """A tracked misconception for a learner about a specific concept.

    Misconceptions are persistent records that track specific wrong mental
    models a learner holds. They exist independently from the general mastery
    state — a learner can have high mastery but still hold a specific
    misconception about an edge case.

    A learner can have multiple misconceptions about one concept.

    Example:
        Concept: Recursion
        Misconception: "Each recursive call immediately returns before
        the next call executes."

    The severity, status, and evidence_count fields allow tracking the
    lifecycle of a misconception from detection through resolution.
    """
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[MisconceptionStatus] = mapped_column(
        Enum(MisconceptionStatus), default=MisconceptionStatus.ACTIVE
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_observed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    evidence_count: Mapped[int] = mapped_column(Integer, default=1)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_prerequisite_ids: Mapped[list | None] = mapped_column(
        JSON, nullable=True, default=list
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="misconceptions")


class MaterialMetadata(Base):
    """Metadata for uploaded learning materials (PDFs, notes, etc.)."""
    __tablename__ = "material_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    associated_concept_ids: Mapped[list | None] = mapped_column(
        JSON, nullable=True, default=list
    )
    upload_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="materials")
