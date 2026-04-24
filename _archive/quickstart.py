#!/usr/bin/env python3
"""
Quick Start Guide

Run this to see the system in action immediately.
"""

import subprocess
import sys


def main():
    print("=" * 70)
    print("HYPERDIMENSIONAL MULTI-AGENT SYSTEM - QUICK START")
    print("=" * 70)
    print()

    print("This system solves the infinite context problem for LLMs.")
    print()
    print("Key features:")
    print("  ✓ Cross-project knowledge preservation")
    print("  ✓ Causal chains (WHY things exist)")
    print("  ✓ No context pruning")
    print("  ✓ Works without conversation history")
    print()

    print("=" * 70)
    print("RUNNING DEMO")
    print("=" * 70)
    print()

    # Run the working demo
    result = subprocess.run([sys.executable, "working_demo.py"],
                          capture_output=False,
                          text=True)

    if result.returncode == 0:
        print()
        print("=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("What just happened:")
        print("  1. Created 3 projects (auth-service, api-gateway, rate-limiter)")
        print("  2. rate-limiter was created FOR auth-service")
        print("  3. System preserved the 'why' across sessions")
        print("  4. Queried in new session without conversation history")
        print("  5. Successfully retrieved cross-project knowledge")
        print()
        print("Check the generated files:")
        print("  - working_demo/rate-limiter/docs/WHY.md")
        print("  - working_demo/rate-limiter/.meta/origin.json")
        print()
        print("Next steps:")
        print("  - Read README.md for full documentation")
        print("  - Read SYSTEM_OVERVIEW.md for technical details")
        print("  - Explore the code in hypervector.py, neuromorphic_agent.py")
        print("  - Try creating your own projects!")
        print()
    else:
        print("Demo failed. Check the error above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
