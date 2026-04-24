#!/usr/bin/env python3
"""
HOW TO USE - Simple Guide

This shows you EXACTLY how to use the system in your own projects.
"""

from claude_code_integration import init_knowledge_system

print("=" * 70)
print("HOW TO USE THE KNOWLEDGE SYSTEM")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Initialize (do this once per workspace)
# ============================================================================

print("STEP 1: Initialize")
print("-" * 70)
print()
print("In your Python code:")
print()
print("  from claude_code_integration import init_knowledge_system")
print("  knowledge = init_knowledge_system()")
print()

knowledge = init_knowledge_system()

print("✓ Done! This creates .claude/knowledge/ directory")
print()

# ============================================================================
# STEP 2: Track projects as you create them
# ============================================================================

print("STEP 2: Track Projects")
print("-" * 70)
print()
print("When you create a project:")
print()
print("  knowledge.track_project_creation(")
print("      project_name='my-service',")
print("      reason='What it does',")
print("      created_for='parent-service'  # If applicable")
print("  )")
print()

# Example
knowledge.track_project_creation(
    project_name="example-service",
    reason="Example service for demonstration",
    created_for=None,
    technologies=["Python", "FastAPI"]
)

print("✓ Done! Knowledge saved to disk")
print()

# ============================================================================
# STEP 3: Query later (even in new sessions)
# ============================================================================

print("STEP 3: Query Later")
print("-" * 70)
print()
print("In a NEW session (weeks later):")
print()
print("  from claude_code_integration import init_knowledge_system")
print("  knowledge = init_knowledge_system()  # Loads existing knowledge")
print("  print(knowledge.why_does_exist('my-service'))")
print()

# Example
answer = knowledge.why_does_exist("example-service")
print("Output:")
print(answer)
print()

# ============================================================================
# THAT'S IT!
# ============================================================================

print("=" * 70)
print("THAT'S ALL YOU NEED!")
print("=" * 70)
print()
print("The system:")
print("  ✅ Stores knowledge to .claude/knowledge/")
print("  ✅ Loads automatically in new sessions")
print("  ✅ Works without conversation history")
print("  ✅ No LLM API needed")
print()

# ============================================================================
# WHERE IS THE KNOWLEDGE STORED?
# ============================================================================

print("=" * 70)
print("WHERE IS KNOWLEDGE STORED?")
print("=" * 70)
print()
print("Location: .claude/knowledge/")
print()
print("Files created:")
print("  • system_state.json - System state")
print("  • knowledge_base.json - Hypervector space")
print("  • projects/")
print("    └── your-project/")
print("        ├── .meta/origin.json (machine-readable)")
print("        ├── docs/WHY.md (human-readable)")
print("        └── README.md")
print()

# ============================================================================
# HOW TO VERIFY IT'S WORKING
# ============================================================================

print("=" * 70)
print("HOW TO VERIFY IT'S WORKING")
print("=" * 70)
print()
print("1. Check files exist:")
print("   $ ls -la .claude/knowledge/")
print()
print("2. Read WHY.md:")
print("   $ cat .claude/knowledge/projects/your-project/docs/WHY.md")
print()
print("3. Test in new session:")
print("   - Close Python")
print("   - Open new Python session")
print("   - Run: knowledge = init_knowledge_system()")
print("   - Run: print(knowledge.why_does_exist('your-project'))")
print("   - If it returns the answer, it's working!")
print()

# ============================================================================
# COMMON COMMANDS
# ============================================================================

print("=" * 70)
print("COMMON COMMANDS")
print("=" * 70)
print()

print("# Initialize")
print("knowledge = init_knowledge_system()")
print()

print("# Track project")
print("knowledge.track_project_creation(")
print("    project_name='name',")
print("    reason='why',")
print("    created_for='parent',  # optional")
print("    causal_chain=['step1', 'step2'],  # optional")
print("    technologies=['tech1', 'tech2']  # optional")
print(")")
print()

print("# Add relationship")
print("knowledge.add_relationship('subject', 'relation', 'object')")
print()

print("# Query why")
print("print(knowledge.why_does_exist('project-name'))")
print()

print("# Get full context")
print("context = knowledge.query_context('project-name')")
print()

print("# List all projects")
print("projects = knowledge.list_projects()")
print()

print("# Visualize")
print("print(knowledge.visualize())")
print()

print("# Export summary")
print("knowledge.export_summary('./SUMMARY.md')")
print()

# ============================================================================
# FINAL NOTES
# ============================================================================

print("=" * 70)
print("IMPORTANT NOTES")
print("=" * 70)
print()
print("✅ NO LLM API NEEDED")
print("   This is just Python storing/retrieving data")
print()
print("✅ WORKS OFFLINE")
print("   No internet connection required")
print()
print("✅ PERMANENT STORAGE")
print("   Knowledge never deleted unless you delete files")
print()
print("✅ CROSS-SESSION")
print("   Works across Python sessions, Claude sessions, etc.")
print()
print("✅ HUMAN & MACHINE READABLE")
print("   WHY.md for humans, origin.json for machines")
print()

print("=" * 70)
print("YOU'RE READY TO USE IT!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Copy the 5 core files to your workspace")
print("  2. Use: knowledge = init_knowledge_system()")
print("  3. Track your projects as you create them")
print("  4. Query later when you need to remember")
print()
print("Questions? Read: CLAUDE_CODE_USAGE.md")
print()
