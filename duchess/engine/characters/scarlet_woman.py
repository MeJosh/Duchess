"""
Scarlet Woman character implementation.

Ability: "If there are 5 or more players alive & the Demon dies, you become 
the Demon."

Note: For MVP, this is primarily a role marker. The transformation mechanic
will be relevant for later phases when we model death and game progression.
"""

from typing import Any

from duchess.engine.game_state import Role, World
from duchess.engine.characters.base import Character, CharacterInfo
from duchess.utils import get_logger

logger = get_logger(__name__)


class ScarletWoman(Character):
    """
    Scarlet Woman - Evil Minion
    
    Becomes the Demon if the Demon dies while 5+ players are alive.
    
    For MVP, we implement basic team information. The transformation
    mechanic is deferred to later phases.
    """
    
    role = Role.SCARLET_WOMAN
    
    @staticmethod
    def generate_info(
        world: World,
        player: str,
        night: int = 1,
        **kwargs: Any
    ) -> CharacterInfo:
        """
        Generate Scarlet Woman information.
        
        The Scarlet Woman learns who the Demon is and who other evil
        players are on the first night.
        
        Args:
            world: The true game state
            player: The Scarlet Woman player
            night: Night number
            **kwargs: Unused for Scarlet Woman
            
        Returns:
            CharacterInfo with evil team information
        """
        ScarletWoman.validate_player_has_role(world, player)
        
        logger.info(f"Generating Scarlet Woman info for {player} on night {night}")
        
        # Get all evil players
        evil_team = list(world.get_evil_players())
        
        # Identify the Demon
        demon_players = [
            p for p, role in world.assignments.items()
            if role.role_type.name == 'DEMON'
        ]
        
        if not demon_players:
            logger.error("No demon found in world - invalid state")
            raise ValueError("World must have a Demon for Scarlet Woman")
        
        demon = demon_players[0]
        
        # Other evil players (excluding self)
        other_evil = [p for p in evil_team if p != player]
        
        if other_evil:
            team_str = ", ".join(other_evil)
            message = f"Your demon: {demon}. Evil team: {team_str}"
        else:
            message = f"Your demon: {demon}. You are the only minion."
            logger.warning(f"Scarlet Woman {player} has no other evil teammates")
        
        info = CharacterInfo(
            character=Role.SCARLET_WOMAN,
            night=night,
            data={
                'demon': demon,
                'evil_team': evil_team,
                'can_become_demon': len(world.assignments) >= 5,
            },
            message=message
        )
        
        logger.info(f"Scarlet Woman {player} learns: {message}")
        logger.debug(f"Evil team composition: {evil_team}")
        
        return info
