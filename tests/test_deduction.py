"""Tests for deduction engine - symbolic and probabilistic reasoning."""

import pytest
from duchess.engine.game_state import World, Role
from duchess.reasoning.deduction import (
    prove_role,
    is_proven_evil,
    is_proven_good,
    calculate_role_probabilities,
    calculate_alignment_probabilities,
    find_proven_facts,
    get_possible_roles,
    count_worlds_where,
)


def make_world(assignments):
    """Helper to create test worlds without validation."""
    return World(assignments, skip_validation=True)


class TestProveRole:
    """Test symbolic deduction of proven roles."""

    def test_single_world_all_roles_proven(self):
        """With one world, all roles are proven."""
        world = make_world(
            {
                0: Role.WASHERWOMAN,
                1: Role.INVESTIGATOR,
                2: Role.EMPATH,
                3: Role.IMP,
                4: Role.SCARLET_WOMAN,
            }
        )

        assert prove_role([world], 0) == Role.WASHERWOMAN
        assert prove_role([world], 1) == Role.INVESTIGATOR
        assert prove_role([world], 2) == Role.EMPATH
        assert prove_role([world], 3) == Role.IMP
        assert prove_role([world], 4) == Role.SCARLET_WOMAN

    def test_no_worlds_returns_none(self):
        """Empty world list means nothing proven."""
        assert prove_role([], 0) is None

    def test_conflicting_roles_returns_none(self):
        """When worlds disagree on role, nothing proven."""
        world1 = make_world({0: Role.WASHERWOMAN, 1: Role.IMP})
        world2 = make_world({0: Role.INVESTIGATOR, 1: Role.IMP})

        # Player 0 has different roles across worlds
        assert prove_role([world1, world2], 0) is None

        # Player 1 has same role in all worlds
        assert prove_role([world1, world2], 1) == Role.IMP

    def test_string_player_ids(self):
        """Test with string player identifiers."""
        world1 = make_world({"Alice": Role.EMPATH, "Bob": Role.IMP})
        world2 = make_world({"Alice": Role.EMPATH, "Bob": Role.IMP})

        assert prove_role([world1, world2], "Alice") == Role.EMPATH
        assert prove_role([world1, world2], "Bob") == Role.IMP


class TestProvenAlignment:
    """Test symbolic deduction of alignment (good/evil)."""

    def test_proven_evil_single_world(self):
        """With one world, evil roles are proven evil."""
        world = World(
            {
                0: Role.WASHERWOMAN,
                1: Role.IMP,
                2: Role.SCARLET_WOMAN,
            }
        )

        assert not is_proven_evil([world], 0)
        assert is_proven_evil([world], 1)
        assert is_proven_evil([world], 2)

    def test_proven_good_single_world(self):
        """With one world, good roles are proven good."""
        world = World(
            {
                0: Role.WASHERWOMAN,
                1: Role.IMP,
                2: Role.SCARLET_WOMAN,
            }
        )

        assert is_proven_good([world], 0)
        assert not is_proven_good([world], 1)
        assert not is_proven_good([world], 2)

    def test_conflicting_alignments_not_proven(self):
        """When player could be good or evil, alignment not proven."""
        # Player 0 is Washerwoman in world1, Imp in world2
        world1 = make_world({0: Role.WASHERWOMAN, 1: Role.IMP})
        world2 = make_world({0: Role.IMP, 1: Role.WASHERWOMAN})

        assert not is_proven_evil([world1, world2], 0)
        assert not is_proven_good([world1, world2], 0)

    def test_same_alignment_different_roles_proven(self):
        """Player with different good roles is still proven good."""
        world1 = make_world({0: Role.WASHERWOMAN, 1: Role.IMP})
        world2 = make_world({0: Role.INVESTIGATOR, 1: Role.IMP})

        # Player 0 is good in both worlds (different roles)
        assert is_proven_good([world1, world2], 0)
        assert not is_proven_evil([world1, world2], 0)

        # Player 1 is evil in both worlds (same role)
        assert is_proven_evil([world1, world2], 1)
        assert not is_proven_good([world1, world2], 1)


