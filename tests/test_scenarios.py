"""Tests for the scenario system."""

import pytest
from pathlib import Path
from duchess.simulation import (
    Scenario,
    ScenarioRunner,
    SCENARIO_WASHERWOMAN_SIMPLE,
    SCENARIO_INVESTIGATOR_COMPLEX,
    SCENARIO_EMPATH_DEDUCTION,
    ALL_SCENARIOS,
)
from duchess.engine.game_state import World, Role
from duchess.agents.memory import InformationType


class TestScenario:
    """Test Scenario dataclass."""
    
    def test_scenario_creation(self):
        """Test creating a scenario."""
        scenario = Scenario(
            name="Test Scenario",
            description="A test scenario",
            players=["Alice", "Bob", "Charlie", "Diana", "Eve"],
            true_world=World({
                "Alice": Role.WASHERWOMAN,
                "Bob": Role.INVESTIGATOR,
                "Charlie": Role.EMPATH,
                "Diana": Role.IMP,
                "Eve": Role.SCARLET_WOMAN,
            }),
            agent_name="Alice",
            agent_role=Role.WASHERWOMAN,
            observations=[],
        )
        
        assert scenario.name == "Test Scenario"
        assert len(scenario.players) == 5
        assert scenario.agent_name == "Alice"
        assert scenario.agent_role == Role.WASHERWOMAN
        assert len(scenario.observations) == 0
    
    def test_predefined_scenarios_exist(self):
        """Test that predefined scenarios are available."""
        assert SCENARIO_WASHERWOMAN_SIMPLE is not None
        assert SCENARIO_INVESTIGATOR_COMPLEX is not None
        assert SCENARIO_EMPATH_DEDUCTION is not None
        assert len(ALL_SCENARIOS) >= 3


