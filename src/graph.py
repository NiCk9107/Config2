"""Модуль графа зависимостей и поиска циклов."""
from typing import Dict, List, Set, Tuple


class DependencyGraph:
    """Ориентированный граф зависимостей пакетов."""

    def __init__(self) -> None:
        """Создание пустого графа."""
        self._adjacency: Dict[str, List[str]] = {}

    def add_node(self, name: str) -> None:
        """
        Добавление узла в граф.

        Args:
            name: Имя пакета.
        """
        if name not in self._adjacency:
            self._adjacency[name] = []

    def add_edge(self, source: str, target: str) -> None:
        """
        Добавление ребра зависимости source -> target.

        Args:
            source: Пакет-владелец зависимости.
            target: Пакет-зависимость.
        """
        self.add_node(source)
        self.add_node(target)
        if target not in self._adjacency[source]:
            self._adjacency[source].append(target)

    def nodes(self) -> List[str]:
        """
        Список всех узлов графа.

        Returns:
            Отсортированный список имён пакетов.
        """
        return sorted(self._adjacency.keys())

    def edges(self) -> List[Tuple[str, str]]:
        """
        Список всех рёбер графа.

        Returns:
            Отсортированный список пар (source, target).
        """
        result: List[Tuple[str, str]] = []
        for source in self.nodes():
            for target in self._adjacency[source]:
                result.append((source, target))
        return sorted(result)

    def dependencies_of(self, name: str) -> List[str]:
        """
        Прямые зависимости пакета.

        Args:
            name: Имя пакета.

        Returns:
            Список имён зависимостей (пустой, если узла нет).
        """
        return list(self._adjacency.get(name, []))

    def find_cycles(self) -> List[List[str]]:
        """
        Поиск циклических зависимостей обходом в глубину.

        Returns:
            Список циклов, каждый цикл — список имён пакетов.
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        for node in self.nodes():
            if node not in visited:
                self._dfs(node, [], set(), visited, cycles)
        return cycles

    def _dfs(
        self,
        node: str,
        path: List[str],
        on_stack: Set[str],
        visited: Set[str],
        cycles: List[List[str]],
    ) -> None:
        """
        Рекурсивный обход в глубину для поиска циклов.

        Args:
            node: Текущий узел.
            path: Путь от корня обхода.
            on_stack: Узлы на текущем стеке рекурсии.
            visited: Все посещённые узлы.
            cycles: Накопитель найденных циклов.
        """
        visited.add(node)
        on_stack.add(node)
        path.append(node)
        for dep in self.dependencies_of(node):
            if dep in on_stack:
                start = path.index(dep)
                cycles.append(path[start:] + [dep])
            elif dep not in visited:
                self._dfs(dep, path, on_stack, visited, cycles)
        path.pop()
        on_stack.discard(node)