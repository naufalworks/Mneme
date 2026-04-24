"""
Simple demo showing the knowledge system in action.
"""

from src.mneme import init_knowledge_system


def main():
    print("=" * 70)
    print("KNOWLEDGE SYSTEM DEMO")
    print("=" * 70)
    print()

    # Initialize
    knowledge = init_knowledge_system()

    # Track projects
    print("Creating projects...\n")

    knowledge.track_project_creation(
        project_name="auth-service",
        reason="Handle user authentication",
        technologies=["Python", "FastAPI", "JWT"]
    )

    knowledge.track_project_creation(
        project_name="rate-limiter",
        reason="Prevent API abuse",
        created_for="auth-service",
        causal_chain=[
            "auth-service experiencing high load",
            "Brute-force attacks detected",
            "Security team recommended rate limiting",
            "rate-limiter created"
        ],
        technologies=["Python", "Redis"]
    )

    # Add relationships
    knowledge.add_relationship("auth-service", "uses", "rate-limiter")

    # Query
    print("\n" + "=" * 70)
    print("QUERY: Why does rate-limiter exist?")
    print("=" * 70)
    print(knowledge.why_does_exist("rate-limiter"))

    # Stats
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    stats = knowledge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Demo complete!")


if __name__ == "__main__":
    main()
