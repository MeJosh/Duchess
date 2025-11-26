"""
Report generator for agent analysis results.

Generates markdown reports showing agent reasoning progress and accuracy.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union

from duchess.engine.game_state import World, Role
from duchess.reasoning.deduction import (
    prove_role,
    is_proven_evil,
    is_proven_good,
    calculate_role_probabilities,
    find_proven_facts,
)
from duchess.utils import get_logger

logger = get_logger(__name__)


@dataclass
class Observation:
    """
    A single observation made by the agent.
    
    Attributes:
        step: Sequential step number (0, 1, 2, ...)
        description: Human-readable description of the observation
        constraint_type: Type of constraint applied (e.g., "washerwoman", "empath")
        worlds_before: Number of worlds before applying this observation
        worlds_after: Number of worlds after applying this observation
        proven_facts: New facts proven at this step
        data: Additional structured data about the observation
    """
    step: int
    description: str
    constraint_type: str
    worlds_before: int
    worlds_after: int
    proven_facts: Dict[Union[int, str], Role] = field(default_factory=dict)
    data: Dict = field(default_factory=dict)


class ReportGenerator:
    """
    Generate analysis reports for agent reasoning.
    
    Creates markdown reports showing:
    - Ground truth (true game state)
    - Timeline of observations and deductions
    - Final belief state
    - Accuracy metrics
    """
    
    def __init__(
        self,
        true_world: World,
        agent_player: Union[int, str],
        agent_role: Role,
    ):
        """
        Initialize report generator.
        
        Args:
            true_world: The actual game state (ground truth)
            agent_player: Player identifier for the agent
            agent_role: The agent's true role
        """
        self.true_world = true_world
        self.agent_player = agent_player
        self.agent_role = agent_role
        self.observations: List[Observation] = []
        self.final_worlds: Optional[List[World]] = None
        
        logger.info(
            f"Initialized ReportGenerator for {agent_player} ({agent_role.name})"
        )
    
    def add_observation(
        self,
        description: str,
        constraint_type: str,
        worlds_before: List[World],
        worlds_after: List[World],
        data: Optional[Dict] = None,
    ) -> None:
        """
        Record an observation made by the agent.
        
        Args:
            description: Human-readable description
            constraint_type: Type of constraint (e.g., "washerwoman")
            worlds_before: Belief state before this observation
            worlds_after: Belief state after this observation
            data: Additional structured data
        """
        step = len(self.observations)
        
        # Find newly proven facts
        facts_before = find_proven_facts(worlds_before) if worlds_before else {}
        facts_after = find_proven_facts(worlds_after)
        
        new_facts = {
            player: role
            for player, role in facts_after.items()
            if player not in facts_before or facts_before[player] != role
        }
        
        obs = Observation(
            step=step,
            description=description,
            constraint_type=constraint_type,
            worlds_before=len(worlds_before),
            worlds_after=len(worlds_after),
            proven_facts=new_facts,
            data=data or {},
        )
        
        self.observations.append(obs)
        logger.debug(
            f"Added observation {step}: {description} "
            f"({len(worlds_before)} → {len(worlds_after)} worlds)"
        )
    
    def set_final_belief_state(self, worlds: List[World]) -> None:
        """
        Set the final belief state after all observations.
        
        Args:
            worlds: Final list of possible worlds
        """
        self.final_worlds = worlds
        logger.info(f"Final belief state: {len(worlds)} worlds")
    
    def generate(self) -> str:
        """
        Generate the complete markdown report.
        
        Returns:
            Markdown-formatted report string
        """
        logger.info("Generating report...")
        
        sections = [
            self._generate_header(),
            self._generate_ground_truth(),
            self._generate_timeline(),
            self._generate_final_analysis(),
            self._generate_accuracy_score(),
        ]
        
        report = "\n\n".join(sections)
        logger.info("Report generated successfully")
        return report
    
    def save(self, filepath: Union[str, Path]) -> None:
        """
        Generate and save report to file.
        
        Args:
            filepath: Path to save the report
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate()
        filepath.write_text(report)
        
        logger.info(f"Report saved to {filepath}")
    
    def _generate_header(self) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Agent Analysis Report