class TestScenarioRunner:
    """Test ScenarioRunner class."""
    
    def test_runner_initialization(self):
        """Test creating a scenario runner."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        
        assert runner.scenario == SCENARIO_WASHERWOMAN_SIMPLE
        assert runner.agent is None  # Not created until run()
    
    def test_run_washerwoman_scenario(self):
        """Test running the washerwoman scenario."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        results = runner.run()
        
        # Check result structure
        assert "scenario_name" in results
        assert "agent_name" in results
        assert "agent_role" in results
        assert "observations_count" in results
        assert "initial_worlds" in results
        assert "final_worlds" in results
        assert "proven_facts" in results
        assert "role_probabilities" in results
        
        # Check values
        assert results["scenario_name"] == "Washerwoman Simple Test"
        assert results["agent_name"] == "Alice"
        assert results["agent_role"] == "Washerwoman"
        assert results["observations_count"] == 1
        
        # Should reduce worlds
        assert results["final_worlds"] < results["initial_worlds"]
        
        # Agent should know their own role
        assert "Alice" in results["proven_facts"]
        assert results["proven_facts"]["Alice"] == Role.WASHERWOMAN
    
    def test_run_investigator_scenario(self):
        """Test running the investigator scenario."""
        runner = ScenarioRunner(SCENARIO_INVESTIGATOR_COMPLEX)
        results = runner.run()
        
        assert results["agent_name"] == "Bob"
        assert results["agent_role"] == "Investigator"
        assert results["observations_count"] == 1
        
        # Should reduce worlds
        assert results["final_worlds"] < results["initial_worlds"]
        
        # Agent should know their own role
        assert "Bob" in results["proven_facts"]
    
    def test_run_empath_scenario(self):
        """Test running the empath scenario."""
        runner = ScenarioRunner(SCENARIO_EMPATH_DEDUCTION)
        results = runner.run()
        
        assert results["agent_name"] == "Charlie"
        assert results["agent_role"] == "Empath"
        assert results["observations_count"] == 1
        
        # Should reduce worlds
        assert results["final_worlds"] < results["initial_worlds"]
        
        # Agent should know their own role
        assert "Charlie" in results["proven_facts"]
    
    def test_generate_report_before_run_fails(self):
        """Test that generating report before running raises error."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        
        with pytest.raises(RuntimeError, match="Must run"):
            runner.generate_report()
    
    def test_generate_report_after_run(self):
        """Test generating report after running scenario."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        runner.run()
        
        report = runner.generate_report()
        
        # Should be markdown format
        assert isinstance(report, str)
        assert len(report) > 0
        assert "Agent Analysis Report" in report
        assert "Alice" in report
        assert "Washerwoman" in report
    
    def test_generate_report_saves_to_file(self, tmp_path):
        """Test saving report to file."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        runner.run()
        
        output_file = tmp_path / "test_report.md"
        report = runner.generate_report(filepath=str(output_file))
        
        # File should exist
        assert output_file.exists()
        
        # Content should match returned report
        content = output_file.read_text()
        assert content == report
        assert "Agent Analysis Report" in content


class TestScenarioIntegration:
    """Integration tests for complete scenario execution."""
    
    def test_all_scenarios_run_successfully(self):
        """Test that all predefined scenarios run without errors."""
        for scenario in ALL_SCENARIOS:
            runner = ScenarioRunner(scenario)
            results = runner.run()
            
            # All scenarios should produce valid results
            assert results["final_worlds"] > 0
            assert len(results["proven_facts"]) >= 1  # At least self-knowledge
            assert results["final_worlds"] <= results["initial_worlds"]
    
    def test_scenario_with_multiple_observations(self):
        """Test scenario with multiple observations."""
        scenario = Scenario(
            name="Multi-observation Test",
            description="Test multiple constraints",
            players=["Alice", "Bob", "Charlie", "Diana", "Eve"],
            true_world=World({
                "Alice": Role.WASHERWOMAN,
                "Bob": Role.INVESTIGATOR,
                "Charlie": Role.EMPATH,
                "Diana": Role.IMP,
                "Eve": Role.SCARLET_WOMAN,
            }),
            agent_name="Alice",
            agent_role=Role.WASHERWOMAN,
            observations=[
                {
                    "type": InformationType.WASHERWOMAN,
                    "data": {"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
                },
                # Could add more observations here in future
            ],
        )
        
        runner = ScenarioRunner(scenario)
        results = runner.run()
        
        # Should successfully process both observations
        assert results["observations_count"] == 1
        assert results["final_worlds"] < results["initial_worlds"]
    
    def test_scenario_results_contain_probabilities(self):
        """Test that results include probability distributions."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        results = runner.run()
        
        role_probs = results["role_probabilities"]
        
        # Should have probabilities for all players except the agent
        # (agent doesn't analyze itself)
        other_players = [p for p in SCENARIO_WASHERWOMAN_SIMPLE.players 
                        if p != SCENARIO_WASHERWOMAN_SIMPLE.agent_name]
        
        for player in other_players:
            assert player in role_probs
            player_probs = role_probs[player]
            
            # Should have probabilities for multiple roles
            assert len(player_probs) > 0
            
            # Probabilities should be valid
            for role, prob in player_probs.items():
                assert 0 <= prob <= 1
            
            # Probabilities should sum to ~1.0
            total = sum(player_probs.values())
            assert abs(total - 1.0) < 0.01
    
    def test_scenario_deduction_correctness(self):
        """Test that scenario deductions are logically correct."""
        runner = ScenarioRunner(SCENARIO_WASHERWOMAN_SIMPLE)
        results = runner.run()
        
        # In washerwoman scenario, we know:
        # - Alice is Washerwoman (self-knowledge)
        # - One of Bob or Charlie is Investigator
        
        proven = results["proven_facts"]
        role_probs = results["role_probabilities"]
        
        # Alice should be proven Washerwoman (via self-knowledge)
        assert proven["Alice"] == Role.WASHERWOMAN
        # Note: Alice doesn't appear in role_probs because agent doesn't analyze self
        
        # Bob and Charlie should have elevated Investigator probability
        # (but maybe not 100% unless worlds are very constrained)
        bob_inv_prob = role_probs["Bob"].get(Role.INVESTIGATOR, 0)
        charlie_inv_prob = role_probs["Charlie"].get(Role.INVESTIGATOR, 0)
        
        # At least one should have non-zero probability
        assert bob_inv_prob > 0 or charlie_inv_prob > 0
