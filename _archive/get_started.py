#!/usr/bin/env python3
"""
Getting Started with Your 3-Project Scenario

This script helps you set up your own 3-project system.
Just fill in your project details and run!
"""

from global_knowledge_system import GlobalKnowledgeSystem


def setup_your_projects():
    """
    Template for your specific 3-project scenario.

    Replace the placeholder text with your actual project information.
    """

    print("=" * 70)
    print("SETTING UP YOUR 3-PROJECT SYSTEM")
    print("=" * 70)
    print()

    # Initialize the system
    system = GlobalKnowledgeSystem(base_path="./my_projects", dims=10000)

    # ========================================================================
    # PROJECT 1: Your first project
    # ========================================================================

    print("Creating Project 1...")

    project1_name = "project1"  # TODO: Replace with your project name
    project1_reason = "Description of what project 1 does"  # TODO: Replace

    system.create_project(
        name=project1_name,
        reason=project1_reason,
        domain_concepts=[project1_name, "concept1", "concept2"]  # TODO: Add relevant concepts
    )

    # Add facts about project 1
    system.add_project_fact(project1_name, project1_name, "implements", "feature_x")  # TODO: Customize
    system.add_project_fact(project1_name, project1_name, "uses", "technology_y")  # TODO: Customize

    print(f"✓ Created {project1_name}\n")

    # ========================================================================
    # PROJECT 2: Your second project (optional: related to project 1)
    # ========================================================================

    print("Creating Project 2...")

    project2_name = "project2"  # TODO: Replace with your project name
    project2_reason = "Description of what project 2 does"  # TODO: Replace
    project2_created_for = None  # TODO: Set to project1_name if related, or None

    system.create_project(
        name=project2_name,
        reason=project2_reason,
        created_for=project2_created_for,  # Link to project 1 if needed
        domain_concepts=[project2_name, "concept3", "concept4"]  # TODO: Add relevant concepts
    )

    # Add facts about project 2
    system.add_project_fact(project2_name, project2_name, "handles", "task_z")  # TODO: Customize

    if project2_created_for:
        system.add_project_fact(project2_name, project2_name, "uses", project2_created_for)

    print(f"✓ Created {project2_name}\n")

    # ========================================================================
    # PROJECT 3: Created because project 1 needed something
    # ========================================================================

    print("Creating Project 3 (THE KEY ONE)...")

    project3_name = "project3"  # TODO: Replace with your project name
    project3_reason = "What project 3 does to solve project 1's need"  # TODO: Replace

    # TODO: Fill in the causal chain - why was project 3 created?
    causal_chain = [
        f"{project1_name} had problem X",  # TODO: What problem did project 1 have?
        "Investigation revealed Y",  # TODO: What did you discover?
        "Decision to create separate solution",  # TODO: What decision was made?
        f"{project3_name} project created"
    ]

    system.create_project(
        name=project3_name,
        reason=project3_reason,
        created_for=project1_name,  # This is the key link!
        domain_concepts=[project3_name, "concept5", "concept6"],  # TODO: Add relevant concepts
        causal_chain=causal_chain
    )

    # Add facts about project 3
    system.add_project_fact(project3_name, project3_name, "solves", f"{project1_name}_problem")  # TODO: Customize
    system.add_project_fact(project3_name, project3_name, "protects", project1_name)  # TODO: Customize
    system.add_project_fact(project1_name, project1_name, "needs", project3_name)

    print(f"✓ Created {project3_name}\n")

    # ========================================================================
    # SAVE THE SYSTEM
    # ========================================================================

    print("Saving system state...")
    system.save("./my_projects/system_state.json")
    print("✓ Saved to ./my_projects/system_state.json\n")

    # ========================================================================
    # SHOW WHAT WAS CREATED
    # ========================================================================

    print(system.visualize())

    # ========================================================================
    # TEST THE CRITICAL QUESTION
    # ========================================================================

    print("\n" + "=" * 70)
    print("TESTING: Why does project 3 exist?")
    print("=" * 70)

    context = system.get_project_context(project3_name)

    print(f"\nAnswer:")
    print(f"  Created for: {context['origin']['created_for']}")
    print(f"  Reason: {context['origin']['reason']}")

    print(f"\nCausal Chain:")
    for i, step in enumerate(context['causal_chain']['chain'], 1):
        print(f"  {i}. {step}")

    print(f"\nRelated Projects:")
    for rel in context['related_projects']:
        print(f"  • {rel['project']} (connection: {rel['strength']:.2f})")

    print(f"\nArtifacts Created:")
    for key, path in context['artifacts'].items():
        print(f"  • {key}: {path}")

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print()
    print("Your 3-project system is set up!")
    print()
    print("Key achievement:")
    print(f"  The system knows {project3_name} was created because")
    print(f"  {project1_name} needed it. This knowledge will persist")
    print("  across sessions, even without conversation history.")
    print()
    print("Next steps:")
    print("  1. Check the generated files in ./my_projects/")
    print(f"  2. Read {project3_name}/docs/WHY.md")
    print("  3. Try loading in a new session:")
    print("     system = GlobalKnowledgeSystem(base_path='./my_projects')")
    print("     system.load('./my_projects/system_state.json')")
    print(f"     context = system.get_project_context('{project3_name}')")
    print()


