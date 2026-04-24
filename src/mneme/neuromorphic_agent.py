"""
Neuromorphic Agent System

Implements spiking agents with attention mechanisms and Hebbian learning.
Agents maintain specialized knowledge domains and communicate through
spike propagation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from collections import deque
from .hypervector import HypervectorSpace


class NeuromorphicAgent:
    """
    A spiking agent that maintains domain-specific knowledge.

    Features:
    - Attention mechanism (only activates for relevant queries)
    - Hebbian learning (connections strengthen with use)
    - Spike propagation (activates connected agents)
    """

    def __init__(self, name: str, knowledge_base: HypervectorSpace,
                 domain_concepts: Optional[List[str]] = None):
        self.name = name
        self.kb = knowledge_base
        self.domain_concepts = domain_concepts or [name]

        # Agent state
        self.activation = 0.0
        self.last_spike_time = None

        # Connections to other agents (agent -> weight)
        self.connections: Dict['NeuromorphicAgent', float] = {}

        # Statistics - use bounded deque to prevent memory leak
        self.spike_count = 0
        self.query_history: deque = deque(maxlen=1000)  # Keep last 1000 queries

        # Create domain vector (bundle of domain concepts)
        domain_vecs = [self.kb.get_or_create_concept(c) for c in self.domain_concepts]
        self.domain_vector = self.kb.bundle(domain_vecs)

    def connect(self, other_agent: 'NeuromorphicAgent', weight: float = 0.5):
        """Create connection to another agent."""
        self.connections[other_agent] = weight

    def strengthen_connection(self, other_agent: 'NeuromorphicAgent', delta: float = 0.1):
        """Hebbian learning: strengthen connection when agents fire together."""
        if other_agent in self.connections:
            self.connections[other_agent] = min(1.0, self.connections[other_agent] + delta)

    def weaken_connection(self, other_agent: 'NeuromorphicAgent', delta: float = 0.05):
        """Weaken unused connections over time."""
        if other_agent in self.connections:
            self.connections[other_agent] = max(0.0, self.connections[other_agent] - delta)

    def calculate_attention(self, query_vector: np.ndarray) -> float:
        """
        Calculate how relevant this query is to the agent's domain.

        Returns attention score [0, 1].
        """
        similarity = self.kb.cosine_similarity(query_vector, self.domain_vector)

        # Normalize to [0, 1]
        attention = (similarity + 1) / 2

        return attention

    def spike(self, query_vector: np.ndarray,
              propagate: bool = True,
              visited: Optional[Set['NeuromorphicAgent']] = None) -> List[Tuple[Dict, float]]:
        """
        Agent activation (spike).

        1. Calculate attention
        2. If attention > threshold, search knowledge base
        3. Propagate spike to connected agents
        4. Return results
        """
        if visited is None:
            visited = set()

        # Prevent infinite loops
        if self in visited:
            return []
        visited.add(self)

        # Calculate attention
        attention = self.calculate_attention(query_vector)

        # Record query
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "attention": attention,
            "activated": attention > 0.5
        })

        # Only activate if attention is high enough
        if attention < 0.5:
            return []

        # Spike!
        self.activation = attention
        self.last_spike_time = datetime.now()
        self.spike_count += 1

        # Search knowledge base
        results = self.kb.query(query_vector, top_k=10)

        # Filter results relevant to this agent's domain
        filtered_results = []
        for meta, score in results:
            # Check if fact involves this agent's domain
            fact_concepts = [meta['subject'], meta['object']]
            if any(concept in self.domain_concepts for concept in fact_concepts):
                filtered_results.append((meta, score * attention))

        # Propagate to connected agents
        if propagate:
            for connected_agent, weight in self.connections.items():
                if weight > 0.3:  # Only propagate through strong connections
                    # Hebbian learning: strengthen connection
                    self.strengthen_connection(connected_agent, delta=0.05)

                    # Propagate spike (with reduced intensity)
                    connected_results = connected_agent.spike(
                        query_vector,
                        propagate=True,
                        visited=visited
                    )

                    # Add connected agent's results (weighted by connection strength)
                    for meta, score in connected_results:
                        filtered_results.append((meta, score * weight))

        return filtered_results

    def add_fact(self, subject: str, relation: str, obj: str,
                 metadata: Optional[Dict] = None):
        """Add a fact to this agent's knowledge base."""
        meta = {
            "agent": self.name,
            **(metadata or {})
        }
        self.kb.encode_fact(subject, relation, obj, metadata=meta)

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "name": self.name,
            "domain": self.domain_concepts,
            "spike_count": self.spike_count,
            "num_connections": len(self.connections),
            "connections": {
                agent.name: weight
                for agent, weight in self.connections.items()
            },
            "last_spike": self.last_spike_time.isoformat() if self.last_spike_time else None
        }

    def __repr__(self):
        return f"NeuromorphicAgent(name='{self.name}', domain={self.domain_concepts})"


