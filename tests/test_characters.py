"""
Tests for character ability implementations.
"""

import pytest
from duchess.engine.game_state import Role, create_world
from duchess.engine.characters import (
    Washerwoman,
    Investigator,
    Empath,
    Imp,
    ScarletWoman,
    CharacterInfo,
)


class TestWasherwoman:
    """Tests for Washerwoman character ability."""
    
    def test_washerwoman_basic_info(self):
        """Test that Washerwoman receives valid information."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.SCARLET_WOMAN,
            "Frank": Role.IMP,
        })
        
        info = Washerwoman.generate_info(world, "Alice")
        
        assert isinstance(info, CharacterInfo)
        assert info.character == Role.WASHERWOMAN
        assert info.night == 1
        assert 'players' in info.data
        assert 'role' in info.data
        assert 'truth' in info.data
        
        # Should show 2 players
        assert len(info.data['players']) == 2
        
        # One of them should actually have the role mentioned
        truth_player = info.data['truth']
        mentioned_role = info.data['role']
        assert world.get_role(truth_player) == mentioned_role
        
        # The truth player should be in the list
        assert truth_player in info.data['players']
    
    def test_washerwoman_specified_target(self):
        """Test Washerwoman with specified target for deterministic testing."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.SCARLET_WOMAN,
            "Eve": Role.IMP,
        })
        
        # Specify that Bob should be the target
        info = Washerwoman.generate_info(
            world, "Alice",
            target_player="Bob",
            other_player="Charlie"
        )
        
        assert info.data['truth'] == "Bob"
        assert info.data['role'] == Role.EMPATH
        assert set(info.data['players']) == {"Bob", "Charlie"}
    
    def test_washerwoman_wrong_role_error(self):
        """Test that Washerwoman errors if player doesn't have the role."""
        world = create_world({
            "Alice": Role.EMPATH,  # Alice is NOT Washerwoman
            "Bob": Role.WASHERWOMAN,
            "Charlie": Role.IMP,
        })
        
        with pytest.raises(ValueError, match="not Washerwoman"):
            Washerwoman.generate_info(world, "Alice")


class TestInvestigator:
    """Tests for Investigator character ability."""
    
    def test_investigator_basic_info(self):
        """Test that Investigator receives valid information."""
        world = create_world({
            "Alice": Role.INVESTIGATOR,
            "Bob": Role.EMPATH,
            "Charlie": Role.WASHERWOMAN,
            "Diana": Role.SCARLET_WOMAN,
            "Eve": Role.IMP,
        })
        
        info = Investigator.generate_info(world, "Alice")
        
        assert isinstance(info, CharacterInfo)
        assert info.character == Role.INVESTIGATOR
        assert info.night == 1
        assert 'players' in info.data
        assert 'role' in info.data
        assert 'truth' in info.data
        
        # Should show 2 players
        assert len(info.data['players']) == 2
        
        # One of them should actually have the minion role mentioned
        truth_player = info.data['truth']
        mentioned_role = info.data['role']
        assert world.get_role(truth_player) == mentioned_role
        assert mentioned_role == Role.SCARLET_WOMAN  # Only minion in this setup
        
        # The truth player should be in the list
        assert truth_player in info.data['players']
    
    def test_investigator_specified_target(self):
        """Test Investigator with specified target for deterministic testing."""
        world = create_world({
            "Alice": Role.INVESTIGATOR,
            "Bob": Role.EMPATH,
            "Charlie": Role.SCARLET_WOMAN,
            "Diana": Role.IMP,
        })
        
        info = Investigator.generate_info(
            world, "Alice",
            target_player="Charlie",
            other_player="Bob"
        )
        
        assert info.data['truth'] == "Charlie"
        assert info.data['role'] == Role.SCARLET_WOMAN
        assert set(info.data['players']) == {"Charlie", "Bob"}
    
    def test_investigator_no_minions_error(self):
        """Test that Investigator errors if no minions exist."""
        # Create invalid world without minions for testing
        world = create_world({
            "Alice": Role.INVESTIGATOR,
            "Bob": Role.IMP,
        })
        
        with pytest.raises(ValueError, match="No Minions"):
            Investigator.generate_info(world, "Alice")


