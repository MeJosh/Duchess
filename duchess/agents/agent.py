"""Reasoning agent that builds beliefs and makes deductions."""

from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass

from duchess.engine.game_state import World, Role
from duchess.reasoning.world_builder import generate_worlds
from duchess.reasoning.constraints import (
    apply_constraints,
    WasherwomanConstraint,
    InvestigatorConstraint,
    EmpathConstraint,
)
from duchess.reasoning.deduction import (
    prove_role,
    find_proven_facts,
    calculate_role_probabilities,
    is_proven_good,
    is_proven_evil,
)
from duchess.agents.memory import AgentMemory, InformationType
from duchess.reporting import ReportGenerator
from duchess.utils.logger import get_logger

logger = get_logger(__name__)


class ReasoningAgent:
    """Agent that performs deductive reasoning using world-based belief states.
    
    The agent:
    1. Maintains memory of all information received
    2. Builds a belief state (set of possible worlds)
    3. Applies constraints from trusted information
    4. Makes deductions about role assignments
    5. Can generate analysis reports
    """
    
    def __init__(
        self,
        name: Union[str, int],
        role: Role,
        players: Union[int, List[Union[str, int]]],
        true_world: Optional[World] = None,
    ):
        """Initialize a reasoning agent.
        
        Args:
            name: Agent's identifier (player name or seat number, 1-indexed)
            role: Agent's true role
            players: Either number of players (int) or list of player identifiers.
                    If int, generates default names "Player 1", "Player 2", etc.
            true_world: Ground truth for report generation (optional)
        """
        # Normalize player list
        if isinstance(players, int):
            num_players = players
            player_list = [f"Player {i}" for i in range(1, num_players + 1)]
        else:
            player_list = [str(p) if isinstance(p, int) else p for p in players]
            num_players = len(player_list)
        
        # Normalize agent name
        if isinstance(name, int):
            agent_name = f"Player {name}"
        else:
            agent_name = name
        
        self.name = agent_name
        self.role = role
        self.players = player_list
        self.num_players = num_players
        self.true_world = true_world
        
        # Initialize memory
        self.memory = AgentMemory(agent_name=agent_name, agent_role=role)
        
        # Initialize belief state to all possible worlds
        self._initial_worlds = generate_worlds(players=player_list)
        self.memory.update_belief_state(self._initial_worlds)
        
        # Report generator for analysis visualization (set up before rebuild)
        self.reporter: Optional[ReportGenerator] = None
        if true_world is not None:
            self.reporter = ReportGenerator(
                true_world=true_world,
                agent_player=agent_name,
                agent_role=role,
            )
        
        # Apply self-knowledge to filter worlds
        self.rebuild_belief_state()
        
        logger.info(
            f"Initialized agent {agent_name} ({role.value}) "
            f"with {len(self._initial_worlds)} initial worlds"
        )
    
    def receive_information(
        self,
        info_type: InformationType,
        data: Dict,
        source: str = "self",
        night: int = 0,
    ) -> None:
        """Receive new information and update beliefs.
        
        Args:
            info_type: Type of information received
            data: Information content
            source: Who provided this information
            night: When this was received
        """
        # Add to memory
        self.memory.add_information(
            info_type=info_type,
            data=data,
            source=source,
            night=night,
            trusted=True,  # MVP: trust all info
        )
        
        # Rebuild belief state with new information
        self.rebuild_belief_state()
        
        logger.info(
            f"{self.name} received {info_type.value} info, "
            f"now {len(self.memory.current_worlds)} worlds remain"
        )
    
    def rebuild_belief_state(self) -> None:
        """Rebuild belief state by applying all trusted information."""
        worlds = self._initial_worlds.copy()
        worlds_before = len(worlds)
        
        # Get all trusted information
        trusted_info = self.memory.get_trusted_information()
        
        # Apply each constraint
        for info in trusted_info:
            worlds_after_prev = len(worlds)
            
            if info.info_type == InformationType.SELF_KNOWLEDGE:
                # Apply self role knowledge
                from duchess.reasoning.constraints import RoleConstraint
                constraint = RoleConstraint(
                    player=self.name,
                    role=info.data["role"],
                )
                worlds = apply_constraints(worlds, [constraint])
            
            elif info.info_type == InformationType.WASHERWOMAN:
                players = info.data["players"]
                constraint = WasherwomanConstraint(
                    player1=players[0],
                    player2=players[1],
                    role=info.data["role"],
                )
                worlds = apply_constraints(worlds, [constraint])
            
            elif info.info_type == InformationType.INVESTIGATOR:
                players = info.data["players"]
                constraint = InvestigatorConstraint(
                    player1=players[0],
                    player2=players[1],
                    role=info.data["role"],
                )
                worlds = apply_constraints(worlds, [constraint])
            
            elif info.info_type == InformationType.EMPATH:
                constraint = EmpathConstraint(
                    empath_player=info.data["empath_player"],
                    evil_count=info.data["evil_count"],
                )
                worlds = apply_constraints(worlds, [constraint])
            
            # Track in reporter if available
            if self.reporter and info.info_type != InformationType.SELF_KNOWLEDGE:
                # Get proven facts after this constraint
                proven = find_proven_facts(worlds)
                
                # Create a temporary list to track worlds_before for this step
                # (we need the count before this specific constraint)
                temp_worlds = self._initial_worlds.copy()
                for prev_info in trusted_info:
                    if prev_info == info:
                        break
                    # Apply previous constraints
                    if prev_info.info_type == InformationType.SELF_KNOWLEDGE:
                        from duchess.reasoning.constraints import RoleConstraint
                        constraint = RoleConstraint(
                            player=self.name,
                            role=prev_info.data["role"],
                        )
                        temp_worlds = apply_constraints(temp_worlds, [constraint])
                    elif prev_info.info_type == InformationType.WASHERWOMAN:
                        players = prev_info.data["players"]
                        constraint = WasherwomanConstraint(
                            player1=players[0],
                            player2=players[1],
                            role=prev_info.data["role"],
                        )
                        temp_worlds = apply_constraints(temp_worlds, [constraint])
                    elif prev_info.info_type == InformationType.INVESTIGATOR:
                        players = prev_info.data["players"]
                        constraint = InvestigatorConstraint(
                            player1=players[0],
                            player2=players[1],
                            role=prev_info.data["role"],
                        )
                        temp_worlds = apply_constraints(temp_worlds, [constraint])
                    elif prev_info.info_type == InformationType.EMPATH:
                        constraint = EmpathConstraint(
                            empath_player=prev_info.data["empath_player"],
                            evil_count=prev_info.data["evil_count"],
                        )
                        temp_worlds = apply_constraints(temp_worlds, [constraint])
                
                self.reporter.add_observation(
                    description=str(info),
                    constraint_type=info.info_type.value,
                    worlds_before=temp_worlds,
                    worlds_after=worlds,
                    data=info.data,
                )
        
        # Update memory
        self.memory.update_belief_state(worlds)
        
        logger.debug(
            f"Rebuilt belief state: {worlds_before} → {len(worlds)} worlds "
            f"({len(trusted_info)} constraints applied)"
        )
    
    def get_proven_facts(self) -> Dict[Union[str, int], Role]:
        """Get all proven role assignments.
        
        Returns:
            Dictionary mapping players to their proven roles
        """
        return find_proven_facts(self.memory.current_worlds)
    
    def get_role_probabilities(
        self,
        player: Union[str, int]
    ) -> Dict[Role, float]:
        """Calculate probability distribution over roles for a player.
        
        Args:
            player: Player to analyze
            
        Returns:
            Dictionary mapping roles to probabilities
        """
        return calculate_role_probabilities(self.memory.current_worlds, player)
    
    def is_good(self, player: Union[str, int]) -> Optional[bool]:
        """Check if a player is proven good.
        
        Args:
            player: Player to check
            
        Returns:
            True if proven good, False if proven evil, None if uncertain
        """
        if is_proven_good(self.memory.current_worlds, player):
            return True
        elif is_proven_evil(self.memory.current_worlds, player):
            return False
        else:
            return None
    
    def get_evil_probability(self, player: Union[str, int]) -> float:
        """Calculate probability that a player is evil.
        
        Args:
            player: Player to analyze
            
        Returns:
            Probability (0.0 to 1.0) that player is evil
        """
        probs = self.get_role_probabilities(player)
        evil_roles = {Role.IMP, Role.SCARLET_WOMAN}
        return sum(prob for role, prob in probs.items() if role in evil_roles)
    
    def analyze(self) -> Dict[str, any]:
        """Perform comprehensive analysis of current belief state.
        
        Returns:
            Dictionary containing:
            - worlds_count: Number of possible worlds
            - proven_facts: Certain role assignments
            - probabilities: Role probabilities for each player
            - evil_probabilities: Likelihood each player is evil
        """
        worlds = self.memory.current_worlds
        proven = self.get_proven_facts()
        
        # Get all players from first world
        if worlds:
            players = list(worlds[0].assignments.keys())
        else:
            players = []
        
        # Calculate probabilities for each player
        probabilities = {}
        evil_probs = {}
        
        for player in players:
            if player != self.name:  # Don't analyze self
                probabilities[player] = self.get_role_probabilities(player)
                evil_probs[player] = self.get_evil_probability(player)
        
        analysis = {
            "agent": self.name,
            "role": self.role,
            "worlds_count": len(worlds),
            "proven_facts": proven,
            "probabilities": probabilities,
            "evil_probabilities": evil_probs,
        }
        
        logger.info(f"Analysis complete: {len(proven)} proven facts, {len(worlds)} worlds")
        
        return analysis
    
    def generate_report(self, filepath: Optional[str] = None) -> str:
        """Generate a detailed analysis report.
        
        Args:
            filepath: If provided, save report to this file
            
        Returns:
            Markdown-formatted report
        """
        if self.reporter is None:
            raise ValueError("Cannot generate report without true_world")
        
        # Set final belief state
        self.reporter.set_final_belief_state(self.memory.current_worlds)
        
        # Generate report
        report = self.reporter.generate()
        
        # Save if filepath provided
        if filepath:
            self.reporter.save(filepath)
            logger.info(f"Report saved to {filepath}")
        
        return report
    
    def get_summary(self) -> str:
        """Get human-readable summary of agent's state.
        
        Returns:
            Multi-line string with analysis summary
        """
        analysis = self.analyze()
        
        lines = [
            f"Agent: {self.name} ({self.role.value})",
            f"Possible worlds: {analysis['worlds_count']}",
            "",
            "Proven Facts:",
        ]
        
        if analysis["proven_facts"]:
            for player, role in analysis["proven_facts"].items():
                marker = " (self)" if player == self.name else ""
                lines.append(f"  - {player}: {role.value}{marker}")
        else:
            lines.append("  (none)")
        
        lines.append("")
        lines.append("Evil Probabilities:")
        
        for player, prob in sorted(
            analysis["evil_probabilities"].items(),
            key=lambda x: -x[1]
        ):
            lines.append(f"  - {player}: {prob:.1%}")
        
        return "\n".join(lines)
