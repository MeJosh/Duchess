"""
Tests for world generation and enumeration.
"""

import math
import pytest
from duchess.engine.game_state import Role
from duchess.reasoning import WorldGenerator, generate_worlds, filter_worlds


class TestWorldGenerator:
    """Tests for WorldGenerator class."""
    
    def test_init(self):
        """Test WorldGenerator initialization."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        gen = WorldGenerator(players)
        
        assert gen.players == players
        assert gen.num_players == 5
    
    def test_count_worlds_5_players(self):
        """Test world count calculation for 5 players."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        gen = WorldGenerator(players)
        
        count = gen.count_worlds()
        
        # 5 players: 5 Imp choices × 4 SW choices × 3! good role perms
        # = 5 × 4 × 6 = 120
        assert count == 120
    
    def test_count_worlds_7_players(self):
        """Test world count calculation for 7 players."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
        gen = WorldGenerator(players)
        
        count = gen.count_worlds()
        
        # 7 players: 7 Imp choices × 6 SW choices × 5! good role perms
        # = 7 × 6 × 120 = 5040
        assert count == 5040
    
    def test_generate_all_worlds_5_players(self):
        """Test generating all worlds for 5 players."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        gen = WorldGenerator(players)
        
        worlds = gen.generate_all_worlds()
        
        # Should generate 120 worlds
        assert len(worlds) == 120
        
        # Each world should have 5 players
        for world in worlds:
            assert len(world.assignments) == 5
        
        # Each world should have exactly 1 Imp
        for world in worlds:
            imps = [p for p, r in world.assignments.items() if r == Role.IMP]
            assert len(imps) == 1
        
        # Each world should have exactly 1 Scarlet Woman
        for world in worlds:
            sws = [p for p, r in world.assignments.items() if r == Role.SCARLET_WOMAN]
            assert len(sws) == 1
    
    def test_generate_all_worlds_7_players(self):
        """Test generating all worlds for 7 players."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
        gen = WorldGenerator(players)
        
        worlds = gen.generate_all_worlds()
        
        # Should generate 5040 worlds
        assert len(worlds) == 5040
        
        # Spot check some properties
        assert all(len(w.assignments) == 7 for w in worlds[:10])
        assert all(len(w.get_evil_players()) == 2 for w in worlds[:10])
    
    def test_all_worlds_unique(self):
        """Test that all generated worlds are unique."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        gen = WorldGenerator(players)
        
        worlds = gen.generate_all_worlds()
        
        # Convert to hashable representation
        world_signatures = []
        for world in worlds:
            # Create sorted tuple of (player, role) pairs
            sig = tuple(sorted(
                (p, r.value) for p, r in world.assignments.items()
            ))
            world_signatures.append(sig)
        
        # All should be unique
        assert len(world_signatures) == len(set(world_signatures))
    
    def test_worlds_cover_all_possibilities(self):
        """Test that generated worlds cover all role assignment possibilities."""
        players = ["Alice", "Bob", "Charlie"]
        gen = WorldGenerator(players)
        
        worlds = gen.generate_all_worlds()
        
        # For 3 players, check that Alice is Imp in some worlds
        alice_imp_worlds = [
            w for w in worlds 
            if w.get_role("Alice") == Role.IMP
        ]
        assert len(alice_imp_worlds) > 0
        
        # Check that Alice is Washerwoman in some worlds
        alice_washer_worlds = [
            w for w in worlds 
            if w.get_role("Alice") == Role.WASHERWOMAN
        ]
        assert len(alice_washer_worlds) > 0
        
        # Check that Alice is Scarlet Woman in some worlds
        alice_sw_worlds = [
            w for w in worlds 
            if w.get_role("Alice") == Role.SCARLET_WOMAN
        ]
        assert len(alice_sw_worlds) > 0
    
    def test_custom_roles(self):
        """Test generating worlds with custom role distribution."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        gen = WorldGenerator(players)
        
        # Custom: all good players are Townsfolk (no special roles)
        custom_roles = [Role.TOWNSFOLK] * 3
        
        worlds = gen.generate_all_worlds(available_roles=custom_roles)
        
        # Still generates worlds, but with different role distribution
        assert len(worlds) > 0
        
        # Check that all good players are Townsfolk
        for world in worlds:
            good_players = world.get_good_players()
            for player in good_players:
                assert world.get_role(player) == Role.TOWNSFOLK


class TestGenerateWorldsFunction:
    """Tests for the convenience generate_worlds function."""
    
    def test_generate_worlds_basic(self):
        """Test basic world generation with convenience function."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        
        worlds = generate_worlds(players)
        
        assert len(worlds) == 120
        assert all(len(w.assignments) == 5 for w in worlds)
    
    def test_generate_worlds_custom_roles(self):
        """Test generate_worlds with custom roles."""
        players = ["Alice", "Bob", "Charlie"]
        custom_roles = [Role.EMPATH]  # Only 1 good player, all Empath
        
        worlds = generate_worlds(players, available_roles=custom_roles)
        
        # All good players should be Empath
        for world in worlds:
            good_players = world.get_good_players()
            assert len(good_players) == 1
            for player in good_players:
                assert world.get_role(player) == Role.EMPATH


