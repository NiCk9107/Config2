"""Тесты экспорта графа в язык D2."""
import unittest
from typing import Dict, List

from src.graph_builder import build_graph
from src.d2_export import graph_to_d2


def make_fetcher(repo: Dict[str, List[str]]):
    """Создание fetcher из словаря для тестов."""
    def fetcher(package: str) -> List[str]:
        return repo.get(package, [])
    return fetcher


class TestD2Export(unittest.TestCase):
    """Тесты функции graph_to_d2."""

    def test_d2_text_simple(self) -> None:
        """Тест D2-представления простого графа."""
        repo = {"A": ["B"], "B": []}
        graph = build_graph("A", make_fetcher(repo))
        text = graph_to_d2(graph)
        self.assertIn('"A"', text)
        self.assertIn('"A" -> "B"', text)

    def test_d2_text_cycle(self) -> None:
        """Тест: цикл отображается явным ребром."""
        repo = {"A": ["B"], "B": ["A"]}
        graph = build_graph("A", make_fetcher(repo))
        text = graph_to_d2(graph)
        self.assertIn('"B" -> "A"', text)


if __name__ == "__main__":
    unittest.main()