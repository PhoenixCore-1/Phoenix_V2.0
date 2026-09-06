"""Page definitions for the Phoenix System presentation layer.

Pages are deliberately declarative. Business modules will contribute their
own pages through the same mechanism, while company configuration can later
customise layout and component placement without changing business code.
"""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class PageDefinition:
    key: str
    title: str
    route: str
    module_code: str | None = None
    components: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)


class PageRegistry:
    """Runtime registry for Phoenix System page definitions."""

    def __init__(self) -> None:
        self._pages: dict[str, PageDefinition] = {}

    def register(self, page: PageDefinition) -> None:
        if page.key in self._pages:
            raise ValueError(f"Page already registered: {page.key}")
        self._pages[page.key] = page

    def get(self, key: str) -> PageDefinition:
        try:
            return self._pages[key]
        except KeyError:
            raise ValueError(f"Page not registered: {key}") from None

    def list(self) -> list[PageDefinition]:
        return list(self._pages.values())


def register_system_pages(registry: PageRegistry) -> None:
    """Register pages owned by the Phoenix System shell."""
    defaults = (
        PageDefinition(
            key="system.dashboard",
            title="Dashboard",
            route="/",
            components=("welcome", "module_grid", "system_status"),
        ),
        PageDefinition(
            key="system.administration",
            title="System",
            route="/system",
            components=("system_navigation",),
        ),
    )
    for page in defaults:
        if not any(existing.key == page.key for existing in registry.list()):
            registry.register(page)