class TestRoleProbabilities:
    """Test probabilistic reasoning for role distributions."""

    def test_single_world_certainty(self):
        """With one world, all probabilities are 1.0."""
        world = World(
            {
                0: Role.WASHERWOMAN,
                1: Role.IMP,
            }
        )

        probs = calculate_role_probabilities([world], 0)
        assert probs[Role.WASHERWOMAN] == 1.0
        assert len(probs) == 1

    def test_equal_probability_distribution(self):
        """Test 50/50 split between two roles."""
        world1 = make_world({0: Role.WASHERWOMAN, 1: Role.IMP})
        world2 = make_world({0: Role.INVESTIGATOR, 1: Role.IMP})

        probs = calculate_role_probabilities([world1, world2], 0)
        assert probs[Role.WASHERWOMAN] == 0.5
        assert probs[Role.INVESTIGATOR] == 0.5
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_unequal_probability_distribution(self):
        """Test non-uniform distribution."""
        world1 = make_world({0: Role.WASHERWOMAN})
        world2 = make_world({0: Role.WASHERWOMAN})
        world3 = make_world({0: Role.INVESTIGATOR})

        probs = calculate_role_probabilities([world1, world2, world3], 0)
        assert probs[Role.WASHERWOMAN] == pytest.approx(2 / 3)
        assert probs[Role.INVESTIGATOR] == pytest.approx(1 / 3)
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_empty_worlds_returns_empty(self):
        """No worlds means no probability distribution."""
        probs = calculate_role_probabilities([], 0)
        assert probs == {}

    def test_all_roles_present(self):
        """Test distribution across all 5 roles."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
            make_world({0: Role.EMPATH}),
            make_world({0: Role.IMP}),
            make_world({0: Role.SCARLET_WOMAN}),
        ]

        probs = calculate_role_probabilities(worlds, 0)
        assert len(probs) == 5
        assert all(prob == 0.2 for prob in probs.values())
        assert sum(probs.values()) == pytest.approx(1.0)


class TestAlignmentProbabilities:
    """Test probabilistic reasoning for good/evil probabilities."""

    def test_certain_good(self):
        """Player is good in all worlds."""
        world1 = make_world({0: Role.WASHERWOMAN})
        world2 = make_world({0: Role.INVESTIGATOR})

        good_prob, evil_prob = calculate_alignment_probabilities([world1, world2], 0)
        assert good_prob == 1.0
        assert evil_prob == 0.0

    def test_certain_evil(self):
        """Player is evil in all worlds."""
        world1 = make_world({0: Role.IMP})
        world2 = make_world({0: Role.SCARLET_WOMAN})

        good_prob, evil_prob = calculate_alignment_probabilities([world1, world2], 0)
        assert good_prob == 0.0
        assert evil_prob == 1.0

    def test_fifty_fifty_split(self):
        """Equal probability of good and evil."""
        world1 = make_world({0: Role.WASHERWOMAN})
        world2 = make_world({0: Role.IMP})

        good_prob, evil_prob = calculate_alignment_probabilities([world1, world2], 0)
        assert good_prob == 0.5
        assert evil_prob == 0.5

    def test_unequal_split(self):
        """75% good, 25% evil."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
            make_world({0: Role.EMPATH}),
            make_world({0: Role.IMP}),
        ]

        good_prob, evil_prob = calculate_alignment_probabilities(worlds, 0)
        assert good_prob == 0.75
        assert evil_prob == 0.25

    def test_empty_worlds(self):
        """No worlds returns (0.0, 0.0)."""
        good_prob, evil_prob = calculate_alignment_probabilities([], 0)
        assert good_prob == 0.0
        assert evil_prob == 0.0


