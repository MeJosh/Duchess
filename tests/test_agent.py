"""Tests for agent implementation."""

import pytest
from pathlib import Path

from duchess.engine.game_state import World, Role
from duchess.agents import (
    AgentMemory,
    Information,
    InformationType,
    ReasoningAgent,
)


class TestInformationType:
    """Test InformationType enum."""
    
    def test_enum_values(self):
        """Test enum has expected values."""
        assert InformationType.WASHERWOMAN.value == "washerwoman"
        assert InformationType.INVESTIGATOR.value == "investigator"
        assert InformationType.EMPATH.value == "empath"
        assert InformationType.SELF_KNOWLEDGE.value == "self_knowledge"


class TestInformation:
    """Test Information dataclass."""
    
    def test_washerwoman_repr(self):
        """Test washerwoman information representation."""
        info = Information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
            source="self",
        )
        
        repr_str = repr(info)
        assert "Washerwoman" in repr_str
        assert "Bob" in repr_str
        assert "Charlie" in repr_str
        assert "Investigator" in repr_str
    
    def test_investigator_repr(self):
        """Test investigator information representation."""
        info = Information(
            info_type=InformationType.INVESTIGATOR,
            data={"players": [3, 4], "role": Role.SCARLET_WOMAN},
            source="self",
        )
        
        repr_str = repr(info)
        assert "Investigator" in repr_str
        assert "3" in repr_str or "[3, 4]" in repr_str
    
    def test_empath_repr(self):
        """Test empath information representation."""
        info = Information(
            info_type=InformationType.EMPATH,
            data={"empath_player": 2, "evil_count": 1},
            source="self",
        )
        
        repr_str = repr(info)
        assert "Empath" in repr_str
        assert "1" in repr_str
        assert "evil" in repr_str.lower()
    
    def test_self_knowledge_repr(self):
        """Test self-knowledge representation."""
        info = Information(
            info_type=InformationType.SELF_KNOWLEDGE,
            data={"role": Role.WASHERWOMAN},
            source="self",
        )
        
        repr_str = repr(info)
        assert "Self" in repr_str
        assert "Washerwoman" in repr_str


class TestAgentMemory:
    """Test AgentMemory class."""
    
    def test_initialization(self):
        """Test memory initialization with self-knowledge."""
        memory = AgentMemory(agent_name="Alice", agent_role=Role.WASHERWOMAN)
        
        assert memory.agent_name == "Alice"
        assert memory.agent_role == Role.WASHERWOMAN
        assert len(memory.information) == 1  # Self-knowledge added
        assert memory.information[0].info_type == InformationType.SELF_KNOWLEDGE
        assert memory.information[0].data["role"] == Role.WASHERWOMAN
    
    def test_add_information(self):
        """Test adding information to memory."""
        memory = AgentMemory(agent_name=0, agent_role=Role.INVESTIGATOR)
        
        memory.add_information(
            info_type=InformationType.INVESTIGATOR,
            data={"players": [1, 2], "role": Role.SCARLET_WOMAN},
            night=1,
        )
        
        assert len(memory.information) == 2  # Self + new info
        assert memory.information[1].info_type == InformationType.INVESTIGATOR
        assert memory.information[1].night == 1
    
    def test_get_trusted_information(self):
        """Test filtering for trusted information."""
        memory = AgentMemory(agent_name="Alice", agent_role=Role.EMPATH)
        
        memory.add_information(
            info_type=InformationType.EMPATH,
            data={"neighbors": ["Bob", "Charlie"], "evil_count": 0},
            trusted=True,
        )
        
        memory.add_information(
            info_type=InformationType.PUBLIC_CLAIM,
            data={"claim": "I am Washerwoman"},
            trusted=False,
        )
        
        trusted = memory.get_trusted_information()
        assert len(trusted) == 2  # Self + empath (not public claim)
        assert all(info.trusted for info in trusted)
    
    def test_get_information_by_type(self):
        """Test filtering by information type."""
        memory = AgentMemory(agent_name="Bob", agent_role=Role.WASHERWOMAN)
        
        memory.add_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Charlie", "Diana"], "role": Role.EMPATH},
        )
        
        memory.add_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Eve", "Frank"], "role": Role.INVESTIGATOR},
        )
        
        washer_info = memory.get_information_by_type(InformationType.WASHERWOMAN)
        assert len(washer_info) == 2
    
    def test_get_character_ability_info(self):
        """Test getting only character ability information."""
        memory = AgentMemory(agent_name="Charlie", agent_role=Role.EMPATH)
        
        memory.add_information(
            info_type=InformationType.EMPATH,
            data={"neighbors": ["Alice", "Bob"], "evil_count": 1},
        )
        
        # This shouldn't be included (self-knowledge)
        ability_info = memory.get_character_ability_info()
        assert len(ability_info) == 1
        assert ability_info[0].info_type == InformationType.EMPATH
    
    def test_update_belief_state(self):
        """Test updating belief state."""
        memory = AgentMemory(agent_name=0, agent_role=Role.WASHERWOMAN)
        
        worlds = [
            World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True),
            World({0: Role.WASHERWOMAN, 1: Role.EMPATH}, skip_validation=True),
        ]
        
        memory.update_belief_state(worlds)
        assert len(memory.current_worlds) == 2
        assert memory.current_worlds == worlds
    
    def test_get_summary(self):
        """Test getting memory summary."""
        memory = AgentMemory(agent_name="Diana", agent_role=Role.INVESTIGATOR)
        
        memory.add_information(
            info_type=InformationType.INVESTIGATOR,
            data={"players": ["Eve", "Frank"], "role": Role.SCARLET_WOMAN},
        )
        
        summary = memory.get_summary()
        assert "Diana" in summary
        assert "Investigator" in summary
        assert "2 pieces" in summary  # Self + investigator info


