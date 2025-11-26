"""
Washerwoman character implementation.

Ability: "You start knowing that 1 of 2 players is a particular Townsfolk."
"""

import random
from typing import Any, List

from duchess.engine.game_state import Role, RoleType, World
from duchess.engine.characters.base import Character, CharacterInfo
from duchess.utils import get_logger

logger = get_logger(__name__)


class Washerwoman(Character):
    """
    Washerwoman - Good Townsfolk
    
    Learns that one of two players is a specific Townsfolk role.
    The information is always truthful (in MVP, no drunk/poisoned).
    """
    
    role = Role.WASHERWOMAN
    
    @staticmethod
    def generate_info(
        world: World,
        player: str,
        night: int = 1,
        **kwargs: Any
    ) -> CharacterInfo:
        """
        Generate Washerwoman information.
        
        Chooses 2 players where at least one has a Townsfolk role,
        then tells the Washerwoman which Townsfolk role one of them has.
        
        Args:
            world: The true game state
            player: The Washerwoman player
            night: Night number (always 1 for Washerwoman)
            **kwargs: Can specify 'target_player' and 'other_player' for testing
            
        Returns:
            CharacterInfo with the two players and Townsfolk role
        """
        Washerwoman.validate_player_has_role(world, player)
        
        logger.info(f"Generating Washerwoman info for {player} on night {night}")
        
        # Get all Townsfolk (excluding the Washerwoman themselves)
        townsfolk_players = [
            p for p, role in world.assignments.items()
            if p != player and role.role_type == RoleType.TOWNSFOLK
        ]
        
        if not townsfolk_players:
            logger.warning(f"No other Townsfolk found in world for {player}")
            raise ValueError("No Townsfolk available for Washerwoman to learn about")
        
        # Choose the target Townsfolk (the one who actually has the role)
        if 'target_player' in kwargs:
            target = kwargs['target_player']
            logger.debug(f"Using specified target: {target}")
        else:
            target = random.choice(townsfolk_players)
            logger.debug(f"Randomly selected target: {target}")
        
        target_role = world.get_role(target)
        
        # Choose the other player (could be anyone except Washerwoman and target)
        other_players = [p for p in world.assignments.keys() if p not in (player, target)]
        
        if 'other_player' in kwargs:
            other = kwargs['other_player']
            logger.debug(f"Using specified other player: {other}")
        else:
            other = random.choice(other_players)
            logger.debug(f"Randomly selected other player: {other}")
        
        # Randomly order the two players for presentation
        players = [target, other]
        random.shuffle(players)
        
        message = (
            f"One of {players[0]} or {players[1]} is the {target_role.value}"
        )
        
        info = CharacterInfo(
            character=Role.WASHERWOMAN,
            night=night,
            data={
                'players': players,
                'role': target_role,
                'truth': target,  # Which player actually has the role
            },
            message=message
        )
        
        logger.info(f"Washerwoman {player} learns: {message}")
        logger.debug(f"Truth: {target} is actually the {target_role.value}")
        
        return info