**Generated:** {timestamp}  
**Agent:** {self.agent_player} ({self.agent_role.name})  
**Total Observations:** {len(self.observations)}"""
    
    def _generate_ground_truth(self) -> str:
        """Generate ground truth section showing true game state."""
        lines = ["## Ground Truth", "", "**TRUE ROLES:**"]
        
        # Sort players for consistent output
        players = sorted(self.true_world.assignments.keys(), key=str)
        
        for player in players:
            role = self.true_world.get_role(player)
            alignment = "GOOD" if role.is_good() else "EVIL"
            role_type = role.role_type.name.title()
            
            # Add marker for agent's own role
            marker = " ⭐ (Agent)" if player == self.agent_player else ""
            
            lines.append(
                f"- **{player}**: {role.name.replace('_', ' ').title()} "
                f"[{alignment} - {role_type}]{marker}"
            )
        
        return "\n".join(lines)
    
    def _generate_timeline(self) -> str:
        """Generate timeline of observations and deductions."""
        if not self.observations:
            return "## Observation Timeline\n\n*No observations recorded.*"
        
        lines = ["## Observation Timeline", ""]
        
        for obs in self.observations:
            lines.append(f"### Step {obs.step}: {obs.description}")
            lines.append("")
            
            # Show world reduction
            reduction_pct = 0
            if obs.worlds_before > 0:
                reduction_pct = (
                    (obs.worlds_before - obs.worlds_after) / obs.worlds_before * 100
                )
            
            lines.append(f"**Belief State Update:**")
            lines.append(f"- Worlds before: {obs.worlds_before}")
            lines.append(f"- Worlds after: {obs.worlds_after}")
            lines.append(f"- Reduction: {reduction_pct:.1f}%")
            lines.append("")
            
            # Show new proven facts
            if obs.proven_facts:
                lines.append("**Newly Proven Facts:**")
                for player, role in obs.proven_facts.items():
                    lines.append(f"- ✓ {player} is {role.name.replace('_', ' ').title()}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_final_analysis(self) -> str:
        """Generate final analysis section showing conclusions."""
        if self.final_worlds is None:
            return "## Final Analysis\n\n*No final belief state set.*"
        
        lines = ["## Final Analysis", ""]
        
        # Overall statistics
        initial_worlds = self.observations[0].worlds_before if self.observations else 0
        final_count = len(self.final_worlds)
        
        if initial_worlds > 0:
            reduction_pct = (initial_worlds - final_count) / initial_worlds * 100
            lines.append(
                f"**Worlds Remaining:** {final_count} "
                f"({reduction_pct:.1f}% reduction from initial)"
            )
        else:
            lines.append(f"**Worlds Remaining:** {final_count}")
        
        lines.append("")
        
        # Proven facts
        proven = find_proven_facts(self.final_worlds)
        
        if proven:
            lines.append("### Proven Facts (100% Certain)")
            lines.append("")
            for player, role in sorted(proven.items(), key=lambda x: str(x[0])):
                marker = " (self-knowledge)" if player == self.agent_player else ""
                lines.append(f"- ✓ **{player}**: {role.name.replace('_', ' ').title()}{marker}")
            lines.append("")
        
        # High confidence predictions
        lines.append("### Role Probabilities")
        lines.append("")
        
        # Get players from the belief state worlds instead of ground truth
        if self.final_worlds:
            players = sorted(self.final_worlds[0].assignments.keys(), key=str)
        else:
            players = sorted(self.true_world.assignments.keys(), key=str)
        
        for player in players:
            if player in proven:
                continue  # Skip already proven
            
            probs = calculate_role_probabilities(self.final_worlds, player)
            
            if not probs:
                continue
            
            # Show top 2 most likely roles
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            top_roles = sorted_probs[:2]
            
            lines.append(f"**{player}:**")
            for role, prob in top_roles:
                confidence = "High" if prob >= 0.9 else "Medium" if prob >= 0.7 else "Low"
                lines.append(
                    f"- {role.name.replace('_', ' ').title()}: {prob:.1%} ({confidence})"
                )
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_accuracy_score(self) -> str:
        """Generate accuracy metrics comparing predictions to ground truth."""
        if self.final_worlds is None:
            return "## Accuracy Report\n\n*No final belief state set.*"
        
        lines = ["## Accuracy Report", ""]
        
        # Get players from the belief state worlds instead of ground truth
        if self.final_worlds:
            players = sorted(self.final_worlds[0].assignments.keys(), key=str)
        else:
            players = sorted(self.true_world.assignments.keys(), key=str)
        
        # Calculate role prediction accuracy
        correct_roles = 0
        total_roles = 0
        predictions = []
        
        for player in players:
            true_role = self.true_world.get_role(player)
            
            # Skip agent's self-knowledge
            if player == self.agent_player:
                continue
            
            total_roles += 1
            
            # Get predicted role (highest probability)
            probs = calculate_role_probabilities(self.final_worlds, player)
            
            if probs:
                predicted_role = max(probs.items(), key=lambda x: x[1])
                confidence = predicted_role[1]
                
                is_correct = predicted_role[0] == true_role
                if is_correct:
                    correct_roles += 1
                
                predictions.append({
                    "player": player,
                    "true": true_role,
                    "predicted": predicted_role[0],
                    "confidence": confidence,
                    "correct": is_correct,
                })
        
        # Summary
        if total_roles > 0:
            accuracy_pct = correct_roles / total_roles * 100
            lines.append(
                f"**Role Prediction Accuracy:** {correct_roles}/{total_roles} "
                f"({accuracy_pct:.1f}%)"
            )
        else:
            lines.append("**Role Prediction Accuracy:** N/A")
        
        lines.append("")
        
        # Detailed predictions
        lines.append("### Detailed Predictions")
        lines.append("")
        
        for pred in predictions:
            symbol = "✓" if pred["correct"] else "✗"
            true_name = pred["true"].name.replace("_", " ").title()
            pred_name = pred["predicted"].name.replace("_", " ").title()
            
            if pred["correct"]:
                lines.append(
                    f"- {symbol} **{pred['player']}**: Predicted {pred_name} "
                    f"({pred['confidence']:.1%}) → CORRECT"
                )
            else:
                lines.append(
                    f"- {symbol} **{pred['player']}**: Predicted {pred_name} "
                    f"({pred['confidence']:.1%}) → Actually {true_name}"
                )
        
        lines.append("")
        
        # Alignment accuracy
        correct_alignments = 0
        total_alignments = 0
        
        for player in players:
            if player == self.agent_player:
                continue
            
            total_alignments += 1
            
            true_evil = self.true_world.get_role(player).is_evil()
            predicted_evil = is_proven_evil(self.final_worlds, player)
            predicted_good = is_proven_good(self.final_worlds, player)
            
            # Check if we got alignment right
            if (true_evil and predicted_evil) or (not true_evil and predicted_good):
                correct_alignments += 1
        
        if total_alignments > 0:
            alignment_pct = correct_alignments / total_alignments * 100
            lines.append(
                f"**Alignment Detection:** {correct_alignments}/{total_alignments} "
                f"({alignment_pct:.1f}%)"
            )
        
        return "\n".join(lines)
