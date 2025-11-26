# Duchess - System Architecture

## Overview
Duchess is a Blood on the Clocktower (BotC) simulation and analysis engine focused on agent-based deduction and automated gameplay.

## Core Philosophy
- **Logic-first approach**: Use symbolic reasoning and probabilistic inference, not LLMs
- **Modular design**: Separate game state, rules engine, and agent reasoning
- **API-ready**: Backend designed for future web client integration

## System Components

### 1. Game Engine (`duchess/engine/`)
Manages game state and rule enforcement.

**Key Modules:**
- `game_state.py` - Immutable game state representation
- `characters/` - Character ability implementations (Washerwoman, Investigator, Empath, Imp, Scarlet Woman)
- `rules.py` - Game flow and phase transitions (night → day → voting)
- `actions.py` - Player actions (nominations, votes, night actions)

**Design Principles:**
- Game state is immutable; actions produce new states
- Character abilities are pure functions when possible
- Clear separation between public and private information

### 2. Reasoning Engine (`duchess/reasoning/`)
Agent logic for information analysis and decision-making.

**Key Modules:**
- `world_builder.py` - Generate possible "worlds" (game state hypotheses) consistent with known information
- `probability.py` - Bayesian inference for world likelihood
- `deduction.py` - Symbolic logic for provable facts
- `strategy.py` - Decision-making based on world models

**Approach:**
- **Symbolic reasoning**: Prove facts when information is certain (e.g., "If Washerwoman saw Alice/Bob and one is Chef, Alice cannot be Imp")
- **Probabilistic inference**: Track likelihood of worlds when information is uncertain (accounting for lies/bluffs)
- **World enumeration**: Generate all possible game configurations consistent with observations

### 3. Agent System (`duchess/agents/`)
Individual player agents with memory and decision-making.

**Key Modules:**
- `agent.py` - Base agent class (observations, beliefs, actions)
- `information.py` - Information tracking and sharing
- `memory.py` - Agent memory of claims and observations

**Agent Capabilities:**
- Receive private information (character ability results)
- Track public claims from other players
- Detect contradictions
- Make decisions (claims, votes, night actions)

### 4. Simulation Runner (`duchess/simulation/`)
Orchestrates multi-agent games.

**Key Modules:**
- `simulator.py` - Run complete games with multiple agents
- `scenarios.py` - Hardcoded scenarios for testing deduction

**MVP Scope:**
- Start with single hardcoded scenario
- One agent analyzes scenario and attempts deduction
- Later: Full multi-agent game simulation

### 5. REST API (`duchess/api/`)
Future web client interface (FastAPI).

**Deferred to post-MVP:**
- Game state visualization endpoints
- Manual input for testing agent reasoning
- Game replay/analysis

## Technology Stack

### Core
- **Python 3.11+**
- **Custom multi-agent orchestration** (no framework for MVP)
- **FastAPI** (future API, minimal for now)

### Key Libraries
- `pydantic` - Data validation and settings
- `dataclasses` - Immutable game state
- `typing` - Strong type hints throughout
- `pytest` - Testing

### Future Considerations
- `numpy` - If we need matrix operations for probability
- `networkx` - If we model social graphs
- `sqlalchemy` - If we persist game history

## Data Flow

```
Scenario Definition
    ↓
Game Engine (creates initial state)
    ↓
Agent receives private info (character ability)
    ↓
Reasoning Engine (builds possible worlds)
    ↓
Deduction Engine (proves facts / calculates probabilities)
    ↓
Agent Decision (output conclusion)
```

## MVP Scope - Phase 1

**Goal:** Single agent analyzes a hardcoded scenario and deduces information.

**Includes:**
1. Basic game state representation
2. Five character implementations (Washerwoman, Investigator, Empath, Imp, Scarlet Woman)
3. Single agent that can:
   - Receive character ability information
   - Build possible worlds
   - Apply symbolic deduction
   - Output conclusions

**Excludes:**
- Full game simulation (no day/night cycles)
- Multi-agent interaction
- Voting/nomination
- Complex probability calculations (start with world counting)
- Web API/dashboard

## Project Structure

```
duchess/
├── engine/
│   ├── game_state.py
│   ├── characters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── washerwoman.py
│   │   ├── investigator.py
│   │   ├── empath.py
│   │   ├── imp.py
│   │   └── scarlet_woman.py
│   ├── rules.py
│   └── actions.py
├── reasoning/
│   ├── world_builder.py
│   ├── deduction.py
│   └── probability.py
├── agents/
│   ├── agent.py
│   └── information.py
├── simulation/
│   └── scenarios.py
└── api/  # Future
    └── main.py

tests/
├── engine/
├── reasoning/
└── agents/

docs/
├── architecture.md (this file)
├── game-mechanics.md
├── agent-design.md
└── features/
```

## Next Steps
1. Define game mechanics and rules (`game-mechanics.md`)
2. Design agent reasoning approach (`agent-design.md`)
3. Implement core game state and character abilities
4. Build first scenario and test deduction

---
*Last updated: 2025-11-26*