class TestFindProvenFacts:
    """Test finding all proven role assignments."""

    def test_all_players_proven(self):
        """Single world proves all player roles."""
        world = World(
            {
                0: Role.WASHERWOMAN,
                1: Role.INVESTIGATOR,
                2: Role.IMP,
            }
        )

        facts = find_proven_facts([world])
        assert facts == {
            0: Role.WASHERWOMAN,
            1: Role.INVESTIGATOR,
            2: Role.IMP,
        }

    def test_partial_proven_facts(self):
        """Some players proven, others uncertain."""
        world1 = World(
            {
                0: Role.WASHERWOMAN,
                1: Role.IMP,
                2: Role.EMPATH,
            }
        )
        world2 = World(
            {
                0: Role.INVESTIGATOR,  # Different from world1
                1: Role.IMP,  # Same as world1
                2: Role.EMPATH,  # Same as world1
            }
        )

        facts = find_proven_facts([world1, world2])
        assert facts == {
            1: Role.IMP,
            2: Role.EMPATH,
        }
        assert 0 not in facts  # Player 0 has conflicting roles

    def test_no_proven_facts(self):
        """All players have conflicting assignments."""
        world1 = make_world({0: Role.WASHERWOMAN, 1: Role.IMP})
        world2 = make_world({0: Role.IMP, 1: Role.WASHERWOMAN})

        facts = find_proven_facts([world1, world2])
        assert facts == {}

    def test_empty_worlds(self):
        """No worlds returns empty dict."""
        facts = find_proven_facts([])
        assert facts == {}

    def test_string_player_ids(self):
        """Test with string player identifiers."""
        world = World(
            {
                "Alice": Role.WASHERWOMAN,
                "Bob": Role.IMP,
                "Charlie": Role.EMPATH,
            }
        )

        facts = find_proven_facts([world])
        assert facts == {
            "Alice": Role.WASHERWOMAN,
            "Bob": Role.IMP,
            "Charlie": Role.EMPATH,
        }


class TestGetPossibleRoles:
    """Test finding all possible roles for a player."""

    def test_single_world_single_role(self):
        """One world means one possible role."""
        world = make_world({0: Role.WASHERWOMAN})

        possible = get_possible_roles([world], 0)
        assert possible == {Role.WASHERWOMAN}

    def test_multiple_possible_roles(self):
        """Player has different roles across worlds."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
            make_world({0: Role.IMP}),
        ]

        possible = get_possible_roles(worlds, 0)
        assert possible == {Role.WASHERWOMAN, Role.INVESTIGATOR, Role.IMP}

    def test_all_five_roles_possible(self):
        """Player could be any of the 5 roles."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
            make_world({0: Role.EMPATH}),
            make_world({0: Role.IMP}),
            make_world({0: Role.SCARLET_WOMAN}),
        ]

        possible = get_possible_roles(worlds, 0)
        assert possible == {
            Role.WASHERWOMAN,
            Role.INVESTIGATOR,
            Role.EMPATH,
            Role.IMP,
            Role.SCARLET_WOMAN,
        }

    def test_empty_worlds(self):
        """No worlds returns empty set."""
        possible = get_possible_roles([], 0)
        assert possible == set()

    def test_duplicate_roles_across_worlds(self):
        """Same role in multiple worlds counted once."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.WASHERWOMAN}),
        ]

        possible = get_possible_roles(worlds, 0)
        assert possible == {Role.WASHERWOMAN}


class TestCountWorldsWhere:
    """Test counting worlds matching a predicate."""

    def test_count_all_worlds(self):
        """Predicate true for all worlds."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
        ]

        count = count_worlds_where(worlds, lambda w: True)
        assert count == 2

    def test_count_no_worlds(self):
        """Predicate false for all worlds."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
        ]

        count = count_worlds_where(worlds, lambda w: False)
        assert count == 0

    def test_count_by_role(self):
        """Count worlds where player has specific role."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.INVESTIGATOR}),
            make_world({0: Role.WASHERWOMAN}),
        ]

        count = count_worlds_where(
            worlds, lambda w: w.get_role(0) == Role.WASHERWOMAN
        )
        assert count == 2

    def test_count_by_alignment(self):
        """Count worlds where player is evil."""
        worlds = [
            make_world({0: Role.WASHERWOMAN}),
            make_world({0: Role.IMP}),
            make_world({0: Role.INVESTIGATOR}),
        ]

        count = count_worlds_where(worlds, lambda w: w.get_role(0).is_evil())
        assert count == 1

    def test_complex_predicate(self):
        """Test with multi-condition predicate."""
        worlds = [
            make_world({0: Role.WASHERWOMAN, 1: Role.IMP}),
            make_world({0: Role.INVESTIGATOR, 1: Role.SCARLET_WOMAN}),
            make_world({0: Role.IMP, 1: Role.WASHERWOMAN}),
        ]

        # Count worlds where player 0 is good AND player 1 is evil
        count = count_worlds_where(
            worlds,
            lambda w: w.get_role(0).is_good() and w.get_role(1).is_evil(),
        )
        assert count == 2

    def test_empty_worlds(self):
        """Empty world list returns 0."""
        count = count_worlds_where([], lambda w: True)
        assert count == 0


