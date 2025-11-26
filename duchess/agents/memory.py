"""Agent memory for storing observations and information."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Union
from enum import Enum

from duchess.engine.game_state import Role
from duchess.utils.logger import get_logger

logger = get_logger(__name__)


class InformationType(Enum):
    """Types of information an agent can receive."""

    WASHERWOMAN = "washerwoman"
    INVESTIGATOR = "investigator"
    EMPATH = "empath"
    SELF_KNOWLEDGE = "self_knowledge"  # Agent's own role
    PUBLIC_CLAIM = "public_claim"  # Future: other players' claims


@dataclass
class Information:
    """A piece of information received by an agent.

    This could be from:
    - Their own character ability
    - Public claims from other players (future)
    - Deduced facts (future)
    """

    info_type: InformationType
    data: Dict[str, Any]
    source: str  # Who provided this info ("self", player name, etc.)
    night: int = 0  # Which night this was received (0 = setup)
    trusted: bool = True  # Whether agent trusts this info

    def __repr__(self) -> str:
        """Human-readable representation."""
        if self.info_type == InformationType.WASHERWOMAN:
            players = self.data.get("players", [])
            role = self.data.get("role", "?")
            role_name = role.value if hasattr(role, 'value') else str(role)
            return f"Washerwoman: one of {players} is {role_name}"

        elif self.info_type == InformationType.INVESTIGATOR:
            players = self.data.get("players", [])
            role = self.data.get("role", "?")
            role_name = role.value if hasattr(role, 'value') else str(role)
            return f"Investigator: one of {players} is {role_name}"

        elif self.info_type == InformationType.EMPATH:
            empath_player = self.data.get("empath_player", "?")
            count = self.data.get("evil_count", 0)
            return f"Empath (player {empath_player}): {count} evil neighbor(s)"

        elif self.info_type == InformationType.SELF_KNOWLEDGE:
            role = self.data.get("role", "?")
            role_name = role.value if hasattr(role, 'value') else str(role)
            return f"Self: I am {role_name}"

        else:
            return f"{self.info_type.value}: {self.data}"
@dataclass
class AgentMemory:
    """Memory system for an agent.

    Stores:
    - Agent's identity (name, role)
    - All information received
    - Current belief state (list of possible worlds)
    """

    agent_name: Union[str, int]
    agent_role: Role
    information: List[Information] = field(default_factory=list)
    current_worlds: List = field(default_factory=list)  # List[World] - avoid circular import

    def __post_init__(self):
        """Initialize agent memory with self-knowledge."""
        logger.info(f"Initialized memory for {self.agent_name} ({self.agent_role.value})")

        # Add self-knowledge as first piece of information
        self.add_information(
            info_type=InformationType.SELF_KNOWLEDGE,
            data={"role": self.agent_role},
            source="self",
        )

    def add_information(
        self,
        info_type: InformationType,
        data: Dict[str, Any],
        source: str = "self",
        night: int = 0,
        trusted: bool = True,
    ) -> None:
        """Add a new piece of information to memory.

        Args:
            info_type: Type of information (washerwoman, investigator, etc.)
            data: Information content (players, roles, counts, etc.)
            source: Who provided this info
            night: Which night/day this was received
            trusted: Whether to trust this information
        """
        info = Information(
            info_type=info_type,
            data=data,
            source=source,
            night=night,
            trusted=trusted,
        )

        self.information.append(info)
        logger.debug(f"Added information: {info}")

    def get_trusted_information(self) -> List[Information]:
        """Get all trusted information.

        Returns:
            List of Information objects where trusted=True
        """
        return [info for info in self.information if info.trusted]

    def get_information_by_type(self, info_type: InformationType) -> List[Information]:
        """Get all information of a specific type.

        Args:
            info_type: Type of information to retrieve

        Returns:
            List of matching Information objects
        """
        return [info for info in self.information if info.info_type == info_type]

    def get_character_ability_info(self) -> List[Information]:
        """Get information from character abilities only.

        Returns:
            List of Information from washerwoman/investigator/empath abilities
        """
        ability_types = {
            InformationType.WASHERWOMAN,
            InformationType.INVESTIGATOR,
            InformationType.EMPATH,
        }

        return [
            info for info in self.information
            if info.info_type in ability_types and info.trusted
        ]

    def update_belief_state(self, worlds: List) -> None:
        """Update the current belief state (list of possible worlds).

        Args:
            worlds: List of World objects representing current beliefs
        """
        self.current_worlds = worlds
        logger.debug(f"Updated belief state: {len(worlds)} worlds")

    def get_summary(self) -> str:
        """Get a human-readable summary of agent's memory.

        Returns:
            Multi-line string summarizing agent's knowledge
        """
        lines = [
            f"Agent: {self.agent_name} ({self.agent_role.value})",
            f"Information received: {len(self.information)} pieces",
            f"Current belief state: {len(self.current_worlds)} possible worlds",
            "",
            "Trusted Information:",
        ]

        for i, info in enumerate(self.get_trusted_information(), 1):
            lines.append(f"  {i}. {info}")

        return "\n".join(lines)
