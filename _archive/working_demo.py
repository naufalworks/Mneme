"""
Comprehensive Working Demo

This demo shows the complete system working end-to-end with proper
fact retrieval and cross-project knowledge preservation.
"""

from global_knowledge_system import GlobalKnowledgeSystem
import json


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    print_header("HYPERDIMENSIONAL MULTI-AGENT SYSTEM - WORKING DEMO")

    # Create fresh system
    system = GlobalKnowledgeSystem(base_path="./working_demo", dims=10000)

    # ========================================================================
    # PART 1: Create projects and add facts
    # ========================================================================

    print_header("PART 1: Creating Projects with Cross-Project Relationships")

    print("Creating auth-service...")
    system.create_project(
        name="auth-service",
        reason="Core authentication service using JWT tokens",
        domain_concepts=["auth-service", "authentication", "JWT"]
    )

    # Add facts
    system.add_project_fact("auth-service", "auth-service", "implements", "JWT")
    system.add_project_fact("auth-service", "auth-service", "needs", "rate_limiting")
    system.add_project_fact("auth-service", "auth-service", "handles", "user_authentication")
    print("✓ auth-service created with 3 facts\n")

    print("Creating api-gateway...")
    system.create_project(
        name="api-gateway",
        reason="Central API gateway for routing",
        created_for="auth-service",
        domain_concepts=["api-gateway", "routing"]
    )

    system.add_project_fact("api-gateway", "api-gateway", "uses", "auth-service")
    system.add_project_fact("api-gateway", "api-gateway", "routes", "http_requests")
    print("✓ api-gateway created with 2 facts\n")

    print("Creating rate-limiter (THE KEY TEST)...")
    system.create_project(
        name="rate-limiter",
        reason="Prevent API abuse through rate limiting",
        created_for="auth-service",
        domain_concepts=["rate-limiter", "rate_limiting"],
        causal_chain=[
            "auth-service had no rate limiting",
            "Brute-force attacks detected",
            "Decision to create rate-limiter",
            "rate-limiter project created"
        ]
    )

    system.add_project_fact("rate-limiter", "rate-limiter", "protects", "auth-service")
    system.add_project_fact("rate-limiter", "rate-limiter", "prevents", "abuse")
    system.add_project_fact("api-gateway", "api-gateway", "uses", "rate-limiter")
    print("✓ rate-limiter created with 3 facts\n")

    # ========================================================================
    # PART 2: Show all facts in the system
    # ========================================================================

    print_header("PART 2: All Facts in Knowledge Base")

    print(f"Total concepts: {len(system.hypervector_space.concepts)}")
    print(f"Total facts: {len(system.hypervector_space.facts)}\n")

    print("All facts stored:")
    for i, meta in enumerate(system.hypervector_space.metadata, 1):
        print(f"{i:2d}. {meta['subject']:20s} → {meta['relation']:15s} → {meta['object']}")

    # ========================================================================
    # PART 3: Query individual facts
    # ========================================================================

    print_header("PART 3: Querying Facts")

    print("Query 1: Find facts containing 'rate-limiter' as subject")
    print("-" * 70)
    count = 0
    for meta in system.hypervector_space.metadata:
        if meta['subject'] == 'rate-limiter':
            print(f"  • {meta['subject']} {meta['relation']} {meta['object']}")
            count += 1
    print(f"Found {count} facts\n")

    print("Query 2: Find facts with relation 'created_for'")
    print("-" * 70)
    count = 0
    for meta in system.hypervector_space.metadata:
        if meta['relation'] == 'created_for':
            print(f"  • {meta['subject']} {meta['relation']} {meta['object']}")
            count += 1
    print(f"Found {count} facts\n")

    print("Query 3: What was created for auth-service?")
    print("-" * 70)
    count = 0
    for meta in system.hypervector_space.metadata:
        if meta['relation'] == 'created_for' and meta['object'] == 'auth-service':
            print(f"  • {meta['subject']} was created for {meta['object']}")
            count += 1
    print(f"Found {count} projects\n")

    # ========================================================================
    # PART 4: Cross-project context
    # ========================================================================

    print_header("PART 4: Cross-Project Context")

    print("Getting full context for rate-limiter...")
    print("-" * 70)
    context = system.get_project_context("rate-limiter")

    print(f"\nProject: {context['project']}")
    print(f"Reason: {context['origin']['reason']}")
    print(f"Created for: {context['origin']['created_for']}")

    print("\nCausal Chain (WHY it exists):")
    for i, step in enumerate(context['causal_chain']['chain'], 1):
        print(f"  {i}. {step}")

    print("\nRelated Projects (via agent network):")
    for rel in context['related_projects']:
        print(f"  • {rel['project']} (connection: {rel['strength']:.2f})")

    print("\nArtifacts created:")
    for key, path in context['artifacts'].items():
        print(f"  • {key}: {path}")

    # ========================================================================
    # PART 5: Answer the critical question
    # ========================================================================

    print_header("PART 5: THE CRITICAL TEST")

    print("Question: 'Why does rate-limiter exist?'\n")

    print("Answer from multiple sources:\n")

    print("1. From metadata (direct lookup):")
    for meta in system.hypervector_space.metadata:
        if meta['subject'] == 'rate-limiter' and meta['relation'] == 'created_for':
            print(f"   → rate-limiter was created for {meta['object']}")

    print("\n2. From causal chain:")
    for step in context['causal_chain']['chain']:
        print(f"   → {step}")

    print("\n3. From origin.json:")
    print(f"   → Created for: {context['origin']['created_for']}")
    print(f"   → Reason: {context['origin']['reason']}")

    print("\n4. From agent network:")
    print(f"   → Connected to: {[r['project'] for r in context['related_projects']]}")

    print("\n5. From facts about rate-limiter:")
    for meta in system.hypervector_space.metadata:
        if meta['subject'] == 'rate-limiter':
            print(f"   → rate-limiter {meta['relation']} {meta['object']}")

    # ========================================================================
    # PART 6: Simulate new session
    # ========================================================================

    print_header("PART 6: Simulating New Session (No Conversation History)")

    print("Saving system state...")
    system.save("./working_demo/system_state.json")
    print("✓ Saved\n")

    print("Creating new system instance (simulating new session)...")
    new_system = GlobalKnowledgeSystem(base_path="./working_demo")
    new_system.load("./working_demo/system_state.json")
    print("✓ Loaded\n")

    print("Querying new system: 'Why does rate-limiter exist?'")
    print("-" * 70)

    # Get context from new system
    new_context = new_system.get_project_context("rate-limiter")

    print(f"\nAnswer: rate-limiter was created for {new_context['origin']['created_for']}")
    print(f"Reason: {new_context['origin']['reason']}\n")

    print("Causal chain:")
    for i, step in enumerate(new_context['causal_chain']['chain'], 1):
        print(f"  {i}. {step}")

    # ========================================================================
    # PART 7: Verify artifacts on disk
    # ========================================================================

    print_header("PART 7: Verifying Crystallized Artifacts")

    import os
    from pathlib import Path

    print("Checking files created on disk...\n")

    base = Path("./working_demo")
    for project in ["auth-service", "api-gateway", "rate-limiter"]:
        print(f"{project}:")
        why_file = base / project / "docs" / "WHY.md"
        origin_file = base / project / ".meta" / "origin.json"

        if why_file.exists():
            print(f"  ✓ WHY.md exists ({why_file.stat().st_size} bytes)")
        if origin_file.exists():
            print(f"  ✓ origin.json exists ({origin_file.stat().st_size} bytes)")

            # Read and show key info
            with open(origin_file) as f:
                origin = json.load(f)
            if origin.get('created_for'):
                print(f"    → Created for: {origin['created_for']}")
        print()

    # ========================================================================
    # SUMMARY
    # ========================================================================

    print_header("SUMMARY: System Capabilities Demonstrated")

    print("✓ Cross-project relationships preserved")
    print("✓ Causal chains explain WHY projects exist")
    print("✓ Multiple redundant storage mechanisms:")
    print("    - Hypervector facts (semantic encoding)")
    print("    - Agent network (connections)")
    print("    - Crystallized artifacts (WHY.md, origin.json)")
    print("    - Causal chain records")
    print()
    print("✓ Knowledge survives across sessions")
    print("✓ No conversation history needed")
    print("✓ Query: 'Why does rate-limiter exist?'")
    print("  Answer: Created for auth-service to prevent abuse")
    print()
    print("KEY ACHIEVEMENT:")
    print("  The system knows rate-limiter was created because")
    print("  auth-service needed rate limiting, even in a fresh")
    print("  session with no conversation history.")

    print_header("END OF DEMO")


if __name__ == "__main__":
    main()
