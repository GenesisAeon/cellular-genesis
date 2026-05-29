"""genesis-os computational apoptosis resource governor."""

from __future__ import annotations

import time
from typing import TypedDict

from cellular_genesis.constants import RESOURCE_ATP_THRESHOLD


class _NodeState(TypedDict):
    resource: float
    alive: bool
    registered_at: float


class ComputationalApoptosisGovernor:
    """
    Gemini's insight: bridge between cellular-genesis and genesis-os.

    Monitors normalised resource usage of genesis-os nodes.
    When a node's 'ATP' (CPU + memory, normalised) falls below
    RESOURCE_ATP_THRESHOLD, triggers apoptotic cleanup.
    """

    def __init__(self, threshold: float = RESOURCE_ATP_THRESHOLD) -> None:
        self.threshold = threshold
        self._nodes: dict[str, _NodeState] = {}
        self.events: list[dict[str, object]] = []

    def register_node(self, node_id: str, resource_level: float = 1.0) -> None:
        self._nodes[node_id] = _NodeState(
            resource=resource_level,
            alive=True,
            registered_at=time.time(),
        )

    def update_resource(self, node_id: str, resource_level: float) -> None:
        if node_id in self._nodes:
            self._nodes[node_id]["resource"] = resource_level

    def check_apoptosis(self) -> list[str]:
        """Return node IDs that have crossed the apoptotic threshold."""
        triggered = []
        for nid, state in self._nodes.items():
            if state["alive"] and state["resource"] < self.threshold:
                triggered.append(nid)
        return triggered

    def trigger_computational_apoptosis(self, node_id: str) -> dict[str, object]:
        """Mark node as apoptotic, log Phase Transition Event."""
        if node_id not in self._nodes:
            return {"error": f"unknown node {node_id}"}
        node = self._nodes[node_id]
        node["alive"] = False
        event: dict[str, object] = {
            "node_id": node_id,
            "resource_at_death": node["resource"],
            "timestamp": time.time(),
            "type": "computational_apoptosis",
        }
        self.events.append(event)
        return event

    def alive_nodes(self) -> list[str]:
        return [nid for nid, s in self._nodes.items() if s["alive"]]
