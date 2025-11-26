# Agent Reasoning Design

## Overview
This document describes how Duchess agents process information, build world models, and make deductions in Blood on the Clocktower.

## Core Approach: Worlds-Based Reasoning

### What is a "World"?
A **world** is a complete assignment of roles to players that is consistent with all known information.

**Example:**
```python
world = {
    "Alice": "Washerwoman",
    "Bob": "Empath",
    "Charlie": "Investigator",
    "Diana": "Townsfolk",
    "Eve": "Townsfolk",
    "Frank": "Scarlet Woman",
    "Grace": "Imp"
}
```

### Why Worlds?
In BotC, you never know the complete game state, but you can:
1. **Enumerate possibilities**: Generate all valid role assignments
2. **Apply constraints**: Eliminate worlds inconsistent with observations
3. **Calculate probabilities**: Count remaining worlds to assess likelihood
4. **Prove facts**: If all remaining worlds agree on something, it's certain

## Agent Reasoning Pipeline

### Phase 1: Information Reception
Agent receives private information from their character ability.

```python
class Agent:
    def __init__(self, name: str, character: str):
        self.name = name
        self.character = character
        self.private_info = []
        self.observations = []
        self.beliefs = WorldSet()  # All possible worlds
```

**Example:**
```python
agent = Agent("Alice", "Washerwoman")
agent.receive_info({
    "type": "character_ability",
    "players": ["Bob", "Charlie"],
    "role": "Empath",
    "message": "One of Bob or Charlie is the Empath"
})
```

### Phase 2: World Generation
Generate all possible worlds consistent with game setup rules.

**Constraints:**
- Exactly 1 Demon (Imp)
- Exactly 1 Minion (Scarlet Woman)
- Remaining players are Townsfolk
- Each player has exactly one role

**Algorithm:**
```python
def generate_all_worlds(players: List[str]) -> List[World]:
    worlds = []

    # Choose 1 player to be Imp
    for imp in players:
        # Choose 1 different player to be Scarlet Woman
        for scarlet in players:
            if scarlet == imp:
                continue

            # Assign remaining as Townsfolk (or other good roles)
            remaining = [p for p in players if p not in [imp, scarlet]]

            # Distribute Washerwoman, Investigator, Empath among remaining
            for assignment in permutations(remaining, 3):
                world = create_world(
                    imp=imp,
                    scarlet_woman=scarlet,
                    washerwoman=assignment[0],
                    investigator=assignment[1],
                    empath=assignment[2],
                    townsfolk=[others...]
                )
                worlds.append(world)

    return worlds
```

**Optimization:** For 7 players with 5 specific roles, this generates manageable number of worlds (~hundreds).

### Phase 3: Constraint Application
Filter worlds using known information.

**Washerwoman Constraint:**
```python
def apply_washerwoman_constraint(worlds: List[World], info: dict) -> List[World]:
    """
    Info: {"players": ["Bob", "Charlie"], "role": "Empath"}
    Keep only worlds where Bob is Empath OR Charlie is Empath
    """
    player1, player2 = info["players"]
    role = info["role"]

    return [
        world for world in worlds
        if world[player1] == role or world[player2] == role
    ]
```

**Investigator Constraint:**
```python
def apply_investigator_constraint(worlds: List[World], info: dict) -> List[World]:
    """
    Info: {"players": ["Frank", "Grace"], "role": "Scarlet Woman"}
    Keep only worlds where Frank is SW OR Grace is SW
    """
    player1, player2 = info["players"]
    role = info["role"]

    return [
        world for world in worlds
        if world[player1] == role or world[player2] == role
    ]
```

**Empath Constraint:**
```python
def apply_empath_constraint(worlds: List[World], info: dict) -> List[World]:
    """
    Info: {"neighbors": ["Eve", "Frank"], "evil_count": 1}
    Keep only worlds where exactly 1 of Eve/Frank is evil
    """
    neighbors = info["neighbors"]
    evil_count = info["evil_count"]

    return [
        world for world in worlds
        if count_evil_in(world, neighbors) == evil_count
    ]

def count_evil_in(world: World, players: List[str]) -> int:
    evil_roles = {"Imp", "Scarlet Woman"}
    return sum(1 for p in players if world[p] in evil_roles)
```

### Phase 4: Deduction

#### Symbolic Deduction (Provable Facts)
If all remaining worlds agree on a fact, it's certain.

```python
def prove_role(worlds: List[World], player: str) -> Optional[str]:
    """
    If all worlds assign the same role to player, return that role.
    Otherwise return None (uncertain).
    """
    roles = {world[player] for world in worlds}

    if len(roles) == 1:
        return roles.pop()  # Proven!
    else:
        return None  # Multiple possibilities
```

**Example:**
```
Remaining worlds after constraints: 50
In all 50 worlds: Alice is Washerwoman
In 25 worlds: Bob is Empath (in other 25: Charlie is Empath)
In all 50 worlds: Grace is Imp or Scarlet Woman (evil)

Proven facts:
- Alice is Washerwoman ✓
- Grace is evil ✓

Uncertain:
- Whether Bob or Charlie is Empath (50/50)
```

