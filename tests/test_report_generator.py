"""Tests for report generator."""

import pytest
from pathlib import Path

from duchess.engine.game_state import World, Role
from duchess.reporting import ReportGenerator, Observation


@pytest.fixture
def simple_world():
    """Create a simple test world."""
    return World(
        {
            0: Role.WASHERWOMAN,
            1: Role.INVESTIGATOR,
            2: Role.EMPATH,
            3: Role.IMP,
            4: Role.SCARLET_WOMAN,
        }
    )


@pytest.fixture
def report_generator(simple_world):
    """Create a basic report generator."""
    return ReportGenerator(
        true_world=simple_world,
        agent_player=0,
        agent_role=Role.WASHERWOMAN,
    )


class TestObservation:
    """Test Observation dataclass."""
    
    def test_observation_creation(self):
        """Test creating an observation."""
        obs = Observation(
            step=0,
            description="Received Washerwoman info",
            constraint_type="washerwoman",
            worlds_before=720,
            worlds_after=360,
            proven_facts={1: Role.INVESTIGATOR},
            data={"players": [1, 2], "role": Role.INVESTIGATOR},
        )
        
        assert obs.step == 0
        assert obs.description == "Received Washerwoman info"
        assert obs.worlds_before == 720
        assert obs.worlds_after == 360
        assert obs.proven_facts[1] == Role.INVESTIGATOR
    
    def test_observation_defaults(self):
        """Test observation with default values."""
        obs = Observation(
            step=1,
            description="Test",
            constraint_type="test",
            worlds_before=100,
            worlds_after=50,
        )
        
        assert obs.proven_facts == {}
        assert obs.data == {}