class TestIntegration:
    """Integration tests combining multiple deduction functions."""

    def test_scenario_with_proven_and_uncertain(self):
        """Realistic scenario: some facts proven, others probabilistic."""
        # 4 worlds where player 0 and 1 are fixed, player 2 varies
        worlds = [
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.IMP,
                    2: Role.INVESTIGATOR,
                }
            ),
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.IMP,
                    2: Role.EMPATH,
                }
            ),
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.IMP,
                    2: Role.INVESTIGATOR,
                }
            ),
            World(
                {
                    0: Role.WASHERWOMAN,
                    1: Role.IMP,
                    2: Role.INVESTIGATOR,
                }
            ),
        ]

        # Player 0 and 1 have proven roles
        assert prove_role(worlds, 0) == Role.WASHERWOMAN
        assert prove_role(worlds, 1) == Role.IMP
        assert prove_role(worlds, 2) is None  # Not proven

        # Player 0 proven good, player 1 proven evil
        assert is_proven_good(worlds, 0)
        assert is_proven_evil(worlds, 1)

        # Player 2 probabilities: 75% Investigator, 25% Empath
        probs = calculate_role_probabilities(worlds, 2)
        assert probs[Role.INVESTIGATOR] == 0.75
        assert probs[Role.EMPATH] == 0.25

        # Proven facts only include player 0 and 1
        facts = find_proven_facts(worlds)
        assert facts == {0: Role.WASHERWOMAN, 1: Role.IMP}

    def test_deduction_chain_narrows_uncertainty(self):
        """As we apply constraints, uncertainty decreases."""
        # Start with 3 worlds
        worlds = [
            make_world({0: Role.WASHERWOMAN, 1: Role.IMP}),
            make_world({0: Role.INVESTIGATOR, 1: Role.IMP}),
            make_world({0: Role.EMPATH, 1: Role.IMP}),
        ]

        # Initially: player 0 has 3 possible roles, player 1 proven
        assert len(get_possible_roles(worlds, 0)) == 3
        assert prove_role(worlds, 1) == Role.IMP

        # Calculate probabilities for player 0
        probs_before = calculate_role_probabilities(worlds, 0)
        assert len(probs_before) == 3

        # "Apply constraint" by filtering to 1 world
        filtered_worlds = [worlds[0]]

        # Now player 0 is proven
        assert prove_role(filtered_worlds, 0) == Role.WASHERWOMAN
        assert len(get_possible_roles(filtered_worlds, 0)) == 1

        probs_after = calculate_role_probabilities(filtered_worlds, 0)
        assert probs_after[Role.WASHERWOMAN] == 1.0
