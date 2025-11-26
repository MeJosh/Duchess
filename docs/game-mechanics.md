# Blood on the Clocktower - Game Mechanics (MVP Subset)

## Overview

This document describes the simplified BotC mechanics implemented in Duchess MVP. We focus on 5 characters and basic information flow, excluding full game simulation initially.

## Game Basics

### Teams

- **Good Team**: Trying to identify and execute the Demon
- **Evil Team**: Demon trying to survive and kill all good players

### Win Conditions (for reference, not MVP)

- **Good wins**: Demon is executed
- **Evil wins**: Only 2 players alive (1 good, 1 evil or 2 evil)

## Character Roster (MVP)

### Good Team - Townsfolk

#### Washerwoman

**Ability**: "You start knowing that 1 of 2 players is a particular Townsfolk."

**Implementation Details:**

- Triggers during first night setup
- Storyteller chooses 2 players where at least one IS the named Townsfolk
- Could be: Player A (actual Chef), Player B (not Chef) → "One of A/B is the Chef"
- Information is always true in MVP (no drunk/poisoned mechanics)

**Information Structure:**

```python
{
    "character": "Washerwoman",
    "players": ["Alice", "Bob"],
    "role": "Empath",
    "truth": "Alice"  # Which player actually has the role
}
```

#### Investigator

**Ability**: "You start knowing that 1 of 2 players is a particular Minion."

**Implementation Details:**

- Triggers during first night setup
- Storyteller chooses 2 players where at least one IS the named Minion
- MVP only has 1 Minion (Scarlet Woman), so always learns about Scarlet Woman
- Information is always true in MVP

**Information Structure:**

```python
{
    "character": "Investigator",
    "players": ["Charlie", "Diana"],
    "role": "Scarlet Woman",
    "truth": "Charlie"
}
```

#### Empath

**Ability**: "Each night, you learn how many of your living neighbors are evil."

**Implementation Details:**

- Triggers every night (including first night)
- Neighbors = 2 adjacent players in seating order (circular)
- Counts Demon + Minions as evil
- Returns 0, 1, or 2

**Information Structure:**

```python
{
    "character": "Empath",
    "night": 1,
    "evil_count": 1,  # Number of evil neighbors
    "neighbors": ["Eve", "Frank"]  # For reference
}
```

### Evil Team

#### Imp (Demon)

**Ability**: "Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp."

**Implementation Details:**

- Each night (except first), chooses a player to kill
- Can choose self to pass Demon to a Minion
- MVP: Simplified death mechanics, focus on information implications

**Action Structure:**

```python
{
    "character": "Imp",
    "night": 2,
    "target": "Alice",  # Player to kill
    "self_kill": False
}
```

#### Scarlet Woman (Minion)

**Ability**: "If there are 5 or more players alive & the Demon dies, you become the Demon."

**Implementation Details:**

- Passive ability, triggers when Imp dies (execution or self-kill)
- Only triggers if 5+ players alive
- In MVP, mainly creates uncertainty (could the Scarlet Woman have become Imp?)

**No direct action**, but affects world-building:

- If Imp claimed dead but kills continue → Scarlet Woman likely became new Imp
- Creates bluffing opportunities

## Information Types

### Private Information

Information only the receiving player knows (unless they share it):

- Character ability results
- Your own character and alignment

### Public Information

Information all players can observe:

- Who died and when
- Who was nominated/executed
- Public claims made by players

### Claimed Information

What players SAY they know (may be lies):

- "I'm the Washerwoman and I know Alice or Bob is the Empath"
- "I'm the Investigator and Charlie is the Scarlet Woman"

## MVP Simplifications

### Included Mechanics

- Starting information (Washerwoman, Investigator, first Empath reading)
- Private information reception
- Character ability logic
- Basic evil/good team structure

### Excluded Mechanics (Future)

- **No game flow**: No day/night cycles, nominations, voting, executions
- **No deaths**: Focus on information deduction, not death mechanics
- **No Drunk/Poisoned**: All information is truthful
- **No Storyteller discretion**: Character info is deterministic based on setup
- **No bluffs in MVP**: Focus on consistent world-building first

### Testing Scenarios Instead

For MVP, we'll use **hardcoded scenarios** like:

```text
Setup:
- 7 players: Alice, Bob, Charlie, Diana, Eve, Frank, Grace
- Roles: Washerwoman(Alice), Investigator(Bob), Empath(Charlie),
         Townsfolk(Diana), Townsfolk(Eve), Scarlet Woman(Frank), Imp(Grace)

Private Information Given:
- Alice (Washerwoman): "Bob or Charlie is the Empath" → Charlie is Empath
- Bob (Investigator): "Frank or Grace is Scarlet Woman" → Frank is Scarlet Woman
- Charlie (Empath): "1 evil neighbor" → neighbors are Bob and Diana

Agent Goal:
From Alice's perspective, deduce:
- Who could be the Imp?
- What are the possible world configurations?
- What can be proven vs. probabilistic?
```

## Information Consistency Rules

### For Washerwoman/Investigator

- Exactly 1 of the 2 named players has the specified role
- The other player could be ANY other role

### For Empath

- Count is exact and truthful
- But doesn't specify WHICH neighbors are evil
- Neighbors could change if players die (future mechanic)

### World Consistency

A "valid world" must satisfy:

1. Exactly 1 Demon (Imp or Scarlet-Woman-turned-Imp)
2. Exactly 1 Minion (Scarlet Woman, unless became Imp)
3. All Townsfolk information is internally consistent
4. Empath counts match actual evil neighbors

## Deduction Challenges

### Provable Facts

- If Washerwoman says "A or B is Empath" and A dies/reveals as non-Empath → B is Empath
- If Investigator says "C or D is Scarlet Woman" and see one is Imp → other is Scarlet Woman

### Probabilistic Reasoning

- If Empath says "1 evil neighbor" and neighbors are X and Y → 50/50 which is evil (if no other info)
- Multiple information sources can narrow probabilities

### Bluff Detection (Future)

- If claims contradict (both claim Washerwoman) → at least one is lying
- If evil player claims Townsfolk info → need to model deception

---

Last updated: 2025-11-26

