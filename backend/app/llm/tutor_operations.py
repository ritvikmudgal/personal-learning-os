"""Tutor LLM operations helper — structured operations using the abstract LLMProvider.

Encapsulates LLM tasks required by the learning engine:
- Intent classification
- Concept name resolution
- Teaching plan generation
- Tailored explanation generation
- Learner response evaluation & structured evidence candidate extraction
"""

import json
import re
from typing import Any
from app.llm.provider import LLMProvider, GenerateOptions
from app.utils.logging import get_logger

logger = get_logger("llm.tutor_operations")


def _extract_json(text: str) -> dict[str, Any]:
    """Helper to safely parse JSON from LLM output, handling markdown code blocks."""
    text_clean = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
    if match:
        text_clean = match.group(1)
    else:
        first_brace = text_clean.find("{")
        last_brace = text_clean.rfind("}")
        if first_brace != -1 and last_brace != -1:
            text_clean = text_clean[first_brace : last_brace + 1]

    try:
        return json.loads(text_clean)
    except Exception as e:
        logger.warning("Failed to parse JSON from LLM output: %s. Raw text: %s", e, text[:200])
        return {}


class TutorLLMOperations:
    """Helper class providing structured LLM operations for the learning engine."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def classify_learning_intent(self, user_input: str) -> dict[str, str]:
        """Classify user intent (e.g. teach, explain, review, struggling) and extract target concept."""
        system_prompt = (
            "You are a learning intent classifier for a personal tutor OS. "
            "Analyze the user's message and classify the intent into one of: "
            "'teach' (wants a full guided teaching path), 'explain' (wants a quick explanation), "
            "'struggling' (expressing confusion/mistake), or 'review' (wants to review a concept). "
            "Also extract the target concept name. "
            "Return valid JSON only in this format: "
            '{"intent": "teach|explain|struggling|review", "target_concept": "Concept Name"}'
        )
        opts = GenerateOptions(temperature=0.1, max_tokens=150)
        resp = await self.provider.generate(prompt=user_input, system_prompt=system_prompt, options=opts)
        parsed = _extract_json(resp.text)
        intent = parsed.get("intent", "teach")
        target_concept = parsed.get("target_concept", user_input.strip())
        return {"intent": intent, "target_concept": target_concept}

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
        parsed = _extract_json(resp.text)
        return {
            "matched_id": parsed.get("matched_id"),
            "matched_name": parsed.get("matched_name") or raw_concept,
            "is_new": parsed.get("is_new", True if parsed.get("matched_id") is None else False),
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
        parsed = _extract_json(resp.text)
        steps = parsed.get("steps", [])
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
        parsed = _extract_json(resp.text)
        
        quality = float(parsed.get("result_quality", 0.7))
        quality = max(0.0, min(1.0, quality))
        
        return {
            "result_quality": quality,
            "is_sufficient": bool(parsed.get("is_sufficient", quality >= 0.6)),
            "misconception_detected": parsed.get("misconception_detected"),
            "feedback": parsed.get("feedback", "Evaluation completed."),
        }
