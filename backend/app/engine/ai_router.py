"""AI Request Router & Classifier for Local-First, Low-CPU Architecture.

Categorizes user requests into:
- DETERMINISTIC: SQLite, Concept Graph, Learner State queries -> 0 LLM calls
- RETRIEVAL: Library notes and material searches -> 0 LLM calls
- LLM_REQUIRED: Genuine teaching & explanation requests -> 1 On-Demand LLM call
- HEAVY_LLM: Deep multi-turn reasoning -> On-Demand Local or Cloud Fallback
"""

from enum import Enum
import re
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.graph_service import GraphService
from app.services.learner_state_service import LearnerStateService
from app.services.misconception_service import MisconceptionService
from app.services.retrieval_service import RetrievalService
from app.embeddings.factory import get_embedding_provider
from app.utils.logging import get_logger

logger = get_logger("engine.ai_router")


class QueryCategory(str, Enum):
    NORMAL_CONVERSATION = "normal_conversation"
    DETERMINISTIC = "deterministic"
    RETRIEVAL = "retrieval"
    LLM_REQUIRED = "llm_required"
    HEAVY_LLM = "heavy_llm"


class AIRouter:
    """Router that classifies requests and executes zero-LLM deterministic paths."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.graph_service = GraphService(session)
        self.state_service = LearnerStateService(session)
        self.misconception_service = MisconceptionService(session)
        self.retrieval_service = RetrievalService(session, embedding_provider=get_embedding_provider())

    def classify_request(self, user_message: str) -> QueryCategory:
        """Classify user request using fast pattern rules and keyword analysis."""
        msg = user_message.strip().lower()

        # 0. Normal Conversation Triggers (Zero-LLM Greetings, Thanks, Capabilities, Acknowledgements)
        normal_patterns = [
            r"^(hello|hi|hey|greetings|yo|good morning|good afternoon|good evening)( there)?[\.!\?]*$",
            r"^(thanks|thank you|thx|many thanks|thank you so much)[\.!\?]*$",
            r"^(how are you|how's it going|how are things|how do you do)[\.!\?]*$",
            r"^(what can you do|who are you|what is your name|tell me about yourself|what are your features|what can i study|help)[\.!\?]*$",
            r"^(okay|ok|cool|got it|awesome|nice|sounds good|great|sure)[\.!\?]*$",
        ]
        for pat in normal_patterns:
            if re.search(pat, msg):
                return QueryCategory.NORMAL_CONVERSATION

        # 1. Deterministic Graph & Learner State Triggers
        deterministic_patterns = [
            r"\b(weak|weakness|weaknesses|gaps|unstudied)\b",
            r"\b(prerequisite|prerequisites|prereq|prereqs)\s+(for|of)\b",
            r"\b(my\s+state|learner\s+state|my\s+progress|knowledge\s+state)\b",
            r"\b(my\s+misconceptions|active\s+misconceptions|flagged\s+misconceptions)\b",
            r"\b(show|list)\s+(my\s+)?(concepts|graph|topics)\b",
        ]
        for pat in deterministic_patterns:
            if re.search(pat, msg):
                return QueryCategory.DETERMINISTIC

        # 2. Retrieval Triggers
        retrieval_patterns = [
            r"\b(find|search|show|get)\s+(my\s+)?(notes|materials|docs|documents|uploads)\b",
            r"\bwhat\s+did\s+i\s+study\s+about\b",
            r"\bnotes\s+on\b",
        ]
        for pat in retrieval_patterns:
            if re.search(pat, msg):
                return QueryCategory.RETRIEVAL

        # 3. Heavy LLM Triggers
        heavy_patterns = [
            r"\banalyze\s+my\s+understanding\b",
            r"\bevaluate\s+this\s+complex\b",
            r"\bdeep\s+code\s+review\b",
        ]
        for pat in heavy_patterns:
            if re.search(pat, msg):
                return QueryCategory.HEAVY_LLM

        # 4. Default: LLM Required for teaching / explanations
        return QueryCategory.LLM_REQUIRED

    async def execute_deterministic_route(
        self,
        category: QueryCategory,
        user_message: str,
        learner_id: int,
    ) -> Dict[str, Any]:
        """Execute zero-LLM deterministic path and format output."""
        msg = user_message.strip().lower()

        if category == QueryCategory.NORMAL_CONVERSATION:
            return self._build_normal_conversation_response(user_message)
        elif category == QueryCategory.DETERMINISTIC:
            if "misconception" in msg:
                return await self._build_misconceptions_response(learner_id)
            elif "prerequisite" in msg or "prereq" in msg:
                return await self._build_prerequisites_response(user_message)
            elif "state" in msg or "progress" in msg:
                return await self._build_learner_state_response(learner_id)
            else:
                return await self._build_weak_concepts_response(learner_id)

        elif category == QueryCategory.RETRIEVAL:
            return await self._build_retrieval_response(user_message, learner_id)

        # Fallback empty structure
        return {
            "text": "Query processed deterministically.",
            "target_concept_name": None,
            "teaching_plan": ["Deterministic query executed"],
            "provenance": [],
            "llm_calls_count": 0,
        }

    def _build_normal_conversation_response(self, user_message: str) -> Dict[str, Any]:
        """Build instant deterministic response for greetings, thanks, capabilities, and status."""
        msg = user_message.strip().lower()

        if re.search(r"^(thanks|thank you|thx)", msg):
            text = "You're very welcome! Let me know whenever you're ready to dive into another concept or material."
        elif re.search(r"^(how are you|how's it going|how are things)", msg):
            text = "I'm doing great, thank you! I'm here in your Study Cottage, ready whenever you want to study or explore something new."
        elif re.search(r"^(what can you do|who are you|what is your name|tell me about yourself|what are your features|help)", msg):
            text = (
                "I am your local AI Tutor inside your Personal Learning OS!\n\n"
                "Here is what I can do for you:\n"
                "- **Study Concepts**: Ask me to explain any concept (e.g. *'Teach me binary search'* or *'Explain recursion'*).\n"
                "- **Explore Notes**: Search your uploaded library materials and notes.\n"
                "- **Track Progress**: Ask to see your weak concepts, prerequisite DAG, or active misconceptions.\n\n"
                "What would you like to explore today?"
            )
        elif re.search(r"^(okay|ok|cool|got it|awesome|nice|sounds good|great|sure)", msg):
            text = "Got it! Whenever you want to explore a concept or ask a question, just let me know."
        else:
            text = "Hello! Welcome to your Study Cottage. What concept or topic would you like to explore or learn today?"

        return {
            "text": text,
            "target_concept_name": None,
            "teaching_plan": [],
            "provenance": [],
            "llm_calls_count": 0,
        }

    async def _build_weak_concepts_response(self, learner_id: int) -> Dict[str, Any]:
        """Build weak concepts summary directly from database."""
        all_concepts = await self.graph_service.get_all_concepts()
        weak_list = []

        for c in all_concepts:
            st = await self.state_service.get_state(learner_id, c.id)
            mastery = st.mastery_probability if st else 0.0
            if mastery < 0.6:
                weak_list.append((c.name, mastery))

        if not weak_list:
            text = "### Learner Knowledge State\n\nYou currently have **no weak concepts** flagged! Great job maintaining solid mastery across your study graph."
        else:
            text = "### Weak Concepts & Target Areas\n\nHere are the concepts currently flagged with low mastery or decay:\n\n"
            for name, mastery in weak_list[:5]:
                text += f"- **{name}**: {mastery * 100:.0f}% mastery\n"
            text += "\n*Recommendation*: Focus your next study turn on one of these concepts to strengthen your foundation."

        return {
            "text": text,
            "target_concept_name": weak_list[0][0] if weak_list else "Learner State",
            "teaching_plan": ["Queried Learner State DB", "Filtered Weak Concepts"],
            "provenance": [{"type": "learner_state", "title": "Knowledge Graph DB", "detail": "0 LLM Calls"}],
            "llm_calls_count": 0,
        }

    async def _build_prerequisites_response(self, user_message: str) -> Dict[str, Any]:
        """Build prerequisite DAG lookup directly from database."""
        all_concepts = await self.graph_service.get_all_concepts()
        target = None
        msg_clean = user_message.lower()

        # Find target concept mentioned in prompt
        for c in sorted(all_concepts, key=lambda x: len(x.name), reverse=True):
            if c.name.lower() in msg_clean:
                target = c
                break

        if not target and all_concepts:
            target = all_concepts[0]

        if not target:
            return {
                "text": "No concepts found in your knowledge graph yet.",
                "target_concept_name": None,
                "teaching_plan": ["Deterministic DAG Query"],
                "provenance": [],
                "llm_calls_count": 0,
            }

        prereqs = await self.graph_service.get_direct_prerequisites(target.id)
        if not prereqs:
            text = f"### Prerequisite DAG for **{target.name}**\n\n**{target.name}** is a foundational concept and has no direct prerequisites listed in your knowledge graph."
        else:
            text = f"### Direct Prerequisites for **{target.name}**\n\n"
            for p in prereqs:
                text += f"- **{p.name}** ({p.description or 'Foundational Concept'})\n"

        return {
            "text": text,
            "target_concept_name": target.name,
            "teaching_plan": [f"Prerequisite DAG lookup for {target.name}"],
            "provenance": [{"type": "prerequisite", "title": "Concept Graph DAG", "detail": f"Direct prereqs for {target.name} (0 LLM Calls)"}],
            "llm_calls_count": 0,
        }

    async def _build_learner_state_response(self, learner_id: int) -> Dict[str, Any]:
        """Build overall learner state summary directly from database."""
        all_concepts = await self.graph_service.get_all_concepts()
        total = len(all_concepts)
        mastered = 0

        for c in all_concepts:
            st = await self.state_service.get_state(learner_id, c.id)
            if st and st.mastery_probability >= 0.7:
                mastered += 1

        text = f"### Overall Learner Progress\n\n- **Total Graph Concepts**: {total}\n- **Mastered Concepts ($\\\\ge 70\\%$)**: {mastered}\n- **Active Session**: Online\n\nKeep studying to expand your personal learning sanctuary!"
        return {
            "text": text,
            "target_concept_name": "Learner Progress",
            "teaching_plan": ["Queried Learner Profile & State"],
            "provenance": [{"type": "learner_state", "title": "Learner Profile DB", "detail": "0 LLM Calls"}],
            "llm_calls_count": 0,
        }

    async def _build_misconceptions_response(self, learner_id: int) -> Dict[str, Any]:
        """Build misconceptions list directly from database."""
        misc_list = await self.misconception_service.get_active_misconceptions(learner_id)
        if not misc_list:
            text = "### Flagged Misconceptions\n\nYou currently have **no active misconceptions** flagged in your learning record!"
        else:
            text = "### Active Learner Misconceptions\n\n"
            for m in misc_list:
                text += f"- **Misconception**: {m.description} (Severity: {m.severity:.1f})\n"

        return {
            "text": text,
            "target_concept_name": "Misconceptions",
            "teaching_plan": ["Queried Misconceptions DB"],
            "provenance": [{"type": "misconception", "title": "Misconception Record", "detail": "0 LLM Calls"}],
            "llm_calls_count": 0,
        }

    async def _build_retrieval_response(self, user_message: str, learner_id: int) -> Dict[str, Any]:
        """Build retrieval response directly from Layer 3 RAG database search."""
        from app.utils.query_cleaner import strip_conversational_noise
        query_clean = strip_conversational_noise(user_message) or user_message

        res_list = await self.retrieval_service.search_semantic(
            query=query_clean,
            learner_id=learner_id,
            top_k=3,
        )

        if not res_list:
            text = f"### Library Material Search\n\nNo uploaded notes or materials found matching **\"{query_clean}\"**."
            prov = []
        else:
            text = f"### Matching Notes & Library Materials for **\"{query_clean}\"**\n\n"
            prov = []
            for r in res_list:
                page_info = f" (Page {r.page_number})" if r.page_number else ""
                text += f"#### Source: *{r.material_title}*{page_info}\n> {r.clean_content[:350]}...\n\n"
                prov.append({
                    "type": "material",
                    "title": r.material_title,
                    "detail": f"Library Excerpt{page_info} (0 LLM Calls)",
                })

        return {
            "text": text,
            "target_concept_name": "Library Search",
            "teaching_plan": [f"Semantic Vector Search for '{query_clean}'"],
            "provenance": prov,
            "llm_calls_count": 0,
        }
