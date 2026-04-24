"""
Global Knowledge System

Coordinates the entire hyperdimensional multi-agent crystallization system.
Manages cross-project knowledge, agent networks, and crystallization.
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np

from hypervector import HypervectorSpace
from neuromorphic_agent import NeuromorphicAgent, AgentNetwork
from crystallization import CrystallizationEngine


class GlobalKnowledgeSystem:
    """
    The central coordinator for the entire system.

    Manages:
    - Global hypervector space (shared across all projects)
    - Agent network (specialized agents per project/domain)
    - Crystallization (conversation → artifacts)
    - Cross-project queries and relationships
    """

    def __init__(self, base_path: str = ".", dims: int = 10000):
        self.base_path = Path(base_path)

        # Core components
        self.hypervector_space = HypervectorSpace(dims=dims)
        self.agent_network = AgentNetwork(self.hypervector_space)
        self.crystallization = CrystallizationEngine(base_path=str(self.base_path))

        # Project registry
        self.projects: Dict[str, Dict] = {}

        # Causal chains (for "why" queries)
        self.causal_chains: List[Dict] = []

        # System metadata
        self.created_at = datetime.now()
        self.query_count = 0

    def create_project(self,
                      name: str,
                      reason: str,
                      created_for: Optional[str] = None,
                      domain_concepts: Optional[List[str]] = None,
                      causal_chain: Optional[List[str]] = None) -> Dict:
        """
        Create a new project with full knowledge integration.

        Steps:
        1. Create agent for the project
        2. Crystallize artifacts (WHY.md, origin.json)
        3. Encode facts into hypervector space
        4. Establish cross-project connections
        5. Record causal chain
        """

        # 1. Create agent
        concepts = domain_concepts or [name]
        agent = self.agent_network.create_agent(name, concepts)

        # 2. Crystallize artifacts
        artifact_files = self.crystallization.crystallize_project_origin(
            project_name=name,
            reason=reason,
            created_for=created_for,
            causal_chain=causal_chain
        )

        # 3. Encode facts into hypervector space
        # Basic fact: project exists
        agent.add_fact(name, "is_a", "project", metadata={"reason": reason})

        # If created for another project, encode relationship
        if created_for:
            agent.add_fact(name, "created_for", created_for)
            agent.add_fact(created_for, "spawned", name)

            # Establish bidirectional agent connection
            if created_for in self.agent_network.agents:
                parent_agent = self.agent_network.agents[created_for]
                agent.connect(parent_agent, weight=0.9)
                parent_agent.connect(agent, weight=0.9)

                # Update crystallized relationship
                self.crystallization.crystallize_relationship(
                    name, created_for, "created_for", reason
                )

        # 4. Record causal chain
        if causal_chain:
            chain_record = {
                "project": name,
                "chain": causal_chain,
                "timestamp": datetime.now().isoformat()
            }
            self.causal_chains.append(chain_record)

            # Encode causal chain into hypervectors
            for i, step in enumerate(causal_chain):
                step_concept = f"{name}_causal_step_{i}"
                agent.add_fact(step_concept, "describes", name)
                agent.add_fact(step_concept, "content", step)

        # 5. Register project
        self.projects[name] = {
            "name": name,
            "reason": reason,
            "created_for": created_for,
            "created_at": datetime.now().isoformat(),
            "agent": agent,
            "artifacts": artifact_files
        }

        return {
            "project": name,
            "agent": agent.name,
            "artifacts": artifact_files,
            "status": "created"
        }

    def add_project_fact(self, project_name: str, subject: str,
                        relation: str, obj: str):
        """Add a fact to a project's knowledge base."""
        if project_name not in self.agent_network.agents:
            raise ValueError(f"Project {project_name} not found")

        agent = self.agent_network.agents[project_name]
        agent.add_fact(subject, relation, obj)

    def query(self, query_text: str, top_k: int = 10) -> Dict:
        """
        Query the global knowledge system.

        This is the main entry point for asking questions.

        Process:
        1. Encode query as hypervector
        2. Broadcast to agent network
        3. Agents spike and return results
        4. Bundle and rank results
        5. Return structured response
        """
        self.query_count += 1

        # Parse query to extract components
        query_components = self._parse_query(query_text)

        # Encode query as hypervector
        if query_components:
            query_vector = self.hypervector_space.encode_query(**query_components)
        else:
            # Fallback: encode entire query text as concept
            query_vector = self.hypervector_space.get_or_create_concept(query_text)

        # Broadcast to agent network
        results = self.agent_network.broadcast_query(query_vector)

        # Deduplicate and rank
        seen = set()
        unique_results = []
        for meta, score, agent_name in results:
            fact_key = (meta['subject'], meta['relation'], meta['object'])
            if fact_key not in seen:
                seen.add(fact_key)
                unique_results.append((meta, score, agent_name))

        # Limit results
        unique_results = unique_results[:top_k]

        # Check if this is a "why" query
        causal_info = None
        if "why" in query_text.lower():
            causal_info = self._find_causal_chain(query_text)

        return {
            "query": query_text,
            "results": [
                {
                    "fact": f"{meta['subject']} {meta['relation']} {meta['object']}",
                    "score": score,
                    "agent": agent_name,
                    "metadata": meta
                }
                for meta, score, agent_name in unique_results
            ],
            "causal_chain": causal_info,
            "num_results": len(unique_results),
            "timestamp": datetime.now().isoformat()
        }

    def _parse_query(self, query_text: str) -> Optional[Dict]:
        """
        Parse natural language query into structured components.

        Simple heuristic-based parsing.
        """
        query_lower = query_text.lower()

        # Pattern: "what does X need?"
        if "what does" in query_lower and "need" in query_lower:
            parts = query_lower.split("what does")[1].split("need")
            subject = parts[0].strip()
            return {"subject": subject, "relation": "needs"}

        # Pattern: "why does X exist?"
        if "why" in query_lower and "exist" in query_lower:
            parts = query_lower.split("why does")[1].split("exist")
            subject = parts[0].strip()
            return {"subject": subject, "relation": "created_for"}

        # Pattern: "what uses X?"
        if "what uses" in query_lower:
            parts = query_lower.split("what uses")[1]
            obj = parts.strip().rstrip("?")
            return {"relation": "uses", "obj": obj}

        return None

    def _find_causal_chain(self, query_text: str) -> Optional[Dict]:
        """Find causal chain relevant to query."""
        query_lower = query_text.lower()

        for chain_record in self.causal_chains:
            project = chain_record["project"]
            if project.lower() in query_lower:
                return chain_record

        return None

    def get_project_context(self, project_name: str) -> Dict:
        """
        Get full context for a project.

        Includes:
        - Origin information
        - Related projects
        - Key facts
        - Causal chain
        """
        if project_name not in self.projects:
            return {"error": f"Project {project_name} not found"}

        project_info = self.projects[project_name]

        # Get origin from crystallized artifact
        origin = self.crystallization.read_origin(project_name)

        # Get agent stats
        agent = project_info["agent"]
        agent_stats = agent.get_stats()

        # Find related projects (via agent connections)
        related = [
            {"project": conn_agent.name, "strength": weight}
            for conn_agent, weight in agent.connections.items()
        ]

        # Get causal chain
        causal = next(
            (c for c in self.causal_chains if c["project"] == project_name),
            None
        )

        return {
            "project": project_name,
            "origin": origin,
            "agent": agent_stats,
            "related_projects": related,
            "causal_chain": causal,
            "artifacts": project_info["artifacts"]
        }

    def visualize(self) -> str:
        """Generate ASCII visualization of the entire system."""
        lines = []
        lines.append("=" * 70)
        lines.append("GLOBAL KNOWLEDGE SYSTEM")
        lines.append("=" * 70)

        # System stats
        kb_stats = self.hypervector_space.stats()
        network_stats = self.agent_network.get_network_stats()

        lines.append(f"\nSystem Stats:")
        lines.append(f"  Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Total queries: {self.query_count}")
        lines.append(f"  Hypervector dimensions: {kb_stats['dimensions']}")
        lines.append(f"  Total concepts: {kb_stats['num_concepts']}")
        lines.append(f"  Total facts: {kb_stats['num_facts']}")
        lines.append(f"  Total agents: {network_stats['num_agents']}")
        lines.append(f"  Total spikes: {network_stats['total_spikes']}")

        # Projects
        lines.append(f"\nProjects ({len(self.projects)}):")
        for name, info in self.projects.items():
            lines.append(f"  • {name}")
            lines.append(f"    Reason: {info['reason']}")
            if info['created_for']:
                lines.append(f"    Created for: {info['created_for']}")

        # Agent network
        lines.append("\n" + self.agent_network.visualize_connections())

        # Project graph
        lines.append("\n" + self.crystallization.visualize_project_graph())

        return "\n".join(lines)

    def save(self, filepath: str):
        """Save the entire system state."""
        # Save hypervector space
        kb_path = Path(filepath).parent / "knowledge_base.json"
        self.hypervector_space.save(str(kb_path))

        # Save system metadata
        metadata = {
            "created_at": self.created_at.isoformat(),
            "query_count": self.query_count,
            "projects": {
                name: {
                    "name": info["name"],
                    "reason": info["reason"],
                    "created_for": info["created_for"],
                    "created_at": info["created_at"]
                }
                for name, info in self.projects.items()
            },
            "causal_chains": self.causal_chains
        }

        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

    def load(self, filepath: str):
        """Load system state from disk."""
        # Load hypervector space
        kb_path = Path(filepath).parent / "knowledge_base.json"
        if kb_path.exists():
            self.hypervector_space.load(str(kb_path))

        # Load metadata
        with open(filepath, 'r') as f:
            metadata = json.load(f)

        self.query_count = metadata["query_count"]
        self.causal_chains = metadata["causal_chains"]

        # Reconstruct projects and agents
        for name, info in metadata["projects"].items():
            # Create agent
            agent = self.agent_network.create_agent(name, [name])

            # Register project
            self.projects[name] = {
                "name": name,
                "reason": info["reason"],
                "created_for": info["created_for"],
                "created_at": info["created_at"],
                "agent": agent,
                "artifacts": {}
            }

        # Reconnect agents based on created_for relationships
        for name, info in self.projects.items():
            if info["created_for"]:
                parent_name = info["created_for"]
                if parent_name in self.agent_network.agents:
                    self.agent_network.connect_agents(name, parent_name, weight=0.9)


if __name__ == "__main__":
    # Quick test
    system = GlobalKnowledgeSystem(base_path="./test_projects")

    print("Creating test projects...\n")

    # Create auth-service
    system.create_project(
        name="auth-service",
        reason="Core authentication service for the platform"
    )

    # Create rate-limiter (for auth-service)
    system.create_project(
        name="rate-limiter",
        reason="Prevent API abuse through request rate limiting",
        created_for="auth-service",
        causal_chain=[
            "auth-service had no rate limiting",
            "Risk of abuse identified",
            "Decision to create separate rate limiting service",
            "rate-limiter project created"
        ]
    )

    # Add some facts
    system.add_project_fact("auth-service", "auth-service", "needs", "rate_limiting")
    system.add_project_fact("auth-service", "auth-service", "implements", "JWT")

    print(system.visualize())

    # Query
    print("\n" + "=" * 70)
    print("QUERY: What does auth-service need?")
    print("=" * 70)
    result = system.query("What does auth-service need?")
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 70)
    print("QUERY: Why does rate-limiter exist?")
    print("=" * 70)
    result = system.query("Why does rate-limiter exist?")
    print(json.dumps(result, indent=2))
