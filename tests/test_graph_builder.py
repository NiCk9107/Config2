"""Тесты построения графа зависимостей."""
import unittest
from typing import Dict, List

from src.graph_builder import build_graph


def make_fetcher(repo: Dict[str, List[str]]):
    """Создание fetcher из словаря для тестов."""
    def fetcher(package: str) -> List[str]:
        return repo.get(package, [])
    return fetcher


class TestGraphBuilder(unittest.TestCase):
    """Тесты функции build_graph."""

    def test_simple_graph(self) -> None:
        """Тест построения ациклического графа."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = build_graph("A", make_fetcher(repo))
        self.assertEqual(graph.nodes(), ["A", "B", "C", "D"])
        self.assertIn(("A", "B"), graph.edges())

    def test_cycle_does_not_hang(self) -> None:
        """Тест: граф с циклом строится без зависания."""
        repo = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph = build_graph("A", make_fetcher(repo))
        self.assertEqual(len(graph.nodes()), 3)
        self.assertEqual(len(graph.find_cycles()), 1)

    def test_diamond_node_once(self) -> None:
        """Тест: общий узел ромба добавляется один раз."""
        repo = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = build_graph("A", make_fetcher(repo))
        self.assertEqual(graph.nodes().count("D"), 1)

    def test_self_loop(self) -> None:
        """Тест: самопетля обрабатывается корректно."""
        repo = {"A": ["A"]}
        graph = build_graph("A", make_fetcher(repo))
        self.assertEqual(graph.find_cycles(), [["A", "A"]])


if __name__ == "__main__":
    unittest.main()