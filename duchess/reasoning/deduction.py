"""
Deduction engine for symbolic and probabilistic reasoning.

Provides functions to:
- Prove facts when all remaining worlds agree
- Calculate probability distributions over roles
- Identify proven evil/good players
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Union, Tuple, Callable
from duchess.engine.game_state import World, Role
from duchess.utils.logger import setup_logger

logger = setup_logger(__name__)


def prove_role(worlds: List[World], player: Union[int, str]) -> Optional[Role]:
    """
    Determine if a player's role is proven across all worlds.
    
    If all remaining worlds assign the same role to the player, that role
    is proven. Otherwise, the role is uncertain.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        The proven role if certain, None if uncertain
    """
    if not worlds:
        logger.warning(f"Cannot prove role for player {player}: no worlds")
        return None
    
    roles = {world.get_role(player) for world in worlds}
    
    if len(roles) == 1:
        proven_role = roles.pop()
        logger.info(f"Player {player} is proven to be {proven_role.name}")
        return proven_role
    else:
        logger.debug(
            f"Player {player} role uncertain: {len(roles)} possibilities "
            f"({', '.join(r.name for r in roles)})"
        )
        return None


def is_proven_evil(worlds: List[World], player: Union[int, str]) -> bool:
    """
    Check if a player is proven to be evil.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        True if player is evil in all worlds, False otherwise
    """
    if not worlds:
        return False
    
    is_evil_in_all = all(world.get_role(player).is_evil() for world in worlds)
    
    if is_evil_in_all:
        logger.info(f"Player {player} is proven evil")
    
    return is_evil_in_all


def is_proven_good(worlds: List[World], player: Union[int, str]) -> bool:
    """
    Check if a player is proven to be good.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        True if player is good in all worlds, False otherwise
    """
    if not worlds:
        return False
    
    is_good_in_all = all(world.get_role(player).is_good() for world in worlds)
    
    if is_good_in_all:
        logger.info(f"Player {player} is proven good")
    
    return is_good_in_all


def calculate_role_probabilities(
    worlds: List[World], 
    player: Union[int, str]
) -> Dict[Role, float]:
    """
    Calculate probability distribution over roles for a player.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        Dictionary mapping each possible role to its probability
    """
    if not worlds:
        logger.warning(f"Cannot calculate probabilities for player {player}: no worlds")
        return {}
    
    role_counts: Dict[Role, int] = defaultdict(int)
    
    for world in worlds:
        role = world.get_role(player)
        role_counts[role] += 1
    
    total = len(worlds)
    probabilities = {
        role: count / total
        for role, count in role_counts.items()
    }
    
    logger.debug(
        f"Player {player} role probabilities: "
        f"{', '.join(f'{r.name}: {p:.1%}' for r, p in probabilities.items())}"
    )
    
    return probabilities


def calculate_alignment_probabilities(
    worlds: List[World],
    player: Union[int, str]
) -> Tuple[float, float]:
    """
    Calculate probability that a player is good vs evil.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        Tuple of (good_probability, evil_probability)
    """
    if not worlds:
        logger.warning(f"Cannot calculate alignment for player {player}: no worlds")
        return (0.0, 0.0)
    
    evil_count = sum(1 for world in worlds if world.get_role(player).is_evil())
    good_count = len(worlds) - evil_count
    
    total = len(worlds)
    good_prob = good_count / total
    evil_prob = evil_count / total
    
    logger.debug(
        f"Player {player} alignment: "
        f"{good_prob:.1%} good, {evil_prob:.1%} evil"
    )
    
    return (good_prob, evil_prob)


def find_proven_facts(worlds: List[World]) -> Dict[Union[int, str], Role]:
    """
    Find all proven role assignments across all players.
    
    Args:
        worlds: List of possible worlds
        
    Returns:
        Dictionary mapping players to their proven roles
    """
    if not worlds:
        logger.warning("Cannot find proven facts: no worlds")
        return {}
    
    # Get all players from first world (all worlds have same players)
    players = list(worlds[0].assignments.keys())
    
    proven_facts = {}
    for player in players:
        role = prove_role(worlds, player)
        if role is not None:
            proven_facts[player] = role
    
    logger.info(
        f"Found {len(proven_facts)} proven facts out of {len(players)} players"
    )
    
    return proven_facts


def get_possible_roles(
    worlds: List[World],
    player: Union[int, str]
) -> Set[Role]:
    """
    Get all possible roles for a player across worlds.
    
    Args:
        worlds: List of possible worlds
        player: Player identifier
        
    Returns:
        Set of all roles the player could have
    """
    if not worlds:
        return set()
    
    return {world.get_role(player) for world in worlds}


def count_worlds_where(
    worlds: List[World],
    predicate: Callable[[World], bool]
) -> int:
    """
    Count how many worlds satisfy a predicate function.
    
    Args:
        worlds: List of possible worlds
        predicate: Function that takes a World and returns bool
        
    Returns:
        Count of worlds where predicate returns True
        
    Example:
        # Count worlds where player 0 is the Imp
        count = count_worlds_where(worlds, lambda w: w.get_role(0) == Role.IMP)
    """
    count = sum(1 for world in worlds if predicate(world))
    
    if worlds:
        logger.debug(
            f"Predicate matches {count}/{len(worlds)} worlds ({count/len(worlds):.1%})"
        )
    
    return count
