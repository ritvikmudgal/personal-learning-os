# Learning Engine

This module is intentionally empty in the foundation layer.

## What will go here

The learning engine is the core intelligence of the Personal Learning OS. It will contain:

### Knowledge State Management
- Update learner knowledge states based on study events and assessment results
- Track confidence vs. demonstrated understanding divergence
- Model knowledge decay over time (spaced repetition)

### Prerequisite Analysis
- Trace weaknesses through the concept prerequisite graph
- Detect when a learner struggles because of gaps in foundational concepts
- Recommend prerequisite review before advancing

### Misconception Detection
- Identify patterns in assessment errors
- Link misconceptions to specific concepts and their prerequisites
- Track misconception resolution over time

### Learning Path Generation
- Recommend what to learn next based on current state + goals
- Adapt paths based on assessment results
- Balance new material with review of decaying knowledge

### Assessment Engine
- Generate assessments targeting weak areas
- Vary difficulty based on demonstrated level
- Use LLM provider for generating questions and evaluating free-form answers

## Integration Points

- **Database**: Uses repositories from `app/db/repositories/`
- **LLM**: Uses provider from `app/llm/factory.py`
- **API**: Will be exposed through new endpoints in `app/api/`
- **Domain**: Uses schemas from `app/domain/`

## Design Principle

The engine will never call Ollama or any cloud API directly.
All LLM communication goes through the `LLMProvider` interface.
