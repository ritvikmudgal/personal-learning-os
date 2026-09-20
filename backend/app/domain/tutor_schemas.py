"""Pydantic schemas for structured LLM operations in Layer 4 tutor engine."""

from pydantic import BaseModel, Field


class IntentClassificationSchema(BaseModel):
    """Schema for intent classification from user messages."""

    intent: str = Field(
        default="teach",
        description="Intent type: 'teach', 'explain', 'struggling', 'review', or 'override'",
    )
    target_concept: str = Field(
        default="",
        description="Extracted or requested target concept name",
    )


class ConceptResolutionSchema(BaseModel):
    """Schema for concept resolution against the Concept Graph."""

    matched_id: int | None = Field(
        default=None,
        description="Matched concept ID in Concept Graph if found",
    )
    matched_name: str = Field(
        default="",
        description="Resolved concept name",
    )
    is_new: bool = Field(
        default=False,
        description="Whether this is a newly proposed concept candidate",
    )


class TeachingPlanSchema(BaseModel):
    """Schema for structured teaching plan output."""

    steps: list[str] = Field(
        default_factory=list,
        description="List of step-by-step teaching plan items",
    )


class LearnerResponseAssessmentSchema(BaseModel):
    """Schema for evaluating learner response turns."""

    result_quality: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Quality rating of learner understanding (0.0 to 1.0)",
    )
    is_sufficient: bool = Field(
        default=True,
        description="Whether explanation/response demonstrates sufficient understanding",
    )
    misconception_detected: str | None = Field(
        default=None,
        description="Description of detected misconception if any",
    )
    feedback: str = Field(
        default="Evaluation completed.",
        description="Feedback or assessment notes",
    )
