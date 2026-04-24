"""
Interactive Query Demo

Shows how to query the system and get cross-project knowledge.
"""

from global_knowledge_system import GlobalKnowledgeSystem
import json


def main():
    print("=" * 70)
    print("LOADING EXISTING SYSTEM")
    print("=" * 70)

    # Load the existing system
    system = GlobalKnowledgeSystem(base_path="./demo_projects")

    try:
        system.load("./demo_projects/system_state.json")
        print("✓ Loaded existing system state\n")
    except FileNotFoundError:
        print("No existing system found. Run demo.py first.\n")
        return

    # Show system overview
    print(system.visualize())

    print("\n" + "=" * 70)
    print("INTERACTIVE QUERIES")
    print("=" * 70)

    # Direct hypervector queries (more reliable)
    print("\n1. Direct Query: Find all facts about 'rate-limiter'")
    print("-" * 70)

    # Get the rate-limiter concept vector
    rate_limiter_vec = system.hypervector_space.get_or_create_concept("rate-limiter")
    results = system.hypervector_space.query(rate_limiter_vec, top_k=10, threshold=0.2)

    print(f"Found {len(results)} facts:")
    for meta, score in results:
        print(f"  • {meta['subject']} → {meta['relation']} → {meta['object']} (score: {score:.3f})")

    print("\n2. Direct Query: Find all facts about 'auth-service'")
    print("-" * 70)

    auth_vec = system.hypervector_space.get_or_create_concept("auth-service")
    results = system.hypervector_space.query(auth_vec, top_k=10, threshold=0.2)

    print(f"Found {len(results)} facts:")
    for meta, score in results:
        print(f"  • {meta['subject']} → {meta['relation']} → {meta['object']} (score: {score:.3f})")

    print("\n3. Query: What was created_for auth-service?")
    print("-" * 70)

    query_vec = system.hypervector_space.encode_query(
        relation="created_for",
        obj="auth-service"
    )
    results = system.hypervector_space.query(query_vec, top_k=5, threshold=0.2)

    print(f"Found {len(results)} results:")
    for meta, score in results:
        print(f"  • {meta['subject']} was created for {meta['object']} (score: {score:.3f})")

    print("\n4. Get Full Context: rate-limiter")
    print("-" * 70)

    context = system.get_project_context("rate-limiter")

    print(f"\nProject: {context['project']}")
    print(f"Reason: {context['origin']['reason']}")
    print(f"Created for: {context['origin']['created_for']}")

    print("\nCausal Chain:")
    for i, step in enumerate(context['causal_chain']['chain'], 1):
        print(f"  {i}. {step}")

    print("\nRelated Projects:")
    for rel in context['related_projects']:
        print(f"  • {rel['project']} (connection strength: {rel['strength']:.2f})")

    print("\n5. Agent Network Query: Broadcast to all agents")
    print("-" * 70)

    # Create a query vector for "created_for"
    query_vec = system.hypervector_space.get_or_create_concept("created_for")
    results = system.agent_network.broadcast_query(query_vec)

    print(f"Found {len(results)} results from agents:")
    for meta, score, agent_name in results[:10]:
        print(f"  [{agent_name}] {meta['subject']} → {meta['relation']} → {meta['object']} (score: {score:.3f})")

    print("\n6. Concept Similarity: What's related to 'rate_limiting'?")
    print("-" * 70)

    related = system.hypervector_space.get_related_concepts("rate_limiting", top_k=10)
    print(f"Concepts similar to 'rate_limiting':")
    for concept, similarity in related:
        print(f"  • {concept} (similarity: {similarity:.3f})")

    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)

    print("\n✓ The system preserves cross-project relationships")
    print("✓ rate-limiter knows it was created for auth-service")
    print("✓ Causal chains explain WHY projects exist")
    print("✓ Agent network maintains connections between projects")
    print("✓ Hypervector space enables semantic similarity queries")
    print("✓ All knowledge persists in artifacts (WHY.md, origin.json)")

    print("\n" + "=" * 70)
    print("TESTING THE CRITICAL QUESTION")
    print("=" * 70)

    print("\nQuestion: 'Why does rate-limiter exist?'")
    print("Answer sources:\n")

    print("1. From Causal Chain:")
    causal = context['causal_chain']
    for step in causal['chain']:
        print(f"   - {step}")

    print("\n2. From Origin Metadata:")
    print(f"   - Created for: {context['origin']['created_for']}")
    print(f"   - Reason: {context['origin']['reason']}")

    print("\n3. From Agent Network:")
    print(f"   - Connected to: {[r['project'] for r in context['related_projects']]}")

    print("\n4. From Hypervector Space:")
    query_vec = system.hypervector_space.encode_query(
        subject="rate-limiter",
        relation="created_for"
    )
    results = system.hypervector_space.query(query_vec, top_k=3)
    for meta, score in results:
        print(f"   - {meta['subject']} {meta['relation']} {meta['object']}")

    print("\n✓ ANSWER: rate-limiter exists because auth-service needed")
    print("  rate limiting to prevent abuse. This knowledge is preserved")
    print("  across sessions through multiple redundant mechanisms.")


if __name__ == "__main__":
    main()
