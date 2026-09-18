"""SQLAlchemy ORM models for the Personal Learning OS domain.

This module defines the complete database schema covering:
- Learner profiles
- Concepts and concept relationships (lightweight knowledge graph)
- Learner knowledge state per concept
- Learning events/history
- Assessment records
- Misconceptions
- Uploaded material metadata

Design decisions:
- JSON columns used for flexible/evolving fields (preferences, detected misconceptions)
- Concept relationships form a directed graph stored in a junction table
- Knowledge state tracks both self-reported confidence and demonstrated understanding
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
    """Tracks a learner's understanding of a specific concept.

    This is the core of the adaptive learning model. It tracks:
    - understanding_level: Overall understanding (0.0 to 1.0)
    - confidence: Learner's self-reported confidence (0.0 to 1.0)
    - demonstrated_level: Score from assessments (0.0 to 1.0)
    - decay_factor: How quickly knowledge decays without review
    """
    __tablename__ = "knowledge_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    understanding_level: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    demonstrated_level: Mapped[float] = mapped_column(Float, default=0.0)
    decay_factor: Mapped[float] = mapped_column(Float, default=0.5)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_studied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    learner: Mapped["LearnerProfile"] = relationship(back_populates="knowledge_states")
    concept: Mapped["Concept"] = relationship(back_populates="knowledge_states")


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

    Links to prerequisite concepts that may be the root cause.
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
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
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
