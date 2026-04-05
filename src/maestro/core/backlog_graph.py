from __future__ import annotations

from maestro.schemas.backlog_graph import BacklogGraph, BacklogGraphEdge, BacklogGraphNode
from maestro.schemas.contracts import Backlog, Ticket, TicketStatus


def build_backlog_graph(backlog: Backlog) -> BacklogGraph:
    depth_cache: dict[str, int] = {}
    tickets_by_id = {ticket.id: ticket for ticket in backlog.tickets}

    def depth(ticket: Ticket) -> int:
        if ticket.id in depth_cache:
            return depth_cache[ticket.id]
        if not ticket.dependencies:
            depth_cache[ticket.id] = 0
            return 0
        value = 1 + max(depth(tickets_by_id[dependency]) for dependency in ticket.dependencies)
        depth_cache[ticket.id] = value
        return value

    ordered_tickets = sorted(
        backlog.tickets,
        key=lambda ticket: (depth(ticket), -ticket.priority, ticket.id),
    )
    nodes = [
        BacklogGraphNode(
            ticket_id=ticket.id,
            dependencies=list(ticket.dependencies),
            parallelizable=not ticket.dependencies,
            priority=ticket.priority,
            critical_path_rank=depth(ticket),
        )
        for ticket in ordered_tickets
    ]
    edges = [
        BacklogGraphEdge(source_ticket_id=dependency, target_ticket_id=ticket.id)
        for ticket in backlog.tickets
        for dependency in ticket.dependencies
    ]
    critical_depth = max((node.critical_path_rank for node in nodes), default=0)
    critical_path = [node.ticket_id for node in nodes if node.critical_path_rank == critical_depth]
    return BacklogGraph(
        nodes=nodes,
        edges=edges,
        ordered_ticket_ids=[ticket.id for ticket in ordered_tickets],
        critical_path_ticket_ids=critical_path,
    )


def select_next_ticket(backlog: Backlog, completed_tickets: list[str]) -> Ticket | None:
    graph = backlog.execution_graph or build_backlog_graph(backlog)
    completed = set(completed_tickets)
    for ticket_id in graph.ordered_ticket_ids:
        ticket = next((item for item in backlog.tickets if item.id == ticket_id), None)
        if ticket is None or ticket.status is not TicketStatus.pending:
            continue
        node = next(node for node in graph.nodes if node.ticket_id == ticket_id)
        if set(node.dependencies).issubset(completed):
            return ticket
    return None
