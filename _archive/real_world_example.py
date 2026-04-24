#!/usr/bin/env python3
"""
Real-World Example: Using Knowledge System in Claude Code

This shows how you would actually use the system during a coding session.
"""

from claude_code_integration import init_knowledge_system

def example_session_1():
    """
    Session 1: You're building a new system with Claude Code
    """
    print("=" * 70)
    print("SESSION 1: Building the System")
    print("=" * 70)
    print()

    # Initialize knowledge system
    knowledge = init_knowledge_system()

    print("You: 'Create an authentication service'\n")
    print("Claude: *creates auth-service code*\n")

    # Track what was created
    knowledge.track_project_creation(
        project_name="auth-service",
        reason="Handle user authentication and session management",
        technologies=["Python", "FastAPI", "JWT", "PostgreSQL"]
    )

    print("\nYou: 'Now create an API gateway that uses the auth service'\n")
    print("Claude: *creates api-gateway code*\n")

    knowledge.track_project_creation(
        project_name="api-gateway",
        reason="Central routing and load balancing for all services",
        created_for="auth-service",
        technologies=["Node.js", "Express", "Nginx"]
    )
    knowledge.add_relationship("api-gateway", "uses", "auth-service")

    print("\nYou: 'The auth service is getting hammered. We need rate limiting.'\n")
    print("Claude: *creates rate-limiter service*\n")

    knowledge.track_project_creation(
        project_name="rate-limiter",
        reason="Prevent API abuse and brute-force attacks",
        created_for="auth-service",
        causal_chain=[
            "auth-service experiencing high load",
            "Brute-force login attempts detected in logs",
            "Security team recommended rate limiting",
            "Decision to create separate rate-limiter service for reusability"
        ],
        technologies=["Python", "Redis", "Token Bucket Algorithm"]
    )
    knowledge.add_relationship("auth-service", "uses", "rate-limiter")
    knowledge.add_relationship("api-gateway", "uses", "rate-limiter")

    print("\n✓ Session 1 complete - All knowledge saved to .claude/knowledge/")
    print(f"  Projects tracked: {len(knowledge.list_projects())}")
    print(f"  Facts stored: {knowledge.get_stats()['total_facts']}")


def example_session_2():
    """
    Session 2: Three weeks later, new Claude Code session
    """
    print("\n\n" + "=" * 70)
    print("SESSION 2: Three Weeks Later (New Session)")
    print("=" * 70)
    print()

    # Initialize - automatically loads existing knowledge
    knowledge = init_knowledge_system()

    print("You: 'Why do we have a rate-limiter service?'\n")
    print("Claude: *queries knowledge system*\n")

    # Get the answer
    answer = knowledge.why_does_exist("rate-limiter")
    print(answer)

    print("\n" + "-" * 70)
    print("\nYou: 'What services are we running?'\n")
    print("Claude: *lists projects*\n")

    projects = knowledge.list_projects()
    for proj in projects:
        print(f"  • {proj['name']}")
        print(f"    Reason: {proj['reason']}")
        if proj['created_for']:
            print(f"    Created for: {proj['created_for']}")
        print()

    print("✓ Session 2 complete - Knowledge retrieved without conversation history!")


def example_session_3():
    """
    Session 3: Adding more services
    """
    print("\n\n" + "=" * 70)
    print("SESSION 3: Expanding the System")
    print("=" * 70)
    print()

    knowledge = init_knowledge_system()

    print("You: 'Add a monitoring service'\n")
    print("Claude: *creates monitoring service*\n")

    knowledge.track_project_creation(
        project_name="monitoring-service",
        reason="Centralized logging and metrics collection",
        technologies=["Prometheus", "Grafana", "Loki"]
    )

    # Link to existing services
    for service in ["auth-service", "api-gateway", "rate-limiter"]:
        knowledge.add_relationship("monitoring-service", "monitors", service)

    print("\nYou: 'Show me the system architecture'\n")
    print("Claude: *visualizes knowledge graph*\n")

    print(knowledge.visualize())

    print("\n✓ Session 3 complete - System expanded!")


def example_query_patterns():
    """
    Common query patterns
    """
    print("\n\n" + "=" * 70)
    print("COMMON QUERY PATTERNS")
    print("=" * 70)
    print()

    knowledge = init_knowledge_system()

    # Pattern 1: Why questions
    print("1. Why does X exist?")
    print("-" * 70)
    print(knowledge.why_does_exist("rate-limiter"))

    # Pattern 2: What uses X?
    print("\n\n2. What uses rate-limiter?")
    print("-" * 70)
    context = knowledge.query_context("rate-limiter")
    related = context.get('related_projects', [])
    for rel in related:
        print(f"  • {rel['project']} (connection strength: {rel['strength']:.2f})")

    # Pattern 3: Full context
    print("\n\n3. Full context for auth-service")
    print("-" * 70)
    context = knowledge.query_context("auth-service")
    print(f"Reason: {context['origin']['reason']}")
    print(f"Technologies: {context['origin'].get('domain_concepts', [])}")
    print(f"Related projects: {[r['project'] for r in context.get('related_projects', [])]}")

    # Pattern 4: System overview
    print("\n\n4. System statistics")
    print("-" * 70)
    stats = knowledge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Run all examples"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║  REAL-WORLD EXAMPLE: Using Knowledge System in Claude Code      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # Run example sessions
    example_session_1()
    example_session_2()
    example_session_3()
    example_query_patterns()

    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✓ Session 1: Created 3 services, tracked relationships")
    print("✓ Session 2: Retrieved knowledge without conversation history")
    print("✓ Session 3: Expanded system, maintained connections")
    print("✓ Queries: Answered 'why' questions from stored knowledge")
    print()
    print("Key Achievement:")
    print("  The system knows why rate-limiter was created for auth-service,")
    print("  even weeks later in a new session with no conversation history.")
    print()
    print("All knowledge stored in: .claude/knowledge/")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
