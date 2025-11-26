"""Example usage of the ReportGenerator for visualizing agent deduction progress."""

from duchess.engine.game_state import World, Role
from duchess.reasoning.world_builder import generate_all_worlds
from duchess.reasoning.constraints import apply_washerwoman_constraint
from duchess.reporting import ReportGenerator


def main():
    """Generate an example report showing agent deduction process."""
    
    # Ground truth
    true_world = World({
        "Alice": Role.WASHERWOMAN,
        "Bob": Role.INVESTIGATOR,
        "Charlie": Role.EMPATH,
        "Diana": Role.IMP,
        "Eve": Role.SCARLET_WOMAN,
    })
    
    # Initialize reporter
    reporter = ReportGenerator(
        true_world=true_world,
        agent_player="Alice",
        agent_role=Role.WASHERWOMAN,
    )
    
    # Step 1: Initial belief (all possible worlds)
    initial_worlds = generate_all_worlds(num_players=5)
    print(f"Initial worlds: {len(initial_worlds)}")
    
    # Step 2: Apply Washerwoman information
    # Alice learned one of Bob/Charlie is Investigator
    washer_worlds = apply_washerwoman_constraint(
        initial_worlds,
        players=["Bob", "Charlie"],
        role=Role.INVESTIGATOR,
    )
    
    reporter.add_observation(
        description="Received Washerwoman information: one of Bob/Charlie is Investigator",
        constraint_type="washerwoman",
        worlds_before=initial_worlds,
        worlds_after=washer_worlds,
        data={"players": ["Bob", "Charlie"], "role": Role.INVESTIGATOR},
    )
    
    # Set final belief state
    reporter.set_final_belief_state(washer_worlds)
    
    # Generate and save report
    output_path = "logs/example_report.md"
    reporter.save(output_path)
    print(f"\nReport saved to: {output_path}")
    
    # Also print to console
    report = reporter.generate()
    print("\n" + "="*60)
    print(report)
    print("="*60)


if __name__ == "__main__":
    main()
