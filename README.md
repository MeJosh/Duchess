# Duchess

A Blood on the Clocktower analysis engine using symbolic reasoning and probabilistic inference for agent-based deduction.

## Overview

Duchess implements world-based reasoning to analyze social deduction scenarios. The system generates all possible game configurations ("worlds"), applies constraints from character abilities, and uses symbolic logic and probabilistic inference to make deductions.

## Current Status: MVP Development (Phase 5/8 Complete)

**✅ Completed Phases:**

- **Phase 0**: Project setup with Poetry, logging infrastructure
- **Phase 1**: Core data models (World, Role) with immutability
- **Phase 2**: Character abilities (Washerwoman, Investigator, Empath, Imp, Scarlet Woman)
- **Phase 3**: World generation - enumerate all possible role assignments
- **Phase 4**: Constraint system - filter worlds based on character information
- **Phase 5**: Deduction engine - symbolic and probabilistic reasoning

**📊 Test Coverage:** 107 tests, 96% overall coverage

**🔄 Next Steps:** Phase 6 (Agent Implementation) - memory and decision-making

**Characters Implemented:**

- **Good Team**: Washerwoman, Investigator, Empath
- **Evil Team**: Imp (Demon), Scarlet Woman (Minion)

## Design Documents

See the `docs/` directory for comprehensive design documentation:

- `architecture.md` - System structure and components
- `game-mechanics.md` - BotC rules subset for MVP
- `agent-design.md` - Reasoning pipeline and algorithms
- `mvp-plan.md` - Implementation phases and tasks

## Installation

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with verbose logging
poetry run pytest -v --log-cli-level=DEBUG
```

## Development

See `docs/mvp-plan.md` for the implementation roadmap.

## Philosophy

- **No LLMs for logic**: Pure symbolic reasoning and probabilistic inference
- **Immutable state**: Functional approach with frozen dataclasses
- **Test-driven**: Comprehensive testing at every phase
- **High visibility**: Extensive logging for debugging and analysis

---

For detailed architecture and design decisions, consult the documentation in `docs/`.
