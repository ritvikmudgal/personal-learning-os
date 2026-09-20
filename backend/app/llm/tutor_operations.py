import ast
import json
import re
from typing import Any, Type, TypeVar
from pydantic import BaseModel

from app.domain.tutor_schemas import (
    ConceptResolutionSchema,
    IntentClassificationSchema,
    LearnerResponseAssessmentSchema,
    TeachingPlanSchema,
)
from app.llm.provider import GenerateOptions, LLMProvider
from app.utils.logging import get_logger

logger = get_logger("llm.tutor_operations")

T = TypeVar("T", bound=BaseModel)


def parse_structured_llm_output(
    text: str,
    schema_cls: Type[T],
    fallback_instance: T | None = None,
) -> T:
    """Safely parse LLM text into a Pydantic model with a 5-step fallback pipeline:

    1. Extract JSON/Python dict substring from code blocks or raw text braces.
    2. Try standard json.loads().
    3. Try ast.literal_eval() for Python dict syntax (single quotes, True/False/None).
    4. Pydantic schema validation.
    5. Fallback instance return on failure.
    """
    if fallback_instance is None:
        fallback_instance = schema_cls()

    text_clean = text.strip()
    match = re.search(r"```(?:json|python)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
    if match:
        text_clean = match.group(1)
    else:
        first_brace = text_clean.find("{")
        last_brace = text_clean.rfind("}")
        if first_brace != -1 and last_brace != -1:
            text_clean = text_clean[first_brace : last_brace + 1]

    parsed_dict: dict[str, Any] | None = None

    # Step 1: json.loads
    try:
        parsed_dict = json.loads(text_clean)
    except Exception:
        pass

    # Step 2: ast.literal_eval for single-quoted dicts
    if parsed_dict is None:
        try:
            val = ast.literal_eval(text_clean)
            if isinstance(val, dict):
                parsed_dict = val
        except Exception:
            pass

    # Step 3: if dictionary extraction failed completely
    if parsed_dict is None:
        logger.warning(
            "Failed to parse dict from LLM output for schema %s. Snippet: %s",
            schema_cls.__name__,
            text[:200],
        )
        return fallback_instance

    # Step 4: Validate against Pydantic schema
    try:
        return schema_cls.model_validate(parsed_dict)
    except Exception as e:
        logger.warning(
            "Pydantic validation failed for %s: %s. Dict: %s",
            schema_cls.__name__,
            e,
            parsed_dict,
        )
        return fallback_instance


class TutorLLMOperations:
    """Helper class providing structured LLM operations for the learning engine."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def classify_learning_intent(self, user_input: str) -> dict[str, str]:
        """Classify user intent (e.g. teach, explain, review, struggling, override) and extract target concept."""
        system_prompt = (
            "You are a learning intent classifier for a personal tutor OS. "
            "Analyze the user's message and classify the intent into one of: "
            "'teach' (wants a full guided teaching path), 'explain' (wants a quick explanation), "
            "'struggling' (expressing confusion/mistake), 'review' (wants to review a concept), "
            "or 'override' (wants to skip prerequisites/already knows prerequisites). "
            "Also extract the target concept name. "
            "Return valid JSON only in this format: "
            '{"intent": "teach|explain|struggling|review|override", "target_concept": "Concept Name"}'
        )
        opts = GenerateOptions(temperature=0.1, max_tokens=150)
        resp = await self.provider.generate(prompt=user_input, system_prompt=system_prompt, options=opts)
        
        parsed = parse_structured_llm_output(
            resp.text,
            IntentClassificationSchema,
            fallback_instance=IntentClassificationSchema(intent="teach", target_concept=user_input.strip()),
        )
        
        target = parsed.target_concept.strip() if parsed.target_concept else user_input.strip()
        if target.lower() in ("none", "null", "undefined", "n/a"):
            target = user_input.strip()

        return {"intent": parsed.intent, "target_concept": target}

    async def resolve_concept_name(self, raw_concept: str, available_concepts: list[dict]) -> dict[str, Any]:
        """Match raw concept string against existing graph concepts or suggest new concept details."""
        concepts_summary = ", ".join([f"'{c['name']}' (id={c['id']})" for c in available_concepts[:30]])
        system_prompt = (
            "You are a concept resolver for a knowledge graph. "
            f"Existing concepts in graph: [{concepts_summary}]. "
            "Match the user's requested concept to an existing concept if it matches closely. "
            "Return valid JSON only: "
            '{"matched_id": int or null, "matched_name": "string", "is_new": bool}'
        )
        opts = GenerateOptions(temperature=0.1, max_tokens=150)
        resp = await self.provider.generate(
            prompt=f"User concept request: '{raw_concept}'",
            system_prompt=system_prompt,
            options=opts,
        )
        
        parsed = parse_structured_llm_output(
            resp.text,
            ConceptResolutionSchema,
            fallback_instance=ConceptResolutionSchema(matched_id=None, matched_name=raw_concept, is_new=True),
        )
        
        matched_name = parsed.matched_name.strip() if parsed.matched_name else raw_concept
        if matched_name.lower() in ("none", "null", "undefined", "n/a"):
            matched_name = raw_concept

        return {
            "matched_id": parsed.matched_id,
            "matched_name": matched_name,
            "is_new": parsed.is_new if parsed.matched_id is None else False,
        }

    async def generate_teaching_plan(
        self,
        target_concept: str,
        weak_prereqs: list[str],
        known_prereqs: list[str],
        active_misconceptions: list[str],
    ) -> list[str]:
        """Generate a personalized 3-4 step teaching plan."""
        context_str = f"Target: {target_concept}\nWeak Prerequisites: {weak_prereqs}\nStrong Prerequisites: {known_prereqs}\nActive Misconceptions: {active_misconceptions}"
        system_prompt = (
            "You are an expert pedagogical planner. Create a concise 3 to 4 step teaching plan for the student. "
            "If weak prerequisites exist, include step 1 addressing them first. "
            "Return valid JSON only: {'steps': ['Step 1 description', 'Step 2 description', ...]}"
        )
        opts = GenerateOptions(temperature=0.3, max_tokens=250)
        resp = await self.provider.generate(prompt=context_str, system_prompt=system_prompt, options=opts)
        
        parsed = parse_structured_llm_output(
            resp.text,
            TeachingPlanSchema,
            fallback_instance=TeachingPlanSchema(steps=[]),
        )
        
        steps = [s for s in parsed.steps if isinstance(s, str) and s.strip()]
        if not steps:
            if weak_prereqs:
                steps = [f"Review foundation: {', '.join(weak_prereqs)}", f"Introduce core ideas of {target_concept}", f"Practice and verify {target_concept}"]
            else:
                steps = [f"Introduce core concept: {target_concept}", f"Explore key mechanisms and examples", f"Verify understanding of {target_concept}"]
        return steps

    async def generate_explanation(
        self,
        formatted_context: str,
        strategy: str = "direct",
    ) -> str:
        """Generate a warm, clear, concept-grounded explanation based on assembled context budget."""
        system_prompt = (
            "You are a warm, encouraging personal AI study tutor inside a serene learning sanctuary. "
            "Your tone is calm, clear, insightful, and pedagogical (never overly formal, never generic bot-speak). "
            "Use the provided learner context (prerequisites, misconceptions, past knowledge, uploaded materials) to deliver your explanation. "
            "If uploaded materials or prior knowledge are present in context, weave them naturally into your response. "
            "Keep your response structured, well-formatted, readable, and engaging. "
            "End with a thoughtful, Socratic follow-up question to check the learner's understanding."
        )
        prompt = f"Teaching Strategy: {strategy}\n\nContext:\n{formatted_context}\n\nPlease explain the concept to the learner."
        opts = GenerateOptions(temperature=0.6, max_tokens=700)
        resp = await self.provider.generate(prompt=prompt, system_prompt=system_prompt, options=opts)
        return resp.text.strip()

    def deterministic_concept_resolution(self, raw_concept: str, available_concepts: list[dict]) -> dict[str, Any] | None:
        """Fast Python-side exact/substring matcher against Concept Graph without calling LLM."""
        raw_clean = raw_concept.strip().lower()
        if not raw_clean or len(raw_clean) < 2:
            return None

        # Sort concepts by name length descending so longer, more specific concepts match first
        sorted_concepts = sorted(available_concepts, key=lambda c: len(c.get("name", "")), reverse=True)

        # 1. Exact match
        for c in sorted_concepts:
            c_name = c["name"].strip().lower()
            if c_name == raw_clean:
                return {"matched_id": c["id"], "matched_name": c["name"], "is_new": False}

        # 2. Word boundary or substring match (longer concepts checked first)
        for c in sorted_concepts:
            c_name = c["name"].strip().lower()
            if len(c_name) >= 3 and (re.search(rf"\b{re.escape(c_name)}\b", raw_clean) or c_name in raw_clean):
                return {"matched_id": c["id"], "matched_name": c["name"], "is_new": False}

        return None

    async def stream_explanation(
        self,
        formatted_context: str,
        strategy: str = "direct",
    ):
        """Stream explanation token by token for low latency."""
        system_prompt = (
            "You are a warm, encouraging personal AI study tutor inside a serene learning sanctuary. "
            "Your tone is calm, clear, insightful, and pedagogical (never overly formal, never generic bot-speak). "
            "Use the provided learner context (prerequisites, misconceptions, past knowledge, uploaded materials) to deliver your explanation. "
            "Keep explanations concise, focused, structured, readable, and engaging (roughly 300 to 500 words). "
            "End with a thoughtful follow-up question to check understanding."
        )
        prompt = f"Teaching Strategy: {strategy}\n\nContext:\n{formatted_context}\n\nPlease explain the concept to the learner."
        opts = GenerateOptions(temperature=0.5, max_tokens=500)

        if hasattr(self.provider, "generate_stream"):
            async for token in self.provider.generate_stream(prompt=prompt, system_prompt=system_prompt, options=opts):
                yield token
        else:
            resp = await self.provider.generate(prompt=prompt, system_prompt=system_prompt, options=opts)
            yield resp.text.strip()

    async def evaluate_learner_response(
        self,
        learner_response: str,
        current_concept: str,
        expected_context: str,
    ) -> dict[str, Any]:
        """Evaluate a student's response turn for understanding quality and potential misconceptions."""
        system_prompt = (
            "You are an educational evaluator for an adaptive tutor. "
            "Evaluate the learner's response regarding the concept. "
            "Determine result_quality (float from 0.0 to 1.0, where 1.0 = full correct understanding, 0.5 = partial, 0.0 = completely incorrect). "
            "Check if any misconception was expressed. "
            "Return valid JSON only in this format: "
            '{"result_quality": 0.85, "is_sufficient": true, "misconception_detected": "optional description or null", "feedback": "short feedback note"}'
        )
        prompt = f"Concept: {current_concept}\nExpected Context: {expected_context}\nLearner Response: {learner_response}"
        opts = GenerateOptions(temperature=0.2, max_tokens=250)
        resp = await self.provider.generate(prompt=prompt, system_prompt=system_prompt, options=opts)
        
        parsed = parse_structured_llm_output(
            resp.text,
            LearnerResponseAssessmentSchema,
            fallback_instance=LearnerResponseAssessmentSchema(),
        )
        
        quality = max(0.0, min(1.0, float(parsed.result_quality)))
        misc = parsed.misconception_detected
        if isinstance(misc, str):
            misc = misc.strip()
            if misc.lower() in ("none", "null", "undefined", "n/a", ""):
                misc = None

        return {
            "result_quality": quality,
            "is_sufficient": bool(parsed.is_sufficient),
            "misconception_detected": misc,
            "feedback": parsed.feedback or "Evaluation completed.",
        }


