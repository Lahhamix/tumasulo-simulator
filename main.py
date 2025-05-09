"""Main entry point for the Tomasulo's algorithm simulator."""

import argparse
import os
import sys
from simulator import Simulator

def main():
    """Main entry point for the simulator."""
    parser = argparse.ArgumentParser(description='Tomasulo Algorithm Simulator')
    
    # Load a manual trace file
    parser.add_argument('--trace', type=str, help='Path to a trace file')

    # Optional: generate a random trace
    parser.add_argument('--generate', action='store_true', help='Generate a random trace file')
    parser.add_argument('--output', type=str, default='output_trace.txt', help='Path to save the generated trace')
    parser.add_argument('--num', type=int, default=100, help='Number of instructions to generate')
    parser.add_argument('--seed', type=int, help='Seed for random generation')

    # Simulation control
    parser.add_argument('--step', action='store_true', help='Run simulation step-by-step')
    parser.add_argument('--verbose', action='store_true', help='Print internal state each cycle')
    
    args = parser.parse_args()

    # Handle trace generation
    if args.generate:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"[INFO] Generated random trace at {args.output}")

        # Use the generated trace as input if no manual file is provided
        if not args.trace:
            args.trace = args.output

    # Check that a trace file is provided
    if not args.trace:
        print("[ERROR] No trace file provided. Use --trace or --generate.")
        return 1

    if not os.path.exists(args.trace):
        print(f"[ERROR] Trace file '{args.trace}' not found.")
        return 1

    simulator = Simulator()

    try:
        simulator.load_trace(args.trace)
    except Exception as e:
        print(f"[ERROR] Failed to load trace: {e}")
        return 1

    print(f"[INFO] Loaded {len(simulator.instructions)} instructions from {args.trace}")

    # Run simulation
    if args.step:
        while True:
            continue_sim, state = simulator.run_step()
            print(f"\n[Cycle {state['cycle']}] PC: {state['pc']}")

            if args.verbose:
                print("Registers:", state['registers'])
                print("Register Status:", state['register_status'])
                print("Busy Reservation Stations:")
                for rs in state['reservation_stations']:
                    print(f"  {rs['name']}: op={rs['op']}, dest={rs['dest']}, "
                          f"vj={rs['vj']}, vk={rs['vk']}, qj={rs['qj']}, qk={rs['qk']}, "
                          f"executing={rs['executing']}, cycles_left={rs['cycles_left']}")
                if state['cdb']['busy']:
                    print(f"CDB: {state['cdb']['name']} -> {state['cdb']['value']}")

            if not continue_sim:
                break
            input("Press Enter to continue...")

        print("\n[INFO] Simulation complete!")
        print(simulator.metrics.report())
    else:
        print("\n[INFO] Running simulation to completion...")
        report = simulator.run()
        print(report)

    return 0

if __name__ == "__main__":
    sys.exit(main())
