"""Command-line interface for running Duchess scenarios.

Usage:
    python -m duchess.simulation.run [scenario_name]
    
Examples:
    python -m duchess.simulation.run
    python -m duchess.simulation.run washerwoman
    python -m duchess.simulation.run --all
"""

import sys
from pathlib import Path
from typing import Optional
from duchess.simulation import ALL_SCENARIOS, ScenarioRunner
from duchess.utils.logger import logger


def list_scenarios():
    """Print available scenarios."""
    print("\n=== Available Scenarios ===\n")
    for i, scenario in enumerate(ALL_SCENARIOS, 1):
        print(f"{i}. {scenario.name}")
        print(f"   {scenario.description}")
        print(f"   Players: {len(scenario.players)}, Observations: {len(scenario.observations)}\n")


def run_scenario(scenario_name: Optional[str] = None, save_reports: bool = False):
    """Run a scenario or all scenarios.
    
    Args:
        scenario_name: Name (or partial name) of scenario to run, or None for all
        save_reports: Whether to save markdown reports to disk
    """
    # Find matching scenarios
    if scenario_name is None or scenario_name == "all":
        scenarios_to_run = ALL_SCENARIOS
    else:
        name_lower = scenario_name.lower()
        scenarios_to_run = [
            s for s in ALL_SCENARIOS
            if name_lower in s.name.lower()
        ]
        
        if not scenarios_to_run:
            print(f"❌ No scenario found matching '{scenario_name}'")
            list_scenarios()
            sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"  DUCHESS - Blood on the Clocktower Analysis Engine")
    print(f"{'='*70}\n")
    
    # Run each scenario
    for i, scenario in enumerate(scenarios_to_run, 1):
        print(f"\n{'─'*70}")
        print(f"Scenario {i}/{len(scenarios_to_run)}: {scenario.name}")
        print(f"{'─'*70}")
        print(f"Description: {scenario.description}")
        print(f"Agent: {scenario.agent_name} ({scenario.agent_role.value})")
        print(f"Players: {', '.join(scenario.players)}")
        print()
        
        # Create and run
        runner = ScenarioRunner(scenario)
        results = runner.run()
        
        # Display summary
        print(f"\n📊 Results:")
        print(f"  Initial worlds: {results['initial_worlds']}")
        print(f"  After {results['observations_count']} observation(s): {results['final_worlds']} worlds")
        print(f"  Reduction: {results['initial_worlds'] - results['final_worlds']} worlds eliminated")
        
        if results['proven_facts']:
            print(f"\n✓ Proven Facts ({len(results['proven_facts'])}):")
            for player, role in results['proven_facts'].items():
                print(f"    {player}: {role.value}")
        else:
            print(f"\n  No additional facts proven beyond self-knowledge")
        
        # Show some interesting probabilities
        print(f"\n📈 Sample Role Probabilities:")
        role_probs = results['role_probabilities']
        for player in list(scenario.players)[:3]:  # Show first 3 players
            if player in role_probs:
                probs = role_probs[player]
                # Find most likely roles
                sorted_roles = sorted(probs.items(), key=lambda x: x[1], reverse=True)
                top_roles = sorted_roles[:2]  # Top 2
                prob_str = ", ".join([f"{role.value}: {prob:.1%}" for role, prob in top_roles])
                print(f"    {player}: {prob_str}")
        
        # Save report if requested
        if save_reports:
            output_dir = Path("reports")
            output_dir.mkdir(exist_ok=True)
            
            filename = f"{scenario.name.lower().replace(' ', '_')}.md"
            filepath = output_dir / filename
            
            runner.generate_report(filepath=str(filepath))
            print(f"\n💾 Report saved: {filepath}")
    
    print(f"\n{'='*70}")
    print(f"  Analysis Complete")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Duchess BotC analysis scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run all scenarios
  %(prog)s --list              # List available scenarios
  %(prog)s washerwoman         # Run scenarios matching 'washerwoman'
  %(prog)s --all --save        # Run all and save reports
        """
    )
    
    parser.add_argument(
        "scenario",
        nargs="?",
        help="Scenario name (or partial match) to run. Omit to run all.",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available scenarios and exit",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all scenarios (same as omitting scenario name)",
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save markdown reports to reports/ directory",
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
        sys.exit(0)
    
    scenario_name = args.scenario
    if args.all:
        scenario_name = "all"
    
    try:
        run_scenario(scenario_name, save_reports=args.save)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception("Error running scenario")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
