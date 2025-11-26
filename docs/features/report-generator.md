# Feature: Analysis Report Generator

## Overview

Generate detailed, shareable reports showing agent reasoning progress and accuracy in Blood on the Clocktower scenario analysis.

## Goals

1. **Transparency**: Show exactly what the agent knew and when
2. **Shareability**: Easy to share progress/results (GitHub, forums, etc.)
3. **Debugging**: Help identify where reasoning went wrong
4. **Validation**: Measure agent accuracy against ground truth

## Report Structure

### Section 1: Ground Truth
```
GAME SETUP
----------
Players: 7
Characters: Washerwoman, Investigator, Empath, Imp, Scarlet Woman (x2 Townsfolk)

TRUE ROLES:
  Player 0 (Alice):   Washerwoman  [GOOD]
  Player 1 (Bob):     Investigator [GOOD]
  Player 2 (Charlie): Empath       [GOOD]
  Player 3 (Diana):   Imp          [EVIL - Demon]
  Player 4 (Eve):     Scarlet Woman [EVIL - Minion]
  Player 5 (Frank):   Washerwoman  [GOOD]
  Player 6 (Grace):   Investigator [GOOD]
```

### Section 2: Information Timeline
```
AGENT PERSPECTIVE: Alice (Washerwoman)
--------------------------------------

[Night 1] Received Washerwoman Information:
  "One of Bob or Charlie is the Investigator"
  
  Initial Belief State:
  - Total possible worlds: 720
  - After applying constraint: 360 worlds
  - Reduction: 50%
  
  Known Facts:
  - Alice is Washerwoman (100% - self-knowledge)
  
  Role Probabilities:
  - Bob:     50% Investigator, 25% Empath, 15% Imp, 10% Scarlet Woman
  - Charlie: 50% Investigator, 30% Empath, 15% Imp, 5% Scarlet Woman
  - Diana:   ...
  
  Deductions:
  ✓ Bob OR Charlie is Investigator (proven)
  ✓ At least one of Bob/Charlie is Good (proven)

[Day 1] Public Information: (hypothetical future expansion)
  Diana claims to be the Empath, saw 1 evil neighbor
  
  Updated Belief State:
  - Applying Diana's claim: 360 → 45 worlds
  - Reduction: 87.5% from initial
  
  New Deductions:
  ✓ If Diana is truthful: Charlie or Eve is evil (proven)
  ✗ Diana's claim contradicts Bob being Investigator in 20% of worlds
```

### Section 3: Final Analysis
```
FINAL BELIEF STATE
------------------
Worlds Remaining: 16 (97.8% reduction from initial)

Proven Facts:
  ✓ Alice: Washerwoman (100% - self-knowledge)
  ✓ Bob: Investigator (100%)
  ✓ Diana: Evil alignment (100%)
  
Highly Confident (>90%):
  → Charlie: Empath (95%)
  → Diana: Imp (92%)
  
Uncertain:
  ? Eve: 60% Scarlet Woman, 30% Washerwoman, 10% Investigator
  ? Frank: 45% Washerwoman, 35% Investigator, 20% Empath
  ? Grace: 55% Investigator, 45% Washerwoman
```

### Section 4: Accuracy Score
```
ACCURACY REPORT
---------------
Correctly Identified Roles: 3/7 (42.9%)
  ✓ Alice (self-knowledge doesn't count for scoring)
  ✓ Bob: Predicted Investigator (100%) → CORRECT
  ✓ Diana: Predicted Imp (92%) → CORRECT
  ✗ Charlie: Predicted Empath (95%) → CORRECT
  ✗ Eve: Predicted Scarlet Woman (60%) → CORRECT
  ✗ Frank: Predicted Washerwoman (45%) → CORRECT
  ✗ Grace: Predicted Investigator (55%) → CORRECT

Alignment Accuracy: 7/7 (100%)
  All good/evil alignments correctly identified

Probability Calibration:
  90-100% predictions: 3 made, 3 correct (100% accurate)
  70-90% predictions:  2 made, 2 correct (100% accurate)
  50-70% predictions:  4 made, 2 correct (50% accurate)
  
Overall Score: A-
  - Excellent alignment detection
  - Strong high-confidence predictions
  - Needs more information to resolve remaining uncertainty
```

## Implementation Plan

### Phase 1: Basic Reporting (MVP)
- [ ] Create `ReportGenerator` class
- [ ] Output Markdown format
- [ ] Section 1: Ground truth display
- [ ] Section 2: Single observation timeline entry
- [ ] Section 3: Final belief state summary
- [ ] Section 4: Basic accuracy metrics

### Phase 2: Rich Timeline
- [ ] Track all constraint applications
- [ ] Show world count reduction at each step
- [ ] Display probability changes over time
- [ ] Highlight key deductions

### Phase 3: Multiple Formats
- [ ] HTML output with styling
- [ ] JSON for programmatic analysis
- [ ] ASCII art visualizations (probability bars, etc.)

### Phase 4: Advanced Analytics
- [ ] Probability calibration curves
- [ ] Efficiency metrics (info gained per observation)
- [ ] Comparison between multiple agents
- [ ] Export to charts/graphs

## API Design (Draft)

```python
from duchess.reporting import ReportGenerator

# Create a report generator
reporter = ReportGenerator(
    true_world=true_world,
    agent_name="Alice",
    format="markdown"  # or "html", "json"
)

# Add observations as agent receives them
reporter.add_observation(
    timestamp=1,
    observation_type="washerwoman_info",
    data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
    belief_state=agent.belief_state,
    deductions=agent.recent_deductions
)

# Generate final report
report_text = reporter.generate()
reporter.save("reports/scenario_1_alice.md")

# Or get specific sections
ground_truth = reporter.generate_ground_truth()
timeline = reporter.generate_timeline()
accuracy = reporter.calculate_accuracy()
```

## Open Questions

1. **Output format preference?** Markdown, HTML, JSON, or multiple?
2. **Visualization needs?** Charts, graphs, probability bars?
3. **Scoring methodology?** How to weight different aspects of accuracy?
4. **Real-time vs post-hoc?** Generate during analysis or after completion?
5. **Comparison mode?** Compare multiple agents on same scenario?

## Future Enhancements

- Interactive HTML reports with collapsible sections
- Diff view showing belief changes between observations
- Confidence intervals and uncertainty quantification
- Integration with web dashboard
- Export to social media friendly formats
- Replay/animation of reasoning process

---

**Status**: Design Phase  
**Target**: Phase 6-7 of MVP (alongside Agent Implementation)  
**Priority**: Medium (enables validation and sharing)
