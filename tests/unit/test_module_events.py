from uuid import uuid4

from phoenix_framework.context import FrameworkContext
from phoenix_framework.events import EventSubscription, ModuleEvent, ModuleEventBus


def test_event_is_delivered_to_matching_subscription():
    received = []
    bus = ModuleEventBus()
    bus.subscribe(EventSubscription("sub-1", "crm", "customer.created.v1", received.append))
    event = ModuleEvent(
        "evt-1", "customer.created.v1", "crm",
        FrameworkContext("req-1", uuid4(), uuid4(), uuid4(), frozenset(), frozenset()),
        {"customer_id": "C1"},
    )

    assert bus.publish(event) == ("sub-1",)
    assert received == [event]


def test_unsubscribe_stops_delivery():
    received = []
    bus = ModuleEventBus()
    bus.subscribe(EventSubscription("sub-1", "sales", "customer.created.v1", received.append))
    bus.unsubscribe("sub-1")
    event = ModuleEvent(
        "evt-1", "customer.created.v1", "crm",
        FrameworkContext("req-1", uuid4(), uuid4(), uuid4(), frozenset(), frozenset()),
        {},
    )

    assert bus.publish(event) == ()
    assert received == []


def test_duplicate_subscription_is_rejected():
    bus = ModuleEventBus()
    subscription = EventSubscription("sub-1", "sales", "order.created.v1", lambda event: None)
    bus.subscribe(subscription)

    try:
        bus.subscribe(subscription)
        assert False, "Expected duplicate subscription to fail"
    except ValueError as exc:
        assert "Duplicate subscription" in str(exc)