class TestEmpath:
    """Tests for Empath character ability."""
    
    def test_empath_zero_evil_neighbors(self):
        """Test Empath with no evil neighbors."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,  # Bob between Alice (good) and Charlie (good)
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.SCARLET_WOMAN,
            "Frank": Role.IMP,
        })
        
        info = Empath.generate_info(world, "Bob")
        
        assert isinstance(info, CharacterInfo)
        assert info.character == Role.EMPATH
        assert info.data['evil_count'] == 0
        assert len(info.data['neighbors']) == 2
        assert set(info.data['neighbors']) == {"Alice", "Charlie"}
    
    def test_empath_one_evil_neighbor(self):
        """Test Empath with one evil neighbor."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,  # Bob (evil) is Charlie's left neighbor
            "Charlie": Role.EMPATH,
            "Diana": Role.INVESTIGATOR,  # Diana (good) is Charlie's right neighbor
            "Eve": Role.SCARLET_WOMAN,
            "Frank": Role.TOWNSFOLK,
        })
        
        info = Empath.generate_info(world, "Charlie")
        
        assert info.data['evil_count'] == 1
        assert set(info.data['neighbors']) == {"Bob", "Diana"}
    
    def test_empath_two_evil_neighbors(self):
        """Test Empath with two evil neighbors."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,  # Bob (evil) is Charlie's left neighbor
            "Charlie": Role.EMPATH,
            "Diana": Role.SCARLET_WOMAN,  # Diana (evil) is Charlie's right neighbor
            "Eve": Role.INVESTIGATOR,
        })
        
        info = Empath.generate_info(world, "Charlie")
        
        assert info.data['evil_count'] == 2
        assert set(info.data['neighbors']) == {"Bob", "Diana"}
    
    def test_empath_multiple_nights(self):
        """Test Empath receiving info on different nights."""
        world = create_world({
            "Alice": Role.EMPATH,
            "Bob": Role.WASHERWOMAN,
            "Charlie": Role.IMP,
        })
        
        info_night1 = Empath.generate_info(world, "Alice", night=1)
        info_night2 = Empath.generate_info(world, "Alice", night=2)
        
        assert info_night1.night == 1
        assert info_night2.night == 2
        # Same result since world hasn't changed
        assert info_night1.data['evil_count'] == info_night2.data['evil_count']


class TestImp:
    """Tests for Imp character ability."""
    
    def test_imp_learns_minions(self):
        """Test that Imp learns who their minions are."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.SCARLET_WOMAN,
            "Eve": Role.IMP,
        })
        
        info = Imp.generate_info(world, "Eve")
        
        assert isinstance(info, CharacterInfo)
        assert info.character == Role.IMP
        assert 'minions' in info.data
        assert 'Diana' in info.data['minions']
        assert len(info.data['minions']) == 1
        assert info.data['team_size'] == 2  # Imp + 1 minion
    
    def test_imp_no_minions(self):
        """Test Imp with no minions (unusual but valid)."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
        })
        
        info = Imp.generate_info(world, "Bob")
        
        assert info.data['minions'] == []
        assert info.data['team_size'] == 1


class TestScarletWoman:
    """Tests for Scarlet Woman character ability."""
    
    def test_scarlet_woman_learns_demon(self):
        """Test that Scarlet Woman learns who the Demon is."""
        world = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.INVESTIGATOR,
            "Diana": Role.SCARLET_WOMAN,
            "Eve": Role.IMP,
        })
        
        info = ScarletWoman.generate_info(world, "Diana")
        
        assert isinstance(info, CharacterInfo)
        assert info.character == Role.SCARLET_WOMAN
        assert 'demon' in info.data
        assert info.data['demon'] == "Eve"
        assert 'evil_team' in info.data
        assert set(info.data['evil_team']) == {"Diana", "Eve"}
    
    def test_scarlet_woman_can_become_demon_flag(self):
        """Test that Scarlet Woman knows if they can become Demon (5+ players)."""
        world_5_players = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.EMPATH,
            "Charlie": Role.SCARLET_WOMAN,
            "Diana": Role.TOWNSFOLK,
            "Eve": Role.IMP,
        })
        
        world_4_players = create_world({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.SCARLET_WOMAN,
            "Charlie": Role.TOWNSFOLK,
            "Diana": Role.IMP,
        })
        
        info_5 = ScarletWoman.generate_info(world_5_players, "Charlie")
        info_4 = ScarletWoman.generate_info(world_4_players, "Bob")
        
        assert info_5.data['can_become_demon'] is True
        assert info_4.data['can_become_demon'] is False


class TestCharacterInfo:
    """Tests for CharacterInfo dataclass."""
    
    def test_character_info_immutable(self):
        """Test that CharacterInfo is immutable."""
        info = CharacterInfo(
            character=Role.WASHERWOMAN,
            night=1,
            data={'test': 'value'},
            message="Test message"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            info.night = 2  # type: ignore
    
    def test_character_info_str(self):
        """Test human-readable string representation."""
        info = CharacterInfo(
            character=Role.EMPATH,
            night=2,
            data={'evil_count': 1},
            message="1 evil neighbor"
        )
        
        s = str(info)
        assert "Night 2" in s
        assert "Empath" in s
        assert "1 evil neighbor" in s
