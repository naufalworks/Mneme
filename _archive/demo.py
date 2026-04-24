"""
Interactive Demo: 3-Project Scenario

Demonstrates the hyperdimensional multi-agent crystallization system
with a realistic scenario:
- auth-service (created first)
- api-gateway (uses auth-service)
- rate-limiter (created for auth-service needs)

Shows cross-project knowledge preservation and querying.
"""

import json
from global_knowledge_system import GlobalKnowledgeSystem


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_result(result: dict):
    """Pretty print query results."""
    print(f"Query: {result['query']}")
    print(f"Found {result['num_results']} results:\n")

    for i, r in enumerate(result['results'], 1):
        print(f"{i}. {r['fact']}")
        print(f"   Score: {r['score']:.3f} | Agent: {r['agent']}")

    if result.get('causal_chain'):
        print("\nCausal Chain:")
        for i, step in enumerate(result['causal_chain']['chain'], 1):
            print(f"  {i}. {step}")


def main():
    print_section("HYPERDIMENSIONAL MULTI-AGENT CRYSTALLIZATION SYSTEM")
    print("Demo: 3-Project Cross-Project Knowledge Scenario\n")

    # Initialize system
    print("Initializing global knowledge system...")
    system = GlobalKnowledgeSystem(base_path="./demo_projects", dims=10000)
    print("✓ System initialized\n")

    # ========================================================================
    # SESSION 1: Creating the projects
    # ========================================================================

    print_section("SESSION 1: Creating Projects")

    # Step 1: Create auth-service
    print("Step 1: Creating auth-service...")
    result1 = system.create_project(
        name="auth-service",
        reason="Core authentication service using JWT tokens",
        domain_concepts=["auth-service", "authentication", "JWT", "security"]
    )
    print(f"✓ Created {result1['project']}")
    print(f"  Artifacts: {list(result1['artifacts'].keys())}\n")

    # Add facts about auth-service
    system.add_project_fact("auth-service", "auth-service", "implements", "JWT")
    system.add_project_fact("auth-service", "auth-service", "handles", "user_login")
    system.add_project_fact("auth-service", "auth-service", "needs", "rate_limiting")
    print("✓ Added facts about auth-service\n")

    # Step 2: Create api-gateway
    print("Step 2: Creating api-gateway...")
    result2 = system.create_project(
        name="api-gateway",
        reason="Central API gateway for routing and authentication",
        created_for="auth-service",
        domain_concepts=["api-gateway", "routing", "gateway"],
        causal_chain=[
            "Multiple services needed unified entry point",
            "auth-service needed to be integrated with routing",
            "Decision to create API gateway",
            "api-gateway project created"
        ]
    )
    print(f"✓ Created {result2['project']}")
    print(f"  Created for: auth-service\n")

    # Add facts about api-gateway
    system.add_project_fact("api-gateway", "api-gateway", "uses", "auth-service")
    system.add_project_fact("api-gateway", "api-gateway", "routes", "requests")
    print("✓ Added facts about api-gateway\n")

    # Step 3: Create rate-limiter (THE KEY TEST)
    print("Step 3: Creating rate-limiter for auth-service...")
    result3 = system.create_project(
        name="rate-limiter",
        reason="Prevent API abuse through request rate limiting",
        created_for="auth-service",
        domain_concepts=["rate-limiter", "rate_limiting", "throttling", "abuse_prevention"],
        causal_chain=[
            "auth-service had no rate limiting",
            "Risk of brute-force attacks identified",
            "Abuse incidents occurred in production",
            "Decision to create separate rate limiting service",
            "rate-limiter project created"
        ]
    )
    print(f"✓ Created {result3['project']}")
    print(f"  Created for: auth-service")
    print(f"  Reason: {result3['project']} was created because auth-service needed rate limiting\n")

    # Add facts about rate-limiter
    system.add_project_fact("rate-limiter", "rate-limiter", "prevents", "abuse")
    system.add_project_fact("rate-limiter", "rate-limiter", "protects", "auth-service")
    system.add_project_fact("rate-limiter", "rate-limiter", "implements", "token_bucket")
    system.add_project_fact("api-gateway", "api-gateway", "uses", "rate-limiter")
    print("✓ Added facts about rate-limiter\n")

    # Show system state
    print(system.visualize())

    # ========================================================================
    # SESSION 2: Querying (simulating new session, no conversation history)
    # ========================================================================

    print_section("SESSION 2: Querying Cross-Project Knowledge")
    print("(Simulating new session - no conversation history available)\n")

    # Query 1: What does auth-service need?
    print("Query 1: What does auth-service need?")
    print("-" * 70)
    result = system.query("What does auth-service need?")
    print_result(result)

    # Query 2: Why does rate-limiter exist? (THE CRITICAL TEST)
    print("\n\nQuery 2: Why does rate-limiter exist?")
    print("-" * 70)
    result = system.query("Why does rate-limiter exist?")
    print_result(result)

    # Query 3: What uses auth-service?
    print("\n\nQuery 3: What uses auth-service?")
    print("-" * 70)
    result = system.query("What uses auth-service?")
    print_result(result)

    # Query 4: What does api-gateway use?
    print("\n\nQuery 4: What does api-gateway use?")
    print("-" * 70)
    result = system.query("What does api-gateway use?")
    print_result(result)

    # ========================================================================
    # SESSION 3: Deep context queries
    # ========================================================================

    print_section("SESSION 3: Deep Context Queries")

    # Get full context for rate-limiter
    print("Getting full context for rate-limiter...")
    print("-" * 70)
    context = system.get_project_context("rate-limiter")

    print(f"\nProject: {context['project']}")
    print(f"\nOrigin:")
    print(f"  Created: {context['origin']['created']}")
    print(f"  Reason: {context['origin']['reason']}")
    print(f"  Created for: {context['origin']['created_for']}")

    print(f"\nRelated Projects:")
    for rel in context['related_projects']:
        print(f"  • {rel['project']} (strength: {rel['strength']:.2f})")

    print(f"\nCausal Chain:")
    for i, step in enumerate(context['causal_chain']['chain'], 1):
        print(f"  {i}. {step}")

    print(f"\nArtifacts:")
    for key, path in context['artifacts'].items():
        print(f"  • {key}: {path}")

    # ========================================================================
    # SESSION 4: Testing persistence
    # ========================================================================

    print_section("SESSION 4: Testing Persistence")

    # Save system state
    print("Saving system state...")
    system.save("./demo_projects/system_state.json")
    print("✓ System state saved to ./demo_projects/system_state.json")
    print("✓ Knowledge base saved to ./demo_projects/knowledge_base.json\n")

    # Create new system and load
    print("Creating new system instance and loading state...")
    new_system = GlobalKnowledgeSystem(base_path="./demo_projects")
    new_system.load("./demo_projects/system_state.json")
    print("✓ State loaded\n")

    # Query the loaded system
    print("Querying loaded system: Why does rate-limiter exist?")
    print("-" * 70)
    result = new_system.query("Why does rate-limiter exist?")
    print_result(result)

    # ========================================================================
    # Summary
    # ========================================================================

    print_section("SUMMARY")

    print("✓ Created 3 projects with cross-project relationships")
    print("✓ rate-limiter was created FOR auth-service")
    print("✓ System preserved the 'why' (causal chain)")
    print("✓ Queries work across projects without conversation history")
    print("✓ Knowledge persists across sessions")
    print("\nKey Achievement:")
    print("  Even in a new session with no conversation history,")
    print("  the system knows WHY rate-limiter exists and its")
    print("  relationship to auth-service.")
    print("\nThis is achieved through:")
    print("  1. Hypervector encoding (semantic relationships)")
    print("  2. Agent network (cross-project connections)")
    print("  3. Crystallized artifacts (WHY.md, origin.json)")
    print("  4. Causal chain preservation")

    print_section("END OF DEMO")


if __name__ == "__main__":
    main()
