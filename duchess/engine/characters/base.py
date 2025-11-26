"""
Base character class for Blood on the Clocktower characters.

All character abilities are implemented as pure functions that take a World
and return information that would be given to the player with that character.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from duchess.engine.game_state import Role, World
from duchess.utils import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CharacterInfo:
    """
    Information provided by a character's ability.
    
    This is what a player receives when their character ability activates.
    The structure varies by character type.
    
    Attributes:
        character: The character role providing this information
        night: Which night this info was received (1 = first night)
        data: Character-specific information dictionary
        message: Human-readable description of the information
    """
    
    character: Role
    night: int
    data: Dict[str, Any]
    message: str
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"Night {self.night} - {self.character.value}: {self.message}"


class Character(ABC):
    """
    Abstract base class for character abilities.
    
    Each character implementation provides a static method to generate
    the information that character receives based on the true game state.
    """
    
    role: Role
    
    @staticmethod
    @abstractmethod
    def generate_info(
        world: World,
        player: str,
        night: int = 1,
        **kwargs: Any
    ) -> CharacterInfo:
        """
        Generate the information this character receives.
        
        Args:
            world: The true game state (complete role assignment)
            player: The player who has this character
            night: Which night it is (default 1 for setup)
            **kwargs: Additional character-specific parameters
            
        Returns:
            CharacterInfo containing what the player learns
            
        Raises:
            ValueError: If player doesn't have this character in the world
        """
        pass
    
    @classmethod
    def validate_player_has_role(cls, world: World, player: str) -> None:
        """
        Verify that the player has this character's role.
        
        Args:
            world: The game world
            player: Player name to check
            
        Raises:
            ValueError: If player doesn't have the expected role
        """
        actual_role = world.get_role(player)
        if actual_role != cls.role:
            logger.error(
                f"Player {player} has role {actual_role.value}, "
                f"not {cls.role.value}"
            )
            raise ValueError(
                f"Player {player} is {actual_role.value}, not {cls.role.value}"
            )
        logger.debug(f"Validated: {player} has role {cls.role.value}")
