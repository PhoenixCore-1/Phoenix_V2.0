"""Generic asynchronous inter-module event contracts and in-process event bus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Tuple

from phoenix_framework.context import FrameworkContext


@dataclass(frozen=True)
class ModuleEvent:
    """An event published by a Phoenix module through the Framework boundary."""

    event_id: str
    event_type: str
    source_module: str
    context: FrameworkContext
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name, value in (
            ("event_id", self.event_id),
            ("event_type", self.event_type),
            ("source_module", self.source_module),
        ):
            if not value.strip():
                raise ValueError(f"Event {name} cannot be empty")


@dataclass(frozen=True)
class EventSubscription:
    """A subscription to a published event type."""

    subscription_id: str
    module_code: str
    event_type: str
    handler: Callable[[ModuleEvent], None]


class ModuleEventBus:
    """Minimal Framework event boundary; persistence is a later Core concern."""

    def __init__(self) -> None:
        self._subscriptions: Dict[str, List[EventSubscription]] = {}

    def subscribe(self, subscription: EventSubscription) -> None:
        if not subscription.subscription_id.strip():
            raise ValueError("Subscription id cannot be empty")
        if not subscription.module_code.strip():
            raise ValueError("Subscription module cannot be empty")
        subscribers = self._subscriptions.setdefault(subscription.event_type, [])
        if any(item.subscription_id == subscription.subscription_id for item in subscribers):
            raise ValueError(f"Duplicate subscription: {subscription.subscription_id}")
        subscribers.append(subscription)

    def publish(self, event: ModuleEvent) -> Tuple[str, ...]:
        delivered: List[str] = []
        for subscription in tuple(self._subscriptions.get(event.event_type, ())):
            subscription.handler(event)
            delivered.append(subscription.subscription_id)
        return tuple(delivered)

    def unsubscribe(self, subscription_id: str) -> None:
        for event_type in tuple(self._subscriptions):
            self._subscriptions[event_type] = [
                item for item in self._subscriptions[event_type]
                if item.subscription_id != subscription_id
            ]
            if not self._subscriptions[event_type]:
                del self._subscriptions[event_type]