#### Probabilistic Reasoning
Calculate likelihood by counting worlds.

```python
def calculate_probabilities(worlds: List[World], player: str) -> Dict[str, float]:
    """
    Return probability distribution over roles for a player.
    """
    role_counts = defaultdict(int)

    for world in worlds:
        role_counts[world[player]] += 1

    total = len(worlds)
    return {
        role: count / total
        for role, count in role_counts.items()
    }
```

**Example:**
```python
probabilities = calculate_probabilities(remaining_worlds, "Bob")
# {
#   "Empath": 0.5,
#   "Townsfolk": 0.3,
#   "Investigator": 0.2
# }
```

### Phase 5: Decision Making (Future)
Based on world model, agent decides:
- What to claim publicly
- Who to vote for
- Who to target with night ability

**MVP:** Just output deductions, don't make decisions yet.

## Information Fusion

When multiple agents share information, combine constraints:

```python
def fuse_information(agent: Agent, claim: Claim) -> None:
    """
    Another player makes a public claim.
    If we trust it, add it as a constraint.
    """
    if agent.trusts(claim.source):
        agent.beliefs.apply_constraint(claim.to_constraint())
    else:
        # Model deception (future)
        agent.beliefs.split_on_trust(claim)
```

## Handling Uncertainty

### Trust Levels (Future)
- **Certain**: Own character ability results
- **Trusted**: Claims from confirmed good players
- **Uncertain**: Claims from unconfirmed players
- **Distrusted**: Claims contradicting known facts

### World Splitting (Future)
If uncertain whether to trust a claim:
- Branch A: "Assume claim is true" → apply constraint
- Branch B: "Assume claim is false" → player is likely evil

Track both possibilities with weights.

## MVP Implementation Plan

### Phase 1: Single Agent, Trusted Info
**Scope:**
- One agent receives private info from their character
- All info is truthful (no lies)
- Agent builds worlds and makes deductions
- Output: "Proven facts" and "Probability distributions"

**Example Output:**
```
Agent: Alice (Washerwoman)
Private Info: "One of Bob or Charlie is the Empath"

Analysis:
- Total possible worlds: 210
- After applying constraints: 105 worlds remain

Proven Facts:
- I am the Washerwoman
- Bob or Charlie is the Empath (one of them, not both)
- Frank or Grace is evil (at least one)

Probabilities:
- Bob is Empath: 50%
- Charlie is Empath: 50%
- Grace is Imp: 60%
- Frank is Scarlet Woman: 35%
- Grace is Scarlet Woman: 5%
```

### Phase 2: Multiple Info Sources (Future)
Combine constraints from multiple character abilities.

### Phase 3: Bluff Detection (Future)
Model deceptive claims and identify contradictions.

### Phase 4: Strategic Decision-Making (Future)
Optimal voting and claiming strategies.

## Data Structures

### World Representation
```python
@dataclass(frozen=True)
class World:
    """Immutable role assignment."""
    assignments: Dict[str, str]  # player -> role

    def __getitem__(self, player: str) -> str:
        return self.assignments[player]

    def is_evil(self, player: str) -> bool:
        return self.assignments[player] in {"Imp", "Scarlet Woman"}
```

### Constraint Representation
```python
@dataclass
class Constraint:
    type: str  # "washerwoman", "investigator", "empath", etc.
    params: dict

    def apply(self, world: World) -> bool:
        """Returns True if world satisfies this constraint."""
        pass
```

### Belief State
```python
class BeliefState:
    """Set of possible worlds with probabilities."""

    def __init__(self, worlds: List[World]):
        self.worlds = worlds
        self.priors = {w: 1.0 / len(worlds) for w in worlds}

    def apply_constraint(self, constraint: Constraint) -> None:
        self.worlds = [w for w in self.worlds if constraint.apply(w)]
        self._normalize_priors()

    def probability(self, predicate: Callable[[World], bool]) -> float:
        return sum(
            self.priors[w]
            for w in self.worlds
            if predicate(w)
        )
```

## Testing Strategy

### Unit Tests
- Test each constraint function with known worlds
- Verify world generation produces correct count
- Test deduction logic with simple scenarios

### Integration Tests
- Full scenarios with multiple constraints
- Verify correct probability calculations
- Test edge cases (no valid worlds, single valid world)

### Example Test Case
```python
def test_washerwoman_deduction():
    # Setup: 5 players, Alice is Washerwoman
    players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    worlds = generate_all_worlds(players)

    # Alice learns: "Bob or Charlie is Empath"
    constraint = WasherwomanConstraint(
        players=["Bob", "Charlie"],
        role="Empath"
    )

    valid_worlds = [w for w in worlds if constraint.apply(w)]

    # Verify: Bob is Empath in ~50% of worlds
    bob_empath_prob = sum(
        1 for w in valid_worlds if w["Bob"] == "Empath"
    ) / len(valid_worlds)

    assert 0.45 < bob_empath_prob < 0.55
```

---
*Last updated: 2025-11-26*
