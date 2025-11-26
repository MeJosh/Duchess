# Duchess Project - AI Coding Agent Instructions

## Project Overview
Duchess is a Blood on the Clocktower (BotC) analysis engine using symbolic reasoning and probabilistic inference for agent-based deduction. **No LLMs for logic** - only symbolic/probabilistic approaches.

## Key Concepts
- **Worlds-based reasoning**: Generate all possible role assignments, filter by constraints, calculate probabilities
- **MVP scope**: 5 characters (Washerwoman, Investigator, Empath, Imp, Scarlet Woman), hardcoded scenarios, single-agent deduction
- **Immutable game state**: Pure functions, no side effects in core logic

## Architecture
See `docs/architecture.md` for full system design. Key modules:
- `duchess/engine/` - Game state and character abilities (pure functions)
- `duchess/reasoning/` - World generation, constraints, deduction logic
- `duchess/agents/` - Agent memory and decision-making
- `duchess/simulation/` - Scenario runner

## Design Documents (Read First!)
Before implementing features, consult:
- `docs/architecture.md` - System structure and component boundaries
- `docs/game-mechanics.md` - BotC rules subset for MVP
- `docs/agent-design.md` - Reasoning pipeline and world-building approach
- `docs/mvp-plan.md` - Implementation phases and tasks

## Critical Patterns
1. **Immutability**: Game state and worlds are frozen dataclasses
2. **Constraint-based filtering**: All deduction works by eliminating impossible worlds
3. **Type hints everywhere**: Use `mypy` strict mode
4. **Test-driven**: Write tests before/alongside implementation

## Technology Stack
- Python 3.11+, no multi-agent framework (custom for MVP)
- `pydantic` for validation, `pytest` for testing
- FastAPI planned for future web client (defer for now)

## Development Workflow
```bash
# Setup (once implemented)
poetry install
poetry run pytest

# Run scenario analysis (future)
poetry run python -m duchess.simulation.run scenario_1
```

## Next Implementation Steps
Follow `docs/mvp-plan.md` phases:
1. Project setup (pyproject.toml, structure)
2. Core data models (World, Player)
3. Character abilities
4. World generation & constraint system
5. Deduction engine
6. Agent implementation
7. Scenarios

## When Making Changes
- Keep game logic pure (no I/O in engine/)
- Add type hints and docstrings
- Update relevant design docs if architecture changes
- Write tests for new constraints/deduction logic

---
*Last updated: 2025-11-26*
