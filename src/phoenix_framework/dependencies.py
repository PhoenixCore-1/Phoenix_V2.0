"""Generic module dependency validation and resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Set, Tuple

from phoenix_framework.contracts import ModuleIntegrationContract, ModuleDependency


@dataclass(frozen=True)
class DependencyIssue:
    module_code: str
    dependency: str
    reason: str


def _version_parts(version: str) -> Tuple[int, ...]:
    """Parse numeric dotted versions; reject ambiguous version strings."""
    try:
        parts = tuple(int(part) for part in version.split("."))
    except ValueError as exc:
        raise ValueError(f"Unsupported module version: {version}") from exc
    if not parts or any(part < 0 for part in parts):
        raise ValueError(f"Unsupported module version: {version}")
    return parts


def _version_in_range(version: str, dependency: ModuleDependency) -> bool:
    current = _version_parts(version)
    if dependency.minimum_version and current < _version_parts(dependency.minimum_version):
        return False
    if dependency.maximum_version and current > _version_parts(dependency.maximum_version):
        return False
    return True


def validate_dependencies(
    contracts: Iterable[ModuleIntegrationContract],
) -> Tuple[DependencyIssue, ...]:
    """Validate required modules, compatible versions and dependency cycles."""
    by_code: Dict[str, ModuleIntegrationContract] = {}
    for contract in contracts:
        if contract.module_code in by_code:
            raise ValueError(f"Duplicate integration contract: {contract.module_code}")
        by_code[contract.module_code] = contract

    issues = []
    graph: Dict[str, Set[str]] = {code: set() for code in by_code}

    for contract in contracts:
        for dependency in contract.dependencies:
            target = by_code.get(dependency.module_code)
            if target is None:
                if dependency.required:
                    issues.append(DependencyIssue(contract.module_code, dependency.module_code, "missing required module"))
                continue
            if not _version_in_range(target.version, dependency):
                issues.append(DependencyIssue(contract.module_code, dependency.module_code, "incompatible version"))
            graph[contract.module_code].add(dependency.module_code)
            for capability in dependency.capabilities:
                if capability not in target.provided_capabilities:
                    issues.append(DependencyIssue(contract.module_code, dependency.module_code, f"missing capability: {capability}"))

    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(code: str) -> None:
        if code in visiting:
            issues.append(DependencyIssue(code, code, "circular dependency"))
            return
        if code in visited:
            return
        visiting.add(code)
        for target in graph[code]:
            visit(target)
        visiting.remove(code)
        visited.add(code)

    for code in graph:
        visit(code)

    return tuple(issues)
