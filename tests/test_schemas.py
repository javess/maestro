from maestro.schemas.contracts import Backlog, ProductSpec, Ticket


def test_product_spec_round_trip() -> None:
    spec = ProductSpec(
        title="x",
        summary="y",
        outcomes=["a"],
        scope=["b"],
        acceptance_criteria=["c"],
    )
    assert spec.title == "x"


def test_backlog_requires_tickets() -> None:
    backlog = Backlog(
        tickets=[
            Ticket(
                id="T-1",
                title="t",
                description="d",
                acceptance_criteria=["a"],
            )
        ]
    )
    assert backlog.tickets[0].id == "T-1"
