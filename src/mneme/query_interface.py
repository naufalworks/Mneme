"""Query interface for knowledge retrieval."""

from typing import Dict
from .cache import QueryCache


class QueryInterface:
    """Handles knowledge queries with caching."""

    def __init__(self, system):
        self.system = system
        self.cache = QueryCache(maxsize=128)

    def why_exists(self, project_name: str) -> str:
        """Answer 'Why does X exist?' question."""
        # Check cache first
        cache_key = self.cache._make_key("why_exists", project_name)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        context = self.system.get_project_context(project_name)

        if not context or 'error' in context:
            return f"No information found about {project_name}"

        lines = [f"# Why {project_name} Exists\n"]

        # Origin
        origin = context.get('origin', {})
        if origin.get('created_for'):
            lines.append(f"Created for: {origin['created_for']}")
        lines.append(f"Reason: {origin.get('reason', 'Unknown')}\n")

        # Causal chain
        causal = context.get('causal_chain')
        if causal and causal.get('chain'):
            lines.append("Causal Chain:")
            for i, step in enumerate(causal['chain'], 1):
                lines.append(f"  {i}. {step}")
            lines.append("")

        # Related projects
        related = context.get('related_projects', [])
        if related:
            lines.append("Related Projects:")
            for rel in related:
                lines.append(f"  • {rel['project']} (connection: {rel['strength']:.2f})")

        result = "\n".join(lines)

        # Cache the result
        self.cache.set(cache_key, result)

        return result

    def visualize(self) -> str:
        """Get ASCII visualization."""
        return self.system.visualize()

    def get_stats(self) -> Dict:
        """Get system statistics."""
        kb_stats = self.system.hypervector_space.stats()
        network_stats = self.system.agent_network.get_network_stats()

        return {
            "total_projects": len(self.system.projects),
            "total_concepts": kb_stats['num_concepts'],
            "total_facts": kb_stats['num_facts'],
            "total_agents": network_stats['num_agents'],
            "hypervector_dims": kb_stats['dimensions']
        }

    def invalidate_cache(self, project_name: str = None) -> None:
        """Invalidate cache for a project or all cache."""
        if project_name:
            self.cache.invalidate(project_name)
        else:
            self.cache.clear()
