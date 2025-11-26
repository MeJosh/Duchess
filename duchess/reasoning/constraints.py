"""
Constraint system for filtering possible worlds based on character information.

Each constraint represents a piece of information (e.g., Washerwoman sees Bob/Charlie
as Investigator) and filters out worlds that don't match this information.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Set
from duchess.engine.game_state import World, Role
from duchess.utils.logger import setup_logger

logger = setup_logger(__name__)


class Constraint(ABC):
    """
    Abstract base class for all constraints.
    
    A constraint filters a list of worlds, keeping only those that satisfy
    the constraint's condition.
    """
    
    @abstractmethod
    def apply(self, worlds: List[World]) -> List[World]:
        """
        Filter worlds, keeping only those that satisfy this constraint.
        
        Args:
            worlds: List of possible worlds to filter
            
        Returns:
            Filtered list of worlds that satisfy the constraint
        """
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return human-readable description of this constraint."""
        pass


@dataclass(frozen=True)
class WasherwomanConstraint(Constraint):
    """
    Washerwoman sees two players, one of whom has a specific Townsfolk role.
    
    Filters to worlds where at least one of the two players has the specified role.
    """
    player1: int
    player2: int
    role: Role
    
    def apply(self, worlds: List[World]) -> List[World]:
        """Keep worlds where player1 OR player2 has the specified role."""
        logger.debug(
            f"Applying Washerwoman constraint: player {self.player1} or "
            f"{self.player2} is {self.role.name}"
        )
        
        filtered = [
            world for world in worlds
            if world.get_role(self.player1) == self.role
            or world.get_role(self.player2) == self.role
        ]
        
        logger.info(
            f"Washerwoman constraint: {len(worlds)} worlds → {len(filtered)} worlds"
        )
        return filtered
    
    def description(self) -> str:
        return (
            f"Washerwoman sees players {self.player1} and {self.player2}, "
            f"one is {self.role.name}"
        )


@dataclass(frozen=True)
class InvestigatorConstraint(Constraint):
    """
    Investigator sees two players, one of whom has a specific Minion role.
    
    Filters to worlds where at least one of the two players has the specified role.
    """
    player1: int
    player2: int
    role: Role
    
    def apply(self, worlds: List[World]) -> List[World]:
        """Keep worlds where player1 OR player2 has the specified role."""
        logger.debug(
            f"Applying Investigator constraint: player {self.player1} or "
            f"{self.player2} is {self.role.name}"
        )
        
        filtered = [
            world for world in worlds
            if world.get_role(self.player1) == self.role
            or world.get_role(self.player2) == self.role
        ]
        
        logger.info(
            f"Investigator constraint: {len(worlds)} worlds → {len(filtered)} worlds"
        )
        return filtered
    
    def description(self) -> str:
        return (
            f"Investigator sees players {self.player1} and {self.player2}, "
            f"one is {self.role.name}"
        )


@dataclass(frozen=True)
class EmpathConstraint(Constraint):
    """
    Empath sees the number of evil neighbors (0, 1, or 2).
    
    Filters to worlds where the Empath's neighbors have exactly the
    specified count of evil players.
    """
    empath_player: int
    evil_count: int
    
    def apply(self, worlds: List[World]) -> List[World]:
        """Keep worlds where empath has exactly evil_count evil neighbors."""
        logger.debug(
            f"Applying Empath constraint: player {self.empath_player} "
            f"sees {self.evil_count} evil neighbors"
        )
        
        filtered = []
        for world in worlds:
            neighbors = world.get_neighbors(self.empath_player)
            actual_evil_count = sum(
                1 for n in neighbors
                if world.get_role(n).is_evil()
            )
            
            if actual_evil_count == self.evil_count:
                filtered.append(world)
        
        logger.info(
            f"Empath constraint: {len(worlds)} worlds → {len(filtered)} worlds"
        )
        return filtered
    
    def description(self) -> str:
        return (
            f"Empath (player {self.empath_player}) sees "
            f"{self.evil_count} evil neighbor(s)"
        )


@dataclass(frozen=True)
class ScarletWomanConstraint(Constraint):
    """
    Scarlet Woman learns if she is in play and who the Imp is.
    
    This constraint verifies that a player claiming to be Scarlet Woman
    correctly identifies the Imp.
    """
    scarlet_woman_player: int
    imp_player: int
    
    def apply(self, worlds: List[World]) -> List[World]:
        """Keep worlds where scarlet_woman_player is SW and imp_player is Imp."""
        logger.debug(
            f"Applying Scarlet Woman constraint: player {self.scarlet_woman_player} "
            f"is SW and sees player {self.imp_player} as Imp"
        )
        
        filtered = [
            world for world in worlds
            if (world.get_role(self.scarlet_woman_player) == Role.SCARLET_WOMAN
                and world.get_role(self.imp_player) == Role.IMP)
        ]
        
        logger.info(
            f"Scarlet Woman constraint: {len(worlds)} worlds → {len(filtered)} worlds"
        )
        return filtered
    
    def description(self) -> str:
        return (
            f"Scarlet Woman (player {self.scarlet_woman_player}) "
            f"sees player {self.imp_player} as Imp"
        )


@dataclass(frozen=True)
class RoleConstraint(Constraint):
    """
    Simple constraint: a specific player has a specific role.
    
    Useful for representing proven facts or claims.
    """
    player: int
    role: Role
    
    def apply(self, worlds: List[World]) -> List[World]:
        """Keep worlds where player has the specified role."""
        logger.debug(
            f"Applying Role constraint: player {self.player} is {self.role.name}"
        )
        
        filtered = [
            world for world in worlds
            if world.get_role(self.player) == self.role
        ]
        
        logger.info(
            f"Role constraint: {len(worlds)} worlds → {len(filtered)} worlds"
        )
        return filtered
    
    def description(self) -> str:
        return f"Player {self.player} is {self.role.name}"


def apply_constraints(worlds: List[World], constraints: List[Constraint]) -> List[World]:
    """
    Apply multiple constraints sequentially to a list of worlds.
    
    Args:
        worlds: Initial list of possible worlds
        constraints: List of constraints to apply in order
        
    Returns:
        List of worlds that satisfy all constraints
    """
    logger.info(f"Applying {len(constraints)} constraints to {len(worlds)} worlds")
    
    result = worlds
    for i, constraint in enumerate(constraints):
        logger.debug(f"Constraint {i+1}/{len(constraints)}: {constraint.description()}")
        result = constraint.apply(result)
        
        if not result:
            logger.warning(f"No worlds remain after constraint {i+1}")
            break
    
    logger.info(f"Final result: {len(result)} worlds remain after all constraints")
    return result
