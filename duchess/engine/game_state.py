"""
Game state representation for Blood on the Clocktower.

Defines core data structures for representing game configurations (worlds),
players, and roles. All game state is immutable to support pure functional
reasoning.
"""

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Dict, FrozenSet, Mapping, Set, Union

from duchess.utils import get_logger

logger = get_logger(__name__)


class Team(Enum):
    """Player team alignment."""
    GOOD = "good"
    EVIL = "evil"


class RoleType(Enum):
    """Category of character role."""
    TOWNSFOLK = "townsfolk"
    OUTSIDER = "outsider"
    MINION = "minion"
    DEMON = "demon"


class Role(Enum):
    """Character roles available in the game.
    
    For MVP, we implement 5 roles:
    - Washerwoman, Investigator, Empath (Good/Townsfolk)
    - Scarlet Woman (Evil/Minion)
    - Imp (Evil/Demon)
    """
    
    # Townsfolk (Good team)
    WASHERWOMAN = "Washerwoman"
    INVESTIGATOR = "Investigator"
    EMPATH = "Empath"
    TOWNSFOLK = "Townsfolk"  # Generic good role
    
    # Minions (Evil team)
    SCARLET_WOMAN = "Scarlet Woman"
    
    # Demons (Evil team)
    IMP = "Imp"
    
    @property
    def team(self) -> Team:
        """Return the team alignment for this role."""
        if self in (Role.IMP, Role.SCARLET_WOMAN):
            return Team.EVIL
        return Team.GOOD
    
    @property
    def role_type(self) -> RoleType:
        """Return the role type category."""
        if self == Role.IMP:
            return RoleType.DEMON
        elif self == Role.SCARLET_WOMAN:
            return RoleType.MINION
        else:
            return RoleType.TOWNSFOLK
    
    def is_evil(self) -> bool:
        """Check if this role is on the evil team."""
        return self.team == Team.EVIL
    
    def is_good(self) -> bool:
        """Check if this role is on the good team."""
        return self.team == Team.GOOD


@dataclass(frozen=True)
class World:
    """
    Immutable representation of a complete role assignment.
    
    A "world" is a possible game configuration where each player has exactly
    one role. This is the fundamental unit for worlds-based reasoning.
    
    Attributes:
        assignments: Immutable mapping from player name to their role
        skip_validation: If True, skip game rules validation (useful for unit tests)
    """
    
    assignments: Mapping[str, Role]
    skip_validation: bool = False
    
    def __post_init__(self) -> None:
        """Validate the world after creation."""
        logger.debug(f"Creating world with {len(self.assignments)} players")
        
        # Convert to truly immutable mapping
        object.__setattr__(self, 'assignments', MappingProxyType(dict(self.assignments)))
        
        if not self.assignments:
            logger.error("Attempted to create empty world")
            raise ValueError("World must have at least one player")
        
        # Validate world consistency (unless skipped for testing)
        if not self.skip_validation:
            self._validate()
            logger.debug(f"World created successfully: {self._summary()}")
        else:
            logger.debug(f"World created (validation skipped): {self._summary()}")
    
    def _validate(self) -> None:
        """Validate that the world configuration is legal."""
        role_counts = self._count_roles()
        
        # Check demon count
        demon_count = sum(1 for r in self.assignments.values() if r.role_type == RoleType.DEMON)
        if demon_count != 1:
            logger.error(f"Invalid demon count: {demon_count} (expected 1)")
            raise ValueError(f"World must have exactly 1 Demon, found {demon_count}")
        
        # Check minion count (for 7 players, should be exactly 1)
        minion_count = sum(1 for r in self.assignments.values() if r.role_type == RoleType.MINION)
        player_count = len(self.assignments)
        
        # Standard BotC: 5-6 players = 1 minion, 7-9 = 1 minion, 10-12 = 2 minions, etc.
        # For MVP with 7 players, we expect exactly 1 minion
        expected_minions = 1 if player_count <= 9 else 2
        
        if minion_count != expected_minions:
            logger.warning(
                f"Unusual minion count: {minion_count} for {player_count} players "
                f"(expected {expected_minions})"
            )
    
    def _count_roles(self) -> Dict[Role, int]:
        """Count occurrences of each role."""
        counts: Dict[Role, int] = {}
        for role in self.assignments.values():
            counts[role] = counts.get(role, 0) + 1
        return counts
    
    def _summary(self) -> str:
        """Generate a brief summary of this world."""
        role_counts = self._count_roles()
        evil_count = sum(1 for r in self.assignments.values() if r.is_evil())
        return f"{len(self.assignments)} players, {evil_count} evil, roles={role_counts}"
    
    def get_role(self, player: Union[int, str]) -> Role:
        """
        Get the role of a specific player.
        
        Args:
            player: Player identifier (name or index)
            
        Returns:
            The role assigned to this player
            
        Raises:
            KeyError: If player not in this world
        """
        if player not in self.assignments:
            logger.error(f"Player '{player}' not found in world")
            raise KeyError(f"Player '{player}' not in world")
        return self.assignments[player]
    
    def is_evil(self, player: Union[int, str]) -> bool:
        """Check if a player is on the evil team."""
        return self.get_role(player).is_evil()
    
    def is_good(self, player: Union[int, str]) -> bool:
        """Check if a player is on the good team."""
        return self.get_role(player).is_good()
    
    def get_players_with_role(self, role: Role) -> Set[str]:
        """Get all players with a specific role."""
        return {player for player, r in self.assignments.items() if r == role}
    
    def get_evil_players(self) -> Set[str]:
        """Get all players on the evil team."""
        return {player for player, role in self.assignments.items() if role.is_evil()}
    
    def get_good_players(self) -> Set[str]:
        """Get all players on the good team."""
        return {player for player, role in self.assignments.items() if role.is_good()}
    
    def get_neighbors(self, player: Union[int, str]) -> tuple[Union[int, str], Union[int, str]]:
        """
        Get the clockwise and counter-clockwise neighbors of a player.
        
        Assumes players are seated in the order they appear in assignments.
        
        Args:
            player: Player identifier to find neighbors for
            
        Returns:
            Tuple of (left_neighbor, right_neighbor)
            
        Raises:
            KeyError: If player not in world
            ValueError: If fewer than 3 players (can't have distinct neighbors)
        """
        players = list(self.assignments.keys())
        
        if player not in players:
            raise KeyError(f"Player '{player}' not in world")
        
        if len(players) < 3:
            raise ValueError("Need at least 3 players to determine neighbors")
        
        idx = players.index(player)
        left = players[(idx - 1) % len(players)]
        right = players[(idx + 1) % len(players)]
        
        logger.debug(f"Neighbors of {player}: left={left}, right={right}")
        return (left, right)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        lines = ["World:"]
        for player, role in self.assignments.items():
            team_marker = "👹" if role.is_evil() else "😇"
            lines.append(f"  {team_marker} {player}: {role.value}")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"World({len(self.assignments)} players)"


def create_world(assignments: Dict[str, Role]) -> World:
    """
    Factory function to create a validated World.
    
    Args:
        assignments: Dictionary mapping player names to roles
        
    Returns:
        Validated World instance
        
    Raises:
        ValueError: If world configuration is invalid
    """
    logger.info(f"Creating world with {len(assignments)} players")
    return World(assignments=assignments)
