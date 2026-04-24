"""
Claude Code Integration for Hyperdimensional Multi-Agent System

This module integrates the knowledge system with Claude Code to automatically
preserve cross-project knowledge, causal chains, and context across sessions.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from global_knowledge_system import GlobalKnowledgeSystem


class ClaudeCodeIntegration:
    """
    Integration layer between Claude Code and the knowledge system.

    Automatically tracks:
    - Projects created during coding sessions
    - Why decisions were made
    - Cross-project relationships
    - Causal chains of development
    """

    def __init__(self, workspace_path: str = None):
        """
        Initialize the integration.

        Args:
            workspace_path: Path to the current workspace.
                          Defaults to current directory.
        """
        self.workspace_path = Path(workspace_path or os.getcwd())

        # Initialize knowledge system in .claude/knowledge/
        self.knowledge_dir = self.workspace_path / ".claude" / "knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.system = GlobalKnowledgeSystem(
            base_path=str(self.knowledge_dir / "projects"),
            dims=10000
        )

        # Load existing state if available
        self.state_file = self.knowledge_dir / "system_state.json"
        if self.state_file.exists():
            self.system.load(str(self.state_file))
            print(f"✓ Loaded existing knowledge from {self.state_file}")
        else:
            print(f"✓ Initialized new knowledge system at {self.knowledge_dir}")

    def track_project_creation(self,
                              project_name: str,
                              reason: str,
                              created_for: Optional[str] = None,
                              causal_chain: Optional[List[str]] = None,
                              technologies: Optional[List[str]] = None) -> Dict:
        """
        Track when a new project/component is created.

        Args:
            project_name: Name of the project/component
            reason: Why it was created
            created_for: Parent project (if applicable)
            causal_chain: Steps that led to creation
            technologies: Tech stack used

        Returns:
            Dict with project info and artifacts created
        """
        print(f"\n📝 Tracking project: {project_name}")

        # Create domain concepts from technologies
        domain_concepts = [project_name]
        if technologies:
            domain_concepts.extend(technologies)

        # Create project in knowledge system
        result = self.system.create_project(
            name=project_name,
            reason=reason,
            created_for=created_for,
            domain_concepts=domain_concepts,
            causal_chain=causal_chain
        )

        # Save state
        self._save_state()

        print(f"✓ Tracked {project_name}")
        if created_for:
            print(f"  → Created for: {created_for}")
        if causal_chain:
            print(f"  → Causal chain: {len(causal_chain)} steps")

        return result

    def add_relationship(self,
                        subject: str,
                        relation: str,
                        object: str) -> None:
        """
        Add a relationship between projects/components.

        Args:
            subject: Source project
            relation: Type of relationship (uses, depends_on, implements, etc.)
            object: Target project/concept
        """
        self.system.add_project_fact(subject, subject, relation, object)
        self._save_state()
        print(f"✓ Added: {subject} {relation} {object}")

    def query_context(self, project_name: str) -> Dict:
        """
        Get full context for a project.

        Args:
            project_name: Name of the project

        Returns:
            Dict with origin, causal chain, relationships, artifacts
        """
        return self.system.get_project_context(project_name)

    def why_does_exist(self, project_name: str) -> str:
        """
        Answer "Why does X exist?" question.

        Args:
            project_name: Name of the project

        Returns:
            Human-readable explanation
        """
        context = self.query_context(project_name)

        if not context or 'error' in context:
            return f"No information found about {project_name}"

        explanation = []
        explanation.append(f"# Why {project_name} Exists\n")

        # Origin
        origin = context.get('origin', {})
        if origin.get('created_for'):
            explanation.append(f"Created for: {origin['created_for']}")
        explanation.append(f"Reason: {origin.get('reason', 'Unknown')}\n")

        # Causal chain
        causal = context.get('causal_chain')
        if causal and causal.get('chain'):
            explanation.append("Causal Chain:")
            for i, step in enumerate(causal['chain'], 1):
                explanation.append(f"  {i}. {step}")
            explanation.append("")

        # Related projects
        related = context.get('related_projects', [])
        if related:
            explanation.append("Related Projects:")
            for rel in related:
                explanation.append(f"  • {rel['project']} (connection: {rel['strength']:.2f})")

        return "\n".join(explanation)

    def list_projects(self) -> List[Dict]:
        """
        List all tracked projects.

        Returns:
            List of project info dicts
        """
        projects = []
        for name, info in self.system.projects.items():
            projects.append({
                "name": name,
                "reason": info["reason"],
                "created_for": info.get("created_for"),
                "created_at": info.get("created_at")
            })
        return projects

    def visualize(self) -> str:
        """
        Get ASCII visualization of the knowledge system.

        Returns:
            Formatted string with system overview
        """
        return self.system.visualize()

    def export_summary(self, output_file: Optional[str] = None) -> str:
        """
        Export a summary of all tracked knowledge.

        Args:
            output_file: Optional file to write summary to

        Returns:
            Summary text
        """
        summary = []
        summary.append("=" * 70)
        summary.append("CLAUDE CODE KNOWLEDGE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"\nGenerated: {datetime.now().isoformat()}")
        summary.append(f"Workspace: {self.workspace_path}\n")

        # Projects
        projects = self.list_projects()
        summary.append(f"Total Projects: {len(projects)}\n")

        for proj in projects:
            summary.append(f"\n## {proj['name']}")
            summary.append(f"Reason: {proj['reason']}")
            if proj['created_for']:
                summary.append(f"Created for: {proj['created_for']}")
            summary.append(f"Created: {proj['created_at']}")

            # Get full context
            context = self.query_context(proj['name'])

            # Causal chain
            causal = context.get('causal_chain')
            if causal and causal.get('chain'):
                summary.append("\nCausal Chain:")
                for step in causal['chain']:
                    summary.append(f"  - {step}")

            # Related projects
            related = context.get('related_projects', [])
            if related:
                summary.append("\nRelated:")
                for rel in related:
                    summary.append(f"  - {rel['project']}")

        summary_text = "\n".join(summary)

        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(summary_text)
            print(f"✓ Summary exported to {output_file}")

        return summary_text

    def _save_state(self):
        """Save system state to disk."""
        self.system.save(str(self.state_file))

    def get_stats(self) -> Dict:
        """
        Get statistics about the knowledge system.

        Returns:
            Dict with stats
        """
        kb_stats = self.system.hypervector_space.stats()
        network_stats = self.system.agent_network.get_network_stats()

        return {
            "workspace": str(self.workspace_path),
            "knowledge_dir": str(self.knowledge_dir),
            "total_projects": len(self.system.projects),
            "total_concepts": kb_stats['num_concepts'],
            "total_facts": kb_stats['num_facts'],
            "total_agents": network_stats['num_agents'],
            "hypervector_dims": kb_stats['dimensions']
        }


# Convenience functions for Claude Code
def init_knowledge_system(workspace_path: str = None) -> ClaudeCodeIntegration:
    """
    Initialize the knowledge system for the current workspace.

    Args:
        workspace_path: Path to workspace (defaults to current directory)

    Returns:
        ClaudeCodeIntegration instance
    """
    return ClaudeCodeIntegration(workspace_path)


def track_project(integration: ClaudeCodeIntegration,
                 name: str,
                 reason: str,
                 created_for: str = None,
                 why_steps: List[str] = None,
                 tech_stack: List[str] = None) -> Dict:
    """
    Quick function to track a project.

    Args:
        integration: ClaudeCodeIntegration instance
        name: Project name
        reason: Why it was created
        created_for: Parent project
        why_steps: Causal chain steps
        tech_stack: Technologies used

    Returns:
        Project info dict
    """
    return integration.track_project_creation(
        project_name=name,
        reason=reason,
        created_for=created_for,
        causal_chain=why_steps,
        technologies=tech_stack
    )


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("CLAUDE CODE INTEGRATION - EXAMPLE")
    print("=" * 70)
    print()

    # Initialize
    integration = init_knowledge_system("./example_workspace")

    # Track projects
    print("Tracking projects...\n")

    track_project(
        integration,
        name="auth-service",
        reason="Handle user authentication and authorization",
        tech_stack=["Python", "FastAPI", "JWT"]
    )

    track_project(
        integration,
        name="rate-limiter",
        reason="Prevent API abuse through request rate limiting",
        created_for="auth-service",
        why_steps=[
            "auth-service had no rate limiting",
            "Brute-force attacks detected in logs",
            "Security team recommended rate limiting",
            "Decision to create separate rate-limiter service"
        ],
        tech_stack=["Python", "Redis", "Token Bucket"]
    )

    # Add relationships
    print("\nAdding relationships...\n")
    integration.add_relationship("auth-service", "uses", "rate-limiter")
    integration.add_relationship("rate-limiter", "protects", "auth-service")

    # Query
    print("\n" + "=" * 70)
    print("QUERY: Why does rate-limiter exist?")
    print("=" * 70)
    print(integration.why_does_exist("rate-limiter"))

    # Visualize
    print("\n" + "=" * 70)
    print("SYSTEM VISUALIZATION")
    print("=" * 70)
    print(integration.visualize())

    # Stats
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    stats = integration.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Export summary
    print("\n" + "=" * 70)
    print("EXPORTING SUMMARY")
    print("=" * 70)
    integration.export_summary("./example_workspace/.claude/knowledge/SUMMARY.md")

    print("\n✓ Integration example complete!")
