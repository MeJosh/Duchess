# MVP Implementation Plan

## Goal
Build a minimal system where a single agent can analyze a hardcoded Blood on the Clocktower scenario and deduce information using world-based reasoning.

## Success Criteria

- [x] Define game state with 7 players and 5 character types
- [x] Implement character ability logic (Washerwoman, Investigator, Empath, Imp, Scarlet Woman)
- [x] Generate all possible world configurations
- [x] Apply constraints from character abilities
- [x] Output proven facts and probability distributions
- [ ] Test with at least 2 different scenarios

**Current Status:** Phase 5/8 Complete - 107 tests passing, 96% coverage

## Implementation Phases

### Phase 0: Project Setup ✅

**Tasks:**

- [x] Initialize Python project structure
- [x] Setup `pyproject.toml` with dependencies
- [x] Configure pytest
- [x] Create package structure matching `docs/architecture.md`
- [x] Setup logging infrastructure (console + file)

**Dependencies:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.5"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
black = "^23.12"
mypy = "^1.7"
```

### Phase 1: Core Data Models ✅

**File:** `duchess/engine/game_state.py`

**Tasks:**

- [x] Define `World` dataclass (immutable role assignments)
- [x] Define character role enums (Role, RoleType)
- [x] Basic world validation logic
- [x] Support both integer and string player identifiers
- [x] Implement `get_role()`, `is_evil()`, `get_neighbors()` methods

**Tests:** 19 tests, 99% coverage

**Example:**
```python
@dataclass(frozen=True)
class World:
    assignments: Dict[str, str]

    def get_role(self, player: str) -> str: ...
    def is_evil(self, player: str) -> bool: ...
    def validate(self) -> bool: ...  # Check role counts
