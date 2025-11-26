"""
Tests for game state data structures.
"""

import pytest
from duchess.engine.game_state import (
    Role,
    Team,
    RoleType,
    World,
    create_world,
)


class TestRole:
    """Tests for Role enum and its properties."""
    
    def test_role_teams(self):
        """Test that roles have correct team assignments."""
        # Good roles
        assert Role.WASHERWOMAN.team == Team.GOOD
        assert Role.INVESTIGATOR.team == Team.GOOD
        assert Role.EMPATH.team == Team.GOOD
        assert Role.TOWNSFOLK.team == Team.GOOD
        
        # Evil roles
        assert Role.IMP.team == Team.EVIL
        assert Role.SCARLET_WOMAN.team == Team.EVIL
    
    def test_role_types(self):
        """Test that roles have correct type categories."""
        assert Role.WASHERWOMAN.role_type == RoleType.TOWNSFOLK
        assert Role.INVESTIGATOR.role_type == RoleType.TOWNSFOLK
        assert Role.EMPATH.role_type == RoleType.TOWNSFOLK
        assert Role.TOWNSFOLK.role_type == RoleType.TOWNSFOLK
        
        assert Role.SCARLET_WOMAN.role_type == RoleType.MINION
        assert Role.IMP.role_type == RoleType.DEMON
    
    def test_role_alignment_helpers(self):
        """Test is_evil() and is_good() helper methods."""
        assert Role.WASHERWOMAN.is_good()
        assert not Role.WASHERWOMAN.is_evil()
        
        assert Role.IMP.is_evil()
        assert not Role.IMP.is_good()
        
        assert Role.SCARLET_WOMAN.is_evil()
        assert not Role.SCARLET_WOMAN.is_good()


class TestWorld:
    """Tests for World data structure."""
    
    def test_create_simple_world(self):
        """Test creating a basic valid world."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.TOWNSFOLK,
            "Frank": Role.SCARLET_WOMAN,
            "Grace": Role.IMP,
        })
        
        assert len(world.assignments) == 7
        assert world.get_role("Alice") == Role.WASHERWOMAN
        assert world.get_role("Grace") == Role.IMP
    
    def test_world_immutability(self):
        """Test that world assignments cannot be modified."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        # Attempting to modify should raise an error
        with pytest.raises((AttributeError, TypeError)):
            world.assignments["Alice"] = Role.IMP  # type: ignore
    
    def test_world_requires_players(self):
        """Test that empty worlds are rejected."""
        with pytest.raises(ValueError, match="at least one player"):
            create_world({})
    
    def test_world_requires_one_demon(self):
        """Test that worlds must have exactly 1 demon."""
        # No demon
        with pytest.raises(ValueError, match="exactly 1 Demon"):
            create_world({
                "Alice": Role.WASHERWOMAN,
                "Bob": Role.SCARLET_WOMAN,
            })
        
        # Two demons
        with pytest.raises(ValueError, match="exactly 1 Demon"):
            create_world({
                "Alice": Role.IMP,
                "Bob": Role.IMP,
                "Charlie": Role.SCARLET_WOMAN,
            })
    
    def test_get_role(self):
        """Test retrieving player roles."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        assert world.get_role("Alice") == Role.WASHERWOMAN
        assert world.get_role("Bob") == Role.IMP
        
        with pytest.raises(KeyError):
            world.get_role("Charlie")
    
    def test_is_evil_is_good(self):
        """Test evil/good player checks."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.SCARLET_WOMAN,
            "Charlie": Role.IMP,
        })
        
        assert world.is_good("Alice")
        assert not world.is_evil("Alice")
        
        assert world.is_evil("Bob")
        assert not world.is_good("Bob")
        
        assert world.is_evil("Charlie")
        assert not world.is_good("Charlie")
    
    def test_get_players_with_role(self):
        """Test finding players by role."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.TOWNSFOLK,
            "Charlie": Role.TOWNSFOLK,
            "Diana": Role.IMP,
        })
        
        townfolk = world.get_players_with_role(Role.TOWNSFOLK)
        assert townfolk == {"Bob", "Charlie"}
        
        washerwomen = world.get_players_with_role(Role.WASHERWOMAN)
        assert washerwomen == {"Alice"}
        
        imps = world.get_players_with_role(Role.IMP)
        assert imps == {"Diana"}
    
    def test_get_evil_good_players(self):
        """Test getting all players by alignment."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.SCARLET_WOMAN,
            "Diana": Role.IMP,
        })
        
        good = world.get_good_players()
        assert good == {"Alice", "Bob"}
        
        evil = world.get_evil_players()
        assert evil == {"Charlie", "Diana"}
    
    def test_get_neighbors(self):
        """Test finding adjacent players in seating order."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.SCARLET_WOMAN,
            "Frank": Role.IMP,
        })
        
        # Bob's neighbors should be Alice and Charlie
        left, right = world.get_neighbors("Bob")
        assert left == "Alice"
        assert right == "Charlie"
        
        # Test wraparound: Alice's left neighbor is Frank
        left, right = world.get_neighbors("Alice")
        assert left == "Frank"
        assert right == "Bob"
        
        # Frank's right neighbor wraps to Alice
        left, right = world.get_neighbors("Frank")
        assert left == "Eve"
        assert right == "Alice"
    
    def test_get_neighbors_requires_minimum_players(self):
        """Test that neighbor lookup requires at least 3 players."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        with pytest.raises(ValueError, match="at least 3 players"):
            world.get_neighbors("Alice")
    
    def test_world_str_representation(self):
        """Test human-readable string output."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        s = str(world)
        assert "Alice" in s
        assert "Washerwoman" in s
        assert "Bob" in s
        assert "Imp" in s
    
    def test_world_repr(self):
        """Test developer representation."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        r = repr(world)
        assert "World" in r
        assert "2 players" in r


class TestWorldValidation:
    """Tests for world validation logic."""
    
    def test_valid_7_player_world(self):
        """Test standard 7-player setup."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.INVESTIGATOR,
            "Charlie": Role.EMPATH,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.TOWNSFOLK,
            "Frank": Role.SCARLET_WOMAN,
            "Grace": Role.IMP,
        })
        
        assert len(world.assignments) == 7
        assert len(world.get_evil_players()) == 2
        assert len(world.get_good_players()) == 5
    
    def test_valid_5_player_world(self):
        """Test minimal 5-player setup."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.TOWNSFOLK,
            "Diana": Role.SCARLET_WOMAN,
            "Eve": Role.IMP,
        })
        
        assert len(world.assignments) == 5
        assert len(world.get_evil_players()) == 2
        assert len(world.get_good_players()) == 3
