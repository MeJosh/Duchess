"""Reasoning engine - world generation, constraints, and deduction."""

from .world_builder import WorldGenerator, generate_worlds, filter_worlds
from .constraints import (
    Constraint,
    WasherwomanConstraint,
    InvestigatorConstraint,
    EmpathConstraint,
    ScarletWomanConstraint,
    RoleConstraint,
    apply_constraints,
)
from .deduction import (
    prove_role,
    is_proven_evil,
    is_proven_good,
    calculate_role_probabilities,
    calculate_alignment_probabilities,
    find_proven_facts,
    get_possible_roles,
    count_worlds_where,
)

__all__ = [
    "WorldGenerator",
    "generate_worlds",
    "filter_worlds",
    "Constraint",
    "WasherwomanConstraint",
    "InvestigatorConstraint",
    "EmpathConstraint",
    "ScarletWomanConstraint",
    "RoleConstraint",
    "apply_constraints",
    "prove_role",
    "is_proven_evil",
    "is_proven_good",
    "calculate_role_probabilities",
    "calculate_alignment_probabilities",
    "find_proven_facts",
    "get_possible_roles",
    "count_worlds_where",
]