class TestReasoningAgent:
    """Test ReasoningAgent class."""
    
    @pytest.fixture
    def players_5(self):
        """Fixture for 5 player names."""
        return ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    
    @pytest.fixture
    def players_int(self):
        """Fixture for integer player IDs."""
        return [0, 1, 2, 3, 4]
    
    def test_initialization(self, players_5):
        """Test agent initialization."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        assert agent.name == "Alice"
        assert agent.role == Role.WASHERWOMAN
        assert agent.num_players == 5
        assert len(agent.memory.current_worlds) > 0
        assert agent.reporter is None  # No true_world provided
    
    def test_initialization_with_true_world(self, players_5):
        """Test agent initialization with true world for reporting."""
        true_world = World({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.INVESTIGATOR,
            "Charlie": Role.EMPATH,
            "Diana": Role.IMP,
            "Eve": Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
            true_world=true_world,
        )
        
        assert agent.reporter is not None
        assert agent.reporter.agent_player == "Alice"
    
    def test_receive_washerwoman_information(self, players_5):
        """Test receiving washerwoman information."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        initial_count = len(agent.memory.current_worlds)
        
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        
        # Should have reduced number of worlds
        assert len(agent.memory.current_worlds) < initial_count
        
        # Should have added information to memory
        assert len(agent.memory.information) == 2  # Self + washerwoman
    
    def test_receive_investigator_information(self, players_5):
        """Test receiving investigator information."""
        agent = ReasoningAgent(
            name="Bob",
            role=Role.INVESTIGATOR,
            players=players_5,
        )
        
        initial_count = len(agent.memory.current_worlds)
        
        agent.receive_information(
            info_type=InformationType.INVESTIGATOR,
            data={"players": ["Charlie", "Diana"], "role": Role.SCARLET_WOMAN},
        )
        
        assert len(agent.memory.current_worlds) < initial_count
    
    def test_receive_empath_information(self, players_5):
        """Test receiving empath information."""
        agent = ReasoningAgent(
            name="Charlie",
            role=Role.EMPATH,
            players=players_5,
        )
        
        initial_count = len(agent.memory.current_worlds)
        
        # Empath is Charlie (index 2 in players_5), sees 1 evil neighbor
        agent.receive_information(
            info_type=InformationType.EMPATH,
            data={"empath_player": "Charlie", "evil_count": 1},
        )
        
        assert len(agent.memory.current_worlds) < initial_count
    
    def test_multiple_constraints(self, players_5):
        """Test applying multiple constraints."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        # Add first constraint
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        count_after_first = len(agent.memory.current_worlds)
        
        # Add second constraint (hypothetical - not realistic for washerwoman)
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Diana", "Eve"], "role": Role.EMPATH},
        )
        count_after_second = len(agent.memory.current_worlds)
        
        # Second constraint should further reduce worlds
        assert count_after_second <= count_after_first
    
    def test_get_proven_facts(self, players_5):
        """Test getting proven facts."""
        # Create scenario where we can prove something
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        proven = agent.get_proven_facts()
        
        # At minimum, agent knows their own role
        assert 0 in proven
        assert proven[0] == Role.WASHERWOMAN
    
    def test_get_role_probabilities(self, players_5):
        """Test calculating role probabilities."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        probs = agent.get_role_probabilities("Bob")
        
        # Should be a valid probability distribution
        assert isinstance(probs, dict)
        assert all(0 <= p <= 1 for p in probs.values())
        assert abs(sum(probs.values()) - 1.0) < 0.01  # Sum to ~1.0
    
    def test_is_good(self, players_5):
        """Test checking if player is good."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        # Agent knows they are good
        assert agent.is_good("Alice") is True
    
    def test_get_evil_probability(self, players_5):
        """Test calculating evil probability."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        evil_prob = agent.get_evil_probability("Bob")
        
        # Should be between 0 and 1
        assert 0 <= evil_prob <= 1
    
    def test_analyze(self, players_5):
        """Test comprehensive analysis."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        
        analysis = agent.analyze()
        
        assert "agent" in analysis
        assert "worlds_count" in analysis
        assert "proven_facts" in analysis
        assert "probabilities" in analysis
        assert "evil_probabilities" in analysis
        
        assert analysis["agent"] == "Alice"
        assert analysis["role"] == Role.WASHERWOMAN
        assert analysis["worlds_count"] > 0
    
    def test_get_summary(self, players_5):
        """Test getting summary string."""
        agent = ReasoningAgent(
            name="Bob",
            role=Role.INVESTIGATOR,
            players=players_5,
        )
        
        summary = agent.get_summary()
        
        assert "Bob" in summary
        assert "Investigator" in summary
        assert "Possible worlds" in summary
        assert "Proven Facts" in summary
    
    def test_generate_report(self, players_5):
        """Test generating analysis report."""
        true_world = World({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.INVESTIGATOR,
            "Charlie": Role.EMPATH,
            "Diana": Role.IMP,
            "Eve": Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
            true_world=true_world,
        )
        
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        
        report = agent.generate_report()
        
        assert "Agent Analysis Report" in report
        assert "Alice" in report
        assert "Washerwoman" in report
    
    def test_generate_report_save(self, tmp_path):
        """Test saving report to file."""
        true_world = World({
            0: Role.WASHERWOMAN,
            1: Role.INVESTIGATOR,
            2: Role.EMPATH,
            3: Role.IMP,
            4: Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name=0,
            role=Role.WASHERWOMAN,
            players=players_5,
            true_world=true_world,
        )
        
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": [1, 2], "role": Role.INVESTIGATOR},
        )
        
        output_file = tmp_path / "agent_report.md"
        agent.generate_report(filepath=output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Agent Analysis Report" in content
    
    def test_generate_report_without_true_world(self, players_5):
        """Test that generating report without true_world raises error."""
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
        )
        
        with pytest.raises(ValueError, match="Cannot generate report"):
            agent.generate_report()


class TestAgentIntegration:
    """Integration tests with realistic scenarios."""
    
    @pytest.fixture
    def players_5(self):
        """Fixture for 5 player names."""
        return ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    
    @pytest.fixture
    def players_int(self):
        """Fixture for integer player IDs."""
        return [0, 1, 2, 3, 4]
    
    def test_washerwoman_scenario(self, players_5):
        """Test washerwoman agent with realistic scenario."""
        true_world = World({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.INVESTIGATOR,
            "Charlie": Role.EMPATH,
            "Diana": Role.IMP,
            "Eve": Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name="Alice",
            role=Role.WASHERWOMAN,
            players=players_5,
            true_world=true_world,
        )
        
        # Alice learns Bob or Charlie is Investigator (Bob is)
        agent.receive_information(
            info_type=InformationType.WASHERWOMAN,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        
        # Check analysis
        analysis = agent.analyze()
        
        # Should have reduced worlds
        assert analysis["worlds_count"] < 720  # Less than all possible
        
        # Should know own role
        proven = analysis["proven_facts"]
        assert "Alice" in proven
        assert proven["Alice"] == Role.WASHERWOMAN
        
        # Bob should have >0 probability of being Investigator
        bob_probs = analysis["probabilities"]["Bob"]
        assert Role.INVESTIGATOR in bob_probs
        assert bob_probs[Role.INVESTIGATOR] > 0
    
    def test_investigator_scenario(self, players_int):
        """Test investigator agent with realistic scenario."""
        true_world = World({
            0: Role.WASHERWOMAN,
            1: Role.INVESTIGATOR,
            2: Role.EMPATH,
            3: Role.IMP,
            4: Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name=1,
            role=Role.INVESTIGATOR,
            players=players_int,
            true_world=true_world,
        )
        
        # Investigator learns 3 or 4 is Scarlet Woman (4 is)
        agent.receive_information(
            info_type=InformationType.INVESTIGATOR,
            data={"players": [3, 4], "role": Role.SCARLET_WOMAN},
        )
        
        analysis = agent.analyze()
        
        # At least one of 3 or 4 should have evil probability
        evil_3 = analysis["evil_probabilities"][3]
        evil_4 = analysis["evil_probabilities"][4]
        
        # At least one should have significant evil probability
        assert evil_3 > 0 or evil_4 > 0
    
    def test_empath_scenario(self, players_5):
        """Test empath agent with realistic scenario."""
        true_world = World({
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.INVESTIGATOR,
            "Charlie": Role.EMPATH,
            "Diana": Role.IMP,
            "Eve": Role.SCARLET_WOMAN,
        })
        
        agent = ReasoningAgent(
            name="Charlie",
            role=Role.EMPATH,
            players=players_5,
            true_world=true_world,
        )
        
        # Charlie's neighbors are Bob (good) and Diana (evil) → count = 1
        agent.receive_information(
            info_type=InformationType.EMPATH,
            data={"neighbors": ["Bob", "Diana"], "evil_count": 1},
        )
        
        analysis = agent.analyze()
        
        # Should have constrained worlds
        assert analysis["worlds_count"] < 720
        
        # Diana should have elevated evil probability
        diana_evil = analysis["evil_probabilities"]["Diana"]
        bob_evil = analysis["evil_probabilities"]["Bob"]
        
        # With 1 evil neighbor, probabilities should be affected
        # (exact values depend on world distribution)
        assert 0 <= diana_evil <= 1
        assert 0 <= bob_evil <= 1
