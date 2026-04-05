import pytest
from pydantic import ValidationError

from maestro.core.backlog_graph import build_backlog_graph, select_next_ticket
from maestro.schemas.backlog_graph import BacklogGraph, BacklogGraphEdge, BacklogGraphNode
from maestro.schemas.contracts import Backlog, Ticket, TicketStatus


def sample_backlog() -> Backlog:
    return Backlog(
        tickets=[
            Ticket(
                id="TICKET-1",
                title="Foundations",
                description="Set up shared contracts",
                acceptance_criteria=["contracts exist"],
                priority=3,
            ),
            Ticket(
                id="TICKET-2",
                title="Dependent flow",
                description="Build on shared contracts",
                acceptance_criteria=["flow exists"],
                dependencies=["TICKET-1"],
                priority=2,
            ),
            Ticket(
                id="TICKET-3",
                title="Independent docs",
                description="Add docs",
                acceptance_criteria=["docs exist"],
                priority=1,
            ),
        ]
    )


def test_build_backlog_graph_orders_by_dependency_then_priority() -> None:
    graph = build_backlog_graph(sample_backlog())

    assert graph.ordered_ticket_ids == ["TICKET-1", "TICKET-3", "TICKET-2"]
    assert graph.critical_path_ticket_ids == ["TICKET-2"]
    assert graph.nodes[0].parallelizable is True


def test_backlog_graph_rejects_unknown_dependencies() -> None:
    with pytest.raises(ValidationError):
        BacklogGraph(
            nodes=[BacklogGraphNode(ticket_id="TICKET-1", dependencies=["missing"])],
            edges=[],
        )


def test_select_next_ticket_respects_completed_dependencies() -> None:
    backlog = sample_backlog()
    backlog.execution_graph = build_backlog_graph(backlog)

    first = select_next_ticket(backlog, completed_tickets=[])
    assert first is not None
    assert first.id == "TICKET-1"
    first.status = TicketStatus.complete

    second = select_next_ticket(backlog, completed_tickets=["TICKET-1"])
    assert second is not None
    assert second.id == "TICKET-3"

    second.status = TicketStatus.complete
    third = select_next_ticket(backlog, completed_tickets=["TICKET-1", "TICKET-3"])
    assert third is not None
    assert third.id == "TICKET-2"


def test_backlog_graph_rejects_unknown_edge_nodes() -> None:
    with pytest.raises(ValidationError):
        BacklogGraph(
            nodes=[BacklogGraphNode(ticket_id="TICKET-1")],
            edges=[BacklogGraphEdge(source_ticket_id="TICKET-1", target_ticket_id="TICKET-2")],
        )