class TestFilterWorlds:
    """Tests for world filtering functionality."""
    
    def test_filter_worlds_basic(self):
        """Test basic world filtering."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        worlds = generate_worlds(players)
        
        # Filter to only worlds where Alice is Imp
        alice_imp_worlds = filter_worlds(
            worlds,
            lambda w: w.get_role("Alice") == Role.IMP
        )
        
        # Should have some, but not all
        assert len(alice_imp_worlds) > 0
        assert len(alice_imp_worlds) < len(worlds)
        
        # All filtered worlds should have Alice as Imp
        for world in alice_imp_worlds:
            assert world.get_role("Alice") == Role.IMP
    
    def test_filter_worlds_multiple_conditions(self):
        """Test filtering with multiple conditions."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        worlds = generate_worlds(players)
        
        # Filter: Alice is Washerwoman AND Bob is Empath
        filtered = filter_worlds(
            worlds,
            lambda w: (
                w.get_role("Alice") == Role.WASHERWOMAN and
                w.get_role("Bob") == Role.EMPATH
            )
        )
        
        assert len(filtered) > 0
        
        # Verify all match conditions
        for world in filtered:
            assert world.get_role("Alice") == Role.WASHERWOMAN
            assert world.get_role("Bob") == Role.EMPATH
    
    def test_filter_worlds_evil_count(self):
        """Test filtering based on evil player count (should always be 2)."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        worlds = generate_worlds(players)
        
        # Filter to worlds with exactly 2 evil players (should be all)
        filtered = filter_worlds(
            worlds,
            lambda w: len(w.get_evil_players()) == 2
        )
        
        assert len(filtered) == len(worlds)  # All worlds should pass
    
    def test_filter_worlds_no_matches(self):
        """Test filtering that returns no matches."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        worlds = generate_worlds(players)
        
        # Impossible condition: Alice is both Imp and Washerwoman
        filtered = filter_worlds(
            worlds,
            lambda w: (
                w.get_role("Alice") == Role.IMP and
                w.get_role("Alice") == Role.WASHERWOMAN
            )
        )
        
        assert len(filtered) == 0
    
    def test_filter_worlds_all_match(self):
        """Test filtering where all worlds match."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        worlds = generate_worlds(players)
        
        # Condition that's always true
        filtered = filter_worlds(
            worlds,
            lambda w: len(w.assignments) == 5
        )
        
        assert len(filtered) == len(worlds)


class TestWorldGenerationPerformance:
    """Tests for world generation performance and scalability."""
    
    def test_5_player_generation_fast(self):
        """Test that 5-player world generation is fast."""
        import time
        
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        
        start = time.time()
        worlds = generate_worlds(players)
        elapsed = time.time() - start
        
        assert len(worlds) == 120
        # Should be very fast (< 1 second)
        assert elapsed < 1.0
    
    def test_7_player_generation_reasonable(self):
        """Test that 7-player world generation is reasonable."""
        import time
        
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
        
        start = time.time()
        worlds = generate_worlds(players)
        elapsed = time.time() - start
        
        assert len(worlds) == 5040
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
    
    def test_count_vs_actual(self):
        """Test that count_worlds matches actual generation."""
        players = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        gen = WorldGenerator(players)
        
        expected = gen.count_worlds()
        worlds = gen.generate_all_worlds()
        actual = len(worlds)
        
        assert actual == expected
