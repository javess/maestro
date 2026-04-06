import time

from maestro.server.scheduler import LocalRunScheduler


def test_scheduler_queues_and_runs_tasks() -> None:
    scheduler = LocalRunScheduler(max_workers=1)
    order: list[str] = []

    def first() -> None:
        time.sleep(0.1)
        order.append("first")

    def second() -> None:
        order.append("second")

    scheduler.enqueue("run-1", first)
    scheduler.enqueue("run-2", second)

    time.sleep(0.25)

    assert order == ["first", "second"]
    assert scheduler.future_state("run-1") == "done"
    assert scheduler.future_state("run-2") == "done"


def test_scheduler_can_cancel_queued_runs() -> None:
    scheduler = LocalRunScheduler(max_workers=1)

    def first() -> None:
        time.sleep(0.2)

    def second() -> None:
        raise AssertionError("should not run")

    scheduler.enqueue("run-1", first)
    scheduler.enqueue("run-2", second)

    assert scheduler.cancel("run-2") is True
    time.sleep(0.25)
    assert scheduler.future_state("run-2") == "cancelled"
