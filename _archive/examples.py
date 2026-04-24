"""
Example: Using the System for Your Own Projects

This shows how to use the system for real-world scenarios.
"""

from global_knowledge_system import GlobalKnowledgeSystem


def example_1_simple_project():
    """Create a single project."""
    print("Example 1: Simple Project Creation")
    print("-" * 70)

    system = GlobalKnowledgeSystem(base_path="./examples/simple")

    system.create_project(
        name="my-app",
        reason="Main application for user management"
    )

    system.add_project_fact("my-app", "my-app", "uses", "PostgreSQL")
    system.add_project_fact("my-app", "my-app", "implements", "REST_API")

    print("✓ Created my-app")
    print(system.visualize())


def example_2_related_projects():
    """Create projects with relationships."""
    print("\nExample 2: Related Projects")
    print("-" * 70)

    system = GlobalKnowledgeSystem(base_path="./examples/related")

    # Create main service
    system.create_project(
        name="user-service",
        reason="Manages user accounts and profiles"
    )

    # Create authentication service for user-service
    system.create_project(
        name="auth-service",
        reason="Handles authentication and authorization",
        created_for="user-service",
        causal_chain=[
            "user-service needed authentication",
            "Security requirements identified",
            "Decision to separate auth concerns",
            "auth-service created"
        ]
    )

    # Add facts
    system.add_project_fact("user-service", "user-service", "uses", "auth-service")
    system.add_project_fact("auth-service", "auth-service", "protects", "user-service")

    print("✓ Created user-service and auth-service")

    # Query the relationship
    context = system.get_project_context("auth-service")
    print(f"\nauth-service was created for: {context['origin']['created_for']}")
    print("\nCausal chain:")
    for step in context['causal_chain']['chain']:
        print(f"  - {step}")


def example_3_complex_system():
    """Create a complex multi-project system."""
    print("\nExample 3: Complex Multi-Project System")
    print("-" * 70)

    system = GlobalKnowledgeSystem(base_path="./examples/complex")

    # Core service
    system.create_project(
        name="api-core",
        reason="Core API service"
    )

    # Database layer
    system.create_project(
        name="database-layer",
        reason="Database abstraction and ORM",
        created_for="api-core"
    )

    # Caching layer
    system.create_project(
        name="cache-service",
        reason="Redis-based caching for performance",
        created_for="api-core",
        causal_chain=[
            "api-core had slow response times",
            "Profiling showed database bottleneck",
            "Decision to add caching layer",
            "cache-service created"
        ]
    )

    # Monitoring
    system.create_project(
        name="monitoring",
        reason="Observability and alerting",
        created_for="api-core"
    )

    # Add relationships
    system.add_project_fact("api-core", "api-core", "uses", "database-layer")
    system.add_project_fact("api-core", "api-core", "uses", "cache-service")
    system.add_project_fact("monitoring", "monitoring", "observes", "api-core")
    system.add_project_fact("cache-service", "cache-service", "improves", "api-core")

    print("✓ Created 4 interconnected projects")
    print(system.visualize())

    # Save for later
    system.save("./examples/complex/system_state.json")
    print("\n✓ System state saved")


def example_4_query_later():
    """Load and query a saved system."""
    print("\nExample 4: Query Saved System (New Session)")
    print("-" * 70)

    # Simulate new session - create fresh system
    system = GlobalKnowledgeSystem(base_path="./examples/complex")

    # Load previous state
    try:
        system.load("./examples/complex/system_state.json")
        print("✓ Loaded system from previous session")

        # Query: Why does cache-service exist?
        context = system.get_project_context("cache-service")

        print("\nQuery: Why does cache-service exist?")
        print(f"Answer: Created for {context['origin']['created_for']}")
        print(f"Reason: {context['origin']['reason']}")

        print("\nCausal chain:")
        for step in context['causal_chain']['chain']:
            print(f"  - {step}")

        print("\n✓ Successfully retrieved cross-project knowledge without conversation history!")

    except FileNotFoundError:
        print("Run example 3 first to create the system")


def example_5_your_scenario():
    """Template for your 3-project scenario."""
    print("\nExample 5: Your 3-Project Scenario Template")
    print("-" * 70)

    system = GlobalKnowledgeSystem(base_path="./examples/your_projects")

    # Project 1
    system.create_project(
        name="project1",
        reason="[Your reason for project 1]"
    )

    # Project 2
    system.create_project(
        name="project2",
        reason="[Your reason for project 2]",
        created_for="project1"  # If related to project1
    )

    # Project 3 - created because project1 needed something
    system.create_project(
        name="project3",
        reason="[What project3 does]",
        created_for="project1",
        causal_chain=[
            "project1 had [problem]",
            "[Investigation or event]",
            "Decision to create project3",
            "project3 created"
        ]
    )

    # Add facts about relationships
    system.add_project_fact("project1", "project1", "needs", "project3")
    system.add_project_fact("project3", "project3", "solves", "project1_problem")

    print("✓ Created your 3 projects")

    # Save
    system.save("./examples/your_projects/system_state.json")

    # Later, in a new session, you can query:
    # context = system.get_project_context("project3")
    # This will tell you project3 was created for project1 and why!

    print("\nTo query later:")
    print("  system = GlobalKnowledgeSystem(base_path='./examples/your_projects')")
    print("  system.load('./examples/your_projects/system_state.json')")
    print("  context = system.get_project_context('project3')")
    print("  print(context['origin']['created_for'])  # 'project1'")


if __name__ == "__main__":
    print("=" * 70)
    print("USAGE EXAMPLES")
    print("=" * 70)

    example_1_simple_project()
    example_2_related_projects()
    example_3_complex_system()
    example_4_query_later()
    example_5_your_scenario()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nYou now know how to:")
    print("  ✓ Create projects")
    print("  ✓ Link projects with 'created_for'")
    print("  ✓ Add causal chains")
    print("  ✓ Query cross-project knowledge")
    print("  ✓ Save and load system state")
    print("\nAdapt example_5_your_scenario() for your needs!")
