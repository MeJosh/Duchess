"""
Tests for the constraint system.

Tests filtering of possible worlds based on character information.
"""

import pytest
from duchess.engine.game_state import World, Role
from duchess.reasoning.world_builder import WorldGenerator
from duchess.reasoning.constraints import (
    WasherwomanConstraint,
    InvestigatorConstraint,
    EmpathConstraint,
    ScarletWomanConstraint,
    RoleConstraint,
    apply_constraints,
)


class TestWasherwomanConstraint:
    """Test Washerwoman constraint filtering."""
    
    def test_filters_correctly(self):
        """Washerwoman constraint should keep only worlds where one of two players has the role."""
        # Generate all 5-player worlds
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        # Apply constraint: player 0 or 1 is Investigator
        constraint = WasherwomanConstraint(
            player1=0,
            player2=1,
            role=Role.INVESTIGATOR
        )
        filtered = constraint.apply(all_worlds)
        
        # Check: all filtered worlds have player 0 OR 1 as Investigator
        for world in filtered:
            assert (
                world.get_role(0) == Role.INVESTIGATOR
                or world.get_role(1) == Role.INVESTIGATOR
            ), f"World doesn't satisfy constraint: {world.assignments}"
        
        # Check: some worlds were filtered out (those where neither 0 nor 1 is Investigator)
        assert len(filtered) < len(all_worlds)
    
    def test_no_matches_returns_empty(self):
        """If no worlds match, should return empty list."""
        # Create a single world manually where player 0 is Imp, 1 is SW
        world = World(
            assignments={
                0: Role.IMP,
                1: Role.SCARLET_WOMAN,
                2: Role.WASHERWOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Constraint says 0 or 1 should be Washerwoman
        constraint = WasherwomanConstraint(
            player1=0,
            player2=1,
            role=Role.WASHERWOMAN
        )
        filtered = constraint.apply([world])
        
        # Should filter out this world
        assert len(filtered) == 0
    
    def test_all_match_returns_all(self):
        """If all worlds match, should return all."""
        # Create worlds where player 0 is always Investigator
        worlds = [
            World(
                assignments={
                    0: Role.INVESTIGATOR,
                    1: Role.SCARLET_WOMAN,
                    2: Role.WASHERWOMAN,
                    3: Role.IMP,
                    4: Role.EMPATH,
                }
            ),
            World(
                assignments={
                    0: Role.INVESTIGATOR,
                    1: Role.IMP,
                    2: Role.WASHERWOMAN,
                    3: Role.SCARLET_WOMAN,
                    4: Role.EMPATH,
                }
            ),
        ]
        
        constraint = WasherwomanConstraint(
            player1=0,
            player2=1,
            role=Role.INVESTIGATOR
        )
        filtered = constraint.apply(worlds)
        
        # All should match (player 0 is always Investigator)
        assert len(filtered) == 2


class TestInvestigatorConstraint:
    """Test Investigator constraint filtering."""
    
    def test_filters_correctly(self):
        """Investigator constraint should keep only worlds where one of two players is Minion."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        # Apply constraint: player 2 or 3 is Scarlet Woman
        constraint = InvestigatorConstraint(
            player1=2,
            player2=3,
            role=Role.SCARLET_WOMAN
        )
        filtered = constraint.apply(all_worlds)
        
        # Check: all filtered worlds have player 2 OR 3 as Scarlet Woman
        for world in filtered:
            assert (
                world.get_role(2) == Role.SCARLET_WOMAN
                or world.get_role(3) == Role.SCARLET_WOMAN
            )
        
        # Check: some worlds were filtered out
        assert len(filtered) < len(all_worlds)
    
    def test_demon_is_not_minion(self):
        """Investigator sees Minions, not Demons."""
        # Create world where player 0 is Imp
        world = World(
            
            assignments={
                0: Role.IMP,
                1: Role.SCARLET_WOMAN,
                2: Role.WASHERWOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Constraint says 0 or 1 should be Scarlet Woman
        # Player 0 is Imp (Demon), not Scarlet Woman (Minion)
        constraint = InvestigatorConstraint(
            player1=0,
            player2=1,
            role=Role.SCARLET_WOMAN
        )
        filtered = constraint.apply([world])
        
        # Should keep this world (player 1 is Scarlet Woman)
        assert len(filtered) == 1


class TestEmpathConstraint:
    """Test Empath constraint filtering."""
    
    def test_zero_evil_neighbors(self):
        """Empath with 0 evil neighbors filters correctly."""
        # Create specific world: 0=W, 1=I, 2=E, 3=Imp, 4=SW
        # Player 2 (Empath) has neighbors 1 (good) and 3 (evil)
        # So player 2 sees 1 evil neighbor, not 0
        world1 = World(
            
            assignments={
                0: Role.WASHERWOMAN,
                1: Role.INVESTIGATOR,
                2: Role.EMPATH,
                3: Role.IMP,
                4: Role.SCARLET_WOMAN,
            }
        )
        
        # Player 0 (Washerwoman) has neighbors 4 (SW=evil) and 1 (I=good)
        # So player 0 sees 1 evil neighbor, not 0
        
        # Try player 1: neighbors are 0 (W=good) and 2 (E=good)
        # Player 1 sees 0 evil neighbors
        constraint = EmpathConstraint(empath_player=1, evil_count=0)
        filtered = constraint.apply([world1])
        
        # Should keep the world (player 1 has 0 evil neighbors)
        assert len(filtered) == 1
    
    def test_one_evil_neighbor(self):
        """Empath with 1 evil neighbor filters correctly."""
        world = World(
            
            assignments={
                0: Role.WASHERWOMAN,
                1: Role.INVESTIGATOR,
                2: Role.EMPATH,
                3: Role.IMP,
                4: Role.SCARLET_WOMAN,
            }
        )
        
        # Player 2 (Empath) has neighbors 1 (good) and 3 (evil)
        constraint = EmpathConstraint(empath_player=2, evil_count=1)
        filtered = constraint.apply([world])
        
        assert len(filtered) == 1
    
    def test_two_evil_neighbors(self):
        """Empath with 2 evil neighbors filters correctly."""
        world = World(
            
            assignments={
                0: Role.IMP,
                1: Role.WASHERWOMAN,
                2: Role.SCARLET_WOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Player 4 (Empath) has neighbors 3 (good) and 0 (evil)
        # Only 1 evil neighbor, not 2
        constraint = EmpathConstraint(empath_player=4, evil_count=2)
        filtered = constraint.apply([world])
        
        # Should filter out (player 4 doesn't have 2 evil neighbors)
        assert len(filtered) == 0
    
    def test_filters_on_all_worlds(self):
        """Test Empath constraint on full world set."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        # Player 0 sees 1 evil neighbor
        constraint = EmpathConstraint(empath_player=0, evil_count=1)
        filtered = constraint.apply(all_worlds)
        
        # Verify all filtered worlds satisfy constraint
        for world in filtered:
            neighbors = world.get_neighbors(0)
            evil_count = sum(1 for n in neighbors if world.get_role(n).is_evil())
            assert evil_count == 1


class TestScarletWomanConstraint:
    """Test Scarlet Woman constraint filtering."""
    
    def test_correct_identification(self):
        """SW correctly identifying Imp should keep world."""
        world = World(
            
            assignments={
                0: Role.IMP,
                1: Role.SCARLET_WOMAN,
                2: Role.WASHERWOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Player 1 (SW) sees player 0 as Imp
        constraint = ScarletWomanConstraint(
            scarlet_woman_player=1,
            imp_player=0
        )
        filtered = constraint.apply([world])
        
        assert len(filtered) == 1
    
    def test_incorrect_identification(self):
        """SW incorrectly identifying Imp should filter out world."""
        world = World(
            
            assignments={
                0: Role.IMP,
                1: Role.SCARLET_WOMAN,
                2: Role.WASHERWOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Player 1 (SW) claims player 2 is Imp (wrong!)
        constraint = ScarletWomanConstraint(
            scarlet_woman_player=1,
            imp_player=2
        )
        filtered = constraint.apply([world])
        
        assert len(filtered) == 0
    
    def test_wrong_player_claiming_sw(self):
        """Non-SW player claiming to be SW should filter out world."""
        world = World(
            
            assignments={
                0: Role.IMP,
                1: Role.SCARLET_WOMAN,
                2: Role.WASHERWOMAN,
                3: Role.INVESTIGATOR,
                4: Role.EMPATH,
            }
        )
        
        # Player 2 (Washerwoman) claims to be SW and sees 0 as Imp
        constraint = ScarletWomanConstraint(
            scarlet_woman_player=2,
            imp_player=0
        )
        filtered = constraint.apply([world])
        
        assert len(filtered) == 0


class TestRoleConstraint:
    """Test simple role constraint."""
    
    def test_filters_by_role(self):
        """Role constraint should keep only worlds where player has role."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        # Player 0 is Imp
        constraint = RoleConstraint(player=0, role=Role.IMP)
        filtered = constraint.apply(all_worlds)
        
        # All filtered worlds should have player 0 as Imp
        for world in filtered:
            assert world.get_role(0) == Role.IMP
        
        # Should be fewer than all worlds
        assert len(filtered) < len(all_worlds)
    
    def test_known_player_count(self):
        """For 5 players, there are exactly 4 worlds where each player is Imp."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        # Player 2 is Imp
        constraint = RoleConstraint(player=2, role=Role.IMP)
        filtered = constraint.apply(all_worlds)
        
        # Total worlds = 5 (Imp choices) × 4 (SW choices) × 3! (townsfolk perms) = 120
        # Worlds where player 2 is Imp = 1 (Imp choice) × 4 (SW choices) × 3! = 24
        assert len(filtered) == 24


class TestApplyConstraints:
    """Test applying multiple constraints."""
    
    def test_empty_constraints_returns_all(self):
        """No constraints should return all worlds."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        filtered = apply_constraints(all_worlds, [])
        
        assert len(filtered) == len(all_worlds)
    
    def test_multiple_constraints_narrow_down(self):
        """Multiple constraints should progressively narrow down worlds."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        constraints = [
            RoleConstraint(player=0, role=Role.IMP),  # Player 0 is Imp
            RoleConstraint(player=1, role=Role.SCARLET_WOMAN),  # Player 1 is SW
        ]
        filtered = apply_constraints(all_worlds, constraints)
        
        # Should have exactly 3! = 6 worlds (permutations of 3 townsfolk)
        assert len(filtered) == 6
        
        # All should have player 0 as Imp and player 1 as SW
        for world in filtered:
            assert world.get_role(0) == Role.IMP
            assert world.get_role(1) == Role.SCARLET_WOMAN
    
    def test_contradictory_constraints_return_empty(self):
        """Contradictory constraints should return no worlds."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        constraints = [
            RoleConstraint(player=0, role=Role.IMP),
            RoleConstraint(player=0, role=Role.WASHERWOMAN),  # Contradiction!
        ]
        filtered = apply_constraints(all_worlds, constraints)
        
        assert len(filtered) == 0
    
    def test_complex_scenario(self):
        """Test realistic scenario with multiple character info."""
        generator = WorldGenerator(5)
        all_worlds = generator.generate_all_worlds()
        
        constraints = [
            # Washerwoman sees player 0 or 1 as Investigator
            WasherwomanConstraint(player1=0, player2=1, role=Role.INVESTIGATOR),
            # Investigator sees player 3 or 4 as Scarlet Woman
            InvestigatorConstraint(player1=3, player2=4, role=Role.SCARLET_WOMAN),
            # Empath (player 2) sees 1 evil neighbor
            EmpathConstraint(empath_player=2, evil_count=1),
        ]
        filtered = apply_constraints(all_worlds, constraints)
        
        # Verify all constraints are satisfied
        for world in filtered:
            # Check Washerwoman constraint
            assert (
                world.get_role(0) == Role.INVESTIGATOR
                or world.get_role(1) == Role.INVESTIGATOR
            )
            
            # Check Investigator constraint
            assert (
                world.get_role(3) == Role.SCARLET_WOMAN
                or world.get_role(4) == Role.SCARLET_WOMAN
            )
            
            # Check Empath constraint
            neighbors = world.get_neighbors(2)
            evil_count = sum(1 for n in neighbors if world.get_role(n).is_evil())
            assert evil_count == 1
        
        # Some worlds should remain
        assert len(filtered) > 0
        # But not all
        assert len(filtered) < len(all_worlds)
