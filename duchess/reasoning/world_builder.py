"""
World generation and enumeration for reasoning.

This module generates all possible world configurations (role assignments)
that could exist given a set of players and roles. This is the foundation
for worlds-based reasoning.
"""

from itertools import combinations, permutations
from typing import Dict, List, Set, Union

from duchess.engine.game_state import Role, World, create_world
from duchess.utils import get_logger

logger = get_logger(__name__)


class WorldGenerator:
    """
    Generates all possible world configurations for a given setup.
    
    A world is valid if:
    1. Exactly 1 Demon (Imp)
    2. Exactly 1 Minion (Scarlet Woman) for 5-9 players
    3. All other players are Townsfolk roles
    4. Each player has exactly one role
    """
    
    def __init__(self, players: Union[int, List[str]]):
        """
        Initialize the world generator.
        
        Args:
            players: Either number of players (int) or list of player names.
                    If int, generates default names "Player 1", "Player 2", etc.
        """
        if isinstance(players, int):
            # Generate default player names: "Player 1", "Player 2", ...
            self.players = [f"Player {i}" for i in range(1, players + 1)]
        else:
            self.players = players
        self.num_players = len(self.players)
        logger.info(f"Initialized WorldGenerator for {self.num_players} players")
    
    def generate_all_worlds(
        self,
        available_roles: List[Role] | None = None
    ) -> List[World]:
        """
        Generate all possible world configurations.
        
        For MVP with 5 characters, we enumerate all ways to assign:
        - 1 player as Imp (demon)
        - 1 player as Scarlet Woman (minion)
        - Remaining players distributed among Washerwoman, Investigator, Empath, Townsfolk
        
        Args:
            available_roles: List of Townsfolk roles to distribute. If None,
                           uses MVP default: [Washerwoman, Investigator, Empath, Townsfolk...]
        
        Returns:
            List of all valid World configurations
        """
        if self.num_players < 5:
            logger.warning(f"Generating worlds for {self.num_players} players (minimum is 5)")
        
        logger.info(f"Starting world generation for {self.num_players} players")
        
        # Default MVP roles if not specified
        if available_roles is None:
            available_roles = self._get_default_townsfolk_roles()
        
        worlds: List[World] = []
        
        # Choose 1 player to be Imp
        for imp_player in self.players:
            logger.debug(f"Trying {imp_player} as Imp")
            
            # Choose 1 different player to be Scarlet Woman
            for sw_player in self.players:
                if sw_player == imp_player:
                    continue
                
                logger.debug(f"  Trying {sw_player} as Scarlet Woman")
                
                # Remaining players get Townsfolk roles
                remaining_players = [
                    p for p in self.players 
                    if p not in (imp_player, sw_player)
                ]
                
                # Generate all permutations of Townsfolk role assignments
                for townsfolk_assignment in self._assign_townsfolk(
                    remaining_players, 
                    available_roles
                ):
                    # Build complete assignment
                    assignment = {
                        imp_player: Role.IMP,
                        sw_player: Role.SCARLET_WOMAN,
                    }
                    assignment.update(townsfolk_assignment)
                    
                    # Create and validate world
                    try:
                        world = create_world(assignment)
                        worlds.append(world)
                    except ValueError as e:
                        logger.error(f"Failed to create world: {e}")
                        continue
        
        logger.info(f"Generated {len(worlds)} total worlds")
        return worlds
    
    def _get_default_townsfolk_roles(self) -> List[Role]:
        """
        Get the default Townsfolk role distribution for MVP.
        
        For our MVP with 5 characters:
        - Up to 1 Washerwoman
        - Up to 1 Investigator  
        - Up to 1 Empath
        - Remaining players are generic Townsfolk
        
        Returns:
            List of Townsfolk roles matching player count (minus 2 for evil)
        """
        num_good = self.num_players - 2  # Subtract Imp and Scarlet Woman
        
        # Build list of special roles up to the number we need
        special_roles = [
            Role.WASHERWOMAN,
            Role.INVESTIGATOR,
            Role.EMPATH,
        ]
        
        roles = special_roles[:num_good]  # Take only what we need
        
        # Fill remaining slots with generic Townsfolk
        while len(roles) < num_good:
            roles.append(Role.TOWNSFOLK)
        
        logger.debug(f"Default Townsfolk roles: {[r.value for r in roles]}")
        return roles
    
    def _assign_townsfolk(
        self, 
        players: List[str], 
        roles: List[Role]
    ) -> List[Dict[str, Role]]:
        """
        Generate all possible assignments of Townsfolk roles to players.
        
        This handles the case where we have specific roles (Washerwoman, 
        Investigator, Empath) and generic roles (Townsfolk). We need to
        try all permutations.
        
        Args:
            players: List of player names to assign roles to
            roles: List of Townsfolk roles to assign
            
        Returns:
            List of assignment dictionaries mapping player -> role
        """
        if len(players) != len(roles):
            logger.error(
                f"Player count ({len(players)}) doesn't match role count ({len(roles)})"
            )
            raise ValueError("Player count must match role count")
        
        assignments: List[Dict[str, Role]] = []
        
        # Generate all permutations of role assignments
        for role_perm in permutations(roles):
            assignment = {
                player: role 
                for player, role in zip(players, role_perm)
            }
            assignments.append(assignment)
        
        logger.debug(f"Generated {len(assignments)} Townsfolk permutations")
        return assignments
    
    def count_worlds(self) -> int:
        """
        Calculate how many worlds will be generated without actually generating them.
        
        This is useful for estimating computational cost.
        
        Returns:
            Expected number of worlds
        """
        num_good = self.num_players - 2
        
        # Number of ways to choose Imp: n
        # Number of ways to choose Scarlet Woman: n-1
        # Number of permutations of good roles: (num_good)!
        
        import math
        
        imp_choices = self.num_players
        sw_choices = self.num_players - 1
        
        # For MVP with distinct roles (W, I, E, T, T, ...), we need full factorial
        good_perms = math.factorial(num_good)
        
        total = imp_choices * sw_choices * good_perms
        
        logger.debug(
            f"World count calculation: {imp_choices} Imp × {sw_choices} SW × "
            f"{good_perms} good perms = {total}"
        )
        
        return total


def generate_worlds(
    players: List[str],
    available_roles: List[Role] | None = None
) -> List[World]:
    """
    Convenience function to generate all worlds for a player list.
    
    Args:
        players: List of player names
        available_roles: Optional list of Townsfolk roles to use
        
    Returns:
        List of all possible World configurations
    """
    generator = WorldGenerator(players)
    return generator.generate_all_worlds(available_roles)


def filter_worlds(
    worlds: List[World],
    predicate: callable
) -> List[World]:
    """
    Filter a list of worlds based on a predicate function.
    
    This is a helper for constraint application.
    
    Args:
        worlds: List of worlds to filter
        predicate: Function that takes a World and returns bool
        
    Returns:
        Filtered list of worlds where predicate returns True
    """
    initial_count = len(worlds)
    filtered = [w for w in worlds if predicate(w)]
    removed = initial_count - len(filtered)
    
    logger.info(
        f"Filtered worlds: {initial_count} → {len(filtered)} "
        f"(removed {removed})"
    )
    
    return filtered