```

**Tests:** 19 tests, 99% coverage

### Phase 2: Character Abilities ✅

**Files:** `duchess/engine/characters/*.py`

**Tasks:**

- [x] `base.py` - Abstract Character class
- [x] `washerwoman.py` - Implement ability logic
- [x] `investigator.py` - Implement ability logic
- [x] `empath.py` - Implement ability logic
- [x] `imp.py` - Implement demon role
- [x] `scarlet_woman.py` - Implement minion role

**Tests:** 35 tests, 95% coverage for character modules

### Phase 3: World Generation ✅

**File:** `duchess/reasoning/world_builder.py`

**Tasks:**

- [x] Implement `WorldGenerator.generate_all_worlds()`
- [x] Support both player count and player name list
- [x] Optimize generation for 5-7 players
- [x] Add world filtering utilities

**Tests:** 18 tests, 93% coverage

### Phase 4: Constraint System ✅

**File:** `duchess/reasoning/constraints.py`

**Tasks:**

- [x] Define `Constraint` abstract class
- [x] Implement `WasherwomanConstraint`
- [x] Implement `InvestigatorConstraint`
- [x] Implement `EmpathConstraint`
- [x] Implement `ScarletWomanConstraint`
- [x] Implement `RoleConstraint`
- [x] Implement `apply_constraints()` filter function

**Tests:** 18 tests, 97% coverage

### Phase 5: Deduction Engine ✅

**File:** `duchess/reasoning/deduction.py`

**Tasks:**

- [x] `prove_role(worlds, player)` - Returns role if certain, None otherwise
- [x] `is_proven_evil/good(worlds, player)` - Symbolic alignment deduction
- [x] `calculate_role_probabilities(worlds, player)` - Returns probability distribution
- [x] `calculate_alignment_probabilities(worlds, player)` - Good/evil probabilities
- [x] `find_proven_facts(worlds)` - Returns all certain facts
- [x] `get_possible_roles(worlds, player)` - Set of possible roles
- [x] `count_worlds_where(worlds, predicate)` - Generic world counting

**Tests:** 36 tests, 97% coverage

**Key Functions:**
```python
class Washerwoman(Character):
    @staticmethod
    def generate_info(world: World, player: str) -> dict:
        """Generate the information this character receives."""
        # Return {"players": [...], "role": "...", "truth": "..."}
```

**Tests:**
- Unit test each character's info generation
- Verify info is always consistent with world

### Phase 3: World Generation
**File:** `duchess/reasoning/world_builder.py`

**Tasks:**
- [ ] Implement `generate_all_worlds(players: List[str], roles: List[str])`
- [ ] Optimize generation for 7 players
- [ ] Add world filtering utilities

**Algorithm:**
1. Enumerate all ways to assign 1 Imp, 1 Scarlet Woman
2. Distribute remaining roles among other players
3. Return list of valid `World` objects

**Tests:**
- Verify correct number of worlds generated
- Verify all worlds are valid (correct role counts)
- Test with different player counts

### Phase 4: Constraint System
**File:** `duchess/reasoning/deduction.py`

**Tasks:**
- [ ] Define `Constraint` abstract class
- [ ] Implement `WasherwomanConstraint`
- [ ] Implement `InvestigatorConstraint`
- [ ] Implement `EmpathConstraint`
- [ ] Implement `apply_constraint(worlds, constraint)` filter

**Example:**
```python
@dataclass
class WasherwomanConstraint(Constraint):
    players: Tuple[str, str]
    role: str

    def satisfies(self, world: World) -> bool:
        return (
            world.get_role(self.players[0]) == self.role or
            world.get_role(self.players[1]) == self.role
        )
```

**Tests:**
- Test each constraint with known worlds
- Verify correct filtering
- Test edge cases (no valid worlds, all worlds valid)

### Phase 5: Deduction Engine
**File:** `duchess/reasoning/deduction.py` (extended)

**Tasks:**
- [ ] `prove_role(worlds, player)` - Returns role if certain, None otherwise
- [ ] `calculate_role_probabilities(worlds, player)` - Returns probability distribution
- [ ] `find_proven_facts(worlds)` - Returns all certain facts
- [ ] `analyze_evil_likelihood(worlds)` - Who is likely evil

**Example:**
```python
def find_proven_facts(worlds: List[World]) -> List[str]:
    facts = []
    players = worlds[0].assignments.keys()

    for player in players:
        role = prove_role(worlds, player)
        if role:
            facts.append(f"{player} is {role}")

    return facts
```

**Tests:**
- Test with scenarios where facts are provable
- Test with uncertain scenarios
- Verify probability calculations sum to 1.0

### Phase 6: Agent Implementation
**File:** `duchess/agents/agent.py`

**Tasks:**
- [ ] Define `Agent` class with memory
- [ ] `receive_info(info)` - Store private information
- [ ] `build_belief_state()` - Generate and filter worlds
- [ ] `make_deductions()` - Analyze belief state
- [ ] `output_analysis()` - Human-readable summary

**Example:**
```python
class Agent:
    def __init__(self, name: str, character: str):
        self.name = name
        self.character = character
        self.private_info = []
        self.belief_state: Optional[List[World]] = None

    def analyze(self) -> str:
        self.belief_state = self.build_belief_state()
        facts = find_proven_facts(self.belief_state)
        probs = self.calculate_probabilities()
        return self.format_output(facts, probs)
```

**Tests:**
- End-to-end test with simple scenario
- Verify agent produces correct deductions

### Phase 7: Scenario System
**File:** `duchess/simulation/scenarios.py`

**Tasks:**
- [ ] Define `Scenario` dataclass
- [ ] Create hardcoded test scenarios
- [ ] Scenario runner that executes agent analysis

**Example Scenario:**
```python
@dataclass
class Scenario:
    name: str
    players: List[str]
    true_world: World
    agent_name: str
    agent_info: dict  # Private info given to agent

scenario_1 = Scenario(
    name="Simple Washerwoman Test",
    players=["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"],
    true_world=World({
        "Alice": "Washerwoman",
        "Bob": "Empath",
        "Charlie": "Investigator",
        "Diana": "Townsfolk",
        "Eve": "Townsfolk",
        "Frank": "Scarlet Woman",
        "Grace": "Imp",
    }),
    agent_name="Alice",
    agent_info={
        "type": "washerwoman",
        "players": ["Bob", "Charlie"],
        "role": "Empath"
    }
)
```

### Phase 8: Integration & Testing
**Tasks:**
- [ ] Run scenario_1 and verify output
- [ ] Create scenario_2 with different setup
- [ ] Add integration tests
- [ ] Document example outputs

## Example Output (Target)

```
=== Duchess Analysis ===
Scenario: Simple Washerwoman Test
Agent: Alice (Washerwoman)

Private Information Received:
- "One of Bob or Charlie is the Empath"

World Analysis:
- Total possible worlds: 240
- Worlds consistent with my information: 120

Proven Facts:
✓ I (Alice) am the Washerwoman
✓ Either Bob or Charlie is the Empath (but not both)
✓ Exactly one of the 7 players is the Imp
✓ Exactly one of the 7 players is the Scarlet Woman

Role Probabilities:
Bob:
  - Empath: 50.0%
  - Investigator: 16.7%
  - Townsfolk: 16.7%
  - Imp: 8.3%
  - Scarlet Woman: 8.3%

Charlie:
  - Empath: 50.0%
  - Investigator: 16.7%
  - Townsfolk: 16.7%
  - Imp: 8.3%
  - Scarlet Woman: 8.3%

[... other players ...]

Evil Likelihood:
- Grace: 20% likely to be evil
- Frank: 20% likely to be evil
- Diana: 20% likely to be evil
[...]

Conclusions:
- Cannot definitively identify the Imp yet
- Need more information from other players or additional nights
```

## Timeline Estimate
- Phase 0: 1 hour (setup)
- Phase 1: 2 hours (data models)
- Phase 2: 3 hours (characters)
- Phase 3: 2 hours (world generation)
- Phase 4: 2 hours (constraints)
- Phase 5: 2 hours (deduction)
- Phase 6: 2 hours (agent)
- Phase 7: 1 hour (scenarios)
- Phase 8: 2 hours (integration)

**Total: ~17 hours of focused work**

## Next Steps
1. Review this plan and adjust if needed
2. Initialize project structure (Phase 0)
3. Begin implementing core data models (Phase 1)

---
*Last updated: 2025-11-26*
