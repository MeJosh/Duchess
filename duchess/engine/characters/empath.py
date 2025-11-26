"""
Empath character implementation.

Ability: "Each night, you learn how many of your living neighbors are evil."
"""

from typing import Any

from duchess.engine.game_state import Role, World
from duchess.engine.characters.base import Character, CharacterInfo
from duchess.utils import get_logger

logger = get_logger(__name__)


class Empath(Character):
    """
    Empath - Good Townsfolk
    
    Each night, learns how many of their two living neighbors are evil.
    Returns 0, 1, or 2.
    """
    
    role = Role.EMPATH
    
    @staticmethod
    def generate_info(
        world: World,
        player: str,
        night: int = 1,
        **kwargs: Any
    ) -> CharacterInfo:
        """
        Generate Empath information.
        
        Counts how many of the Empath's two neighbors are evil
        (Demon or Minion).
        
        Args:
            world: The true game state
            player: The Empath player
            night: Night number (1+ for Empath, triggers each night)
            **kwargs: Unused for Empath
            
        Returns:
            CharacterInfo with evil neighbor count
        """
        Empath.validate_player_has_role(world, player)
        
        logger.info(f"Generating Empath info for {player} on night {night}")
        
        # Get neighbors (returns tuple of left, right)
        try:
            left_neighbor, right_neighbor = world.get_neighbors(player)
            neighbors = [left_neighbor, right_neighbor]
            logger.debug(f"{player}'s neighbors: {neighbors}")
        except ValueError as e:
            logger.error(f"Cannot get neighbors for {player}: {e}")
            raise
        
        # Count evil neighbors
        evil_count = sum(1 for neighbor in neighbors if world.is_evil(neighbor))
        
        neighbor_details = [
            f"{n} ({world.get_role(n).value}, {'evil' if world.is_evil(n) else 'good'})"
            for n in neighbors
        ]
        
        message = f"{evil_count} of your neighbors are evil"
        
        info = CharacterInfo(
            character=Role.EMPATH,
            night=night,
            data={
                'neighbors': neighbors,
                'evil_count': evil_count,
            },
            message=message
        )
        
        logger.info(f"Empath {player} learns: {message}")
        logger.debug(f"Neighbor details: {neighbor_details}")
        
        return info