class AgentNetwork:
    """
    Network of neuromorphic agents with automatic connection management.
    """

    def __init__(self, knowledge_base: HypervectorSpace):
        self.kb = knowledge_base
        self.agents: Dict[str, NeuromorphicAgent] = {}

    def create_agent(self, name: str, domain_concepts: Optional[List[str]] = None) -> NeuromorphicAgent:
        """Create a new agent in the network."""
        agent = NeuromorphicAgent(name, self.kb, domain_concepts)
        self.agents[name] = agent
        return agent

    def connect_agents(self, agent1_name: str, agent2_name: str,
                       weight: float = 0.5, bidirectional: bool = True):
        """Create connection between two agents."""
        agent1 = self.agents[agent1_name]
        agent2 = self.agents[agent2_name]

        agent1.connect(agent2, weight)

        if bidirectional:
            agent2.connect(agent1, weight)

    def auto_connect(self, threshold: float = 0.3):
        """
        Automatically connect agents with similar domains.

        Uses LSH index for O(n log n) similarity search instead of O(n²).
        """
        agent_list = list(self.agents.values())

        # For small networks (< 10 agents), use simple pairwise comparison
        if len(agent_list) < 10:
            for i, agent1 in enumerate(agent_list):
                for agent2 in agent_list[i+1:]:
                    try:
                        # Calculate domain similarity
                        similarity = self.kb.cosine_similarity(
                            agent1.domain_vector,
                            agent2.domain_vector
                        )

                        # Normalize to [0, 1]
                        similarity = (similarity + 1) / 2

                        if similarity > threshold:
                            agent1.connect(agent2, similarity)
                            agent2.connect(agent1, similarity)
                    except ValueError:
                        # Skip if zero vectors
                        continue
        else:
            # For larger networks, use LSH index for efficient similarity search
            from .lsh_index import LSHIndex

            # Build LSH index of agent domain vectors
            lsh = LSHIndex(dims=self.kb.dims, n_bits=256)
            for idx, agent in enumerate(agent_list):
                lsh.add(agent.domain_vector, {"agent_idx": idx, "name": agent.name})

            # Query for similar agents (O(n log n) instead of O(n²))
            for idx, agent in enumerate(agent_list):
                try:
                    similar_results = lsh.query(agent.domain_vector, top_k=10)

                    for meta, similarity in similar_results:
                        other_idx = meta["agent_idx"]
                        if other_idx != idx:  # Don't connect to self
                            # Normalize to [0, 1]
                            similarity = (similarity + 1) / 2

                            if similarity > threshold:
                                other_agent = agent_list[other_idx]
                                agent.connect(other_agent, similarity)
                                other_agent.connect(agent, similarity)
                except ValueError:
                    # Skip if zero vectors
                    continue

    def broadcast_query(self, query_vector: np.ndarray) -> List[Tuple[Dict, float, str]]:
        """
        Broadcast query to all agents in parallel.

        Returns list of (metadata, score, agent_name) tuples.
        """
        all_results = []

        for agent in self.agents.values():
            results = agent.spike(query_vector, propagate=False)

            # Tag results with agent name
            for meta, score in results:
                all_results.append((meta, score, agent.name))

        # Sort by score
        all_results.sort(key=lambda x: x[1], reverse=True)

        return all_results

    def get_network_stats(self) -> Dict:
        """Get statistics for entire network."""
        return {
            "num_agents": len(self.agents),
            "agents": {name: agent.get_stats() for name, agent in self.agents.items()},
            "total_spikes": sum(agent.spike_count for agent in self.agents.values())
        }

    def visualize_connections(self) -> str:
        """Generate ASCII visualization of agent connections."""
        lines = ["Agent Network:"]
        lines.append("=" * 50)

        for agent in self.agents.values():
            lines.append(f"\n{agent.name}:")
            if agent.connections:
                for connected_agent, weight in agent.connections.items():
                    bar = "█" * int(weight * 10)
                    lines.append(f"  → {connected_agent.name} [{bar}] {weight:.2f}")
            else:
                lines.append("  (no connections)")

        return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    kb = HypervectorSpace(dims=10000)
    network = AgentNetwork(kb)

    # Create agents
    auth_agent = network.create_agent("auth-service", ["auth-service", "authentication"])
    limiter_agent = network.create_agent("rate-limiter", ["rate-limiter", "rate_limiting"])

    # Add facts
    auth_agent.add_fact("auth-service", "needs", "rate_limiting")
    limiter_agent.add_fact("rate-limiter", "created_for", "auth-service")

    # Connect agents
    network.connect_agents("auth-service", "rate-limiter", weight=0.9)

    # Query
    query_vec = kb.encode_query(subject="auth-service", relation="needs")
    results = network.broadcast_query(query_vec)

    print("Query: What does auth-service need?")
    for meta, score, agent_name in results[:5]:
        print(f"  [{agent_name}] {meta['subject']} {meta['relation']} {meta['object']} (score: {score:.3f})")

    print("\n" + network.visualize_connections())
