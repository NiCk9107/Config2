"""Модуль вычисления порядка загрузки зависимостей."""
from collections import deque
from typing import Callable, Deque, List, Set

from .graph import DependencyGraph

FetchFunc = Callable[[str], List[str]]


def bfs_load_order(root: str, fetch: FetchFunc) -> List[str]:
    """
    Порядок обнаружения пакетов при обходе в ширину.

    Args:
        root: Имя корневого пакета.
        fetch: Функция получения зависимостей пакета.

    Returns:
        Список имён пакетов в порядке обхода BFS.
    """
    order: List[str] = []
    visited: Set[str] = {root}
    queue: Deque[str] = deque([root])
    _bfs_order_step(queue, visited, order, fetch)
    return order


def _bfs_order_step(
    queue: Deque[str],
    visited: Set[str],
    order: List[str],
    fetch: FetchFunc,
) -> None:
    """
    Один шаг BFS с рекурсивным продолжением обхода.

    Args:
        queue: Очередь пакетов на обработку.
        visited: Множество уже учтённых пакетов.
        order: Накопитель порядка загрузки.
        fetch: Функция получения зависимостей пакета.
    """
    if not queue:
        return
    current = queue.popleft()
    order.append(current)
    for dep in fetch(current):
        if dep not in visited:
            visited.add(dep)
            queue.append(dep)
    _bfs_order_step(queue, visited, order, fetch)


def topological_load_order(graph: DependencyGraph) -> List[str]:
    """
    Топологический порядок: зависимости раньше зависимых.

    Args:
        graph: Построенный граф зависимостей.

    Returns:
        Список имён пакетов в порядке установки.
        Пустой список, если в графе есть циклы.
    """
    nodes = graph.nodes()
    remaining = {n: len(graph.dependencies_of(n)) for n in nodes}
    dependents = {n: [] for n in nodes}
    for source, target in graph.edges():
        dependents[target].append(source)

    ready = sorted(n for n in nodes if remaining[n] == 0)
    queue: Deque[str] = deque(ready)
    order: List[str] = []

    while queue:
        current = queue.popleft()
        order.append(current)
        for dep in sorted(dependents[current]):
            remaining[dep] -= 1
            if remaining[dep] == 0:
                queue.append(dep)

    if len(order) != len(nodes):
        return []
    return order