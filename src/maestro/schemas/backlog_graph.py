from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class BacklogGraphNode(BaseModel):
    ticket_id: str
    dependencies: list[str] = Field(default_factory=list)
    parallelizable: bool = False
    priority: int = 1
    critical_path_rank: int = 0


class BacklogGraphEdge(BaseModel):
    source_ticket_id: str
    target_ticket_id: str


class BacklogGraph(BaseModel):
    nodes: list[BacklogGraphNode]
    edges: list[BacklogGraphEdge] = Field(default_factory=list)
    ordered_ticket_ids: list[str] = Field(default_factory=list)
    critical_path_ticket_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph(self) -> BacklogGraph:
        node_ids = [node.ticket_id for node in self.nodes]
        unique_node_ids = set(node_ids)
        if len(node_ids) != len(unique_node_ids):
            raise ValueError("backlog graph ticket ids must be unique")

        for edge in self.edges:
            if edge.source_ticket_id not in unique_node_ids:
                raise ValueError(
                    f"backlog graph edge references unknown source ticket '{edge.source_ticket_id}'"
                )
            if edge.target_ticket_id not in unique_node_ids:
                raise ValueError(
                    f"backlog graph edge references unknown target ticket '{edge.target_ticket_id}'"
                )

        for node in self.nodes:
            missing_dependencies = sorted(set(node.dependencies) - unique_node_ids)
            if missing_dependencies:
                raise ValueError(
                    f"backlog graph node '{node.ticket_id}' depends on unknown tickets: "
                    f"{missing_dependencies}"
                )

        if self.ordered_ticket_ids:
            missing_ordered = sorted(set(self.ordered_ticket_ids) - unique_node_ids)
            if missing_ordered:
                raise ValueError(
                    f"ordered backlog ticket ids reference unknown tickets: {missing_ordered}"
                )

        if self.critical_path_ticket_ids:
            missing_critical = sorted(set(self.critical_path_ticket_ids) - unique_node_ids)
            if missing_critical:
                raise ValueError(
                    f"critical path ticket ids reference unknown tickets: {missing_critical}"
                )

        return self
