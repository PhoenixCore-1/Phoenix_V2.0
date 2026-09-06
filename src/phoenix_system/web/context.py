"""Bridge between Phoenix Core security context and the web application."""

from phoenix_core.security.context import RequestContext
from phoenix_framework.context import FrameworkContext


def framework_context_from_core(context: RequestContext) -> FrameworkContext:
    """Project the authoritative Core request context for web/framework use."""
    return FrameworkContext.from_core(context)
