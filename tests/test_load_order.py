"""Тесты вычисления порядка загрузки зависимостей."""
import unittest
from typing import Dict, List

from src.graph_builder import build_graph
from src.load_order import bfs_load_order, topological_load_order


def make_fetcher(repo: Dict[str, List[str]]):
    """Создание fetcher из словаря для тестов."""
    def fetcher(package: str) -> List[str]:
        return repo.get(package, [])
    return fetcher


class TestLoadOrder(unittest.TestCase):
    """Тесты функций bfs_load_order и topological_load_order."""

    def test_bfs_order_simple(self) -> None:
        """Тест BFS-порядка на простом графе."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        order = bfs_load_order("A", make_fetcher(repo))
        self.assertEqual(order, ["A", "B", "C", "D"])

    def test_topo_order_simple(self) -> None:
        """Тест топологического порядка: зависимости первыми."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = build_graph("A", make_fetcher(repo))
        order = topological_load_order(graph)
        self.assertEqual(order, ["D", "B", "C", "A"])

    def test_topo_order_with_cycle(self) -> None:
        """Тест: при цикле топологический порядок не определён."""
        repo = {"A": ["B"], "B": ["A"]}
        graph = build_graph("A", make_fetcher(repo))
        self.assertEqual(topological_load_order(graph), [])


if __name__ == "__main__":
    unittest.main()