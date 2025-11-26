# Changelog

All notable changes to the Duchess project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Report Generator MVP for visualizing agent deduction progress
  - `ReportGenerator` class for generating markdown analysis reports
  - `Observation` dataclass for tracking agent learning steps
  - Four-section reports: header, ground truth, timeline, accuracy metrics
  - World reduction tracking showing percentage of possibilities eliminated
  - Accuracy scoring comparing predictions to ground truth
  - Example usage in `examples/report_example.py`
  - 18 comprehensive tests with 92% coverage

### Changed

- Overall test coverage increased to 95% (125 tests total)

## [0.1.0] - 2025-11-26

### Initial Release

- Project structure and build configuration
  - Poetry-based dependency management
  - pytest testing infrastructure with coverage reporting
  - Comprehensive design documentation in `docs/`

- Core game state models (Phase 1)
  - `World` class with frozen dataclass for immutable game states
  - `Role` enum for all 5 MVP characters
  - Player assignment validation and evil count tracking
  - 99% test coverage for game state module

- Character ability implementations (Phase 2)
  - Washerwoman: identifies Townsfolk among two players
  - Investigator: identifies Minion among two players
  - Empath: counts living evil neighbors
  - Imp: demon kill ability
  - Scarlet Woman: becomes Imp if Imp dies with 5+ alive
  - Complete test suite for all character abilities

- World generation system (Phase 3)
  - `generate_all_worlds()` creates all valid role assignments
  - Generates 720 possible worlds for 6-player games
  - Role distribution validation
  - 93% test coverage with comprehensive edge case testing

- Constraint system (Phase 4)
  - `apply_washerwoman_constraint()` for Townsfolk info
  - `apply_investigator_constraint()` for Minion info
  - `apply_empath_constraint()` for neighbor alignment
  - Efficient world filtering by eliminating impossible scenarios
  - 97% test coverage for constraint logic

- Deduction engine (Phase 5)
  - `prove_role()` determines if player role is certain
  - `find_proven_facts()` identifies all certain role assignments
  - `calculate_role_probabilities()` computes likelihood distributions
  - `is_proven_good()` / `is_proven_evil()` for alignment detection
  - Pure functional design with no side effects
  - 97% test coverage for deduction logic

### Documentation

- `docs/architecture.md` - System design and component boundaries
- `docs/game-mechanics.md` - BotC rules subset for MVP
- `docs/agent-design.md` - Reasoning pipeline and world-building approach
- `docs/mvp-plan.md` - Implementation phases and task breakdown
- `docs/features/report-generator.md` - Report generation design specification
- `.github/copilot-instructions.md` - AI coding agent guidelines

### Development

- Configured mypy for strict type checking
- Set up pytest with coverage reporting
- Implemented structured logging with duchess.utils.logger
- Created example scripts in `examples/` directory

[Unreleased]: https://github.com/MeJosh/Duchess/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MeJosh/Duchess/releases/tag/v0.1.0
