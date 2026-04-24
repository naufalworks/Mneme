"""Optimized agent network with cycle prevention."""

from typing import Set, Dict, List, Tuple
import numpy as np


class OptimizedAgentNetwork:
    """Agent network with cycle prevention and depth limiting."""

    def __init__(self, hypervector_space):
        self.hypervector_space = hypervector_space
        self.agents = {}

    def propagate_query(self,
                       start_agent,
                       query_vector: np.ndarray,
                       max_depth: int = 3,
                       min_attention: float = 0.5) -> List[Tuple[str, float]]:
        """
        Propagate query through network with cycle prevention.

        Args:
            start_agent: Starting agent
            query_vector: Query vector
            max_depth: Maximum propagation depth
            min_attention: Minimum attention threshold

        Returns:
            List of (agent_name, attention_score) tuples
        """
        visited: Set[str] = set()
        results: List[Tuple[str, float]] = []

        # BFS with depth tracking
        queue = [(start_agent, 0)]  # (agent, depth)

        while queue:
            agent, depth = queue.pop(0)

            # Skip if already visited
            if agent.name in visited:
                continue

            visited.add(agent.name)

            # Calculate attention
            attention = agent.calculate_attention(query_vector)

            # Add to results if above threshold
            if attention >= min_attention:
                results.append((agent.name, attention))

            # Propagate to connected agents if within depth limit
            if depth < max_depth:
                for connected_agent, weight in agent.connections.items():
                    if connected_agent.name not in visited:
                        # Only propagate if connection is strong enough
                        if weight * attention >= min_attention:
                            queue.append((connected_agent, depth + 1))

        # Sort by attention score
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def find_shortest_path(self,
                          from_agent: str,
                          to_agent: str) -> List[str]:
        """Find shortest path between two agents (BFS)."""
        if from_agent not in self.agents or to_agent not in self.agents:
            return []

        visited = set()
        queue = [(self.agents[from_agent], [from_agent])]

        while queue:
            agent, path = queue.pop(0)

            if agent.name == to_agent:
                return path

            if agent.name in visited:
                continue

            visited.add(agent.name)

            for connected_agent in agent.connections.keys():
                if connected_agent.name not in visited:
                    queue.append((connected_agent, path + [connected_agent.name]))

        return []  # No path found
