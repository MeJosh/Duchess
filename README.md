# Duchess

A Blood on the Clocktower analysis engine using symbolic reasoning and probabilistic inference for agent-based deduction.

## Overview

Duchess implements world-based reasoning to analyze social deduction scenarios. The system generates all possible game configurations ("worlds"), applies constraints from character abilities, and uses symbolic logic and probabilistic inference to make deductions.

## Current Status: MVP Complete! 🎉

**✅ All 8 Phases Implemented:**

- **Phase 0**: Project setup with Poetry, logging infrastructure
- **Phase 1**: Core data models (World, Role) with immutability
- **Phase 2**: Character abilities (Washerwoman, Investigator, Empath, Imp, Scarlet Woman)
- **Phase 3**: World generation - enumerate all possible role assignments
- **Phase 4**: Constraint system - filter worlds based on character information
- **Phase 5**: Deduction engine - symbolic and probabilistic reasoning
- **Phase 6**: Agent implementation - memory, belief state, and decision-making
- **Phase 7**: Scenario system - test framework and CLI runner
- **Phase 8**: Integration & testing - end-to-end validation

**📊 Test Coverage:** 168 tests, 88% overall coverage

**Characters Implemented:**

- **Good Team**: Washerwoman, Investigator, Empath
- **Evil Team**: Imp (Demon), Scarlet Woman (Minion)

## Design Documents

See the `docs/` directory for comprehensive design documentation:

- `architecture.md` - System structure and components
- `game-mechanics.md` - BotC rules subset for MVP
- `agent-design.md` - Reasoning pipeline and algorithms
- `mvp-plan.md` - Implementation phases and tasks

## Installation & Quick Start

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# List available scenarios
poetry run python -m duchess.simulation.run --list

# Run a specific scenario
poetry run python -m duchess.simulation.run washerwoman

# Run all scenarios
poetry run python -m duchess.simulation.run --all

# Generate and save reports
poetry run python -m duchess.simulation.run --all --save
```

## Usage Examples

### Running Scenarios

The CLI runner allows you to test the agent's reasoning capabilities:

```bash
# List available test scenarios
$ poetry run python -m duchess.simulation.run --list
Available scenarios:
  1. washerwoman - Simple Washerwoman deduction
  2. investigator - Complex Investigator reasoning  
  3. empath - Empath neighbor detection

# Run the washerwoman scenario
$ poetry run python -m duchess.simulation.run washerwoman

📊 Results:
  Initial worlds: 24
  After 1 observation(s): 12 worlds
  Reduction: 12 worlds eliminated

✓ Proven Facts (1):
    Alice: Washerwoman

📈 Sample Role Probabilities:
    Bob: Investigator: 50.0%
    Charlie: Investigator: 50.0%
```

### Programmatic Usage

```python
from duchess.simulation import ScenarioRunner, SCENARIO_WASHERWOMAN_SIMPLE

# Run a scenario
runner = ScenarioRunner()
results = runner.run(SCENARIO_WASHERWOMAN_SIMPLE)

# Access results
print(f"Proven facts: {results['proven_facts']}")
print(f"Role probabilities: {results['role_probabilities']}")

# Generate a markdown report
report = runner.generate_report(SCENARIO_WASHERWOMAN_SIMPLE, results)
```

## Architecture Highlights

- **World-based reasoning**: Generate all possible game states, filter by constraints
- **Constraint system**: Compositional rules from character abilities
- **Agent architecture**: Memory system, belief state management, deduction pipeline
- **Scenario framework**: Reproducible test cases with ground truth

## Test Coverage

All core functionality is comprehensively tested:

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=duchess --cov-report=term-missing

# Run specific test modules
poetry run pytest tests/test_agent.py -v
poetry run pytest tests/test_scenarios.py -v
```

**Test Breakdown:**

- 30 tests for agent reasoning and memory
- 13 tests for scenario system
- 125 tests for core engine, constraints, and deduction
- **Total: 168 tests with 88% coverage**

## Development

See `docs/mvp-plan.md` for the implementation roadmap.

## Philosophy

- **No LLMs for logic**: Pure symbolic reasoning and probabilistic inference
- **Immutable state**: Functional approach with frozen dataclasses
- **Test-driven**: Comprehensive testing at every phase
- **High visibility**: Extensive logging for debugging and analysis

---

For detailed architecture and design decisions, consult the documentation in `docs/`.
