# Personal Learning OS — System Architecture

## Overview
Personal Learning OS is a local-first digital learning environment running as a desktop application built with Tauri, React, FastAPI, SQLAlchemy async, SQLite, and Ollama.

---

## Foundation Layer (Layer 1)
- **Frontend**: React + TypeScript + Vite styled with CSS variables and Tailwind CSS v4.
- **Desktop**: Tauri (Rust wrapper).
- **Backend API**: FastAPI running on Python 3.14.
- **Persistence**: SQLite database via Async SQLAlchemy ORM.
- **LLM Provider**: Abstract provider interface (`LLMProvider`) supporting primary local model execution (`OllamaProvider` using `qwen2.5:3b`) and cloud fallback (`CloudFallbackProvider`).

---

## Core Learning Engine + Knowledge Graph (Layer 2)

Layer 2 introduces persistent knowledge representation and quantitative learning models.

```
                   +-----------------------+
                   |  Evidence Service     |
                   +-----------+-----------+
                               |
                               v
+------------------+   +-------+-------+   +-------------------+
| Misconception    |   | Update Engine |   | Decay Service     |
| Service          |   +-------+-------+   +---------+---------+
+--------+---------+           |                     |
         |                     v                     v
         |          +----------+----------+          |
         +--------->| Multi-dimensional   |<---------+
                    | Learner State       |
                    +----------+----------+
                               |
                               v
                    +----------+----------+
                    | Prerequisite Gap    |
                    | Analysis Engine     |
                    +---------------------+
```

### 1. Concept Graph & Traversal Algorithms
- **Nodes**: `Concept` entities (id, name, description, domain, difficulty_level).
- **Edges**: `ConceptRelationship` entities with types: `PREREQUISITE`, `RELATED`, `PART_OF`, `BUILDS_ON`, `CONTRASTS`, `EXTENDS`, `APPLIED_IN`.
- **Cycle Prevention**: Before inserting any `PREREQUISITE` edge ($A \rightarrow B$), a BFS/DFS traversal validates that $B$ cannot reach $A$ through existing dependent edges, preventing cycles in the DAG.
- **Graph Traversal**: Subgraph and transitive chain extraction via `GraphService` for direct/transitive prerequisites and dependents.

### 2. Multi-Dimensional Learner Knowledge State
The learner's state per concept is tracked across 6 independent dimensions:

| Dimension | Type | Range | Description |
|---|---|---|---|
| `mastery_probability` | Float | 0.0 – 1.0 | Estimated probability that the learner has mastered the concept. |
| `knowledge_strength` | Float | 0.0 – 1.0 | Durability and stability of knowledge. Extends decay half-life. |
| `forgetting_state` | Float | 0.0 – 1.0 | Quantitative measure of forgetting based on time since last reinforcement. |
| `confidence` | Float | 0.0 – 1.0 | Learner's self-reported confidence. Updated only when explicitly provided. |
| `evidence_reliability` | Float | 0.0 – 1.0 | Aggregate quality and volume of supporting evidence. |
| `misconception_severity` | Float | 0.0 – 1.0 | Aggregate severity of active misconceptions for this concept. |

### 3. Evidence Model
- Persistent observation records (`Evidence`) representing discrete learning interactions.
- Stores `evidence_type` (`study_session`, `reading`, `explanation`, `assessment_answer`, `solved_problem`, `repeated_success`, `repeated_failure`, `ai_observation`, `self_report`), `result_quality` (0.0–1.0), `difficulty` (0.0–1.0), optional `confidence`, and notes.

### 4. Forgetting & Decay Model
- Retention is calculated dynamically without mutating historical mastery estimates:
  $$\text{effective\_half\_life} = \text{BASE\_HALF\_LIFE} \times (1.0 + \text{KNOWLEDGE\_STRENGTH\_MULTIPLIER} \times \text{knowledge\_strength})$$
  $$\text{forgetting\_state} = 1.0 - \exp\left(-\ln(2) \times \frac{\text{elapsed\_days}}{\text{effective\_half\_life}}\right)$$
  $$\text{effective\_mastery} = \text{mastery\_probability} \times (1.0 - \text{forgetting\_state} \times \text{FORGETTING\_IMPACT})$$
- Default engineering parameters:
  - `BASE_HALF_LIFE_DAYS = 14.0`
  - `KNOWLEDGE_STRENGTH_MULTIPLIER = 3.0`
  - `FORGETTING_IMPACT = 0.7`

### 5. Prerequisite Gap Analysis
- Traverses the prerequisite DAG starting at a target concept using `find_learning_gaps`.
- Evaluates each prerequisite concept's effective mastery taking decay into account:
  - `strong`: $\text{effective\_mastery} \ge 0.7$
  - `moderate`: $0.4 \le \text{effective\_mastery} < 0.7$
  - `weak`: $\text{effective\_mastery} < 0.4$
  - `unknown`: No state record
- Identifies weak and unstudied prerequisites to inform adaptive learning paths.

### Engineering Disclaimers & Assumptions
> [!NOTE]
> The quantitative update rules and decay formulas are deterministic engineering approximations designed for software integration, not validated cognitive science research models. Constants can be tuned or calibrated as real learning data accumulates in future layers.
