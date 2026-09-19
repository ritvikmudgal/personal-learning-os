# Layer 4 Architecture: AI Learning Engine + Personalized Tutor + LangGraph Orchestration

## 1. System Purpose & Core Architectural Principles

Layer 4 transforms the Personal Learning OS Study Cottage into a truly adaptive, concept-aware, prerequisite-driven, and material-grounded tutoring engine.

### Core Loop
```
USER GOAL ("Teach me X")
   │
   ▼
1. UNDERSTAND TARGET & RESOLVE CONCEPT
   │
   ▼
2. RETRIEVE 6D LEARNER KNOWLEDGE STATE
   │
   ▼
3. PREREQUISITE GAP ANALYSIS (Layer 2 DAG)
   │
   ▼
4. IDENTIFY OLD KNOWLEDGE TO REACTIVATE
   │
   ▼
5. SEMANTIC MATERIAL RETRIEVAL (Layer 3 RAG)
   │
   ▼
6. SYNTHESIZE TEACHING PLAN
   │
   ▼
7. GENERATE TAILORED EXPLANATION & PROVENANCE
   │
   ▼
8. EVALUATE LEARNER RESPONSE
   │
   ▼
9. PRODUCE EVIDENCE CANDIDATE ──► EvidenceService ──► UpdateEngine ──► LearnerState
   │
   ▼
10. ROUTE NEXT (Backtrack / Advance / End)
```

---

## 2. LangGraph State Machine Architecture

### State Schema (`LearningState`)
The state graph manages an explicit, bounded state dictionary:
- `learner_id`: Active learner profile ID.
- `user_goal`: Raw prompt input (e.g. "Teach me binary search").
- `target_concept_id` / `target_concept_name`: Resolved target node in Concept Graph.
- `current_concept_id` / `current_concept_name`: Currently active concept focus (may be a weak prerequisite gap during backtracking).
- `prerequisite_gaps`: List of weak or unstudied prerequisites.
- `relevant_known_concepts`: List of strong prerequisite concepts for reactivation.
- `learner_state_snapshots`: 6D knowledge states for target & related concepts.
- `misconceptions`: Active misconception records.
- `retrieved_material`: Relevant document chunks with page/section provenance.
- `teaching_plan`: 3-4 step personalized teaching path.
- `conversation_context`: Recent conversation turns.
- `evidence_candidates`: Structured evidence items evaluated from user turns.
- `next_action`: Routing flag (`teach_gap`, `teach_target`, `backtrack`, `advance`, `end`).
- `session_id`: Active `TeachingSession` PK.

### Graph Nodes & State Transitions
1. `understand_goal`: Classifies intent and resolves target concept against the Concept Graph (auto-creating candidate concepts if absent).
2. `load_learner_context`: Loads 6D learner states and active misconceptions.
3. `analyze_prerequisites`: Runs prerequisite gap analysis (`find_learning_gaps`), setting `next_action = "teach_gap"` if weak prerequisites are present.
4. `retrieve_materials`: Runs local vector similarity search (`RetrievalService.search_semantic`) for library RAG chunks.
5. `plan_teaching`: Calls `TutorLLMOperations.generate_teaching_plan` to build a 3–4 step teaching path.
6. `teach_step`: Generates a warm, structured explanation using `ContextBuilderService` to budget prompt context for `qwen2.5:3b`.
7. `evaluate_response`: Evaluates student response quality (0.0–1.0) and checks for expressed misconceptions.
8. `update_learner_state`: Submits structured evidence candidates to `EvidenceService.record_evidence()`, which updates `KnowledgeState` deterministically via `UpdateEngine`.
9. `route_next`: Conditional routing (backtracks to gap fix if struggling, advances if verified).

---

## 3. Strict Learner State Isolation Guarantee

> [!IMPORTANT]
> **Deterministic State Integrity**:
> The LLM **NEVER** directly mutates `mastery_probability`, `knowledge_strength`, `forgetting_state`, or `confidence`.
> The LLM generates a structured `EvidenceCandidate`. This candidate passes into `EvidenceService.record_evidence()`, which creates an immutable `Evidence` record and invokes `UpdateEngine.update_state_from_evidence()`.

---

## 4. Context Budgeting for Small Local Models (`qwen2.5:3b`)

To run smoothly on 8GB RAM local environments with small 3B models:
- Capped prompt context limit (~1500–2000 tokens / ~6000–8000 characters).
- **Strict Priority Order**:
  1. Target Concept & User Message
  2. Prerequisite Gaps (if present)
  3. Active Misconceptions
  4. 6D Learner Knowledge State
  5. Top 2-3 Material Excerpts with Provenance
  6. Relevant Prior Knowledge
  7. Recent 3–4 Conversation Turns

---

## 5. Teaching Sessions Persistence (`TeachingSession`)

- SQLite table `teaching_sessions`:
  - `id`: PK
  - `learner_id`: FK
  - `target_concept_id`: FK
  - `user_goal`: Goal text
  - `status`: `active`, `completed`, `paused`
  - `teaching_plan`: JSON list of steps
  - `messages`: JSON list of conversation turns
  - `session_metadata`: JSON object storing RAG sources and gap warnings

---

## 6. Web Knowledge Interface Boundary

`BaseWebKnowledgeRetriever` in `app/services/web_knowledge.py` defines the abstract boundary for web knowledge lookup. In Layer 4, `StubWebKnowledgeRetriever` is active. Future layers can swap in live web search providers without modifying `LearningGraphRunner` or `TutorService`.

---

## 7. Verification & Test Suite Summary

- **Backend Pytest Suite**: **67 / 67 tests passing** in ~8.35s.
  - `test_langgraph_workflow.py`: Node execution, goal resolution, gap analysis routing.
  - `test_context_builder.py`: Context priority ordering and character limit budgeting.
  - `test_personalized_tutor.py`: End-to-end tutor service and concept resolution.
  - `test_teaching_sessions.py`: Session CRUD, message turns, active session retrieval.
  - `test_evidence_flow_isolation.py`: Evidence candidate pipeline isolation test.
- **Frontend TypeScript Build**: `npx tsc --noEmit` passed with **0 errors**.
