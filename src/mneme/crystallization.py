"""
Crystallization Engine

Converts ephemeral conversations into permanent artifacts:
- WHY.md documents explaining project origins
- origin.json metadata files
- Causal chain documentation
- Cross-project dependency tracking
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class CrystallizationEngine:
    """
    Transforms knowledge into persistent artifacts.

    Artifacts are the permanent memory - they survive across sessions
    and provide ground truth for the hypervector knowledge base.
    """

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

    def crystallize_project_origin(self,
                                   project_name: str,
                                   reason: str,
                                   created_for: Optional[str] = None,
                                   dependencies: Optional[List[str]] = None,
                                   causal_chain: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Create origin artifacts for a new project.

        Returns dict of created file paths.
        """
        project_path = self.base_path / project_name
        meta_path = project_path / ".meta"
        docs_path = project_path / "docs"

        # Create directories
        meta_path.mkdir(parents=True, exist_ok=True)
        docs_path.mkdir(parents=True, exist_ok=True)

        created_files = {}

        # 1. Create origin.json
        origin_data = {
            "project": project_name,
            "created": datetime.now().isoformat(),
            "reason": reason,
            "created_for": created_for,
            "dependencies": {
                "upstream": [created_for] if created_for else [],
                "downstream": []
            },
            "causal_chain": causal_chain or [],
            "metadata": {
                "crystallized_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        origin_file = meta_path / "origin.json"
        with open(origin_file, 'w') as f:
            json.dump(origin_data, f, indent=2)
        created_files['origin'] = str(origin_file)

        # 2. Create WHY.md
        why_content = self._generate_why_doc(
            project_name, reason, created_for, causal_chain
        )

        why_file = docs_path / "WHY.md"
        with open(why_file, 'w') as f:
            f.write(why_content)
        created_files['why'] = str(why_file)

        # 3. Create README.md stub
        readme_content = f"""# {project_name}

{reason}

## Origin

This project was created on {datetime.now().strftime('%Y-%m-%d')}.

See [WHY.md](docs/WHY.md) for detailed context.

## Dependencies

"""
        if created_for:
            readme_content += f"- Created for: `{created_for}`\n"

        if dependencies:
            readme_content += "\nUpstream dependencies:\n"
            for dep in dependencies:
                readme_content += f"- `{dep}`\n"

        readme_file = project_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        created_files['readme'] = str(readme_file)

        return created_files

    def _generate_why_doc(self,
                         project_name: str,
                         reason: str,
                         created_for: Optional[str],
                         causal_chain: Optional[List[str]]) -> str:
        """Generate WHY.md content."""

        content = f"""---
name: {project_name}-origin
description: Why {project_name} exists
type: project
created: {datetime.now().isoformat()}
---

# Why {project_name} Exists

{reason}

"""

        if created_for:
            content += f"""## Created For

This project was created to support `{created_for}`.

"""

        if causal_chain:
            content += """## Causal Chain

The sequence of events that led to this project:

"""
            for i, step in enumerate(causal_chain, 1):
                content += f"{i}. {step}\n"
            content += "\n"

        content += f"""## How to Apply

When modifying `{project_name}`, consider:

"""

        if created_for:
            content += f"- Impact on `{created_for}` (this project was created for it)\n"

        content += f"""- The original reason for creation: {reason}
- Whether changes align with the project's purpose

## Metadata

- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Crystallized**: {datetime.now().isoformat()}
"""

        return content

    def update_dependency(self,
                         project_name: str,
                         dependency_type: str,  # 'upstream' or 'downstream'
                         dependency_name: str):
        """Add a dependency to a project's origin.json."""

        origin_file = self.base_path / project_name / ".meta" / "origin.json"

        if not origin_file.exists():
            raise FileNotFoundError(f"No origin.json found for {project_name}")

        with open(origin_file, 'r') as f:
            origin_data = json.load(f)

        # Add dependency if not already present
        if dependency_name not in origin_data['dependencies'][dependency_type]:
            origin_data['dependencies'][dependency_type].append(dependency_name)
            origin_data['metadata']['last_updated'] = datetime.now().isoformat()

        with open(origin_file, 'w') as f:
            json.dump(origin_data, f, indent=2)

    def crystallize_decision(self,
                           project_name: str,
                           decision_title: str,
                           context: str,
                           decision: str,
                           alternatives: Optional[List[str]] = None,
                           consequences: Optional[List[str]] = None) -> str:
        """
        Create a decision record (ADR-style).

        Returns path to created file.
        """
        docs_path = self.base_path / project_name / "docs" / "decisions"
        docs_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{timestamp}-{decision_title.lower().replace(' ', '-')}.md"
        filepath = docs_path / filename

        content = f"""# {decision_title}

**Date**: {datetime.now().strftime('%Y-%m-%d')}

## Context

{context}

## Decision

{decision}

"""

        if alternatives:
            content += "## Alternatives Considered\n\n"
            for alt in alternatives:
                content += f"- {alt}\n"
            content += "\n"

        if consequences:
            content += "## Consequences\n\n"
            for cons in consequences:
                content += f"- {cons}\n"
            content += "\n"

        with open(filepath, 'w') as f:
            f.write(content)

        return str(filepath)

    def crystallize_relationship(self,
                               project1: str,
                               project2: str,
                               relationship_type: str,
                               description: str):
        """
        Document a relationship between two projects.

        Updates both projects' metadata.
        """
        # Update project1's origin.json
        origin1_file = self.base_path / project1 / ".meta" / "origin.json"
        if origin1_file.exists():
            with open(origin1_file, 'r') as f:
                origin1 = json.load(f)

            if 'relationships' not in origin1:
                origin1['relationships'] = []

            origin1['relationships'].append({
                "project": project2,
                "type": relationship_type,
                "description": description,
                "established": datetime.now().isoformat()
            })

            with open(origin1_file, 'w') as f:
                json.dump(origin1, f, indent=2)

        # Update project2's origin.json (reverse relationship)
        origin2_file = self.base_path / project2 / ".meta" / "origin.json"
        if origin2_file.exists():
            with open(origin2_file, 'r') as f:
                origin2 = json.load(f)

            if 'relationships' not in origin2:
                origin2['relationships'] = []

            # Reverse relationship type
            reverse_type = self._reverse_relationship(relationship_type)

            origin2['relationships'].append({
                "project": project1,
                "type": reverse_type,
                "description": description,
                "established": datetime.now().isoformat()
            })

            with open(origin2_file, 'w') as f:
                json.dump(origin2, f, indent=2)

    def _reverse_relationship(self, rel_type: str) -> str:
        """Get reverse relationship type."""
        reverse_map = {
            "depends_on": "depended_by",
            "created_for": "created",
            "uses": "used_by",
            "extends": "extended_by"
        }
        return reverse_map.get(rel_type, rel_type)

    def read_origin(self, project_name: str) -> Optional[Dict]:
        """Read a project's origin.json."""
        origin_file = self.base_path / project_name / ".meta" / "origin.json"

        if not origin_file.exists():
            return None

        with open(origin_file, 'r') as f:
            return json.load(f)

    def get_project_graph(self) -> Dict:
        """
        Generate a graph of all projects and their relationships.

        Returns dict with nodes and edges.
        """
        projects = []
        relationships = []

        # Scan for all projects
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / ".meta" / "origin.json").exists():
                origin = self.read_origin(item.name)
                if origin:
                    projects.append({
                        "name": item.name,
                        "reason": origin.get("reason"),
                        "created": origin.get("created")
                    })

                    # Extract relationships
                    if "relationships" in origin:
                        for rel in origin["relationships"]:
                            relationships.append({
                                "from": item.name,
                                "to": rel["project"],
                                "type": rel["type"]
                            })

        return {
            "projects": projects,
            "relationships": relationships
        }

    def visualize_project_graph(self) -> str:
        """Generate ASCII visualization of project relationships."""
        graph = self.get_project_graph()

        lines = ["Project Dependency Graph:"]
        lines.append("=" * 60)

        for project in graph["projects"]:
            lines.append(f"\n{project['name']}")
            lines.append(f"  Reason: {project['reason']}")

            # Find relationships
            outgoing = [r for r in graph["relationships"] if r["from"] == project["name"]]
            if outgoing:
                lines.append("  Relationships:")
                for rel in outgoing:
                    lines.append(f"    → {rel['type']} {rel['to']}")

        return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    engine = CrystallizationEngine(base_path="./test_projects")

    # Create a test project
    files = engine.crystallize_project_origin(
        project_name="rate-limiter",
        reason="Prevent API abuse through request rate limiting",
        created_for="auth-service",
        causal_chain=[
            "auth-service had no rate limiting",
            "Risk of abuse identified",
            "Decision to create separate rate limiting service",
            "rate-limiter project created"
        ]
    )

    print("Created files:")
    for key, path in files.items():
        print(f"  {key}: {path}")

    # Read it back
    origin = engine.read_origin("rate-limiter")
    print(f"\nOrigin data: {json.dumps(origin, indent=2)}")
