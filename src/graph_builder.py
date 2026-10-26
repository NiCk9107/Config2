"""Построение графа зависимостей обходом в ширину (BFS)."""
from collections import deque
from typing import Callable, Deque, List, Set

from .graph import DependencyGraph

FetchFunc = Callable[[str], List[str]]


def build_graph(
    root: str, fetch_dependencies: FetchFunc
) -> DependencyGraph:
    """
    Построение графа зависимостей от корневого пакета.

    Args:
        root: Имя корневого пакета.
        fetch_dependencies: Функция получения зависимостей пакета.

    Returns:
        Построенный граф зависимостей.
    """
    graph = DependencyGraph()
    graph.add_node(root)
    visited: Set[str] = {root}
    queue: Deque[str] = deque([root])
    _bfs_step(graph, queue, visited, fetch_dependencies)
    return graph


def _bfs_step(
    graph: DependencyGraph,
    queue: Deque[str],
    visited: Set[str],
    fetch_dependencies: FetchFunc,
) -> None:
    """
    Один шаг BFS с рекурсивным продолжением обхода.

    Args:
        graph: Накапливаемый граф зависимостей.
        queue: Очередь пакетов на обработку (FIFO).
        visited: Множество уже посещённых пакетов.
        fetch_dependencies: Функция получения зависимостей пакета.
    """
    if not queue:
        return
    current = queue.popleft()
    for dep in fetch_dependencies(current):
        graph.add_edge(current, dep)
        if dep not in visited:
            visited.add(dep)
            queue.append(dep)
    _bfs_step(graph, queue, visited, fetch_dependencies)