def example_filled_in():
    """
    Example with actual values filled in.
    This shows what your setup_your_projects() should look like.
    """

    print("=" * 70)
    print("EXAMPLE: E-commerce System")
    print("=" * 70)
    print()

    system = GlobalKnowledgeSystem(base_path="./example_ecommerce", dims=10000)

    # Project 1: Main store
    system.create_project(
        name="online-store",
        reason="Main e-commerce platform for selling products",
        domain_concepts=["online-store", "ecommerce", "shopping"]
    )

    system.add_project_fact("online-store", "online-store", "implements", "shopping_cart")
    system.add_project_fact("online-store", "online-store", "uses", "PostgreSQL")
    system.add_project_fact("online-store", "online-store", "needs", "payment_processing")

    print("✓ Created online-store\n")

    # Project 2: Admin panel
    system.create_project(
        name="admin-panel",
        reason="Admin interface for managing products and orders",
        created_for="online-store",
        domain_concepts=["admin-panel", "management", "dashboard"]
    )

    system.add_project_fact("admin-panel", "admin-panel", "manages", "online-store")

    print("✓ Created admin-panel\n")

    # Project 3: Payment service (created because online-store needed it)
    system.create_project(
        name="payment-service",
        reason="Handle payment processing and fraud detection",
        created_for="online-store",
        domain_concepts=["payment-service", "payments", "stripe"],
        causal_chain=[
            "online-store needed payment processing",
            "Security and PCI compliance requirements identified",
            "Decision to separate payment logic into microservice",
            "payment-service project created"
        ]
    )

    system.add_project_fact("payment-service", "payment-service", "processes", "payments")
    system.add_project_fact("payment-service", "payment-service", "protects", "online-store")
    system.add_project_fact("online-store", "online-store", "uses", "payment-service")

    print("✓ Created payment-service\n")

    # Save
    system.save("./example_ecommerce/system_state.json")

    print(system.visualize())

    # Test
    print("\n" + "=" * 70)
    print("TEST: Why does payment-service exist?")
    print("=" * 70)

    context = system.get_project_context("payment-service")
    print(f"\nAnswer: Created for {context['origin']['created_for']}")
    print(f"Reason: {context['origin']['reason']}")
    print("\nCausal chain:")
    for step in context['causal_chain']['chain']:
        print(f"  - {step}")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║  GETTING STARTED: Your 3-Project System                         ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("This script helps you set up your own 3-project system.")
    print()
    print("Choose an option:")
    print("  1. See an example (e-commerce system)")
    print("  2. Set up your own projects (edit this file first)")
    print()

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("\nRunning example...\n")
        example_filled_in()
    elif choice == "2":
        print("\nSetting up your projects...\n")
        print("NOTE: Edit this file first to fill in your project details!")
        print("Look for TODO comments in the setup_your_projects() function.\n")

        proceed = input("Have you edited the file? (y/n): ").strip().lower()
        if proceed == "y":
            setup_your_projects()
        else:
            print("\nPlease edit get_started.py first:")
            print("  1. Open get_started.py in your editor")
            print("  2. Find the setup_your_projects() function")
            print("  3. Replace TODO comments with your project details")
            print("  4. Run this script again")
    else:
        print("\nInvalid choice. Run the script again.")