class TestReportGenerator:
    """Test ReportGenerator class."""
    
    def test_initialization(self, report_generator, simple_world):
        """Test report generator initialization."""
        assert report_generator.true_world == simple_world
        assert report_generator.agent_player == 0
        assert report_generator.agent_role == Role.WASHERWOMAN
        assert report_generator.observations == []
        assert report_generator.final_worlds is None
    
    def test_add_observation(self, report_generator):
        """Test adding observations."""
        worlds_before = [
            World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True),
            World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True),
        ]
        worlds_after = [
            World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True),
        ]
        
        report_generator.add_observation(
            description="Test observation",
            constraint_type="test",
            worlds_before=worlds_before,
            worlds_after=worlds_after,
            data={"test": "value"},
        )
        
        assert len(report_generator.observations) == 1
        obs = report_generator.observations[0]
        assert obs.step == 0
        assert obs.description == "Test observation"
        assert obs.worlds_before == 2
        assert obs.worlds_after == 1
        assert obs.data == {"test": "value"}
    
    def test_add_multiple_observations(self, report_generator):
        """Test adding multiple observations."""
        world1 = World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True)
        world2 = World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True)
        
        report_generator.add_observation(
            description="First",
            constraint_type="test1",
            worlds_before=[world1, world2],
            worlds_after=[world2],
        )
        
        report_generator.add_observation(
            description="Second",
            constraint_type="test2",
            worlds_before=[world2],
            worlds_after=[world2],
        )
        
        assert len(report_generator.observations) == 2
        assert report_generator.observations[0].step == 0
        assert report_generator.observations[1].step == 1
    
    def test_set_final_belief_state(self, report_generator):
        """Test setting final belief state."""
        worlds = [
            World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True),
        ]
        
        report_generator.set_final_belief_state(worlds)
        assert report_generator.final_worlds == worlds
    
    def test_generate_header(self, report_generator):
        """Test header generation."""
        header = report_generator._generate_header()
        
        assert "Agent Analysis Report" in header
        assert "0 (WASHERWOMAN)" in header  # Agent info in markdown format
        assert "Total Observations:** 0" in header
    
    def test_generate_ground_truth(self, report_generator):
        """Test ground truth section."""
        ground_truth = report_generator._generate_ground_truth()
        
        assert "Ground Truth" in ground_truth
        assert "TRUE ROLES:" in ground_truth
        assert "Washerwoman" in ground_truth
        assert "Investigator" in ground_truth
        assert "Imp" in ground_truth
        assert "⭐ (Agent)" in ground_truth  # Agent marker
    
    def test_generate_timeline_empty(self, report_generator):
        """Test timeline with no observations."""
        timeline = report_generator._generate_timeline()
        
        assert "Observation Timeline" in timeline
        assert "No observations recorded" in timeline
    
    def test_generate_timeline_with_observations(self, report_generator):
        """Test timeline with observations."""
        world1 = World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True)
        world2 = World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True)
        
        report_generator.add_observation(
            description="Test observation",
            constraint_type="test",
            worlds_before=[world1, world2],
            worlds_after=[world2],
        )
        
        timeline = report_generator._generate_timeline()
        
        assert "Observation Timeline" in timeline
        assert "Step 0: Test observation" in timeline
        assert "Worlds before: 2" in timeline
        assert "Worlds after: 1" in timeline
        assert "Reduction: 50.0%" in timeline
    
    def test_generate_final_analysis_no_state(self, report_generator):
        """Test final analysis without belief state."""
        analysis = report_generator._generate_final_analysis()
        
        assert "Final Analysis" in analysis
        assert "No final belief state set" in analysis
    
    def test_generate_final_analysis_with_state(self, report_generator):
        """Test final analysis with belief state."""
        # Add an observation first
        initial_worlds = [
            World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True),
            World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True),
        ]
        final_worlds = [
            World({0: Role.WASHERWOMAN, 1: Role.INVESTIGATOR}, skip_validation=True),
        ]
        
        report_generator.add_observation(
            description="Test",
            constraint_type="test",
            worlds_before=initial_worlds,
            worlds_after=final_worlds,
        )
        
        report_generator.set_final_belief_state(final_worlds)
        analysis = report_generator._generate_final_analysis()
        
        assert "Final Analysis" in analysis
        assert "Worlds Remaining:** 1" in analysis  # Markdown format
        assert "50.0% reduction" in analysis
        assert "Proven Facts" in analysis
    
    def test_generate_accuracy_score_no_state(self, report_generator):
        """Test accuracy score without belief state."""
        score = report_generator._generate_accuracy_score()
        
        assert "Accuracy Report" in score
        assert "No final belief state set" in score
    
    def test_generate_accuracy_score_with_state(self, report_generator):
        """Test accuracy score with predictions."""
        # Create final state that matches ground truth
        final_worlds = [
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.INVESTIGATOR,
                    2: Role.EMPATH,
                    3: Role.IMP,
                    4: Role.SCARLET_WOMAN,
                }
            )
        ]
        
        report_generator.set_final_belief_state(final_worlds)
        score = report_generator._generate_accuracy_score()
        
        assert "Accuracy Report" in score
        assert "Role Prediction Accuracy" in score
        assert "4/4 (100.0%)" in score  # All correct except agent
        assert "Alignment Detection" in score
    
    def test_generate_complete_report(self, report_generator):
        """Test generating complete report."""
        # Add observation
        worlds = [
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.INVESTIGATOR,
                    2: Role.EMPATH,
                    3: Role.IMP,
                    4: Role.SCARLET_WOMAN,
                }
            )
        ]
        
        report_generator.add_observation(
            description="Perfect deduction",
            constraint_type="test",
            worlds_before=worlds * 10,  # Simulate starting with more worlds
            worlds_after=worlds,
        )
        
        report_generator.set_final_belief_state(worlds)
        
        report = report_generator.generate()
        
        # Check all major sections present
        assert "Agent Analysis Report" in report
        assert "Ground Truth" in report
        assert "Observation Timeline" in report
        assert "Final Analysis" in report
        assert "Accuracy Report" in report
    
    def test_save_report(self, report_generator, tmp_path):
        """Test saving report to file."""
        output_file = tmp_path / "test_report.md"
        
        # Add minimal observation
        worlds = [World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True)]
        
        report_generator.add_observation(
            description="Test",
            constraint_type="test",
            worlds_before=worlds,
            worlds_after=worlds,
        )
        
        report_generator.set_final_belief_state(worlds)
        report_generator.save(output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Agent Analysis Report" in content
    
    def test_save_creates_directories(self, report_generator, tmp_path):
        """Test that save creates parent directories."""
        output_file = tmp_path / "nested" / "dirs" / "report.md"
        
        worlds = [World({0: Role.WASHERWOMAN, 1: Role.IMP}, skip_validation=True)]
        report_generator.set_final_belief_state(worlds)
        
        report_generator.save(output_file)
        
        assert output_file.exists()
        assert output_file.parent.exists()


class TestReportIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_realistic_scenario(self):
        """Test with a realistic deduction scenario."""
        # Ground truth
        true_world = World(
            {
                "Alice": Role.WASHERWOMAN,
                "Bob": Role.INVESTIGATOR,
                "Charlie": Role.EMPATH,
                "Diana": Role.IMP,
                "Eve": Role.SCARLET_WOMAN,
            }
        )
        
        reporter = ReportGenerator(
            true_world=true_world,
            agent_player="Alice",
            agent_role=Role.WASHERWOMAN,
        )
        
        # Initial belief (multiple possibilities)
        initial_worlds = [
            World(
                {"Alice": Role.WASHERWOMAN, "Bob": Role.INVESTIGATOR, 
                 "Charlie": Role.EMPATH, "Diana": Role.IMP, "Eve": Role.SCARLET_WOMAN}
            ),
            World(
                {"Alice": Role.WASHERWOMAN, "Bob": Role.EMPATH,
                 "Charlie": Role.INVESTIGATOR, "Diana": Role.IMP, "Eve": Role.SCARLET_WOMAN}
            ),
        ]
        
        # After Washerwoman info narrows it down
        final_worlds = [initial_worlds[0]]
        
        reporter.add_observation(
            description="Received Washerwoman information",
            constraint_type="washerwoman",
            worlds_before=initial_worlds,
            worlds_after=final_worlds,
            data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
        )
        
        reporter.set_final_belief_state(final_worlds)
        
        report = reporter.generate()
        
        # Verify report quality
        assert "Alice" in report
        assert "Washerwoman" in report
        assert "50.0% reduction" in report  # 2 → 1 world
        assert "100.0%" in report  # Should be 100% accurate
