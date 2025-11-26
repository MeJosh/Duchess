"""Scenario system for testing agent reasoning.

Provides hardcoded scenarios for MVP testing of single-agent deduction.
Each scenario represents a complete game setup with a ground truth world
and specific agent perspective.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from duchess.engine.game_state import World, Role
from duchess.agents.agent import ReasoningAgent
from duchess.agents.memory import InformationType
from duchess.utils.logger import logger


@dataclass
class Scenario:
    """A test scenario with ground truth and agent perspective.
    
    Attributes:
        name: Descriptive name for the scenario
        description: What this scenario tests
        players: List of player identifiers
        true_world: The ground truth World
        agent_name: Which player is the reasoning agent
        agent_role: The agent's true role
        observations: List of observations the agent receives
    """
    name: str
    description: str
    players: List[str]
    true_world: World
    agent_name: str
    agent_role: Role
    observations: List[Dict[str, Any]]


class ScenarioRunner:
    """Runs scenarios and collects agent analysis."""
    
    def __init__(self, scenario: Scenario):
        """Initialize runner with a scenario.
        
        Args:
            scenario: The scenario to run
        """
        self.scenario = scenario
        self.agent: Optional[ReasoningAgent] = None
        
    def run(self) -> Dict[str, Any]:
        """Execute the scenario and return analysis results.
        
        Returns:
            Dict containing:
                - scenario_name: Name of the scenario
                - agent_name: Agent identifier
                - agent_role: Agent's role
                - observations_count: Number of observations received
                - initial_worlds: World count before observations
                - final_worlds: World count after all observations
                - proven_facts: Dict of proven player roles
                - role_probabilities: Dict of probability distributions
                - analysis: Full agent analysis
        """
        logger.info(f"Running scenario: {self.scenario.name}")
        
        # Create agent with ground truth for reporting
        self.agent = ReasoningAgent(
            name=self.scenario.agent_name,
            role=self.scenario.agent_role,
            players=self.scenario.players,
            true_world=self.scenario.true_world,
        )
        
        initial_worlds = len(self.agent.memory.current_worlds)
        logger.info(f"Agent initialized with {initial_worlds} possible worlds")
        
        # Feed observations to agent
        for i, obs in enumerate(self.scenario.observations, 1):
            logger.info(f"Applying observation {i}/{len(self.scenario.observations)}")
            self.agent.receive_information(
                info_type=obs["type"],
                data=obs["data"],
            )
            logger.debug(f"Worlds after observation {i}: {len(self.agent.memory.current_worlds)}")
        
        # Get final analysis
        analysis = self.agent.analyze()
        
        results = {
            "scenario_name": self.scenario.name,
            "agent_name": self.scenario.agent_name,
            "agent_role": self.scenario.agent_role.value,
            "observations_count": len(self.scenario.observations),
            "initial_worlds": initial_worlds,
            "final_worlds": analysis["worlds_count"],
            "proven_facts": analysis["proven_facts"],
            "role_probabilities": analysis["probabilities"],  # Map to expected key
            "evil_probabilities": analysis["evil_probabilities"],
            "analysis": analysis,
        }
        
        logger.info(
            f"Scenario complete: {initial_worlds} → {analysis['worlds_count']} worlds, "
            f"{len(analysis['proven_facts'])} proven facts"
        )
        
        return results
    
    def generate_report(self, filepath: Optional[str] = None) -> str:
        """Generate markdown report for the scenario.
        
        Args:
            filepath: Optional path to save report
            
        Returns:
            Markdown-formatted report string
        """
        if not self.agent:
            raise RuntimeError("Must run() scenario before generating report")
        
        return self.agent.generate_report(filepath=filepath)


# Hardcoded scenarios for MVP testing

SCENARIO_WASHERWOMAN_SIMPLE = Scenario(
    name="Washerwoman Simple Test",
    description="Basic washerwoman deduction with clear constraint",
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
        }
    ],
)

SCENARIO_INVESTIGATOR_COMPLEX = Scenario(
    name="Investigator Multiple Constraints",
    description="Investigator with multiple observations",
    players=["Alice", "Bob", "Charlie", "Diana", "Eve"],
    true_world=World({
        "Alice": Role.WASHERWOMAN,
        "Bob": Role.INVESTIGATOR,
        "Charlie": Role.EMPATH,
        "Diana": Role.IMP,
        "Eve": Role.SCARLET_WOMAN,
    }),
    agent_name="Bob",
    agent_role=Role.INVESTIGATOR,
    observations=[
        {
            "type": InformationType.INVESTIGATOR,
            "data": {"players": ["Diana", "Eve"], "role": Role.SCARLET_WOMAN},
        }
    ],
)

SCENARIO_EMPATH_DEDUCTION = Scenario(
    name="Empath Evil Neighbor Detection",
    description="Empath identifying evil neighbors",
    players=["Alice", "Bob", "Charlie", "Diana", "Eve"],
    true_world=World({
        "Alice": Role.WASHERWOMAN,
        "Bob": Role.INVESTIGATOR,
        "Charlie": Role.EMPATH,
        "Diana": Role.IMP,
        "Eve": Role.SCARLET_WOMAN,
    }),
    agent_name="Charlie",
    agent_role=Role.EMPATH,
    observations=[
        {
            "type": InformationType.EMPATH,
            "data": {"empath_player": "Charlie", "evil_count": 1},
        }
    ],
)

# All available scenarios
ALL_SCENARIOS = [
    SCENARIO_WASHERWOMAN_SIMPLE,
    SCENARIO_INVESTIGATOR_COMPLEX,
    SCENARIO_EMPATH_DEDUCTION,
]
