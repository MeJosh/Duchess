"""
Imp character implementation.

Ability: "Each night*, choose a player: they die. If you kill yourself this 
way, a Minion becomes the Imp."

Note: For MVP, we implement the role definition but not full death mechanics.
The Imp's ability is primarily relevant for world-building and identifying evil.
"""

from typing import Any, Optional

from duchess.engine.game_state import Role, World
from duchess.engine.characters.base import Character, CharacterInfo
from duchess.utils import get_logger

logger = get_logger(__name__)


class Imp(Character):
    """
    Imp - Evil Demon
    
    The Imp is the primary evil role. Each night (except the first),
    they choose a player to kill.
    
    For MVP, we don't implement full night actions, but this class
    exists for completeness and world validation.
    """
    
    role = Role.IMP
    
    @staticmethod
    def generate_info(
        world: World,
        player: str,
        night: int = 1,
        **kwargs: Any
    ) -> CharacterInfo:
        """
        Generate Imp information.
        
        The Imp learns who their Minion teammates are on the first night.
        This is standard BotC demon behavior.
        
        Args:
            world: The true game state
            player: The Imp player
            night: Night number
            **kwargs: Unused for Imp
            
        Returns:
            CharacterInfo with minion team information
        """
        Imp.validate_player_has_role(world, player)
        
        logger.info(f"Generating Imp info for {player} on night {night}")
        
        # Get evil team members (minions)
        evil_team = [
            p for p in world.get_evil_players()
            if p != player  # Exclude the Imp themselves
        ]
        
        if evil_team:
            minions_str = ", ".join(evil_team)
            message = f"Your minion(s): {minions_str}"
        else:
            message = "You have no minions (unusual setup)"
            logger.warning(f"Imp {player} has no minion teammates")
        
        info = CharacterInfo(
            character=Role.IMP,
            night=night,
            data={
                'minions': evil_team,
                'team_size': len(evil_team) + 1,  # +1 for the Imp
            },
            message=message
        )
        
        logger.info(f"Imp {player} learns: {message}")
        logger.debug(f"Evil team: {[player] + evil_team}")
        
        return info
